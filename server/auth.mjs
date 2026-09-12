import { randomBytes, scrypt as derive, timingSafeEqual, createHash } from 'node:crypto';
import { promisify } from 'node:util';
import { readFileSync, existsSync, mkdirSync, writeFileSync, renameSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
const scrypt=promisify(derive);
export const authFile=resolve(process.env.AUTH_FILE||new URL('../.private/auth.json',import.meta.url).pathname);
export async function passwordHash(password,salt=randomBytes(16).toString('hex')) {return {salt,hash:(await scrypt(password,salt,64)).toString('hex')};}
export function readState(file=authFile){return existsSync(file)?JSON.parse(readFileSync(file,'utf8')):{users:{},quotas:{}};}
export function saveState(state,file=authFile){mkdirSync(dirname(file),{recursive:true,mode:0o700});writeFileSync(file+'.tmp',JSON.stringify(state),{mode:0o600});renameSync(file+'.tmp',file);}
export function send(res,status,body,headers={}){res.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff',...headers});res.end(JSON.stringify(body));}
export function createAuth({file=authFile,now=Date.now,origin=process.env.APP_ORIGIN,secure=process.env.NODE_ENV==='production',minuteLimit=30,dayLimit=100}={}){
 const sessions=new Map(),attempts=new Map();
 const cookie=(value,age)=>`wv_session=${value}; HttpOnly; SameSite=Strict; Path=/; Max-Age=${age}${secure?'; Secure':''}`;
 const sessionKey=req=>createHash('sha256').update((req.headers.cookie||'').match(/(?:^|;\s*)wv_session=([a-f0-9]{64})(?:;|$)/)?.[1]||'').digest('hex');
 function user(req){
  const key=sessionKey(req),session=sessions.get(key);
  if(!session)return null;
  const account=readState(file).users[session.username];
  if(session.expires<=now()||!account||account.hash!==session.version){sessions.delete(key);return null;}
  return session.username;
 }
 async function handle(req,res,path){
  if(!path.startsWith('/api/auth/'))return false;
  if(path==='/api/auth/session'&&req.method==='GET'){send(res,200,{username:user(req)});return true;}
  if(req.method!=='POST'){send(res,405,{error:'Method not allowed'});return true;}
  const expected=origin||`http://${req.headers.host}`;
  if(req.headers.origin!==expected){send(res,403,{error:'Invalid origin'});return true;}
  if(path==='/api/auth/logout'){sessions.delete(sessionKey(req));send(res,200,{ok:true},{'Set-Cookie':cookie('',0)});return true;}
  if(path!=='/api/auth/login'){send(res,404,{error:'Not found'});return true;}
  // Never trust client-supplied forwarding headers. Behind a proxy this is a shared IP limit.
  const ip=req.socket.remoteAddress||'unknown',time=now();
  for(const [k,v] of attempts)if(v.reset<=time)attempts.delete(k);
  if(attempts.size>10000){send(res,429,{error:'Try later'},{'Retry-After':'900'});return true;}
  const attempt=attempts.get(ip)||{count:0,reset:time+900000};attempts.set(ip,attempt);
  if(++attempt.count>5){send(res,429,{error:'Too many login attempts'},{'Retry-After':String(Math.max(1,Math.ceil((attempt.reset-time)/1000)))});return true;}
  try{
   let text='';for await(const chunk of req){text+=chunk;if(Buffer.byteLength(text)>2048){send(res,413,{error:'Request too large'});return true;}}
   const {username,password}=JSON.parse(text);
   if(typeof username!=='string'||typeof password!=='string'||password.length>256){send(res,400,{error:'Invalid credentials'});return true;}
   const account=readState(file).users[username];
   const candidate=await passwordHash(password,account?.salt||'00000000000000000000000000000000');
   if(!account||!timingSafeEqual(Buffer.from(candidate.hash,'hex'),Buffer.from(account.hash,'hex'))){send(res,401,{error:'Invalid credentials'});return true;}
   for(const [k,v] of sessions)if(v.expires<=time||v.username===username)sessions.delete(k);
   const token=randomBytes(32).toString('hex');sessions.set(createHash('sha256').update(token).digest('hex'),{username,version:account.hash,expires:time+28800000});
   send(res,200,{username},{'Set-Cookie':cookie(token,28800)});
  }catch{send(res,400,{error:'Unable to sign in'});}
  return true;
 }
 function authorize(req,res,path){
  const username=user(req);if(!username){send(res,401,{error:'Login required'});return false;}
  if(path==='/api/unit'){
   const state=readState(file),time=now(),day=new Date(time).toISOString().slice(0,10);
   const q=state.quotas[username]||{day,count:0,minute:time,burst:0};
   if(q.day!==day){q.day=day;q.count=0;}
   if(time-q.minute>=60000){q.minute=time;q.burst=0;}
   if(q.count>=dayLimit||q.burst>=minuteLimit){const wait=q.count>=dayLimit?Math.ceil((Date.parse(day)+86400000-time)/1000):Math.ceil((q.minute+60000-time)/1000);send(res,429,{error:'Query limit reached',retryAfter:wait},{'Retry-After':String(wait)});return false;}
   q.count++;q.burst++;state.quotas[username]=q;saveState(state,file);
  }
  return true;
 }
 return {handle,authorize};
}
