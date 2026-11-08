"""Preserve108 and add gradual, code-rendered concrete weathering for4–7F."""
from pathlib import Path
import shutil,json,hashlib
R=Path(__file__).resolve().parents[1];S=R/'preview/city-market108';O=R/'preview/city-market109';O.mkdir(exist_ok=True)
names=['index.html','app.js','style.css','material108.js','wall92.json','generator.js','market-profiles.js','members.js','merch-catalog.js','market-stock.js','market-generator.js','visibility-paths.js','visibility.js','random-floor.js']
for name in names:shutil.copy2(S/name,O/name)
p=O/'index.html';s=p.read_text(encoding='utf-8').replace('새 콘크리트 상점가108','점점 낡아가는 상점가109')
s=s.replace('확정 콘크리트 벽과 세로창 양개문에 맞춘 4~7층 상점가 시안입니다. 진열장·셔터·물류 소품은 청회색으로 맞추고, 멤버 굿즈와 종이 상자의 색은 남겼습니다.','4층의 가는 잔균열부터 7층의 길어진 균열·작은 모서리 마모까지, 안쪽으로 갈수록 벽이 조금씩 낡아집니다. 바닥과 굿즈 색상은 그대로입니다.')
s=s.replace('<div class="reviewbar">','<div class="reviewbar"><label><input type="checkbox" id="noWear"> 균열 전108 비교</label><label for="wearLevel">벽 노후화</label><select id="wearLevel"><option value="auto">현재 층에 맞게</option><option value="4">4층 · 잔균열</option><option value="5">5층 · 갈라지는 벽</option><option value="6">6층 · 길어진 균열</option><option value="7">7층 · 금과 모서리 마모</option></select>')
s=s.replace('href="buildings.html"','href="../city-market108/buildings.html"').replace('href="catalog.html"','href="../city-market108/catalog.html"')
s=s.replace('<script src="material108.js"></script>','<script src="material108.js"></script><script src="wear109.js"></script>').replace('app.js?v=108','app.js?v=109').replace('상점가108 ·','상점가109 ·')
p.write_text(s,encoding='utf-8')
p=O/'app.js';s=p.read_text(encoding='utf-8');s=s.replace('marketFloor=4,','marketFloor=([4,5,6,7].includes(Number(new URLSearchParams(location.search).get("floor")))?Number(new URLSearchParams(location.search).get("floor")):4),',1);s=s.replace('// Existing venue artwork',"if(stage>=3&&!Market108.isOld())Wear109.draw(ctx,map,t,marketFloor,hash);\n\n// Existing venue artwork",1)
s+='\nfor(const id of ["noWear","wearLevel"])document.getElementById(id).onchange=()=>draw();\n';p.write_text(s,encoding='utf-8')
(O/'inputs.json').write_text(json.dumps({'revision':109,'previous':108,'sourceFiles':{n:hashlib.sha256((S/n).read_bytes()).hexdigest() for n in names},'geometryChanged':False,'nativeIntegrated':False},indent=2)+'\n')
print('Prepared separate gradual-weathering109 review.')
