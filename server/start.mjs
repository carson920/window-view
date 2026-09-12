if(process.env.NODE_ENV==='production' && !/^https:\/\//.test(process.env.APP_ORIGIN||''))throw new Error('Production requires APP_ORIGIN=https://your-domain');
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { api } from './api.mjs';
const dist=resolve(fileURLToPath(new URL('../dist/',import.meta.url)));
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.svg':'image/svg+xml','.png':'image/png'};
export const server=createServer((req,res)=>api(req,res,async()=>{
 try {
  const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
  if(req.method!=='GET' || !(pathname==='/' || pathname==='/index.html' || pathname.startsWith('/assets/')))throw Error();
  const file=resolve(dist,'.'+(pathname==='/'?'/index.html':pathname));
  if(!file.startsWith(dist+sep) || !(await stat(file)).isFile())throw Error();
  res.writeHead(200,{'Content-Type':types[extname(file)]||'application/octet-stream','X-Content-Type-Options':'nosniff'});res.end(await readFile(file));
 }catch{res.writeHead(404);res.end('Not found');}
}));
server.listen(Number(process.env.PORT||5173),process.env.HOST||'127.0.0.1',()=>console.log(`Window View server: ${server.address().port}`));
