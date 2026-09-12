import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {mapLayout} from '../src/osmPreview.js';
const read=p=>JSON.parse(fs.readFileSync(new URL('../'+p,import.meta.url)));
const data=read('data/properties.json');
const source=read('data/chestwood-tower-2/result.json');
function inside(p,ring){let yes=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])yes=!yes;}return yes;}
for(const [court,phase,count] of [['locwood',1,14],['maywood',6,8],['kenswood',7,14]]){
 test(`${court}: all towers have independent geometry, correct template mapping and centered maps`,()=>{
  const e=data.estates.find(e=>e.id===`kingswood-${court}`);assert.equal(e.buildings.length,count);
  const ids=new Set(),centers=new Set();
  for(let tower=1;tower<=count;tower++){
   const r=read(`data/${court}-tower-${tower}/result.json`),o=read(r.officialFile),ring=o.geometry.rings[0],b=e.buildings.find(b=>b.id===`tower-${tower}`);
   ids.add(r.buildingCsuid);assert.equal(r.buildingCsuid,o.attributes.BuildingCSUID);assert.equal(o.attributes.BuildingNameEN,`${court[0].toUpperCase()+court.slice(1)} Court Block ${tower}`);
   assert.ok(r.transform.rmsMetres<2);assert.equal(r.windows.length,30);assert.equal(b.flats.length,8);assert.equal(b.floors.max,r.maxFloor);
   const expectedMirror=phase===1?tower>=8:phase===6?tower%2===1:[1,2,4,6,8,10,12].includes(tower);assert.equal(r.transform.reflected,expectedMirror);
   for(const w of r.windows){
    assert.ok(!inside([w.cameraLng,w.cameraLat],ring));assert.ok(w.interiorNormalDot<0);assert.ok(Math.abs(w.facadeDistanceMeters)<5);
    const sourceFlat=Object.keys(r.annotation.stackMapping).find(k=>r.annotation.stackMapping[k]===w.flat);
    assert.deepEqual(r.annotation.rooms[w.flat],source.annotation.rooms[sourceFlat]);
    const s=source.windows.find(s=>s.flat===sourceFlat&&s.id===w.id);
    const heading=expectedMirror?-s.heading-source.transform.rotationDegrees-r.transform.rotationDegrees:s.heading+source.transform.rotationDegrees-r.transform.rotationDegrees;
    assert.ok(Math.abs((w.heading-heading+1260)%360-180)<1e-6);
    const saved=b.flats.find(f=>f.label===w.flat).windows.find(s=>s.id===w.id);assert.equal(saved.latitude,w.cameraLat);assert.equal(saved.longitude,w.cameraLng);assert.equal(saved.georefVerified,false);
   }
   const m=mapLayout(ring,b.flats[0].windows[0],800,320),xs=m.outline.map(p=>p[0]),ys=m.outline.map(p=>p[1]);
   assert.ok(Math.abs((Math.min(...xs)+Math.max(...xs))/2-400)<1e-6);assert.ok(Math.abs((Math.min(...ys)+Math.max(...ys))/2-160)<1e-6);centers.add(m.center.join(','));
  }
  assert.equal(ids.size,count);assert.equal(centers.size,count);
 });
}
