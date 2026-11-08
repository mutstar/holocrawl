"""Keep accepted112 wall insets; study coherent floor-object volumes113."""
from pathlib import Path
import shutil,json,hashlib
R=Path(__file__).resolve().parents[1];S=R/'preview/city-market112';O=R/'preview/city-market113';O.mkdir(exist_ok=True)
names=['index.html','app.js','style.css','material108.js','wall92.json','wear109.js','wear110.js','scene112.js','generator.js','market-profiles.js','members.js','merch-catalog.js','market-stock.js','market-generator.js','visibility-paths.js','visibility.js','random-floor.js']
for n in names:shutil.copy2(S/n,O/n)
p=O/'index.html';s=p.read_text(encoding='utf-8').replace('벽과 소품의 연결 시안112','바닥 소품의 입체·접지 시안113').replace('상점가112 ·','상점가113 ·').replace('진열장은 콘크리트에 매립하고, 바닥 소품은 접지 그림자를 더한 연결 시안입니다. 디자인과 지형은 유지했습니다.','매립 진열장은 유지하고, 바닥 소품을 같은 빛 방향·면 구성·명암 단계로 정리했습니다. 짧은 투영 그림자와 진한 접지부를 함께 표시합니다.')
s=s.replace('<div class="reviewbar">','<div class="reviewbar"><label><input type="checkbox" id="beforeFloor113"> 바닥 소품 수정 전112</label>')
s=s.replace('<script src="scene112.js"></script>','<script src="scene112.js"></script><script src="floor113.js"></script>').replace('app.js?v=112','app.js?v=113');p.write_text(s,encoding='utf-8')
p=O/'app.js';s=p.read_text(encoding='utf-8').replace('Scene112.draw','Scene113.draw').replace('"beforeScene112"]','"beforeScene112","beforeFloor113"]');p.write_text(s,encoding='utf-8')
(O/'inputs.json').write_text(json.dumps({'revision':113,'previous':112,'sourceFiles':{n:hashlib.sha256((S/n).read_bytes()).hexdigest() for n in names},'geometryChanged':False,'nativeIntegrated':False},indent=2)+'\n')
print('Prepared floor-volume113 study;112 wall renderer unchanged.')
