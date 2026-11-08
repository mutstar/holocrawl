(function(root){
 'use strict';
 // Material92: roof/coping0..17; front18..31. Leave its seam and foot intact.
 const top=19,height=12,cache=new Map(),utilityCache=new WeakMap();
 const size=m=>({w:m.width||m.w,h:m.height||m.h});
 function solid(m,x,y){const{w,h}=size(m);if(x<0||y<0||x>=w||y>=h)return true;return m.rows?'#+G'.includes(m.rows[y][x]):m.cells[y*w+x]===0;}
 function wall(m,x,y){const{w,h}=size(m);return x>=0&&y>=0&&x<w&&y<h&&(m.rows?m.rows[y][x]==='#':m.cells[y*w+x]===0);}
 function allowed(m,x,y,px,py){
  if(!wall(m,x,y)||solid(m,x,y+1)||py<top||py>=top+height)return false;
  // Follow material92's south-east mitre, never paint the three-pixel side.
  return solid(m,x+1,y)||px<29+Math.floor((py-18)*3/13);
 }
 function canvas(w,h=32){const c=document.createElement('canvas');c.width=w;c.height=h;return c;}
 function mask(art,m,f){
  const c=canvas(art.width),g=c.getContext('2d',{willReadFrequently:true});g.drawImage(art,0,0);const a=g.getImageData(0,0,c.width,c.height);
  for(let py=0;py<32;py++)for(let x=0;x<c.width;x++)if(!allowed(m,f.x+Math.floor(x/32),f.y,x%32,py))a.data.fill(0,(py*c.width+x)*4,(py*c.width+x)*4+4);
  g.putImageData(a,0,0);return c;
 }
 function fixtureSprite(f,m,images,mix=0){
  const k=`${m.seed}:${m.floorNumber||m.depth}:${f.type}:${f.x},${f.y}:${mix}`;if(cache.has(k))return cache.get(k);
  const old=canvas(64),q=old.getContext('2d');q.imageSmoothingEnabled=false;q.translate(-f.x*32,-f.y*32);Scene112.draw(q,f,m,images,32,mix);
  const c=canvas(64),g=c.getContext('2d');g.imageSmoothingEnabled=false;
  // A low display opening belongs to the short front, below the coping.
  // Miniatures keep their aspect ratio; never flatten full-height people/shirts.
  g.fillStyle='#53646b';g.fillRect(3,19,58,12);g.fillStyle='#101a20';g.fillRect(4,20,56,10);
  const ids=MarketStock.select(m.seed,m.floorNumber||m.depth,f,mix);
  if(f.type==='acrylic-window')ids.forEach((id,i)=>g.drawImage(MarketStock.getSprite(id),11+i*18,21,5,8));
  else if(f.type==='shirt-window')ids.forEach((id,i)=>g.drawImage(MarketStock.getShirt(id),9+i*18,21,8,8));
  else if(f.type==='poster-wall')g.drawImage(old,6,10,52,19,21,21,22,8);
  else g.drawImage(old,6,10,52,19,6,21,52,8);
  g.fillStyle='#26333b';g.fillRect(4,20,56,1);g.fillStyle='#31444e';g.fillRect(59,20,1,10);g.fillStyle='#42535d';g.fillRect(4,30,56,1);
  const value=mask(c,m,f);if(cache.size>1000)cache.clear();cache.set(k,value);return value;
 }
 function drawFixture(ctx,f,m,images,t,mix=0){
  if(Market108.isOld()||document.getElementById('beforeScene112')?.checked)return Scene112.draw(ctx,f,m,images,t,mix);
  ctx.drawImage(fixtureSprite(f,m,images,mix),f.x*t,f.y*t,2*t,t);
 }
 function utilitySprite(p,m,units){
  let entries=utilityCache.get(units);if(!entries){entries=new Map();utilityCache.set(units,entries);}const k=`${m.seed}:${m.depth||m.floorNumber}:${p.type}:${p.x},${p.y}:${p.length}`;if(entries.has(k))return entries.get(k);
  const c=canvas((p.length||1)*32),g=c.getContext('2d');g.imageSmoothingEnabled=false;const im=units[p.type];
  // Shorten the two vertical terminals to the front's height, while keeping
  // the original thick horizontal pipe and join bands, instead of flattening32px.
  if(p.type==='pipe')for(let i=0;i<p.length;i++)g.drawImage(im,i===0?0:i===p.length-1?64:32,10,32,14,i*32,top,32,height);
  else{
   const raw=PixelReducer.read(im),b=PixelReducer.bounds(raw,1),s=Math.min(28/b.w,height/b.h),w=Math.max(1,Math.round(b.w*s)),h=Math.max(1,Math.round(b.h*s));
   g.drawImage(im,b.x,b.y,b.w,b.h,Math.floor((32-w)/2),top+Math.floor((height-h)/2),w,h);
  }
  const value=mask(c,m,p);entries.set(k,value);return value;
 }
 function drawUtility(ctx,p,m,units,t=32){ctx.drawImage(utilitySprite(p,m,units),p.x*t,p.y*t,(p.length||1)*t,t);}
 root.WallMount119={top,height,allowed,fixtureSprite,utilitySprite,drawFixture,drawUtility};
})(globalThis);
