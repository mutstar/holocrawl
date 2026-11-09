from pathlib import Path
from PIL import Image
import json,shutil
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source';b=r/'analysis/native/su-wave02';a=r/'assets/holocrawl/su-wave02'
(b/'before').mkdir(parents=True,exist_ok=True);a.mkdir(parents=True,exist_ok=True)
for f in ['holo-visual.cc','tilereg-dgn.cc','holo-campaign-test.cc','rltiles/dc-holo-feat.txt']:
 old=r/'engine/tiles-crawl/crawl-ref/source'/f
 shutil.copy2(old,b/'before'/Path(f).name)
src=Path('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0/exec-c5d742ba-601c-41a6-a393-3f9bd14d6742.png')
shutil.copy2(src,a/'wave-source.png')
im=Image.open(src).convert('RGBA');box=im.getchannel('A').point(lambda v:255 if v>32 else 0).getbbox();im=im.crop(box).resize((20,24),Image.Resampling.NEAREST)
base=Image.new('RGBA',(32,32));base.alpha_composite(im,(6,4))
names=['e','se','s','sw','w','nw','n','ne'];entries=[]
for i,name in enumerate(names):
 out=base.rotate(-45*i,resample=Image.Resampling.NEAREST,expand=False)
 out.save(s/f'rltiles/holo/fx_suwave_{name}.png');out.save(a/f'wave-{name}.png')
 entries.append(f'fx_suwave_{name} HOLO_FX_SUWAVE_{name.upper()}')
p=s/'rltiles/dc-holo-feat.txt';t=p.read_text(encoding='utf-8-sig');assert 'HOLO_FX_SUWAVE_E' not in t;p.write_text(t+'\n'+'\n'.join(entries)+'\n',encoding='utf-8')
(a/'generation.json').write_text(json.dumps(dict(source=str(src),transparent=True,nativeTile=[32,32],artSize=[20,24],integration='Crop transparent bounds, nearest-neighbor resize, eight 45-degree nearest-neighbor rotations; no painted pixels.',prompt='Compact east-moving breaking turquoise wave front, 3 bright foam curls, short dark blue wake; chunky low-resolution pixel art, transparent background, no circle or whirlpool.'),indent=2),encoding='utf-8')
ps=(r/'scripts/capture-su-wave01.ps1').read_text(encoding='utf-8-sig').replace('su-wave01','su-wave02');(r/'scripts/capture-su-wave02.ps1').write_text(ps,encoding='utf-8')
print('Eight native travelling wave tiles prepared')
