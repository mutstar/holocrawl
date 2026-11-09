from pathlib import Path
from PIL import Image
import json,shutil,hashlib
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source';a=r/'assets/holocrawl/vivi-curtain01';b=r/'analysis/native/vivi-curtain01'
a.mkdir(parents=True,exist_ok=True);(b/'before').mkdir(parents=True,exist_ok=True)
for f in ['holo-visual.cc','holo-campaign-test.cc','rltiles/dc-holo-feat.txt']:shutil.copy2(r/'engine/tiles-crawl/crawl-ref/source'/f,b/'before'/Path(f).name)
sources=[Path('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0/exec-6b408f23-a85c-4777-9107-c4220bd27782.png'),Path('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0/exec-3b419cc6-5d38-48ce-bcbe-46daeb2b79ed.png')]
canvases=[]
for path,name in zip(sources,['open','closed']):
 shutil.copy2(path,a/f'{name}-source.png');im=Image.open(path).convert('RGBA');im=im.crop(im.getchannel('A').point(lambda v:255 if v>64 else 0).getbbox()).resize((84,72),Image.Resampling.NEAREST)
 canvas=Image.new('RGBA',(96,96));canvas.alpha_composite(im,(6,12));canvases.append(canvas)
frames=[canvases[0]]
for height in [40,64]:
 frame=canvases[0].copy();frame.alpha_composite(canvases[1].crop((0,0,96,height)),(0,0));frames.append(frame)
frames.append(canvases[1]);entries=[];hashes={}
for frame,name in zip(frames,['open','drop1','drop2','closed']):
 p=s/f'rltiles/holo/fx_vivicurtrain_{name}.png';frame.save(p);frame.save(a/f'{name}.png');entries.append(f'fx_vivicurtrain_{name} HOLO_FX_VIVICURTAIN_{name.upper()}');hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
p=s/'rltiles/dc-holo-feat.txt';t=p.read_text(encoding='utf-8-sig');assert 'HOLO_FX_VIVICURTAIN_OPEN' not in t;p.write_text(t+'\n'+'\n'.join(entries)+'\n',encoding='utf-8')
(a/'generation.json').write_text(json.dumps(dict(sources=[str(p) for p in sources],canvas=[96,96],nativeArt=[84,72],span=[3,3],stages=['open','drop40','drop64','closed','gold-flash','fade'],integration='Generated open and closed curtains; transparent crop/nearest resize. Two falling frames composite the top of closed curtain over open curtain. No painted pixels.',sha256=hashes,scope='Test-only staged VFX, no terrain or combat changes.'),indent=2),encoding='utf-8')
ps=(r/'scripts/capture-vivi-finale01.ps1').read_text(encoding='utf-8-sig').replace('vivi-finale01','vivi-curtain01');(r/'scripts/capture-vivi-curtain01.ps1').write_text(ps,encoding='utf-8')
print('Vivi native3x3 curtain frames prepared')
