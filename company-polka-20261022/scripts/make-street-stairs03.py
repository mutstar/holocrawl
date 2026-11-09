from pathlib import Path
import shutil
r=Path(__file__).resolve().parents[1];src=r/'analysis/previews/street-stairs01';d=r/'analysis/previews/street-stairs03';d.mkdir(exist_ok=True)
for n in ['app.js','generator.js','index.html','style.css']:shutil.copy2(src/n,d/n)
shutil.copytree(src/'assets',d/'assets',dirs_exist_ok=True)
p=d/'generator.js';s=p.read_text(encoding='utf-8')
s=s.replace('const b=distances(map,map.start);let far=0;', '''
 // Choose the arrival stair on an open 3x3 floor patch close to the original start.
 const arrivals=[];for(let y=2;y<h-2;y++)for(let x=2;x<w-2;x++){let clear=true;for(let yy=y-1;yy<=y+1;yy++)for(let xx=x-1;xx<=x+1;xx++)if(cells[yy*w+xx]!==FLOOR)clear=false;if(clear)arrivals.push({x,y,score:Math.abs(x-map.start.x)+Math.abs(y-map.start.y)});}
 arrivals.sort((a,b)=>a.score-b.score);if(!arrivals.length)continue;
 map.upstairs={x:arrivals[0].x,y:arrivals[0].y};map.start={x:map.upstairs.x,y:map.upstairs.y+1};
 const b=distances(map,map.start);let far=0;''')
p.write_text(s,encoding='utf-8')
p=d/'app.js';s=p.read_text(encoding='utf-8').replace('const sources={downstairs:',"const sources={upstairs:'assets/stairs-up03-28.png',downstairs:")
s=s.replace("if(map.exitType==='wall'){const door=map.exitDoor;", "ctx.drawImage(images.upstairs,(map.upstairs.x+.0625)*t,(map.upstairs.y+.0625)*t,t*.875,t*.875);if(map.exitType==='wall'){const door=map.exitDoor;")
s=s.replace("if(stage===4){mc.fillStyle='#eadcaa';", "if(stage===4){mc.fillStyle='#9ab9db';mc.fillRect(map.upstairs.x*scale,map.upstairs.y*scale,scale,scale);mc.fillStyle='#eadcaa';")
s=s.replace("$('message').textContent='방향키·WASD로 이동하거나, 갈 곳을 클릭하세요.';", "$('message').textContent='시작 지점 · 바로 뒤의 계단은 이전 층으로 돌아가는 올라가는 계단이에요.';")
insert="""
function showStart(){stop();stage=4;overview=false;player={...map.start};draw();$('message').textContent='시작 지점 · 캐릭터 바로 뒤의 작은 계단이 올라가는 계단이에요. 실제 층 이동은 아직 연결 전이에요.';}
$('startView').onclick=showStart;
"""
s=s.replace('Promise.all(Object.entries(sources)',insert+'Promise.all(Object.entries(sources)')
s=s.replace('window.previewApp={showExit,','window.previewApp={showStart,showExit,').replace('exitType:map?.exitType,','exitType:map?.exitType,upstairs:map?.upstairs,start:map?.start,')
p.write_text(s,encoding='utf-8')
p=d/'index.html';s=p.read_text(encoding='utf-8').replace('<button id="exitView">','<button id="startView">올라가는 계단·시작점</button><button id="exitView">').replace('v=flat-stairs02','v=upstairs03').replace('잔향도시 · 1칸 계단 도트','잔향도시 · 올라가는 계단과 시작점')
p.write_text(s,encoding='utf-8')
for name in ['test-street-stairs01.cjs','check-street-stairs01.cjs']:
 s=(r/'scripts'/name).read_text(encoding='utf-8-sig').replace('street-stairs01','street-stairs03').replace('8792/','8793/')
 if name.startswith('test-'):s=s.replace('assert(m.prefab);',"assert(m.prefab);assert(m.upstairs);assert.strictEqual(m.start.y,m.upstairs.y+1);assert.strictEqual(m.cells[m.upstairs.y*m.w+m.upstairs.x],g.FLOOR);")
 (r/'scripts'/name.replace('stairs01','stairs03')).write_text(s,encoding='utf-8')
capture=(r/'scripts/capture-street-stairs01.cjs').read_text(encoding='utf-8').replace('street-stairs01','street-stairs03').replace('8792/?v=stairs01#floor','8793/?v=upstairs03#start').replace('stairs-field.png','upstairs-field.png')
(r/'scripts/capture-street-stairs03.cjs').write_text(capture,encoding='utf-8')
print('Prepared upstairs and arrival layout.')
