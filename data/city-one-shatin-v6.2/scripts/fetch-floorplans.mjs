import fs from 'node:fs/promises';
import path from 'node:path';
const manifest = JSON.parse(await fs.readFile(new URL('../sources/primary-source.json', import.meta.url), 'utf8'));
const outDir = new URL('../floorplans/primary/', import.meta.url);
await fs.mkdir(outDir, { recursive: true });
const results=[];
for (const item of manifest.items || []) {
  const url=item.previewUrl; if(!url) continue;
  const ext=(new URL(url)).pathname.split('.').pop().toLowerCase()||'jpg';
  const name=String(item.id||'plan').replace(/[^a-zA-Z0-9._-]/g,'-')+'.'+ext;
  const target=new URL('../floorplans/primary/'+name, import.meta.url);
  console.log('Fetching',item.id,url);
  try {
    const res=await fetch(url,{headers:{'user-agent':'Mozilla/5.0 WindowViewResearch/1.0','accept':'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'},redirect:'follow'});
    if(!res.ok){console.warn('FAILED',item.id,res.status,res.statusText);results.push({id:item.id,ok:false,status:res.status});continue;}
    const buf=Buffer.from(await res.arrayBuffer()); await fs.writeFile(target,buf);
    console.log('Saved',path.basename(target.pathname),buf.length,'bytes');results.push({id:item.id,ok:true,bytes:buf.length,file:'floorplans/primary/'+name});
  } catch(e){console.warn('FAILED',item.id,e.message);results.push({id:item.id,ok:false,error:e.message});}
}
await fs.writeFile(new URL('../floorplans/fetch-results.json', import.meta.url),JSON.stringify(results,null,2)+'\n');
console.log('Done',results.filter(x=>x.ok).length,'/',results.length);
