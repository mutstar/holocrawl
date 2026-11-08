"""Create a reversible scene-integration study, retaining110 art and geometry."""
from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parents[1];S=R/'preview/city-market110';O=R/'preview/city-market112';O.mkdir(exist_ok=True)
names=['index.html','app.js','style.css','material108.js','wall92.json','wear109.js','wear110.js','generator.js','market-profiles.js','members.js','merch-catalog.js','market-stock.js','market-generator.js','visibility-paths.js','visibility.js','random-floor.js']
for n in names:shutil.copy2(S/n,O/n)
p=O/'index.html';s=p.read_text(encoding='utf-8').replace('불규칙한 균열의 상점가110','벽과 소품의 연결 시안112').replace('상점가110 ·','상점가112 ·')
s=s.replace('<div class="reviewbar">','<div class="reviewbar"><label><input type="checkbox" id="beforeScene112"> 배치 수정 전110</label>')
s=s.replace('<script src="market-stock.js"></script>','<script src="market-stock.js"></script><script src="scene112.js"></script>').replace('app.js?v=110','app.js?v=112')
s=s.replace('가는 실금·불규칙한 긴 금·가지형 균열·좁은 틈을 섞었습니다. 방향과 길이, 갈라지는 위치도 달라지고, 4층에서 7층으로 갈수록 낡아집니다.','진열장은 콘크리트에 매립하고, 바닥 소품은 접지 그림자를 더한 연결 시안입니다. 디자인과 지형은 유지했습니다.')
p.write_text(s,encoding='utf-8')
p=O/'app.js';s=p.read_text(encoding='utf-8').replace('MarketStock.draw(ctx,shop,map,images,t,stockMix)','Scene112.draw(ctx,shop,map,images,t,stockMix)').replace('MarketStock.draw(ctx,prop,map,images,t,stockMix)','Scene112.draw(ctx,prop,map,images,t,stockMix)')
s=s.replace('["noWear","wearLevel","patternBefore109"]','["noWear","wearLevel","patternBefore109","beforeScene112"]');p.write_text(s,encoding='utf-8')
(O/'inputs.json').write_text(json.dumps({'revision':112,'previous':110,'sourceFiles':{n:hashlib.sha256((S/n).read_bytes()).hexdigest() for n in names},'geometryChanged':False,'nativeIntegrated':False},indent=2)+'\n')
print('Prepared reversible scene-integration112 study.')
