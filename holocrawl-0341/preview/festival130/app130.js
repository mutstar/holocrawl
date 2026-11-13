(async()=>{
 'use strict';
 const canvas=(w,h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return c;},g=c=>{const q=c.getContext('2d',{willReadFrequently:true});q.imageSmoothingEnabled=false;return q;};
 const load=u=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>reject(Error(u));im.src=u;}),json=async u=>{const r=await fetch(u);if(!r.ok)throw Error(u);return r.json();};
 const stallCatalog=new URL('../festival214/stalls214.json?v=228',location.href);
 const propCatalog=new URL('../festival215/props215.json?v=230',location.href);
 const [propSpecs,stallSpecs,source,wall,material,rects,planes,featAtlas,floorAtlas,surfaceAtlas,festivalDoor]=await Promise.all([json(propCatalog),json(stallCatalog),json('../native-play107/maps/map-10786001-1.json'),load('../wall-height121/wall22.png'),load('../festival125/assets/wall-source.png'),json('../wall-height121/rects121.json'),json('../wall-height121/planes121.json'),load('../native-play107/assets/feat.png'),load('../native-play107/assets/floor.png'),load('../festival216/assets/surfaces216.png'),load('../festival217/assets/door217.png')]);
 const sprites={},names={},actor={};await Promise.all([...propSpecs.map(async s=>{sprites[s.id]=await load(new URL(s.native,propCatalog));names[s.id]=s.name;}),...stallSpecs.map(async s=>{sprites[s.id]=await load(new URL(s.native,stallCatalog));names[s.id]=s.name;}),...['body','boots','armour','helmet','sword'].map(async k=>actor[k]=await load(`../city-market02/assets/${k}.png`))]);
 const brokenSprites=Object.fromEntries(stallSpecs.map(({id})=>[id,drawBrokenFestivalStall(canvas,sprites[id],id)]));
 sprites['collapsed-yagura']=await load(new URL('assets/collapsed-yagura-simple.png',propCatalog));
 names['collapsed-yagura']='무너진 야구라 무대';
 const objectName=p=>p.kind==='broken-stall'?`${names[p.type]} (부서진 노점)`:names[p.type];
 for(const prop of FestivalDebris130){
  const sprite=canvas(prop.footW*32,prop.footH*32);
  prop.draw(g(sprite));
  sprites[prop.id]=sprite;
  names[prop.id]=prop.name;
 }
 const texture=canvas(64,64);g(texture).drawImage(material,material.width/4,material.height/4,material.width/2,material.height/2,0,0,64,64);const tex=g(texture).getImageData(0,0,64,64).data,agedWall=createFestivalWall129({canvas,g,wall,rects,planes,tex});
 const festivalSurfaces=createFestivalSurfaces216({canvas,g,atlas:surfaceAtlas,wall,rects,planes});
 const drawWoodArch=createFestivalWoodArch({canvas,g,texture:festivalDoor,profile:DoorFit159});
 const classicSurfaces=document.getElementById('classic-surfaces');
 const ironDoors=document.getElementById('iron-doors');
 const floorCounts=new Map();source.floors.forEach(i=>floorCounts.set(i,(floorCounts.get(i)||0)+1));const floorIds=[...floorCounts].sort((a,b)=>b[1]-a[1]).map(a=>a[0]).filter(i=>source.palette[i].atlas==='floor').slice(0,4),floorTiles=[];
 for(const id of floorIds)for(let r=0;r<4;r++){const c=canvas(32,32),q=g(c),f=source.palette[id];q.translate(16,16);q.rotate(r*Math.PI/2);q.drawImage(floorAtlas,f.sx,f.sy,32,32,-16,-16,32,32);floorTiles.push(c);}
 const [stairsUp,stairsDown]=await Promise.all(['up','down'].map(kind=>load(`../city-random15/assets/crawl-stairs-${kind}-mirrored32.png`)));
 const stairTiles={up:stairsUp,down:stairsDown};
 const doorRef=source.doors.find(d=>d.linked.length===1),closed=source.palette[source.features[doorRef.y*source.width+doorRef.x]],opened=source.palette[doorRef.opened];
 const field=document.getElementById('map'),ctx=g(field),mini=document.getElementById('mini'),mg=g(mini),seedInput=document.getElementById('seed'),focus=document.getElementById('focus');
 const floorSelect=document.getElementById('floor');
 const zoomIn=document.getElementById('zoom-in'),zoomOut=document.getElementById('zoom-out');
 const maxZoom=3;
 let mapZoom=1;
 let map,state,base,decor,overview=false,view,timer=null;const dirs=[[-1,0],[1,0],[0,-1],[0,1],[-1,-1],[1,-1],[-1,1],[1,1]],around=[[1,0],[-1,0],[0,1],[0,-1]],idx=(x,y)=>y*map.w+x;
 const wallAt=(x,y)=>x>=0&&y>=0&&x<map.w&&y<map.h&&map.cells[idx(x,y)]===0;
 const inVerticalWall=({x,y})=>wallAt(x,y-1)&&wallAt(x,y+1);
 const stop=()=>{clearTimeout(timer);timer=null;};
 function opacity(x,y){const i=idx(x,y);if(map.cells[i]===0)return 2;const d=map.doors.find(d=>d.x===x&&d.y===y);if(d&&!state.opened.has(d.id))return 2;if(map.structures.some(p=>x>=p.x&&y>=p.y&&x<p.x+p.footW&&y<p.y+p.footH))return 2;return 0;}
 const visible=()=>CrawlVisibility.compute(map.w,map.h,state.player,opacity,7);
 function drawTile(q,t,x,y){q.drawImage(t.atlas==='feat'?featAtlas:floorAtlas,t.sx,t.sy,t.width,t.height,x+t.dx,y+t.dy,t.width,t.height);}
 function cache(){
  const classic=classicSurfaces.checked;
  const doorCells=new Set(map.doors.map(({x,y})=>idx(x,y)));
  const lowerWallCaps=new Set(map.doors.filter(inVerticalWall).map(({x,y})=>idx(x,y+1)));
  const neighbors=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
  function mask(x,y){
   let connections=0;
   const fittedWalls=!classic&&!ironDoors.checked?DoorFit159.wallCells(map,x,y):null;
   for(const [bit,[dx,dy]] of neighbors.entries()){
    const nx=x+dx,ny=y+dy;
    if(nx<0||ny<0||nx>=map.w||ny>=map.h)continue;
    // Keep the top coping of the real wall below a vertical doorway visible.
    const showCoping=bit===0&&lowerWallCaps.has(idx(x,y));
    const solid=fittedWalls?fittedWalls[idx(nx,ny)]===0
     :wallAt(nx,ny)||(!classic&&!showCoping&&doorCells.has(idx(nx,ny)));
    if(solid)connections|=1<<bit;
   }
   return connections;
  }
  base=canvas(map.w*32,map.h*32);
  const q=g(base);
  q.fillStyle='#171c19';
  q.fillRect(0,0,base.width,base.height);
  for(let y=0;y<map.h;y++)for(let x=0;x<map.w;x++){
   let tile;
   if(map.cells[idx(x,y)]===0){
    const connections=mask(x,y);
    let wearRandom;
    if(!classic&&map.floor===10&&(connections&16)===0){
     const random=StreetGen.random(`${map.seed}:festival-wall:${x},${y}`);
     if(random()<.39)wearRandom=random;
    }
    tile=classic ? agedWall(connections,0,x,y) : festivalSurfaces.wallTile(connections,x,y,wearRandom);
   }else{
    tile=classic ? floorTiles[RandomFloor.index(map.seed+':F8',0,x,y)] : festivalSurfaces.floorTile(x,y);
   }
   q.drawImage(tile,x*32,y*32);
  }
  for(const s of map.stairs)q.drawImage(stairTiles[s.kind],s.x*32,s.y*32);
  decor=canvas(base.width,base.height);const d=g(decor);for(const p of map.lanterns)d.drawImage(sprites['lantern-string'],p.x*32,p.y*32);
 }
 function draw(){if(!map)return;const fog=document.getElementById('fog').checked,show=document.getElementById('objects').checked,seen=visible();for(let i=0;i<seen.length;i++)if(seen[i])state.explored[i]=1;
  const t=overview?Math.floor(Math.min(field.width/map.w,field.height/map.h)):32*mapZoom,s=t/32;
  const cameraOffset=(size,tiles,player)=>overview
   ?Math.floor((size-tiles*t)/2)
   :-Math.max(0,Math.min(tiles*t-size,Math.round((player+.5)*t-size/2)));
  const ox=cameraOffset(field.width,map.w,state.player.x),oy=cameraOffset(field.height,map.h,state.player.y);
  view={t,s,ox,oy};ctx.fillStyle='#0c110f';ctx.fillRect(0,0,field.width,field.height);ctx.save();ctx.translate(ox,oy);ctx.scale(s,s);ctx.drawImage(base,0,0);
  if(show)ctx.drawImage(decor,0,0);
  for(const door of map.doors){
   const isOpen=state.opened.has(door.id);
   const x=door.x*32,y=door.y*32;
   if(ironDoors.checked) DoorFit159.draw(ctx,map,door,isOpen,null,base);
   else if(classicSurfaces.checked) drawTile(ctx,isOpen?opened:closed,x,y);
   else drawWoodArch(ctx,map,door,isOpen,base);
  }
  const things=show?[...map.structures,...map.loose].map(p=>({...p,bottom:(p.y+p.footH)*32})):[];things.push({kind:'player',x:state.player.x,y:state.player.y,bottom:(state.player.y+1)*32});things.sort((a,b)=>a.bottom-b.bottom||a.x-b.x);
  for(const p of things){if(p.kind==='player'){for(const k of ['body','boots','armour','helmet','sword'])ctx.drawImage(actor[k],p.x*32,p.y*32,32,32);continue;}const sprite=p.kind==='broken-stall'?brokenSprites[p.type]:sprites[p.type];ctx.save();ctx.fillStyle='rgba(5,5,4,.3)';ctx.beginPath();ctx.ellipse((p.x+p.footW/2)*32,p.bottom-3,p.footW*12,3,0,0,Math.PI*2);ctx.fill();ctx.restore();ctx.drawImage(sprite,p.x*32,p.bottom-sprite.height);}
  if(fog)for(let y=0;y<map.h;y++)for(let x=0;x<map.w;x++){const i=idx(x,y);if(!state.explored[i]){ctx.fillStyle='#070b09';ctx.fillRect(x*32,y*32,32,32);}else if(!seen[i]){ctx.fillStyle='rgba(0,0,0,.77)';ctx.fillRect(x*32,y*32,32,32);}}
  ctx.restore();mg.fillStyle='#101512';mg.fillRect(0,0,320,280);for(let y=0;y<map.h;y++)for(let x=0;x<map.w;x++){const i=idx(x,y);if(fog&&!state.explored[i])continue;mg.fillStyle=map.cells[i]===0?'#3d3830':'#85857a';mg.fillRect(x*4,y*4,4,4);}for(const p of map.structures)if(!fog||state.explored[idx(p.x,p.y)]){mg.fillStyle=p.kind==='stall'?'#cb7852':'#d8b06c';mg.fillRect(p.x*4,p.y*4,p.footW*4,p.footH*4);}for(const p of map.stairs)if(!fog||state.explored[idx(p.x,p.y)]){mg.fillStyle=p.kind==='up'?'#6cb7de':'#ebd17f';mg.fillRect(p.x*4,p.y*4,4,4);}mg.fillStyle='#ebf4e3';mg.fillRect(state.player.x*4,state.player.y*4,4,4);
  if(!overview){mg.strokeStyle='#f1c889';mg.strokeRect(-ox*4/t+.5,-oy*4/t+.5,field.width*4/t,field.height*4/t);}
  zoomIn.disabled=!overview&&mapZoom===maxZoom;
  zoomOut.disabled=overview;
  document.getElementById('overview').setAttribute('aria-pressed',String(overview));document.getElementById('status').textContent=`${map.floor}층 · ${state.turns}턴 · ${state.player.x},${state.player.y} · ${state.message}`;
 }
 function move(dx,dy,auto=false){if(!auto)stop();const x=state.player.x+dx,y=state.player.y+dy;if(x<0||y<0||x>=map.w||y>=map.h||!map.open[idx(x,y)]){state.message='벽·포장마차·소품이 있는 칸입니다.';draw();return false;}const d=map.doors.find(d=>d.x===x&&d.y===y);if(d&&!state.opened.has(d.id)){state.opened.add(d.id);state.message='문을 열었습니다.';}else{state.player={x,y};state.message='축제장 골목을 탐험하는 중입니다.';}state.turns++;draw();return true;}
 function route(target){if(!map.open[idx(target.x,target.y)])return[];const prev=new Int32Array(map.w*map.h).fill(-1),from=idx(state.player.x,state.player.y),end=idx(target.x,target.y),queue=[from];prev[from]=from;const fog=document.getElementById('fog').checked;for(let n=0;n<queue.length&&prev[end]<0;n++){const i=queue[n],x=i%map.w,y=(i/map.w)|0;for(const[dx,dy]of dirs){const xx=x+dx,yy=y+dy,j=idx(xx,yy);if(xx<0||yy<0||xx>=map.w||yy>=map.h||!map.open[j]||prev[j]>=0||(fog&&!state.explored[j]))continue;prev[j]=i;queue.push(j);}}if(prev[end]<0)return[];const out=[];for(let i=end;i!==from;i=prev[i])out.push({x:i%map.w,y:(i/map.w)|0});return out.reverse();}
 function follow(path){stop();const step=()=>{if(!path.length)return;const p=path[0];if(!move(Math.sign(p.x-state.player.x),Math.sign(p.y-state.player.y),true))return;if(state.player.x===p.x&&state.player.y===p.y)path.shift();timer=setTimeout(step,70);};step();}
 function approach(p){const points=[];for(let y=p.y-2;y<p.y+(p.footH||1)+3;y++)for(let x=p.x-2;x<p.x+(p.footW||4)+3;x++)if(x>=0&&y>=0&&x<map.w&&y<map.h&&map.open[idx(x,y)])points.push({x,y});points.sort((a,b)=>Math.hypot(a.x-p.x-(p.footW||4)/2,a.y-p.y-(p.footH||0)-1)-Math.hypot(b.x-p.x-(p.footW||4)/2,b.y-p.y-(p.footH||0)-1));return points[0]||map.start;}
 function focusAt(p,text){stop();state.player={...p};state.message=text;overview=false;draw();}
 function generate(){
  stop();
  const floor=Number(floorSelect.value),seed=seedInput.value.trim()||'20261109-8';
  let next;
  try{next=FestivalGen130.generate(seed,floor);}catch(error){
   if(!map)throw error;
   floorSelect.value=String(map.floor);seedInput.value=map.seed;
   document.getElementById('status').textContent='맵을 생성하지 못했습니다. 다른 시드로 다시 시도하세요.';
   return;
  }
  window.festivalReady=false;
  seedInput.value=seed;map=next;
  state={player:{...map.walkStart},opened:new Set(),explored:new Uint8Array(map.w*map.h),turns:0,message:'축제 광장 앞에서 시작'};
  cache();
  const aftermath=floor===10;
  document.getElementById('floor-title').textContent=`${floor}층 — ${aftermath?'축제의 잔해':'낡은 축제장'}`;
  document.getElementById('mini-title').textContent=`${floor}층 전체 지도`;
  field.setAttribute('aria-label',`랜덤 생성한 잔향도시 ${floor}층 지도`);
  const stalls=aftermath?map.loose.filter(p=>p.kind==='broken-stall'):map.structures.filter(p=>p.kind==='stall');
  const propCount=aftermath?map.loose.length-stalls.length:map.loose.length;
  const stats=[['80×70',null],[aftermath?'부서진 포장마차':'포장마차',stalls.length],[objectName(map.stage),1],[aftermath?'기타 축제 잔해':'바닥 소품',propCount],['초롱줄',map.lanterns.length],['문',map.doors.length],['위/아래 계단','3/3']];document.getElementById('stats').replaceChildren(...stats.map(([k,v])=>{const e=document.createElement('span');e.textContent=v===null?k:k+' '+v;return e;}));document.getElementById('audit').textContent=`연결된 이동칸 ${map.floorTiles} · 첫 위→아래 계단 ${map.stairDistance}칸 · 소품 추가 우회 최대 ${map.placementAudit.maxAnchorDetour}칸`;
  focus.replaceChildren();const options=[...map.structures,...map.loose,...map.lanterns];options.forEach((p,i)=>focus.add(new Option(objectName(p)+' · '+p.x+','+p.y,i)));map.focusOptions=options;
  const query=new URLSearchParams({seed});
  if(floor!==8)query.set('floor',String(floor));
  history.replaceState(null,'','?'+query.toString());
  mapZoom=1;overview=true;draw();window.festivalReady=true;
 }
 zoomIn.onclick=()=>{
  mapZoom=overview?1:Math.min(mapZoom+1,maxZoom);
  overview=false;
  draw();
 };
 zoomOut.onclick=()=>{
  if(mapZoom===1)overview=true;
  else mapZoom--;
  draw();
 };
 floorSelect.onchange=generate;
 document.getElementById('generate').onclick=generate;document.getElementById('random').onclick=()=>{seedInput.value=`F${floorSelect.value}-${Math.floor(Math.random()*1e9)}`;generate();};document.getElementById('overview').onclick=()=>{overview=!overview;draw();};document.getElementById('plaza').onclick=()=>focusAt(map.walkStart,'축제 광장 검토 위치');document.getElementById('stairs').onclick=()=>focusAt(map.start,'위 계단에서 탐험 시작');document.getElementById('visit').onclick=()=>{const p=map.focusOptions[Number(focus.value)];focusAt(approach(p),objectName(p)+' 검토 위치');};document.getElementById('fog').onchange=draw;document.getElementById('objects').onchange=draw;document.getElementById('stop').onclick=stop;document.getElementById('close').onclick=()=>{const d=map.doors.find(d=>state.opened.has(d.id)&&Math.max(Math.abs(d.x-state.player.x),Math.abs(d.y-state.player.y))===1);if(d){state.opened.delete(d.id);state.turns++;state.message='인접 문을 닫았습니다.';draw();}};
 for(const b of document.querySelectorAll('[data-step]'))b.onclick=()=>move(...b.dataset.step.split(',').map(Number));
 classicSurfaces.onchange=()=>{cache();draw();};
 ironDoors.onchange=()=>{cache();draw();};
 const keys={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1],a:[-1,0],d:[1,0],w:[0,-1],s:[0,1],q:[-1,-1],e:[1,-1],z:[-1,1],c:[1,1]};addEventListener('keydown',e=>{if(e.key==='Escape')stop();if(keys[e.key]&&!['INPUT','SELECT'].includes(document.activeElement.tagName)){e.preventDefault();move(...keys[e.key]);}});
 field.onclick=e=>{field.focus({preventScroll:true});const r=field.getBoundingClientRect(),x=Math.floor(((e.clientX-r.left)*field.width/r.width-view.ox)/view.t),y=Math.floor(((e.clientY-r.top)*field.height/r.height-view.oy)/view.t);if(x>=0&&y>=0&&x<map.w&&y<map.h){const path=route({x,y});if(path.length)follow(path);}};
 function fit(){const n=Math.max(1,Math.floor(field.parentElement.clientWidth/field.width));field.style.width=field.width*n+'px';field.style.height=field.height*n+'px';field.style.marginInline='auto';}addEventListener('resize',fit);fit();
 window.festival130={getMap:()=>map,getState:()=>state,generate,move,route,focusAt,approach,draw,stop,sprites,opacity,getOverview:()=>overview,setOverview:v=>{overview=v;draw();}};
 const query=new URLSearchParams(location.search);
 if(query.get('seed'))seedInput.value=query.get('seed');
 if(['8','9','10'].includes(query.get('floor')))floorSelect.value=query.get('floor');
 generate();
})().catch(e=>{console.error(e);document.getElementById('status').textContent='축제장 로드 오류: '+e.message;});
