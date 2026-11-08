(function(root){
 'use strict';
 const cache=new Map(),unitCache=new WeakMap(),front=8,top=10,height=20;
 const dims=m=>[m.width||m.w,m.height||m.h];
 function solid(m,x,y){const[w,h]=dims(m);return x<0||y<0||x>=w||y>=h|| (m.rows?'#+G'.includes(m.rows[y][x]):m.cells[y*w+x]===0);}
 function wall(m,x,y){const[w,h]=dims(m);return x>=0&&y>=0&&x<w&&y<h&&(m.rows?m.rows[y][x]==='#':m.cells[y*w+x]===0);}
 function profile(x,W){const d=Math.min(x,W-1-x);return d<3?18:d<5?15:d<7?11:front;}
 function allowed(m,f,x,y,W){
  const xx=f.x+Math.floor(x/32),px=x%32;
  if(!wall(m,xx,f.y)||solid(m,xx,f.y+1)||y<profile(x,W)-4||y>=32)return false;
  if(!solid(m,xx+1,f.y)&&px>=(y<18?29:29+Math.floor((y-18)*3/13)))return false;
  return true;
 }
 function canvas(w){const c=document.createElement('canvas');c.width=w;c.height=32;return c;}
 function facade(W,m,f){
  const c=canvas(W),g=c.getContext('2d'),im=g.createImageData(W,32);
  for(let x=0;x<W;x++){
   const edge=profile(x,W);for(let y=edge-4;y<32;y++){
    if(!allowed(m,f,x,y,W))continue;const i=(y*W+x)*4,hash=(Math.imul((f.x*32+x)+17,374761393)^Math.imul((f.y*32+y)+31,668265263))>>>0,grain=hash%9-4;
    const col=y===edge-4?[134,144,148]:y<edge-1?[116,125,129]:y===edge-1?[90,107,112]:y===edge?[49,65,70]:[52,62,67];
    for(let k=0;k<3;k++)im.data[i+k]=col[k]+grain;im.data[i+3]=255;
   }
  }g.putImageData(im,0,0);return c;
 }
 function finish(c,m,f){const g=c.getContext('2d'),im=g.getImageData(0,0,c.width,32);for(let y=0;y<32;y++)for(let x=0;x<c.width;x++)if(!allowed(m,f,x,y,c.width))im.data.fill(0,(y*c.width+x)*4,(y*c.width+x)*4+4);g.putImageData(im,0,0);return c;}
 function compose(c,art,m,f){
  const g=art.getContext('2d'),im=g.getImageData(0,0,art.width,32);
  for(let y=0;y<32;y++)for(let x=0;x<art.width;x++)if(!allowed(m,f,x,y,art.width)||y<profile(x,art.width)+1||y>30)im.data.fill(0,(y*art.width+x)*4,(y*art.width+x)*4+4);
  g.putImageData(im,0,0);c.getContext('2d').drawImage(art,0,0);c.mountArt=art;return finish(c,m,f);
 }
 function fixtureSprite(f,m,images,mix=0){
  const k=`${m.seed}:${m.floorNumber||m.depth}:${f.type}:${f.x},${f.y}:${mix}`;if(cache.has(k))return cache.get(k);
  const c=facade(64,m,f),art=canvas(64),g=art.getContext('2d'),old=canvas(64),q=old.getContext('2d');g.imageSmoothingEnabled=q.imageSmoothingEnabled=false;q.translate(-f.x*32,-f.y*32);Scene112.draw(q,f,m,images,32,mix);
  g.fillStyle='#53646b';g.fillRect(3,top,58,height);g.fillStyle='#101a20';g.fillRect(4,top+1,56,height-2);
  const ids=MarketStock.select(m.seed,m.floorNumber||m.depth,f,mix);
  if(f.type==='acrylic-window')ids.forEach((id,i)=>g.drawImage(MarketStock.getSprite(id),9+i*18,top+2,10,15));
  else if(f.type==='shirt-window')ids.forEach((id,i)=>g.drawImage(MarketStock.getShirt(id),7+i*18,top+3,14,14));
  else if(f.type==='poster-wall')g.drawImage(old,6,10,52,19,10,top+2,44,16);
  else g.drawImage(old,6,10,52,19,6,top+2,52,height-4);
  g.fillStyle='#26333b';g.fillRect(4,top+1,56,1);g.fillStyle='#31444e';g.fillRect(59,top+1,1,height-2);g.fillStyle='#42535d';g.fillRect(4,top+height-1,56,1);
  const value=compose(c,art,m,f);if(cache.size>1000)cache.clear();cache.set(k,value);return value;
 }
 function utilitySprite(p,m,units){
  let entries=unitCache.get(units);if(!entries){entries=new Map();unitCache.set(units,entries);}const k=`${m.seed}:${m.depth||m.floorNumber}:${p.type}:${p.x},${p.y}:${p.length}`;if(entries.has(k))return entries.get(k);
  const c=facade((p.length||1)*32,m,p),art=canvas(c.width),g=art.getContext('2d'),im=units[p.type];g.imageSmoothingEnabled=false;
  if(p.type==='pipe')for(let i=0;i<p.length;i++)g.drawImage(im,i===0?0:i===p.length-1?64:32,0,32,32,i*32,top,32,height);
  else{const raw=PixelReducer.read(im),b=PixelReducer.bounds(raw,1),s=Math.min(1,28/b.w,height/b.h),w=Math.max(1,Math.round(b.w*s)),h=Math.max(1,Math.round(b.h*s));g.drawImage(im,b.x,b.y,b.w,b.h,Math.floor((32-w)/2),top+Math.floor((height-h)/2),w,h);}
  const value=compose(c,art,m,p);entries.set(k,value);return value;
 }
 function drawFixture(ctx,f,m,images,t,mix=0){if(Market108.isOld()||document.getElementById('beforeScene112')?.checked)return Scene112.draw(ctx,f,m,images,t,mix);ctx.drawImage(fixtureSprite(f,m,images,mix),f.x*t,f.y*t,2*t,t);}
 function drawUtility(ctx,p,m,units,t=32){ctx.drawImage(utilitySprite(p,m,units),p.x*t,p.y*t,(p.length||1)*t,t);}
 root.WallBay120={front,top,height,profile,allowed,fixtureSprite,utilitySprite,drawFixture,drawUtility};
})(globalThis);
