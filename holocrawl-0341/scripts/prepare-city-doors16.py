from pathlib import Path
import json,shutil,random,math
root=Path(__file__).resolve().parents[1];src=root/'preview/city-random15';out=root/'preview/city-doors16';out.mkdir(exist_ok=True)
for name in ['index.html','app.js','boot.js','terrain.js','grounding.js','final-layout.js','wall-volume.js']:
 shutil.copyfile(src/name,out/name)
shutil.copytree(src/'assets',out/'assets',dirs_exist_ok=True)
data=json.loads((src/'native-d1.json').read_text(encoding='utf-8'))
(out/'native-source.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
report=[]
for m in data['maps']:
 w,h=m['w'],m['h'];pal=m['palette'];rows=m['rows'];before=[r[:] for r in rows]
 def feature(x,y):return pal[rows[y][x]] if 0<=x<w and 0<=y<h else 'rock_wall'
 def wall(x,y):return feature(x,y) in ['rock_wall','stone_wall']
 def floor(x,y):return feature(x,y)=='floor'
 existing=[(x,y) for y in range(h) for x in range(w) if 'door' in feature(x,y)]
 stairs=[(x,y) for y in range(h) for x in range(w) if 'stairs' in feature(x,y) or feature(x,y)=='exit_dungeon']
 if 'closed_door' not in pal:pal.append('closed_door')
 rng=random.Random(m['seed']+':door-pass16');candidates=[]
 for y in range(3,h-3):
  for x in range(3,w-3):
   if not floor(x,y) or any(max(abs(x-a),abs(y-b))<=3 for a,b in stairs):continue
   axes=[]
   if wall(x-1,y) and wall(x+1,y) and floor(x,y-1) and floor(x,y+1):axes.append((0,1))
   if wall(x,y-1) and wall(x,y+1) and floor(x-1,y) and floor(x+1,y):axes.append((1,0))
   if not axes:continue
   dx,dy=axes[0];openness=[]
   for direction in [-1,1]:
    a,b=x+direction*dx*2,y+direction*dy*2
    openness.append(sum(floor(a+xx,b+yy) for xx,yy in [(-1,0),(1,0),(0,-1),(0,1)]))
   # Prioritize the throat between a room and a corridor over a long uniform hallway.
   candidates.append((max(openness)+abs(openness[0]-openness[1])+rng.random(),x,y,dx,dy))
 added=[];target=6
 for score,x,y,dx,dy in sorted(candidates,reverse=True):
  if len(existing)+len(added)>=target:break
  if any(math.hypot(x-a,y-b)<6 for a,b in existing+[(p['x'],p['y'])for p in added]):continue
  rows[y][x]=pal.index('closed_door');added.append({'x':x,'y':y,'axis':'vertical' if dy else 'horizontal'})
 assert len(existing)+len(added)>=4, f'Insufficient door sites on {m["seed"]}'
 for y in range(h):
  for x in range(w):
   if rows[y][x]!=before[y][x]:assert pal[before[y][x]]=='floor' and feature(x,y)=='closed_door'
 m['doorPlacement']={'originalCount':len(existing),'added':added,'total':len(existing)+len(added)}
 report.append({'seed':m['seed'],**m['doorPlacement']})
data['method']='Native D:1 geometry with an explicit HoloCrawl door placement pass; only selected floor cells become closed doors.'
data['nativeTerrainUnchanged']=False;data['wallGeometryUnchanged']=True
(out/'native-d1.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'native-d1.js').write_text('globalThis.NativeD1='+json.dumps(data,ensure_ascii=False)+';',encoding='utf-8')
(out/'door-placement16.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['app.js','index.html']:
 p=out/name;s=p.read_text(encoding='utf-8-sig').replace('holocrawl-city-random15','holocrawl-city-doors16').replace('잔향도시 1층 · 새 랜덤 지형','잔향도시 1층 · 길목 문 배치')
 if name=='index.html':s=s.replace('장식은','장식은').replace('새로 생성한 원본 D:1 지형3개 중 선택하며','새 D:1 지형3개에 길목 문 배치를 추가했으며')
 p.write_text(s,encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
