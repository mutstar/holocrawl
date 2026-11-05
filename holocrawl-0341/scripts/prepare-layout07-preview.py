from pathlib import Path
import shutil
r=Path(__file__).resolve().parents[1];src=r/'preview/city-layout06';dst=r/'preview/city-layout07';dst.mkdir(exist_ok=True)
for name in ['members.js','members.json','market-profiles.js','market-stock.js','clean-merch.js','pixel-reducer.js','merch-catalog.js','random-floor.js','visibility.js','visibility-paths.js','style.css','catalog.html','catalog.js','legacy-generator.js','layout04-generator.js','layout05-generator.js','market-generator.js']:
    shutil.copy2(src/name,dst/name)
shutil.copy2(src/'generator.js',dst/'layout06-generator.js');shutil.copytree(src/'assets',dst/'assets',dirs_exist_ok=True)
html=(src/'index.html').read_text(encoding='utf-8').replace('방과 연결 공간의 중간형','큰 구역과 짧은 골목')
html=html.replace('1번 · 방과 통로','A · 방과 통로').replace('중간형 · 이어진 구역과 짧은 골목','B · 큰 구역과 짧은 골목').replace('2번 · 넓게 이어진 공간','C · 넓게 이어진 공간')
html=html.replace('1번·중간형·2번 비교','A·B·C 구조 비교')
html=html.replace('<script src="generator.js?v=layout06"></script>','<script src="layout06-generator.js"></script><script src="generator.js?v=layout07"></script>').replace('app.js?v=layout06','app.js?v=layout07')
(dst/'index.html').write_text(html,encoding='utf-8');shutil.copy2(src/'app.js',dst/'app.js')
print('Prepared independent mixed-layout07 review.')
