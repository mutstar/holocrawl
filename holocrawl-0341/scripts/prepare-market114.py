"""Restore detailed source designs and allow real multi-cell floor furniture."""
from pathlib import Path
import shutil,json,hashlib
R=Path(__file__).resolve().parents[1];S=R/'preview/city-market112';O=R/'preview/city-market114';O.mkdir(exist_ok=True)
names=['index.html','app.js','style.css','material108.js','wall92.json','wear109.js','wear110.js','scene112.js','generator.js','market-profiles.js','members.js','merch-catalog.js','market-stock.js','market-generator.js','visibility-paths.js','visibility.js','random-floor.js']
for n in names:shutil.copy2(S/n,O/n)
shutil.copy2(R/'preview/city-market03/pixel-reducer.js',O/'pixel-reducer.js')
p=O/'index.html';s=p.read_text(encoding='utf-8').replace('벽과 소품의 연결 시안112','원래 디자인·다칸 소품 시안114').replace('상점가112 ·','상점가114 ·')
s=s.replace('진열장은 콘크리트에 매립하고, 바닥 소품은 접지 그림자를 더한 연결 시안입니다. 디자인과 지형은 유지했습니다.','기존 원화의 디자인과 디테일을 살리고 1×1·2×1·2×2 소품을 섞었습니다. 큰 가구와 상자 더미가 실제 통로를 막는 범위도 함께 검사합니다. 매립 진열장은 유지했습니다.')
s=s.replace('<div class="reviewbar">','<div class="reviewbar"><label><input type="checkbox" id="compact112"> 한 칸 배치112 비교</label>')
s=s.replace('<script src="market-generator.js"></script>','<script src="market-generator.js"></script><script src="layout114.js"></script>')
s=s.replace('<script src="scene112.js"></script>','<script src="scene112.js"></script><script src="pixel-reducer.js"></script><script src="scene114.js"></script>').replace('app.js?v=112','app.js?v=114');p.write_text(s,encoding='utf-8')
p=O/'app.js';s=p.read_text(encoding='utf-8').replace('Scene112.draw(ctx,prop,map,images,t,stockMix)','Scene114.draw(ctx,prop,map,images,t,stockMix)')
s=s.replace('for(const prop of map.marketProps)Scene114','for(const prop of [...map.marketProps].sort((a,b)=>(a.y+(a.footH||1))-(b.y+(b.footH||1))))Scene114')
s=s.replace('Promise.all([Market108.load(),','Promise.all([Scene114.load(),Market108.load(),')
s=s.replace('map=MarketGen.generate(seed,marketFloor,$("exitMode").value);','map=MarketGen.generate(seed,marketFloor,$("exitMode").value,$("compact112").checked);')
s=s.replace('map.marketProps.find(p=>p.x===x&&p.y===y)','map.marketProps.find(p=>x>=p.x&&x<p.x+(p.footW||1)&&y>=p.y&&y<p.y+(p.footH||1))')
s+='\ndocument.getElementById("compact112").onchange=()=>{newMap(document.getElementById("seed").value);};\n';p.write_text(s,encoding='utf-8')
(O/'inputs.json').write_text(json.dumps({'revision':114,'previous':112,'sourceFiles':{n:hashlib.sha256((S/n).read_bytes()).hexdigest() for n in names},'geometryChange':'Floor prop occupancy grows; walls/stairs stay fixed','nativeIntegrated':False},indent=2)+'\n')
print('Prepared original-design multi-cell114 study.')
