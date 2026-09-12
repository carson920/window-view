import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const read=p=>JSON.parse(fs.readFileSync(new URL('../'+p,import.meta.url)));
const r=read('data/laguna-tower-1/result.json'),data=read('data/properties.json');
test('Laguna eight flats and 28 main room windows are published',()=>{
 const b=data.estates.find(e=>e.id==='laguna-city').buildings[0];
 assert.equal(b.flats.length,8);assert.equal(r.windows.length,28);
 for(const f of b.flats){assert.equal(f.windows.length,'ADEH'.includes(f.label)?4:3);for(const w of f.windows){const raw=r.windows.find(v=>v.flat===f.label&&v.id===w.id);assert.equal(w.latitude,raw.cameraLat);assert.equal(w.heading,raw.heading);}}
});
test('Laguna fit, outward normals and camera clearance pass',()=>{
 assert.equal(r.buildingCsuid,'4155218755T20050430');assert.ok(r.transform.rmsMetres<.6);
 for(const w of r.windows){assert.ok(w.interiorNormalDot<0);assert.ok(w.cameraOutside);assert.ok(Math.abs(w.facadeDistanceMeters)<2);assert.ok(Number.isFinite(w.lat)&&Number.isFinite(w.lng));assert.ok(w.heading>=0&&w.heading<360);assert.equal(w.georefVerified,false);}
});
test('Corner bedroom views join both outer endpoints, not one pane',()=>{
 for(const f of 'ABCDEFGH'){
  const w=r.windows.find(w=>w.flat===f&&w.id==='bedroom-1');
  const [a,corner,b]=w.cornerGlazingPlanPoints;
  assert.deepEqual(w.planSegment,[a,b]);
  assert.equal(w.viewGeometry,'corner-window-outer-endpoint-chord');
  const first=[corner[0]-a[0],corner[1]-a[1]],second=[b[0]-corner[0],b[1]-corner[1]];
  assert.ok(Math.abs(first[0]*second[0]+first[1]*second[1])/(Math.hypot(...first)*Math.hypot(...second))<.12);
  assert.ok(w.interiorNormalDot<0);assert.ok(w.cameraOutside);
  // Transform the chord tangent independently; heading must be its outward normal.
  const angle=r.transform.rotationDegrees*Math.PI/180;
  const east=(b[0]-a[0])*Math.cos(angle)+(b[1]-a[1])*Math.sin(angle);
  const north=(b[0]-a[0])*Math.sin(angle)-(b[1]-a[1])*Math.cos(angle);
  const heading=w.heading*Math.PI/180;
  assert.ok(Math.abs(east*Math.sin(heading)+north*Math.cos(heading))<1e-7);
 }
 for(const w of r.windows.filter(w=>w.id!=='bedroom-1'))assert.equal(w.cornerGlazingPlanPoints,undefined);
 assert.ok(r.annotation.source.startsWith('https://llam.com.hk/'));
});
