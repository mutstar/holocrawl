"""Import only the three requested altar replacements; retain other PNG bytes."""
from pathlib import Path
from PIL import Image, ImageDraw
import json,hashlib,shutil,sys

root=Path(__file__).resolve().parents[1]
out=root/'assets/holocrawl/altars03';out.mkdir(parents=True,exist_ok=True)
original=out/'original-atlas.png'
if len(sys.argv)>1:shutil.copy2(sys.argv[1],original)
atlas=Image.open(original).convert('RGBA')
src=root/'engine/campaign-crawl/crawl-ref/source'
gods='suisei miko aki fubuki ayame choco korone okayu pekora noel watame towa lamy polka koyori lui raden hajime su vivi sopia mela'.split()
selected={'suisei','lamy','mela'}
previous=json.loads((root/'analysis/native/altars02/checkpoint.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
for i,g in enumerate(gods):
    path=src/'rltiles/holo'/f'altar_{g}.png'
    if g not in selected:
        assert sha(path)==previous['sourceSha256'][path.relative_to(src).as_posix()],g
        continue
    x,y=i%8,i//8
    row_bounds=[0,round(atlas.height*17/48),round(atlas.height*2/3),atlas.height]
    tile=atlas.crop((round(x*atlas.width/8),row_bounds[y],round((x+1)*atlas.width/8),row_bounds[y+1]))
    box=tile.getchannel('A').getbbox();assert box,g
    tile=tile.crop(box);tile.thumbnail((30,30),Image.Resampling.NEAREST)
    native=Image.new('RGBA',(32,32))
    native.paste(tile,((32-tile.width)//2,31-tile.height))
    native.save(path)
preview=Image.new('RGBA',(8*128,3*152),(26,26,34,255));draw=ImageDraw.Draw(preview)
detail=Image.new('RGBA',(3*192,220),(26,26,34,255));dd=ImageDraw.Draw(detail)
assets=[];j=0
for i,g in enumerate(gods):
    path=src/'rltiles/holo'/f'altar_{g}.png';native=Image.open(path).convert('RGBA')
    preview.alpha_composite(native.resize((128,128),Image.Resampling.NEAREST),(i%8*128,i//8*152))
    draw.text((i%8*128+4,i//8*152+132),g,fill='white')
    if g in selected:
        detail.alpha_composite(native.resize((192,192),Image.Resampling.NEAREST),(j*192,0));dd.text((j*192+8,200),g,fill='white');j+=1
    assets.append(dict(god=g,path=path.relative_to(root).as_posix(),sha256=sha(path),changed=g in selected))
preview.save(out/'native-preview.png');detail.save(out/'changed-preview.png')
(out/'manifest.json').write_text(json.dumps(dict(tool='built-in image_gen',nativeSize=[32,32],changedGods=sorted(selected),assets=assets),indent=2)+'\n',encoding='utf-8')
print('Imported Suisei, Lamy, Mela; other 19 native PNGs unchanged.')
