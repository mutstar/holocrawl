from pathlib import Path
from PIL import Image
import json,shutil,hashlib
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source';run=root/'analysis/native/towa-support03'
run.mkdir();(run/'before').mkdir()
changed=['holo-visual.cc','rltiles/dc-holo-main.txt']
for n in changed:
 p=run/'before'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/n,p)
shutil.copy2(root/'runtime/tiles01/HoloCrawl.exe',run/'before/HoloCrawl.exe')
preserved={str(p.relative_to(src)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in list(src.glob('*.cc'))+list(src.glob('*.h'))+list((src/'rltiles/holo').glob('*.png')) if str(p.relative_to(src)).replace('\\','/') not in changed}
(run/'preserved-files.json').write_text(json.dumps(preserved,indent=2),encoding='utf-8')
asset=root/'assets/holocrawl/towa-support03';asset.mkdir(parents=True)
shutil.copy2('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0/exec-af61e9c2-050c-4a96-a9ed-bc18a9188c2b.png',asset/'bullet.png')
im=Image.open(asset/'bullet.png').convert('RGBA');a=im.getchannel('A').point(lambda x:255 if x>128 else 0);im.putalpha(a);im=im.crop(a.getbbox()).resize((18,5),Image.Resampling.NEAREST)
names=['E','NE','N','NW','W','SW','S','SE']
for i,n in enumerate(names):
 b=im.rotate(45*i,resample=Image.Resampling.NEAREST,expand=True);tile=Image.new('RGBA',(32,32));tile.alpha_composite(b,((32-b.width)//2,(32-b.height)//2));tile.save(src/f'rltiles/holo/fx_towa_bullet_{n.lower()}.png')
p=src/'rltiles/dc-holo-main.txt';p.write_text(p.read_text()+'\n'+''.join(f'fx_towa_bullet_{n.lower()} HOLO_TOWA_BULLET_{n}\n' for n in names))
p=src/'holo-visual.cc';s=p.read_text();old='tiles.add_overlay(p,TILE_BOLT_MAGIC_DART+i%6);';new='''const int dx=(delta.x>0)-(delta.x<0),dy=(delta.y>0)-(delta.y<0);
            const int direction=dy<0?(dx>0?1:dx<0?3:2):dy>0?(dx>0?7:dx<0?5:6):(dx<0?4:0);
            tiles.add_overlay(p,TILE_HOLO_TOWA_BULLET_E+direction);''';assert old in s;s=s.replace(old,new);p.write_text(s)
p=root/'scripts/capture-towa-support03.ps1';p.write_text((root/'scripts/capture-towa-support02.ps1').read_text(encoding='utf-8').replace('towa-support02','towa-support03'),encoding='utf-8')
