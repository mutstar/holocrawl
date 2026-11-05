from pathlib import Path
import shutil

r=Path(__file__).resolve().parents[1];src=r/'preview/street-floor-random01';dst=r/'preview/city-market01';dst.mkdir(exist_ok=True)
for n in ['style.css','visibility.js','visibility-paths.js','random-floor.js']:shutil.copy2(src/n,dst/n)
shutil.copytree(src/'assets',dst/'assets',dirs_exist_ok=True)
g=(src/'generator.js').read_text(encoding='utf-8')
g=g.replace('exitMode="auto"){','exitMode="auto",profile={}){')
g=g.replace('int(5,rect.w-2),rh=int(4,rect.h-2)','int(Math.min(profile.minRoomWidth||5,rect.w-2),rect.w-2),rh=int(Math.min(profile.minRoomHeight||4,rect.h-2),rect.h-2)')
g=g.replace('for(let n=0;n<3;n++){const a=rooms','for(let n=0;n<(profile.courts??3);n++){const a=rooms')
g=g.replace('rng()<.55?3:1','rng()<(profile.wideChance??.55)?3:1')
g=g.replace('Math.floor(rooms.length*.85)','Math.floor(rooms.length*(profile.extraLinks??.85))')
g=g.replace("const avenueCount=map.layout==='広場'?3:map.layout==='路地'?1:2;","const avenueCount=profile.avenues??(map.layout==='広場'?3:map.layout==='路地'?1:2);")
(dst/'generator.js').write_text(g,encoding='utf-8')
s=(src/'app.js').read_text(encoding='utf-8')
s=s.replace("let floorMode='random',floorMix=0,floorVariants=[];","let floorMode='random',floorMix=0,floorVariants=[],marketFloor=4;")
s=s.replace("const sources={upstairs:","const sources={marketfront:'assets/market-shopfront64.png',rack:'assets/market-merch-rack32.png',boxes:'assets/market-delivery-boxes32.png',upstairs:")
s=s.replace("RandomFloor.index(map.seed,floorMix,","RandomFloor.index(map.seed+'-F'+marketFloor,floorMix,")
s=s.replace("map=G.generate(seed,80,70,$(\"exitMode\").value);","map=MarketGen.generate(seed,marketFloor,$(\"exitMode\").value);")
old="if(stage>=3){const p=map.prefab;texture([326,57,105,73],p.x*t,p.y*t,p.w*t,p.h*t);for(const prop of map.props){if(prop.type==='fence')ctx.drawImage(images.fence,prop.x*t,prop.y*t+t*.31,t,t*.69);}}"
new="""if(stage>=3){
 for(const shop of map.marketWalls){if(shop.closed){ctx.drawImage(images.marketfront,0,0,32,32,shop.x*t,shop.y*t,t,t);ctx.drawImage(images.marketfront,0,0,32,32,(shop.x+1)*t,shop.y*t,t,t);}else ctx.drawImage(images.marketfront,shop.x*t,shop.y*t,2*t,t);}
 for(const prop of map.props){if(prop.type==='fence')ctx.drawImage(images.fence,prop.x*t,prop.y*t+t*.31,t,t*.69);}
 for(const prop of map.marketProps){ctx.drawImage(images[prop.type],prop.x*t,prop.y*t,t,t);}
}"""
assert old in s;s=s.replace(old,new)
s=s.replace("$('stageTitle').textContent='잔향도시 · 바닥 랜덤 배치';","$('stageTitle').textContent='잔향도시 '+marketFloor+'층 · '+map.profile.name;")
s=s.replace("'독립 랜덤 배치 · 시멘트4종 × 회전4방향'","map.profile.detail")
s=s.replace("$('floorCode').textContent=map.seed+' / 바닥 '+floorMix;","$('floorCode').textContent=map.seed+' / '+marketFloor+'층 / 바닥 '+floorMix;$('floorDescription').textContent=map.profile.detail;$('shopCount').textContent=map.marketWalls.length+'곳';$('propCount').textContent=map.marketProps.length+'개';document.querySelectorAll('[data-floor]').forEach(b=>b.classList.toggle('selected',Number(b.dataset.floor)===marketFloor));")
s=s.replace("newMap('CITY-001');","newMap('MARKET-001');")
s=s.replace("window.previewApp={setFloorMode,","function setMarketFloor(value){if(![4,5,6,7].includes(value))throw Error('Unknown market floor');marketFloor=value;newMap($('seed').value||'MARKET-001');}document.querySelectorAll('[data-floor]').forEach(button=>button.onclick=()=>setMarketFloor(Number(button.dataset.floor)));$('marketView').onclick=()=>{stop();stage=4;overview=false;const p=map.marketWalls[Math.floor(map.marketWalls.length/2)];if(!p)return;player={x:p.x,y:p.y+1};updateVision();draw();};\nwindow.previewApp={setMarketFloor,setFloorMode,")
s=s.replace('getState:()=>({floorMode,','getState:()=>({marketFloor,marketWalls:map.marketWalls,marketProps:map.marketProps,floorProfile:map.profile,floorMode,')
(dst/'app.js').write_text(s,encoding='utf-8')
html=(src/'index.html').read_text(encoding='utf-8')
html=html.replace('HOLOCRAWL / 잔향도시 1~3층','HOLOCRAWL / 잔향도시 4~7층')
html=html.replace('잔향도시 · 바닥 랜덤 배치','잔향도시 · 굿즈 상점가')
html=html.replace('승인한 시멘트 바닥을 칸마다 독립적으로 섞습니다. 회사에서는 브라우저로 도트·맵 구조·배치만 확인해요.','익숙한 도시 벽과 시멘트 바닥 위로 굿즈 상점·진열대·배송 상자가 들어섭니다. 4~7층의 거리 구성을 비교해보세요.')
html=html.replace('<div class="toolbar">','<div class="districts"><span>1~3층 · 공연장 앞 거리</span><b>4~7층 · 굿즈 상점가</b><span>8~10층 · 끝나지 않는 축제</span><span>11~14층 · 뒤틀린 방송 거리</span></div><div class="floor-tabs" aria-label="굿즈 상점가 층 선택"><button data-floor="4">4층 · 상점가 초입</button><button data-floor="5">5층 · 진열 골목</button><button data-floor="6">6층 · 배송 뒷골목</button><button data-floor="7">7층 · 셔터 거리</button></div><p id="floorDescription"></p><div class="toolbar"><button id="marketView">상점 앞 보기</button>')
html=html.replace('value="CITY-001"','value="MARKET-001"')
html=html.replace('<div><dt>현재 시야</dt>','<div><dt>상점 전면</dt><dd id="shopCount"></dd></div><div><dt>진열대·배송 상자</dt><dd id="propCount"></dd></div><div><dt>현재 시야</dt>')
html=html.replace('<section class="card"><h2>시멘트 타일 조합</h2>','<section class="card"><h2>상점가 새 도트</h2><div class="market-swatches"><figure><img src="assets/market-shopfront64.png" alt="셔터와 굿즈 진열창"><figcaption>셔터·굿즈 진열창</figcaption></figure><figure><img src="assets/market-merch-rack32.png" alt="굿즈 진열대"><figcaption>굿즈 진열대</figcaption></figure><figure><img src="assets/market-delivery-boxes32.png" alt="배송 상자"><figcaption>배송 상자</figcaption></figure></div></section><section class="card"><h2>시멘트 타일 조합</h2>')
html=html.replace('<script src="generator.js?v=vision01"></script>','<script src="generator.js?v=market01"></script><script src="market-generator.js"></script>')
html=html.replace('app.js?v=random-floor01','app.js?v=market01')
html=html.replace('<footer>','<footer>4~7층 도트·구조 초안 · 브라우저 검토용 · 몹·보상은 아직 배치하지 않습니다.<br>')
(dst/'index.html').write_text(html,encoding='utf-8')
with(dst/'style.css').open('a',encoding='utf-8')as f:f.write('\n.districts{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0;font-size:12px}.districts>*{padding:8px;background:#1e2427;border:1px solid #3b4245;border-radius:5px;color:#a6a9a4}.districts b{color:#e3d3b6;border-color:#958366}.floor-tabs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px}.floor-tabs .selected{border-color:#cdb88f;background:#34332d;color:#eadcc1}.market-swatches{display:flex;flex-wrap:wrap;gap:10px}.market-swatches figure{margin:0;font-size:11px;color:#b8b9b3}.market-swatches img{height:64px;width:auto;image-rendering:pixelated;background:#4c4c48}.market-swatches figcaption{margin-top:4px}#floorDescription{font-size:13px;margin-bottom:18px}\n')
print('Prepared market4-7 browser layout preview.')
