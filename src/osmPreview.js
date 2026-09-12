export function worldPixel(lng,lat,z=18){
 const size=256*2**z;
 return [(lng+180)/360*size,(1-Math.asinh(Math.tan(lat*Math.PI/180))/Math.PI)/2*size];
}
export function mapLayout(outline,window,width,height){
 const points=outline?.map(([lng,lat])=>worldPixel(lng,lat))||[worldPixel(window.longitude,window.latitude)];
 const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);
 const center=[(Math.min(...xs)+Math.max(...xs))/2,(Math.min(...ys)+Math.max(...ys))/2];
 const left=center[0]-width/2,top=center[1]-height/2;
 const tiles=[];
 for(let x=Math.floor(left/256);x<=Math.floor((left+width)/256);x++)for(let y=Math.floor(top/256);y<=Math.floor((top+height)/256);y++)tiles.push({x,y,left:x*256-left,top:y*256-top});
 const local=p=>[p[0]-left,p[1]-top];
 return {center,tiles,outline:points.map(local),camera:local(worldPixel(window.longitude,window.latitude))};
}
export function renderOsm(frame,outline,window,showWindow=false){
 const width=frame.clientWidth||600,height=frame.clientHeight||320;
 const layout=mapLayout(outline,window,width,height);
 frame.style.cssText+=';position:relative;overflow:hidden;background-image:none;';
 frame.replaceChildren();
 for(const tile of layout.tiles){
  const img=document.createElement('img');img.src=`https://tile.openstreetmap.org/18/${tile.x}/${tile.y}.png`;img.alt='';
  img.style.cssText=`position:absolute;left:${tile.left}px;top:${tile.top}px;width:256px;height:256px;max-width:none;margin:0;border:0;border-radius:0;`;
  frame.append(img);
 }

 const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
 svg.setAttribute('viewBox',`0 0 ${width} ${height}`);
 svg.style.cssText='position:absolute;inset:0;width:100%;height:100%;margin:0;border:0;border-radius:0;background:none;pointer-events:none;transform:none;';
 svg.innerHTML=outline?`<polygon points="${layout.outline.map(p=>p.join(',')).join(' ')}" fill="#157889" fill-opacity="0.15" stroke="#157889" stroke-width="2"/>`:'';
 if(showWindow){
  const [x,y]=layout.camera,a=window.heading*Math.PI/180;
  const ex=x+Math.sin(a)*32,ey=y-Math.cos(a)*32;
  const bx=ex-Math.sin(a)*8,by=ey+Math.cos(a)*8;
  svg.innerHTML+=`<line x1="${x}" y1="${y}" x2="${ex}" y2="${ey}" stroke="#d45630" stroke-width="3" stroke-dasharray="6 4"/><path d="M ${bx+Math.cos(a)*5} ${by+Math.sin(a)*5} L ${ex} ${ey} L ${bx-Math.cos(a)*5} ${by-Math.sin(a)*5}" fill="none" stroke="#d45630" stroke-width="3"/><circle cx="${x}" cy="${y}" r="5" fill="#d45630" stroke="white" stroke-width="2"/>`;
 }
 frame.append(svg);
 const credit=document.createElement('a');credit.href='https://www.openstreetmap.org/copyright';credit.textContent='© OpenStreetMap contributors';credit.target='_blank';credit.rel='noopener';credit.style.cssText='position:absolute;right:0;bottom:0;background:#ffffffdd;padding:3px 6px;font-size:12px;';frame.append(credit);
}
