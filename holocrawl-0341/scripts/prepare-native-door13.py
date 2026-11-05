from pathlib import Path
import shutil

root=Path(__file__).resolve().parents[1];src=root/'preview/native-door12';dst=root/'preview/native-door13';dst.mkdir(exist_ok=True)
for name in ['native-maps.js','native-maps.json','app.js','style.css','index.html','wall-material-manifest.json','wall-processing.json']:
    shutil.copy2(src/name,dst/name)
shutil.copytree(src/'assets',dst/'assets',dirs_exist_ok=True)
for state in ['closed','open']:
    shutil.copy2(src/f'assets/fire-door-{state}32.png',dst/f'assets/previous-fire-door-{state}32.png')
html=(dst/'index.html').read_text(encoding='utf-8').replace('폭을 줄여 다시 그린 철제 문','아치형 철제 양문').replace('잔향도시 · 폭을 줄여 다시 그린 문','잔향도시 · 아치형 철제 양문')
html=html.replace('세 번째 문처럼 좁고 세로로 긴 비율로 다시 그렸습니다.','회색 아치 안의 철제 문짝 두 장. 닫히면 중앙 이음선이 보이고, 열리면 양옆으로 갈라집니다.')
html=html.replace('새로 그린 좁은 철제 문을 실제 지도에 배치한 모습','아치형 철제 양문을 실제 지도에 배치한 모습')
html=html.replace('<a href="../native-door11/proportions.html">이전 세 번째 문 비율 비교</a>','<a href="../native-door12/">이전 외짝 철제 문 비교</a>')
html=html.replace('app.js?v=door12','app.js?v=door13')
(dst/'index.html').write_text(html,encoding='utf-8')
app=(dst/'app.js').read_text(encoding='utf-8').replace("closed:'assets/fire-door-closed32.png',open:'assets/fire-door-open32.png'", "closed:'assets/steel-arch-closed32.png',open:'assets/steel-arch-open32.png'")
app=app.replace('새 원화24×30 · 같은 크기','아치형 철제 양문24×30 · 같은 크기').replace('sameSpriteForBothAxes:true,','sameSpriteForBothAxes:true,doorType:\'arched-double-steel\',')
(dst/'app.js').write_text(app,encoding='utf-8')
installer=(root/'scripts/install-native-door12.cjs').read_text(encoding='utf-8').replace('native-door12','native-door13').replace('fire-door-','steel-arch-')
(root/'scripts/install-native-door13.cjs').write_text(installer,encoding='utf-8')
checks=(root/'scripts/check-native-door12.cjs').read_text(encoding='utf-8').replace('native-door12','native-door13').replace('assets/fire-door-','assets/steel-arch-').replace('redrawn-door-states.png','arched-door-states.png')
(root/'scripts/check-native-door13.cjs').write_text(checks,encoding='utf-8')
print('Prepared arched double-door13 review, preserved12.')
