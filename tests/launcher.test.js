import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { buildLandsdViewUrl, validateCamera } from '../src/landsdUrl.js';
import { calculateAltitude, calculateCamera } from '../src/cameraCalculator.js';
import { getBuildings, getFlats, getWindows, getFloors } from '../src/propertyData.js';
const data = JSON.parse(readFileSync(new URL('../data/properties.json', import.meta.url)));
const estate = data.estates[0], building = estate.buildings[0], window = building.flats[0].windows[0];
const camera = { latitude: 22.3, longitude: 114.2, altitude: 11.5, heading: 90, tilt: 90, roll: 0 };
test('LandsD URL has ordered camera values and Chinese locale', () => {
 assert.equal(buildLandsdViewUrl(camera), 'https://3d.map.gov.hk/mapviewer/app/map?flyto=22.3,114.2,11.5,90,90,0&l=zh-HK');
});
test('null, missing, strings, nonfinite and out-of-range cameras fail', () => {
 for (const key of Object.keys(camera)) for (const value of [null, undefined, NaN, Infinity, '0']) {
  assert.equal(validateCamera({...camera, [key]: value}), false);
  assert.throws(() => buildLandsdViewUrl({...camera, [key]: value}));
 }
 assert.equal(validateCamera({...camera, latitude: 91}), false);
 assert.equal(validateCamera({...camera, longitude: -181}), false);
 assert.equal(validateCamera({...camera, heading: -1}), false);
});
test('altitude formula requires verified real inputs; zero is valid', () => {
 const model = {type:'formula', referenceFloor:1, referenceAltitude:0, floorToFloor:3, verified:true};
 assert.equal(calculateAltitude(model, 20), 58.5);
 assert.equal(calculateAltitude({...model, verified:false}, 20), null);
 assert.equal(calculateAltitude({...model, referenceAltitude:null}, 20), null);
});
test('changing floor only changes altitude', () => {
 const cameras = [5,20,35].map(floor => calculateCamera(estate,building,window,floor,data.eyeHeight));
 assert.deepEqual(cameras.map(c => c.altitude), [23.5,68.5,113.5]);
 for (const c of cameras) assert.deepEqual({...c, altitude:0}, {...camera, altitude:0});
 assert.equal(calculateCamera(estate,building,window,4), null);
});
test('unresolved geometry and unverified real records are blocked', () => {
 assert.equal(calculateCamera(estate,building,building.flats[0].windows[1],5),null);
 assert.equal(calculateCamera({...estate,synthetic:false},building,window,5),null);
 assert.ok(calculateCamera({...estate,synthetic:false},{...building,floorModel:{...building.floorModel,verified:true}},{...window,windowVerified:true,confidence:'verified'},5));
});
test('dependent filters stay within selected parents', () => {
 assert.equal(getBuildings(data,estate.id).length,2);
 assert.deepEqual(getFlats(data,estate.id,'test-b').map(f=>f.id),['c']);
 assert.equal(getWindows(data,estate.id,'test-a','b')[0].id,'side');
 assert.deepEqual(getWindows(data,estate.id,'test-b','a'),[]);
 assert.deepEqual(getBuildings(data,'missing'),[]);
 const expanded = {...data,estates:[...data.estates,{id:'other',buildings:[]}]};
 assert.deepEqual(getBuildings(expanded,'other'),[]);
 assert.equal(getFloors(building).includes(13),false);
 assert.equal(getFloors(building).at(-1),40);
});
test('approved approximate YOHO view enables only the sourced 3/F height', () => {
 const real = data.estates.find(e => e.id === 'yoho-west');
 const tower = real.buildings.find(b => b.id === 'tower-2b');
 const win = tower.flats[0].windows[0];
 assert.deepEqual(calculateCamera(real,tower,win,3), {latitude:22.4595,longitude:114.0024,altitude:28.9,heading:36,tilt:0.1,roll:0});
 assert.equal(win.windowVerified,false);
 assert.equal(calculateCamera(real,tower,{...win,allowApproximate:false},3),null);
 for (const floor of getFloors(tower).filter(f => f !== 3)) assert.equal(calculateCamera(real,tower,win,floor),null);
 assert.equal(calculateCamera(real,tower,{...win,latitude:null},3),null);
});
test('all six Kingswood first towers have eight distinct registered proxies and honestly estimated heights', () => {
 const estates = data.estates.filter(e => e.id.startsWith('kingswood-'));
 assert.equal(estates.length,6);
 for (const estate of estates) {
  const tower=estate.buildings[0];
  assert.equal(tower.floorModel.verified,false);
  assert.equal(tower.floorModel.confidence,'estimated');
  assert.deepEqual(tower.flats.map(f=>f.label),Array.from('ABCDEFGH'));
  const cameras=tower.flats.map(f=>calculateCamera(estate,tower,f.windows[0],3));
  assert.ok(cameras.every(Boolean));
  assert.equal(new Set(cameras.map(c=>`${c.latitude},${c.longitude}`)).size,8);
  assert.equal(calculateAltitude({...tower.floorModel,allowEstimated:false},3),null);
  assert.equal(calculateCamera(estate,tower,tower.flats[0].windows[0],getFloors(tower).at(-1)+1),null);
  for (const flat of tower.flats) {
   const win=flat.windows[0];
   assert.equal(win.windowVerified,false);
   assert.equal(win.research.horizontalGeometry.status,'derived-from-plan-and-LandsD');
   assert.equal(calculateCamera(estate,tower,{...win,allowApproximate:false},3),null);
   const low=calculateCamera(estate,tower,win,3), high=calculateCamera(estate,tower,win,4);
   assert.deepEqual({...low,altitude:0},{...high,altitude:0});
   assert.ok(high.altitude>low.altitude);
  }
 }
});
test('Chestwood G is a southeast-quadrant facade normal, not the old arbitrary bedroom edge', () => {
 const real = data.estates.find(e => e.id === 'kingswood-chestwood');
 const tower = real.buildings[0];
 assert.equal(getFlats(data,real.id,tower.id).length,8);
 assert.equal(getFloors(tower).length,32);
 const camera = calculateCamera(real,tower,tower.flats.find(f=>f.id==='g').windows[0],3);
 assert.ok(camera.heading>90 && camera.heading<180);
 assert.notEqual(camera.heading,151.8);
 assert.equal(tower.floorModel.referenceFloor,0);
 assert.deepEqual(getFlats(data,'yoho-west','tower-1'),[]);
});
