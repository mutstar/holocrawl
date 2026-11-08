"""Preserve109 and prepare varied fracture-pattern review110."""
from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parents[1];S=R/'preview/city-market109';O=R/'preview/city-market110';O.mkdir(exist_ok=True)
names=['index.html','app.js','style.css','material108.js','wall92.json','wear109.js','generator.js','market-profiles.js','members.js','merch-catalog.js','market-stock.js','market-generator.js','visibility-paths.js','visibility.js','random-floor.js']
for n in names:shutil.copy2(S/n,O/n)
p=O/'index.html';s=p.read_text(encoding='utf-8').replace('점점 낡아가는 상점가109','불규칙한 균열의 상점가110').replace('상점가109 ·','상점가110 ·')
s=s.replace('<div class="reviewbar">','<div class="reviewbar"><label><input type="checkbox" id="patternBefore109"> 균열 패턴 수정 전109</label>')
s=s.replace('<script src="wear109.js"></script>','<script src="wear109.js"></script><script src="wear110.js"></script>').replace('app.js?v=109','app.js?v=110')
s=s.replace('4층의 가는 잔균열부터 7층의 길어진 균열·작은 모서리 마모까지, 안쪽으로 갈수록 벽이 조금씩 낡아집니다. 바닥과 굿즈 색상은 그대로입니다.','가는 실금·불규칙한 긴 금·가지형 균열·좁은 틈을 섞었습니다. 방향과 길이, 갈라지는 위치도 달라지고, 4층에서 7층으로 갈수록 낡아집니다.')
p.write_text(s,encoding='utf-8')
p=O/'app.js';s=p.read_text(encoding='utf-8').replace('Wear109.draw(ctx,map,t,marketFloor,hash);','(document.getElementById("patternBefore109").checked?Wear109:Wear110).draw(ctx,map,t,marketFloor,hash);').replace('["noWear","wearLevel"]','["noWear","wearLevel","patternBefore109"]');p.write_text(s,encoding='utf-8')
(O/'inputs.json').write_text(json.dumps({'revision':110,'previous':109,'sourceFiles':{n:hashlib.sha256((S/n).read_bytes()).hexdigest() for n in names},'geometryChanged':False,'nativeIntegrated':False},indent=2)+'\n')
print('Prepared varied fracture review110, preserving109.')
