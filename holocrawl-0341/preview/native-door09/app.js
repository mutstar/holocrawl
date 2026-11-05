'use strict';
const data=NativeCrawlMaps,maps=data.maps,$=id=>document.getElementById(id),canvas=$('field'),ctx=canvas.getContext('2d');
const assets='../city-layout07/assets/',images={},floorPatches=[[270,150,32,32],[285,153,32,32],[160,300,32,32],[260,300,32,32]];
const labels={layout_basic:'방과 복도',layout_gridville:'불규칙한 격자',layout_roguey:'구획을 잇는 방',layout_small_grid:'작은 격자'};
let selected=0,overview=false,legacy=false,focusDoor=0,center={x:40,y:35},tiles=[],transform={},opened=new Set();
const feature=(m,x,y)=>x<0||y<0||x>=m.w||y>=m.h?'rock_wall':m.palette[m.rows[y][x]];
const isWall=f=>f.includes('wall')||f==='granite_statue',isWater=f=>f.includes('water'),isDoor=f=>f.includes('door');
const isUp=f=>f.startsWith('stone_stairs_up'),isDown=f=>f.startsWith('stone_stairs_down');
const doorKey=(x,y)=>selected+':'+x+','+y;
function doors(m){const result=[];for(let y=3;y<m.h-3;y++)for(let x=3;x<m.w-3;x++)if(isDoor(feature(m,x,y))){let score=0;if(isWall(feature(m,x-1,y))&&isWall(feature(m,x+1,y)))score+=8;if(!isWall(feature(m,x,y-1))&&!isWall(feature(m,x,y+1)))score+=4;result.push({x,y,score});}return result.sort((a,b)=>b.score-a.score||a.y-b.y||a.x-b.x);}
function isOpened(x,y){return opened.has(doorKey(x,y))||feature(maps[selected],x,y)==='open_door';}
function color(f){return isUp(f)?'#92d9ba':isDown(f)?'#ebce72':isWater(f)?f==='deep_water'?'#284d6a':'#45869a':isDoor(f)?'#c09b71':isWall(f)?'#172022':'#8b998e';}
function oldDoor(c,x,y,t){c.fillStyle='#2b221b';c.fillRect(x+t*.12,y+t*.08,t*.76,t*.84);c.fillStyle='#8d7759';c.fillRect(x+t*.21,y+t*.12,t*.58,t*.69);c.fillStyle='#b7a587';c.fillRect(x+t*.22,y+t*.16,t*.52,t*.06);c.fillStyle='#322a23';for(let i=0;i<3;i++)c.fillRect(x+t*(.27+i*.17),y+t*.25,t*.04,t*.46);c.fillStyle='#ddcba2';c.fillRect(x+t*.65,y+t*.48,t*.07,t*.07);}
function texture(c,rect,x,y,w,h){c.drawImage(images.reference,...rect,x,y,w,h);}
function tile(c,m,gx,gy,px,py,t,style='new',forceState=null){
 const f=feature(m,gx,gy);
 if(isWall(f)){
  texture(c,[112,54,16,16],px,py,t,t);c.fillStyle='rgba(11,13,15,.60)';c.fillRect(px,py,t,t);
  if(!isWall(feature(m,gx,gy+1))){c.filter='brightness(1.35)';texture(c,[130,62,24,25],px,py+t*.08,t,t*.92);c.filter='none';c.fillStyle='#625d54';c.fillRect(px,py+t*.27,t,Math.max(1,t/32));c.fillStyle='#171714';c.fillRect(px,py+t*.94,t,t*.06);}
  if(f.includes('clear_')||f==='crystal_wall'){c.fillStyle='rgba(118,173,197,.38)';c.fillRect(px,py,t,t);}
  if(f==='granite_statue'){c.fillStyle='#9a9e97';c.fillRect(px+t*.3,py+t*.12,t*.4,t*.73);}return;
 }
 c.drawImage(tiles[RandomFloor.index(m.seed,0,gx,gy)],px,py,t,t);
 if(isDoor(f)){if(style==='old')oldDoor(c,px,py,t);else c.drawImage((forceState===null?isOpened(gx,gy):forceState)?images.open:images.closed,px,py,t,t);return;}
 if(isUp(f)||isDown(f)){c.drawImage(isUp(f)?images.up:images.down,px,py,t,t);return;}
 if(isWater(f)){c.fillStyle=f==='deep_water'?'rgba(13,54,87,.92)':'rgba(46,108,128,.85)';c.fillRect(px,py,t,t);c.fillStyle='#6f9da5';c.fillRect(px+t*.2,py+t*.4,t*.33,Math.max(1,t/32));return;}
 if(f==='floor')return;
 c.font=`bold ${Math.max(6,t*.64)}px monospace`;c.textAlign='center';c.textBaseline='middle';c.fillStyle=f.startsWith('enter_')?'#d0a7dc':'#c9ad85';c.fillText(f.startsWith('enter_')?'Ω':f==='fountain_blue'?'○':f.startsWith('escape_hatch')?f.endsWith('up')?'↑':'↓':f.startsWith('trap')?'^':f==='shaft'?'○':'·',px+t*.5,py+t*.52);
}
function comparisons(){const m=maps[selected],door=doors(m)[focusDoor];if(!door)return;for(const [id,style,state] of [['oldDoor','old',false],['closedDoor','new',false],['openDoor','new',true]]){const c=$(id).getContext('2d');c.imageSmoothingEnabled=false;c.fillStyle='#080b0b';c.fillRect(0,0,320,320);for(let dy=-2;dy<=2;dy++)for(let dx=-2;dx<=2;dx++)tile(c,m,door.x+dx,door.y+dy,(dx+2)*64,(dy+2)*64,64,style,door.x+dx===door.x&&door.y+dy===door.y?state:null);}}
function draw(){
 if(!images.closed||!images.open)return;const m=maps[selected],t=overview?8:32,cols=canvas.width/t,rows=canvas.height/t,cx=overview?0:Math.max(0,Math.min(m.w-cols,Math.floor(center.x-cols/2))),cy=overview?0:Math.max(0,Math.min(m.h-rows,Math.floor(center.y-rows/2))),ox=overview?(canvas.width-m.w*t)/2:0,oy=overview?(canvas.height-m.h*t)/2:0;
 transform={t,cx,cy,ox,oy};ctx.imageSmoothingEnabled=false;ctx.fillStyle='#080b0b';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.save();ctx.translate(ox-cx*t,oy-cy*t);
 for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++)tile(ctx,m,x,y,x*t,y*t,t,legacy?'old':'new');ctx.restore();
 const list=doors(m),door=list[focusDoor];$('mapTitle').textContent=m.place+' · '+(labels[m.layout]||m.layout.replace('layout_',''));$('mapInfo').textContent='지도 번호 '+m.seed+' · 원본 지형 그대로';$('overview').textContent=overview?'거리 크기로 보기':'전체 지도 보기';$('legacy').textContent=legacy?'새 철제 문 보기':'이전 임시 문 비교';$('toggleDoor').textContent=door&&isOpened(door.x,door.y)?'이 문 닫기':'이 문 열기';$('focusInfo').textContent='문 '+(focusDoor+1)+' / '+list.length+' · '+(door?door.x+', '+door.y:'')+' · '+(legacy?'이전 임시 문':'새 철제 방화문');comparisons();
}
function focus(index){const list=doors(maps[selected]);focusDoor=((index%list.length)+list.length)%list.length;center={...list[focusDoor]};overview=false;draw();}
function select(index){selected=index;focusDoor=0;legacy=false;$('mapSelect').value=String(index);focus(0);}
function toggle(x,y){const k=doorKey(x,y);if(opened.has(k))opened.delete(k);else opened.add(k);legacy=false;draw();}
$('mapSelect').onchange=e=>select(Number(e.target.value));$('nextDoor').onclick=()=>focus(focusDoor+1);$('toggleDoor').onclick=()=>{const d=doors(maps[selected])[focusDoor];toggle(d.x,d.y);};$('legacy').onclick=()=>{legacy=!legacy;draw();};$('overview').onclick=()=>{overview=!overview;draw();};
canvas.onclick=e=>{const r=canvas.getBoundingClientRect(),{t,cx,cy,ox,oy}=transform,x=Math.floor(((e.clientX-r.left)*canvas.width/r.width-ox)/t)+cx,y=Math.floor(((e.clientY-r.top)*canvas.height/r.height-oy)/t)+cy,m=maps[selected];if(x<0||y<0||x>=m.w||y>=m.h)return;if(overview){center={x,y};overview=false;draw();}else if(isDoor(feature(m,x,y))){focusDoor=doors(m).findIndex(d=>d.x===x&&d.y===y);toggle(x,y);}else{center={x,y};draw();}canvas.focus();};
window.addEventListener('keydown',e=>{if(['INPUT','SELECT','TEXTAREA','BUTTON'].includes(e.target.tagName))return;const dirs={ArrowLeft:[-2,0],ArrowRight:[2,0],ArrowUp:[0,-2],ArrowDown:[0,2],a:[-2,0],d:[2,0],w:[0,-2],s:[0,2]},v=dirs[e.key];if(!v)return;e.preventDefault();center={x:Math.max(0,Math.min(maps[selected].w-1,center.x+v[0])),y:Math.max(0,Math.min(maps[selected].h-1,center.y+v[1]))};draw();});
window.doorPreview={select,focus,setOverview:value=>{overview=value;draw();},toggleFocused:()=>{const d=doors(maps[selected])[focusDoor];toggle(d.x,d.y);},getState:()=>({selected,overview,legacy,center:{...center},focusDoor,doors:doors(maps[selected]),opened:Array.from(opened),map:maps[selected]}),draw};
(async()=>{const sources={reference:assets+'scene-reference.png',floor:assets+'cement-reference.png',up:assets+'stairs-up12-32.png',down:assets+'stairs-down06-32.png',closed:'assets/fire-door-closed32.png',open:'assets/fire-door-open32.png'};await Promise.all(Object.entries(sources).map(async([key,src])=>{images[key]=await new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>reject(Error('Image unavailable: '+src));im.src=src;});}));for(let i=0;i<16;i++){const patch=floorPatches[Math.floor(i/4)],c=document.createElement('canvas');c.width=c.height=32;const cc=c.getContext('2d');cc.imageSmoothingEnabled=false;cc.translate(16,16);cc.rotate((i%4)*Math.PI/2);cc.drawImage(images.floor,...patch,-16,-16,32,32);tiles.push(c);}maps.forEach((m,i)=>{const o=document.createElement('option');o.value=i;o.textContent=(i+1)+' · '+m.place;$('mapSelect').append(o);});select(0);window.doorPreviewReady=true;})();
