(async()=>{
 const manifest=await(await fetch('manifest.json')).json(),params=new URLSearchParams(location.search);
 const field=document.getElementById('map'),c=field.getContext('2d'),doorButton=document.getElementById('doors');
 let sample=Math.min(manifest.maps.length-1,Math.max(0,Number(params.get('sample'))||0));
 let style='new95',mode='fit',view,loading=false,images={},openedImage,doorsOpen=false,drag=null;
 let center={x:40,y:35};
 if(params.get('focus')==='facility'){center={...manifest.maps[sample].focus};mode='double'}
 const select=document.getElementById('sample');
 select.replaceChildren(...manifest.maps.map((m,i)=>new Option(m.name,String(i))));select.value=String(sample);
 const loadImage=url=>new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>resolve(image);image.onerror=()=>reject(new Error('그림 불러오기 실패: '+url));image.src=url});
 async function load(){loading=true;window.ready=false;document.getElementById('status').textContent='시설을 불러오는 중…';
  const map=manifest.maps[sample],loaded=await Promise.all([...manifest.styles.map(s=>loadImage(map.images[s.id])),loadImage(map.openImage)]);
  images=Object.fromEntries(manifest.styles.map((s,i)=>[s.id,loaded[i]]));openedImage=loaded.at(-1);doorsOpen=false;loading=false;draw();window.ready=true;
 }
 function currentImage(){return style==='new95'&&doorsOpen?openedImage:images[style]}
 function draw(){if(loading||!currentImage())return;const map=manifest.maps[sample],image=currentImage();
  const scale=mode==='fit'?Math.min(field.width/image.width,field.height/image.height):mode==='double'?2:1;
  const ox=mode==='fit'?(field.width-image.width*scale)/2:field.width/2-center.x*32*scale;
  const oy=mode==='fit'?(field.height-image.height*scale)/2:field.height/2-center.y*32*scale;
  c.fillStyle='#101719';c.fillRect(0,0,field.width,field.height);c.imageSmoothingEnabled=false;c.drawImage(image,ox,oy,image.width*scale,image.height*scale);
  view={scale,ox,oy,mode,style,sample,doorsOpen,center:{...center}};
  document.querySelectorAll('[data-style]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.style===style)));
  document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===mode)));
  doorButton.disabled=style!=='new95'||!map.doors.length;
  doorButton.textContent=style!=='new95'?'수정 전 문':!map.doors.length?'열린 입구 · 문틀만':'문 '+(doorsOpen?'닫기':'열기');
  doorButton.setAttribute('aria-pressed',String(doorsOpen));document.getElementById('fullImage').href=image.src;
  document.getElementById('meta').textContent=`${map.name} · 시드${map.seed} · 원래 지형과 출입 위치 유지`;
  document.getElementById('status').textContent=mode==='fit'?'전체 지도 · 누르면 해당 위치로 확대합니다.':`${Math.floor(center.x)},${Math.floor(center.y)} 주변 · ${mode==='double'?'2배 확대':'원본 크기'} · 드래그로 이동`;
 }
 function resize(){field.width=Math.max(280,Math.min(1440,Math.round(field.getBoundingClientRect().width)));field.height=Math.max(420,Math.min(1000,innerHeight-245));draw()}
 document.querySelectorAll('[data-style]').forEach(b=>b.onclick=()=>{style=b.dataset.style;draw()});
 document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{mode=b.dataset.mode;draw()});
 doorButton.onclick=()=>{if(loading||doorButton.disabled)return;doorsOpen=!doorsOpen;draw()};
 document.getElementById('facility').onclick=()=>{center={...manifest.maps[sample].focus};mode='double';draw()};
 document.getElementById('entrance').onclick=()=>{const p=manifest.maps[sample].entrances[0];center={x:p.x+.5,y:p.y+.5};mode='double';draw()};
 select.onchange=()=>{sample=Number(select.value);center={...manifest.maps[sample].focus};load()};
 const point=e=>{const r=field.getBoundingClientRect();return {x:(e.clientX-r.left)*field.width/r.width,y:(e.clientY-r.top)*field.height/r.height}};
 field.onpointerdown=e=>{if(loading)return;const p=point(e);drag={p,last:p,moved:false};field.setPointerCapture(e.pointerId);field.focus()};
 field.onpointermove=e=>{if(!drag||mode==='fit')return;const p=point(e);if(Math.hypot(p.x-drag.p.x,p.y-drag.p.y)>4)drag.moved=true;
  if(drag.moved){center.x=Math.max(0,Math.min(80,center.x-(p.x-drag.last.x)/view.scale/32));center.y=Math.max(0,Math.min(70,center.y-(p.y-drag.last.y)/view.scale/32));draw()}drag.last=p};
 field.onpointerup=e=>{if(!drag)return;if(!drag.moved){const p=point(e);center={x:Math.max(0,Math.min(80,(p.x-view.ox)/view.scale/32)),y:Math.max(0,Math.min(70,(p.y-view.oy)/view.scale/32))};if(mode==='fit')mode='actual';draw()}drag=null};field.onpointercancel=()=>drag=null;
 field.onkeydown=e=>{const d={ArrowLeft:[-2,0],ArrowRight:[2,0],ArrowUp:[0,-2],ArrowDown:[0,2]}[e.key];if(!d)return;e.preventDefault();center={x:Math.max(0,Math.min(80,center.x+d[0])),y:Math.max(0,Math.min(70,center.y+d[1]))};if(mode==='fit')mode='actual';draw()};
 addEventListener('resize',resize);resize();await load();window.cityFacilities95={manifest,getView:()=>view,getImage:()=>currentImage().src};
})().catch(error=>{document.getElementById('status').textContent=error.message;throw error});
