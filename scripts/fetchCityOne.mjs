import fs from 'node:fs';
import {createHash} from 'node:crypto';
const job=new URL('../data/city-one-shatin-approved-job/',import.meta.url);
const data=JSON.parse(fs.readFileSync(new URL('approved-job.json',job)));
fs.mkdirSync(new URL('floorplans/',job),{recursive:true});
const records=[];
for(const item of data.primaryFloorPlanSource.items){
 const target=new URL(`floorplans/${item.id}.jpg`,job),start=performance.now();
 try{
  const cached=fs.existsSync(target);
  if(!cached){const res=await fetch(item.previewUrl,{signal:AbortSignal.timeout(30000)});if(!res.ok)throw Error(`HTTP ${res.status}`);fs.writeFileSync(target,Buffer.from(await res.arrayBuffer()));}
  const bytes=fs.readFileSync(target);records.push({id:item.id,url:item.previewUrl,cached,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex'),seconds:(performance.now()-start)/1000});
 }catch(e){records.push({id:item.id,error:e.message,seconds:(performance.now()-start)/1000});}
 fs.writeFileSync(new URL('sources/downloads.json',job),JSON.stringify(records,null,2)+'\n');
 console.log(item.id,records.at(-1).error||'OK');
 await new Promise(r=>setTimeout(r,500));
}
