'use strict';
const $=id=>document.getElementById(id),canvas=$('map'),ctx=canvas.getContext('2d',{willReadFrequently:true}),mini=$('mini'),mc=mini.getContext('2d');
const V=CrawlVisibility;let memory=null,fogEnabled=false;
let floorMode='random',floorMix=0,floorVariants=[],marketFloor=([4,5,6,7].includes(Number(new URLSearchParams(location.search).get("floor")))?Number(new URLSearchParams(location.search).get("floor")):4),stockMix=0;
const G=StreetGen,stages=[['① 공간 나누기','건물과 빈 공간을 놓을 구역을 무작위로 나눠요.'],['② 방·광장 배치','각 구역에 크기와 위치가 다른 공간을 만들어요.'],['③ 골목 연결','방을 연결하고 돌아갈 수 있는 길도 조금 더 만들어요.'],['④ 장소·소품 배치','준비한 공연장 입구를 붙이고, 길을 막지 않는 위치에 소품을 놓아요.'],['⑤ 계단·시작점 배치','멀리 떨어진 계단과 시작점을 놓고 길 연결을 검사해요.']];
let map,player,stage=4,overview=false,showPath=false,animation=null,walking=null,serial=1,images={},transform={};
const sources={marketfront:'../city-market02/assets/market-shopfront64.png',rack:'../city-market02/assets/market-merch-rack32.png',boxes:'../city-market02/assets/market-delivery-boxes32.png',upstairs:'../city-market02/assets/stairs-up12-32.png',downstairs:'../city-market02/assets/stairs-down06-32.png',fence:'../city-market02/assets/fence-cutout32.png',floor:'../city-market02/assets/cement-reference.png',reference:'../city-market02/assets/scene-reference.png',rat:'../city-market02/assets/rat.png',stairs:'../city-market02/assets/stairs.png',body:'../city-market02/assets/body.png',boots:'../city-market02/assets/boots.png',armour:'../city-market02/assets/armour.png',helmet:'../city-market02/assets/helmet.png',sword:'../city-market02/assets/sword.png'};
Object.assign(sources,Object.fromEntries(MerchCatalog.map(p=>[p.id,p.file])),Object.fromEntries(MarketMembers.map(m=>['member-'+m.id,m.image])));
const loadImage=src=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>reject(new Error('이미지를 불러올 수 없습니다: '+src));im.src=src;});
function hash(x,y){let n=Math.imul(x+19,374761393)^Math.imul(y+73,668265263);for(const c of map.seed)n=Math.imul(n^c.charCodeAt(0),1274126177);return(n^(n>>>13))>>>0;}
function texture(rect,x,y,w,h,opacity=1,source=images.reference){ctx.globalAlpha=opacity;ctx.drawImage(source,...rect,x,y,w,h);ctx.globalAlpha=1;}
const floorPatches=[[270,150,32,32],[285,153,32,32],[160,300,32,32],[260,300,32,32]],roofPatch=[112,54,16,16],facePatch=[130,62,24,25],pavingPatch=[112,86,32,8];
function visibleCells(){return stage===1?map.roomCells:stage===2?map.corridorCells:stage===4&&fogEnabled?memory.renderCells(map.cells):map.cells;}
function canSee(p){return !fogEnabled||stage!==4||Boolean(memory.visible[p.y*map.w+p.x]);}
function isKnown(p){return !fogEnabled||Boolean(memory.explored[p.y*map.w+p.x]);}
function pathTo(p){return fogEnabled?V.knownRoute({w:map.w,h:map.h,cells:memory.renderCells(map.cells)},player,p,memory.explored):G.route(map,player,p);}
function updateVision(){const before=memory.visible;memory.update(map.cells,player);const spotted=map.enemies.some(e=>memory.visible[e.y*map.w+e.x]&&!before[e.y*map.w+e.x]);if(spotted){clearInterval(walking);walking=null;}return spotted;}
function drawFog(t){if(!fogEnabled||stage!==4)return;ctx.filter='none';for(let y=0;y<map.h;y++)for(let x=0;x<map.w;x++){const i=y*map.w+x;if(!memory.explored[i]){ctx.fillStyle='#06090b';ctx.fillRect(x*t,y*t,t,t);}else if(!memory.visible[i]){ctx.fillStyle='rgba(0,0,0,.74)';ctx.fillRect(x*t,y*t,t,t);}}}
function computeTransform(){const t=overview?Math.floor(Math.min(canvas.width/map.w,canvas.height/map.h)):32,ox=overview?Math.floor((canvas.width-map.w*t)/2):0,oy=overview?Math.floor((canvas.height-map.h*t)/2):0,cx=overview?0:Math.max(0,Math.min(map.w-Math.floor(canvas.width/t),player.x-Math.floor(canvas.width/t/2))),cy=overview?0:Math.max(0,Math.min(map.h-Math.floor(canvas.height/t),player.y-Math.floor(canvas.height/t/2)));return{t,ox,oy,cx,cy};}
function draw(){if(!map||!images.reference)return;ctx.imageSmoothingEnabled=false;ctx.fillStyle='#06090b';ctx.fillRect(0,0,canvas.width,canvas.height);transform=computeTransform();const{t,ox,oy,cx,cy}=transform,cells=visibleCells(),open=(x,y)=>x>=0&&y>=0&&x<map.w&&y<map.h&&cells[y*map.w+x]!==G.WALL;
ctx.save();ctx.translate(ox-cx*t,oy-cy*t);
if(Market108.isOld()){
for(let y=0;y<map.h;y++)for(let x=0;x<map.w;x++){const px=x*t,py=y*t;if(stage===0){texture(roofPatch,px,py,t,t);continue;}if(cells[y*map.w+x]!==G.WALL){const tile=floorMode==='repeat'?0:RandomFloor.index(map.seed+'-F'+marketFloor,floorMix,x,y);ctx.drawImage(floorVariants[tile],px,py,t,t);if(!open(x,y-1))texture(pavingPatch,px,py,t,t*.22,.8);if(!open(x-1,y)){ctx.save();ctx.translate(px,py+t);ctx.rotate(-Math.PI/2);texture(pavingPatch,0,0,t,t*.22,.65);ctx.restore();}}else {texture(roofPatch,px,py,t,t);ctx.fillStyle='rgba(11,13,15,.60)';ctx.fillRect(px,py,t,t);}}
if(stage===0){ctx.lineWidth=1;ctx.strokeStyle='#8aa59d';for(const p of map.partitions.filter(p=>p.depth>=2)){ctx.strokeRect(p.x*t,p.y*t,p.w*t,p.h*t);}ctx.fillStyle='#c0d2c8';ctx.font=`${Math.max(10,t*.35)}px monospace`;map.rooms.forEach((r,i)=>ctx.fillText(String(i+1),r.cx*t,r.cy*t));}
else for(let y=0;y<map.h;y++)for(let x=0;x<map.w;x++)if(cells[y*map.w+x]===G.WALL){const px=x*t,py=y*t;if(open(x,y+1)){ctx.filter='brightness(1.35)';texture(facePatch,px,py+t*.08,t,t*.92);ctx.filter='none';ctx.fillStyle='#625d54';ctx.fillRect(px,py+t*.27,t,Math.max(1,t/32));ctx.fillStyle='#171714';ctx.fillRect(px,py+t*.94,t,t*.06);}if(open(x-1,y)){ctx.fillStyle='#5c574d';ctx.fillRect(px,py,t*.06,t);}if(open(x+1,y)){ctx.fillStyle='#3e3b34';ctx.fillRect(px+t*.94,py,t*.06,t);}if(open(x,y-1)){ctx.fillStyle='#35332c';ctx.fillRect(px,py,t,t*.05);}}


}else{
 for(let y=0;y<map.h;y++)for(let x=0;x<map.w;x++){
  const px=x*t,py=y*t;
  if(stage!==0&&cells[y*map.w+x]!==G.WALL){const i=floorMode==='repeat'?0:RandomFloor.index(map.seed+'-F'+marketFloor,floorMix,x,y);ctx.drawImage(floorVariants[i],px,py,t,t);}
  else Market108.wall(ctx,cells,map.w,map.h,x,y,t,hash(x,y)%8);
 }
}
if(stage>=3&&!Market108.isOld())(document.getElementById("patternBefore109").checked?Wear109:Wear110).draw(ctx,map,t,marketFloor,hash);

// Existing venue artwork supplies wall-mounted units; positions depend only on map seed.
if(stage>=3&&Market108.isOld()){for(let y=1;y<map.h-1;y++)for(let x=2;x<map.w-2;x++){
 if(cells[y*map.w+x]!==G.WALL||!open(x,y+1)||cells[y*map.w+x-1]!==G.WALL||cells[y*map.w+x+1]!==G.WALL)continue;
 const p=map.prefab;if(x>=p.x-1&&x<=p.x+p.w&&y>=p.y-1&&y<=p.y+p.h)continue;const e=map.exitDoor;if(e&&x>=e.x-1&&x<=e.x+e.w&&y>=e.y-1&&y<=e.y+e.h)continue;
 if(x%3!==1||hash(x,y)%100>=68)continue;
 const px=x*t,py=y*t,kind=hash(x+431,y)%4;
 ctx.filter='brightness(1.35)';
 if(kind===0)texture([289,34,37,19],px-t*.07,py+t*.13,t*1.15,t*.59);
 if(kind===1){ctx.filter='none';ctx.lineJoin='miter';ctx.beginPath();ctx.moveTo(px+t*.1,py+t*.13);ctx.lineTo(px+t*.58,py+t*.13);ctx.lineTo(px+t*.58,py+t*.83);ctx.strokeStyle='#222526';ctx.lineWidth=Math.max(2,t*.13);ctx.stroke();ctx.strokeStyle='#92938b';ctx.lineWidth=Math.max(1,t*.065);ctx.stroke();ctx.fillStyle='#535750';ctx.fillRect(px+t*.51,py+t*.38,t*.15,t*.07);ctx.fillRect(px+t*.51,py+t*.67,t*.15,t*.07);}
 if(kind===2)texture([294,86,22,16],px+t*.14,py+t*.27,t*.72,t*.52);
 if(kind===3)texture([183,31,32,12],px,py+t*.17,t,t*.38);
 ctx.filter='none';
}}
if(stage>=3){
 for(const shop of map.marketWalls)Scene112.draw(ctx,shop,map,images,t,stockMix);
 for(const prop of map.props){if(prop.type==='fence')ctx.drawImage((Market108.isOld()?images:Market108.images).fence,prop.x*t,prop.y*t+t*.31,t,t*.69);}
 for(const prop of map.marketProps)Scene112.draw(ctx,prop,map,images,t,stockMix);
}
if(stage===4){if(showPath){const path=pathTo(map.exit);ctx.fillStyle='rgba(140,225,210,.8)';for(const p of path)ctx.fillRect(p.x*t+t*.43,p.y*t+t*.43,t*.14,t*.14);}for(const item of map.items){if(!canSee(item))continue;ctx.fillStyle='#d4b775';ctx.fillRect(item.x*t+t*.42,item.y*t+t*.4,t*.16,t*.16);}ctx.drawImage(images.upstairs,map.upstairs.x*t,map.upstairs.y*t,t,t);if(map.exitType==='wall'){const door=map.exitDoor;if(Market108.isOld()){ texture([326,57,105,73],door.x*t,door.y*t,door.w*t,door.h*t);ctx.fillStyle='#bab1a0';ctx.fillRect(map.exit.x*t+t*.14,map.exit.y*t,t*.72,Math.max(1,t*.09)); }else{Market108.exitDoor(ctx,door,t);}}else{ctx.drawImage(images.downstairs,map.exit.x*t,map.exit.y*t,t,t);}for(const enemy of map.enemies)if(canSee(enemy))ctx.drawImage(images.rat,enemy.x*t,enemy.y*t,t,t);for(const part of ['body','boots','armour','helmet','sword'])ctx.drawImage(images[part],player.x*t,player.y*t,t,t);ctx.fillStyle='#9ed7d2';ctx.fillRect(player.x*t+t*.25,player.y*t+t*.94,t*.5,t*.04);}
drawFog(t);ctx.restore();drawMini(cells);updateInfo();}
function drawMini(cells){mc.imageSmoothingEnabled=false;const scale=Math.min(mini.width/map.w,mini.height/map.h);mc.fillStyle='#06090b';mc.fillRect(0,0,mini.width,mini.height);for(let y=0;y<map.h;y++)for(let x=0;x<map.w;x++){const i=y*map.w+x,c=cells[i];if(stage===4&&fogEnabled&&!memory.explored[i])continue;const lit=stage!==4||!fogEnabled||memory.visible[i];mc.fillStyle=c===G.FLOOR?(lit?'#8b8e7d':'#444b42'):c===G.BARRIER?(lit?'#b8b6a0':'#5d6357'):(lit?'#454c43':'#242d27');mc.fillRect(x*scale,y*scale,Math.ceil(scale),Math.ceil(scale));}if(stage===4){if(isKnown(map.upstairs)){mc.fillStyle='#9ab9db';mc.fillRect(map.upstairs.x*scale,map.upstairs.y*scale,scale,scale);}if(isKnown(map.exit)){mc.fillStyle='#eadcaa';mc.fillRect(map.exit.x*scale,map.exit.y*scale,scale,scale);}mc.fillStyle='#a7e5d6';mc.fillRect(player.x*scale,player.y*scale,scale,scale);}if(!overview){mc.strokeStyle='#859d94';mc.lineWidth=1;mc.strokeRect(transform.cx*scale,transform.cy*scale,canvas.width/transform.t*scale,canvas.height/transform.t*scale);}}
function updateInfo(){$('stageTitle').textContent=stages[stage][0];$('stageDetail').textContent=stages[stage][1];$('roomCount').textContent=map.rooms.length+'곳';$('edgeCount').textContent=map.edges.length+'개';$('distance').textContent=isKnown(map.exit)?map.validation.exitDistance+'칸 / 80×70':'미발견 / 80×70';$('validation').textContent=stage<2?'골목을 연결하기 전이에요.':'✓ 모든 길 연결 · 출구 도달 가능';document.querySelectorAll('[data-stage]').forEach(b=>b.classList.toggle('selected',Number(b.dataset.stage)===stage));$('overview').textContent=overview?'거리 화면 보기':'전체 지도 보기';$('path').textContent=showPath?'길 표시 끄기':'발견한 출구까지 길 표시';$('fog').textContent=fogEnabled?'탐험 안개 끄기':'탐험 안개 켜기';let seen=0;for(let i=0;i<map.cells.length;i++)if(memory.explored[i]&&map.cells[i]===G.FLOOR)seen++;$('explored').textContent=(seen/map.validation.walkable*100).toFixed(1)+'%';$('visibleCount').textContent=memory.visible.reduce((a,b)=>a+b,0)+'칸';if(stage===4){$('stageTitle').textContent='잔향도시 '+marketFloor+'층 · '+map.profile.name;$('stageDetail').textContent=fogEnabled?'시야7칸 · 벽 뒤는 가림 · 펜스 너머는 보임':map.profile.detail;$('floorCode').textContent=map.seed+' / '+marketFloor+'층 / 바닥 '+floorMix+' / 상품 '+stockMix;$('floorDescription').textContent=map.profile.detail;$('shopCount').textContent=map.marketWalls.length+'곳';$('propCount').textContent=map.marketProps.length+'개';document.querySelectorAll('[data-floor]').forEach(b=>b.classList.toggle('selected',Number(b.dataset.floor)===marketFloor));}}
function stop(){clearInterval(animation);animation=null;clearInterval(walking);walking=null;}
function newMap(seed){stop();map=MarketGen.generate(seed,marketFloor,$("exitMode").value);map.enemies=[];map.items=[];player={...map.start};memory=new V.Memory(map.w,map.h);memory.update(map.cells,player);stage=4;$('seed').value=map.seed;$('message').textContent='시작 지점 · 바로 뒤의 계단은 이전 층으로 돌아가는 올라가는 계단이에요.';draw();return map;}
function setStage(n){stop();stage=Math.max(0,Math.min(4,n));draw();}
function move(dx,dy){if(stage!==4||!Number.isInteger(dx)||!Number.isInteger(dy)||Math.max(Math.abs(dx),Math.abs(dy))!==1)return false;const x=player.x+dx,y=player.y+dy;if(x<0||y<0||x>=map.w||y>=map.h||map.cells[y*map.w+x]!==G.FLOOR){clearInterval(walking);walking=null;$('message').textContent='벽이나 펜스가 막고 있어요. 다른 길로 가보세요.';return false;}player={x,y};const spotted=updateVision();$('message').textContent=spotted?'새로운 적이 보여 자동 이동을 멈췄어요.':x===map.exit.x&&y===map.exit.y?'다음 층 입구 발견! 층 이동은 아직 연결 전이에요.':'탐험 중 · 밝은 곳만 현재 보이는 범위예요.';draw();return true;}
$('newMap').onclick=()=>newMap('CITY-'+String(++serial).padStart(3,'0')+'-'+Math.floor(Math.random()*100000));$('apply').onclick=()=>newMap($('seed').value.trim()||'CITY-001');$('seed').addEventListener('keydown',e=>{if(e.key==='Enter')$('apply').click();});
$('build').onclick=()=>{stop();stage=0;overview=true;draw();animation=setInterval(()=>{stage++;draw();if(stage===4){clearInterval(animation);animation=null;}},1000);};
document.querySelectorAll('[data-stage]').forEach(b=>b.onclick=()=>setStage(Number(b.dataset.stage)));$('overview').onclick=()=>{overview=!overview;draw();};$('path').onclick=()=>{showPath=!showPath;if(showPath&&!isKnown(map.exit))$('message').textContent='아직 출구를 발견하지 못했어요.';draw();};$('fog').onclick=()=>{fogEnabled=!fogEnabled;draw();};
window.addEventListener('keydown',e=>{if(['INPUT','SELECT','TEXTAREA'].includes(e.target.tagName))return;const keys={q:[-1,-1],e:[1,-1],z:[-1,1],c:[1,1],Home:[-1,-1],PageUp:[1,-1],End:[-1,1],PageDown:[1,1],'7':[-1,-1],'9':[1,-1],'1':[-1,1],'3':[1,1],'8':[0,-1],'2':[0,1],'4':[-1,0],'6':[1,0],ArrowUp:[0,-1],w:[0,-1],W:[0,-1],ArrowDown:[0,1],s:[0,1],S:[0,1],ArrowLeft:[-1,0],a:[-1,0],A:[-1,0],ArrowRight:[1,0],d:[1,0],D:[1,0]};const direction=keys[e.key]||keys[e.key.toLowerCase()];if(direction){e.preventDefault();clearInterval(walking);move(...direction);}});
canvas.onclick=e=>{if(stage!==4)return;const rect=canvas.getBoundingClientRect(),sx=(e.clientX-rect.left)*canvas.width/rect.width,sy=(e.clientY-rect.top)*canvas.height/rect.height,{t,ox,oy,cx,cy}=transform,x=Math.floor((sx-ox)/t)+cx,y=Math.floor((sy-oy)/t)+cy;if(x<0||y<0||x>=map.w||y>=map.h)return;if(fogEnabled&&!memory.explored[y*map.w+x]){$('message').textContent='아직 탐험하지 않은 곳이에요. 먼저 가까이 다가가보세요.';return;}const path=pathTo({x,y});clearInterval(walking);if(!path.length){$('message').textContent='그곳은 막혀 있어요.';return;}let i=1;walking=setInterval(()=>{if(i>=path.length){clearInterval(walking);walking=null;return;}const next=path[i++];if(!move(next.x-player.x,next.y-player.y)){clearInterval(walking);walking=null;}},65);canvas.focus();};

function showFence(){stop();stage=4;overview=false;const fences=map.props.filter(p=>p.type==='fence');if(!fences.length){$('message').textContent='이 지도에는 펜스가 배치되지 않았어요.';return;}const f=fences[Math.floor(fences.length/2)],choices=[];for(let y=1;y<map.h-1;y++)for(let x=1;x<map.w-1;x++)if(map.cells[y*map.w+x]===G.FLOOR)choices.push({x,y,score:Math.abs(x-f.x)+Math.abs(y-(f.y+3))});choices.sort((a,b)=>a.score-b.score);player={x:choices[0].x,y:choices[0].y};updateVision();draw();$('message').textContent='공연장 앞 미리보기 · 은빛 금속 펜스 3칸은 이동을 막으며 옆으로 돌아갈 수 있어요.';}
$('fenceView').onclick=showFence;

function showExit(){stop();stage=4;overview=false;const e=map.exit,choices=[];for(let y=1;y<map.h-1;y++)for(let x=1;x<map.w-1;x++)if(map.cells[y*map.w+x]===G.FLOOR)choices.push({x,y,score:Math.abs(x-e.x)+Math.abs(y-(e.y+3))});choices.sort((a,b)=>a.score-b.score);player={x:choices[0].x,y:choices[0].y};updateVision();draw();$('message').textContent=map.exitType==='wall'?'벽에 붙은 공연장 입구 · 문 앞칸이 다음 층 출구예요.':'광장 바닥의 내려가는 계단 · 승인한 원형 계단 도트예요.';}
$('exitView').onclick=showExit;$('exitMode').onchange=()=>{newMap($('seed').value);showExit();};

function showStart(){stop();stage=4;overview=false;player={...map.start};updateVision();draw();$('message').textContent='시작 지점 · 캐릭터 바로 뒤의 작은 계단이 올라가는 계단이에요. 실제 층 이동은 아직 연결 전이에요.';}
$('startView').onclick=showStart;
Promise.all([Market108.load(),...Object.entries(sources).map(async([k,src])=>{images[k]=await loadImage(src);})]).then(()=>{if(location.hash==='#floor')$('exitMode').value='floor';if(location.hash==='#wall')$('exitMode').value='wall';Market108.prepare(images);MarketStock.makeSprites(images);MarketStock.gallery(images);floorVariants=RandomFloor.variants(images.floor);RandomFloor.showSwatches(floorVariants,$('floorSwatches'));newMap('MARKET-001');if(location.hash==='#fence')showFence();if(['#exit','#floor','#wall'].includes(location.hash))showExit();if(location.hash==='#acrylic')showMerchType('acrylic-window');window.previewReady=true;}).catch(e=>{$('message').textContent=e.message;});

function setFloorMode(mode){if(!['repeat','random'].includes(mode))throw Error('Unknown floor pattern');floorMode=mode;$('floorPattern').value=mode;draw();}
function setFloorMix(value){if(!Number.isSafeInteger(value)||value<0)throw Error('Invalid floor mix');floorMix=value;draw();}
$('floorPattern').onchange=()=>setFloorMode($('floorPattern').value);
$('shuffleFloor').onclick=()=>{setFloorMix(floorMix+1);$('message').textContent='바닥 배치만 다시 섞었어요. 지도·벽·계단 위치는 그대로예요.';};

function setMarketFloor(value){if(![4,5,6,7].includes(value))throw Error('Unknown market floor');marketFloor=value;newMap($('seed').value||'MARKET-001');}document.querySelectorAll('[data-floor]').forEach(button=>button.onclick=()=>setMarketFloor(Number(button.dataset.floor)));$('marketView').onclick=()=>{stop();stage=4;overview=false;const p=map.marketWalls[Math.floor(map.marketWalls.length/2)];if(!p)return;player={x:p.x,y:p.y+1};updateVision();draw();};
function setStockMix(value){if(!Number.isSafeInteger(value)||value<0)throw Error('Invalid stock mix');stockMix=value;draw();} $('shuffleStock').onclick=()=>{setStockMix(stockMix+1);$('message').textContent='아크릴과 티셔츠 조합만 다시 뽑았어요. 지도와 소품 위치는 그대로예요.';};
canvas.addEventListener('mousemove',event=>{if(!map)return;const r=canvas.getBoundingClientRect(),sx=(event.clientX-r.left)*canvas.width/r.width,sy=(event.clientY-r.top)*canvas.height/r.height,{t,ox,oy,cx,cy}=transform,x=Math.floor((sx-ox)/t)+cx,y=Math.floor((sy-oy)/t)+cy;const fixture=map.marketProps.find(p=>p.x===x&&p.y===y)||map.marketWalls.find(p=>p.y===y&&x>=p.x&&x<p.x+2);$('stockInfo').textContent=fixture?MarketStock.describe(fixture,map,stockMix):'진열품 위에 마우스를 올리면 멤버 이름이 나와요.';});
function showMerchType(type){
 stop();stage=4;overview=false;const pool=[...map.marketWalls,...map.marketProps].filter(p=>p.type===type);if(!pool.length)return false;
 const fixture=pool[Math.floor(pool.length/2)],choices=[];
 for(let y=Math.max(1,fixture.y-3);y<=Math.min(map.h-2,fixture.y+3);y++)for(let x=Math.max(1,fixture.x-3);x<=Math.min(map.w-2,fixture.x+3);x++)if(map.cells[y*map.w+x]===G.FLOOR)choices.push({x,y,score:Math.abs(x-fixture.x)+Math.abs(y-fixture.y-2)});
 choices.sort((a,b)=>a.score-b.score);if(!choices.length)return false;player={x:choices[0].x,y:choices[0].y};updateVision();draw();$('stockInfo').textContent=MarketStock.describe(fixture,map,stockMix);return true;
}
$('acrylicView').onclick=()=>showMerchType('acrylic-window');$('shirtView').onclick=()=>showMerchType('shirt-window');$('trashView').onclick=()=>showMerchType('trash-bags');
window.previewApp={showMerchType,setStockMix,setMarketFloor,setFloorMode,setFloorMix,setFogEnabled:value=>{fogEnabled=Boolean(value);draw();},getMap:()=>map,showStart,showExit,showFence,newMap,setStage,draw,getState:()=>({stockMix,stock:map?[...map.marketWalls,...map.marketProps].filter(p=>['acrylic-window','acrylic-rack','shirt-window','shirt-stack'].includes(p.type)).map(p=>({...p,members:MarketStock.select(map.seed,marketFloor,p,stockMix)})):[],marketFloor,marketWalls:map.marketWalls,marketProps:map.marketProps,floorProfile:map.profile,floorMode,floorMix,floorChoices:Array.from({length:map.w*map.h},(_,i)=>floorMode==='repeat'?0:RandomFloor.index(map.seed+'-F'+marketFloor,floorMix,i%map.w,Math.floor(i/map.w))),fogEnabled,visible:Array.from(memory.visible),explored:Array.from(memory.explored),visibleEnemies:map.enemies.filter(canSee),seed:map?.seed,stage,player:{...player},exit:map?.exit,exitDoor:map?.exitDoor,exitType:map?.exitType,upstairs:map?.upstairs,start:map?.start,validation:map?.validation,rooms:map?.rooms.length,width:map?.w,height:map?.h}),setOverview:value=>{overview=value;draw();},move};








document.getElementById('compareOld').onchange=e=>{Market108.setOld(e.target.checked);MarketStock.gallery(images);draw();};

for(const id of ["noWear","wearLevel","patternBefore109","beforeScene112"])document.getElementById(id).onchange=()=>draw();
