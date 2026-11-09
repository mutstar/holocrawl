from pathlib import Path
r=Path(__file__).resolve().parents[1]; d=r/'analysis/previews/street-walls01'
p=d/'app.js';s=p.read_text(encoding='utf-8')
insert="""
function showFence(){stop();stage=4;overview=false;const fences=map.props.filter(p=>p.type==='fence');if(!fences.length){$('message').textContent='이 지도에는 펜스가 배치되지 않았어요.';return;}const f=fences[Math.floor(fences.length/2)],choices=[];for(let y=1;y<map.h-1;y++)for(let x=1;x<map.w-1;x++)if(map.cells[y*map.w+x]===G.FLOOR)choices.push({x,y,score:Math.abs(x-f.x)+Math.abs(y-(f.y+3))});choices.sort((a,b)=>a.score-b.score);player={x:choices[0].x,y:choices[0].y};draw();$('message').textContent='공연장 앞 미리보기 · 은빛 금속 펜스 3칸은 이동을 막으며 옆으로 돌아갈 수 있어요.';}
$('fenceView').onclick=showFence;
"""
s=s.replace('Promise.all(Object.entries(sources)',insert+'Promise.all(Object.entries(sources)')
s=s.replace("newMap('CITY-001');window.previewReady=true;","newMap('CITY-001');if(location.hash==='#fence')showFence();window.previewReady=true;")
s=s.replace('window.previewApp={newMap,','window.previewApp={showFence,newMap,')
p.write_text(s,encoding='utf-8')
p=d/'index.html';s=p.read_text(encoding='utf-8').replace('<button id="build">','<button id="fenceView">공연장·펜스 보기</button><button id="build">').replace('v=no-ticket','v=fence-view')
p.write_text(s,encoding='utf-8')
