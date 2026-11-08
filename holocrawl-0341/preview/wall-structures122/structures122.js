(function(root){
 'use strict';
 const cache=new Map(),unitCache=new WeakMap(),byId=()=>Object.fromEntries(MarketStock.members.map(m=>[m.id,m]));
 function canvas(w){const c=document.createElement('canvas');c.width=w;c.height=32;return c;}
 function hash(text){let h=2166136261;for(const c of String(text))h=Math.imul(h^c.charCodeAt(0),16777619);return h>>>0;}
 function style(f,m){const floor=m.floorNumber||m.depth||1;return{floor,age:Math.max(0,floor-3),seed:hash(`${m.seed}:${floor}:${f.type}:${f.x},${f.y}:122`)};}
 function random(seed){return()=>{seed+=0x6D2B79F5;let t=Math.imul(seed^(seed>>>15),seed|1);t^=t+Math.imul(t^(t>>>7),t|61);return((t^(t>>>14))>>>0)/4294967296;};}
 function finish(c,m,f){const g=c.getContext('2d'),a=g.getImageData(0,0,c.width,32);for(let y=0;y<32;y++)for(let x=0;x<c.width;x++)if(!WallHeight121.allowed(m,f,x,y))a.data.fill(0,(y*c.width+x)*4,(y*c.width+x)*4+4);g.putImageData(a,0,0);return c;}
 function frame(g){
  g.fillStyle='rgba(3,10,16,.48)';g.fillRect(4,12,58,19);
  g.fillStyle='#526873';g.fillRect(3,11,58,19);g.fillStyle='#83959d';g.fillRect(4,11,56,1);
  g.fillStyle='#263b46';g.fillRect(4,12,56,18);g.fillStyle='#13232c';g.fillRect(5,13,54,16);
  g.fillStyle='#102029';g.fillRect(60,12,1,18);g.fillStyle='#708892';g.fillRect(4,30,56,1);
  g.fillStyle='#304852';g.fillRect(5,29,54,1);
 }
 function glass(g){
  // Reflection stays in the gaps; silhouettes and member colours remain clear.
  g.fillStyle='#203641';g.fillRect(6,13,3,6);g.fillStyle='#2d4550';g.fillRect(7,13,1,4);
  for(const x of [23,41]){g.fillStyle='#20343e';g.fillRect(x,13,2,16);g.fillStyle='#465e68';g.fillRect(x,13,1,15);}
 }
 function scuff(g,s,bounds={x:3,y:11,w:58,h:20},shutter=false){
  if(!s.age)return;const r=random(s.seed);for(let i=0;i<s.age*2;i++){
   const x=bounds.x+2+Math.floor(r()*(bounds.w-5)),y=shutter?bounds.y+2+Math.floor(r()*(bounds.h-4)):r()<.5?bounds.y:bounds.y+bounds.h-1;
   g.fillStyle=i%3===0?'#5a4c47':'#26343b';g.fillRect(x,y,1+Math.floor(r()*3),1);
   if(shutter&&r()<.5){g.fillStyle='#526069';g.fillRect(x,y+1,2,1);}
  }
 }
 function shutter(g,images,half,s){
  frame(g);const art=Market108.images[half?'half-shutter':'closed-shutter'];
  if(half){
   g.drawImage(art,10,20,44,9,6,21,52,8);
   g.fillStyle='#374a55';g.fillRect(5,13,54,8);
  }else g.drawImage(art,8,7,48,23,5,13,54,16);
  const bottom=half?20:28;
  for(let y=13;y<=bottom;y+=3){g.fillStyle='#62737b';g.fillRect(6,y,52,1);g.fillStyle='#283943';g.fillRect(6,y+1,52,1);}
  g.fillStyle='#8b989c';g.fillRect(6,bottom,52,1);g.fillStyle='#172832';g.fillRect(6,bottom+1,52,1);
  if(!half){g.fillStyle='#182932';g.fillRect(30,26,4,2);g.fillStyle='#879398';g.fillRect(31,26,2,1);}
  scuff(g,s,{x:5,y:12,w:54,h:18},true);
 }
 function fixtureSprite(f,m,images,mix=0){
  const k=`${m.seed}:${m.floorNumber||m.depth}:${f.type}:${f.x},${f.y}:${mix}`;if(cache.has(k))return cache.get(k);
  const c=canvas(64),g=c.getContext('2d'),s=style(f,m);g.imageSmoothingEnabled=false;
  const ids=MarketStock.select(m.seed,s.floor,f,mix),members=byId();
  if(f.type==='closed-shutter'||f.type==='half-shutter')shutter(g,images,f.type==='half-shutter',s);
  else if(f.type==='poster-wall'){
   const art=Market108.images['poster-wall'];
   for(let i=0;i<3;i++){const x=6+i*18;g.fillStyle='rgba(3,11,16,.5)';g.fillRect(x+1,13,13,18);g.fillStyle='#859096';g.fillRect(x,12,13,18);g.drawImage(art,13+i*13,9,11,18,x+1,13,11,16);g.fillStyle='#a2a8a4';g.fillRect(x+1,12,2,1);if(s.age>=3){g.clearRect(x+11,28,2,2);g.clearRect(x,12,1,1);}}
  }else{
   frame(g);glass(g);
   if(f.type==='acrylic-window'){
    g.fillStyle='#324b57';g.fillRect(6,28,52,1);g.fillStyle='#81969d';g.fillRect(6,29,52,1);
    ids.forEach((id,i)=>{const x=9+i*18;g.drawImage(MarketStock.getSprite(id),x,13,10,15);g.fillStyle='#a2b7be';g.fillRect(x+1,28,8,1);g.fillStyle=members[id].color;g.fillRect(x+4,29,3,1);});
   }else if(f.type==='shirt-window'){
    g.fillStyle='#82959d';g.fillRect(7,13,50,1);g.fillStyle='#344d59';g.fillRect(7,14,50,1);
    ids.forEach((id,i)=>{const x=7+i*18;g.fillStyle='#99a7aa';g.fillRect(x+6,14,2,1);g.drawImage(MarketStock.getShirt(id),x,15,14,14);});
   }
   scuff(g,s);
  }
  const value=finish(c,m,f);if(cache.size>1000)cache.clear();cache.set(k,value);return value;
 }
 function utilitySprite(p,m,units){
  let entries=unitCache.get(units);if(!entries){entries=new Map();unitCache.set(units,entries);}const s=style(p,m),k=`${m.seed}:${s.floor}:${p.type}:${p.x},${p.y}:${p.length}`;if(entries.has(k))return entries.get(k);
  const c=canvas((p.length||1)*32),g=c.getContext('2d'),art=canvas(c.width),q=art.getContext('2d'),image=units[p.type];g.imageSmoothingEnabled=q.imageSmoothingEnabled=false;
  if(p.type==='pipe'){
   for(let i=0;i<p.length;i++)q.drawImage(image,i===0?0:i===p.length-1?64:32,1,32,30,i*32,12,32,18);
   if(s.seed%2===0){const x=Math.floor(c.width/2);q.fillStyle='#263941';q.fillRect(x-3,20,7,5);q.fillStyle='#78565a';q.fillRect(x-2,19,5,1);q.fillRect(x-2,24,5,1);q.fillRect(x-3,20,1,4);q.fillRect(x+3,20,1,4);q.fillStyle='#aa8380';q.fillRect(x-1,19,2,1);q.fillStyle='#b1a5a0';q.fillRect(x,21,1,2);}
  }else{
   const raw=PixelReducer.read(image),b=PixelReducer.bounds(raw,1),limit=p.type==='cabinet'?18:17,scale=Math.min(1,28/b.w,limit/b.h),w=Math.max(1,Math.round(b.w*scale)),h=Math.max(1,Math.round(b.h*scale)),x=Math.floor((32-w)/2),y=12+Math.floor((18-h)/2);
   if(p.type==='vent'){q.fillStyle='#172a34';q.fillRect(x-1,y-1,w+2,h+2);}
   q.drawImage(image,b.x,b.y,b.w,b.h,x,y,w,h);
   if(p.type==='air'){q.fillStyle='#30434d';q.fillRect(x+3,y+h,2,2);q.fillRect(x+w-5,y+h,2,2);q.fillStyle='#8c9ba0';q.fillRect(x+3,y+h,1,1);q.fillRect(x+w-5,y+h,1,1);}
   if(p.type==='cabinet'){q.fillStyle='#304b56';q.fillRect(x+3,y+h,1,2);q.fillRect(x+w-4,y+h,1,2);q.fillStyle='#85999e';q.fillRect(x+1,y+3,1,1);}
  }
  const shade=canvas(c.width),sg=shade.getContext('2d');sg.drawImage(art,0,0);sg.globalCompositeOperation='source-in';sg.fillStyle='#07131b';sg.fillRect(0,0,c.width,32);g.globalAlpha=.42;g.drawImage(shade,1,1);g.globalAlpha=1;g.drawImage(art,0,0);
  if(s.age>=2){const damage=canvas(c.width),dg=damage.getContext('2d');scuff(dg,s,{x:3,y:12,w:c.width-6,h:18},false);dg.globalCompositeOperation='destination-in';dg.drawImage(art,0,0);g.drawImage(damage,0,0);}
  const value=finish(c,m,p);entries.set(k,value);return value;
 }
 function drawFixture(ctx,f,m,images,t,mix=0){if(Market108.isOld()||document.getElementById('beforeScene112')?.checked)return Scene112.draw(ctx,f,m,images,t,mix);ctx.drawImage(fixtureSprite(f,m,images,mix),f.x*t,f.y*t,2*t,t);}
 function drawUtility(ctx,p,m,units,t=32){ctx.drawImage(utilitySprite(p,m,units),p.x*t,p.y*t,(p.length||1)*t,t);}
 root.WallStructures122={style,fixtureSprite,utilitySprite,drawFixture,drawUtility};
 const oldGallery=MarketStock.gallery;
 MarketStock.gallery=images=>{oldGallery(images);const grid=document.getElementById('propSwatches');if(!grid||Market108.isOld())return;const m={w:4,h:2,cells:[0,0,0,0,1,1,1,1],seed:'STRUCT122-CATALOG',floorNumber:4};MerchCatalog.forEach((meta,i)=>{if(meta.kind!=='wall')return;const c=grid.children[i]?.querySelector('canvas');if(!c)return;const g=c.getContext('2d');g.imageSmoothingEnabled=false;g.clearRect(0,0,c.width,c.height);for(let x=0;x<2;x++)WallHeight121.wall(g,m.cells,4,2,x,0,32,0);drawFixture(g,{type:meta.id,x:0,y:0},m,images,32,0);});};
})(globalThis);
