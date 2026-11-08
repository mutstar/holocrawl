"""New review pages. Approved wall121/structures122 and prior reviews stay immutable."""
from pathlib import Path
import shutil,json,hashlib
R=Path(__file__).resolve().parents[1]
for kind in ['street','market']:
 s=R/f'preview/city-{kind}123';d=R/f'preview/city-{kind}124';d.mkdir(exist_ok=True)
 for p in s.iterdir():
  if p.suffix in ['.js','.json','.html','.css'] and p.name not in ['validation.json','inputs.json']:shutil.copy2(p,d/p.name)
 p=d/'index.html';v=p.read_text(encoding='utf-8').replace('city-street123','city-street124').replace('city-market123','city-market124').replace('깔끔한 거리와 밀집 상점가123','통로를 비운 거리와 상점가124').replace('배치 구분123','안전 배치124')
 if kind=='street':
  v=v.replace('<script src="review123.js">','<script src="../passage-safe124/passage124.js"></script><script src="../passage-safe124/street124.js"></script><script src="../facility-exteriors124/facility124.js"></script><script src="review124.js">')
  q=d/'review124.js';t=(d/'review123.js').read_text(encoding='utf-8').replace('play123','play124').replace('Scene117.draw(q,p,stock,images,32,0)','Passage124.drawFloor(q,p,stock,images,32,0)').replace('WallHeight121.load(),','WallHeight121.load(),Facility124.load(),').replace('if(map.overlays[i]>=0)tile(map.palette[map.overlays[i]],dx,dy,s);','if(!Facility124.drawOverlay(g,map,x,y,dx,dy,s)&&map.overlays[i]>=0)tile(map.palette[map.overlays[i]],dx,dy,s);').replace('시설106 + 세로 벽면 거리 구분123 검토','시설124 · 좁은 길을 비운 배치124')
  q.write_text(t,encoding='utf-8');(d/'review123.js').unlink()
  m=json.loads((d/'manifest.json').read_text(encoding='utf-8'));m['revision']=124
  forced=json.loads((R/'preview/native-play107/manifest.json').read_text(encoding='utf-8'))['maps']
  m['maps'] += [{**a,'file':'../native-play107/'+a['file'],'probe':'../native-play107/'+a['probe']} for a in forced if a['forced'] and a['depth']==1]
  (d/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 else:
  v=v.replace('<script src="visibility-paths.js">','<script src="../passage-safe124/passage124.js"></script><script src="../passage-safe124/market124.js"></script><script src="visibility-paths.js">').replace('app.js?v=123','app.js?v=124')
  q=d/'app.js';t=q.read_text(encoding='utf-8').replace('Scene117.draw(ctx,prop,map,images,t,stockMix)','Passage124.drawFloor(ctx,prop,map,images,t,stockMix)');q.write_text(t,encoding='utf-8')
 v=v.replace('바닥과 통로는 유지합니다.','좁은 길과 계단·문 앞을 비우고, 공간이 부족한 소품은 생략합니다. 종이 잔해는 통과할 수 있습니다.')
 v=v.replace('</footer>',' · <a href="../facility-exteriors124/">고정지형9곳 외벽 각각 보기</a></footer>')
 p.write_text(v,encoding='utf-8')
O=R/'preview/passage-safe124'
plan={'revision':124,'scope':'Browser navigation placement; no native engine/save writes','nativeExistingGeometries':36,'nativePlacementVariations':6,'marketFreshSeeds':50,'marketFloors':[4,5,6,7],'seedPrefix':'SAFE124-20261109-','checks':['wall121 and structures122 hashes unchanged','one/two-cell corridors and corners protected','doors/stairs radius3','2x2 anchor components remain connected','six spread anchors to all remaining cells detour <=2','final local portals detour <=2','paper passable','deterministic replay'],'frozenInputs':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['wall-height121','wall-structures122','district-contrast123'] for p in (R/'preview'/folder).iterdir() if p.is_file()}}
(O/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Prepared street124 / market124; plan saved before cohort.')
