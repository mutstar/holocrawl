from pathlib import Path
import shutil,re
root=Path(__file__).resolve().parents[1];src=root/'preview/native-door12';dst=root/'preview/native-water01';dst.mkdir(exist_ok=True)
for name in ['app.js','index.html','style.css','native-maps.js','native-maps.json']:
    shutil.copy2(src/name,dst/name)
shutil.copytree(src/'assets',dst/'assets',dirs_exist_ok=True)
html=(dst/'index.html').read_text(encoding='utf-8').replace('폭을 줄여 다시 그린 철제 문','얕은 물과 잠긴 수로').replace('잔향도시 · 폭을 줄여 다시 그린 문','잔향도시 · 물 타일')
html=html.replace('세 번째 문처럼 좁고 세로로 긴 비율로 다시 그렸습니다.<br><b>가로·세로 모두 같은 도트</b>를 사용하고, 벽에 맞춰 문틀을 연결합니다.','얕은 물은 시멘트 바닥이 비치고, 깊은 물은 짙은 청록색으로 보입니다. 물가와 깊이 경계를 함께 확인해 보세요.')
html=html.replace('<div id="newDoorStates">','<section id="waterCards" class="water-cards"><article><h2>얕은 물 · 바닥이 비치는 웅덩이</h2><canvas id="shallowDemo" width="448" height="448"></canvas></article><article><h2>깊은 물 · 얕은 물과의 경계</h2><canvas id="deepDemo" width="448" height="448"></canvas></article></section><p class="caption">위는 경계 확인용 예시 배치입니다. 아래는 원본 돌죽 생성 지형에 그대로 입힌 모습입니다.</p><div id="newDoorStates">')
html=html.replace('<label for="mapSelect">지도</label>','<button id="waterFocus">물 있는 곳 보기</button><label for="mapSelect">지도</label>').replace('app.js?v=door12','app.js?v=water01')
html=html.replace('같은 실제 문 위치에서 닫힘·열림을 2배 확대했습니다. 그림을 누르면 해당 문을 지도에서 볼 수 있어요.','물 있는 곳 보기 또는 전체 지도를 눌러 물 배치를 확인하세요.')
html=html.replace('<a href="../native-door11/proportions.html">이전 세 번째 문 비율 비교</a>','<a href="../native-door12/">확정된 네모 철제 문</a>')
(dst/'index.html').write_text(html,encoding='utf-8')
css=(dst/'style.css').read_text(encoding='utf-8')+'\n#newDoorStates,#horizontalFocus,#verticalFocus,#nextDoor,#toggleDoor{display:none}.water-cards{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:24px 0}.water-cards article{padding:16px;background:#222d2a;border:1px solid #526b60;border-radius:6px;min-width:0}.water-cards canvas{display:block;width:448px;max-width:100%;height:auto;image-rendering:pixelated}@media(max-width:850px){.water-cards{grid-template-columns:1fr}}\n'
(dst/'style.css').write_text(css,encoding='utf-8')
app=(dst/'app.js').read_text(encoding='utf-8')
app=app.replace("open:'assets/fire-door-open32.png'","open:'assets/fire-door-open32.png',shallow:'assets/water-shallow128.png',deep:'assets/water-deep128.png'")
old="if(isWater(f)){c.fillStyle=f==='deep_water'?'rgba(13,54,87,.92)':'rgba(46,108,128,.85)';c.fillRect(px,py,t,t);c.fillStyle='#6f9da5';c.fillRect(px+t*.2,py+t*.4,t*.33,Math.max(1,t/32));return;}"
app=app.replace(old,"if(isWater(f)){drawWater(c,m,gx,gy,px,py,t);return;}")
app=app.replace("comparisons();\n}","comparisons();waterDemos();\n}")
app=app.replace('select(0);window.doorPreviewReady=true;','select(1);waterFocus();window.doorPreviewReady=true;window.waterPreviewReady=true;')
(dst/'app.js').write_text(app,encoding='utf-8')
print('Prepared water01 using approved door12 and unchanged terrain.')
