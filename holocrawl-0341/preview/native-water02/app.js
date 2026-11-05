'use strict';
const data=NativeCrawlMaps,maps=data.maps,$=id=>document.getElementById(id),canvas=$('field'),ctx=canvas.getContext('2d');
const assets='../city-layout07/assets/',images={},floorPatches=[[270,150,32,32],[285,153,32,32],[160,300,32,32],[260,300,32,32]];
const labels={layout_basic:'방과 복도',layout_gridville:'불규칙한 격자',layout_roguey:'구획을 잇는 방',layout_small_grid:'작은 격자'};
let selected=0,overview=false,doorMode='fit',wallOld=false,focusDoor=0,center={x:40,y:35},tiles=[],transform={},opened=new Set();
const wallRuns=new Map();
function drawWater(c,m,x,y,px,py,t){const f=feature(m,x,y),deep=f==='deep_water',s=t/32,h=hash(m.seed,x,y);c.save();c.globalAlpha=deep?1:.90;c.drawImage(deep?images.deep:images.shallow,(h%4)*32,(Math.floor(h/4)%4)*32,32,32,px,py,t,t);c.restore();const dirs=[[0,-1,0,0,32,2],[0,1,0,30,32,2],[-1,0,0,0,2,32],[1,0,30,0,2,32]];for(const[dx,dy,rx,ry,rw,rh]of dirs){const n=feature(m,x+dx,y+dy);if(!isWater(n)){c.fillStyle='rgba(19,40,43,.68)';c.fillRect(px+rx*s,py+ry*s,rw*s,rh*s);c.fillStyle='rgba(135,162,153,.50)';if(dx)c.fillRect(px+(dx<0?2:29)*s,py+(5+h%9)*s,s,10*s);else c.fillRect(px+(4+h%11)*s,py+(dy<0?2:29)*s,10*s,s);}else if(deep&&n==='shallow_water'){c.fillStyle='rgba(85,143,145,.65)';c.fillRect(px+rx*s,py+ry*s,rw*s,rh*s);}}for(const[dx,dy]of[[-1,-1],[1,-1],[-1,1],[1,1]])if(isWater(feature(m,x+dx,y))&&isWater(feature(m,x,y+dy))&&!isWater(feature(m,x+dx,y+dy))){c.fillStyle='rgba(23,48,48,.65)';c.fillRect(px+(dx<0?0:29)*s,py+(dy<0?0:29)*s,3*s,3*s);}}
function waterDemos(){for(const deep of[false,true]){const m={seed:'WATER-DEMO01',w:7,h:7,palette:['floor','shallow_water','deep_water'],rows:Array.from({length:7},()=>Array(7).fill(0))};for(let y=1;y<=5;y++)for(let x=1;x<=5;x++)if(!(x===1&&y===1||x===5&&y===5))m.rows[y][x]=deep&&x>=2&&x<=4&&y>=2&&y<=4?2:1;const c=$(deep?'deepDemo':'shallowDemo').getContext('2d');c.imageSmoothingEnabled=false;for(let y=0;y<7;y++)for(let x=0;x<7;x++)tile(c,m,x,y,x*64,y*64,64);}}
function waterFocus(){const m=maps[selected],points=[];for(let y=1;y<m.h-1;y++)for(let x=1;x<m.w-1;x++)if(isWater(feature(m,x,y)))points.push({x,y});if(!points.length){$('focusInfo').textContent='이 지도에는 물이 없습니다. 지도2 또는6에서 확인하세요.';return;}center=points[Math.floor(points.length/2)];overview=false;draw();$('focusInfo').textContent='원본 지도 속 물 · '+points.length+'칸 · 지형 위치 그대로';}
const feature=(m,x,y)=>x<0||y<0||x>=m.w||y>=m.h?'rock_wall':m.palette[m.rows[y][x]];
const isWall=f=>f.includes('wall')||f==='granite_statue',isWater=f=>f.includes('water'),isDoor=f=>f.includes('door');
const isUp=f=>f.startsWith('stone_stairs_up'),isDown=f=>f.startsWith('stone_stairs_down');
const doorKey=(x,y)=>selected+':'+x+','+y;
function doorAxis(m,x,y){const joins=(xx,yy)=>{const f=feature(m,xx,yy);return f.includes('wall')||isDoor(f);},vertical=Number(joins(x,y-1))+Number(joins(x,y+1)),horizontal=Number(joins(x-1,y))+Number(joins(x+1,y));return vertical>horizontal?'vertical':'horizontal';}
function doors(m){const result=[];for(let y=3;y<m.h-3;y++)for(let x=3;x<m.w-3;x++)if(isDoor(feature(m,x,y))){let score=0;if(isWall(feature(m,x-1,y))&&isWall(feature(m,x+1,y)))score+=8;if(!isWall(feature(m,x,y-1))&&!isWall(feature(m,x,y+1)))score+=4;result.push({x,y,score});}return result.sort((a,b)=>b.score-a.score||a.y-b.y||a.x-b.x);}
function isOpened(x,y){return opened.has(doorKey(x,y))||feature(maps[selected],x,y)==='open_door';}
function color(f){return isUp(f)?'#92d9ba':isDown(f)?'#ebce72':isWater(f)?f==='deep_water'?'#284d6a':'#45869a':isDoor(f)?'#c09b71':isWall(f)?'#172022':'#8b998e';}
function oldDoor(c,x,y,t){c.fillStyle='#2b221b';c.fillRect(x+t*.12,y+t*.08,t*.76,t*.84);c.fillStyle='#8d7759';c.fillRect(x+t*.21,y+t*.12,t*.58,t*.69);c.fillStyle='#b7a587';c.fillRect(x+t*.22,y+t*.16,t*.52,t*.06);c.fillStyle='#322a23';for(let i=0;i<3;i++)c.fillRect(x+t*(.27+i*.17),y+t*.25,t*.04,t*.46);c.fillStyle='#ddcba2';c.fillRect(x+t*.65,y+t*.48,t*.07,t*.07);}
function texture(c,rect,x,y,w,h){c.drawImage(images.reference,...rect,x,y,w,h);}
function hash(seed,x,y){let n=Math.imul(x+19,374761393)^Math.imul(y+73,668265263);for(const v of seed)n=Math.imul(n^v.charCodeAt(0),1274126177);return(n^(n>>>13))>>>0;}
function faceAt(m,x,y){const f=feature(m,x,y);return (isWall(f)||isDoor(f))&&!isWall(feature(m,x,y+1));}
function wallRun(m,x,y){let start=x;while(start>0&&faceAt(m,start-1,y))start--;const key=m.seed+':'+y+':'+start;if(wallRuns.has(key))return wallRuns.get(key);let end=start;while(end<m.w&&faceAt(m,end,y))end++;const h=hash(m.seed,start,y),joints=new Set();let n=2+h%3;while(n<end-start){joints.add(n);n+=3+hash(m.seed,start+n,y)%4;}const result={start,end,phase:h%8,joints,decor:end-start>=7?start+2+h%(end-start-4):-1};wallRuns.set(key,result);return result;}
function wallFace(c,m,gx,gy,px,py,t,old=false){
 const s=t/32;
 if(old){c.filter='brightness(1.35)';texture(c,[130,62,24,25],px,py+t*.08,t,t*.92);c.filter='none';c.fillStyle='#625d54';c.fillRect(px,py+t*.27,t,Math.max(1,s));c.fillStyle='#171714';c.fillRect(px,py+t*.94,t,t*.06);return;}
 const run=wallRun(m,gx,gy),offset=gx-run.start,sx=((offset+run.phase)%8)*32;
 c.drawImage(images.wall,sx,0,32,32,px,py+2*s,t,30*s);c.fillStyle='rgba(19,21,19,.40)';c.fillRect(px,py,t,3*s);c.fillStyle='#222522';c.fillRect(px,py+30*s,t,2*s);
 if(run.joints.has(offset)){c.fillStyle='rgba(30,32,29,.40)';c.fillRect(px+1*s,py+3*s,1*s,27*s);c.fillStyle='rgba(155,153,139,.16)';c.fillRect(px+2*s,py+3*s,1*s,27*s);}
 if(gx===run.decor){if(hash(m.seed,gx,gy)%2){texture(c,[289,34,37,19],px+2*s,py+9*s,27*s,14*s);}else{c.strokeStyle='#292e2a';c.lineWidth=3*s;c.beginPath();c.moveTo(px+7*s,py+3*s);c.lineTo(px+18*s,py+3*s);c.lineTo(px+18*s,py+28*s);c.stroke();c.strokeStyle='#858a80';c.lineWidth=1*s;c.stroke();}}
}
function wallSides(c,m,gx,gy,px,py,t){const s=t/32,sx=(hash(m.seed,gx,gy)%8)*32;for(const [dx,x,shade] of [[-1,px,.15],[1,px+29*s,.38]])if(!isWall(feature(m,gx+dx,gy))){c.drawImage(images.wall,sx,0,32,32,x,py,3*s,t);c.fillStyle=`rgba(10,15,13,${shade})`;c.fillRect(x,py,3*s,t);c.fillStyle='rgba(156,157,140,.2)';c.fillRect(x,py,1*s,t);}}
function tile(c,m,gx,gy,px,py,t,style='fit',forceState=null,oldWall=wallOld){
 const f=feature(m,gx,gy);
 if(isWall(f)){
  if(oldWall){texture(c,[112,54,16,16],px,py,t,t);c.fillStyle='rgba(11,13,15,.60)';c.fillRect(px,py,t,t);}else{const sx=(hash(m.seed,gx,gy)%8)*32;c.fillStyle='#232521';c.fillRect(px,py,t,t);c.globalAlpha=.14;c.drawImage(images.wall,sx,0,32,32,px,py,t,t);c.globalAlpha=1;}
  if(style==='fit'&&!oldWall)wallSides(c,m,gx,gy,px,py,t);
  const below=feature(m,gx,gy+1),verticalDoorBelow=style==='fit'&&isDoor(below)&&doorAxis(m,gx,gy+1)==='vertical';
  if(!isWall(below)&&!verticalDoorBelow)wallFace(c,m,gx,gy,px,py,t,oldWall);
  if(f.includes('clear_')||f==='crystal_wall'){c.fillStyle='rgba(118,173,197,.38)';c.fillRect(px,py,t,t);}
  if(f==='granite_statue'){c.fillStyle='#9a9e97';c.fillRect(px+t*.3,py+t*.12,t*.4,t*.73);}return;
 }
 c.drawImage(tiles[RandomFloor.index(m.seed,0,gx,gy)],px,py,t,t);
 if(isDoor(f)){
  const open=forceState===null?isOpened(gx,gy):forceState;
  const s=t/32;
  if(doorAxis(m,gx,gy)==='vertical'){
   c.fillStyle='#232521';c.fillRect(px,py,4*s,t);c.fillRect(px+28*s,py,4*s,t);c.fillRect(px,py,t,2*s);c.fillRect(px,py+30*s,t,2*s);wallSides(c,m,gx,gy,px,py,t);
  }else{c.save();c.beginPath();c.rect(px,py,4*s,t);c.rect(px+28*s,py,4*s,t);c.clip();wallFace(c,m,gx,gy,px,py,t,oldWall);c.restore();}
  // The24x30 silhouette is encoded inside this32px asset, equally for both axes.
  c.drawImage(open?images.open:images.closed,px,py,t,t);return;
 }
 if(isUp(f)||isDown(f)){c.drawImage(isUp(f)?images.up:images.down,px,py,t,t);return;}
 if(isWater(f)){drawWater(c,m,gx,gy,px,py,t);return;}
 if(f==='floor')return;
 c.font=`bold ${Math.max(6,t*.64)}px monospace`;c.textAlign='center';c.textBaseline='middle';c.fillStyle=f.startsWith('enter_')?'#d0a7dc':'#c9ad85';c.fillText(f.startsWith('enter_')?'Ω':f==='fountain_blue'?'○':f.startsWith('escape_hatch')?f.endsWith('up')?'↑':'↓':f.startsWith('trap')?'^':f==='shaft'?'○':'·',px+t*.5,py+t*.52);
}
function preferredDoor(axis){const m=maps[selected],list=doors(m).filter(d=>doorAxis(m,d.x,d.y)===axis);if(axis==='horizontal')return list[0];const score=d=>{let north=0,south=0;while(north<3&&isWall(feature(m,d.x,d.y-north-1)))north++;while(south<3&&isWall(feature(m,d.x,d.y+south+1)))south++;return Math.min(north,south)*100+(north+south)*10-Math.abs(d.x-m.w/2)-Math.abs(d.y-m.h/2);};return list.sort((a,b)=>score(b)-score(a))[0];}
function axisDoor(axis){const m=maps[selected],focused=doors(m)[focusDoor];if(focused&&doorAxis(m,focused.x,focused.y)===axis)return focused;return preferredDoor(axis);}
function comparisons(){const m=maps[selected];for(const axis of ['horizontal','vertical']){const door=axisDoor(axis);for(const state of ['closed','open']){const el=$(state+axis),c=el.getContext('2d');c.imageSmoothingEnabled=false;c.fillStyle='#080b0b';c.fillRect(0,0,320,320);if(!door)continue;for(let dy=-2;dy<=2;dy++)for(let dx=-2;dx<=2;dx++)tile(c,m,door.x+dx,door.y+dy,(dx+2)*64,(dy+2)*64,64,'fit',dx===0&&dy===0?state==='open':isOpened(door.x+dx,door.y+dy));el.onclick=()=>{const index=doors(m).findIndex(d=>d.x===door.x&&d.y===door.y),key=doorKey(door.x,door.y);if(state==='open')opened.add(key);else opened.delete(key);focus(index);};}}}
function draw(){
 if(!images.closed||!images.open)return;const m=maps[selected],t=overview?8:32,cols=canvas.width/t,rows=canvas.height/t,cx=overview?0:Math.max(0,Math.min(m.w-cols,Math.floor(center.x-cols/2))),cy=overview?0:Math.max(0,Math.min(m.h-rows,Math.floor(center.y-rows/2))),ox=overview?(canvas.width-m.w*t)/2:0,oy=overview?(canvas.height-m.h*t)/2:0;
 transform={t,cx,cy,ox,oy};ctx.imageSmoothingEnabled=false;ctx.fillStyle='#080b0b';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.save();ctx.translate(ox-cx*t,oy-cy*t);
 for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++)tile(ctx,m,x,y,x*t,y*t,t,doorMode);ctx.restore();
 const list=doors(m),door=list[focusDoor],axis=door?doorAxis(m,door.x,door.y):'horizontal';$('mapTitle').textContent=m.place+' · '+(labels[m.layout]||m.layout.replace('layout_',''));$('mapInfo').textContent='지도 번호 '+m.seed+' · 원본 지형 그대로';$('overview').textContent=overview?'거리 크기로 보기':'전체 지도 보기';$('wallStyle').textContent=wallOld?'새 콘크리트 벽 보기':'이전 벽면 비교';$('toggleDoor').textContent=door&&isOpened(door.x,door.y)?'이 문 닫기':'이 문 열기';$('focusInfo').textContent=(axis==='vertical'?'세로 벽의 문 · 좌우로 통과':'가로 벽의 문 · 위아래로 통과')+' · '+(door?door.x+', '+door.y:'')+' · 새 원화24×30 · 같은 크기';comparisons();waterDemos();
}
function focus(index){const list=doors(maps[selected]);focusDoor=((index%list.length)+list.length)%list.length;center={...list[focusDoor]};overview=false;draw();}
function focusAxis(axis){const list=doors(maps[selected]),d=preferredDoor(axis),index=d?list.findIndex(p=>p.x===d.x&&p.y===d.y):-1;if(index>=0)focus(index);}
function select(index){selected=index;focusDoor=0;$('mapSelect').value=String(index);focusAxis('vertical');}
function toggle(x,y){const k=doorKey(x,y);if(opened.has(k))opened.delete(k);else opened.add(k);draw();}
$('mapSelect').onchange=e=>select(Number(e.target.value));$('nextDoor').onclick=()=>focus(focusDoor+1);$('toggleDoor').onclick=()=>{const d=doors(maps[selected])[focusDoor];toggle(d.x,d.y);};$('overview').onclick=()=>{overview=!overview;draw();};
$('horizontalFocus').onclick=()=>focusAxis('horizontal');$('verticalFocus').onclick=()=>focusAxis('vertical');
$('wallStyle').onclick=()=>{wallOld=!wallOld;draw();};
$('waterFocus').onclick=waterFocus;
canvas.onclick=e=>{const r=canvas.getBoundingClientRect(),{t,cx,cy,ox,oy}=transform,x=Math.floor(((e.clientX-r.left)*canvas.width/r.width-ox)/t)+cx,y=Math.floor(((e.clientY-r.top)*canvas.height/r.height-oy)/t)+cy,m=maps[selected];if(x<0||y<0||x>=m.w||y>=m.h)return;if(overview){center={x,y};overview=false;draw();}else if(isDoor(feature(m,x,y))){focusDoor=doors(m).findIndex(d=>d.x===x&&d.y===y);toggle(x,y);}else{center={x,y};draw();}canvas.focus();};
window.addEventListener('keydown',e=>{if(['INPUT','SELECT','TEXTAREA','BUTTON'].includes(e.target.tagName))return;const dirs={ArrowLeft:[-2,0],ArrowRight:[2,0],ArrowUp:[0,-2],ArrowDown:[0,2],a:[-2,0],d:[2,0],w:[0,-2],s:[0,2]},v=dirs[e.key];if(!v)return;e.preventDefault();center={x:Math.max(0,Math.min(maps[selected].w-1,center.x+v[0])),y:Math.max(0,Math.min(maps[selected].h-1,center.y+v[1]))};draw();});
window.doorPreview={select,focus,focusAxis,setOverview:value=>{overview=value;draw();},toggleFocused:()=>{const d=doors(maps[selected])[focusDoor];toggle(d.x,d.y);},getState:()=>{const m=maps[selected],d=doors(m)[focusDoor],axis=doorAxis(m,d.x,d.y);return{selected,overview,wallOld,doorAxis:axis,doorSpriteSize:[32,32],doorSilhouette:[24,30],sameSpriteForBothAxes:true,center:{...center},focusDoor,doors:doors(m).map(d=>({...d,axis:doorAxis(m,d.x,d.y)})),opened:Array.from(opened),map:m};},draw};
(async()=>{const sources={reference:assets+'scene-reference.png',floor:assets+'cement-reference.png',up:assets+'stairs-up12-32.png',down:assets+'stairs-down06-32.png',closed:'assets/fire-door-closed32.png',open:'assets/fire-door-open32.png',shallow:'assets/water-shallow128.png',deep:'assets/water-deep128.png',crawlClosed:'assets/crawl-closed_door.png',crawlOpen:'assets/crawl-open_door.png',wall:'assets/concrete-wall-surface256.png'};await Promise.all(Object.entries(sources).map(async([key,src])=>{images[key]=await new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>reject(Error('Image unavailable: '+src));im.src=src;});}));for(let i=0;i<16;i++){const patch=floorPatches[Math.floor(i/4)],c=document.createElement('canvas');c.width=c.height=32;const cc=c.getContext('2d');cc.imageSmoothingEnabled=false;cc.translate(16,16);cc.rotate((i%4)*Math.PI/2);cc.drawImage(images.floor,...patch,-16,-16,32,32);tiles.push(c);}maps.forEach((m,i)=>{const o=document.createElement('option');o.value=i;o.textContent=(i+1)+' · '+m.place;$('mapSelect').append(o);});select(1);waterFocus();window.doorPreviewReady=true;window.waterPreviewReady=true;})();
