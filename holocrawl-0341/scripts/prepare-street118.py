"""Reconnect sparse1–3F ambience above unchanged native107 floor exports."""
from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[1];S=R/'preview/native-play107';O=R/'preview/city-street118';O.mkdir(exist_ok=True)
manifest=json.loads((S/'manifest.json').read_text(encoding='utf-8'))
entries=[]
for m in manifest['maps']:
 if m['forced'] or m['depth']>3:continue
 entries.append({**m,'file':'../native-play107/'+m['file'],'probe':'../native-play107/'+m['probe']})
assert len(entries)==36
(O/'manifest.json').write_text(json.dumps({**manifest,'revision':118,'maps':entries,'backgroundSource':107,'nativeAmbientIntegration':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
shutil.copy2(R/'preview/city-market117/wall92.json',O/'wall92.json')
s=(S/'index.html').read_text(encoding='utf-8').replace('잔향도시 · 실제 생성과 플레이 점검107','잔향도시 1~3층 · 거리 소품 재연결118')
s=s.replace('최신 벽·문·시설을 적용한0.34.1 엔진에서 새로 만든 지도입니다. 시야를 밝히며 이동하고, 문과 시설 연결을 확인해 보세요.','최신 벽·문·고정지형이 있는 실제 생성 지도에 초반 거리 소품을 다시 배치했습니다. 상점가보다 드문 진열과 벽 설비를 확인해 보세요.')
s=s.replace('<button id="actorScene">','<button hidden id="actorScene">').replace('<label><input id="actors"','<label hidden><input id="actors"')
s=s.replace('<style>', '<style>[hidden]{display:none!important}')
s=s.replace('<nav><label for="oracle">','<nav hidden><label for="oracle">')
s=s.replace('<canvas id="field"','<nav><button id="streetShops">진열창 주변</button><button id="streetCrate">택배상자 주변</button><button id="streetUtilities">벽 설비 주변</button><label><input id="ambience" type="checkbox" checked>거리 소품 표시</label></nav><input hidden id="beforeScene112" type="checkbox"><canvas id="field"')
a=s.index('<footer>');b=s.index('</footer>',a)+len('</footer>')
s=s[:a]+'<footer>1~3층 일반 거리 소품을 실제 생성 지도 위에 연결한 브라우저 검토판입니다. 엔진107 실행파일과 실제 게임 세이브는 바꾸지 않았습니다. 적·보상은 보류합니다.</footer>'+s[b:]
s=s.replace('<script src="review107.js"></script>','<script src="../city-market117/material108.js"></script><script src="../city-market117/members.js"></script><script src="../city-market117/merch-catalog.js"></script><script src="../city-market117/market-stock.js"></script><script src="../city-market117/scene112.js"></script><script src="../city-market117/pixel-reducer.js"></script><script src="../city-market117/scene117.js"></script><script src="ambient118.js"></script><script src="review118.js"></script>')
(O/'index.html').write_text(s,encoding='utf-8')
s=(S/'review107.js').read_text(encoding='utf-8').replace('`assets/${k}.png`','`../native-play107/assets/${k}.png`')
s=s.replace('let sample=Math.max', 'let ambient,blocked=new Set();\n let sample=Math.max')
s=s.replace("&&(map.passable[y*map.width+x]||cell(x,y)==='+');", "&&(map.passable[y*map.width+x]||cell(x,y)==='+')&&(!document.getElementById('ambience').checked||!blocked.has(key(x,y)));")
s=s.replace("  if(actors)for", "  if(document.getElementById('ambience').checked)drawAmbient118(g,ambient,map,propImages,s,ox,oy,seen,fog);\n  if(actors)for")
s=s.replace("  const playerTiles=(probe.actors||[]).find(a=>a.kind==='player')?.tiles||manifest.playerTiles;\n  for(const t of playerTiles)tile(t,ox+state.player.x*32*s,oy+state.player.y*32*s,s);", "  for(const part of ['body','boots','armour','helmet','sword'])g.drawImage(propImages[part],ox+state.player.x*32*s,oy+state.player.y*32*s,32*s,32*s);")
s=s.replace('壁92','벽92').replace('벽92/문101/시설106 엔진 적용','벽92/문101/시설106 + 초반 소품118 검토')
s=s.replace('map=m;probe=p;', 'map=m;probe=p;ambient=Ambient118.generate(map);blocked=new Set(ambient.blocked);')
s=s.replace('facilityStart();window.ready=true;','stairStart();window.ready=true;')
s=s.replace('window.play107={','window.play118={getAmbience:()=>ambient,focusAmbient,')
s=s.replace("await load();", "await load();document.getElementById('streetShops').onclick=()=>focusAmbient('shops');document.getElementById('streetCrate').onclick=()=>focusAmbient('crate');document.getElementById('streetUtilities').onclick=()=>focusAmbient('utilities');document.getElementById('ambience').onchange=()=>{if(blocked.has(key(state.player.x,state.player.y)))stairStart();draw();};",1)
helper=(R/'scripts/street118-render.js').read_text(encoding='utf-8')
s=s.replace(' let sample=Math.max',helper+'\n let sample=Math.max',1)
(O/'review118.js').write_text(s,encoding='utf-8')
(O/'inputs.json').write_text(json.dumps({'revision':118,'nativeSource':107,'nativeExecutableChanged':False,'maps':{m['file']:m['sha256'] for m in entries},'rendererSource':hashlib.sha256((S/'review107.js').read_bytes()).hexdigest(),'sparseProps':'2 windows/2 stalls/2 shutters/2–3 crates/1 trash/fence/infrastructure'},indent=2)+'\n')
print('Prepared 36 native 1-3F maps with sparse street ambience118.')
