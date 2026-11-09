(async()=>{
 'use strict';
 const load=u=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>reject(Error('Image failed: '+u));im.src=u;});
 const json=async u=>{const r=await fetch(u);if(!r.ok)throw Error(u);return r.json();};
 const canvas=(w,h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return c;};
 const g=c=>{const q=c.getContext('2d',{willReadFrequently:true});q.imageSmoothingEnabled=false;return q;};
 function normalize(im,w,h){
  const input=canvas(im.width,im.height),q=g(input);q.drawImage(im,0,0);const a=q.getImageData(0,0,im.width,im.height).data;
  let x0=im.width,y0=im.height,x1=-1,y1=-1;for(let y=0;y<im.height;y++)for(let x=0;x<im.width;x++)if(a[(y*im.width+x)*4+3]>=220){x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x);y1=Math.max(y1,y);}
  if(x1<x0||y1<y0)throw Error('Sprite has no opaque content');
  const out=canvas(w,h),b=g(out),sw=x1-x0+1,sh=y1-y0+1,s=Math.min((w-2)/sw,(h-2)/sh),dw=Math.round(sw*s),dh=Math.round(sh*s);b.drawImage(im,x0,y0,sw,sh,Math.floor((w-dw)/2),h-dh-1,dw,dh);
  const d=b.getImageData(0,0,w,h);for(let i=0;i<d.data.length;i+=4){d.data[i+3]=d.data[i+3]>=200?255:0;if(!d.data[i+3])d.data[i]=d.data[i+1]=d.data[i+2]=0;else for(let k=0;k<3;k++)d.data[i+k]=Math.round(d.data[i+k]/8)*8;}b.putImageData(d,0,0);return out;
 }
 const specs=await json('props129.json'),props=await Promise.all(specs.map(async s=>({...s,sprite:normalize(await load(s.source),s.w,s.h)})));
 const [wall,material,rects,planes,map,shop]=await Promise.all([load('../wall-height121/wall22.png'),load('../festival125/assets/wall-source.png'),json('../wall-height121/rects121.json'),json('../wall-height121/planes121.json'),json('../native-play107/maps/map-10786001-1.json'),load('../festival128/assets/goldfish96.png')]);
 const texture=canvas(64,64);g(texture).drawImage(material,material.width/4,material.height/4,material.width/2,material.height/2,0,0,64,64);const tex=g(texture).getImageData(0,0,64,64).data;
 const agedWall=createFestivalWall129({canvas,g,wall,rects,planes,tex}),floor=await load('../native-play107/assets/floor.png'),actor={};await Promise.all(['body','boots','armour','helmet','sword'].map(async k=>actor[k]=await load(`../city-market02/assets/${k}.png`)));
 const catalog=document.getElementById('catalog'),select=document.getElementById('propSelect'),field=document.getElementById('scene'),ctx=g(field);let selected='mask-rack';
 const placements=[{id:'lantern-string',x:2,y:1},{id:'nobori',x:6,y:4},{id:'mask-rack',x:1,y:8},{id:'taiko',x:6,y:9},{id:'yagura',x:12,y:4},{id:'bench',x:11,y:10},{id:'festival-cart',x:15,y:9}];
 const rows=Array.from({length:13},(_,y)=>Array.from({length:20},(_,x)=>y<=1||y===12||x===0||x===19?'#':'.').join(''));
 const floorCounts=new Map();for(const i of map.floors)floorCounts.set(i,(floorCounts.get(i)||0)+1);const floorIds=[...floorCounts].sort((a,b)=>b[1]-a[1]).map(x=>x[0]).filter(i=>map.palette[i].atlas==='floor').slice(0,4);
 const dirs=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
 function maskAt(x,y){let m=0;dirs.forEach(([dx,dy],i)=>{if(rows[y+dy]?.[x+dx]==='#')m|=1<<i;});return m;}
 function player(q,x,y){for(const k of ['body','boots','armour','helmet','sword'])q.drawImage(actor[k],x,y,32,32);}
 function cards(){for(const s of props){const c=document.querySelector(`[data-prop="${s.id}"] canvas`),q=g(c);q.clearRect(0,0,c.width,c.height);const x=s.w>112?8:8+Math.floor((96-s.w)/2),y=s.mount==='wall'?34:128-s.h;q.drawImage(s.sprite,x,y);if(document.getElementById('reference').checked)player(q,120,96);}}
 function draw(){
  ctx.fillStyle='#171c19';ctx.fillRect(0,0,640,416);
  for(let y=0;y<13;y++)for(let x=0;x<20;x++){
   const f=map.palette[floorIds[((Math.imul(x+17,73856093)^Math.imul(y+9,19349663))>>>0)%floorIds.length]];ctx.drawImage(floor,f.sx,f.sy,32,32,x*32,y*32,32,32);
   if(rows[y][x]==='#')ctx.drawImage(agedWall(maskAt(x,y),0,x,y),x*32,y*32);
  }
  ctx.save();ctx.fillStyle='rgba(5,5,4,.35)';ctx.beginPath();ctx.ellipse(112,157,38,3,0,0,Math.PI*2);ctx.fill();ctx.restore();ctx.drawImage(shop,64,96,96,64);
  const layers=placements.map(p=>{const s=props.find(s=>s.id===p.id);return{...p,s,bottom:s.mount==='wall'?p.y*32+43:(p.y+s.footprint[1])*32};}).sort((a,b)=>a.bottom-b.bottom);
  for(const p of layers){const s=p.s;if(s.mount==='wall'){ctx.drawImage(s.sprite,p.x*32,p.y*32+11);continue;}
   const [w,h]=s.footprint;ctx.save();ctx.fillStyle='rgba(5,5,4,.3)';ctx.beginPath();ctx.ellipse((p.x+w/2)*32,p.bottom-3,Math.max(8,w*12),3,0,0,Math.PI*2);ctx.fill();ctx.restore();
   ctx.drawImage(s.sprite,p.x*32,p.bottom-s.h);
  }
  if(document.getElementById('reference').checked)player(ctx,9*32,8*32);
  if(document.getElementById('footprints').checked)for(const p of placements){const s=props.find(s=>s.id===p.id);ctx.strokeStyle=p.id===selected?'#ffce72':'#8a8873';ctx.lineWidth=p.id===selected?2:1;const [w,h]=s.footprint;if(s.mount==='wall')ctx.strokeRect(p.x*32+.5,p.y*32+10.5,s.w,32);else ctx.strokeRect(p.x*32+.5,p.y*32+.5,w*32,h*32);}
  const s=props.find(s=>s.id===selected);document.getElementById('status').textContent=`${s.name} · 도트${s.w}×${s.h}px · ${s.description} · 플레이어32×32px`;
 }
 function choose(id){selected=id;select.value=id;document.querySelectorAll('[data-prop]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.prop===id)));draw();}
 for(const s of props){const b=document.createElement('button');b.className='prop-card';b.dataset.prop=s.id;b.setAttribute('aria-label',s.name+' 선택');b.innerHTML=`<strong>${s.name}</strong><canvas width="160" height="144"></canvas><small>${s.description}</small><small>도트 ${s.w}×${s.h}px</small>`;b.onclick=()=>choose(s.id);catalog.append(b);select.add(new Option(s.name,s.id));}
 function fit(){for(const c of document.querySelectorAll('.prop-card canvas,#scene')){const isCard=c.parentElement.classList.contains('prop-card'),available=c.parentElement.clientWidth-(isCard?32:0),s=Math.max(1,Math.min(isCard?3:10,Math.floor(available/c.width)));c.style.width=c.width*s+'px';c.style.height=c.height*s+'px';c.style.marginInline='auto';}}
 document.getElementById('reference').onchange=()=>{cards();draw();};document.getElementById('footprints').onchange=draw;select.onchange=()=>choose(select.value);window.addEventListener('resize',fit);
 window.festival129={props,placements,rows,draw,cards,choose,shop,actor,agedWall,texture,getSelected:()=>selected};cards();choose(selected);fit();window.festivalReady=true;
})().catch(e=>{console.error(e);document.getElementById('status').textContent='소품 로드 오류: '+e.message;});
