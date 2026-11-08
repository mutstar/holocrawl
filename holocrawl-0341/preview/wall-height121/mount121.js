(function(root){
 'use strict';
 const cache=new Map(),unitCache=new WeakMap(),top=11,height=20;
 function canvas(w){const c=document.createElement('canvas');c.width=w;c.height=32;return c;}
 function finish(c,m,f){const g=c.getContext('2d'),im=g.getImageData(0,0,c.width,32);for(let y=0;y<32;y++)for(let x=0;x<c.width;x++)if(!WallHeight121.allowed(m,f,x,y))im.data.fill(0,(y*c.width+x)*4,(y*c.width+x)*4+4);g.putImageData(im,0,0);return c;}
 function fixtureSprite(f,m,images,mix=0){
  const key=`${m.seed}:${m.floorNumber||m.depth}:${f.type}:${f.x},${f.y}:${mix}`;if(cache.has(key))return cache.get(key);
  const c=canvas(64),g=c.getContext('2d'),old=canvas(64),q=old.getContext('2d');g.imageSmoothingEnabled=q.imageSmoothingEnabled=false;q.translate(-f.x*32,-f.y*32);Scene112.draw(q,f,m,images,32,mix);
  g.fillStyle='#53646b';g.fillRect(3,top,58,height);g.fillStyle='#101a20';g.fillRect(4,top+1,56,height-2);
  const ids=MarketStock.select(m.seed,m.floorNumber||m.depth,f,mix);
  if(f.type==='acrylic-window')ids.forEach((id,i)=>g.drawImage(MarketStock.getSprite(id),9+i*18,top+2,10,15));
  else if(f.type==='shirt-window')ids.forEach((id,i)=>g.drawImage(MarketStock.getShirt(id),7+i*18,top+3,14,14));
  else if(f.type==='poster-wall')g.drawImage(old,6,10,52,19,10,top+2,44,16);
  else g.drawImage(old,6,10,52,19,6,top+2,52,height-4);
  g.fillStyle='#26333b';g.fillRect(4,top+1,56,1);g.fillStyle='#31444e';g.fillRect(59,top+1,1,height-2);g.fillStyle='#42535d';g.fillRect(4,top+height-1,56,1);
  const value=finish(c,m,f);if(cache.size>1000)cache.clear();cache.set(key,value);return value;
 }
 function utilitySprite(p,m,units){let entries=unitCache.get(units);if(!entries){entries=new Map();unitCache.set(units,entries);}const k=`${m.seed}:${m.depth||m.floorNumber}:${p.type}:${p.x},${p.y}:${p.length}`;if(entries.has(k))return entries.get(k);
  const c=canvas((p.length||1)*32),g=c.getContext('2d'),im=units[p.type];g.imageSmoothingEnabled=false;
  if(p.type==='pipe')for(let i=0;i<p.length;i++)g.drawImage(im,i===0?0:i===p.length-1?64:32,0,32,32,i*32,top,32,height);
  else{const raw=PixelReducer.read(im),b=PixelReducer.bounds(raw,1),s=Math.min(1,28/b.w,height/b.h),w=Math.max(1,Math.round(b.w*s)),h=Math.max(1,Math.round(b.h*s));g.drawImage(im,b.x,b.y,b.w,b.h,Math.floor((32-w)/2),top+Math.floor((height-h)/2),w,h);}
  const value=finish(c,m,p);entries.set(k,value);return value;
 }
 function drawFixture(ctx,f,m,images,t,mix=0){if(Market108.isOld()||document.getElementById('beforeScene112')?.checked)return Scene112.draw(ctx,f,m,images,t,mix);ctx.drawImage(fixtureSprite(f,m,images,mix),f.x*t,f.y*t,2*t,t);}
 function drawUtility(ctx,p,m,units,t=32){ctx.drawImage(utilitySprite(p,m,units),p.x*t,p.y*t,(p.length||1)*t,t);}
 root.WallMount121={top,height,fixtureSprite,utilitySprite,drawFixture,drawUtility};
})(globalThis);
