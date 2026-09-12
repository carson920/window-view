import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
const root=new URL('../data/laguna-approved-job/',import.meta.url);
const source=JSON.parse(await fs.readFile(new URL('sources/primary-source.json',root)));
const page=await fs.readFile(new URL('sources/primary-page.html',root),'utf8');
const records=[];
await fs.mkdir(new URL('floorplans/full/',root),{recursive:true});
for(const item of source.items){
 const url=item.previewUrl.replace('/estate_small_image/','/estate_image/');
 if(!page.includes(new URL(url).pathname.slice(1)))throw Error('Full image not linked by approved page: '+url);
 const file=new URL(`floorplans/full/${item.id}.jpg`,root);
 let bytes=await fs.readFile(file).catch(()=>null);
 if(!bytes){const response=await fetch(url);if(!response.ok)throw Error(`${url}: ${response.status}`);bytes=Buffer.from(await response.arrayBuffer());await fs.writeFile(file,bytes);await new Promise(r=>setTimeout(r,700));}
 records.push({id:item.id,url,sourcePage:source.sourcePage,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')});
 console.log(item.id,bytes.length);
}
await fs.writeFile(new URL('sources/downloads.json',root),JSON.stringify(records,null,2)+'\n');
