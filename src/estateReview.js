import './estateReview.css';
const files=import.meta.glob('../data/kingswood-footprints/*-official-footprint.json',{eager:true,import:'default'});
import chestwood1 from '../data/chestwood-tower-1-official-footprint.json';
const colors=['#c04523','#2c64c5','#16805d','#923fac','#b07700','#007d96','#c02c77','#566429'];
const phaseIds={'kingswood-locwood':1,'kingswood-sherwood':2,'kingswood-chestwood':3,'kingswood-lynwood':5,'kingswood-maywood':6,'kingswood-kenswood':7};
const short=id=>({living:'客',master:'主','bedroom-1':'1','bedroom-2':'2'}[id]||id);
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function renderEstateReview(container,estate){
 if(container.dataset.estate===estate?.id)return;
 container.dataset.estate=estate?.id||'';container.replaceChildren();
 if(!estate){container.textContent='請先選擇屋苑';return;}
 const title=document.createElement('p');title.textContent=`${estate.nameTC} · ${estate.buildings.length} 座 · 已收錄 ${estate.buildings.reduce((s,b)=>s+b.flats.reduce((n,f)=>n+f.windows.length,0),0)} 個窗`;container.append(title);
 const grid=document.createElement('div');grid.className='estate-review-grid';container.append(grid);
 for(const b of estate.buildings){
  const phase=phaseIds[estate.id],tower=b.id.split('-').at(-1);
  const footprint=phase===3&&tower==='1'?chestwood1:files[`../data/kingswood-footprints/phase-${phase}-tower-${tower}-official-footprint.json`];
  const card=document.createElement('article');card.className='estate-review-tower';
  const heading=document.createElement('h3');heading.textContent=b.nameTC;card.append(heading);grid.append(card);
  if(!footprint){const p=document.createElement('p');p.textContent='未有本座官方輪廓，暫不能繪製總覽。';card.append(p);continue;}
  const ring=footprint.geometry.rings[0],lng=ring[0][0],lat=ring[0][1],cos=Math.cos(lat*Math.PI/180);
  const local=(x,y)=>[(x-lng)*111320*cos,(lat-y)*111320];
  const poly=ring.map(p=>local(...p));
  const windows=b.flats.flatMap((f,i)=>f.windows.filter(w=>Number.isFinite(w.latitude)&&Number.isFinite(w.longitude)).map(w=>({f,w,color:colors[i%8],p:local(w.longitude,w.latitude)})));
  const points=[...poly,...windows.map(w=>w.p)],xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);
  const minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys),scale=Math.min(390/(maxX-minX),390/(maxY-minY));
  const xy=p=>[260+(p[0]-(minX+maxX)/2)*scale,260+(p[1]-(minY+maxY)/2)*scale];
  let markup=`<polygon points="${poly.map(p=>xy(p).join(',')).join(' ')}" fill="#d2e8ec" stroke="#277486" stroke-width="2"/><text x="490" y="28" font-size="19" font-weight="bold">N ↑</text>`;
  const labels=[];
  for(const {f,w,color,p} of windows){const [x,y]=xy(p),a=w.heading*Math.PI/180,dx=Math.sin(a),dy=-Math.cos(a);let lx=x+dx*29,ly=y+dy*29;for(let step=0;step<16;step++){const offset=step*7;lx=x+dx*(29+offset);ly=y+dy*(29+offset);if(!labels.some(p=>Math.abs(p[0]-lx)<30&&Math.abs(p[1]-ly)<14))break;}labels.push([lx,ly]);markup+=`<g><title>${esc(f.label)}室 ${esc(w.nameTC)} · ${w.heading.toFixed(1)}°</title><line x1="${x}" y1="${y}" x2="${x+dx*18}" y2="${y+dy*18}" stroke="${color}" stroke-width="2"/><circle cx="${x}" cy="${y}" r="3.5" fill="${color}" stroke="white"/><text x="${lx}" y="${ly}" fill="${color}" font-size="12" text-anchor="middle" dominant-baseline="middle" stroke="white" stroke-width="3" paint-order="stroke">${esc(f.label)}·${esc(short(w.id))}</text></g>`;}
  // A–H anchors sit inside their window clusters, with an inward offset for legibility.
  for(const f of b.flats){const ws=windows.filter(w=>w.f===f);if(!ws.length)continue;const p=ws.reduce((a,w)=>[a[0]+w.p[0]/ws.length,a[1]+w.p[1]/ws.length],[0,0]);let [x,y]=xy(p);const d=Math.hypot(x-260,y-260)||1;x-=(x-260)/d*30;y-=(y-260)/d*30;markup+=`<text x="${x}" y="${y}" text-anchor="middle" dominant-baseline="middle" font-size="20" font-weight="bold" fill="${ws[0].color}" stroke="white" stroke-width="4" paint-order="stroke">${esc(f.label)}</text>`;}
  const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 520 520');svg.setAttribute('role','img');svg.setAttribute('aria-label',`${b.nameTC} A–H 全部窗位及向外方向`);svg.innerHTML=markup;card.append(svg);
  const note=document.createElement('p');note.textContent=`${windows.length} 個窗 · ${b.floors.min}–${b.floors.max}/F · 配準估算`;card.append(note);
 }
}
