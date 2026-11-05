from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-explore01'
p=out/'app.js';s=p.read_text(encoding='utf-8')
if 'function crateLoot(' not in s:
 s=s.replace(' const reached=reach(start,blocked);', ''' const crateRandom=rng(m.seed+':crates03:'+placementSeed),crateTarget=2+Math.floor(crateRandom()*2);
 for(const spacing of [8,5,3]){for(const p of shuffled(edges,crateRandom)){if(fixtures.filter(f=>f.type==='delivery-boxes').length>=crateTarget)break;if(fixtures.some(f=>Math.hypot(f.x-p.x,f.y-p.y)<spacing))continue;const test=new Set(blocked);test.add(p.x+','+p.y);if(reach(start,test).size>=baseline.size-test.size){fixtures.push({type:'delivery-boxes',...p});blocked.add(p.x+','+p.y);}}}
 const reached=reach(start,blocked);''')
 s=s.replace('saveAvailable=true;', 'saveAvailable=true,brokenCrates=new Set(),groundLoot=[],inventory={potion:0,scroll:0,gold:0};')
 s=s.replace("fixtures.filter(p=>MerchCatalog.find(a=>a.id===p.type).kind==='floor')", "fixtures.filter(p=>!isBrokenCrate(p)&&MerchCatalog.find(a=>a.id===p.type).kind==='floor')")
 s=s.replace("JSON.stringify({player,turns,opened:[...opened],explored:[...explored]})", "JSON.stringify({player,turns,opened:[...opened],explored:[...explored],brokenCrates:[...brokenCrates],groundLoot,inventory})")
 a=s.index('function startExploration(');b=s.index('function gameState()',a)
 s=s[:a]+'''function startExploration(reset=false){stopWalk();opened.clear();brokenCrates=new Set();groundLoot=[];inventory={potion:0,scroll:0,gold:0};player={x:entry().x,y:entry().y};turns=0;explored=new Uint8Array(m.w*m.h);let restored=false;
 if(!reset)try{const saved=JSON.parse(localStorage.getItem(saveKey())||'null');if(saved&&saved.explored.length===explored.length&&pass(saved.player.x,saved.player.y)){brokenCrates=new Set(saved.brokenCrates||[]);groundLoot=saved.groundLoot||[];inventory={potion:0,scroll:0,gold:0,...saved.inventory};player=saved.player;turns=saved.turns;opened=new Set(saved.opened);explored=Uint8Array.from(saved.explored);restored=true;}}catch{}
 updateVision();center={...player};overview=false;$('mapSelect').value=String(selected);message=reset?'탐험을 처음부터 시작합니다.':restored?'저장한 위치에서 탐험을 이어갑니다.':'입구에서 출발! 배송 상자에 부딪히면 부술 수 있습니다.';draw();save();}
'''+s[b:]
 s=s.replace('autoWalking:!!autoTarget,saveAvailable}', 'autoWalking:!!autoTarget,saveAvailable,brokenCrates:[...brokenCrates],groundLoot,inventory,crateCount:fixtures.filter(p=>p.type===\'delivery-boxes\').length}')
 s=s.replace("f=feature(m,x,y);if(!canWalk(x,y))", "f=feature(m,x,y);const crate=fixtures.find(p=>p.x===x&&p.y===y&&p.type==='delivery-boxes'&&!isBrokenCrate(p));if(crate)return breakCrate(crate);if(!canWalk(x,y))")
 s=s.replace("'탐험 중 · 밝은 곳은 현재 시야, 어두운 곳은 지나온 장소입니다.';afterAction();", "'탐험 중 · 밝은 곳은 현재 시야, 어두운 곳은 지나온 장소입니다.';pickupLoot();afterAction();")
 s=s.replace("if(explored[p.y*m.w+p.x]){MarketStock.draw", "if(!isBrokenCrate(p)&&explored[p.y*m.w+p.x]){MarketStock.draw")
 s=s.replace("if(explored[p.y*m.w+p.x])MarketStock.draw", "if(!isBrokenCrate(p)&&explored[p.y*m.w+p.x])MarketStock.draw")
 s=s.replace("for(let y=y0;y<y1;y++)for(let x=x0;x<x1;x++){const i=y*m.w+x;if(!explored[i])", "drawLoot(t);\nfor(let y=y0;y<y1;y++)for(let x=x0;x<x1;x++){const i=y*m.w+x;if(!explored[i])")
 s=s.replace("$('info').textContent=message;}", "$('info').textContent=message;drawInventory();}")
 s=s.replace("if(d===1&&isDoor(feature(m,p.x,p.y)))", "const crate=fixtures.find(f=>f.x===p.x&&f.y===p.y&&f.type==='delivery-boxes'&&!isBrokenCrate(f));if(crate){if(d===1)breakCrate(crate);else{message='배송 상자는 옆으로 다가가서 누르거나 부딪히면 부술 수 있습니다.';draw();}}else if(d===1&&isDoor(feature(m,p.x,p.y)))")
 s+='''
function isBrokenCrate(p){return p.type==='delivery-boxes'&&brokenCrates.has(p.x+','+p.y);}
function crateLoot(p){const random=rng(m.seed+':crate-loot03:'+placementSeed+':'+p.x+','+p.y),kind=['potion','scroll','gold'][Math.floor(random()*3)],quantity=kind==='gold'?10+Math.floor(random()*11):1;return{x:p.x,y:p.y,kind,quantity};}
function lootName(item){return item.kind==='potion'?'회복 물약':item.kind==='scroll'?'두루마리':'금화';}
function breakCrate(p){stopWalk();if(!p||isBrokenCrate(p)||Math.max(Math.abs(p.x-player.x),Math.abs(p.y-player.y))!==1)return false;brokenCrates.add(p.x+','+p.y);const item=crateLoot(p);groundLoot.push(item);message='배송 상자를 부쉈습니다! '+lootName(item)+' '+item.quantity+(item.kind==='gold'?'개':'개')+'가 떨어졌습니다. 그 칸으로 이동하면 줍습니다.';afterAction();return true;}
function pickupLoot(){const item=groundLoot.find(p=>p.x===player.x&&p.y===player.y);if(!item)return;inventory[item.kind]+=item.quantity;groundLoot=groundLoot.filter(p=>p!==item);message=lootName(item)+' '+item.quantity+'개를 주웠습니다.';}
function drawLoot(t){for(const p of groundLoot)if(explored[p.y*m.w+p.x])ctx.drawImage(images['loot-'+p.kind],p.x*t,p.y*t,t,t);}
function drawInventory(){const panel=$('inventory');if(!panel)return;panel.replaceChildren();const title=document.createElement('strong');title.textContent='상자에서 얻은 물건';panel.append(title);for(const kind of ['potion','scroll','gold']){const row=document.createElement('div');row.textContent=(kind==='potion'?'회복 물약':kind==='scroll'?'두루마리':'금화')+' · '+inventory[kind];panel.append(row);}}
'''
 p.write_text(s,encoding='utf-8')
p=out/'grounding.js';s=p.read_text(encoding='utf-8').replace("for(const p of fixtures){const meta=", "for(const p of fixtures){if(isBrokenCrate(p))continue;const meta=");p.write_text(s,encoding='utf-8')
itemRoot=root/'engine/upstream/crawl-ref/source/rltiles/item'
for kind,source in [('potion','potion/i-curing.png'),('scroll','scroll/scroll.png'),('gold','gold/10.png')]:
 shutil.copyfile(itemRoot/source,out/'assets'/f'crate-loot-{kind}.png')
p=out/'boot.js';s=p.read_text(encoding='utf-8')
if "'loot-potion'" not in s:s=s.replace('const sources={',"const sources={'loot-potion':'assets/crate-loot-potion.png','loot-scroll':'assets/crate-loot-scroll.png','loot-gold':'assets/crate-loot-gold.png',")
p.write_text(s,encoding='utf-8')
p=out/'index.html';s=p.read_text(encoding='utf-8')
if 'id="inventory"' not in s:s=s.replace('<p class="hint">방향키', '<section id="inventory" style="border-top:1px solid #40564a;padding:12px 0"></section><p class="hint">방향키')
s=s.replace('진행은 브라우저에 자동 저장됩니다.','배송 상자: 부딪혀서 부수기<br>떨어진 아이템: 밟아서 줍기<br>진행은 브라우저에 자동 저장됩니다.')
s=s.replace('몹·아이템·전투·다음 층 이동은 아직 없습니다.','배송 상자는 층당 2~3개, 내용물은 시험용 물약·두루마리·금화입니다. 획득까지만 연결했으며 아이템 사용·몹·전투·다음 층 이동은 아직 없습니다.')
s=s.replace('src="app.js"','src="app.js?v=crates03"').replace('src="boot.js"','src="boot.js?v=crates03"').replace('src="grounding.js"','src="grounding.js?v=crates03"')
p.write_text(s,encoding='utf-8')
print('2–3 breakable crates, deterministic loot, pickup and persistent inventory connected.')
