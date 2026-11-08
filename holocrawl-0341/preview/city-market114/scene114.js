(function(root){
 'use strict';
 const originals={},designs=new Map(),composites=new Map();
 const image=url=>new Promise((resolve,reject)=>{const a=new Image();a.onload=()=>resolve(a);a.onerror=()=>reject(Error(url));a.src=url;});
 async function load(){
  await Promise.all(MerchCatalog.filter(m=>m.kind==='floor').map(async m=>{
   const url=m.id==='delivery-boxes'?'../city-market01/assets/market-delivery-boxes-original.png':`../city-market02/assets/props/originals/${m.id}.png`;
   const source=PixelReducer.read(await image(url));originals[m.id]={source,bounds:PixelReducer.bounds(source,180)};
  }));
 }
 function design(id,fw,fh){
  const key=`${id}:${fw},${fh}`;if(designs.has(key))return designs.get(key);
  const {source,bounds}=originals[id],W=fw*32,H=fh*32,scale=Math.min((W-6)/bounds.w,(H-8)/bounds.h),w=Math.max(1,Math.round(bounds.w*scale)),h=Math.max(1,Math.round(bounds.h*scale));
  // Resample the preserved high-resolution source at the actual new size.
  // Do not enlarge the old32px thumbnail or replace its design with primitives.
  const reduced=PixelReducer.area(source,w,h,bounds);
  for(let i=0;i<reduced.data.length;i+=4){if(reduced.data[i+3]<96)reduced.data.fill(0,i,i+4);else reduced.data[i+3]=255;}
  const art=Market108.recolor(PixelReducer.canvas(reduced),id),x=Math.floor((W-w)/2),y=H-5-h;
  const value={art,x,y,w,h,W,H};designs.set(key,value);return value;
 }
 function sprite(f,map,mix){
  const fw=f.footW||1,fh=f.footH||1,key=`${map.seed}:${map.floorNumber}:${f.type}:${f.x},${f.y}:${fw},${fh}:${mix}`;
  if(composites.has(key))return composites.get(key);
  const d=design(f.type,fw,fh),c=document.createElement('canvas');c.width=d.W;c.height=d.H;const g=c.getContext('2d');g.imageSmoothingEnabled=false;g.drawImage(d.art,d.x,d.y);
  const meta=MerchCatalog.find(m=>m.id===f.type),ids=MarketStock.select(map.seed,map.floorNumber,f,mix);
  if(meta.content==='acrylic')ids.forEach((id,i)=>g.drawImage(MarketStock.getSprite(id),Math.round(d.x+(3+i*9)/32*d.w),Math.round(d.y+6/32*d.h),Math.round(8/32*d.w),Math.round(13/32*d.h)));
  if(meta.content==='shirts')ids.forEach((id,i)=>g.drawImage(MarketStock.getShirt(id),Math.round(d.x+(3+i*8)/32*d.w),Math.round(d.y+(8+i*3)/32*d.h),Math.round(10/32*d.w),Math.round(10/32*d.h)));
  const shadow=document.createElement('canvas');shadow.width=d.W;shadow.height=d.H;const s=shadow.getContext('2d');s.drawImage(c,0,0);s.globalCompositeOperation='source-in';s.fillStyle='#081016';s.fillRect(0,0,d.W,d.H);
  const value={canvas:c,shadow,...d};if(composites.size>500)composites.clear();composites.set(key,value);return value;
 }
 function draw(ctx,f,map,images,t,mix){
  if(map.compact112||document.getElementById('beforeScene112').checked||Market108.isOld())return Scene112.draw(ctx,f,map,images,t,mix);
  const d=sprite(f,map,mix),s=t/32,bottom=d.y+d.h;
  ctx.save();ctx.translate(f.x*t,f.y*t);ctx.scale(s,s);ctx.beginPath();ctx.rect(0,0,d.W,d.H);ctx.clip();ctx.imageSmoothingEnabled=false;
  ctx.globalAlpha=.17;ctx.drawImage(d.shadow,d.x,d.y,d.w,d.h,d.x+4,bottom-4,d.w+6,8);
  ctx.globalAlpha=.26;ctx.drawImage(d.shadow,d.x,d.y,d.w,d.h,d.x+2,bottom-2,d.w+3,5);
  ctx.globalAlpha=.46;ctx.drawImage(d.shadow,d.x,d.y,d.w,d.h,d.x+1,bottom-1,d.w,3);
  ctx.globalAlpha=1;ctx.drawImage(d.canvas,0,0);ctx.restore();
 }
 root.Scene114={load,draw,sprite,design};
})(globalThis);
