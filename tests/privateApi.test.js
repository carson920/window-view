import test from 'node:test';
import assert from 'node:assert/strict';
import { catalog, lookup } from '../server/api.mjs';
import { readFileSync, readdirSync } from 'node:fs';
test('catalog contains selectors but no window geometry',()=>{
 const text=JSON.stringify(catalog);
 for(const key of ['windows','latitude','longitude','heading'])assert.equal(text.includes('"'+key+'"'),false,key);
});
test('unit API returns exactly the requested flat and rejects bulk requests',()=>{
 const estate=catalog.estates[0],building=estate.buildings[0],flat=building.flats[0];
 const params=new URLSearchParams({estate:estate.id,building:building.id,flat:flat.id});
 const response=lookup('/api/unit',params);
 assert.equal(response.status,200);assert.equal(response.body.flatId,flat.id);assert.ok(response.body.windows.length);
 assert.equal(response.body.estates,undefined);
 params.append('flat','other');assert.equal(lookup('/api/unit',params).status,400);
 assert.equal(lookup('/api/unit',new URLSearchParams({estate:'*',building:'*',flat:'*'})).status,404);
 assert.equal(lookup('/api/all',params).status,404);
});
test('production build does not copy private data or bundle a known coordinate',()=>{
 const files=readdirSync(new URL('../dist/',import.meta.url));assert.ok(!files.includes('data'));
 const raw=JSON.parse(readFileSync(new URL('../data/properties.json',import.meta.url)));
 const coordinate=raw.estates.flatMap(e=>e.buildings).flatMap(b=>b.flats).flatMap(f=>f.windows).find(w=>String(w.latitude).length>12).latitude;
 for(const file of readdirSync(new URL('../dist/assets/',import.meta.url)).filter(f=>f.endsWith('.js')))assert.ok(!readFileSync(new URL('../dist/assets/'+file,import.meta.url),'utf8').includes(String(coordinate)));
});
