import fs from 'node:fs';
const read=p=>JSON.parse(fs.readFileSync(new URL('../'+p,import.meta.url)));
const data=read('data/properties.json');
const buildings=[];
const approved=fs.existsSync(new URL('../data/laguna-approved-job/registration-summary.json',import.meta.url));
const approvedTowers=approved?read('data/laguna-approved-job/registration-summary.json').filter(r=>r.qaPass).map(r=>r.tower):[1,2,3,4];
for(const tower of approvedTowers) {
 const folder=`data/laguna-tower-${tower}`;
 const resultFile=`${folder}/${approved?'approved-result':'result'}.json`;
 if(!fs.existsSync(new URL(`../${resultFile}`,import.meta.url)))continue;
 const r=read(resultFile),o=read(`${folder}/official-footprint.json`),a=o.attributes;
 if(approved && (!r.qa?.pass || r.windows.some(w=>w.qaErrors.length)))throw Error(`Tower ${tower} failed approved QA`);
 // Published source sheets explicitly state these ranges. Missing ranges
 // receive one demo floor only, not Storeys-1 disguised as numbered floors.
 const known=tower<=8?[1,27]:tower>=13&&tower<=15?[1,28]:[16,17,19,20,21,22,23].includes(tower)?[1,25]:[9,10,11,12,24,25,26,27,28,29,30,31,32,33,35,36,37,38].includes(tower)?[1,27]:tower===34?[2,27]:null;
 const floors=known?{min:known[0],max:known[1],excluded:[],verified:true,source:'Approved L02/L06/L07/L09/L10/L11 printed floor-range labels'}:{min:1,max:1,excluded:[],verified:false,scope:'Single 1/F demo only; approved source does not specify numbered floor range'};
 if(approved){
  fs.writeFileSync(new URL(`../${folder}/result.json`,import.meta.url),JSON.stringify(r,null,2)+'\n');
  fs.writeFileSync(new URL(`../${folder}/annotations.json`,import.meta.url),JSON.stringify(r.annotation,null,2)+'\n');
 }
 buildings.push({id:`tower-${tower}`,nameTC:`第${tower}座`,nameEN:`Tower ${tower}`,governmentBuildingId:r.buildingCsuid,source:r.annotation.sourcePage,
  floors,
  floorModel:{type:'formula',referenceFloor:0,referenceAltitude:a.BaseHeight,floorToFloor:(a.TopHeight-a.BaseHeight)/a.Storeys,verified:false,allowEstimated:true,confidence:'estimated',note:'Building-average floor elevation, not a verified floor datum.'},
  flats:[...'ABCDEFGH'].map(flat=>({id:flat.toLowerCase(),label:flat,windows:r.windows.filter(w=>w.flat===flat).map(w=>({...w,
   nameTC:({living:'客廳',master:'主人房','bedroom-1':'睡房1','bedroom-2':'睡房2'}[w.id])+'窗（配準估算）',nameEN:w.id,
   latitude:w.cameraLat,longitude:w.cameraLng,tilt:.1,roll:0,allowApproximate:true,source:r.annotation.sourcePage,
   research:{noteTC:'按批准美林物業圖則窗線配準本座官方輪廓；中原北向上截圖約束 A–H；高度估算。',
    approvedJob:r.approvedJob,templateId:r.annotation.templateId,variantNote:r.annotation.reviewNotes,orientationEvidence:r.orientationEvidence,confidenceDimensions:r.confidenceDimensions,
    windowExtraction:r.annotation.extractionMethod,horizontalGeometry:{status:'derived-from-plan-and-LandsD',confidence:'review',registrationRmsMetres:r.transform.rmsMetres},
    registrationFile:resultFile,sources:[r.annotation.sourcePage,r.annotation.source,o.provenance.queryUrl]}
  }))}))});
}
const estate={id:'laguna-city',nameTC:'麗港城',nameEN:'Laguna City',buildings};
const index=data.estates.findIndex(e=>e.id===estate.id);
if(index<0)data.estates.push(estate);else data.estates[index]=estate;
fs.writeFileSync(new URL('../data/properties.json',import.meta.url),JSON.stringify(data,null,2)+'\n');
