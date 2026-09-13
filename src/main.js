import { displayName } from './presentation.js';
import { renderEstateReview } from './estateReview.js';
import { renderOsm } from './osmPreview.js';
import './style.css';
import './preview.css';
import { getEstate, getBuildings, getFlats, getWindows, getFloors } from './propertyData.js';
import { calculateCamera } from './cameraCalculator.js';
import { buildLandsdViewUrl } from './landsdUrl.js';
const $ = id => document.getElementById(id);
const name = item => `${item.nameTC} · ${item.nameEN}`;
const fill = (id, items, label = name) => { $(id).replaceChildren(...(items.length ? items.map(item => new Option(label(item), item.id)) : [new Option('資料待補 · Not yet available', '')])); $(id).disabled = !items.length; };
function sunlightScore(window) {
  if (!window || !Number.isFinite(window.heading)) return null;
  const heading = ((window.heading % 360) + 360) % 360;
  const distanceFromSouth = Math.abs(180 - heading);
  return Math.round(100 - (distanceFromSouth * 80 / 180));
}
let floors = [];
let data={estates:[]}, activeWindows=[], activeOutline=null, selectedWindowId=null, reviewBuildings=null, requestId=0, loadStatus='請按「載入單位資料」';
function selection() {
  const estate = getEstate(data, $('estate').value);
  const building = getBuildings(data, estate?.id).find(item => item.id === $('building').value);
  const window = activeWindows.find(item => item.id === selectedWindowId);
  const floor = $('floor').value === '' ? null : Number($('floor').value);
  return { estate, building, window, floor };
}
function cameraState() {
  const selected = selection();
  const camera = calculateCamera(selected.estate, selected.building, selected.window, selected.floor, data.eyeHeight ?? 1.5);
  return { ...selected, camera, url: camera ? buildLandsdViewUrl(camera) : null };
}
function render() {
  const { estate, building, window, floor, camera, url } = cameraState();
  $('status').textContent = camera ? (estate.synthetic ? '合成測試景觀 · Synthetic camera ready' : '景觀已就緒 · View ready') : loadStatus;
  const score = sunlightScore(window);
  $('camera-values').replaceChildren(...[['緯度 Latitude', camera?.latitude ?? window?.latitude], ['經度 Longitude', camera?.longitude ?? window?.longitude], ['高度 Altitude', camera ? `${camera.altitude.toFixed(1)} m` : null], ['方向 Heading', camera?.heading ?? window?.heading], ['日照分數 Sunlight score', score === null ? null : `${score}/100 · 方向估算`], ['傾角 Tilt', camera?.tilt ?? window?.tilt]].flatMap(([label, value]) => {
    const dt = document.createElement('dt'); dt.textContent = label;
    const dd = document.createElement('dd'); dd.textContent = value ?? '—'; return [dt, dd];
  }));
  $('view').disabled = !url;
  try { renderMapPreview(estate, window); } catch (error) { console.warn('preview render failed', error); }
  renderEstateReview($('estate-review'),estate,building,$('flat').value,activeWindows,activeOutline);
  renderEstateReview($('estate-overview'),estate,building,$('flat').value,[],null,reviewBuildings);
  $('debug').textContent = JSON.stringify({ estateId: estate?.id ?? null, buildingId: building?.id ?? null, floor, flatId: $('flat').value || null, windowId: window?.id ?? null, latitude: window?.latitude ?? null, longitude: window?.longitude ?? null, altitude: camera?.altitude ?? null, heading: window?.heading ?? null, tilt: window?.tilt ?? null, confidence: window?.confidence ?? null, windowVerified: window?.windowVerified ?? false, synthetic: estate?.synthetic ?? false, research: window?.research ?? null, generatedLandsdUrl: url }, null, 2);
}
function renderMapPreview(estate, selectedWindow) {
  const svg=$('map-preview');
  const anchor=activeWindows.find(w=>Number.isFinite(w.latitude)&&Number.isFinite(w.longitude));
  if(anchor)renderOsm($('osm-frame'),activeOutline,selectedWindow||anchor,Boolean(selectedWindow));
  const north='<text class="preview-north" x="330" y="24" text-anchor="middle">N</text><path d="M330 53 V32 M324 39 L330 32 L336 39" fill="none" stroke="#172e3c" stroke-width="2"/>';
  let shape='',wx=180,wy=108;
  if(activeOutline){
    const xs=activeOutline.map(p=>p[0]),ys=activeOutline.map(p=>p[1]);
    const minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys);
    const scale=Math.min(270/(maxX-minX),150/(maxY-minY)),tx=180-(maxX-minX)*scale/2;
    const xy=p=>[(p[0]-minX)*scale+tx,190-(p[1]-minY)*scale];
    shape=`<polygon class="preview-footprint" points="${activeOutline.map(p=>xy(p).join(',')).join(' ')}"/>`;
    if(selectedWindow)[wx,wy]=xy([selectedWindow.longitude,selectedWindow.latitude]);
  }else{
    shape='<rect class="preview-footprint" x="70" y="38" width="220" height="140" rx="12"/><text class="preview-label" x="12" y="202">示意輪廓 · Schematic footprint</text>';
  }
  let marker='';
  if(selectedWindow){
    const rad=(selectedWindow.heading||0)*Math.PI/180,ex=wx+Math.sin(rad)*25,ey=wy-Math.cos(rad)*25;
    marker=`<line class="preview-normal" x1="${wx}" y1="${wy}" x2="${ex}" y2="${ey}"/><circle class="preview-camera" cx="${wx}" cy="${wy}" r="7"/>`;
  }
  if(svg){svg.style.transform='none';svg.innerHTML=shape+marker+north;}
}
function renderWindowButtons(){
 $('window-buttons').replaceChildren(...activeWindows.map(w=>{
  const button=document.createElement('button');button.type='button';button.textContent=displayName(w.nameTC);
  button.setAttribute('aria-pressed',String(w.id===selectedWindowId));
  button.addEventListener('click',()=>{selectedWindowId=w.id;renderWindowButtons();render();});return button;
 }));
}
function windowsChanged() {
  ++requestId;activeWindows=[];activeOutline=null;selectedWindowId=null;renderWindowButtons();
  reviewBuildings=null; document.querySelector('[data-review-section]')?.setAttribute('hidden','');
  setResultsVisible(false);
  $('osm-frame').replaceChildren();
  loadStatus='請按「載入單位資料」· Press Load unit';
  $('load-unit').disabled=!$('flat').value;
  $('load-unit').textContent='載入單位資料 · Load unit';render();
}
async function loadUnit() {
  if($('load-unit').disabled)return;
  const token=++requestId;
  activeWindows=[];activeOutline=null;selectedWindowId=null;renderWindowButtons();$('osm-frame').replaceChildren();render();
  $('load-unit').disabled=true;$('load-unit').textContent='載入中…';
  loadStatus='載入所選單位 · Loading unit…';$('status').textContent=loadStatus;
  const params=new URLSearchParams({estate:$('estate').value,building:$('building').value,flat:$('flat').value,floor:$('floor').value});
  try {
    const response=await fetch('/api/unit?'+params);
    if(response.status===401){if(token===requestId)showLogin();return;}
    if(response.status===429){if(token===requestId){loadStatus='已達查詢限額，請 '+response.headers.get('Retry-After')+' 秒後再試';$('status').textContent=loadStatus;};return;}
    if(!response.ok)throw new Error('Unit request failed');
    const unit=await response.json();
    if(token!==requestId)return;
    setResultsVisible(true);activeWindows=unit.windows;activeOutline=unit.outline;selectedWindowId=null;reviewBuildings=null;document.querySelector('[data-review-section]')?.setAttribute('hidden','');renderWindowButtons();loadStatus=activeWindows.length?'請選擇下方窗口 · Select a window':'此單位暫無可用窗資料';render();
    try { const review=await fetch('/api/estate-review?estate='+encodeURIComponent($('estate').value)); if(review.ok){reviewBuildings=(await review.json()).buildings;document.querySelector('[data-review-section]')?.removeAttribute('hidden');render();} } catch { /* selected-unit review remains available */ }
    document.querySelector('.map-preview-card')?.scrollIntoView({behavior:'smooth',block:'start'});
  } catch(error) {
    if(token!==requestId)return;
    loadStatus='未能載入單位，請按掣重試 · Unable to load unit';$('status').textContent=loadStatus;
  } finally {
    if(token===requestId){$('load-unit').disabled=activeWindows.length>0;$('load-unit').textContent=activeWindows.length?'已載入 · Loaded':'載入單位資料 · Load unit';}
  }
}
function buildingChanged() {
  const building = selection().building;
  floors = getFloors(building);
  fill('floor', floors.map(floor => ({ id: String(floor) })), item => `${item.id}/F`);
  fill('flat', getFlats(data, $('estate').value, $('building').value), item => item.label); windowsChanged();
}
function estateChanged() { fill('building', getBuildings(data, $('estate').value)); const preferred = getEstate(data, $('estate').value)?.defaultBuildingId; if (preferred && getBuildings(data, $('estate').value).some(b => b.id === preferred)) $('building').value = preferred; buildingChanged(); }
$('load-unit').addEventListener('click',loadUnit);
$('estate').addEventListener('change', estateChanged); $('building').addEventListener('change', buildingChanged); $('flat').addEventListener('change', windowsChanged);
$('floor').addEventListener('change', windowsChanged);
$('view').addEventListener('click', () => { const { url } = cameraState(); if (url) window.open(url, '_blank', 'noopener,noreferrer'); });
function setResultsVisible(visible){
 document.querySelectorAll('[data-loaded-section]').forEach(section=>{section.hidden=!visible;});
 document.querySelector('.layout').classList.toggle('awaiting-load',!visible);
}
function showLogin(){
 setResultsVisible(false);
 ++requestId;activeWindows=[];activeOutline=null;data={estates:[]};
 $('osm-frame').replaceChildren();$('estate-review').replaceChildren();$('debug').textContent='';$('camera-values').replaceChildren();
 document.querySelector('main').hidden=true;$('login-panel').hidden=false;
}
async function init(){
 try{
  const response=await fetch('/api/catalog');if(!response.ok)throw Error();
  data=await response.json();$('login-panel').hidden=true;document.querySelector('main').hidden=false;
  fill('estate',data.estates);if(getEstate(data,data.defaultEstateId))$('estate').value=data.defaultEstateId;estateChanged();
 }catch{showLogin();$('login-status').textContent='未能連接資料服務，請稍後重新載入';}
}
$('login-form').addEventListener('submit',async event=>{
 event.preventDefault();const button=event.target.querySelector('button');button.disabled=true;
 try{
  const response=await fetch('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:$('username').value,password:$('password').value})});
  $('password').value='';
  if(!response.ok){$('login-status').textContent=response.status===429?'登入嘗試過多，請稍後再試':'登入失敗，請檢查帳戶及密碼';return;}
  $('login-status').textContent='';await init();
 }catch{$('login-status').textContent='連線失敗，請重試';}finally{button.disabled=false;}
});
$('logout').addEventListener('click',async()=>{
 const response=await fetch('/api/auth/logout',{method:'POST'}).catch(()=>null);
 if(response?.ok){showLogin();}else{$('status').textContent='登出失敗，請重試';}
});
init();

let mapResizeTimer; window.addEventListener("resize",()=>{clearTimeout(mapResizeTimer);mapResizeTimer=setTimeout(()=>render(),100);});
