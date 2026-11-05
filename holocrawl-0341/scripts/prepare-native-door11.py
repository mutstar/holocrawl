from pathlib import Path
import shutil,re

root=Path(__file__).resolve().parents[1]
src=root/'preview/native-door10';dst=root/'preview/native-door11';dst.mkdir(exist_ok=True)
for name in ['native-maps.js','native-maps.json','app.js','style.css','art-manifest.json','wall-material-manifest.json','wall-processing.json']:
    shutil.copy2(src/name,dst/name)
shutil.copytree(src/'assets',dst/'assets',dirs_exist_ok=True)
html=(src/'index.html').read_text(encoding='utf-8')
html=html.replace('잔향도시 · 문 비율과 콘크리트 벽','잔향도시 · 벽 방향과 문틀')
html=html.replace('<h1>문은 조금 좁게, 벽은 반복을 줄여서</h1><p>돌죽 원본 문과 이전 방화문을 비교합니다. 새 문은 <b>폭24 · 높이30픽셀</b>로 조정하고, 양옆 문설주를 벽에 붙였습니다.</p>','<h1>가로문은 그대로, 세로문은 벽에 맞춰서</h1><p>가로 벽의 문은 <b>폭24</b>를 유지합니다. 세로 벽의 문은 <b>폭32</b>로 채우고, 위아래 문틀과 벽 옆면을 연결했습니다.</p>')
def row(axis,title):
    cards=''.join(f'<article><h2>{label}</h2><canvas id="{name}{axis}" width="320" height="320"></canvas></article>' for name,label in [('slim','A · 기존 폭24'),('wide','B · 모두 폭32'),('fit','C · 벽 방향에 맞춤')])
    return f'<section id="{axis}Comparisons" class="orientation-review"><h2>{title}</h2><div class="comparisons">{cards}</div></section>'
html=re.sub(r'<section id="doorComparisons".*?</section>',row('horizontal','가로 벽의 문 · 위아래로 통과')+row('vertical','세로 벽의 문 · 좌우로 통과'),html,count=1)
html=html.replace('같은 원본 지형 · 같은 위치 · 2배 확대 / 문을 열면 위 비교도 함께 바뀝니다.','같은 위치에서 문 폭과 벽 연결만 비교합니다. 각 줄의 그림을 누르면 해당 문을 지도에서 볼 수 있어요.')
html=re.sub(r'<section class="wall-review">.*?</section>','',html,count=1)
html=html.replace('<button id="nextDoor">','<label for="doorMode">문 표시</label><select id="doorMode"><option value="fit">C · 벽 방향에 맞춤</option><option value="slim">A · 기존 폭24</option><option value="wide">B · 모두 폭32</option></select><button id="horizontalFocus">가로문 보기</button><button id="verticalFocus">세로문 보기</button><button id="nextDoor">')
html=re.sub(r'<button id="legacy">.*?</button>','',html,count=1)
html=html.replace('원본 지도에 폭을 줄인 문과 콘크리트 벽을 배치한 모습','원본 지도에 벽 방향에 맞는 문과 문틀을 배치한 모습')
html=html.replace('원본 돌죽 문은 비교용으로만 표시합니다.','')
html=html.replace('<a href="../native-layout08/">원본 지도 6개 비교</a>','<a href="../native-door10/">이전 문 폭·돌죽 원본 비교</a>')
html=html.replace('app.js?v=door10','app.js?v=door11')
(dst/'index.html').write_text(html,encoding='utf-8')
css=(dst/'style.css').read_text(encoding='utf-8')+'\n.orientation-review{margin-top:26px}.orientation-review>h2{font-size:18px;margin:0}.orientation-review .comparisons{margin-top:12px}.orientation-review canvas{cursor:pointer}.comparisons article:nth-child(2){border-color:#526b60}.comparisons article:nth-child(3){border-color:#a9c494}\n'
(dst/'style.css').write_text(css,encoding='utf-8')
print('Prepared door11 orientation comparison with unchanged terrain and assets.')
