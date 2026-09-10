import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const read=p=>JSON.parse(fs.readFileSync(new URL('../'+p,import.meta.url)));
const result=read('data/chestwood-tower-2/result.json');
const estate=read('data/properties.json').estates.find(e=>e.id==='kingswood-chestwood');
test('Tower 1 reflects the complete confirmed Tower 2 template onto its own footprint',()=>{
 const mirrored=read('data/chestwood-tower-1/result.json');
 assert.equal(mirrored.buildingCsuid,'1797235344T20050430');
 assert.equal(mirrored.transform.reflected,true);
 assert.ok(mirrored.transform.rmsMetres<1.2);
 assert.deepEqual(mirrored.annotation.rooms,result.annotation.rooms);
 assert.equal(mirrored.windows.length,30);
 for(const w of mirrored.windows){
  const source=result.windows.find(s=>s.flat===w.flat&&s.id===w.id);
  assert.ok(w.cameraOutside);
  assert.ok(w.interiorNormalDot<0);
  const expected=(-source.heading-result.transform.rotationDegrees-mirrored.transform.rotationDegrees+720)%360;
  assert.ok(Math.abs(((w.heading-expected+540)%360)-180)<1e-6);
  const saved=estate.buildings.find(b=>b.id==='tower-1').flats.find(f=>f.label===w.flat).windows.find(s=>s.id===w.id);
  assert.equal(saved.latitude,w.cameraLat);
  assert.equal(saved.longitude,w.cameraLng);
  assert.notEqual(saved.latitude,source.cameraLat);
 }
});
test('Small-bedroom numbering runs from near to far relative to living room',()=>{
 for(const flat of ['A','B','C','D','G','H']){
  const rooms=result.annotation.rooms[flat];
  const interior=id=>rooms.find(r=>r[0]===id)[3];
  const living=interior('living');
  const distance=id=>Math.hypot(...interior(id).map((v,i)=>v-living[i]));
  assert.ok(distance('bedroom-1')<distance('bedroom-2'),`${flat}: bedroom 1 must be nearer the living room`);
 }
});
test('Reviewed sill lines determine bedroom directions without a blanket 90-degree rule',()=>{
 const separation=(a,b)=>Math.abs(((a-b+540)%360)-180);
 for(const flat of ['A','B','C','D','G','H']){
  const windows=result.windows.filter(w=>w.flat===flat);
  const master=windows.find(w=>w.id==='master');
  for(const id of ['bedroom-1','bedroom-2']){
   const bedroom=windows.find(w=>w.id===id);
   const expected=id==='bedroom-2' && ['A','D','H'].includes(flat) ? 0 : 90;
   assert.ok(Math.abs(separation(bedroom.heading,master.heading)-expected)<0.01,`${flat} ${id} must match reviewed sill orientation`);
  }
 }
});
test('Tower 2 uses independent 2/4/6 labelled tracing and all eight stacks',()=>{
 assert.equal(result.buildingCsuid,'1799735365T20050430');
 assert.equal(result.windows.length,30);
 assert.deepEqual([...new Set(result.windows.map(w=>w.flat))],[...'ABCDEFGH']);
 assert.ok(result.transform.rmsMetres<1.2);
 assert.equal(result.transform.reflected,false);
 for(const w of result.windows){
  assert.ok(w.interiorNormalDot<0,`${w.flat} ${w.id} must face away from room interior`);
  assert.ok(w.cameraOutside,`${w.flat} ${w.id} camera must clear polygon`);
  assert.ok(Number.isFinite(w.projectedFacadeLat));
  assert.ok(Math.abs(w.facadeDistanceMeters)<5);
  const saved=estate.buildings.find(b=>b.id==='tower-2').flats.find(f=>f.label===w.flat).windows.find(v=>v.id===w.id);
  assert.equal(saved.latitude,w.cameraLat);assert.equal(saved.longitude,w.cameraLng);
  assert.equal(saved.georefVerified,false);
 }
});
