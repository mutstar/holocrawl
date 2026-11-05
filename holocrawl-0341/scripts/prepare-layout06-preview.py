from pathlib import Path
import shutil,re
r=Path(__file__).resolve().parents[1];src=r/'preview/city-layout05';dst=r/'preview/city-layout06';dst.mkdir(exist_ok=True)
for name in ['members.js','members.json','market-profiles.js','market-stock.js','clean-merch.js','pixel-reducer.js','merch-catalog.js','random-floor.js','visibility.js','visibility-paths.js','style.css','catalog.html','catalog.js','legacy-generator.js','layout04-generator.js','market-generator.js']:
    shutil.copy2(src/name,dst/name)
shutil.copy2(src/'generator.js',dst/'layout05-generator.js')
shutil.copytree(src/'assets',dst/'assets',dirs_exist_ok=True)
html=(src/'index.html').read_text(encoding='utf-8').replace('불규칙하게 이어지는 거리','방과 연결 공간의 중간형')
html=re.sub(r'<select id="layoutMode">.*?</select>','<select id="layoutMode"><option value="rooms">1번 · 방과 통로</option><option value="balanced">중간형 · 이어진 구역과 짧은 골목</option><option value="connected">2번 · 넓게 이어진 공간</option></select>',html)
html=html.replace('이전2번과 연결 방식 비교','1번·중간형·2번 비교')
html=html.replace('<script src="generator.js?v=layout05"></script>','<script src="layout05-generator.js"></script><script src="generator.js?v=layout06"></script>')
html=html.replace('app.js?v=layout05','app.js?v=layout06')
(dst/'index.html').write_text(html,encoding='utf-8')
s=(src/'app.js').read_text(encoding='utf-8').replace("get('layout')||'connected'","get('layout')||'balanced'")
s=s.replace("['connected','auto','plaza','rooms','alleys','previous']","['balanced','connected','auto','plaza','rooms','alleys','previous']")
(dst/'app.js').write_text(s,encoding='utf-8')
p=dst/'market-generator.js';s=p.read_text(encoding='utf-8').replace("layoutMode='connected'","layoutMode='balanced'");p.write_text(s,encoding='utf-8')
print('Prepared middle layout06; both previous endpoints retained.')
