from pathlib import Path
from collections import deque
import json,shutil,random
root=Path(__file__).resolve().parents[1];src=root/'preview/city-batch21';out=root/'preview/city-batch22';out.mkdir(exist_ok=True)
for name in ['index.html','app.js','boot.js','terrain.js','grounding.js','final-layout.js','wall-volume.js','glass-wall.js','showcase-joint.js']:shutil.copyfile(src/name,out/name)
shutil.copytree(src/'assets',out/'assets',dirs_exist_ok=True)
data=json.loads((src/'native-d1.json').read_text(encoding='utf-8'))
(out/'before-stairs.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copyfile(src/'native-source.json',out/'native-source.json')
dirs=[(dx,dy)for dy in [-1,0,1]for dx in [-1,0,1]if dx or dy]
rules={'entryMinSteps':18,'entryMinGridDistance':9,'downstairsMinSteps':14,'downstairsMinGridDistance':8,'stairsCount':'one entry, three downstairs','note':'HoloCrawl anti-clustering policy; not a claimed universal vanilla Crawl minimum distance.'}
reports=[]
for m in data['maps']:
 w,h=m['w'],m['h'];pal=m['palette'];rows=m['rows'];before=[r[:]for r in rows]
 def feature(p):
  x,y=p;return pal[rows[y][x]] if 0<=x<w and 0<=y<h else 'rock_wall'
 def walk(p):
  f=feature(p);return 'wall' not in f and f not in ['granite_statue','tree','deep_water']
 def dist(start):
  q=deque([start]);ds={start:0}
  while q:
   x,y=q.popleft()
   for dx,dy in dirs:
    p=(x+dx,y+dy)
    if p not in ds and 0<=p[0]<w and 0<=p[1]<h and walk(p):ds[p]=ds[x,y]+1;q.append(p)
  return ds
 def grid(a,b):return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
 entry=next((x,y)for y,row in enumerate(rows)for x,v in enumerate(row)if pal[v]=='exit_dungeon' or pal[v].startswith('stone_stairs_up'))
 stairs=[{'feature':pal[v],'old':(x,y)}for y,row in enumerate(rows)for x,v in enumerate(row)if pal[v].startswith('stone_stairs_down')]
 assert len(stairs)==3
 entry_dist=dist(entry);old_points=[s['old']for s in stairs]
 def metrics(points):
  pairs=[(a,b)for i,a in enumerate(points)for b in points[i+1:]]
  return {'entryMinSteps':min(entry_dist[p]for p in points),'entryMinGridDistance':min(grid(entry,p)for p in points),'downstairsMinSteps':min(dist(a)[b]for a,b in pairs),'downstairsMinGridDistance':min(grid(a,b)for a,b in pairs)}
 old_metrics=metrics(old_points)
 doors=[(x,y)for y,row in enumerate(rows)for x,v in enumerate(row)if 'door' in pal[v]]
 candidates=[(x,y)for y in range(2,h-2)for x in range(2,w-2)if feature((x,y))=='floor' and (x,y) in entry_dist and entry_dist[x,y]>=rules['entryMinSteps'] and grid(entry,(x,y))>=rules['entryMinGridDistance'] and all(grid((x,y),p)>3 for p in doors) and sum(walk((x+dx,y+dy))for dx,dy in dirs)>=5]
 rng=random.Random(m['seed']+':stair-spread22');rng.shuffle(candidates)
 chosen=[];chosen_dist=[]
 def valid(p):return entry_dist.get(p,-1)>=rules['entryMinSteps'] and grid(entry,p)>=rules['entryMinGridDistance'] and all(d.get(p,-1)>=rules['downstairsMinSteps'] and grid(p,q)>=rules['downstairsMinGridDistance']for q,d in zip(chosen,chosen_dist))
 # Keep valid native stairs; relocate only conflicting stairs, not every staircase.
 for stair in stairs:
  p=stair['old']
  if not valid(p):
   pool=[q for q in candidates if valid(q) and all(grid(q,s['old'])>1 for s in stairs if s['old']!=p)]
   if not pool:raise RuntimeError('Cannot spread stairs on '+m['seed'])
   p=pool[0]
  stair['new']=p;chosen.append(p);chosen_dist.append(dist(p))
 for s in stairs:
  if s['old']!=s['new']:x,y=s['old'];rows[y][x]=pal.index('floor')
 for s in stairs:x,y=s['new'];rows[y][x]=pal.index(s['feature'])
 after=metrics(chosen)
 for key in ['entryMinSteps','entryMinGridDistance','downstairsMinSteps','downstairsMinGridDistance']:assert after[key]>=rules[key]
 for y in range(h):
  for x in range(w):
   if rows[y][x]!=before[y][x]:assert pal[before[y][x]]=='floor' or pal[before[y][x]].startswith('stone_stairs_down')
 m['stairPlacement']={'entry':entry,'before':old_metrics,'after':after,'stairs':stairs,'moved':sum(s['old']!=s['new']for s in stairs),'rules':rules}
 reports.append({'seed':m['seed'],**m['stairPlacement']})
data.update(method='Native D:1 geometry plus HoloCrawl room-entry door pass17 and staircase anti-clustering pass22',stairPolicy=rules,wallGeometryUnchanged=True,nativeTerrainUnchanged=False)
(out/'native-d1.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'native-d1.js').write_text('globalThis.NativeD1='+json.dumps(data,ensure_ascii=False)+';',encoding='utf-8')
(out/'stairs-placement22.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['app.js','index.html']:
 p=out/name;s=p.read_text(encoding='utf-8-sig').replace('holocrawl-city-batch21','holocrawl-city-batch22').replace('랜덤 맵 8종','랜덤 맵 8종 · 계단 분산')
 p.write_text(s,encoding='utf-8')
print(json.dumps([{'seed':r['seed'],'moved':r['moved'],'before':r['before'],'after':r['after']}for r in reports],ensure_ascii=False))
