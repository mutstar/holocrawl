from pathlib import Path
from collections import deque
import json,shutil,random,math
root=Path(__file__).resolve().parents[1];src=root/'preview/city-random15';out=root/'preview/city-doors17';out.mkdir(exist_ok=True)
for name in ['index.html','app.js','boot.js','terrain.js','grounding.js','final-layout.js','wall-volume.js']:shutil.copyfile(src/name,out/name)
shutil.copyfile(root/'scripts/wall-volume01.js',out/'wall-volume.js')
shutil.copytree(src/'assets',out/'assets',dirs_exist_ok=True)
data=json.loads((src/'native-d1.json').read_text(encoding='utf-8'))
(out/'native-source.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
report=[]
for m in data['maps']:
 w,h=m['w'],m['h'];pal=m['palette'];rows=m['rows'];before=[r[:] for r in rows]
 def feature(x,y):return pal[before[y][x]] if 0<=x<w and 0<=y<h else 'rock_wall'
 def wall(x,y):return feature(x,y) in ['rock_wall','stone_wall']
 def floor(x,y):return feature(x,y)=='floor'
 existing=[(x,y) for y in range(h) for x in range(w) if 'door' in feature(x,y)]
 stairs=[(x,y) for y in range(h) for x in range(w) if 'stairs' in feature(x,y) or feature(x,y)=='exit_dungeon']
 # Wide interior regions are geometric room candidates, not fixed rectangular templates.
 wide={(x,y) for y in range(2,h-2) for x in range(2,w-2) if all(floor(x+dx,y+dy) for dy in [-1,0,1] for dx in [-1,0,1])}
 labels={};sizes={}
 for p in sorted(wide):
  if p in labels:continue
  label=len(sizes);q=deque([p]);labels[p]=label;size=0
  while q:
   x,y=q.popleft();size+=1
   for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]:
    n=(x+dx,y+dy)
    if n in wide and n not in labels:labels[n]=label;q.append(n)
  sizes[label]=size
 def room_on_side(x,y,dx,dy,sign):
  start=(x+dx*sign,y+dy*sign);q=deque([(start,0)]);seen={start}
  while q:
   (a,b),distance=q.popleft()
   if (a,b) in labels and sizes[labels[a,b]]>=3:return labels[a,b],distance
   if distance>=3:continue
   for xx,yy in [(a+1,b),(a-1,b),(a,b+1),(a,b-1)]:
    if ((xx-x)*dx+(yy-y)*dy)*sign<1 or not floor(xx,yy) or (xx,yy) in seen:continue
    seen.add((xx,yy));q.append(((xx,yy),distance+1))
  return None,99
 rng=random.Random(m['seed']+':room-doors17');density=rng.choice([.4,.55,.7]);candidates=[]
 for y in range(3,h-3):
  for x in range(3,w-3):
   if not floor(x,y) or any(max(abs(x-a),abs(y-b))<=3 for a,b in stairs):continue
   axes=[]
   if wall(x-1,y) and wall(x+1,y) and floor(x,y-1) and floor(x,y+1):axes.append((0,1))
   if wall(x,y-1) and wall(x,y+1) and floor(x-1,y) and floor(x+1,y):axes.append((1,0))
   if not axes:continue
   dx,dy=axes[0];left,ld=room_on_side(x,y,dx,dy,-1);right,rd=room_on_side(x,y,dx,dy,1)
   if left is None and right is None or left is not None and left==right or min(ld,rd)>1:continue
   if any(math.hypot(x-a,y-b)<3.5 for a,b in existing):continue
   candidates.append({'x':x,'y':y,'axis':'vertical' if dy else 'horizontal','rooms':[left,right],'distanceToRoom':min(ld,rd),'tie':rng.random()})
 # Collapse multiple adjacent positions along the same entrance to its closest throat.
 portals=[]
 for c in sorted(candidates,key=lambda c:(c['distanceToRoom'],c['tie'])):
  if any(math.hypot(c['x']-p['x'],c['y']-p['y'])<4 for p in portals):continue
  portals.append(c)
 selected=[p for p in portals if rng.random()<density]
 # A small fallback only when the entire floor has almost no doors; not a fixed target.
 if len(existing)+len(selected)<2:
  for p in portals:
   if p not in selected:selected.append(p)
   if len(existing)+len(selected)>=2:break
 if 'closed_door' not in pal:pal.append('closed_door')
 for p in selected:rows[p['y']][p['x']]=pal.index('closed_door');p.pop('tie',None)
 for y in range(h):
  for x in range(w):
   if rows[y][x]!=before[y][x]:assert feature(x,y)=='floor' and pal[rows[y][x]]=='closed_door'
 m['doorPlacement']={'originalCount':len(existing),'candidateEntrances':len(portals),'density':density,'added':selected,'total':len(existing)+len(selected),'rule':'probability at room entrances; preserve existing doors; small fallback only if total below two'}
 report.append({'seed':m['seed'],**m['doorPlacement']})
data.update(method='Native D:1 geometry with HoloCrawl room-entrance probabilistic door placement inspired by Crawl principles.',nativeTerrainUnchanged=False,wallGeometryUnchanged=True)
(out/'native-d1.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'native-d1.js').write_text('globalThis.NativeD1='+json.dumps(data,ensure_ascii=False)+';',encoding='utf-8')
(out/'door-placement17.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['app.js','index.html']:
 p=out/name;s=p.read_text(encoding='utf-8-sig').replace('holocrawl-city-random15','holocrawl-city-doors17').replace('잔향도시 1층 · 새 랜덤 지형','잔향도시 1층 · 방 입구 문 배치')
 if name=='index.html':s=s.replace('이번에 새로 생성한 원본 D:1 지형3개 중 선택하며','새 D:1 지형3개에 방 입구 문을 확률 배치했으며')
 p.write_text(s.replace('wall-volume.js?v=13','wall-volume.js?v=20'),encoding='utf-8')
shutil.copyfile(root/'scripts/glass-wall18.js',out/'glass-wall.js')
p=out/'index.html';s=p.read_text(encoding='utf-8').replace('<script src="boot.js','<script src="glass-wall.js?v=18"></script><script src="boot.js');p.write_text(s,encoding='utf-8')
shutil.copyfile(root/'scripts/showcase-joint19.js',out/'showcase-joint.js')
s=p.read_text(encoding='utf-8').replace('<script src="boot.js','<script src="showcase-joint.js?v=20"></script><script src="boot.js');p.write_text(s,encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
