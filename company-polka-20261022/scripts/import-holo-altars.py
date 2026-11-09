"""Slice the generated altar atlas into native transparent 32px tiles."""
from pathlib import Path
from PIL import Image, ImageDraw
import shutil, json, hashlib, sys

root=Path(__file__).resolve().parents[1]
out=root/'assets/holocrawl/altars01'
out.mkdir(parents=True,exist_ok=True)
original=out/'original-atlas.png'
if len(sys.argv)>1:shutil.copy2(sys.argv[1],original)
atlas=Image.open(original).convert('RGBA')
gods='suisei miko aki fubuki ayame choco korone okayu pekora noel watame towa lamy polka koyori lui raden hajime su vivi sopia mela'.split()
target=root/'engine/campaign-crawl/crawl-ref/source/rltiles/holo'
preview=Image.new('RGBA',(8*128,3*152),(26,26,34,255))
draw=ImageDraw.Draw(preview)
assets=[]
for i,g in enumerate(gods):
    x,y=i%8,i//8
    tile=atlas.crop((round(x*atlas.width/8),round(y*atlas.height/3),round((x+1)*atlas.width/8),round((y+1)*atlas.height/3)))
    box=tile.getchannel('A').getbbox()
    assert box,(g,'empty generated cell')
    tile=tile.crop(box)
    tile.thumbnail((30,30),Image.Resampling.NEAREST)
    native=Image.new('RGBA',(32,32))
    native.paste(tile,((32-tile.width)//2,31-tile.height))
    path=target/f'altar_{g}.png'
    native.save(path)
    assert native.getchannel('A').getextrema()[0]==0
    preview.alpha_composite(native.resize((128,128),Image.Resampling.NEAREST),(x*128,y*152))
    draw.text((x*128+4,y*152+132),g,fill='white')
    assets.append(dict(god=g,path=path.relative_to(root).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest().upper()))
assert len({a['sha256'] for a in assets})==22
preview.save(out/'native-preview.png')
(out/'manifest.json').write_text(json.dumps(dict(tool='built-in image_gen',nativeSize=[32,32],assets=assets),indent=2)+'\n',encoding='utf-8')
print('Imported 22 unique RGBA altar structures; original atlas alpha preserved.')
