import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {lookup} from './server/api.mjs';
const job='data/city-one-shatin-v6.2',read=p=>JSON.parse(fs.readFileSync(new URL(p,import.meta.url)));
const report=read(`${job}/processing-report.json`),issues=read(`${job}/needs-review.json`),traces=read(`${job}/canonical-window-traces.json`),estate=read('data/properties.json').estates.find(e=>e.id==='city-one-shatin');
const results=report.towers.map(t=>read(`${job}/review-results/tower-${t.tower}/result.json`));
test('City One v6.2: approved transforms and source geometry remain unchanged',()=>{
 for(const r of results){const folder=`review-results/tower-${r.tower}`;const old=read(`${job}/${folder}/previous-result.json`);assert.deepEqual(r.transform,old.transform);assert.deepEqual(r.orientationEvidence,old.orientationEvidence);assert.deepEqual(read(`${job}/${folder}/official-footprint.json`).geometry,read(`data/city-one-shatin-approved-job/${folder}/official-footprint.json`).geometry);}
});
test('City One v6.2: recognized bay faces retain source evidence and are not whole perimeters',()=>{
 const samples=read(`${job}/window-samples/window-pattern-samples.json`).items;
 let bays=0;
 for(const f of traces.families)for(const w of f.windows){assert.ok(samples.some(s=>s.id===w.recognitionEvidence));assert.ok(['sill-line','bay-window-face'].includes(w.representationClass));assert.equal(w.p1.length,2);assert.equal(w.p2.length,2);if(w.representationClass==='bay-window-face')bays++;}
 assert.ok(bays>100);
 for(const r of results)for(const w of r.productionWindows){assert.ok(w.representationClass&&w.recognitionEvidence);const f=traces.families.find(f=>f.familyId===r.annotation.templateId),trace=f.windows.find(t=>t.flat===w.flat&&t.id===w.id);assert.deepEqual(w.sourcePlanSegment,[trace.p1,trace.p2]);}
});
test('City One v6.2: all review callouts are English, outward and non-overlapping',()=>{
 const files=results.flatMap(r=>['window-review','family-diff-overlay','approved-overlay'].map(n=>`${job}/review-results/tower-${r.tower}/${n}.labels.json`));
 for(const file of files){const {labels}=read(file);assert.ok(labels.length);for(let i=0;i<labels.length;i++){const a=labels[i],b=a.box;assert.match(a.text,/^[\x20-\x7e]+$/);assert.ok(a.outwardNormal.reduce((v,n,k)=>v+n*((b[k]+b[k+2])/2-a.windowMidpoint[k]),0)>0);for(const other of labels.slice(i+1)){const c=other.box;assert.ok(b[2]<c[0]||b[0]>c[2]||b[3]<c[1]||b[1]>c[3],file);}}}
});
function inside(p,ring){let c=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])c=!c;}return c;}
test('City One: 52 towers independently registered with fixed approved handedness',()=>{
 assert.equal(results.length,52);assert.equal(new Set(results.map(r=>r.buildingCsuid)).size,52);
 for(const r of results){assert.equal(r.transform.reflected,false);assert.ok(r.transform.scaleMetresPerCanvasPixel>0);assert.equal(r.transform.rotationDegrees,r.orientationEvidence.fixedRotationDegrees);assert.ok(r.transform.rmsMetres<=1.5);assert.ok(r.orientationEvidence.northUp);}
});
test('City One: canonical family reuse has exact structural evidence and original endpoints',()=>{
 assert.equal(traces.families.length,14);
 for(const f of traces.families){assert.ok(f.windows.length);const bytes=fs.readFileSync(`${job}/floorplans/H-${f.canonicalTower}-typ.jpg`);assert.equal(createHash('sha256').update(bytes).digest('hex'),f.sourceImageSha256);for(const w of f.windows)for(const p of [w.p1,w.p2,w.interiorWitness])assert.ok(p[0]>=0&&p[1]>=0&&p[0]<f.sourceImageSize[0]&&p[1]<f.sourceImageSize[1]);}
 for(const v of read(`${job}/family-verification.json`)){assert.ok(v.pass_);assert.equal(v.determinant,1);assert.ok(v.exactRoiPixels||v.coreLabelOnly);}
});
test('City One: production counts reconcile; reviewed exclusions cannot leak',()=>{
 const actual=estate.buildings.flatMap(b=>b.flats.flatMap(f=>f.windows.map(w=>[Number(b.id.split('-')[1]),f.label,w])));
 assert.equal(estate.buildings.length,report.towersRepresented);assert.equal(actual.length,report.productionWindowCount);
 for(const [t,f,w] of actual){assert.ok(!issues.some(i=>i.tower===t&&i.flat===f&&i.room===w.id),`${t}/${f}/${w.id}`);assert.deepEqual(w.sourcePlanSegment,w.planSegment);assert.ok(w.sourceImage&&w.sourceSha256&&w.research.sources.every(Boolean));assert.ok(w.windowVerified&&w.georefVerified);assert.deepEqual(w.qaErrors,[]);}
 for(const r of results){assert.equal(actual.filter(([t])=>t===r.tower).length,r.productionWindows.length);assert.equal(r.productionWindows.length,report.towers.find(t=>t.tower===r.tower).productionWindowCount);}
});
test('City One: recomputed normals face away from room witness and cameras are outside',()=>{
 for(const r of results){const ring=read(`${job}/review-results/tower-${r.tower}/official-footprint.json`).geometry.rings[0];
  for(const w of r.productionWindows){const source=r.annotation.rooms[w.flat].find(x=>x[0]===w.id);const mid=[(source[1][0]+source[2][0])/2,-(source[1][1]+source[2][1])/2];const v=[source[3][0]-mid[0],-source[3][1]-mid[1]];const a=r.transform.rotationDegrees*Math.PI/180,world=[v[0]*Math.cos(a)-v[1]*Math.sin(a),v[0]*Math.sin(a)+v[1]*Math.cos(a)];const h=w.heading*Math.PI/180,n=[Math.sin(h),Math.cos(h)];assert.ok(n[0]*world[0]+n[1]*world[1]<0);assert.ok(!inside([w.cameraLng,w.cameraLat],ring));assert.ok(!inside([w.cameraLng+n[0]*2/r.factor[0],w.cameraLat+n[1]*2/r.factor[1]],ring));assert.ok(Math.abs(w.facadeDistanceMeters)<=2);assert.ok(w.cameraOffsetMetres<=3);}
 }
});
test('City One: catalog, per-unit footprint and unsupported floors are explicit',()=>{
 assert.ok(lookup('/api/catalog',new URLSearchParams()).body.estates.some(e=>e.id===estate.id));
 for(const b of estate.buildings){const p=new URLSearchParams({estate:estate.id,building:b.id,flat:b.flats[0].id,floor:String(b.floors.min)});const r=lookup('/api/unit',p);assert.equal(r.status,200);assert.ok(r.body.outline.length>3);assert.ok(r.body.windows.length);p.set('floor',String(b.floors.max+1));assert.equal(lookup('/api/unit',p).body.code,'FLOOR_DATA_UNAVAILABLE');}
 const p=new URLSearchParams({estate:estate.id,building:'tower-8',flat:estate.buildings.find(b=>b.id==='tower-8').flats[0].id,floor:'28'});assert.equal(lookup('/api/unit',p).status,422);
});
