import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const read=p=>JSON.parse(fs.readFileSync(new URL('../'+p,import.meta.url)));
const estate=read('data/properties.json').estates.find(e=>e.id==='kingswood-lynwood');
const source=read('data/chestwood-tower-2/result.json');
for(const tower of [1,2,3,4,5,6,7,8,9,10]) test(`Tower ${tower} retains confirmed template and uses independent official placement`,()=>{
 const r=read(`data/lynwood-tower-${tower}/result.json`);
 const o=read(`data/kingswood-footprints/phase-5-tower-${tower}-official-footprint.json`);
 assert.equal(r.buildingCsuid,o.attributes.BuildingCSUID);
 assert.equal(r.transform.reflected,[1,2,4,6,8].includes(tower));
 assert.ok(r.transform.rmsMetres<1.2);
 assert.deepEqual(r.annotation.rooms,source.annotation.rooms);
 assert.equal(r.windows.length,30);
 const building=estate.buildings.find(b=>b.id===`tower-${tower}`);
 assert.equal(building.flats.length,8);
 for(const w of r.windows){
  assert.ok(w.cameraOutside,`${w.flat}/${w.id}`);
  assert.ok(w.interiorNormalDot<0);
  assert.ok(Math.abs(w.facadeDistanceMeters)<5);
  const s=source.windows.find(s=>s.flat===w.flat&&s.id===w.id);
  const expected=[1,2,4,6,8].includes(tower) ? -s.heading-source.transform.rotationDegrees-r.transform.rotationDegrees : s.heading+source.transform.rotationDegrees-r.transform.rotationDegrees;
  assert.ok(Math.abs(((w.heading-expected+1080+180)%360)-180)<1e-6);
  const saved=building.flats.find(f=>f.label===w.flat).windows.find(s=>s.id===w.id);
  assert.equal(saved.latitude,w.cameraLat);assert.equal(saved.longitude,w.cameraLng);
  assert.notEqual(saved.latitude,s.cameraLat);
 }
});
