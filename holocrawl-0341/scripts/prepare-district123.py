from pathlib import Path
import shutil,json,hashlib
R=Path(__file__).resolve().parents[1];A=R/'preview/district-contrast123'
for kind in ['street','market']:
 S=R/f'preview/city-{kind}122';O=R/f'preview/city-{kind}123';O.mkdir(exist_ok=True)
 for p in S.iterdir():
  if p.suffix in ['.js','.json','.html','.css'] and p.name not in ['validation.json','inputs.json']:shutil.copy2(p,O/p.name)
 p=O/'index.html';s=p.read_text(encoding='utf-8').replace('22픽셀 벽 기준 구조물 정리122','깔끔한 거리와 밀집 상점가123').replace('city-street122','city-street123').replace('city-market122','city-market123').replace('review122.js','review123.js').replace('app.js?v=122','app.js?v=123').replace('상점가122','상점가123')
 if kind=='street':
  s=s.replace('<script src="ambient118.js"></script>','<script src="ambient118.js"></script><script src="../district-contrast123/clean123.js"></script>')
  s=s.replace('모든 일반 벽의 세로 면을22픽셀로 통일해 ㄱ자와 모서리를 같은 높이로 연결하는 비교 시안입니다.','벽은22픽셀 그대로입니다. 설비2~3곳과 소수의 진열창만 남긴 깔끔한 초반 거리입니다.')
  code=(S/'review122.js').read_text(encoding='utf-8').replace('play122','play123').replace('구조물122','거리 구분123')
  code=code.replace("ambient.walls.find(a=>a.type==='acrylic-window'):","(ambient.walls.find(a=>a.type==='acrylic-window')||ambient.walls[0]):")
  (O/'review123.js').write_text(code,encoding='utf-8');(O/'review122.js').unlink()
  p=O/'manifest.json';m=json.loads(p.read_text(encoding='utf-8'));m['revision']=123;m['ambientRevision']=123;p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 else:
  s=s.replace('<script src="../wall-structures122/market122.js"></script>','<script src="../wall-structures122/market122.js"></script><script src="../district-contrast123/market123.js"></script>')
  s=s.replace('진열장 뒤만 솟는 부분 없이 같은 마감선으로 연결합니다.','벽은 유지하면서 진열장과 셔터가 연속되는 상점 전면을 늘렸습니다.')
 s=s.replace('<footer>','<footer>배치 구분123 · 벽121(22px)·구조물122 아트 유지 · ',1)
 p=O/'index.html';p.write_text(s,encoding='utf-8')
inputs={'revision':123,'nativeIntegrated':False,'wallBaseline':121,'structureArt':122,'wallAndFloorTerrainChanged':False,'sourceFiles':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for n in ['city-street122','city-market122','wall-structures122','wall-height121'] for p in (R/'preview'/n).iterdir() if p.suffix in ['.js','.json','.html','.css','.png']}}
(A/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n',encoding='utf-8')
print('Prepared clean street123 and denser shopping123; approved walls/art preserved.')
