"""Reduce114 furniture against the unchanged32px player reference."""
from pathlib import Path
import shutil,json,hashlib
R=Path(__file__).resolve().parents[1];S=R/'preview/city-market114';O=R/'preview/city-market115';O.mkdir(exist_ok=True)
names=['index.html','app.js','style.css','material108.js','wall92.json','wear109.js','wear110.js','scene112.js','scene114.js','layout114.js','pixel-reducer.js','generator.js','market-profiles.js','members.js','merch-catalog.js','market-stock.js','market-generator.js','visibility-paths.js','visibility.js','random-floor.js']
for n in names:shutil.copy2(S/n,O/n)
p=O/'layout114.js';s=p.read_text(encoding='utf-8').replace("'acrylic-rack':[2,2]","'acrylic-rack':[2,1]").replace("'hoodie-rack':[2,2]","'hoodie-rack':[2,1]").replace("'delivery-boxes':[2,2]","'delivery-boxes':[1,1]").replace("'delivery-cart':[2,2]","'delivery-cart':[1,1]").replace('multicell114','multicell115');(O/'layout115.js').write_text(s,encoding='utf-8')
p=O/'scene114.js';s=p.read_text(encoding='utf-8').replace('Scene114','Scene115')
s=s.replace(' function design(id,fw,fh){'," const caps={'acrylic-rack':[40,27],'hoodie-rack':[40,27],'delivery-boxes':[26,24],'delivery-cart':[26,24],'shirt-stack':[38,22],'badge-trays':[38,23],'plush-basket':[38,23],'open-carton':[30,23],'folding-crates':[40,24],'recycling-bins':[40,25]};\n function design(id,fw,fh){")
old='scale=Math.min((W-6)/bounds.w,(H-8)/bounds.h),w='
new='limit=caps[id]||[W-6,H-8],scale=Math.min(Math.min(W-6,limit[0])/bounds.w,Math.min(H-5,limit[1])/bounds.h),w='
assert old in s;s=s.replace(old,new);(O/'scene115.js').write_text(s,encoding='utf-8')
p=O/'app.js';s=p.read_text(encoding='utf-8').replace('Scene114','Scene115');p.write_text(s,encoding='utf-8')
p=O/'index.html';s=p.read_text(encoding='utf-8').replace('원래 디자인·다칸 소품 시안114','캐릭터에 맞춘 소품 크기115').replace('상점가114 ·','상점가115 ·').replace('scene114.js','scene115.js').replace('layout114.js','layout115.js').replace('app.js?v=114','app.js?v=115')
s=s.replace('기존 원화의 디자인과 디테일을 살리고 1×1·2×1·2×2 소품을 섞었습니다. 큰 가구와 상자 더미가 실제 통로를 막는 범위도 함께 검사합니다. 매립 진열장은 유지했습니다.','32픽셀 캐릭터 옆에서 진열대·상자 더미를 작게 조정했습니다. 원래 디자인과 매립 진열장은 유지하고, 낮은 2×1 진열대와 1×1 상자를 섞었습니다.')
p.write_text(s,encoding='utf-8')
(O/'inputs.json').write_text(json.dumps({'revision':115,'previous':114,'sourceFiles':{n:hashlib.sha256((S/n).read_bytes()).hexdigest() for n in names},'nativeIntegrated':False,'playerChanged':False},indent=2)+'\n')
print('Prepared player-relative size115; detailed source art preserved.')
