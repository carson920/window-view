import fs from 'node:fs';
const read=p=>JSON.parse(fs.readFileSync(new URL('../'+p,import.meta.url)));
const data=read('data/properties.json');
const buildings=[];
for(const tower of [1,2,3,4]) {
 const folder=`data/laguna-tower-${tower}`;
 if(!fs.existsSync(new URL(`../${folder}/result.json`,import.meta.url)))continue;
 const r=read(`${folder}/result.json`),o=read(`${folder}/official-footprint.json`),a=o.attributes;
 buildings.push({id:`tower-${tower}`,nameTC:`第${tower}座`,nameEN:`Tower ${tower}`,governmentBuildingId:r.buildingCsuid,source:r.annotation.sourcePage,
  floors:{min:1,max:27,excluded:[]},
  floorModel:{type:'formula',referenceFloor:0,referenceAltitude:a.BaseHeight,floorToFloor:(a.TopHeight-a.BaseHeight)/a.Storeys,verified:false,allowEstimated:true,confidence:'estimated',note:'Building-average floor elevation, not a verified floor datum.'},
  flats:[...'ABCDEFGH'].map(flat=>({id:flat.toLowerCase(),label:flat,windows:r.windows.filter(w=>w.flat===flat).map(w=>({...w,
   nameTC:({living:'客廳',master:'主人房','bedroom-1':'睡房1','bedroom-2':'睡房2'}[w.id])+'窗（配準估算）',nameEN:w.id,
   latitude:w.cameraLat,longitude:w.cameraLng,tilt:.1,roll:0,allowApproximate:true,source:r.annotation.sourcePage,
   research:{noteTC:`按美林物業窗線配準；${tower===1?'B、C 採第1座特別版':'B、C 採標準版'}，轉角細房用兩端連線。高度估算。`,
    windowExtraction:r.annotation.extractionMethod,horizontalGeometry:{status:'derived-from-plan-and-LandsD',confidence:'review',registrationRmsMetres:r.transform.rmsMetres},
    registrationFile:`${folder}/result.json`,sources:[r.annotation.sourcePage,r.annotation.source,o.provenance.queryUrl]}
  }))}))});
}
const estate={id:'laguna-city',nameTC:'麗港城',nameEN:'Laguna City',buildings};
const index=data.estates.findIndex(e=>e.id===estate.id);
if(index<0)data.estates.push(estate);else data.estates[index]=estate;
fs.writeFileSync(new URL('../data/properties.json',import.meta.url),JSON.stringify(data,null,2)+'\n');
