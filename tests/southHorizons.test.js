import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { catalog, lookup } from '../server/api.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url)));
const audit=read('data/south-horizons-approved-job/artifact-audit.json');
const estate=read('data/properties.json').estates.find(e=>e.id==='south-horizons');

test('South Horizons publishes exactly audited towers and their independently registered windows',()=>{
  assert.equal(audit.towers.length,34);
  assert.deepEqual(estate.buildings.map(b=>b.id),audit.towers.filter(t=>t.publicationPass).map(t=>`tower-${t.tower.toLowerCase()}`));
  for(const b of estate.buildings){
    const result=read(`data/south-horizons-${b.id}/result.json`);
    assert.equal(result.qa.pass,true);assert.equal(b.governmentBuildingId,result.buildingCsuid);
    assert.equal(b.floorModel.verified,false);
    assert.deepEqual(b.flats.map(f=>f.label),[...'ABCDEFGH']);
    for(const flat of b.flats){
      const res=lookup('/api/unit',new URLSearchParams({estate:estate.id,building:b.id,flat:flat.id}));
      assert.equal(res.status,200);assert.ok(res.body.outline.length>10);
      assert.equal(res.body.windows.length,flat.windows.length);
      for(const w of flat.windows){
        const saved=result.windows.find(s=>s.flat===flat.label&&s.id===w.id);
        assert.equal(w.latitude,saved.cameraLat);assert.equal(w.longitude,saved.cameraLng);assert.equal(w.heading,saved.heading);
        assert.equal(saved.cameraOutside,true);assert.ok(saved.interiorNormalDot<0);assert.deepEqual(saved.qaErrors,[]);
      }
    }
  }
});
test('South Horizons review, floor variants and catalog privacy remain consistent',()=>{
  const e=catalog.estates.find(e=>e.id===estate.id);assert.equal(e.buildings.length,31);
  for(const id of ['tower-1','tower-3','tower-6'])assert.equal(lookup('/api/unit',new URLSearchParams({estate:estate.id,building:id,flat:'a'})).status,404);
  assert.equal(e.buildings.find(b=>b.id==='tower-13').floors.min,4);
  assert.equal(e.buildings.find(b=>b.id==='tower-30').floors.max,29);
  assert.equal(e.buildings.find(b=>b.id==='tower-33a').floors.max,30);
  assert.ok(!JSON.stringify(e).includes('cameraLat'));
  const review=lookup('/api/estate-review',new URLSearchParams({estate:estate.id}));
  assert.equal(review.status,200);assert.equal(review.body.buildings.length,31);
  assert.equal(review.body.buildings.flatMap(b=>b.flats).flatMap(f=>f.windows).length,911);
});
