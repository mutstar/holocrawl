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
 const caps={'acrylic-rack':[40,27],'hoodie-rack':[40,27],'delivery-boxes':[26,24],'delivery-cart':[26,24],'shirt-stack':[38,22],'badge-trays':[38,23],'plush-basket':[38,23],'open-carton':[30,23],'folding-crates':[40,24],'recycling-bins':[40,25]};
 function rgb(hex){return[0,2,4].map(i=>parseInt(hex.slice(1+i,3+i),16));}
 function colorDistance(a,b){return Math.hypot(...rgb(a).map((v,i)=>v-rgb(b)[i]));}
 function clothingIds(f,map,mix){
  const chosen=MarketStock.select(map.seed,map.floorNumber,f,mix);if(f.type!=='hoodie-rack')return chosen;
  const hash=text=>{let n=2166136261;for(const c of text)n=Math.imul(n^c.charCodeAt(0),16777619);return n>>>0;};
  const members=MarketStock.members,byId=Object.fromEntries(members.map(m=>[m.id,m])),pool=[...members].sort((a,b)=>hash(`${map.seed}:${f.x},${f.y}:${mix}:${a.id}`)-hash(`${map.seed}:${f.x},${f.y}:${mix}:${b.id}`));
  const ids=[];for(let i=0;i<3;i++){const candidates=[byId[chosen[i]],...pool],m=candidates.find(m=>!ids.includes(m.id)&&ids.every(id=>colorDistance(byId[id].color,m.color)>=80));ids.push(m.id);}return ids;
 }
 function dyeCloth(art,original,id,ids){
  const members=Object.fromEntries(MarketStock.members.map(m=>[m.id,m])),colors=ids.map(id=>rgb(members[id].color)),g=art.getContext('2d',{willReadFrequently:true}),im=g.getImageData(0,0,art.width,art.height),a=im.data,b=original.data,w=art.width,h=art.height,slots=new Int8Array(w*h).fill(-1),sum=[0,0,0],count=[0,0,0];
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){
   const i=(y*w+x)*4,nx=x/Math.max(1,w-1),ny=y/Math.max(1,h-1),l=.2126*b[i]+.7152*b[i+1]+.0722*b[i+2];
   if(!b[i+3]||l<28)continue;
   if(id==='shirt-stack'){if(ny>.76||nx<.015||nx>.985)continue;}
   else{if(ny<.22||ny>.79||nx<.055||nx>.96)continue;if(Math.min(b[i],b[i+1],b[i+2])>190&&Math.max(b[i],b[i+1],b[i+2])-Math.min(b[i],b[i+1],b[i+2])<35)continue;}
   const slot=nx<.335?0:nx<.67?1:2;slots[y*w+x]=slot;sum[slot]+=l;count[slot]++;
  }
  const mean=sum.map((s,i)=>s/Math.max(1,count[i]));
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){const slot=slots[y*w+x];if(slot<0)continue;const i=(y*w+x)*4,l=.2126*b[i]+.7152*b[i+1]+.0722*b[i+2],factor=Math.max(.24,Math.min(1.12,l/mean[slot]))*.78;
   for(let c=0;c<3;c++)a[i+c]=Math.max(0,Math.min(255,Math.round(colors[slot][c]*factor)));
  }
  g.putImageData(im,0,0);
 }
 function bagContacts(d){
  const a=d.canvas.getContext('2d').getImageData(0,0,d.W,d.H).data,bottoms=Array(d.W).fill(-1);let lowest=-1;
  for(let x=0;x<d.W;x++)for(let y=d.H-1;y>=0;y--)if(a[(y*d.W+x)*4+3]>=96){bottoms[x]=y;lowest=Math.max(lowest,y);break;}
  return bottoms.flatMap((y,x)=>y>=lowest-4&&y>=0&&y+1<d.H?[{x,y:y+1,bodyY:y}]:[]);
 }
 function design(id,fw,fh,ids=[]){
  const key=`${id}:${fw},${fh}:${ids.join(",")}`;if(designs.has(key))return designs.get(key);
  const {source,bounds}=originals[id],W=fw*32,H=fh*32,limit=caps[id]||[W-6,H-8],scale=Math.min(Math.min(W-6,limit[0])/bounds.w,Math.min(H-5,limit[1])/bounds.h),w=Math.max(1,Math.round(bounds.w*scale)),h=Math.max(1,Math.round(bounds.h*scale));
  // Resample the preserved high-resolution source at the actual new size.
  // Do not enlarge the old32px thumbnail or replace its design with primitives.
  const reduced=PixelReducer.area(source,w,h,bounds);
  for(let i=0;i<reduced.data.length;i+=4){if(reduced.data[i+3]<96)reduced.data.fill(0,i,i+4);else reduced.data[i+3]=255;}
  const art=Market108.recolor(PixelReducer.canvas(reduced),id);if(ids.length===3)dyeCloth(art,reduced,id,ids);const x=Math.floor((W-w)/2),y=H-5-h;
  const value={art,x,y,w,h,W,H};designs.set(key,value);return value;
 }
 function sprite(f,map,mix){
  const fw=f.footW||1,fh=f.footH||1,key=`${map.seed}:${map.floorNumber}:${f.type}:${f.x},${f.y}:${fw},${fh}:${mix}`;
  if(composites.has(key))return composites.get(key);
  const selected=clothingIds(f,map,mix),isCloth=['shirt-stack','hoodie-rack'].includes(f.type),d=design(f.type,fw,fh,isCloth?selected:[]),c=document.createElement('canvas');c.width=d.W;c.height=d.H;const g=c.getContext('2d');g.imageSmoothingEnabled=false;g.drawImage(d.art,d.x,d.y);
  const meta=MerchCatalog.find(m=>m.id===f.type),ids=selected;
  if(meta.content==='acrylic')ids.forEach((id,i)=>g.drawImage(MarketStock.getSprite(id),Math.round(d.x+(3+i*9)/32*d.w),Math.round(d.y+6/32*d.h),Math.round(8/32*d.w),Math.round(13/32*d.h)));

  const shadow=document.createElement('canvas');shadow.width=d.W;shadow.height=d.H;const s=shadow.getContext('2d');s.drawImage(c,0,0);s.globalCompositeOperation='source-in';s.fillStyle='#081016';s.fillRect(0,0,d.W,d.H);
  const value={canvas:c,shadow,...d,clothingIds:isCloth?selected:[]};if(composites.size>500)composites.clear();composites.set(key,value);return value;
 }
 function draw(ctx,f,map,images,t,mix){
  if(map.compact112||document.getElementById('beforeScene112').checked||Market108.isOld())return Scene112.draw(ctx,f,map,images,t,mix);
  const d=sprite(f,map,mix),s=t/32,bottom=d.y+d.h;
  ctx.save();ctx.translate(f.x*t,f.y*t);ctx.scale(s,s);ctx.beginPath();ctx.rect(0,0,d.W,d.H);ctx.clip();ctx.imageSmoothingEnabled=false;
  if(f.type==='shopping-bags'){
   const contacts=bagContacts(d);ctx.fillStyle='#081016';
   ctx.globalAlpha=.15;for(const p of contacts)ctx.fillRect(p.x+1,p.y+1,1,1);
   ctx.globalAlpha=.38;for(const p of contacts)ctx.fillRect(p.x,p.y,1,1);
  }else{
  ctx.globalAlpha=.17;ctx.drawImage(d.shadow,d.x,d.y,d.w,d.h,d.x+4,bottom-4,d.w+6,8);
  ctx.globalAlpha=.26;ctx.drawImage(d.shadow,d.x,d.y,d.w,d.h,d.x+2,bottom-2,d.w+3,5);
  ctx.globalAlpha=.46;ctx.drawImage(d.shadow,d.x,d.y,d.w,d.h,d.x+1,bottom-1,d.w,3);
  }
  ctx.globalAlpha=1;ctx.drawImage(d.canvas,0,0);ctx.restore();
 }
 root.Scene117={load,draw,sprite,design,clothingIds,bagContacts};
 const previousDescription=MarketStock.describe;
 MarketStock.describe=(f,map,mix=0)=>f.type==='hoodie-rack'
  ?'후드 상품 랙 · '+clothingIds(f,map,mix).map(id=>MarketStock.members.find(m=>m.id===id).name).join(' / ')
  :previousDescription(f,map,mix);
})(globalThis);
