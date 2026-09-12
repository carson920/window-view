import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {lookup} from '../server/api.mjs';
const read=p=>JSON.parse(fs.readFileSync(new URL('../'+p,import.meta.url)));
const summary=read('data/laguna-approved-job/registration-summary.json');
const data=read('data/properties.json').estates.find(e=>e.id==='laguna-city');
function inside([x,y],ring){let hit=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])hit=!hit;}return hit;}
test('Approved package covers 38 distinct official towers without silently dropping failed jobs',()=>{
 assert.equal(summary.length,38);assert.equal(new Set(summary.map(r=>r.csuid)).size,38);
 assert.deepEqual(data.buildings.map(b=>Number(b.id.split('-')[1])),summary.filter(r=>r.qaPass).map(r=>r.tower));
 assert.equal(data.buildings.flatMap(b=>b.flats.flatMap(f=>f.windows)).length,1064);
});
test('Laguna published floor ranges include Block 18 and the 24–26 1–26/F group',()=>{
 const expected={18:[1,25],24:[1,26],25:[1,26],26:[1,26],31:[1,27]};
 for(const [tower,[min,max]] of Object.entries(expected)){
  const floors=data.buildings.find(b=>b.id===`tower-${tower}`).floors;
  assert.deepEqual([floors.min,floors.max],[min,max]);
  assert.equal(floors.verified,true);
 }
});
for(const record of summary)test(`Approved Laguna ${record.tower}: semantic placement, window tangent, official clearance and API`,()=>{
 const r=read(`data/laguna-tower-${record.tower}/approved-result.json`),o=read(`data/laguna-tower-${record.tower}/official-footprint.json`);
 assert.ok(r.qa.pass,JSON.stringify(r.qa.errors));assert.equal(r.buildingCsuid,o.attributes.BuildingCSUID);
 assert.equal(o.attributes.BuildingNameEN,`Laguna City Block ${record.tower}`);
 assert.equal(r.windows.length,28);assert.ok(r.transform.rmsMetres<1.5);
 assert.equal(Object.keys(r.transform.semanticErrors).length,8);
 for(const v of Object.values(r.transform.semanticErrors))assert.ok(v.error<=40);
 // Independently calculate the normal orthogonality including reflections.
 const t=r.transform,angle=t.rotationDegrees*Math.PI/180;
 for(const w of r.windows){
  assert.deepEqual(w.qaErrors,[]);assert.ok(w.interiorNormalDot<0);
  assert.ok(!inside([w.cameraLng,w.cameraLat],o.geometry.rings[0]));
  assert.ok(Math.abs(w.facadeDistanceMeters)<=2);assert.ok(w.cameraOffsetMetres>=1&&w.cameraOffsetMetres<=3);
  const [a,b]=w.planSegment,dx=(b[0]-a[0])*(t.reflected?-1:1),dy=-(b[1]-a[1]);
  const east=dx*Math.cos(angle)-dy*Math.sin(angle),north=dx*Math.sin(angle)+dy*Math.cos(angle),h=w.heading*Math.PI/180;
  assert.ok(Math.abs(east*Math.sin(h)+north*Math.cos(h))<1e-6);
  assert.ok(Number.isFinite(w.projectedFacadeLat)&&Number.isFinite(w.projectedFacadeLng));
  assert.equal(w.georefVerified,false);
 }
 for(const flat of 'abcdefgh'){
  const api=lookup('/api/unit',new URLSearchParams({estate:'laguna-city',building:`tower-${record.tower}`,flat}));
  assert.equal(api.status,200);assert.deepEqual(api.body.outline,o.geometry.rings[0]);
  for(const w of api.body.windows){const src=r.windows.find(v=>v.flat.toLowerCase()===flat&&v.id===w.id);assert.equal(w.latitude,src.cameraLat);assert.equal(w.longitude,src.cameraLng);assert.equal(w.heading,src.heading);}
 }
});
test('Inset variants and source-specific bedroom orientations are not collapsed',()=>{
 for(const [n,id] of [[1,'L01-special'],[13,'L01-special'],[15,'L02-special'],[20,'L11-special'],[25,'L04-standard'],[30,'L04-standard'],[32,'L05-special'],[33,'L06-special'],[34,'L05-special']])assert.equal(read(`data/laguna-tower-${n}/approved-result.json`).annotation.templateId,id);
 for(const n of [2,4,6,8])assert.ok(read(`data/laguna-tower-${n}/approved-result.json`).transform.rotationDegrees>300);
 for(const n of [11,21,23])assert.equal(read(`data/laguna-tower-${n}/approved-result.json`).transform.reflected,true);
 const b=data.buildings.find(b=>b.id==='tower-38');for(const f of b.flats.filter(f=>'bc'.includes(f.id)))assert.deepEqual(f.windows.map(w=>w.id),['living','bedroom-1','bedroom-2']);
});
