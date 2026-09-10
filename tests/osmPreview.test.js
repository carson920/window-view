import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {mapLayout} from '../src/osmPreview.js';
test('OSM centers every selected tower and assembles distinct adjacent tiles',()=>{
 const centers=[];
 for(let tower=1;tower<=6;tower++){
  const f=JSON.parse(fs.readFileSync(new URL(`../data/kingswood-footprints/phase-2-tower-${tower}-official-footprint.json`,import.meta.url)));
  const outline=f.geometry.rings[0];
  const m=mapLayout(outline,{longitude:outline[0][0],latitude:outline[0][1]},800,320);
  const xs=m.outline.map(p=>p[0]),ys=m.outline.map(p=>p[1]);
  assert.ok(Math.abs((Math.min(...xs)+Math.max(...xs))/2-400)<1e-6);
  assert.ok(Math.abs((Math.min(...ys)+Math.max(...ys))/2-160)<1e-6);
  assert.equal(new Set(m.tiles.map(t=>`${t.x}/${t.y}`)).size,m.tiles.length);
  centers.push(m.center.join(','));
 }
 assert.equal(new Set(centers).size,6);
});
