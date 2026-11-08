(function(root){
 'use strict';
 const cache=new Map(),catalog=()=>Object.fromEntries(MerchCatalog.map(m=>[m.id,m]));
 function composed(f,map,images,mix){
  const key=`${map.seed}:${map.floorNumber}:${f.type}:${f.x},${f.y}:${mix}:${Market108.isOld()}`;
  if(cache.has(key))return cache.get(key);
  const meta=catalog()[f.type],source=document.createElement('canvas');source.width=meta.width;source.height=32;
  const g=source.getContext('2d');g.imageSmoothingEnabled=false;
  g.translate(-f.x*32,-f.y*32);MarketStock.draw(g,f,map,images,32,mix);
  const shade=document.createElement('canvas');shade.width=source.width;shade.height=32;const c=shade.getContext('2d');c.drawImage(source,0,0);c.globalCompositeOperation='source-in';c.fillStyle='#081117';c.fillRect(0,0,shade.width,32);
  if(cache.size>500)cache.clear();const value={source,shade};cache.set(key,value);return value;
 }
 function draw(ctx,f,map,images,t,mix){
  if(document.getElementById('beforeScene112').checked||Market108.isOld())return MarketStock.draw(ctx,f,map,images,t,mix);
  const meta=catalog()[f.type],{source,shade}=composed(f,map,images,mix),s=t/32;
  ctx.save();ctx.translate(f.x*t,f.y*t);ctx.scale(s,s);ctx.imageSmoothingEnabled=false;
  if(meta.kind==='wall'){
   // One opening cut into the same concrete volume. The old ornamental
   // outside frame is cropped; merchandise inside keeps its existing colours.
   ctx.fillStyle='#26333b';ctx.fillRect(3,7,58,24);
   ctx.fillStyle='#53646b';ctx.fillRect(3,7,58,1);ctx.fillRect(4,30,56,1);
   ctx.fillStyle='#101a20';ctx.fillRect(4,8,56,22);
   ctx.drawImage(source,10,11,44,18,6,10,52,19);
   ctx.fillStyle='rgba(5,12,17,.42)';ctx.fillRect(5,9,54,2);ctx.fillRect(5,10,1,19);
   ctx.fillStyle='#31444e';ctx.fillRect(59,9,1,20);
  }else{
   // A short shadow lies on the ground, instead of a dark outline around
   // the entire item. Keep the original object at its exact32px footprint.
   ctx.globalAlpha=.25;ctx.drawImage(shade,0,0,32,32,3,25,28,6);ctx.globalAlpha=1;
   ctx.drawImage(source,0,0);
  }
  ctx.restore();
 }
 root.Scene112={draw};
})(globalThis);
