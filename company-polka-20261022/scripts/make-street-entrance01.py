from pathlib import Path
import shutil
r=Path(__file__).resolve().parents[1];src=r/'analysis/previews/street-walls01';d=r/'analysis/previews/street-entrance01';d.mkdir(exist_ok=True)
for n in ['app.js','generator.js','index.html','style.css']:shutil.copy2(src/n,d/n)
shutil.copytree(src/'assets',d/'assets',dirs_exist_ok=True)
p=d/'generator.js';s=p.read_text(encoding='utf-8')
needle='map.exit={x:far%w,y:Math.floor(far/w)};'
s=s.replace(needle,needle+'''
 // A reachable threshold beneath a solid 3x2 facade replaces the floor stair icon.
 const doors=[];for(let y=2;y<h-3;y++)for(let x=2;x<w-4;x++){
  let ok=true;for(let yy=y;yy<y+2;yy++)for(let xx=x;xx<x+3;xx++)if(cells[yy*w+xx]!==WALL)ok=false;
  for(let xx=x;xx<x+3;xx++)if(cells[(y+2)*w+xx]!==FLOOR)ok=false;
  const p=map.prefab;if(x<p.x+p.w+1&&x+3>p.x-1&&y<p.y+p.h+1&&y+2>p.y-1)ok=false;
  const distance=b.dist[(y+2)*w+x+1];if(ok&&distance>=18)doors.push({x,y,w:3,h:2,distance});
 }
 doors.sort((a,b)=>b.distance-a.distance);if(!doors.length)continue;
 map.exitDoor=doors[0];map.exit={x:map.exitDoor.x+1,y:map.exitDoor.y+2};far=map.exit.y*w+map.exit.x;
''')
p.write_text(s,encoding='utf-8')
p=d/'app.js';s=p.read_text(encoding='utf-8')
s=s.replace("if(x>=p.x-1&&x<=p.x+p.w&&y>=p.y-1&&y<=p.y+p.h)continue;", "if(x>=p.x-1&&x<=p.x+p.w&&y>=p.y-1&&y<=p.y+p.h)continue;const e=map.exitDoor;if(e&&x>=e.x-1&&x<=e.x+e.w&&y>=e.y-1&&y<=e.y+e.h)continue;")
s=s.replace("ctx.drawImage(images.stairs,map.exit.x*t,map.exit.y*t,t,t);", "const door=map.exitDoor;texture([326,57,105,73],door.x*t,door.y*t,door.w*t,door.h*t);ctx.fillStyle='#bab1a0';ctx.fillRect(map.exit.x*t+t*.14,map.exit.y*t,t*.72,Math.max(1,t*.09));ctx.fillStyle='#8fd0cd';ctx.beginPath();ctx.moveTo(map.exit.x*t+t*.35,map.exit.y*t+t*.23);ctx.lineTo(map.exit.x*t+t*.65,map.exit.y*t+t*.23);ctx.lineTo(map.exit.x*t+t*.5,map.exit.y*t+t*.39);ctx.closePath();ctx.fill();")
s=s.replace("'출구 도착! 다른 지도도 만들어보세요.'","'会場入口 · 다음 층 입구 도착! 층 이동은 아직 연결 전이에요.'")
insert="""
function showExit(){stop();stage=4;overview=false;const e=map.exit,choices=[];for(let y=1;y<map.h-1;y++)for(let x=1;x<map.w-1;x++)if(map.cells[y*map.w+x]===G.FLOOR)choices.push({x,y,score:Math.abs(x-e.x)+Math.abs(y-(e.y+3))});choices.sort((a,b)=>a.score-b.score);player={x:choices[0].x,y:choices[0].y};draw();$('message').textContent='다음 층 입구 미리보기 · 문 앞 청록 표시 칸이 기존 내려가는 계단 자리예요.';}
$('exitView').onclick=showExit;
"""
s=s.replace('Promise.all(Object.entries(sources)',insert+'Promise.all(Object.entries(sources)')
s=s.replace("if(location.hash==='#fence')showFence();","if(location.hash==='#fence')showFence();if(location.hash==='#exit')showExit();")
s=s.replace('window.previewApp={showFence,','window.previewApp={showExit,showFence,').replace('exit:map?.exit,','exit:map?.exit,exitDoor:map?.exitDoor,')
p.write_text(s,encoding='utf-8')
p=d/'index.html';s=p.read_text(encoding='utf-8').replace('<button id="fenceView">','<button id="exitView">다음 층 입구 보기</button><button id="fenceView">').replace('v=fence-alpha01','v=entrance01').replace('잔향도시 · 골목의 벽장식','잔향도시 · 다음 층으로 가는 입구').replace('내려가는 계단','다음 층 입구')
p.write_text(s,encoding='utf-8')
for source,target in [('test-street-walls01.cjs','test-street-entrance01.cjs'),('check-street-walls01.cjs','check-street-entrance01.cjs')]:
 s=(r/'scripts'/source).read_text(encoding='utf-8-sig').replace('street-walls01','street-entrance01').replace('8790/','8791/')
 if source.startswith('test-'):s=s.replace('assert(m.prefab);',"assert(m.prefab);assert(m.exitDoor);assert(m.exit.x===m.exitDoor.x+1&&m.exit.y===m.exitDoor.y+2);for(let yy=m.exitDoor.y;yy<m.exitDoor.y+2;yy++)for(let xx=m.exitDoor.x;xx<m.exitDoor.x+3;xx++)assert.strictEqual(m.cells[yy*m.w+xx],g.WALL);")
 (r/'scripts'/target).write_text(s,encoding='utf-8')
capture=(r/'scripts/capture-street-fence01.cjs').read_text(encoding='utf-8').replace('street-walls01','street-entrance01').replace('8790/?v=fence-view#fence','8791/?v=entrance01#exit').replace('fence-field.png','entrance-field.png')
(r/'scripts/capture-street-entrance01.cjs').write_text(capture,encoding='utf-8')
print('Created entrance preview.')
