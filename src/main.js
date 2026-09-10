import { renderEstateReview } from './estateReview.js';
import lynwood1Footprint from '../data/kingswood-footprints/phase-5-tower-1-official-footprint.json';
import lynwood2Footprint from '../data/kingswood-footprints/phase-5-tower-2-official-footprint.json';
import lynwood3Footprint from '../data/kingswood-footprints/phase-5-tower-3-official-footprint.json';
import lynwood4Footprint from '../data/kingswood-footprints/phase-5-tower-4-official-footprint.json';
import lynwood5Footprint from '../data/kingswood-footprints/phase-5-tower-5-official-footprint.json';
import lynwood6Footprint from '../data/kingswood-footprints/phase-5-tower-6-official-footprint.json';
import lynwood7Footprint from '../data/kingswood-footprints/phase-5-tower-7-official-footprint.json';
import lynwood8Footprint from '../data/kingswood-footprints/phase-5-tower-8-official-footprint.json';
import lynwood9Footprint from '../data/kingswood-footprints/phase-5-tower-9-official-footprint.json';
import lynwood10Footprint from '../data/kingswood-footprints/phase-5-tower-10-official-footprint.json';
import sherwood1Footprint from '../data/kingswood-footprints/phase-2-tower-1-official-footprint.json';
import sherwood2Footprint from '../data/kingswood-footprints/phase-2-tower-2-official-footprint.json';
import sherwood3Footprint from '../data/kingswood-footprints/phase-2-tower-3-official-footprint.json';
import sherwood4Footprint from '../data/kingswood-footprints/phase-2-tower-4-official-footprint.json';
import sherwood5Footprint from '../data/kingswood-footprints/phase-2-tower-5-official-footprint.json';
import sherwood6Footprint from '../data/kingswood-footprints/phase-2-tower-6-official-footprint.json';
import { renderOsm } from './osmPreview.js';
import data from '../data/properties.json';
import './style.css';
import './preview.css';
import { getEstate, getBuildings, getFlats, getWindows, getFloors } from './propertyData.js';
import { calculateCamera } from './cameraCalculator.js';
import { buildLandsdViewUrl } from './landsdUrl.js';
import previewData from '../data/kingswood-preview.json';
import chestwood2Footprint from '../data/kingswood-footprints/phase-3-tower-2-official-footprint.json';
import chestwood3Footprint from '../data/kingswood-footprints/phase-3-tower-3-official-footprint.json';
import chestwood4Footprint from '../data/kingswood-footprints/phase-3-tower-4-official-footprint.json';
import chestwood5Footprint from '../data/kingswood-footprints/phase-3-tower-5-official-footprint.json';
import chestwood6Footprint from '../data/kingswood-footprints/phase-3-tower-6-official-footprint.json';
const $ = id => document.getElementById(id);
const name = item => `${item.nameTC} · ${item.nameEN}`;
const fill = (id, items, label = name) => { $(id).replaceChildren(...(items.length ? items.map(item => new Option(label(item), item.id)) : [new Option('資料待補 · Not yet available', '')])); $(id).disabled = !items.length; };
let floors = [];
function selection() {
  const estate = getEstate(data, $('estate').value);
  const building = getBuildings(data, estate?.id).find(item => item.id === $('building').value);
  const window = getWindows(data, estate?.id, building?.id, $('flat').value).find(item => item.id === $('window').value);
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
  document.querySelector('.notice').textContent = estate?.synthetic ? '僅供合成測試 · SYNTHETIC TEST ONLY' : '景觀預覽 · View preview — 估算窗位會清楚標示，並非實地量測。 Approximate positions are labelled and are not surveyed window locations.';
  $('floor-label').textContent = floor === null ? '—' : `${floor}/F`;
  $('floor-slider').value = Math.max(0, floors.indexOf(floor));
  $('floor-slider').setAttribute('aria-valuetext', `${floor ?? '—'}/F`);
  $('status').textContent = camera ? (estate.synthetic ? '合成測試景觀 · Synthetic camera ready' : (window.allowApproximate ? '估算景觀已就緒 · Approximate view ready' : '景觀已就緒 · View ready')) : '景觀資料尚未提供 · View geometry not yet available';
  if (window?.research) $('status').textContent += ' — ' + window.research.noteTC + ' ' + window.research.noteEN;
  const estimatedHeight = building?.floorModel?.confidence === 'estimated';
  $('camera-values').replaceChildren(...[['緯度 Latitude', camera?.latitude ?? window?.latitude], ['經度 Longitude', camera?.longitude ?? window?.longitude], [estimatedHeight ? '估算高度 Estimated altitude' : '高度 Altitude', camera ? `${camera.altitude.toFixed(1)} m${estimatedHeight ? ' · 未核實 / unverified' : ''}` : null], ['方向 Heading', camera?.heading ?? window?.heading], ['傾角 Tilt', camera?.tilt ?? window?.tilt]].flatMap(([label, value]) => {
    const dt = document.createElement('dt'); dt.textContent = label;
    const dd = document.createElement('dd'); dd.textContent = value ?? '—'; return [dt, dd];
  }));
  $('view').disabled = $('copy').disabled = !url;
  try { renderMapPreview(estate, window); } catch (error) { $('map-preview').innerHTML='<rect class="preview-footprint" x="65" y="40" width="230" height="135" rx="12"/><circle class="preview-camera" cx="180" cy="108" r="7"/><text class="preview-north" x="330" y="24">N</text><text class="preview-label" x="12" y="202">Preview temporarily using registered building frame</text>'; console.warn('preview render failed', error); }
  renderEstateReview($('estate-review'),estate);
  $('copy-status').textContent = '';
  $('debug').textContent = JSON.stringify({ estateId: estate?.id ?? null, buildingId: building?.id ?? null, floor, flatId: $('flat').value || null, windowId: window?.id ?? null, latitude: window?.latitude ?? null, longitude: window?.longitude ?? null, altitude: camera?.altitude ?? null, heading: window?.heading ?? null, tilt: window?.tilt ?? null, confidence: window?.confidence ?? null, windowVerified: window?.windowVerified ?? false, synthetic: estate?.synthetic ?? false, research: window?.research ?? null, generatedLandsdUrl: url }, null, 2);
}
function renderMapPreview(estate, selectedWindow) {
  const svg=$('map-preview'); if (!svg) return;
  svg.style.transform='none';
  const phaseNumber={"kingswood-locwood":1,"kingswood-sherwood":2,"kingswood-chestwood":3,"kingswood-lynwood":5,"kingswood-maywood":6,"kingswood-kenswood":7}[estate?.id];
  const towerFootprint=phaseNumber===3 ? {'tower-2':chestwood2Footprint,'tower-3':chestwood3Footprint,'tower-4':chestwood4Footprint,'tower-5':chestwood5Footprint,'tower-6':chestwood6Footprint}[selection().building?.id] : null;
  const sherwoodFootprint=phaseNumber===2 ? {'tower-1':sherwood1Footprint,'tower-2':sherwood2Footprint,'tower-3':sherwood3Footprint,'tower-4':sherwood4Footprint,'tower-5':sherwood5Footprint,'tower-6':sherwood6Footprint}[selection().building?.id] : null;
  const lynwoodFootprint=phaseNumber===5 ? {'tower-1':lynwood1Footprint,'tower-2':lynwood2Footprint,'tower-3':lynwood3Footprint,'tower-4':lynwood4Footprint,'tower-5':lynwood5Footprint,'tower-6':lynwood6Footprint,'tower-7':lynwood7Footprint,'tower-8':lynwood8Footprint,'tower-9':lynwood9Footprint,'tower-10':lynwood10Footprint}[selection().building?.id] : null;
  const record=lynwoodFootprint ? {outline:lynwoodFootprint.geometry.rings[0]} : sherwoodFootprint ? {outline:sherwoodFootprint.geometry.rings[0]} : towerFootprint ? {outline:towerFootprint.geometry.rings[0]} : previewData[phaseNumber];
  if(!selectedWindow?.latitude) { svg.innerHTML='<text x="50%" y="50%" text-anchor="middle" fill="currentColor">選擇單位以顯示位置 · Select a flat</text>'; return; }
  const frame=$('osm-frame'); if(frame) renderOsm(frame,record?.outline,selectedWindow);
  if(!record) { const cx=180, cy=108, rad=(selectedWindow.heading||0)*Math.PI/180, ex=cx+Math.sin(rad)*55, ey=cy-Math.cos(rad)*55; svg.innerHTML=`<rect class="preview-footprint" x="70" y="38" width="220" height="140" rx="12"/><line class="preview-normal" x1="${cx}" y1="${cy}" x2="${ex.toFixed(1)}" y2="${ey.toFixed(1)}"/><circle class="preview-camera" cx="${cx}" cy="${cy}" r="7"/><text class="preview-north" x="330" y="24">N</text><text class="preview-label" x="12" y="202">藍：示意 footprint · 紅：所選窗 · 線：向外 heading</text>`; return; }
  const pts=record.outline; const xs=pts.map(p=>p[0]), ys=pts.map(p=>p[1]); const minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys); const s=Math.min(270/(maxX-minX),150/(maxY-minY)); const tx=180-(maxX-minX)*s/2;
  const xy=p=>`${((p[0]-minX)*s+tx).toFixed(1)},${(190-(p[1]-minY)*s).toFixed(1)}`; const outline=record.outline.map(xy).join(' '); const wx=(selectedWindow.longitude-minX)*s+tx, wy=190-(selectedWindow.latitude-minY)*s; const rad=(selectedWindow.heading||0)*Math.PI/180; const ex=wx+Math.sin(rad)*25, ey=wy-Math.cos(rad)*25;
  svg.innerHTML=`<polygon class="preview-footprint" points="${outline}"/><line class="preview-normal" x1="${wx.toFixed(1)}" y1="${wy.toFixed(1)}" x2="${ex.toFixed(1)}" y2="${ey.toFixed(1)}"/><circle class="preview-camera" cx="${wx.toFixed(1)}" cy="${wy.toFixed(1)}" r="7"/><text class="preview-north" x="330" y="24">N</text><text class="preview-label" x="12" y="202">藍：LandsD footprint · 青：所選窗 · 線：向外 heading</text>`;
}
function windowsChanged() { fill('window', getWindows(data, $('estate').value, $('building').value, $('flat').value)); render(); }
function buildingChanged() {
  const building = selection().building;
  floors = getFloors(building);
  fill('floor', floors.map(floor => ({ id: String(floor) })), item => `${item.id}/F`);
  $('floor-slider').min = 0; $('floor-slider').max = Math.max(0, floors.length - 1); $('floor-slider').step = 1; $('floor-slider').disabled = !floors.length;
  $('min-floor').textContent = floors.length ? `${floors[0]}/F` : '—'; $('max-floor').textContent = floors.length ? `${floors.at(-1)}/F` : '—';
  fill('flat', getFlats(data, $('estate').value, $('building').value), item => item.label); windowsChanged();
}
function estateChanged() { fill('building', getBuildings(data, $('estate').value)); const preferred = getEstate(data, $('estate').value)?.defaultBuildingId; if (preferred && getBuildings(data, $('estate').value).some(b => b.id === preferred)) $('building').value = preferred; buildingChanged(); }
$('estate').addEventListener('change', estateChanged); $('building').addEventListener('change', buildingChanged); $('flat').addEventListener('change', windowsChanged);
$('window').addEventListener('change', render); $('floor').addEventListener('change', render);
$('floor-slider').addEventListener('input', () => { $('floor').value = String(floors[Number($('floor-slider').value)]); render(); });
$('view').addEventListener('click', () => { const { url } = cameraState(); if (url) window.open(url, '_blank', 'noopener,noreferrer'); });
$('copy').addEventListener('click', async () => {
  const { url } = cameraState(); if (!url) return;
  try { await navigator.clipboard.writeText(url); $('copy-status').textContent = '已複製 · Link copied'; }
  catch { $('copy-status').textContent = '無法複製，請從開發資料複製連結。 Copy the URL from Debug details.'; }
});
const calInputs=['cal-x','cal-y','cal-scale','cal-rotate'].map($); const applyCalibration=()=>{ const svg=$('map-preview'); if(!svg)return; const x=Number($('cal-x').value),y=Number($('cal-y').value),s=Number($('cal-scale').value)/100,r=Number($('cal-rotate').value); svg.style.transform=`translate(${x}px,${y}px) rotate(${r}deg) scale(${s})`; }; calInputs.forEach(i=>i?.addEventListener('input',applyCalibration)); $('cal-save')?.addEventListener('click',()=>{ const value=Object.fromEntries(calInputs.map(i=>[i.id.replace('cal-',''),Number(i.value)])); localStorage.setItem('window-view-calibration',JSON.stringify(value)); $('cal-status').textContent=' Saved locally'; });
let planPoints=[]; $('plan-file')?.addEventListener('change',e=>{ const f=e.target.files?.[0]; if(f && f.type.startsWith('image/')) $('plan-image').src=URL.createObjectURL(f); }); $('plan-draw')?.addEventListener('click',e=>{ const r=e.currentTarget.getBoundingClientRect(); planPoints.push([(e.clientX-r.left)/r.width*360,(e.clientY-r.top)/r.height*215]); if(planPoints.length===2){ const [a,b]=planPoints; const deg=(Math.atan2(b[0]-a[0],-(b[1]-a[1]))*180/Math.PI+360)%360; e.currentTarget.innerHTML=`<line class="plan-line" x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}"/>`; $('plan-heading').textContent=`Window heading: ${deg.toFixed(1)}°`; localStorage.setItem('window-view-plan-line',JSON.stringify({a,b,heading:deg})); planPoints=[]; } });
fill('estate', data.estates); if (getEstate(data, data.defaultEstateId)) $('estate').value = data.defaultEstateId; estateChanged();

let mapResizeTimer; window.addEventListener("resize",()=>{clearTimeout(mapResizeTimer);mapResizeTimer=setTimeout(()=>render(),100);});
