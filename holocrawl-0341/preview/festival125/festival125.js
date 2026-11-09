(async()=>{
 'use strict';
 const load=u=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>reject(Error('Image failed: '+u));im.src=u;});
 const json=async u=>{const r=await fetch(u);if(!r.ok)throw Error(u);return r.json();};
 const canvas=(w,h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return c;};
 const g=c=>{const q=c.getContext('2d',{willReadFrequently:true});q.imageSmoothingEnabled=false;return q;};
 const dirs=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
 const [wall,material,stallSource,lanternSource,rects,planes,lookup,manifest]=await Promise.all([
  load('../wall-height121/wall22.png'),load('assets/wall-source.png'),load('assets/takoyaki-source.png'),load('assets/lantern-source.png'),json('../wall-height121/rects121.json'),json('../wall-height121/planes121.json'),json('../wall-height121/native-lookup121.json'),json('../city-street124/manifest.json')]);
 const atlases={};await Promise.all(['floor','wall','feat','main','player'].map(async k=>atlases[k]=await load(`../native-play107/assets/${k}.png`)));
 const actor={};await Promise.all(['body','boots','armour','helmet','sword'].map(async k=>actor[k]=await load(`../city-market02/assets/${k}.png`)));
 await WallHeight121.load();
 function normalize(im,w,h){
  const source=canvas(im.width,im.height),q=g(source);q.drawImage(im,0,0);const a=q.getImageData(0,0,im.width,im.height).data;
  let x0=im.width,y0=im.height,x1=-1,y1=-1;
  for(let y=0;y<im.height;y++)for(let x=0;x<im.width;x++)if(a[(y*im.width+x)*4+3]>=220){x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x);y1=Math.max(y1,y);}
  const out=canvas(w,h),b=g(out),sw=x1-x0+1,sh=y1-y0+1,s=Math.min((w-2)/sw,(h-2)/sh),dw=Math.round(sw*s),dh=Math.round(sh*s);
  b.drawImage(im,x0,y0,sw,sh,Math.floor((w-dw)/2),h-dh-1,dw,dh);
  const d=b.getImageData(0,0,w,h);for(let i=0;i<d.data.length;i+=4){d.data[i+3]=d.data[i+3]>=200?255:0;if(!d.data[i+3]){d.data[i]=d.data[i+1]=d.data[i+2]=0;}else for(let j=0;j<3;j++)d.data[i+j]=Math.round(d.data[i+j]/8)*8;}
  b.putImageData(d,0,0);return out;
 }
 const stall=normalize(stallSource,96,64),lantern=normalize(lanternSource,16,32),texture=canvas(64,64);g(texture).drawImage(material,material.width/4,material.height/4,material.width/2,material.height/2,0,0,64,64);const tex=g(texture).getImageData(0,0,64,64).data;
 // One reflected material field spans the wall; lighting never changes per cell.
 const fold=n=>{const p=((n%128)+128)%128;return p<64?p:127-p;};
 const wallCache=new Map();
 function agedWall(mask,variant=0,worldX=0,worldY=0){
  const key=`${mask}:${variant}:${((worldX%4)+4)%4}:${((worldY%4)+4)%4}`;if(wallCache.has(key))return wallCache.get(key);
  const c=canvas(32,32),q=g(c),rect=rects[`${mask}:0`];q.drawImage(wall,...rect,0,0,32,32);const d=q.getImageData(0,0,32,32),front=planes[String(mask)];
  for(let y=0;y<32;y++)for(let x=0;x<32;x++){
   const i=(y*32+x)*4;if(!d.data[i+3])continue;
   const old=[d.data[i],d.data[i+1],d.data[i+2]],lum=old[0]*.2126+old[1]*.7152+old[2]*.0722;
   if(front[y*32+x]==='1'){
    const tx=fold(worldX*32+x+variant*7),ty=fold(worldY*32+y+variant*11),j=(ty*64+tx)*4;
    const shade=.82*(.99-Math.max(0,y-10)*.0045);
    for(let k=0;k<3;k++)d.data[i+k]=Math.round(tex[j+k]*shade);
   }else{
    d.data[i]=Math.round(lum*.98);d.data[i+1]=Math.round(lum*.88);d.data[i+2]=Math.round(lum*.75);
   }
  }
  q.putImageData(d,0,0);wallCache.set(key,c);return c;
 }
 function maskAt(rows,x,y){let m=0;dirs.forEach(([dx,dy],i)=>{if(rows[y+dy]?.[x+dx]==='#')m|=1<<i;});return m;}
 function variant(x,y,seed=0){return((Math.imul(x+seed,73856093)^Math.imul(y,19349663))>>>0)%8;}
 function drawWallStudy(){
  const c=document.getElementById('walls'),q=g(c);q.clearRect(0,0,c.width,c.height);
  const rows=['.......','.#####.','.......','.##..#.','..#....'];
  for(let y=0;y<rows.length;y++)for(let x=0;x<rows[y].length;x++)if(rows[y][x]==='#')q.drawImage(agedWall(maskAt(rows,x,y),0,x,y),x*32,y*32);
  const s=document.getElementById('stall'),sq=g(s);sq.drawImage(stall,24,29);const l=document.getElementById('lantern'),lq=g(l);lq.drawImage(lantern,12,34);lq.save();lq.filter='brightness(.45)';lq.drawImage(lantern,50,34);lq.restore();
 }
 drawWallStudy();
 const select=document.getElementById('mapSelect'),field=document.getElementById('map'),ctx=g(field),mini=document.getElementById('overview'),mg=g(mini);
 const mapCandidates=[];
 for(const entry of manifest.maps.filter(m=>!m.forced&&m.depth===1)){const m=await json(entry.file);mapCandidates.push({...entry,locations:findSpots(m).length});}
 const entries=mapCandidates.filter(m=>m.locations>0).slice(0,3);entries.forEach((m,i)=>select.add(new Option(`기존 실제 지도 ${i+1} · 시드${m.seed}`,i)));
 let map,spots=[],spotIndex=0,aged=true,job=0;
 const key=(x,y)=>`${x},${y}`;
 function findSpots(m){
  const points=[],special=[];for(let y=0;y<m.height;y++)for(let x=0;x<m.width;x++)if('<>+'.includes(m.rows[y][x]))special.push({x,y});
  const inside=(x,y)=>m.origin&&x>=m.origin.x-2&&y>=m.origin.y-2&&x<m.origin.x+m.origin.width+2&&y<m.origin.y+m.origin.height+2;
  for(let y=2;y<m.height-5;y++)for(let x=3;x<m.width-7;x++){
   if(!Array.from({length:5},(_,i)=>m.rows[y][x+i]==='#').every(Boolean))continue;
   let ok=true;for(let dy=1;dy<=4;dy++)for(let dx=0;dx<5;dx++)if(m.rows[y+dy][x+dx]!=='.'||!m.passable[(y+dy)*m.width+x+dx]||inside(x+dx,y+dy))ok=false;
   if(!ok||special.some(p=>Math.max(Math.abs(p.x-x-2),Math.abs(p.y-y-2))<6))continue;
   points.push({x:x+1,y:y+1,wallY:y});
  }
  return points.sort((a,b)=>variant(a.x,a.y,m.seed)-variant(b.x,b.y,m.seed)||a.y-b.y||a.x-b.x);
 }
 function nativeTile(q,t,x,y,wallX,wallY){
  if(t.atlas==='wall'){
   const r=lookup[`${t.sx},${t.sy}`];if(r){if(aged){const mask=(r[1]/32*16+r[0]/32)%256; // Each block of256 atlas cells holds one material variant.
      q.drawImage(agedWall(mask,map.seed%8,wallX,wallY),x,y,32,32);
     }else q.drawImage(wall,...r,x,y,32,32);return;}
  }
  q.drawImage(atlases[t.atlas],t.sx,t.sy,t.width,t.height,x+t.dx,y+t.dy,t.width,t.height);
 }
 function draw(){
  if(!map||!spots.length)return;const spot=spots[spotIndex%spots.length];
  const ox=Math.max(0,Math.min(map.width-18,spot.x-8)),oy=Math.max(0,Math.min(map.height-11,spot.y-3));
  ctx.fillStyle='#151a18';ctx.fillRect(0,0,576,352);
  for(let y=oy;y<oy+11;y++)for(let x=ox;x<ox+18;x++){
   const i=y*map.width+x,px=(x-ox)*32,py=(y-oy)*32;nativeTile(ctx,map.palette[map.floors[i]],px,py,x,y);nativeTile(ctx,map.palette[map.features[i]],px,py,x,y);
   if(map.overlays[i]>=0)nativeTile(ctx,map.palette[map.overlays[i]],px,py,x,y);
  }
  const sx=(spot.x-ox)*32,sy=(spot.y-oy)*32;
  // Contact shadows are confined to the stall footprint, clear of the walking lane.
  ctx.fillStyle='rgba(8,7,6,.5)';ctx.fillRect(sx+6,sy+58,84,5);ctx.drawImage(stall,sx,sy);
  for(const dx of [-1,3]){
   ctx.save();if(!document.getElementById('lamps').checked)ctx.filter='brightness(.45)';
   ctx.drawImage(lantern,(spot.x+dx-ox)*32+10,(spot.wallY-oy)*32+10,11,22);ctx.restore();
  }
  for(const k of Object.keys(actor))ctx.drawImage(actor[k],sx+32,sy+96,32,32);
  mg.fillStyle='#151a18';mg.fillRect(0,0,320,280);for(let y=0;y<map.height;y++)for(let x=0;x<map.width;x++){mg.fillStyle=map.rows[y][x]==='#'?'#5d5145':map.rows[y][x]==='+'?'#bc895e':map.passable[y*map.width+x]?'#929087':'#252824';mg.fillRect(x*4,y*4,4,4);}mg.strokeStyle='#e9b85e';mg.lineWidth=1;mg.strokeRect(ox*4+.5,oy*4+.5,72,44);mg.fillStyle='#c96a51';mg.fillRect(spot.x*4,spot.y*4,12,8);
  document.getElementById('status').textContent=`시드${map.seed} · 원본${map.width}×${map.height} · 검토 지점${spotIndex%spots.length+1}/${spots.length} · 포장마차3×2칸 · 앞쪽2줄 통행 공간 · 벽${aged?'축제 회벽':'기존121'}`;
  document.getElementById('aged').setAttribute('aria-pressed',String(aged));document.getElementById('original').setAttribute('aria-pressed',String(!aged));
 }
 async function changeMap(){const n=++job;window.festivalReady=false;const m=await json(entries[select.value||0].file);if(n!==job)return;map=m;spots=findSpots(map);if(!spots.length)throw Error('No safe stall location');spotIndex=0;draw();window.festivalReady=true;}
 select.onchange=changeMap;document.getElementById('nextSpot').onclick=()=>{spotIndex++;draw();};document.getElementById('aged').onclick=()=>{aged=true;draw();};document.getElementById('original').onclick=()=>{aged=false;draw();};document.getElementById('lamps').onchange=draw;
 function fitCanvases(){for(const c of document.querySelectorAll('.card canvas,#map')){const available=c.parentElement.clientWidth-(c.parentElement.classList.contains('card')?36:0),scale=Math.max(1,Math.floor(available/c.width));c.style.width=c.width*scale+'px';c.style.height=c.height*scale+'px';c.style.maxWidth='none';c.style.marginInline='auto';}document.querySelectorAll('.card').forEach(c=>c.style.overflowX='auto');}
 window.addEventListener('resize',fitCanvases);fitCanvases();
 window.festival125={agedWall,stall,lantern,texture,getMap:()=>map,getSpots:()=>spots,getSpot:()=>spots[spotIndex%spots.length],entries,mapCandidates,draw,findSpots,rects,planes,wall,wallCache};
 await changeMap();
})().catch(e=>{console.error(e);document.getElementById('status').textContent='샘플 로드 오류: '+e.message;});
