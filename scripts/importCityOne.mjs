import fs from 'node:fs';
import {createHash} from 'node:crypto';
const root=new URL('../',import.meta.url), job=process.env.CITY_ONE_JOB||'data/city-one-shatin-v6.2';
const read=p=>JSON.parse(fs.readFileSync(new URL(p,root),'utf8'));
const report=read(`${job}/processing-report.json`),data=read('data/properties.json');
const buildings=[];
for(const t of report.towers){
 const folder=`${job}/review-results/tower-${t.tower}`,r=read(`${folder}/result.json`),o=read(`${folder}/official-footprint.json`),a=o.attributes;
 if(!r.productionWindows.length)continue;
 if(!r.qa.transformPass||r.transform.reflected||r.transform.rmsMetres>1.5||!(r.transform.scaleMetresPerCanvasPixel>0))throw Error(`Invalid transform ${t.tower}`);
 for(const w of r.productionWindows){
  if(w.qaErrors.length||!w.cameraOutside||!(w.interiorNormalDot<0)||!w.georefVerified)throw Error(`Invalid window ${t.tower}/${w.flat}/${w.id}`);
  const hash=createHash('sha256').update(fs.readFileSync(new URL(`${job}/floorplans/H-${t.tower}-typ.jpg`,root))).digest('hex');
  if(w.sourceSha256!==hash)throw Error('Stale source');
 }
 if(![a.BaseHeight,a.TopHeight,a.Storeys].every(Number.isFinite)||a.Storeys<=0||a.TopHeight<=a.BaseHeight)throw Error(`Invalid floor model ${t.tower}`);
 const name=id=>id.startsWith('living')?`客廳${id==='living-side'?'側面':''}`:`睡房${id.match(/\d+/)?.[0]||''}${id.endsWith('side')?'側面':''}`;
 buildings.push({id:`tower-${t.tower}`,nameTC:`第${t.tower}座`,nameEN:`Tower ${t.tower}`,governmentBuildingId:r.buildingCsuid,geometryFile:`${folder}/official-footprint.json`,source:r.annotation.sourcePage,
 floors:{min:r.floors[0],max:r.floors[1],excluded:[],verified:t.tower!==8,source:r.annotation.source,scope:'Approved typical floor plan only; unmapped floors unavailable'},
 floorModel:{type:'formula',referenceFloor:0,referenceAltitude:a.BaseHeight,floorToFloor:(a.TopHeight-a.BaseHeight)/a.Storeys,verified:false,allowEstimated:true,confidence:'estimated',note:'Derived building-average elevation; not verified floor-to-floor height.'},
 flats:[...new Set(r.productionWindows.map(w=>w.flat))].sort().map(flat=>({id:flat.toLowerCase(),label:flat,windows:r.productionWindows.filter(w=>w.flat===flat).map(w=>({...w,nameTC:name(w.id),nameEN:w.id,latitude:w.cameraLat,longitude:w.cameraLng,cameraOffsetMeters:w.cameraOffsetMetres,tilt:.1,roll:0,allowApproximate:true,allowEstimated:true,source:r.annotation.sourcePage,
 sourcePlanSegment:w.sourcePlanSegment,planSegmentRole:w.sourceExtentRole,floorApplicability:{min:r.floors[0],max:r.floors[1]},
 research:{templateId:t.familyId,orientationEvidence:r.orientationEvidence,confidenceDimensions:r.confidenceDimensions,registrationFile:`${folder}/result.json`,windowExtraction:r.annotation.extractionMethod,sources:[r.annotation.source,r.annotation.sourcePage,o.provenance.queryUrl]}
 }))}))});
}
const estate={id:'city-one-shatin',nameTC:'沙田第一城',nameEN:'City One Shatin',defaultBuildingId:buildings[0].id,buildings};
const index=data.estates.findIndex(e=>e.id===estate.id);if(index<0)data.estates.push(estate);else data.estates[index]=estate;
const count=buildings.flatMap(b=>b.flats).flatMap(f=>f.windows).length;
if(count!==report.productionWindowCount||buildings.length!==report.towersRepresented)throw Error('Report count mismatch');
fs.writeFileSync(new URL('data/properties.json',root),JSON.stringify(data,null,2)+'\n');
console.log(`Imported City One Shatin: ${buildings.length} towers, ${count} windows; unresolved rooms excluded.`);
