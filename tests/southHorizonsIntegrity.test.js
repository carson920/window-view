import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {lookup} from '../server/api.mjs';
import {getFloors} from '../src/propertyData.js';
import {calculateCamera} from '../src/cameraCalculator.js';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url)));
const job='data/south-horizons-approved-job';
const audit=read(`${job}/integrity-audit.json`);
const estate=read('data/properties.json').estates.find(e=>e.id==='south-horizons');
function inside([x,y],ring){let hit=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])hit=!hit;}return hit;}
test('production counts reconcile and reviewed exclusions cannot leak',()=>{
 assert.equal(estate.buildings.length,31);
 assert.equal(estate.buildings.flatMap(b=>b.flats).flatMap(f=>f.windows).length,910);
 assert.equal(read(`${job}/processing-report.json`).publishedWindows,910);
 assert.equal(audit.productionWindowCount,910);
 for(const id of ['1','3','6'])assert.ok(!estate.buildings.some(b=>b.id===`tower-${id}`));
 assert.ok(!estate.buildings.find(b=>b.id==='tower-10').flats.find(f=>f.id==='h').windows.some(w=>w.id==='master'));
});
test('each production window has valid identity, provenance, positive transform and correct source/proxy distinction',()=>{
 for(const b of estate.buildings){
  const r=read(`data/south-horizons-${b.id}/result.json`),s=r.transform;
  const ring=read(`data/south-horizons-${b.id}/official-footprint.json`).geometry.rings[0],factor=read(`data/south-horizons-${b.id}/placement.json`).factor;
  assert.equal(s.reflected,false);assert.ok(s.scaleMetresPerCanvasPixel>0);assert.ok(s.rmsMetres<=1.5);assert.equal(r.qa.pass,true);
  const keys=new Set();
  for(const f of b.flats)for(const w of f.windows){
   assert.ok('ABCDEFGH'.includes(f.label));assert.ok(['living','master','bedroom-1','bedroom-2'].includes(w.id));
   const key=f.id+'/'+w.id;assert.ok(!keys.has(key));keys.add(key);
   assert.ok(w.source&&w.sourceTraceFile&&w.research.sources.every(s=>typeof s==='string'&&s.startsWith('https://')));
   assert.deepEqual(w.floorApplicability,{min:b.floors.min,max:b.floors.max});assert.ok(w.interiorNormalDot<0&&w.cameraOutside);assert.deepEqual(w.qaErrors,[]);
   for(const distance of [0,.25,.5,1,1.5,2])assert.equal(inside([w.longitude+Math.sin(w.heading*Math.PI/180)*distance/factor[0],w.latitude+Math.cos(w.heading*Math.PI/180)*distance/factor[1]],ring),false,`${b.id}/${f.id}/${w.id}`);
   const check=audit.normalChecks.find(n=>n.tower===b.id.slice(6).toUpperCase()&&n.flat===f.label&&n.room===w.id);
   assert.ok(Math.abs((check.heading-w.heading+540)%360-180)<1e-7);
   if(w.id==='living'){
    assert.ok(check.localRoomSideSupported);assert.ok(check.centreAloneUnsafe);
    const [p,q]=w.sourcePlanSegment;
    for(let i=0;i<2;i++){
     assert.ok(Math.abs(w.proxyPlanSegment[0][i]-(p[i]+.06*(q[i]-p[i])))<1e-8);
     assert.ok(Math.abs(w.proxyPlanSegment[1][i]-(q[i]-.06*(q[i]-p[i])))<1e-8);
    }
    assert.equal(w.planSegmentRole,'camera-proxy-trimmed-6-percent-each-end');
   }
  }
 }
});
test('special floors cannot select or obtain typical cameras, including API floor requests',()=>{
 for(const v of audit.specialFloors){
  const b=estate.buildings.find(b=>b.id===`tower-${v.tower.toLowerCase()}`);
  if(!b)continue;
  assert.ok(!getFloors(b).includes(v.floor));
  assert.equal(calculateCamera(estate,b,b.flats[0].windows[0],v.floor),null);
  const res=lookup('/api/unit',new URLSearchParams({estate:estate.id,building:b.id,flat:'a',floor:String(v.floor)}));
  assert.equal(res.status,422);assert.equal(res.body.code,'FLOOR_DATA_UNAVAILABLE');assert.equal(res.body.windows,undefined);
 }
});
