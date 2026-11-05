from pathlib import Path
import shutil

root=Path(__file__).resolve().parents[1]
src=root/'preview/native-door09'
dst=root/'preview/native-door10'
dst.mkdir(exist_ok=True)
for name in ['native-maps.js','native-maps.json','app.js','index.html','style.css','art-manifest.json']:
    shutil.copy2(src/name,dst/name)
shutil.copytree(src/'assets',dst/'assets',dirs_exist_ok=True)
for name in ['closed_door.png','open_door.png']:
    shutil.copy2(root/'engine/upstream/crawl-ref/source/rltiles/dngn/doors'/name,dst/'assets'/('crawl-'+name))
html=(dst/'index.html').read_text(encoding='utf-8').replace('잔향도시 · 철제 방화문','잔향도시 · 문 비율과 콘크리트 벽')
html=html.replace('<h1>시멘트 벽에 붙는 철제 방화문</h1><p>작은 은빛 가로 손잡이와 회색 철제 문틀. <b>32×32 도트</b>로 닫힌 문·열린 문을 비교해 보세요.</p>','<h1>문은 조금 좁게, 벽은 반복을 줄여서</h1><p>돌죽 원본 문과 이전 방화문을 비교합니다. 새 문은 <b>폭24 · 높이30픽셀</b>로 조정하고, 양옆 문설주를 벽에 붙였습니다.</p>')
html=html.replace('이전 · 임시 문','돌죽 0.34.1 · 원본').replace('새 문 · 닫힘','이전 방화문 · 폭32').replace('새 문 · 열림','조정한 방화문 · 폭24')
html=html.replace('같은 원본 지형 · 같은 위치 · 2배 확대 / 문만 바꾼 비교입니다.','같은 원본 지형 · 같은 위치 · 2배 확대 / 문을 열면 위 비교도 함께 바뀝니다.')
html=html.replace('<section class="viewer">','<section class="wall-review"><h2>긴 벽면 비교</h2><div class="wall-grid"><article><h3>이전 · 매 칸 같은 패널</h3><canvas id="wallBefore" width="512" height="96"></canvas></article><article><h3>수정 · 이어지는 콘크리트</h3><canvas id="wallAfter" width="512" height="96"></canvas></article></div><p class="caption">네모 테두리를 매 칸 반복하지 않고, 줄눈은 몇 칸 간격으로 드문드문 넣었습니다.</p></section><section class="viewer">',1)
html=html.replace('이전 임시 문 비교','이전 폭32 문 비교').replace('<button id="overview">','<button id="wallStyle">이전 벽면 비교</button><button id="overview">')
html=html.replace('원본 지도에 철제 방화문을 배치한 모습','원본 지도에 폭을 줄인 문과 콘크리트 벽을 배치한 모습')
html=html.replace('문 열림은 모양 확인용이며 게임 행동과 아직 연결하지 않았습니다.','문 열림은 모양 확인용이며 게임 행동과 아직 연결하지 않았습니다. 원본 돌죽 문은 비교용으로만 표시합니다.')
html=html.replace('src="app.js"','src="app.js?v=door10"')
(dst/'index.html').write_text(html,encoding='utf-8')
css=(dst/'style.css').read_text(encoding='utf-8').replace('.comparisons canvas{display:block;width:100%;height:auto;image-rendering:pixelated}', '.comparisons canvas{display:block;width:320px;max-width:100%;height:auto;margin:auto;image-rendering:pixelated}')
css+='\n.wall-review{margin:25px 0;padding:16px;background:#202a27;border:1px solid #526b60;border-radius:6px}.wall-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.wall-grid article{min-width:0}.wall-grid h3{font-size:13px;font-weight:500;color:#b9c7bd}.wall-grid canvas{display:block;width:512px;max-width:100%;height:auto;image-rendering:pixelated}@media(max-width:1000px){.wall-grid{grid-template-columns:1fr}}\n'
(dst/'style.css').write_text(css,encoding='utf-8')
print('Prepared door10 comparison, preserved09 and native terrain.')
