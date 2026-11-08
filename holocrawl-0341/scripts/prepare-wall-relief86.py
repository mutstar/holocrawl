"""Local art proposal for the user's inverted-L wall. Do not change audited art84."""
from pathlib import Path
from collections import deque
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

root=Path(__file__).resolve().parents[1]
source=root/'preview/wall-audit85'
output=root/'preview/wall-relief86'
output.mkdir(parents=True,exist_ok=True)
raw=source/'maps/map-802302584-1.json'
data=json.loads(raw.read_text())
atlases={name:Image.open(source/f'assets/{name}.png').convert('RGBA') for name in ['floor','wall','feat']}
canvas=Image.new('RGBA',(data['width']*32,data['height']*32))
for y in range(data['height']):
 for x in range(data['width']):
  for layer in ['floors','features']:
   tile=data['palette'][data[layer][y*data['width']+x]]
   image=atlases[tile['atlas']].crop((tile['sx'],tile['sy'],tile['sx']+tile['width'],tile['sy']+tile['height']))
   canvas.alpha_composite(image,(x*32+tile['dx'],y*32+tile['dy']))

anchor=(33,36);cells=set();queue=deque([anchor])
while queue:
 x,y=queue.popleft()
 if (x,y) in cells or not (0<=x<data['width'] and 0<=y<data['height']) or data['rows'][y][x]!='#':continue
 cells.add((x,y));queue.extend([(x-1,y),(x+1,y),(x,y-1),(x,y+1)])
expected={(33,y) for y in range(36,42)}|{(x,y) for x in [31,32] for y in range(39,42)}
assert cells==expected and len(cells)==12

before=np.array(canvas.convert('RGBA'));after=before.copy();west_profile=[25,43,61,59,48,39];north_profile=[25,42,55,47,38]
solid=lambda x,y:0<=x<data['width'] and 0<=y<data['height'] and data['rows'][y][x] in '#G+'
for x,y in cells:
 n,w=solid(x,y-1),solid(x-1,y)
 for py in range(32):
  for px in range(32):
   west=west_profile[px] if not w and px<len(west_profile) else 0
   north=north_profile[py] if not n and py<len(north_profile) else 0
   if not (west or north):continue
   # Keep the existing south front and east side completely intact.
   if py>=18 and not solid(x,y+1) or px>=28 and not solid(x+1,y):continue
   sample=before[y*32+min(py,15),x*32+12,:3].astype(float)
   grain=(sample-np.array([38,39,35]))*.8
   color=np.array([1,.92,.82])*max(west,north)+grain
   after[y*32+py,x*32+px,:3]=np.clip(np.round(color),0,255).astype('uint8')

changed=np.any(before!=after,axis=2)
allowed=np.zeros(changed.shape,dtype=bool)
for x,y in cells:allowed[y*32:(y+1)*32,x*32:(x+1)*32]=True
assert not np.any(changed&~allowed)
assert np.array_equal(before[~allowed],after[~allowed])
assert np.array_equal(before[:,:,3],after[:,:,3])
for x,y in cells:
 if not solid(x,y+1):assert np.array_equal(before[y*32+18:(y+1)*32,x*32:(x+1)*32],after[y*32+18:(y+1)*32,x*32:(x+1)*32])
 if not solid(x+1,y):assert np.array_equal(before[y*32:(y+1)*32,x*32+28:(x+1)*32],after[y*32:(y+1)*32,x*32+28:(x+1)*32])
crop=(29*32,35*32,36*32,44*32)
Image.fromarray(before).crop(crop).convert('RGB').save(output/'before.png')
Image.fromarray(after).crop(crop).convert('RGB').save(output/'after.png')
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',21)
board=Image.new('RGB',(940,650),'#141c20');draw=ImageDraw.Draw(board)
for index,(name,title) in enumerate([('before','현재 벽 84'),('after','뒤집힌 ㄴ자 · 국소 명암 시안')]):
 draw.text((20+index*470,15),title,font=font,fill='#d5e3dc')
 image=Image.open(output/f'{name}.png').resize((448,576),Image.Resampling.NEAREST)
 board.paste(image,(12+index*470,58))
board.save(output/'comparison.png')
result={'status':'passed','scope':'Local browser art proposal only; audited native art84 is unchanged.',
 'seed':data['seed'],'anchor':list(anchor),'selectedWallCells':len(cells),'cells':[list(p) for p in sorted(cells)],
 'changedPixels':int(changed.sum()),'outsideSelectionChangedPixels':0,'alphaUnchanged':True,
 'nativeMapSha256':hashlib.sha256(raw.read_bytes()).hexdigest(),
 'baseWallAtlasSha256':hashlib.sha256((source/'assets/wall.png').read_bytes()).hexdigest(),
 'baseFrontAndEastSidePreserved':True}
(output/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
(root/'analysis/wall-relief86/validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','selectedWallCells','changedPixels','outsideSelectionChangedPixels']}))
