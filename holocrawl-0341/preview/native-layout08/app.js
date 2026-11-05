'use strict';
const data=NativeCrawlMaps,maps=data.maps,$=id=>document.getElementById(id),canvas=$('field'),ctx=canvas.getContext('2d');
const assets='../city-layout07/assets/',images={},floorPatches=[[270,150,32,32],[285,153,32,32],[160,300,32,32],[260,300,32,32]];
let selected=0,overview=false,skin='city',center={x:40,y:35},tiles=[],transform={};
const labels={layout_basic:'방과 복도',layout_gridville:'불규칙한 격자',layout_roguey:'구획을 잇는 방',layout_small_grid:'작은 격자'};
const feature=(m,x,y)=>x<0||y<0||x>=m.w||y>=m.h?'rock_wall':m.palette[m.rows[y][x]];
const isWall=f=>f.includes('wall')||f==='granite_statue',isWater=f=>f.includes('water'),isDoor=f=>f.includes('door');
const isUp=f=>f.startsWith('stone_stairs_up'),isDown=f=>f.startsWith('stone_stairs_down');
function color(f){return isUp(f)?'#92d9ba':isDown(f)?'#ebce72':isWater(f)?f==='deep_water'?'#284d6a':'#45869a':isDoor(f)?'#c09b71':isWall(f)?f.includes('clear_')?'#526d76':f==='crystal_wall'?'#617782':'#172022':f.startsWith('enter_')?'#af91bc':'#8b998e';}
function drawPlan(context,m,scale){context.imageSmoothingEnabled=false;context.fillStyle='#172022';context.fillRect(0,0,m.w*scale,m.h*scale);for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++){context.fillStyle=color(feature(m,x,y));context.fillRect(x*scale,y*scale,scale,scale);}}
function drawGallery(){
 $('gallery').replaceChildren();
 maps.forEach((m,i)=>{const card=document.createElement('button'),title=document.createElement('strong'),small=document.createElement('small'),c=document.createElement('canvas');card.className='map-card'+(i===selected?' selected':'');card.dataset.index=i;title.textContent='예시 '+(i+1)+' · '+m.place+' · '+(labels[m.layout]||m.layout.replace('layout_',''));small.textContent='지도 번호 '+m.seed+' / '+m.layout;c.width=m.w*4;c.height=m.h*4;drawPlan(c.getContext('2d'),m,4);card.append(title,c,small);card.onclick=()=>select(i);$('gallery').append(card);});
}
function stairFocus(m){for(let y=1;y<m.h-1;y++)for(let x=1;x<m.w-1;x++)if(isUp(feature(m,x,y)))return{x,y};return{x:40,y:35};}
function roomFocus(m){let best=null;for(let y=8;y<m.h-8;y++)for(let x=12;x<m.w-12;x++){if(feature(m,x,y)!=='floor')continue;let score=0;for(let dy=-5;dy<=5;dy++)for(let dx=-8;dx<=8;dx++){const f=feature(m,x+dx,y+dy);if(!isWall(f))score++;}if(!best||score>best.score)best={x,y,score};}return best||stairFocus(m);}
function select(i){selected=i;center=roomFocus(maps[i]);for(const c of document.querySelectorAll('.map-card'))c.classList.toggle('selected',Number(c.dataset.index)===i);draw();}
function texture(rect,x,y,w,h,im=images.reference){ctx.drawImage(im,...rect,x,y,w,h);}
function symbols(f,x,y,t){
 if(isUp(f)||isDown(f)){ctx.drawImage(isUp(f)?images.up:images.down,x,y,t,t);return;}
 if(isDoor(f)){ctx.fillStyle='#2b221b';ctx.fillRect(x+t*.12,y+t*.08,t*.76,t*.84);ctx.fillStyle='#8d7759';ctx.fillRect(x+t*.21,y+t*.12,t*.58,t*.69);ctx.fillStyle='#b7a587';ctx.fillRect(x+t*.22,y+t*.16,t*.52,t*.06);ctx.fillStyle='#322a23';for(let i=0;i<3;i++)ctx.fillRect(x+t*(.27+i*.17),y+t*.25,t*.04,t*.46);ctx.fillStyle='#ddcba2';ctx.fillRect(x+t*.65,y+t*.48,t*.07,t*.07);return;}
 if(isWater(f)){ctx.fillStyle=f==='deep_water'?'rgba(13,54,87,.92)':'rgba(46,108,128,.85)';ctx.fillRect(x,y,t,t);ctx.fillStyle='#6f9da5';ctx.fillRect(x+t*.2,y+t*.4,t*.33,Math.max(1,t/32));ctx.fillRect(x+t*.5,y+t*.73,t*.27,Math.max(1,t/32));return;}
 if(f==='floor')return;
 ctx.font=`bold ${Math.max(6,t*.64)}px monospace`;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillStyle=f.startsWith('enter_')?'#d0a7dc':f==='fountain_blue'?'#76c4d0':'#c9ad85';
 const mark=f.startsWith('enter_')?'Ω':f==='fountain_blue'?'○':f.startsWith('escape_hatch')?f.endsWith('up')?'↑':'↓':f.startsWith('trap')?'^':f==='shaft'?'○':'·';ctx.fillText(mark,x+t*.5,y+t*.52);
}
function draw(){
 if(!images.reference)return;const m=maps[selected],t=overview?8:32,cols=canvas.width/t,rows=canvas.height/t,cx=overview?0:Math.max(0,Math.min(m.w-cols,Math.floor(center.x-cols/2))),cy=overview?0:Math.max(0,Math.min(m.h-rows,Math.floor(center.y-rows/2))),ox=overview?(canvas.width-m.w*t)/2:0,oy=overview?(canvas.height-m.h*t)/2:0;
 transform={t,cx,cy,ox,oy};ctx.imageSmoothingEnabled=false;ctx.fillStyle='#080b0b';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.save();ctx.translate(ox-cx*t,oy-cy*t);
 for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++){
  const f=feature(m,x,y),px=x*t,py=y*t;
  if(skin==='plan'){ctx.fillStyle=color(f);ctx.fillRect(px,py,t,t);continue;}
  if(isWall(f)){
   texture([112,54,16,16],px,py,t,t);ctx.fillStyle='rgba(11,13,15,.60)';ctx.fillRect(px,py,t,t);
   if(!isWall(feature(m,x,y+1))){ctx.filter='brightness(1.35)';texture([130,62,24,25],px,py+t*.08,t,t*.92);ctx.filter='none';ctx.fillStyle='#625d54';ctx.fillRect(px,py+t*.27,t,Math.max(1,t/32));ctx.fillStyle='#171714';ctx.fillRect(px,py+t*.94,t,t*.06);}
   if(f.includes('clear_')||f==='crystal_wall'){ctx.fillStyle='rgba(118,173,197,.38)';ctx.fillRect(px,py,t,t);}
   if(f==='granite_statue'){ctx.fillStyle='#9a9e97';ctx.fillRect(px+t*.3,py+t*.12,t*.4,t*.73);}
  }else{ctx.drawImage(tiles[RandomFloor.index(m.seed,0,x,y)],px,py,t,t);symbols(f,px,py,t);}
 }
 ctx.restore();$('mapTitle').textContent='예시 '+(selected+1)+' · '+m.place+' · '+(labels[m.layout]||m.layout.replace('layout_',''));$('mapInfo').textContent='지도 번호 '+m.seed+' · 원본80×70칸 · '+m.layout;$('overview').textContent=overview?'거리 크기로 보기':'전체 지도 보기';$('skin').textContent=skin==='city'?'지형 구조로 보기':'도시 타일로 보기';$('focusInfo').textContent='화면 중심 '+Math.round(center.x)+', '+Math.round(center.y)+' · '+(skin==='city'?'도시 타일':'지형 구조');
}
$('overview').onclick=()=>{overview=!overview;draw();};$('skin').onclick=()=>{skin=skin==='city'?'plan':'city';draw();};$('stairs').onclick=()=>{center=stairFocus(maps[selected]);overview=false;draw();};
canvas.onclick=e=>{const r=canvas.getBoundingClientRect(),{t,cx,cy,ox,oy}=transform,x=Math.floor(((e.clientX-r.left)*canvas.width/r.width-ox)/t)+cx,y=Math.floor(((e.clientY-r.top)*canvas.height/r.height-oy)/t)+cy;if(x<0||y<0||x>=maps[selected].w||y>=maps[selected].h)return;center={x,y};overview=false;draw();canvas.focus();};
window.addEventListener('keydown',e=>{if(['INPUT','SELECT','TEXTAREA','BUTTON'].includes(e.target.tagName))return;const dirs={ArrowLeft:[-2,0],ArrowRight:[2,0],ArrowUp:[0,-2],ArrowDown:[0,2],a:[-2,0],d:[2,0],w:[0,-2],s:[0,2]},v=dirs[e.key];if(!v)return;e.preventDefault();center={x:Math.max(0,Math.min(maps[selected].w-1,center.x+v[0])),y:Math.max(0,Math.min(maps[selected].h-1,center.y+v[1]))};draw();});
window.nativePreview={select,setOverview:value=>{overview=value;draw();},setSkin:value=>{skin=value;draw();},getState:()=>({selected,overview,skin,center:{...center},map:maps[selected]}),draw};
(async()=>{await Promise.all(Object.entries({reference:'scene-reference.png',floor:'cement-reference.png',up:'stairs-up12-32.png',down:'stairs-down06-32.png'}).map(async([key,src])=>{images[key]=await new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=reject;im.src=assets+src;});}));for(let i=0;i<16;i++){const patch=floorPatches[Math.floor(i/4)],c=document.createElement('canvas');c.width=c.height=32;const cc=c.getContext('2d');cc.imageSmoothingEnabled=false;cc.translate(16,16);cc.rotate((i%4)*Math.PI/2);cc.drawImage(images.floor,...patch,-16,-16,32,32);tiles.push(c);}drawGallery();select(0);window.nativePreviewReady=true;})();
