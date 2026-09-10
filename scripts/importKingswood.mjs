import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8'));
const write=(f,v)=>fs.writeFileSync(path.join(root,f),JSON.stringify(v,null,2)+'\n');
const results=read('data/kingswood-registration/all-phases.json');
const manifest=read('data/kingswood-first-towers-manifest.json');
const checks=read('data/kingswood-direction-validation.json').checks;
const data=read('data/properties.json');
const service='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0';
data.estates=data.estates.filter(e=>!e.id.startsWith('kingswood-'));
const fixture=data.estates.find(e=>e.id==='synthetic-test')?.buildings.find(b=>b.id==='test-b');
if(fixture)fixture.floorModel={type:'formula',referenceFloor:null,referenceAltitude:null,floorToFloor:null,verified:false,source:null};
const records=[];
for(const r of results){
 const entry=manifest.phases.find(p=>p.phase===r.phase);
 const best=r.candidates[0];
 const alternatives=r.candidates.filter(c=>Math.abs(((c.rotationDegrees-best.rotationDegrees+540)%360)-180)>15);
 const gap=alternatives.length?Math.min(...alternatives.map(c=>c.rmsMetres))-best.rmsMetres:null;
 const check=checks.find(c=>c.phase===r.phase);
 const confidence=r.phase===5?'low':'moderate';
 const model={type:'formula',referenceFloor:0,referenceAltitude:r.attributes.BaseHeight,floorToFloor:(r.attributes.TopHeight-r.attributes.BaseHeight)/r.attributes.Storeys,verified:false,allowEstimated:true,confidence:'estimated',source:service,note:'Derived building-average floor elevation — not verified. Assumes G/F at BaseHeight, floor number times (TopHeight−BaseHeight)/Storeys, plus eye height. No verified floor slab, podium, roof, storey-count or vertical-datum correction.'};
 const flats=[];
 for(const [flat,f] of Object.entries(r.facades)){
  const horizontalGeometry={status:'derived-from-plan-and-LandsD',confidence,facadeMidpoint:f.facadeMidpoint,cameraProxyMeters:1,registrationRmsMetres:+best.rmsMetres.toFixed(2),registrationP95Metres:+best.p95Metres.toFixed(2),nextRotationGapMetres:gap===null?null:+gap.toFixed(2),handedness:'Uses unmirrored, explicitly named first-tower plan. Comparable mirror diagnostics retained; plan identity and independent coarse direction checks support review, not survey verification.',accuracyNote:'RMS is fit residual, not absolute position accuracy or a confidence interval. Simplified footprint, hand tracing and glazing inset remain uncertain.'};
  const heading={status:'derived-from-facade-normal',confidence,degrees:f.heading,accuracyNote:'0.1-degree storage is numerical output, not angular accuracy; manually traced facade proxy.'};
  const verticalGeometry={status:'estimated',confidence:'low',verified:false,method:model.note,model};
  const research={noteTC:`水平為平面圖配準估算（${confidence==='low'?'低':'中等'}可信度）；高度為建築平均估算，未核實。${r.phase===5?'鏡像候選未能完全排除。':''}`,noteEN:`Registered horizontal proxy (${confidence} confidence); estimated building-average altitude, unverified.${r.phase===5?' Mirror ambiguity remains.':''}`,horizontalGeometry,heading,verticalGeometry,independentDirectionCheck:{...check,calculatedDegrees:r.facades[check.flat].heading,usedInOptimisation:false},registrationFile:`data/kingswood-registration/phase-${r.phase}.json`,sources:[entry.floorPlanUrl,entry.estatePage,service,check.source]};
  const base={latitude:f.lat,longitude:f.lng,heading:f.heading,tilt:0.1,roll:0,cameraOffsetMeters:1,windowVerified:false,confidence:'review',allowApproximate:true,source:entry.floorPlanUrl,research};
  flats.push({id:flat.toLowerCase(),label:flat,windows:[
    {id:'living-main',nameTC:'客廳外牆 proxy（估算）',nameEN:'Living-room facade proxy (approximate)',...base},
    {id:'bedroom-main',nameTC:'睡房窗 proxy（估算）',nameEN:'Bedroom window proxy (approximate)',...base}
  ]});
  const altitude=Math.round((model.referenceAltitude+3*model.floorToFloor+1.5)*10)/10;
  records.push({estate:'嘉湖山莊',phase:r.phase,court:r.courtTC,building:1,floor:3,flat,window:'Living-room facade proxy',lat:f.lat,lng:f.lng,heading:f.heading,altitude,altitudeStatus:'estimated',horizontalGeometry,headingGeometry:heading,verticalGeometry,sourceUrls:research.sources,extractionMethod:'Manual trace of own first-tower plan; 72 rotation seeds, symmetric ICP and Chamfer refinement in local WGS84 ellipsoid metre frame; translation, rotation, uniform scale; no physical reflection applied. Facade midpoint + 1 m outward normal. CW/CCW and cyclic order do not define geographic orientation.',flytoUrl:`https://3d.map.gov.hk/mapviewer/app/map?flyto=${f.lat},${f.lng},${altitude},${f.heading},0.1,0&l=zh-HK`});
 }
 const slug=r.courtEN.split(' ')[0].toLowerCase();
 data.estates.push({id:`kingswood-${slug}`,synthetic:false,nameTC:`嘉湖山莊・${r.phase}期 ${r.courtTC}`,nameEN:`Kingswood · Phase ${r.phase} ${r.courtEN}`,defaultBuildingId:'tower-1',source:entry.estatePage,buildings:[{id:'tower-1',nameTC:'第1座',nameEN:'Tower 1',governmentBuildingId:r.attributes.BuildingCSUID,floors:{...entry.floorRangeTypical,excluded:[],source:entry.floorPlanUrl,note:entry.note??'Only stated typical-floor scope'},floorModel:model,flats}]});
 entry.officialFootprintStatus='retrieved';entry.officialFootprintFile=r.officialFile;entry.buildingCSUID=r.attributes.BuildingCSUID;entry.registrationStatus='derived-provisional';
}
data.defaultEstateId='kingswood-chestwood';
write('data/properties.json',data);write('data/kingswood-first-towers-manifest.json',manifest);
write('data/kingswood-48-stacks.json',{scope:'6 first towers × A–H; sample floor 3; use floorModel for other covered typical floors',records});
const columns=['phase','court','building','floor','flat','lat','lng','heading','altitude','altitudeStatus','horizontalConfidence','verticalConfidence','flytoUrl'];
fs.writeFileSync(path.join(root,'data/kingswood-48-stacks.csv'),[columns.join(','),...records.map(r=>columns.map(c=>JSON.stringify(c==='horizontalConfidence'?r.horizontalGeometry.confidence:c==='verticalConfidence'?'low':r[c])).join(','))].join('\n')+'\n');
console.log(`Imported ${results.length} first towers, ${records.length} stacks. Heights remain verified:false.`);
