from pathlib import Path
import shutil,re
r=Path(__file__).resolve().parents[1];src=r/'preview/street';dst=r/'preview/street-vision01';dst.mkdir(exist_ok=True)
for name in ['generator.js','style.css']:shutil.copy2(src/name,dst/name)
shutil.copytree(src/'assets',dst/'assets',dirs_exist_ok=True)
s=(src/'app.js').read_text(encoding='utf-8-sig')
def replace(old,new):
 global s
 assert old in s,old[:100]
 s=s.replace(old,new)
replace("const G=StreetGen,stages=","const V=CrawlVisibility;let memory=null,fogEnabled=true;\nconst G=StreetGen,stages=")
replace("function visibleCells(){return stage===1?map.roomCells:stage===2?map.corridorCells:map.cells;}","function visibleCells(){return stage===1?map.roomCells:stage===2?map.corridorCells:stage===4&&fogEnabled?memory.renderCells(map.cells):map.cells;}\nfunction canSee(p){return !fogEnabled||stage!==4||Boolean(memory.visible[p.y*map.w+p.x]);}\nfunction isKnown(p){return !fogEnabled||Boolean(memory.explored[p.y*map.w+p.x]);}\nfunction pathTo(p){return fogEnabled?V.knownRoute({w:map.w,h:map.h,cells:memory.renderCells(map.cells)},player,p,memory.explored):G.route(map,player,p);}\nfunction updateVision(){const before=memory.visible;memory.update(map.cells,player);const spotted=map.enemies.some(e=>memory.visible[e.y*map.w+e.x]&&!before[e.y*map.w+e.x]);if(spotted){clearInterval(walking);walking=null;}return spotted;}\nfunction drawFog(t){if(!fogEnabled||stage!==4)return;ctx.filter='none';for(let y=0;y<map.h;y++)for(let x=0;x<map.w;x++){const i=y*map.w+x;if(!memory.explored[i]){ctx.fillStyle='#06090b';ctx.fillRect(x*t,y*t,t,t);}else if(!memory.visible[i]){ctx.fillStyle='rgba(0,0,0,.74)';ctx.fillRect(x*t,y*t,t,t);}}}")
replace("ctx.fillStyle='#100f0d';ctx.fillRect", "ctx.fillStyle='#06090b';ctx.fillRect")
replace('const path=G.route(map,player,map.exit);','const path=pathTo(map.exit);')
replace("for(const item of map.items){ctx.fillStyle=", "for(const item of map.items){if(!canSee(item))continue;ctx.fillStyle=")
replace('for(const enemy of map.enemies)ctx.drawImage(images.rat,enemy.x*t,enemy.y*t,t,t);','for(const enemy of map.enemies)if(canSee(enemy))ctx.drawImage(images.rat,enemy.x*t,enemy.y*t,t,t);')
replace('ctx.restore();drawMini(cells);updateInfo();}','drawFog(t);ctx.restore();drawMini(cells);updateInfo();}')
start=s.index('function drawMini(cells)');end=s.index('function updateInfo()',start)
s=s[:start]+'''function drawMini(cells){mc.imageSmoothingEnabled=false;const scale=Math.min(mini.width/map.w,mini.height/map.h);mc.fillStyle='#06090b';mc.fillRect(0,0,mini.width,mini.height);for(let y=0;y<map.h;y++)for(let x=0;x<map.w;x++){const i=y*map.w+x,c=cells[i];if(stage===4&&fogEnabled&&!memory.explored[i])continue;const lit=stage!==4||!fogEnabled||memory.visible[i];mc.fillStyle=c===G.FLOOR?(lit?'#8b8e7d':'#444b42'):c===G.BARRIER?(lit?'#b8b6a0':'#5d6357'):(lit?'#454c43':'#242d27');mc.fillRect(x*scale,y*scale,Math.ceil(scale),Math.ceil(scale));}if(stage===4){if(isKnown(map.upstairs)){mc.fillStyle='#9ab9db';mc.fillRect(map.upstairs.x*scale,map.upstairs.y*scale,scale,scale);}if(isKnown(map.exit)){mc.fillStyle='#eadcaa';mc.fillRect(map.exit.x*scale,map.exit.y*scale,scale,scale);}mc.fillStyle='#a7e5d6';mc.fillRect(player.x*scale,player.y*scale,scale,scale);}if(!overview){mc.strokeStyle='#859d94';mc.lineWidth=1;mc.strokeRect(transform.cx*scale,transform.cy*scale,canvas.width/transform.t*scale,canvas.height/transform.t*scale);}}
'''+s[end:]
replace("$('distance').textContent=map.validation.exitDistance+'칸 / 80×70';", "$('distance').textContent=isKnown(map.exit)?map.validation.exitDistance+'칸 / 80×70':'미발견 / 80×70';")
replace("$('path').textContent=showPath?'길 표시 끄기':'출구까지 길 표시';", "$('path').textContent=showPath?'길 표시 끄기':'발견한 출구까지 길 표시';$('fog').textContent=fogEnabled?'탐험 안개 끄기':'탐험 안개 켜기';let seen=0;for(let i=0;i<map.cells.length;i++)if(memory.explored[i]&&map.cells[i]===G.FLOOR)seen++;$('explored').textContent=(seen/map.validation.walkable*100).toFixed(1)+'%';$('visibleCount').textContent=memory.visible.reduce((a,b)=>a+b,0)+'칸';if(stage===4){$('stageTitle').textContent='시야·탐험 안개';$('stageDetail').textContent=fogEnabled?'시야7칸 · 벽 뒤는 가림 · 펜스 너머는 보임':'전체 배치 확인 모드 · 탐험 기억은 현재 시야만 갱신';}")
replace('player={...map.start};stage=4;', 'player={...map.start};memory=new V.Memory(map.w,map.h);memory.update(map.cells,player);stage=4;')
start=s.index('function move(dx,dy)');end=s.index("$('newMap').onclick",start)
s=s[:start]+'''function move(dx,dy){if(stage!==4||!Number.isInteger(dx)||!Number.isInteger(dy)||Math.max(Math.abs(dx),Math.abs(dy))!==1)return false;const x=player.x+dx,y=player.y+dy;if(x<0||y<0||x>=map.w||y>=map.h||map.cells[y*map.w+x]!==G.FLOOR){clearInterval(walking);walking=null;$('message').textContent='벽이나 펜스가 막고 있어요. 다른 길로 가보세요.';return false;}player={x,y};const spotted=updateVision();$('message').textContent=spotted?'새로운 적이 보여 자동 이동을 멈췄어요.':x===map.exit.x&&y===map.exit.y?'다음 층 입구 발견! 층 이동은 아직 연결 전이에요.':'탐험 중 · 밝은 곳만 현재 보이는 범위예요.';draw();return true;}
'''+s[end:]
replace("$('path').onclick=()=>{showPath=!showPath;draw();};", "$('path').onclick=()=>{showPath=!showPath;if(showPath&&!isKnown(map.exit))$('message').textContent='아직 출구를 발견하지 못했어요.';draw();};$('fog').onclick=()=>{fogEnabled=!fogEnabled;draw();};")
replace("if(e.target.tagName==='INPUT')return;", "if(['INPUT','SELECT','TEXTAREA'].includes(e.target.tagName))return;")
replace('const keys={ArrowUp:',"const keys={q:[-1,-1],e:[1,-1],z:[-1,1],c:[1,1],Home:[-1,-1],PageUp:[1,-1],End:[-1,1],PageDown:[1,1],'7':[-1,-1],'9':[1,-1],'1':[-1,1],'3':[1,1],'8':[0,-1],'2':[0,1],'4':[-1,0],'6':[1,0],ArrowUp:")
replace('if(keys[e.key]){e.preventDefault();clearInterval(walking);move(...keys[e.key]);}',"const direction=keys[e.key]||keys[e.key.toLowerCase()];if(direction){e.preventDefault();clearInterval(walking);move(...direction);}")
replace('const path=G.route(map,player,{x,y});',"if(fogEnabled&&!memory.explored[y*map.w+x]){$('message').textContent='아직 탐험하지 않은 곳이에요. 먼저 가까이 다가가보세요.';return;}const path=pathTo({x,y});")
replace('move(next.x-player.x,next.y-player.y);','if(!move(next.x-player.x,next.y-player.y)){clearInterval(walking);walking=null;}')
replace('player={x:choices[0].x,y:choices[0].y};draw();','player={x:choices[0].x,y:choices[0].y};updateVision();draw();')
replace('overview=false;player={...map.start};draw();','overview=false;player={...map.start};updateVision();draw();')
replace('계단과 양옆 손잡이만 있는 형태예요.','승인한 원형 계단 도트예요.')
replace('getState:()=>({seed:', 'getState:()=>({fogEnabled,visible:Array.from(memory.visible),explored:Array.from(memory.explored),visibleEnemies:map.enemies.filter(canSee),seed:')
replace('window.previewApp={showStart,','window.previewApp={setFogEnabled:value=>{fogEnabled=Boolean(value);draw();},getMap:()=>map,showStart,')
(dst/'app.js').write_text(s,encoding='utf-8')
html=(src/'index.html').read_text(encoding='utf-8-sig')
html=html.replace('잔향도시 · 손잡이 없는 원형 계단','잔향도시 · 시야와 탐험 안개').replace('80×70칸 구조와 시멘트 바닥 유지 · 조금 밝은 벽에 실외기·배관·환기구 추가','돌죽0.34.1 시선 경로 · 주변7칸부터 탐험해보세요. 벽 뒤는 가려지고 지나온 길은 어둡게 기억합니다.')
html=html.replace('<button id="newMap"','<button id="fog">탐험 안개 끄기</button><button id="newMap"')
html=html.replace('</dl>','<div><dt>현재 시야</dt><dd id="visibleCount"></dd></div><div><dt>바닥 탐험</dt><dd id="explored"></dd></div></dl>')
html=html.replace('돌죽 규모의 배치 실험','시야 확인 방법').replace('돌죽 0.24와 같은 격자 크기로 확장한 별도 생성기입니다. 돌죽 원본 생성 알고리즘을 이식한 것은 아닙니다. 길 생성·연결 검사·이동은 동작합니다. 적·보상은 배치 예시이며 전투·획득은 연결 전입니다.','검정은 미탐험, 어두운 지형은 탐험 기억, 밝은 곳은 현재 시야입니다. 적은 현재 시야 안에서만 보입니다. 안개를 꺼서 전체 배치와 비교할 수 있습니다.').replace('승인한 그림의 일부를 질감으로 사용했습니다. 최종 타일 세트와 돌죽 엔진 적용은 다음 단계입니다.','방향키·WASD로 이동합니다. Q/E/Z/C 또는 숫자패드로 대각선 이동도 가능합니다. 지도·배치 확인 버튼은 해당 위치로 이동하는 미리보기 기능입니다. 전투·층 이동은 아직 연결 전입니다.')
html=html.replace('이 번호로 생성','이 번호로 새 탐험').replace('방향키·WASD로 이동하거나, 갈 곳을 클릭하세요.','방향키·WASD / Q·E·Z·C 대각선 · 탐험한 바닥 클릭 이동')
html=html.replace('<script src="generator.js?v=upstairs08"></script>','<script src="generator.js?v=vision01"></script><script src="visibility-paths.js"></script><script src="visibility.js"></script>').replace('app.js?v=upstairs08','app.js?v=vision01')
assert 'visibility.js' in html
(dst/'index.html').write_text(html,encoding='utf-8')
print('Prepared visibility and explored-terrain preview.')
