from pathlib import Path
from PIL import Image
import json,shutil,hashlib
r=Path(__file__).resolve().parents[1];rev='lui-ganmo02';s=r/'engine/campaign-crawl/crawl-ref/source';b=r/'analysis/native'/rev;a=r/'assets/holocrawl'/rev
a.mkdir(parents=True,exist_ok=True);(b/'before/rltiles/holo').mkdir(parents=True,exist_ok=True)
generated=Path('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0')
sources={'body0':'exec-66359911-4544-42f3-ac8d-a82cb6e33393.png','body1':'exec-bb9bb9dd-a421-4eb2-bc85-cd283903cccc.png','altar':'exec-9f6d5c53-b6ed-4abc-9578-3ba2bc47992e.png'}
for name,fn in sources.items():shutil.copy2(generated/fn,a/f'{name}-source.png')
shutil.copy2(Path('C:/Users/071staff/AppData/Local/Temp/lui-official-ganmo.png'),a/'official-reference.png')
def fit(name,size,at=None,bottom=False):
 im=Image.open(a/f'{name}-source.png').convert('RGBA');bounds=im.getchannel('A').point(lambda value: 255 if value>32 else 0).getbbox();im=im.crop(bounds);im.thumbnail(size,Image.Resampling.NEAREST)
 tile=Image.new('RGBA',(32,32));xy=at or ((32-im.width)//2,31-im.height if bottom else (32-im.height)//2);tile.alpha_composite(im,xy);return tile
tiles={}
for i in range(2):
 tiles['raven'+('_1' if i else '')+'.png']=fit(f'body{i}',(30,30),bottom=True)
 tiles[f'fx_ravenflight_{i}.png']=fit(f'body{i}',(30,30))
 tiles[f'fx_night_lui1_{i}.png']=fit(f'body{i}',(12,14),at=(18,0))
tiles['god_lui.png']=fit('body0',(24,28));tiles['charm_lui.png']=fit('body0',(7,7),at=(24,3));tiles['altar_lui.png']=fit('altar',(25,28),bottom=True)
for name,im in tiles.items():
 p=s/'rltiles/holo'/name;shutil.copy2(p,b/'before/rltiles/holo'/name);im.save(p)
preserved={str(p.relative_to(s)):hashlib.sha256(p.read_bytes()).hexdigest() for p in s.rglob('*') if p.is_file() and (p.suffix in ['.cc','.h'] or 'rltiles/holo' in p.as_posix()) and p.name not in tiles}
(b/'preserved-files.json').write_text(json.dumps(preserved,indent=2))
placement=dict(bodyMax=[30,30],badgeMax=[12,14],badgeAt=[18,0],altarMax=[25,28],portraitMax=[24,28],resampling='nearest',reference='https://shop.hololivepro.com/products/takanelui_bd2022')
(a/'placement.json').write_text(json.dumps(placement,indent=2))
sheet=Image.new('RGBA',(32*len(tiles),32),(24,28,35,255))
for i,im in enumerate(tiles.values()):sheet.alpha_composite(im,(32*i,0))
sheet.resize((32*len(tiles)*4,128),Image.Resampling.NEAREST).save(a/'contact.png')
ps=(r/'scripts/capture-lui-hawk01.ps1').read_text(encoding='utf-8').replace('lui-hawk01',rev);(r/f'scripts/capture-{rev}.ps1').write_text(ps,encoding='utf-8')
print('Ganmo native tiles prepared; gameplay source preserved.')

