(async()=>{
 const manifest=await(await fetch('manifest.json')).json(),params=new URLSearchParams(location.search);
 const canvas=document.getElementById('field'),g=canvas.getContext('2d',{willReadFrequently:true}),select=document.getElementById('sample'),oracle=document.getElementById('oracle');
 const atlases={},loadImage=url=>new Promise((r,j)=>{const im=new Image();im.onload=()=>r(im);im.onerror=()=>j(Error(url));im.src=url});
 await Promise.all(['floor','wall','feat','main','player'].map(async k=>atlases[k]=await loadImage(`assets/${k}.png`)));
 let sample=Math.max(0,Number(params.get('sample'))||0),map,probe,state,zoom=2,view,timer,request=0;
 const dirs=[[-1,-1],[0,-1],[1,-1],[-1,0],[1,0],[-1,1],[0,1],[1,1]],key=(x,y)=>`${x},${y}`;
 manifest.maps.forEach((m,i)=>select.add(new Option(`${m.name} · ${m.depth}층 · ${m.forced?'시설 검토':'일반 생성'} · ${m.seed}`,i)));select.value=String(sample);
 const stop=()=>{clearTimeout(timer);timer=null},cell=(x,y)=>map.rows[y]?.[x]??'#';
 const pass=(x,y)=>x>0&&y>0&&x<map.width-1&&y<map.height-1&&(map.passable[y*map.width+x]||cell(x,y)==='+');
 const canStep=(x,y,nx,ny)=>pass(nx,ny)&&(manifest.nativeDiagonalCornerAllowed||nx===x||ny===y||pass(nx,y)||pass(x,ny));
 const visible=()=>CrawlVisibility.compute(map.width,map.height,state.player,(x,y)=>state.opened.has(key(x,y))?0:map.opacity[y*map.width+x],7);
 function tile(t,x,y,s){g.drawImage(atlases[t.atlas],t.sx,t.sy,t.width,t.height,x+t.dx*s,y+t.dy*s,t.width*s,t.height*s)}
 function draw(){if(!map||!state)return;const seen=visible(),fog=document.getElementById('fog').checked,actors=document.getElementById('actors').checked;
  for(let i=0;i<seen.length;i++)if(seen[i]){state.explored[i]=1;state.knownOpen[i]=state.opened.has(key(i%map.width,Math.floor(i/map.width)))?1:0}
  const s=zoom==='fit'?Math.min(canvas.width/(map.width*32),canvas.height/(map.height*32)):Number(zoom);
  const ox=Math.round(zoom==='fit'?(canvas.width-map.width*32*s)/2:canvas.width/2-(state.player.x+.5)*32*s);
  const oy=Math.round(zoom==='fit'?(canvas.height-map.height*32*s)/2:canvas.height/2-(state.player.y+.5)*32*s);
  view={s,ox,oy};g.fillStyle='#080c10';g.fillRect(0,0,canvas.width,canvas.height);g.imageSmoothingEnabled=false;
  const doorMap=new Map(map.doors.map(d=>[key(d.x,d.y),d]));
  for(let y=0;y<map.height;y++)for(let x=0;x<map.width;x++){
   const i=y*map.width+x,dx=ox+x*32*s,dy=oy+y*32*s;if(dx<-32*s||dy<-32*s||dx>canvas.width||dy>canvas.height||(fog&&!state.explored[i]))continue;
   const d=doorMap.get(key(x,y)),open=fog&&!seen[i]?state.knownOpen[i]:state.opened.has(key(x,y));
   tile(map.palette[map.floors[i]],dx,dy,s);tile(map.palette[d&&open?d.opened:map.features[i]],dx,dy,s);
   if(map.overlays[i]>=0)tile(map.palette[map.overlays[i]],dx,dy,s);
   if(fog&&!seen[i]){g.fillStyle='rgba(0,0,0,.77)';g.fillRect(dx,dy,32*s+.5,32*s+.5)}
  }
  if(actors)for(const a of probe.actors||[])if(a.kind!=='player'&&(!fog||seen[a.y*map.width+a.x]))for(const t of a.tiles)tile(t,ox+a.x*32*s,oy+a.y*32*s,s);
  const playerTiles=(probe.actors||[]).find(a=>a.kind==='player')?.tiles||manifest.playerTiles;
  for(const t of playerTiles)tile(t,ox+state.player.x*32*s,oy+state.player.y*32*s,s);
  document.querySelectorAll('[data-zoom]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.zoom===String(zoom))));
  document.getElementById('status').textContent=`${state.turns}턴 · ${state.player.x},${state.player.y} · ${state.message}`;
  const entry=manifest.maps[sample];document.getElementById('meta').textContent=`${entry.name} · 시드${map.seed} · 실제 생성 ${map.width}×${map.height} · ${entry.forced?'시설 지정 검토 표본':'정상 출현표로 생성'} · 벽92/문101/시설106 엔진 적용`;
 }
 function reset(p,message){stop();state={player:{...p},opened:new Set(),explored:new Uint8Array(map.width*map.height),knownOpen:new Uint8Array(map.width*map.height),turns:0,message};oracle.value='';document.getElementById('oracleStatus').textContent='';draw()}
 function stairStart(){for(let y=0;y<map.height;y++)for(let x=0;x<map.width;x++)if(cell(x,y)==='<'){reset({x,y},'계단에서 시작');return}reset({x:probe.frames[0].player[0],y:probe.frames[0].player[1]},'검토 시작')}
 function facilityStart(){if(!map.origin)return stairStart();const o=map.origin;for(let x=o.x;x<o.x+o.width;x++)if('.+'.includes(cell(x,o.y+o.height-1))&&pass(x,o.y+o.height)){reset({x,y:o.y+o.height},'시설 입구 앞에서 시작');return}throw Error('Native facility entrance missing')}
 function move(dx,dy,auto=false){if(!auto)stop();const nx=state.player.x+dx,ny=state.player.y+dy;
  if(!canStep(state.player.x,state.player.y,nx,ny)){state.message='벽·소품·울타리가 막고 있습니다.';draw();return false}
  if(document.getElementById('actors').checked&&(probe.actors||[]).some(a=>a.kind==='monster'&&a.x===nx&&a.y===ny)){state.message='표시용 몬스터가 있는 칸입니다.';draw();return false}
  const k=key(nx,ny);if(cell(nx,ny)==='+'&&!state.opened.has(k)){for(const [x,y] of map.doors.find(d=>d.x===nx&&d.y===ny).linked)state.opened.add(key(x,y));state.message='문을 열었습니다.'}else{state.player={x:nx,y:ny};state.message='실제 생성 지형을 이동하는 중입니다.'}
  state.turns++;oracle.value='';document.getElementById('oracleStatus').textContent='';draw();return true;
 }
 function route(target,knownOnly=true){if(!pass(target.x,target.y))return[];const from=state.player,queue=[from],prev=new Map([[key(from.x,from.y),null]]),end=key(target.x,target.y);
  for(let i=0;i<queue.length&&!prev.has(end);i++)for(const[dx,dy]of dirs){const p=queue[i],n={x:p.x+dx,y:p.y+dy},k=key(n.x,n.y);if(!prev.has(k)&&canStep(p.x,p.y,n.x,n.y)&&(!knownOnly||state.explored[n.y*map.width+n.x])){queue.push(n);prev.set(k,p)}}
  if(!prev.has(end))return[];const path=[];for(let p=target;p;p=prev.get(key(p.x,p.y)))path.push(p);return path.reverse();
 }
 function oracleFrame(index){const f=probe.frames[index];reset({x:f.player[0],y:f.player[1]},'네이티브 시야 대조');
  for(const d of map.doors)if(f.opacity[d.y][d.x]==='0')state.opened.add(key(d.x,d.y));
  const seen=visible();let mismatches=0;for(let i=0;i<seen.length;i++)if(seen[i]!==Number(f.visible[Math.floor(i/map.width)][i%map.width]))mismatches++;
  oracle.value=String(index);document.getElementById('oracleStatus').textContent=`${f.label} · 네이티브와 다른 칸 ${mismatches}개`;draw();return mismatches;
 }
 async function load(){stop();window.ready=false;const pending=++request,entry=manifest.maps[sample];const [m,p]=await Promise.all([fetch(entry.file).then(r=>r.json()),fetch(entry.probe).then(r=>r.json())]);if(pending!==request)return;
  map=m;probe=p;oracle.replaceChildren(new Option('직접 이동',''),...p.frames.map((f,i)=>new Option(`${i+1} · ${f.label} (${f.player})`,i)));
  document.getElementById('facilityStart').disabled=!map.origin;document.getElementById('actorScene').disabled=!probe.actors;
  facilityStart();window.ready=true;
 }
 document.querySelectorAll('[data-zoom]').forEach(b=>b.onclick=()=>{zoom=b.dataset.zoom==='fit'?'fit':Number(b.dataset.zoom);draw()});
 document.querySelectorAll('[data-move]').forEach(b=>b.onclick=()=>move(...b.dataset.move.split(',').map(Number)));
 select.onchange=()=>{sample=Number(select.value);load()};oracle.onchange=()=>{if(oracle.value!=='')oracleFrame(Number(oracle.value))};
 document.getElementById('fog').onchange=draw;document.getElementById('actors').onchange=draw;document.getElementById('stairStart').onclick=stairStart;document.getElementById('facilityStart').onclick=facilityStart;
 document.getElementById('actorScene').onclick=()=>{const p=probe.actors.find(a=>a.kind==='player');reset(p,'네이티브 표시용 몬스터·아이템 배치');document.getElementById('actors').checked=true;draw()};
 document.getElementById('stop').onclick=stop;document.getElementById('closeDoor').onclick=()=>{const d=dirs.map(([dx,dy])=>({x:state.player.x+dx,y:state.player.y+dy})).find(p=>state.opened.has(key(p.x,p.y)));if(d){for(const [x,y] of map.doors.find(a=>a.x===d.x&&a.y===d.y).linked)state.opened.delete(key(x,y));state.turns++;state.message='문을 닫았습니다.';draw()}};
 const keys={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1],a:[-1,0],d:[1,0],w:[0,-1],s:[0,1],q:[-1,-1],e:[1,-1],z:[-1,1],c:[1,1]};addEventListener('keydown',e=>{if(e.key==='Escape')stop();if(keys[e.key]&&!['SELECT','INPUT'].includes(document.activeElement.tagName)){e.preventDefault();move(...keys[e.key])}});
 canvas.onclick=e=>{canvas.focus();stop();const r=canvas.getBoundingClientRect(),x=Math.floor(((e.clientX-r.left)*canvas.width/r.width-view.ox)/view.s/32),y=Math.floor(((e.clientY-r.top)*canvas.height/r.height-view.oy)/view.s/32);const tick=()=>{const next=route({x,y})[1];if(next&&move(next.x-state.player.x,next.y-state.player.y,true))timer=setTimeout(tick,100)};tick()};
 const resize=()=>{canvas.width=Math.max(280,Math.min(1440,Math.round(canvas.getBoundingClientRect().width)));canvas.height=Math.max(420,Math.min(900,innerHeight-265));draw()};addEventListener('resize',resize);resize();
 window.play107={getMap:()=>map,getProbe:()=>probe,getState:()=>({player:{...state.player},turns:state.turns,opened:[...state.opened],explored:[...state.explored]}),getView:()=>view,move,route,oracleFrame,reset,visible,pass,manifest};await load();
})().catch(e=>{document.getElementById('status').textContent=e.message;throw e});
