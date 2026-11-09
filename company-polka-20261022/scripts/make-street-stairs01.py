from pathlib import Path
import shutil
r=Path(__file__).resolve().parents[1];src=r/'analysis/previews/street-entrance01';d=r/'analysis/previews/street-stairs01';d.mkdir(exist_ok=True)
for n in ['app.js','generator.js','index.html','style.css']:shutil.copy2(src/n,d/n)
shutil.copytree(src/'assets',d/'assets',dirs_exist_ok=True)
p=d/'generator.js';s=p.read_text(encoding='utf-8').replace('function generate(seed,w=80,h=70)','function generate(seed,w=80,h=70,exitMode="auto")')
s=s.replace('doors.sort((a,b)=>b.distance-a.distance);if(!doors.length)continue;\n map.exitDoor=doors[0];map.exit={x:map.exitDoor.x+1,y:map.exitDoor.y+2};far=map.exit.y*w+map.exit.x;', '''
 const floors=[];for(let y=2;y<h-2;y++)for(let x=2;x<w-2;x++){let open=true;for(let yy=y-1;yy<=y+1;yy++)for(let xx=x-1;xx<=x+1;xx++)if(cells[yy*w+xx]!==FLOOR)open=false;if(open&&b.dist[y*w+x]>=18)floors.push({x,y,distance:b.dist[y*w+x],type:'floor'});}
 const choices=exitMode==='floor'?floors:exitMode==='wall'?doors.map(p=>({...p,type:'wall'})):[...floors,...doors.map(p=>({...p,type:'wall'}))];
 choices.sort((a,b)=>b.distance-a.distance);if(!choices.length)continue;
 const chosen=choices[int(0,Math.min(11,choices.length-1))];map.exitType=chosen.type;
 if(chosen.type==='wall'){map.exitDoor=chosen;map.exit={x:chosen.x+1,y:chosen.y+2};}else{map.exitDoor=null;map.exit={x:chosen.x,y:chosen.y};}
 far=map.exit.y*w+map.exit.x;
''')
s=s.replace('b.dist[i]>=8&&i!==far','b.dist[i]>=8&&Math.max(Math.abs(i%w-map.exit.x),Math.abs(Math.floor(i/w)-map.exit.y))>1')
p.write_text(s,encoding='utf-8')
p=d/'app.js';s=p.read_text(encoding='utf-8').replace("const sources={fence:","const sources={downstairs:'assets/stairs-rails48.png',fence:")
s=s.replace('map=G.generate(seed);','map=G.generate(seed,80,70,$("exitMode").value);')
start=s.index('const door=map.exitDoor;texture(');end=s.index('for(const enemy of map.enemies)',start)
s=s[:start]+'''if(map.exitType==='wall'){const door=map.exitDoor;texture([326,57,105,73],door.x*t,door.y*t,door.w*t,door.h*t);ctx.fillStyle='#bab1a0';ctx.fillRect(map.exit.x*t+t*.14,map.exit.y*t,t*.72,Math.max(1,t*.09));}else{ctx.drawImage(images.downstairs,(map.exit.x-.25)*t,(map.exit.y-.5)*t,t*1.5,t*1.5);}'''+s[end:]
s=s.replace("'会場入口 · 다음 층 입구 도착! 층 이동은 아직 연결 전이에요.'","'다음 층 입구 도착! 층 이동은 아직 연결 전이에요.'")
s=s.replace("'다음 층 입구 미리보기 · 문 앞 청록 표시 칸이 기존 내려가는 계단 자리예요.'","map.exitType==='wall'?'벽에 붙은 공연장 입구 · 문 앞칸이 다음 층 출구예요.':'광장 바닥의 내려가는 계단 · 계단과 양옆 손잡이만 있는 형태예요.'")
s=s.replace("$('exitView').onclick=showExit;","$('exitView').onclick=showExit;$('exitMode').onchange=()=>{newMap($('seed').value);showExit();};")
s=s.replace("newMap('CITY-001');if(location.hash", "if(location.hash==='#floor')$('exitMode').value='floor';if(location.hash==='#wall')$('exitMode').value='wall';newMap('CITY-001');if(location.hash")
s=s.replace("if(location.hash==='#exit')showExit();","if(['#exit','#floor','#wall'].includes(location.hash))showExit();")
s=s.replace('exitDoor:map?.exitDoor,','exitDoor:map?.exitDoor,exitType:map?.exitType,')
p.write_text(s,encoding='utf-8')
p=d/'index.html';s=p.read_text(encoding='utf-8').replace('<button id="exitView">','<label for="exitMode">출구 형태</label><select id="exitMode"><option value="auto">지형에 맞게</option><option value="floor">바닥 계단</option><option value="wall">벽 입구</option></select><button id="exitView">').replace('v=entrance01','v=stairs01').replace('잔향도시 · 다음 층으로 가는 입구','잔향도시 · 계단과 손잡이')
p.write_text(s,encoding='utf-8')
with (d/'style.css').open('a',encoding='utf-8') as f:f.write('\nselect{font:inherit;background:#292d30;color:#ecebe4;padding:10px;border:1px solid #51565a;border-radius:5px;}\n')
test=(r/'scripts/test-street-walls01.cjs').read_text(encoding='utf-8-sig').replace('street-walls01','street-stairs01')
test=test.replace('assert(m.prefab);',"assert(m.prefab);assert(['wall','floor'].includes(m.exitType));if(m.exitType==='floor'){for(let yy=m.exit.y-1;yy<=m.exit.y+1;yy++)for(let xx=m.exit.x-1;xx<=m.exit.x+1;xx++)assert.strictEqual(m.cells[yy*m.w+xx],g.FLOOR);}else assert(m.exitDoor);")
(r/'scripts/test-street-stairs01.cjs').write_text(test,encoding='utf-8')
check=(r/'scripts/check-street-entrance01.cjs').read_text(encoding='utf-8').replace('street-entrance01','street-stairs01').replace('8791/','8792/')
(r/'scripts/check-street-stairs01.cjs').write_text(check,encoding='utf-8')
capture=(r/'scripts/capture-street-entrance01.cjs').read_text(encoding='utf-8').replace('street-entrance01','street-stairs01').replace('8791/?v=entrance01#exit','8792/?v=stairs01#floor').replace('entrance-field.png','stairs-field.png')
(r/'scripts/capture-street-stairs01.cjs').write_text(capture,encoding='utf-8')
print('Created floor/wall exit preview.')
