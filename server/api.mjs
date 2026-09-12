import { createAuth, send } from './auth.mjs';
const auth=createAuth();
const AUTH_REQUIRED = process.env.AUTH_REQUIRED === 'true';
import { readFileSync, existsSync } from 'node:fs';
const root = new URL('../data/', import.meta.url);
const data = JSON.parse(readFileSync(new URL('properties.json', root), 'utf8'));
const pick = (object, keys) => Object.fromEntries(keys.filter(k => object[k] !== undefined).map(k => [k, object[k]]));
export const catalog = {
  eyeHeight: data.eyeHeight, defaultEstateId: data.defaultEstateId,
  estates: data.estates.filter(e => e.id.startsWith('kingswood-') || ['laguna-city','south-horizons'].includes(e.id)).map(e => ({...pick(e, ['id','nameTC','nameEN','synthetic','defaultBuildingId']), buildings:e.buildings.map(b => ({...pick(b,['id','nameTC','nameEN','floors','floorModel']), flats:b.flats.map(f => pick(f,['id','label']))}))}))
};
const phases={'kingswood-locwood':1,'kingswood-sherwood':2,'kingswood-chestwood':3,'kingswood-lynwood':5,'kingswood-maywood':6,'kingswood-kenswood':7};
const visibleEstate = id => id.startsWith('kingswood-') || ['laguna-city','south-horizons'].includes(id);
function outline(estate, building) {
 const file=estate.id==='south-horizons'?`south-horizons-${building.id}/official-footprint.json`:estate.id==='laguna-city'?`laguna-${building.id}/official-footprint.json`:estate.id==='kingswood-chestwood'&&building.id==='tower-1'?'chestwood-tower-1-official-footprint.json':phases[estate.id]?`kingswood-footprints/phase-${phases[estate.id]}-${building.id}-official-footprint.json`:null;
 if(!file || !existsSync(new URL(file,root)))return null;
 return JSON.parse(readFileSync(new URL(file,root),'utf8')).geometry.rings[0];
}
export function lookup(path, params) {
 if(path==='/api/catalog')return {status:200,body:catalog};
 if(path==='/api/estate-review'){
  const estate=data.estates.find(e=>visibleEstate(e.id)&&e.id===params.get('estate'));
  if(!estate)return {status:404,body:{error:'Estate not found'}};
  return {status:200,body:{estateId:estate.id,buildings:estate.buildings.map(b=>({id:b.id,nameTC:b.nameTC,nameEN:b.nameEN,outline:outline(estate,b),flats:b.flats.map(f=>({id:f.id,label:f.label,windows:f.windows.map(w=>pick(w,['id','nameTC','nameEN','latitude','longitude','heading','confidence','windowVerified','georefVerified']))}))}))}};
 }
 if(path!=='/api/unit')return {status:404,body:{error:'Not found'}};
 if([...params.keys()].some(k=>!['estate','building','flat'].includes(k)) || ['estate','building','flat'].some(k=>params.getAll(k).length!==1))return {status:400,body:{error:'Specify one estate, building and flat'}};
 const estate=data.estates.find(e=>visibleEstate(e.id) && e.id===params.get('estate'));
 const building=estate?.buildings.find(b=>b.id===params.get('building'));
 const flat=building?.flats.find(f=>f.id===params.get('flat'));
 if(!flat)return {status:404,body:{error:'Unit not found'}};
 return {status:200,body:{estateId:estate.id,buildingId:building.id,flatId:flat.id,outline:outline(estate,building),windows:flat.windows.map(w=>pick(w,['id','nameTC','nameEN','latitude','longitude','heading','tilt','roll','confidence','windowVerified','georefVerified','allowApproximate','cameraOffsetMeters']))}};
}
export async function api(req,res,next) {
 const url=new URL(req.url,'http://localhost');
 if(!url.pathname.startsWith('/api/'))return next();
 try {
 if(await auth.handle(req,res,url.pathname))return;
 if(AUTH_REQUIRED && !auth.authorize(req,res,url.pathname))return;
 }catch{send(res,503,{error:'Data service unavailable'});return;}
 const result=req.method==='GET'?lookup(url.pathname,url.searchParams):{status:405,body:{error:'Method not allowed'}};
 res.writeHead(result.status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});
 res.end(JSON.stringify(result.body));
}
