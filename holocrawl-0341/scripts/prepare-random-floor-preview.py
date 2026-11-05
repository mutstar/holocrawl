from pathlib import Path
import shutil

root=Path(__file__).resolve().parents[1]
source=root/'preview/street-vision01';out=root/'preview/street-floor-random01';out.mkdir(exist_ok=True)
for name in ['generator.js','visibility.js','visibility-paths.js','style.css']:
    shutil.copy2(source/name,out/name)
shutil.copytree(source/'assets',out/'assets',dirs_exist_ok=True)
s=(source/'app.js').read_text(encoding='utf-8')
s=s.replace('memory=null,fogEnabled=true','memory=null,fogEnabled=false')
s=s.replace("const G=StreetGen,stages=","let floorMode='random',floorMix=0,floorVariants=[];\nconst G=StreetGen,stages=")
s=s.replace('⑤ 계단·적 배치','⑤ 계단·시작점 배치')
old='texture(floorPatches[hash(x,y)%floorPatches.length],px,py,t,t,1,images.floor);'
assert old in s
s=s.replace(old,"const tile=floorMode==='repeat'?0:RandomFloor.index(map.seed,floorMix,x,y);ctx.drawImage(floorVariants[tile],px,py,t,t);")
s=s.replace("map=G.generate(seed,80,70,$(\"exitMode\").value);player=", "map=G.generate(seed,80,70,$(\"exitMode\").value);map.enemies=[];map.items=[];player=")
s=s.replace("newMap('CITY-001');", "floorVariants=RandomFloor.variants(images.floor);RandomFloor.showSwatches(floorVariants,$('floorSwatches'));newMap('CITY-001');",1)
s=s.replace("$('stageTitle').textContent='시야·탐험 안개';", "$('stageTitle').textContent='잔향도시 · 바닥 랜덤 배치';")
s=s.replace("$('stageDetail').textContent=fogEnabled?'시야7칸 · 벽 뒤는 가림 · 펜스 너머는 보임':'전체 배치 확인 모드 · 탐험 기억은 현재 시야만 갱신';", "$('stageDetail').textContent=fogEnabled?'시야7칸 · 벽 뒤는 가림 · 펜스 너머는 보임':'독립 랜덤 배치 · 시멘트4종 × 회전4방향';$('floorCode').textContent=map.seed+' / 바닥 '+floorMix;")
controls="""
function setFloorMode(mode){if(!['repeat','random'].includes(mode))throw Error('Unknown floor pattern');floorMode=mode;$('floorPattern').value=mode;draw();}
function setFloorMix(value){if(!Number.isSafeInteger(value)||value<0)throw Error('Invalid floor mix');floorMix=value;draw();}
$('floorPattern').onchange=()=>setFloorMode($('floorPattern').value);
$('shuffleFloor').onclick=()=>{setFloorMix(floorMix+1);$('message').textContent='바닥 배치만 다시 섞었어요. 지도·벽·계단 위치는 그대로예요.';};
"""
s=s.replace('window.previewApp={setFogEnabled:',controls+'\nwindow.previewApp={setFloorMode,setFloorMix,setFogEnabled:')
s=s.replace('getState:()=>({fogEnabled,','getState:()=>({floorMode,floorMix,floorChoices:Array.from({length:map.w*map.h},(_,i)=>floorMode===\'repeat\'?0:RandomFloor.index(map.seed,floorMix,i%map.w,Math.floor(i/map.w))),fogEnabled,')
(out/'app.js').write_text(s,encoding='utf-8')
html=(source/'index.html').read_text(encoding='utf-8')
html=html.replace('잔향도시 · 지도 생성 미리보기','잔향도시 · 바닥 랜덤 배치')
html=html.replace('잔향도시 · 시야와 탐험 안개','잔향도시 · 바닥 랜덤 배치')
html=html.replace('돌죽0.34.1 시선 경로 · 주변7칸부터 탐험해보세요. 벽 뒤는 가려지고 지나온 길은 어둡게 기억합니다.','승인한 시멘트 바닥을 칸마다 독립적으로 섞습니다. 회사에서는 브라우저로 도트·맵 구조·배치만 확인해요.')
html=html.replace('<button id="fog">탐험 안개 끄기</button>','<label for="floorPattern">바닥</label><select id="floorPattern"><option value="random">랜덤 배치</option><option value="repeat">한 타일 반복 · 비교</option></select><button id="shuffleFloor">바닥만 다시 섞기</button><button id="fog">탐험 안개 켜기</button>')
html=html.replace('⑤ 계단·적 배치','⑤ 계단·시작점 배치')
start=html.index('<section class="card"><h2>직접 만든 장소도 섞어요')
end=html.index('</aside>',start)
html=html[:start]+'''<section class="card"><h2>시멘트 타일 조합</h2><p>기존 시멘트4종을 각각 4방향으로 회전한 16가지 형태입니다. 옆칸 무늬를 이어 맞추는 조건은 없습니다.</p><div id="floorSwatches"></div><p id="floorCode"></p></section><section class="card note"><h2>구조·배치 확인</h2><p>방향키·WASD / Q·E·Z·C 대각선 이동. 안개를 켜서 시야도 확인할 수 있습니다.</p><p>지도 번호가 같으면 같은 구조가 나옵니다. ‘바닥만 다시 섞기’는 바닥만 바꿉니다. 몹·보상 배치는 나중에 진행해요.</p></section>'''+html[end:]
html=html.replace('<script src="app.js?v=vision01"></script>','<script src="random-floor.js"></script><script src="app.js?v=random-floor01"></script>')
(out/'index.html').write_text(html,encoding='utf-8')
with (out/'style.css').open('a',encoding='utf-8')as f:
    f.write('\n#floorSwatches{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}#floorSwatches figure{margin:0;background:#141719;padding:4px}#floorSwatches canvas{display:block;width:100%;height:auto;image-rendering:pixelated}#floorSwatches figcaption{font:10px monospace;text-align:center;color:#aaa;padding-top:3px}#floorCode{overflow-wrap:anywhere}\n')
print('Prepared independent random floor preview; no native game changes.')
