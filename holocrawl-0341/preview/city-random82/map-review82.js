(async()=>{
 const manifest=await(await fetch('manifest.json')).json();
 const sampleParameter=Number(new URLSearchParams(location.search).get('sample'));
 const sampleIndex=manifest.maps?Math.max(0,Math.min(manifest.maps.length-1,Number.isFinite(sampleParameter)?Math.floor(sampleParameter):0)):0;
 const map=await(await fetch(manifest.maps?manifest.maps[sampleIndex].file:'map.json')).json();
 const atlases={};
 await Promise.all(['floor','wall','feat'].map(name=>new Promise((resolve,reject)=>{
  const image=new Image();image.onload=()=>{atlases[name]=image;resolve();};image.onerror=reject;image.src=`assets/${name}.png?v=${manifest.wallArtRevision||map.seed}`;
 })));
 const field=document.getElementById('map'),c=field.getContext('2d');
 const parameters=new URLSearchParams(location.search);
 const center={x:map.width/2,y:map.height/2};let mode='fit', view;
 if(parameters.has('cx')&&parameters.has('cy')){
  const x=Number(parameters.get('cx')),y=Number(parameters.get('cy'));
  if(Number.isFinite(x)&&Number.isFinite(y)&&x>=0&&y>=0&&x<=map.width&&y<=map.height){center.x=x;center.y=y;mode=parameters.get('zoom')==='2'?'double':'actual';}
 }
 function tile(context,index,x,y,scale){const t=map.palette[index];context.drawImage(atlases[t.atlas],t.sx,t.sy,t.width,t.height,x+t.dx*scale,y+t.dy*scale,t.width*scale,t.height*scale);}
 function render(context,scale,ox,oy){
  context.imageSmoothingEnabled=false;
  for(let y=0;y<map.height;y++)for(let x=0;x<map.width;x++){
   const index=y*map.width+x,px=ox+x*32*scale,py=oy+y*32*scale;
   tile(context,map.floors[index],px,py,scale);tile(context,map.features[index],px,py,scale);
  }
 }
 const full=document.createElement('canvas');full.width=map.width*32;full.height=map.height*32;
 render(full.getContext('2d'),1,0,0);
 function draw(){
  const scale=mode==='fit'?Math.min(field.width/(map.width*32),field.height/(map.height*32)):mode==='actual'?1:2;
  const ox=mode==='fit'?(field.width-map.width*32*scale)/2:field.width/2-center.x*32*scale;
  const oy=mode==='fit'?(field.height-map.height*32*scale)/2:field.height/2-center.y*32*scale;
  c.fillStyle='#0e1216';c.fillRect(0,0,field.width,field.height);
  c.imageSmoothingEnabled=false;c.drawImage(full,ox,oy,full.width*scale,full.height*scale);view={scale,ox,oy};
  for(const name of ['fit','actual','double'])document.getElementById(name).setAttribute('aria-pressed',mode===name);
 }
 function resize(){field.width=Math.min(1250,Math.max(320,innerWidth-42));field.height=Math.max(420,Math.min(850,innerHeight-250));draw();}
 for(const name of ['fit','actual','double'])document.getElementById(name).onclick=()=>{mode=name;draw();};
 field.onclick=event=>{
  const rect=field.getBoundingClientRect();
  center.x=Math.max(0,Math.min(map.width,((event.clientX-rect.left)*field.width/rect.width-view.ox)/view.scale/32));
  center.y=Math.max(0,Math.min(map.height,((event.clientY-rect.top)*field.height/rect.height-view.oy)/view.scale/32));
  if(mode==='fit')mode='actual';draw();field.focus();
  document.getElementById('status').textContent=`${Math.floor(center.x)},${Math.floor(center.y)} 주변 · ${mode==='double'?'2배':'원본 크기'}`;
 };
 field.onkeydown=event=>{
  const directions={ArrowLeft:[-2,0],ArrowRight:[2,0],ArrowUp:[0,-2],ArrowDown:[0,2]};
  if(!directions[event.key])return;event.preventDefault();const [x,y]=directions[event.key];
  center.x=Math.max(0,Math.min(map.width,center.x+x));center.y=Math.max(0,Math.min(map.height,center.y+y));if(mode==='fit')mode='actual';draw();
 };
 document.getElementById('summary').textContent=`시드 ${map.seed} · 잔향도시 1층 · ${map.width}×${map.height}칸 · 시설 제외 · 현재 벽 타일`;
 const samples=document.getElementById('sample');
 if(samples&&manifest.maps){
  samples.replaceChildren(...manifest.maps.map((entry,index)=>new Option(`${index+1}번 · ${entry.seed}`,String(index))));samples.value=String(sampleIndex);
  samples.onchange=()=>{const query=new URLSearchParams();query.set('sample',samples.value);location.search=query.toString();};
 }
 addEventListener('resize',resize);resize();
 window.wallMapReview82={map,manifest,fullImage:()=>full.toDataURL(),getView:()=>({...view,mode})};window.ready=true;
})().catch(error=>{document.getElementById('summary').textContent=`불러오기 실패: ${error.message}`;throw error;});
