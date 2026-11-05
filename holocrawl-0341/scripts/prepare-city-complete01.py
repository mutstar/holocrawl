from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
out=root/'preview/city-complete01'
out.mkdir(exist_ok=True)
source=(root/'preview/native-water02/app.js').read_text(encoding='utf-8')
renderer=source[source.index('function drawWater'):source.index('function preferredDoor')]
renderer=renderer[:renderer.index('function waterDemos')]+renderer[renderer.index('const feature='):]
(out/'terrain.js').write_text(renderer,encoding='utf-8')
(out/'index.html').write_text('''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>잔향도시 · 완성 도트 통합 맵</title><style>
*{box-sizing:border-box}body{margin:0;background:#101716;color:#dae1dc;font:15px/1.6 system-ui,sans-serif}main{max-width:1400px;margin:auto;padding:24px}h1{font-size:26px;margin:4px 0}p{color:#a8bab0;margin:8px 0 18px}button,a{color:#dce6df}button{background:#263b33;border:1px solid #53685d;border-radius:5px;padding:9px 14px;cursor:pointer}nav{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}.viewport{overflow:auto;max-height:78vh;border:1px solid #40534b;background:#080b0b}canvas{display:block;image-rendering:pixelated}#field.fit{width:100%;height:auto}#info{min-height:30px;padding:8px 0;color:#c6d8cb}.legend{display:flex;flex-wrap:wrap;gap:6px 20px;color:#a8bab0;font-size:13px}details{margin:18px 0}#catalog{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px}figure{margin:0;padding:10px;background:#1b2721}figure canvas{height:64px;width:auto}figcaption{font-size:12px;margin-top:6px}footer{font-size:13px;color:#8fa397;margin-top:20px}
</style><main><h1>잔향도시 · 지금까지 만든 도트 한눈에</h1><p>공연장 앞 거리의 공통 지형 + 굿즈 상점가 소품을 한곳에 모았습니다. 실제 층 확정안이 아닌 전체 도트 검토용 배치입니다.</p><nav><button id="fit">원래 크기 32×32로 보기</button><button id="doors">문 모두 열기</button><button id="stock">진열 멤버 바꾸기</button><button data-go="6,8">계단·공연장 앞</button><button data-go="29,7">상점가</button><button data-go="30,22">물·배송 골목</button></nav><div class="viewport" id="viewport"><canvas class="fit" id="field" width="1344" height="960" aria-label="잔향도시 전체 도트 통합 맵"></canvas></div><div id="info">소품에 마우스를 올리면 이름과 진열 멤버가 표시됩니다. 문을 누르면 열고 닫힙니다.</div><div class="legend"><span>시멘트 바닥 랜덤 16변형</span><span>콘크리트 벽·실외기·배관·환기구</span><span>투명 펜스</span><span>원형 계단 위·아래</span><span>네모 철제 문 닫힘·열림</span><span>얕은 물·깊은 물</span><span>상점 소품 20종</span></div><details><summary>배치된 소품 20종 펼치기</summary><div id="catalog"></div></details><footer>몹·아이템 없는 브라우저 배치 시안 · 기존 도트 재사용 · 용암·티켓 단말기 제외<br><a href="../native-water02/">물 도트</a> · <a href="../native-door12/">확정 문</a> · <a href="../city-market03/catalog.html">전체 굿즈 목록</a></footer></main>
<script src="../city-layout07/random-floor.js"></script><script src="../city-layout07/members.js"></script><script src="../city-layout07/merch-catalog.js"></script><script src="../city-layout07/market-stock.js"></script><script src="../city-layout07/pixel-reducer.js"></script><script src="../city-layout07/clean-merch.js"></script><script src="app.js"></script><script src="terrain.js"></script><script src="boot.js"></script></html>''',encoding='utf-8')
(out/'app.js').write_text('''"use strict";
const $=id=>document.getElementById(id),canvas=$('field'),ctx=canvas.getContext('2d'),images={},tiles=[],wallRuns=new Map();
let selected=0,wallOld=false,opened=new Set(),mix=0;
const palette=['rock_wall','floor','closed_door','stone_stairs_up_i','stone_stairs_down_i','shallow_water','deep_water'];
const m={w:42,h:30,seed:'CITY-ALL-ART-01',floorNumber:4,palette,rows:Array.from({length:30},()=>Array(42).fill(0))},maps=[m];
const rect=(x,y,w,h,v=1)=>{for(let yy=y;yy<y+h;yy++)for(let xx=x;xx<x+w;xx++)m.rows[yy][xx]=v;};
// Deliberate review layout: connected irregular street spaces, not a native generator sample.
rect(2,3,15,11);rect(5,14,12,9);rect(3,22,20,5);rect(17,8,10,5);rect(17,17,9,6);rect(22,3,17,10);rect(25,13,14,14);rect(21,24,6,3);
rect(10,4,4,4,0);rect(10,8,1,4,0);rect(11,11,5,1,0);m.rows[10][10]=2;m.rows[11][13]=2;
rect(22,4,4,3,0);rect(29,14,5,3,0);rect(25,18,1,4,0);m.rows[20][25]=2;
rect(33,21,5,5,5);rect(34,22,3,3,6);m.rows[21][33]=1;m.rows[25][37]=1;
m.rows[6][5]=3;m.rows[24][20]=4;
const fixtures=[['acrylic-window',27,2],['closed-shutter',33,2],['half-shutter',36,2],['shirt-window',23,6],['poster-wall',10,7],['acrylic-rack',28,5],['shirt-stack',26,8],['hoodie-rack',36,7],['plush-basket',31,10],['poster-rolls',24,11],['keychain-hooks',37,10],['badge-trays',33,5],['shopping-bags',28,11],['delivery-boxes',27,17],['open-carton',29,19],['delivery-cart',37,17],['folding-crates',27,24],['trash-bags',6,20],['paper-rubbish',7,23],['recycling-bins',10,21]].map(([type,x,y])=>({type,x,y}));
const fences=[{x:5,y:12},{x:6,y:12},{x:7,y:12},{x:8,y:12},{x:16,y:18},{x:17,y:18},{x:18,y:18}];
const mounted=[{kind:0,x:5,y:2},{kind:1,x:8,y:2},{kind:2,x:13,y:2},{kind:3,x:30,y:16}];
function draw(){ctx.imageSmoothingEnabled=false;ctx.fillStyle='#080b0b';ctx.fillRect(0,0,canvas.width,canvas.height);for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++)tile(ctx,m,x,y,x*32,y*32,32);
for(const p of mounted){const x=p.x*32,y=p.y*32;ctx.filter='brightness(1.35)';if(p.kind===0)texture(ctx,[289,34,37,19],x+2,y+9,27,14);if(p.kind===2)texture(ctx,[294,86,22,16],x+5,y+9,22,16);if(p.kind===3)texture(ctx,[183,31,32,12],x,y+7,32,12);if(p.kind===1){ctx.filter='none';ctx.strokeStyle='#292e2a';ctx.lineWidth=4;ctx.beginPath();ctx.moveTo(x+4,y+4);ctx.lineTo(x+19,y+4);ctx.lineTo(x+19,y+28);ctx.stroke();ctx.strokeStyle='#92938b';ctx.lineWidth=2;ctx.stroke();}ctx.filter='none';}
for(const p of fixtures)MarketStock.draw(ctx,p,m,images,32,mix);for(const p of fences)ctx.drawImage(images.fence,p.x*32,p.y*32+10,32,22);
}
function locate(e){const r=canvas.getBoundingClientRect();return{x:Math.floor((e.clientX-r.left)*canvas.width/r.width/32),y:Math.floor((e.clientY-r.top)*canvas.height/r.height/32)};}
canvas.onmousemove=e=>{const{x,y}=locate(e),p=fixtures.find(p=>p.y===y&&x>=p.x&&x<p.x+(MerchCatalog.find(a=>a.id===p.type).kind==='wall'?2:1));if(p)$('info').textContent=MarketStock.describe(p,m,mix);else $('info').textContent=isWater(feature(m,x,y))?(feature(m,x,y)==='deep_water'?'깊은 물':'얕은 물'):isDoor(feature(m,x,y))?'철제 문 · 클릭해서 열기/닫기':isUp(feature(m,x,y))?'올라가는 원형 계단':isDown(feature(m,x,y))?'내려가는 원형 계단':'잔향도시 · 전체 도트 검토용 배치';};
canvas.onclick=e=>{const{x,y}=locate(e);if(isDoor(feature(m,x,y))){const k=doorKey(x,y);opened.has(k)?opened.delete(k):opened.add(k);draw();}};
function fit(value){canvas.classList.toggle('fit',value);$('fit').textContent=value?'원래 크기 32×32로 보기':'전체 지도 맞춰 보기';}
$('fit').onclick=()=>fit(!canvas.classList.contains('fit'));
$('doors').onclick=()=>{const opening=!opened.size;opened.clear();if(opening)for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++)if(isDoor(feature(m,x,y)))opened.add(doorKey(x,y));$('doors').textContent=opening?'문 모두 닫기':'문 모두 열기';draw();};
$('stock').onclick=()=>{mix++;draw();gallery();};
document.querySelectorAll('[data-go]').forEach(b=>b.onclick=()=>{fit(false);const[x,y]=b.dataset.go.split(',').map(Number),v=$('viewport');v.scrollTo({left:x*32-v.clientWidth/2,top:y*32-v.clientHeight/2,behavior:'smooth'});});
function gallery(){$('catalog').replaceChildren();for(const a of MerchCatalog){const f=document.createElement('figure'),c=document.createElement('canvas'),caption=document.createElement('figcaption');c.width=a.width;c.height=32;c.getContext('2d').imageSmoothingEnabled=false;MarketStock.draw(c.getContext('2d'),{type:a.id,x:0,y:0},m,images,32,mix);caption.textContent=a.name;f.append(c,caption);$('catalog').append(f);}}
''',encoding='utf-8')
(out/'boot.js').write_text('''(async()=>{try{const base='../city-layout07/';const sources={reference:base+'assets/scene-reference.png',floor:base+'assets/cement-reference.png',up:base+'assets/stairs-up12-32.png',down:base+'assets/stairs-down06-32.png',fence:base+'assets/fence-cutout32.png',closed:'../native-water02/assets/fire-door-closed32.png',open:'../native-water02/assets/fire-door-open32.png',wall:'../native-water02/assets/concrete-wall-surface256.png',shallow:'../native-water02/assets/water-shallow128.png',deep:'../native-water02/assets/water-deep128.png'};
Object.assign(sources,Object.fromEntries(MerchCatalog.map(p=>['clean-'+p.id,base+'assets/props-clean/'+p.id+'.png'])),Object.fromEntries(MerchCatalog.map(p=>[p.id,base+p.file])),Object.fromEntries(MarketMembers.map(p=>['member-'+p.id,base+p.image])));
for(const[key,src]of Object.entries(sources)){images[key]=await new Promise((resolve,reject)=>{const i=new Image();i.onload=()=>resolve(i);i.onerror=()=>reject(Error(src));i.src=src;});}
const patches=[[270,150,32,32],[285,153,32,32],[160,300,32,32],[260,300,32,32]];for(let i=0;i<16;i++){const c=document.createElement('canvas');c.width=c.height=32;const cc=c.getContext('2d');cc.imageSmoothingEnabled=false;cc.translate(16,16);cc.rotate(i%4*Math.PI/2);cc.drawImage(images.floor,...patches[Math.floor(i/4)],-16,-16,32,32);tiles.push(c);}MarketStock.makeSprites(images);draw();gallery();window.completePreview={map:m,fixtures,fences,mounted,draw};window.ready=true;
}catch(e){$('info').textContent='불러오기 오류: '+e.message;throw e;}})();''',encoding='utf-8')
(out/'manifest.json').write_text(json.dumps({'purpose':'complete existing city art review','layout':'authored review map, not native procedural output','dimensions':[42,30],'tileSize':32,'props':20,'terrainSource':'native-water02','commonArt':'city-layout07','nativeGameApplied':False,'monsters':False,'items':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(out)

