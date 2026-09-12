import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { Readable } from 'node:stream';
import { createAuth, passwordHash, saveState, readState } from '../server/auth.mjs';
function response(){return {writeHead(status,headers){this.status=status;this.headers=headers;},end(body){this.body=JSON.parse(body);}};}
function request(body={},cookie=''){const req=Readable.from([JSON.stringify(body)]);req.method='POST';req.headers={host:'localhost',origin:'http://localhost',cookie};req.socket={remoteAddress:'127.0.0.1'};return req;}
test('authentication, persistent quota, logout, origin and expiry',async()=>{
 const dir=mkdtempSync(join(tmpdir(),'window-auth-')),file=join(dir,'auth.json');
 try{
  saveState({users:{alice:await passwordHash('correct-password')},quotas:{}},file);
  let time=Date.now();const auth=createAuth({file,now:()=>time,minuteLimit:1,dayLimit:2,secure:true});
  let res=response();assert.equal(auth.authorize(request(),res,'/api/unit'),false);assert.equal(res.status,401);
  res=response();let req=request({username:'alice',password:'correct-password'});req.headers.origin='https://evil.invalid';await auth.handle(req,res,'/api/auth/login');assert.equal(res.status,403);
  res=response();await auth.handle(request({username:'alice',password:'wrong'}),res,'/api/auth/login');assert.equal(res.status,401);
  res=response();await auth.handle(request({username:'alice',password:'correct-password'}),res,'/api/auth/login');assert.equal(res.status,200);
  const cookie=res.headers['Set-Cookie'];assert.match(cookie,/HttpOnly/);assert.match(cookie,/Secure/);assert.match(cookie,/SameSite=Strict/);
  req=request({},cookie);assert.equal(auth.authorize(req,response(),'/api/unit'),true);
  res=response();assert.equal(auth.authorize(req,res,'/api/unit'),false);assert.equal(res.status,429);
  time+=60001;assert.equal(auth.authorize(req,response(),'/api/unit'),true);assert.equal(readState(file).quotas.alice.count,2);
  time+=60001;res=response();assert.equal(auth.authorize(req,res,'/api/unit'),false);assert.equal(res.status,429);
  res=response();await auth.handle(req,res,'/api/auth/logout');assert.equal(res.status,200);assert.equal(auth.authorize(req,response(),'/api/catalog'),false);
  res=response();await auth.handle(request({username:'alice',password:'correct-password'}),res,'/api/auth/login');req=request({},res.headers['Set-Cookie']);time+=28800001;assert.equal(auth.authorize(req,response(),'/api/catalog'),false);
  const restarted=createAuth({file});assert.equal(restarted.authorize(req,response(),'/api/unit'),false);assert.equal(readState(file).quotas.alice.count,2);
 }finally{rmSync(dir,{recursive:true,force:true});}
});
test('login attempts are throttled',async()=>{
 const auth=createAuth({file:join(tmpdir(),'nonexistent-auth-test.json')});
 for(let i=0;i<6;i++){const res=response();await auth.handle(request({username:'nobody',password:'bad'}),res,'/api/auth/login');assert.equal(res.status,i===5?429:401);}
});
