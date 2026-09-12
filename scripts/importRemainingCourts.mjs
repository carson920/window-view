import fs from 'node:fs';
const root=new URL('../',import.meta.url),read=p=>JSON.parse(fs.readFileSync(new URL(p,root)));
const data=read('data/properties.json');
for(const [court,phase,count] of [['locwood',1,14],['maywood',6,8],['kenswood',7,14]]){
 const estate=data.estates.find(e=>e.id===`kingswood-${court}`);
 const buildings=[];
 for(let tower=1;tower<=count;tower++){
  const file=`data/${court}-tower-${tower}/result.json`,r=read(file),o=read(r.officialFile),a=o.attributes;
  buildings.push({id:`tower-${tower}`,nameTC:`第${tower}座`,nameEN:`Tower ${tower}`,governmentBuildingId:r.buildingCsuid,source:r.annotation.layoutSource,floors:{min:1,max:r.maxFloor,excluded:[]},floorModel:{type:'formula',referenceFloor:0,referenceAltitude:a.BaseHeight,floorToFloor:(a.TopHeight-a.BaseHeight)/a.Storeys,verified:false,allowEstimated:true,confidence:'estimated',note:'Building-average elevation; floor datum unverified. Typical floors only; roof duplex excluded.'},flats:[...'ABCDEFGH'].map(flat=>({id:flat.toLowerCase(),label:flat,windows:r.windows.filter(w=>w.flat===flat).map(w=>({...w,nameTC:w.id==='living'?'客廳外牆窗（配準估算）':w.id==='master'?'主人房窗（配準估算）':`睡房${w.id.split('-')[1]}窗（配準估算）`,nameEN:w.id,latitude:w.cameraLat,longitude:w.cameraLng,tilt:.1,roll:0,allowApproximate:true,source:r.annotation.layoutSource,research:{windowExtraction:r.annotation.extractionMethod,templateRevision:r.annotation.revision,noteTC:'按本期平面圖單位編號及鏡像分組套用窗線，配準本座官方輪廓；窗位及高度估算。',noteEN:'Plan-labelled template fitted to this tower official footprint; estimated windows and height.',horizontalGeometry:{status:'derived-from-plan-and-LandsD',confidence:'review',registrationRmsMetres:r.transform.rmsMetres},registrationFile:file,sources:[r.annotation.layoutSource,r.annotation.reviewSource,o.provenance.queryUrl]}}))}))});
 }
 estate.buildings=buildings;
}
fs.writeFileSync(new URL('data/properties.json',root),JSON.stringify(data,null,2)+'\n');
console.log('Imported 36 towers, 1080 window proxies');
