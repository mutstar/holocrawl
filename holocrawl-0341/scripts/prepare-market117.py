"""Keep115 scale; fix only shopping-bag contact and clothing displays."""
from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parents[1];S=R/'preview/city-market115';O=R/'preview/city-market117';O.mkdir(exist_ok=True)
names=['index.html','app.js','style.css','material108.js','wall92.json','wear109.js','wear110.js','scene112.js','scene115.js','layout115.js','pixel-reducer.js','generator.js','market-profiles.js','members.js','merch-catalog.js','market-stock.js','market-generator.js','visibility-paths.js','visibility.js','random-floor.js']
for n in names:shutil.copy2(S/n,O/n)
p=O/'index.html';s=p.read_text(encoding='utf-8').replace('캐릭터에 맞춘 소품 크기115','쇼핑백 접지·의류 진열 수정117').replace('상점가115 ·','상점가117 ·').replace('scene115.js','scene117.js').replace('app.js?v=115','app.js?v=117')
s=s.replace('32픽셀 캐릭터 옆에서 진열대·상자 더미를 작게 조정했습니다. 원래 디자인과 매립 진열장은 유지하고, 낮은 2×1 진열대와 1×1 상자를 섞었습니다.','쇼핑백은 바닥 접촉부에 그림자를 붙이고, 티셔츠·후드는 원래 의류 면에 멤버색을 입혔습니다. 기존 크기와 다른 소품의 그림자는 유지합니다.')
p.write_text(s,encoding='utf-8')
p=O/'app.js';p.write_text(p.read_text(encoding='utf-8').replace('Scene115','Scene117'),encoding='utf-8')
(O/'inputs.json').write_text(json.dumps({'revision':117,'previous':115,'sourceFiles':{n:hashlib.sha256((S/n).read_bytes()).hexdigest() for n in names},'targets':['shopping-bags','shirt-stack','hoodie-rack'],'geometryChanged':False,'nativeIntegrated':False},indent=2)+'\n')
print('Prepared targeted contact/clothing117 fixes;115 preserved.')
