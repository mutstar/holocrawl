"""Uniform22px front for a reversible browser study; no native engine writes."""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'preview/wall-height121';O.mkdir(exist_ok=True)
source=(R/'scripts/city_concrete_material92.py').read_text(encoding='utf-8')
# Keep the approved material/4px coping/concave repair. Change the common
# front plane and the corresponding convex-side taper together.
code=source.replace('py>=18','py>=10').replace('py-18','py-10').replace('*3//13','*3//21').replace('y*32+18:y*32+32','y*32+10:y*32+32')
code=code.replace('return a,wall,repaired',"return a,wall,repaired,{'front':front,'side':side,'cap':cap,'rim':rim}")
namespace={};exec(compile(code,'material121-derived','exec'),namespace);render=namespace['render']
grain=np.array(Image.open(R/'preview/native-water02/assets/concrete-wall-surface256.png').convert('RGB'))
dirs=[(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]
atlas=Image.new('RGBA',(512,4096));rects={};planes={}
for variant in range(8):
 texture=np.roll(np.roll(grain,variant*32,axis=1),(variant*3%8)*32,axis=0)
 for mask in range(256):
  rows=[list('.....') for _ in range(5)];rows[2][2]='#'
  for bit,(dx,dy) in enumerate(dirs):
   if mask&(1<<bit):rows[2+dy][2+dx]='#'
  a,wall,repair,masks=render(np.full((160,160,4),255,dtype='uint8'),[''.join(r) for r in rows],texture)
  tile=Image.fromarray(a).crop((64,64,96,96));assert tile.getextrema()[3]==(255,255)
  index=variant*256+mask;x=index%16*32;y=index//16*32;atlas.paste(tile,(x,y));rects[f'{mask}:{variant}']=[x,y,32,32]
  if variant==0:planes[str(mask)]=''.join('1' if b else '0' for b in masks['front'][64:96,64:96].flat)
atlas.save(O/'wall22.png');(O/'rects121.json').write_text(json.dumps(rects,separators=(',',':'))+'\n',encoding='utf-8');(O/'planes121.json').write_text(json.dumps(planes,separators=(',',':'))+'\n',encoding='utf-8')
old=json.loads((R/'preview/city-market120/wall92.json').read_text(encoding='utf-8'))
lookup={','.join(map(str,rect[:2])):rects[key] for key,rect in old.items()};assert len(lookup)==2048
(O/'native-lookup121.json').write_text(json.dumps(lookup,separators=(',',':'))+'\n',encoding='utf-8')
for kind in ['street','market']:
 S=R/f'preview/city-{kind}120';D=R/f'preview/city-{kind}121';D.mkdir(exist_ok=True)
 for p in S.iterdir():
  if p.suffix in ['.js','.json','.html','.css'] and p.name not in ['validation.json','inputs.json']:shutil.copy2(p,D/p.name)
 p=D/'index.html';s=p.read_text(encoding='utf-8').replace('높인 벽 전면과 소품 크기120','전체 세로 벽면22픽셀 통일121').replace('city-street120','city-street121').replace('city-market120','city-market121').replace('review120.js','review121.js').replace('app.js?v=120','app.js?v=121')
 s=s.replace('<script src="../wall-bay120/bay120.js"></script>','<script src="../wall-height121/wall121.js"></script><script src="../wall-height121/mount121.js"></script>')
 s=s.replace('../wall-bay120/size-comparison120.png','../wall-height121/street-comparison121.png')
 s=s.replace('벽 부착9종 전후 비교','부분 높임과 비교').replace('벽92·문101·상점가120','벽121(22px)·문101·상점가121')
 s=s.replace('소품을 크게 되돌리고, 소품이 붙는 구간만 실제 벽 전면을 높여 받쳐주는 비교 시안입니다. 일반 벽과 바닥 소품은 유지합니다.','일반 벽의 세로 면을14→22픽셀로 통일했습니다. 진열장 뒤만 솟는 부분 없이 같은 마감선으로 연결합니다. 바닥과 통로는 유지합니다.')
 s=s.replace('진열창과 설비가 붙은 부분의 실제 벽 전면을 높여 소품 크기를 회복한 비교 시안입니다.','모든 일반 벽의 세로 면을22픽셀로 통일해 ㄱ자와 모서리를 같은 높이로 연결하는 비교 시안입니다.')
 p.write_text(s,encoding='utf-8')
 if kind=='market':
  p=D/'app.js';s=p.read_text(encoding='utf-8').replace('WallBay120','WallMount121').replace('Scene117.load(),Market108.load(),','Scene117.load(),Market108.load(),WallHeight121.load(),').replace('Market108.prepare(images);MarketStock.makeSprites','WallHeight121.installMarket();Market108.prepare(images);MarketStock.makeSprites')
  p.write_text(s,encoding='utf-8')
 else:
  s=(S/'review120.js').read_text(encoding='utf-8').replace('play120','play121').replace('WallBay120','WallMount121').replace('전면120','전면121').replace('벽92/문101/시설106','전체벽22px121/문101/시설106')
  s=s.replace('Market108.load(),Scene117.load(),','Market108.load(),WallHeight121.load(),Scene117.load(),')
  s=s.replace('function tile(t,x,y,s){g.drawImage','function tile(t,x,y,s){if(WallHeight121.nativeTile(g,t,x,y,s))return;g.drawImage')
  (D/'review121.js').write_text(s,encoding='utf-8');(D/'review120.js').unlink()
  p=D/'manifest.json';a=json.loads(p.read_text(encoding='utf-8'));a['revision']=121;a['browserWallMaterial']=121;a['frontHeight']=22;a['source']='Native107 map/physics; browser-only wall22px121 material replacement.';p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inputs={'revision':121,'frontHeight':22,'frontStart':10,'copingWidth':4,'sideWidth':3,'nativeIntegrated':False,'geometryChanged':False,'sourceFiles':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for name in ['city-street120','city-market120','wall-bay120'] for p in (R/'preview'/name).iterdir() if p.suffix in ['.js','.json','.html','.css']},'material92Sha256':hashlib.sha256(source.encode()).hexdigest()}
(O/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n',encoding='utf-8')
print('Prepared2048 uniformly22px wall tiles and street/market121 previews.')
