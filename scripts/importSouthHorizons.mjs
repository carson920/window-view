import fs from 'node:fs';
import { createHash } from 'node:crypto';
const path = p => new URL('../'+p, import.meta.url);
const read = p => JSON.parse(fs.readFileSync(path(p)));
const jobPath='data/south-horizons-approved-job';
const audit=read(`${jobPath}/artifact-audit.json`);
// Refuse stale QA if any registered artifact has changed since the audit.
for(const [file,hash] of Object.entries(audit.preservedArtifactSha256)) {
  if(createHash('sha256').update(fs.readFileSync(path(file))).digest('hex')!==hash)throw Error(`Stale audit: ${file}`);
}
const buildings=audit.towers.filter(t=>t.publicationPass).map(t=>{
  const folder=`data/south-horizons-tower-${t.tower.toLowerCase()}`;
  const r=read(`${folder}/result.json`), o=read(`${folder}/official-footprint.json`), a=o.attributes;
  if(!r.qa.pass || r.windows.some(w=>w.qaErrors.length))throw Error(`Failed QA: ${t.tower}`);
  if(![a.BaseHeight,a.TopHeight,a.Storeys].every(Number.isFinite)||a.Storeys<=0||a.TopHeight<=a.BaseHeight)throw Error(`Invalid floor model: ${t.tower}`);
  return {id:`tower-${t.tower.toLowerCase()}`,nameTC:`第${t.tower}座`,nameEN:`Tower ${t.tower}`,governmentBuildingId:r.buildingCsuid,source:r.annotation.sourcePage,
    floors:{min:t.floors[0],max:t.floors[1],excluded:[],verified:true,source:r.annotation.source,scope:'Approved typical plan only; unprocessed floor variants excluded'},
    floorModel:{type:'formula',referenceFloor:0,referenceAltitude:a.BaseHeight,floorToFloor:(a.TopHeight-a.BaseHeight)/a.Storeys,verified:false,allowEstimated:true,confidence:'estimated',note:'Derived building-average elevation; not verified floor-to-floor height.'},
    flats:[...'ABCDEFGH'].map(flat=>({id:flat.toLowerCase(),label:flat,windows:r.windows.filter(w=>w.flat===flat).map(w=>({...w,
      nameTC:({living:'客廳',master:'主人房','bedroom-1':'睡房1','bedroom-2':'睡房2'})[w.id],nameEN:w.id,
      latitude:w.cameraLat,longitude:w.cameraLng,cameraOffsetMeters:w.cameraOffsetMetres,tilt:.1,roll:0,allowApproximate:true,source:r.annotation.sourcePage,
      research:{approvedJob:r.approvedJob,templateId:r.annotation.templateId,orientationEvidence:r.orientationEvidence,confidenceDimensions:r.confidenceDimensions,
        windowExtraction:r.annotation.extractionMethod,horizontalGeometry:{status:'derived-from-plan-and-LandsD',confidence:'review',registrationRmsMetres:r.transform.rmsMetres},
        registrationFile:`${folder}/result.json`,sources:[r.annotation.sourcePage,r.annotation.source,o.provenance.queryUrl]}
    }))}))};
});
const data=read('data/properties.json');
const estate={id:'south-horizons',nameTC:'海怡半島',nameEN:'South Horizons',defaultBuildingId:buildings[0].id,buildings};
const index=data.estates.findIndex(e=>e.id===estate.id);
if(index<0)data.estates.push(estate);else data.estates[index]=estate;
fs.writeFileSync(path('data/properties.json'),JSON.stringify(data,null,2)+'\n');
console.log(`Imported South Horizons: ${buildings.length} towers, ${buildings.flatMap(b=>b.flats).flatMap(f=>f.windows).length} windows`);
