(async()=>{
 const manifest=await(await fetch('manifest.json')).json();
 const params=new URLSearchParams(location.search),field=document.getElementById('map'),c=field.getContext('2d');
 let sample=Math.min(manifest.maps.length-1,Math.max(0,Number(params.get('sample'))||0));
 let style=manifest.styles.some(s=>s.id===params.get('style'))?params.get('style'):'concrete92';
 let mode='fit',view,loading=false,images={},drag=null;
 let center={x:40,y:35};
 if(params.has('cx')&&params.has('cy')){center={x:Number(params.get('cx')),y:Number(params.get('cy'))};mode=params.get('zoom')==='2'?'double':'actual'}
 const sampleSelect=document.getElementById('sample');sampleSelect.replaceChildren(...manifest.maps.map((m,i)=>new Option('새 랜덤 지도 ·'+m.seed,String(i))));sampleSelect.value=String(sample);
 async function load(){loading=true;document.getElementById('status').textContent='지도를 불러오는 중…';
  const next={};await Promise.all(manifest.styles.map(s=>new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>{next[s.id]=image;resolve()};image.onerror=()=>reject(new Error(s.label+' 이미지 불러오기 실패'));image.src=manifest.maps[sample].images[s.id]})));images=next;loading=false;draw();window.ready=true;
 }
 function draw(){if(loading||!images[style])return;const image=images[style],map=manifest.maps[sample];
  const scale=mode==='fit'?Math.min(field.width/image.width,field.height/image.height):mode==='double'?2:1;
  const ox=mode==='fit'?(field.width-image.width*scale)/2:field.width/2-center.x*32*scale;
  const oy=mode==='fit'?(field.height-image.height*scale)/2:field.height/2-center.y*32*scale;
  c.fillStyle='#101719';c.fillRect(0,0,field.width,field.height);c.imageSmoothingEnabled=false;
  c.drawImage(image,ox,oy,image.width*scale,image.height*scale);view={scale,ox,oy,mode,style,sample,center:{...center}};
  document.querySelectorAll('[data-style]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.style===style)));
  document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===mode)));
  document.getElementById('fullImage').href=map.images[style];
  document.getElementById('status').textContent=mode==='fit'?'전체 지도 · 누르면 그 위치를 확대합니다.':`${Math.floor(center.x)},${Math.floor(center.y)} 주변 · ${mode==='double'?'2배 확대':'원본 크기'} · 드래그 또는 방향키로 이동`;
  document.getElementById('meta').textContent=`시드${map.seed} · 잔향도시1층 · ${map.width}×${map.height}칸 · ${manifest.styles.find(s=>s.id===style).label} · 시설 제외`;
 }
 function resize(){field.width=Math.max(280,Math.min(1440,Math.round(field.getBoundingClientRect().width)));field.height=Math.max(420,Math.min(1000,innerHeight-245));draw()}
 document.querySelectorAll('[data-style]').forEach(b=>b.onclick=()=>{style=b.dataset.style;draw()});
 document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{mode=b.dataset.mode;draw()});
 document.getElementById('corner').onclick=()=>{center={...manifest.maps[sample].focus};mode='double';draw();field.focus()};
 sampleSelect.onchange=()=>{sample=Number(sampleSelect.value);center={x:40,y:35};mode='fit';window.ready=false;load()};
 const point=e=>{const r=field.getBoundingClientRect();return {x:(e.clientX-r.left)*field.width/r.width,y:(e.clientY-r.top)*field.height/r.height}};
 field.onpointerdown=e=>{if(loading)return;const p=point(e);drag={p,last:p,moved:false};field.setPointerCapture(e.pointerId);field.focus()};
 field.onpointermove=e=>{if(!drag||mode==='fit')return;const p=point(e);if(Math.hypot(p.x-drag.p.x,p.y-drag.p.y)>4)drag.moved=true;
  if(drag.moved){center.x=Math.max(0,Math.min(80,center.x-(p.x-drag.last.x)/view.scale/32));center.y=Math.max(0,Math.min(70,center.y-(p.y-drag.last.y)/view.scale/32));draw()}drag.last=p};
 field.onpointerup=e=>{if(!drag)return;if(!drag.moved){const p=point(e);center={x:Math.max(0,Math.min(80,(p.x-view.ox)/view.scale/32)),y:Math.max(0,Math.min(70,(p.y-view.oy)/view.scale/32))};if(mode==='fit')mode='actual';draw()}drag=null};
 field.onpointercancel=()=>drag=null;
 field.onkeydown=e=>{const delta={ArrowLeft:[-2,0],ArrowRight:[2,0],ArrowUp:[0,-2],ArrowDown:[0,2]}[e.key];if(!delta)return;e.preventDefault();center={x:Math.max(0,Math.min(80,center.x+delta[0])),y:Math.max(0,Math.min(70,center.y+delta[1]))};if(mode==='fit')mode='actual';draw()};
 addEventListener('resize',resize);resize();await load();
 window.cityRandom93={manifest,getView:()=>view,getImage:()=>images[style].src};
})().catch(error=>{document.getElementById('status').textContent=error.message;throw error});
