import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {lookup} from '../server/api.mjs';
const read=p=>JSON.parse(fs.readFileSync(new URL('../'+p,import.meta.url)));
const data=read('data/properties.json');
function inside([x,y],ring){let result=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])result=!result;}return result;}
const ids={2:'4152918738T20050430',3:'4150618718T20050430',4:'4148218700T20050430'};
for(const tower of [2,3,4])test(`Laguna ${tower}: correct variant, independent footprint, all room views and API`,()=>{
 const r=read(`data/laguna-tower-${tower}/result.json`),o=read(`data/laguna-tower-${tower}/official-footprint.json`);
 const previous=read(`data/laguna-tower-${tower-1}/result.json`);
 assert.equal(r.buildingCsuid,ids[tower]);assert.ok(r.origin[0]<previous.origin[0]&&r.origin[1]<previous.origin[1]);
 assert.ok(r.transform.rmsMetres<.6);assert.equal(r.windows.length,28);
 assert.ok(r.annotation.layoutVerification.applicableTowers.includes(tower));
 assert.deepEqual(r.annotation.insetTranslations,{});
 assert.equal(Boolean(r.annotation.sourceCanvasTransform),tower%2===0);
 if(tower%2===0){assert.ok(r.annotation.sourceCanvasTransform.rmsePixels<4);assert.ok(r.annotation.rooms.A[0][1][0]<r.annotation.rooms.D[0][1][0]);}
 const building=data.estates.find(e=>e.id==='laguna-city').buildings.find(b=>b.id===`tower-${tower}`);
 assert.equal(building.flats.length,8);
 for(const flat of building.flats){
  const api=lookup('/api/unit',new URLSearchParams({estate:'laguna-city',building:building.id,flat:flat.id}));
  assert.equal(api.status,200);assert.deepEqual(api.body.outline,o.geometry.rings[0]);
  assert.equal(api.body.windows.length,'ADEH'.includes(flat.label)?4:3);
  for(const w of flat.windows){
   assert.ok(!inside([w.longitude,w.latitude],o.geometry.rings[0]));
   assert.ok(w.interiorNormalDot<0&&Math.abs(w.facadeDistanceMeters)<1);
   assert.ok(Number.isFinite(w.heading));assert.equal(w.georefVerified,false);
   const generated=r.windows.find(v=>v.flat===flat.label&&v.id===w.id);
   assert.equal(w.latitude,generated.cameraLat);assert.equal(w.heading,generated.heading);
  }
 }
 const base=read('data/laguna-tower-1/result.json');
 for(const flat of ['B','C'])assert.notDeepEqual(r.annotation.rooms[flat][1].slice(1,3),base.annotation.rooms[flat][1].slice(1,3));
});
