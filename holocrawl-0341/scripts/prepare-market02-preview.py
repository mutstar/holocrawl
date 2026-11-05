from pathlib import Path
import shutil

r=Path(__file__).resolve().parents[1];src=r/'preview/city-market01';out=r/'preview/city-market02';out.mkdir(exist_ok=True)
for n in ['generator.js','market-profiles.js','style.css','visibility.js','visibility-paths.js','random-floor.js']:shutil.copy2(src/n,out/n)
shutil.copytree(src/'assets',out/'assets',dirs_exist_ok=True)
s=(src/'app.js').read_text(encoding='utf-8').replace('marketFloor=4;','marketFloor=4,stockMix=0;')
at=s.index('const loadImage=')
s=s[:at]+"Object.assign(sources,Object.fromEntries(MerchCatalog.map(p=>[p.id,p.file])),Object.fromEntries(MarketMembers.map(m=>['member-'+m.id,m.image])));\n"+s[at:]
old="for(const shop of map.marketWalls){if(shop.closed){ctx.drawImage(images.marketfront,0,0,32,32,shop.x*t,shop.y*t,t,t);ctx.drawImage(images.marketfront,0,0,32,32,(shop.x+1)*t,shop.y*t,t,t);}else ctx.drawImage(images.marketfront,shop.x*t,shop.y*t,2*t,t);}"
assert old in s;s=s.replace(old,'for(const shop of map.marketWalls)MarketStock.draw(ctx,shop,map,images,t,stockMix);')
s=s.replace('for(const prop of map.marketProps){ctx.drawImage(images[prop.type],prop.x*t,prop.y*t,t,t);}','for(const prop of map.marketProps)MarketStock.draw(ctx,prop,map,images,t,stockMix);')
s=s.replace("floorVariants=RandomFloor.variants(images.floor);", "MarketStock.makeSprites(images);MarketStock.gallery(images);floorVariants=RandomFloor.variants(images.floor);")
s=s.replace("$('floorCode').textContent=map.seed+' / '+marketFloor+'층 / 바닥 '+floorMix;","$('floorCode').textContent=map.seed+' / '+marketFloor+'층 / 바닥 '+floorMix+' / 상품 '+stockMix;")
s=s.replace('getState:()=>({marketFloor,','getState:()=>({stockMix,stock:map?[...map.marketWalls,...map.marketProps].filter(p=>[\'acrylic-window\',\'acrylic-rack\',\'shirt-window\',\'shirt-stack\'].includes(p.type)).map(p=>({...p,members:MarketStock.select(map.seed,marketFloor,p,stockMix)})):[],marketFloor,')
s=s.replace('window.previewApp={setMarketFloor,',"function setStockMix(value){if(!Number.isSafeInteger(value)||value<0)throw Error('Invalid stock mix');stockMix=value;draw();} $('shuffleStock').onclick=()=>{setStockMix(stockMix+1);$('message').textContent='아크릴과 티셔츠 조합만 다시 뽑았어요. 지도와 소품 위치는 그대로예요.';};\ncanvas.addEventListener('mousemove',event=>{if(!map)return;const r=canvas.getBoundingClientRect(),sx=(event.clientX-r.left)*canvas.width/r.width,sy=(event.clientY-r.top)*canvas.height/r.height,{t,ox,oy,cx,cy}=transform,x=Math.floor((sx-ox)/t)+cx,y=Math.floor((sy-oy)/t)+cy;const fixture=map.marketProps.find(p=>p.x===x&&p.y===y)||map.marketWalls.find(p=>p.y===y&&x>=p.x&&x<p.x+2);$('stockInfo').textContent=fixture?MarketStock.describe(fixture,map,stockMix):'진열품 위에 마우스를 올리면 멤버 이름이 나와요.';});\nwindow.previewApp={setStockMix,setMarketFloor,")
s=s.replace('멀리 떨어진 출구와 적·보상을 배치하고 연결 상태를 검사해요.','멀리 떨어진 계단과 시작점을 놓고 길 연결을 검사해요.')
s=s.replace('window.previewApp={setStockMix,',(r/'scripts/templates/market02-interactions.js').read_text(encoding='utf-8')+'\nwindow.previewApp={showMerchType,setStockMix,')
s=s.replace('window.previewReady=true;',"if(location.hash==='#acrylic')showMerchType('acrylic-window');window.previewReady=true;")
(out/'app.js').write_text(s,encoding='utf-8')
html=(src/'index.html').read_text(encoding='utf-8')
html=html.replace('잔향도시 · 굿즈 상점가','잔향도시 · 상점가 소품20종')
html=html.replace('4~7층의 거리 구성을 비교해보세요.','진열장·상품 더미·배송·쓰레기 소품20종과 멤버별 랜덤 굿즈를 배치합니다.')
html=html.replace('<button id="shuffleFloor">','<button id="shuffleStock">진열 멤버만 다시 뽑기</button><button id="shuffleFloor">')
html=html.replace('<button id="marketView">','<button id="acrylicView">아크릴 진열 보기</button><button id="shirtView">티셔츠 진열 보기</button><button id="trashView">쓰레기 소품 보기</button><button id="marketView">')
html=html.replace('<div class="workbench">','<div id="stockInfo" class="stock-info">진열품 위에 마우스를 올리면 멤버 이름이 나와요.</div><div class="workbench">')
start=html.index('<section class="card"><h2>상점가 새 도트</h2>');end=html.index('<section class="card"><h2>시멘트 타일 조합</h2>',start)
html=html[:start]+'''<section class="card"><h2>벽·소품20종</h2><p>아크릴은 진열대마다 중복 없는3명, 티셔츠는 멤버별 대표색으로 구성됩니다.</p><p>굿즈 멤버 <b id="memberCount"></b> · 졸업·활동 종료 포함</p><a class="catalog-link" href="catalog.html">소품·전체 멤버 크게 보기 →</a><div id="propSwatches"></div></section>'''+html[end:]
html=html.replace('<script src="market-profiles.js"></script>','<script src="market-profiles.js"></script><script src="members.js"></script><script src="merch-catalog.js"></script><script src="market-stock.js"></script>')
html=html.replace('app.js?v=market01','app.js?v=market02')
html=html.replace('<div id="propSwatches"></div>','<details><summary>소품20종 목록 펼치기</summary><div id="propSwatches"></div></details>')
(out/'index.html').write_text(html,encoding='utf-8')
with(out/'style.css').open('a',encoding='utf-8')as f:f.write('\n.stock-info{min-height:42px;margin:12px 0;padding:10px 12px;background:#20272a;border:1px solid #414b4e;border-radius:5px;font-size:12px;color:#d5ddd9}#propSwatches{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:12px}#propSwatches figure{margin:0;padding:5px;background:#484946;text-align:center;min-width:0}#propSwatches canvas{width:100%;max-width:128px;height:64px;object-fit:contain;image-rendering:pixelated}#propSwatches figcaption{font-size:10px;color:#ecebe6;margin-top:4px}.catalog-link{font-size:12px;color:#abd3d0;line-height:2}\n')
print('Prepared market02 browser with20 fixtures and random member merchandise.')
