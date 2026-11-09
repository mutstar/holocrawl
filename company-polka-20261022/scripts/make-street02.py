from pathlib import Path
import shutil
r=Path(__file__).resolve().parents[1]
src=r/'analysis/previews/street-generator01'; dst=r/'analysis/previews/street-generator02'
dst.mkdir(exist_ok=True)
for name in ['index.html','style.css','app.js','generator.js']:shutil.copy2(src/name,dst/name)
shutil.copytree(src/'assets',dst/'assets',dirs_exist_ok=True)
p=dst/'generator.js';s=p.read_text(encoding='utf-8')
s=s.replace('w=42,h=28','w=80,h=70').replace('depth>=4','depth>=6')
s=s.replace('const wide=rng()<.3?2:1','const wide=rng()<.55?3:1').replace('if(wide===2)carve(x+1,y);','if(wide===3){carve(x+1,y);carve(x,y+1);carve(x+1,y+1);carve(x-1,y);carve(x,y-1);}')
s=s.replace('Math.floor(rooms.length/3)','Math.floor(rooms.length*.85)')
s=s.replace('const rng=random(`${seed}:${attempt}`),int=', 'const rng=random(`${seed}:expanded:${attempt}`),int=')
s=s.replace('const tree=split({x:1,y:1,w:w-2,h:h-2},0);map.roomCells=cells.slice();', '''const tree=split({x:2,y:2,w:w-4,h:h-4},0);
 map.layout=['広場','路地','街区'][Math.floor(rng()*3)];
 // Overlapping open courts break up the separated rectangular room pattern.
 for(let n=0;n<3;n++){const a=rooms[int(0,rooms.length-1)],rw=int(9,15),rh=int(7,12);for(let y=a.cy-Math.floor(rh/2);y<a.cy+Math.ceil(rh/2);y++)for(let x=a.cx-Math.floor(rw/2);x<a.cx+Math.ceil(rw/2);x++)carve(x,y);}
 map.roomCells=cells.slice();''')
s=s.replace('map.corridorCells=cells.slice();', '''// Wide routes link distant courts; buildings form islands with routes on both sides.
 const avenueCount=map.layout==='広場'?3:map.layout==='路地'?1:2;
 for(let n=0;n<avenueCount;n++){const a=rooms[int(0,rooms.length-1)],b=rooms[int(0,rooms.length-1)];corridor(a,b);}
 map.corridorCells=cells.slice();''')
s=s.replace('Math.min(9,safe.length)','Math.min(28,safe.length)').replace('safe.slice(9,15)','safe.slice(28,46)')
p.write_text(s,encoding='utf-8')
p=dst/'app.js';s=p.read_text(encoding='utf-8')
s=s.replace('overview?16:32','overview?Math.floor(Math.min(canvas.width/map.w,canvas.height/map.h)):32')
s=s.replace('const scale=6','const scale=Math.min(mini.width/map.w,mini.height/map.h)')
s=s.replace("else texture(roofPatch,px,py,t,t);", "else {texture(roofPatch,px,py,t,t);ctx.fillStyle='rgba(11,13,15,.72)';ctx.fillRect(px,py,t,t);}")
s=s.replace("'LIVE-001'","'CITY-001'").replace("'LIVE-'","'CITY-'")
s=s.replace("+'칸';$('validation')", "+'칸 / 80×70';$('validation')")
s=s.replace('rooms:map?.rooms.length','rooms:map?.rooms.length,width:map?.w,height:map?.h')
p.write_text(s,encoding='utf-8')
p=dst/'index.html';s=p.read_text(encoding='utf-8')
s=s.replace('같은 재료로, 매번 다른 거리','잔향도시 · 넓어진 거리와 골목').replace('LIVE-001','CITY-001').replace('width="252" height="168"','width="240" height="210"')
s=s.replace('지도를 새로 만들거나, 만들어지는 과정을 한 단계씩 살펴보세요.','80×70칸 지도 · 넓은 광장, 큰길과 뒷골목, 여러 갈래의 우회로를 탐험해보세요.')
s=s.replace('지금은 원리 시연이에요','돌죽 규모의 배치 실험').replace('길 생성·연결 검사·이동은 동작합니다.','돌죽 0.24와 같은 격자 크기로 확장한 별도 생성기입니다. 돌죽 원본 생성 알고리즘을 이식한 것은 아닙니다. 길 생성·연결 검사·이동은 동작합니다.')
p.write_text(s,encoding='utf-8')
print(dst)
