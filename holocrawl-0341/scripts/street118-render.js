 const propImages={},sources118={body:'body',boots:'boots',armour:'armour',helmet:'helmet',sword:'sword'};
 const assetJobs=Object.entries(sources118).map(async([k,v])=>propImages[k]=await loadImage(`../city-market02/assets/${v}.png`));
 assetJobs.push(...MerchCatalog.map(async m=>propImages[m.id]=await loadImage(m.file)));
 assetJobs.push(...MarketMembers.map(async m=>propImages['member-'+m.id]=await loadImage(m.image)));
 assetJobs.push(...Object.entries({fence:'../city-market02/assets/fence-cutout32.png',reference:'../city-market02/assets/scene-reference.png',pipe:'../city-batch22/assets/wall-pipe-elbows10-96.png',cabinet:'../city-batch22/assets/wall-cabinet08-32.png'}).map(async([k,v])=>propImages[k]=await loadImage(v)));
 await Promise.all([Market108.load(),Scene117.load(),...assetJobs]);
 Market108.prepare(propImages);MarketStock.makeSprites(propImages);
 const utility118={};
 for(const[type,crop]of Object.entries({air:[289,34,37,19],vent:[294,86,22,16]})){
  const c=document.createElement('canvas');c.width=c.height=32;const q=c.getContext('2d');q.imageSmoothingEnabled=false;
  const w=type==='air'?28:22,h=type==='air'?15:16;q.drawImage(propImages.reference,...crop,(32-w)/2,32-h-2,w,h);utility118[type]=Market108.recolor(c,type);
 }
 utility118.pipe=Market108.recolor(propImages.pipe,'pipe');utility118.cabinet=Market108.recolor(propImages.cabinet,'cabinet');
 function drawAmbient118(ctx,plan,m,images,s,ox,oy,seen,fog){
  const stock={seed:String(m.seed),floorNumber:m.depth};ctx.save();ctx.translate(ox,oy);ctx.scale(s,s);ctx.imageSmoothingEnabled=false;
  function clipped(p,fw,fh,paint){for(let dy=0;dy<fh;dy++)for(let dx=0;dx<fw;dx++){
   const x=p.x+dx,y=p.y+dy,i=y*m.width+x;if(fog&&!state.explored[i])continue;
   ctx.save();ctx.beginPath();ctx.rect(x*32,y*32,32,32);ctx.clip();
   if(fog&&!seen[i]){
    const c=document.createElement('canvas');c.width=fw*32;c.height=fh*32;const q=c.getContext('2d');q.imageSmoothingEnabled=false;q.translate(-p.x*32,-p.y*32);paint(q);q.setTransform(1,0,0,1,0,0);q.globalCompositeOperation='source-atop';q.fillStyle='rgba(0,0,0,.77)';q.fillRect(0,0,c.width,c.height);ctx.drawImage(c,p.x*32,p.y*32);
   }else paint(ctx);ctx.restore();
  }}
  for(const p of plan.walls)clipped(p,2,1,q=>Scene112.draw(q,p,stock,images,32,0));
  for(const p of plan.infra)clipped(p,p.length,1,q=>{
   if(p.type==='pipe')for(let i=0;i<p.length;i++)q.drawImage(utility118.pipe,i===0?0:i===p.length-1?64:32,0,32,32,(p.x+i)*32,p.y*32,32,32);
   else q.drawImage(utility118[p.type],p.x*32,p.y*32,32,32);
  });
  for(const p of plan.floor)clipped(p,p.footW,p.footH,q=>Scene117.draw(q,p,stock,images,32,0));
  for(const p of plan.fences)clipped(p,1,1,q=>q.drawImage(Market108.images.fence,p.x*32,p.y*32+8,32,24));
  ctx.restore();
 }
 function focusAmbient(kind){
  const p=kind==='shops'?ambient.walls.find(a=>a.type==='acrylic-window'):kind==='crate'?ambient.floor.find(a=>a.type==='delivery-boxes'):ambient.infra.find(a=>a.type==='pipe')||ambient.infra[0];
  if(!p)return;const points=[];for(let y=Math.max(1,p.y-4);y<Math.min(map.height-1,p.y+5);y++)for(let x=Math.max(1,p.x-4);x<Math.min(map.width-1,p.x+(p.length||2)+4);x++)if(pass(x,y))points.push({x,y});
  points.sort((a,b)=>Math.hypot(a.x-p.x-(p.length||2)/2,a.y-p.y-2)-Math.hypot(b.x-p.x-(p.length||2)/2,b.y-p.y-2));
  if(points[0])reset(points[0],kind==='shops'?'초반 거리 진열창':kind==='crate'?'택배상자와 길가 소품':'기존 실외기·환기구·배관을 최신 벽에 연결');
 }
