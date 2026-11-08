from pathlib import Path
import shutil,json,hashlib
R=Path(__file__).resolve().parents[1];A=R/'preview/wall-structures122'
for kind in ['street','market']:
 S=R/f'preview/city-{kind}121';O=R/f'preview/city-{kind}122';O.mkdir(exist_ok=True)
 for p in S.iterdir():
  if p.suffix in ['.js','.json','.html','.css'] and p.name not in ['validation.json','inputs.json']:shutil.copy2(p,O/p.name)
 p=O/'index.html';s=p.read_text(encoding='utf-8').replace('전체 세로 벽면22픽셀 통일121','22픽셀 벽 기준 구조물 정리122').replace('city-street121','city-street122').replace('city-market121','city-market122').replace('review121.js','review122.js').replace('app.js?v=121','app.js?v=122')
 s=s.replace('../wall-height121/mount121.js','../wall-structures122/structures122.js').replace('../wall-height121/street-comparison121.png','../wall-structures122/wall-structures122.png').replace('부분 높임과 비교','벽 구조물9종 확대')
 s=s.replace('바닥과 통로는 유지합니다.','유리·선반·걸이·셔터·설비를 새 벽면에 맞춰 정리했습니다. 바닥과 통로는 유지합니다.')
 if kind=='market':s=s.replace('<script src="layout115.js"></script>','<script src="layout115.js"></script><script src="../wall-structures122/infra122.js"></script><script src="../wall-structures122/market122.js"></script>').replace('<button id="marketView">','<button id="utilitiesView122">벽 설비 보기</button><button id="marketView">').replace('상점가121','상점가122')
 p.write_text(s,encoding='utf-8')
 if kind=='street':
  s=(S/'review121.js').read_text(encoding='utf-8').replace('play121','play122').replace('WallMount121','WallStructures122').replace('전면121','구조물122')
  (O/'review122.js').write_text(s,encoding='utf-8');(O/'review121.js').unlink()
  p=O/'manifest.json';a=json.loads(p.read_text(encoding='utf-8'));a['revision']=122;p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 else:
  p=O/'app.js';s=p.read_text(encoding='utf-8').replace('WallMount121','WallStructures122')
  needle=' for(const prop of map.props){'
  assert needle in s;s=s.replace(needle,' for(const unit of map.marketInfra||[])WallStructures122.drawUtility(ctx,unit,map,wallUnits122,t);\n'+needle,1)
  # Reuse the preserved utility art sources, prepare them once after loading.
  s=s.replace('Object.assign(sources,','Object.assign(sources,{pipe122:"../city-batch22/assets/wall-pipe-elbows10-96.png",cabinet122:"../city-batch22/assets/wall-cabinet08-32.png"});\nObject.assign(sources,',1)
  s=s.replace('const loadImage=','const wallUnits122={};\nfunction prepareUnits122(){for(const[type,crop]of Object.entries({air:[289,34,37,19],vent:[294,86,22,16]})){const c=document.createElement("canvas");c.width=c.height=32;const q=c.getContext("2d");q.imageSmoothingEnabled=false;const w=type==="air"?28:22,h=type==="air"?15:16;q.drawImage(images.reference,...crop,(32-w)/2,32-h-2,w,h);wallUnits122[type]=Market108.recolor(c,type);}wallUnits122.pipe=Market108.recolor(images.pipe122,"pipe");wallUnits122.cabinet=Market108.recolor(images.cabinet122,"cabinet");}\nconst loadImage=',1)
  s=s.replace('Market108.prepare(images);MarketStock.makeSprites','Market108.prepare(images);prepareUnits122();MarketStock.makeSprites',1)
  s+='''
const unitNames122={air:'실외기',vent:'환기구',cabinet:'배전함',pipe:'배관'};
document.getElementById('utilitiesView122').onclick=()=>{const unit=map.marketInfra?.find(p=>p.type==='pipe')||map.marketInfra?.[0];if(!unit)return;stop();stage=4;overview=false;const choices=[];for(let y=Math.max(1,unit.y-3);y<Math.min(map.h-1,unit.y+5);y++)for(let x=Math.max(1,unit.x-3);x<Math.min(map.w-1,unit.x+unit.length+3);x++)if(map.cells[y*map.w+x]===G.FLOOR)choices.push({x,y,d:Math.hypot(x-unit.x-unit.length/2,y-unit.y-2)});choices.sort((a,b)=>a.d-b.d);if(choices[0]){player={x:choices[0].x,y:choices[0].y};updateVision();draw();$('message').textContent='벽 설비가 있는 골목';}};
canvas.addEventListener('mousemove',event=>{if(!map)return;const r=canvas.getBoundingClientRect(),sx=(event.clientX-r.left)*canvas.width/r.width,sy=(event.clientY-r.top)*canvas.height/r.height,{t,ox,oy,cx,cy}=transform,x=Math.floor((sx-ox)/t)+cx,y=Math.floor((sy-oy)/t)+cy,p=map.marketInfra?.find(p=>p.y===y&&x>=p.x&&x<p.x+p.length);if(p)$('stockInfo').textContent=unitNames122[p.type];});
'''
  p.write_text(s,encoding='utf-8')
inputs={'revision':122,'wallBaseline':121,'wallHeight':22,'nativeIntegrated':False,'floorPropRevision':117,'geometryChanged':False,'sourceFiles':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for n in ['city-street121','city-market121','wall-height121'] for p in (R/'preview'/n).iterdir() if p.suffix in ['.js','.json','.html','.css','.png']}}
(A/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n',encoding='utf-8')
print('Prepared1-7F wall structures122 on approved wall121; market infrastructure added without collision changes.')
