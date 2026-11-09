from pathlib import Path
from PIL import Image
import json,shutil,hashlib
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source';a=r/'assets/holocrawl/su-wave03';b=r/'analysis/native/su-wave03'
a.mkdir(parents=True,exist_ok=True);(b/'before').mkdir(parents=True,exist_ok=True);(b/'before-art').mkdir(exist_ok=True)
src=r/'assets/holocrawl/su-wave02/wave-source.png';shutil.copy2(src,a/'wave-source.png')
im=Image.open(src).convert('RGBA');box=im.getchannel('A').point(lambda v:255 if v>32 else 0).getbbox();im=im.crop(box).resize((24,28),Image.Resampling.NEAREST)
base=Image.new('RGBA',(64,64));base.alpha_composite(im,(20,18));hashes={}
for i,name in enumerate(['e','se','s','sw','w','nw','n','ne']):
 p=s/f'rltiles/holo/fx_suwave_{name}.png';shutil.copy2(p,b/'before-art'/p.name)
 rotated=base.rotate(-45*i,resample=Image.Resampling.NEAREST,expand=False);tile=rotated.crop(rotated.getchannel('A').getbbox())
 tile.thumbnail((30,30),Image.Resampling.NEAREST)
 out=Image.new('RGBA',(32,32));out.alpha_composite(tile,((32-tile.width)//2,(32-tile.height)//2));out.save(p);out.save(a/f'wave-{name}.png')
 hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
(a/'generation.json').write_text(json.dumps(dict(revision='su-wave03',source=str(src.relative_to(r)),operation='Nearest-neighbor resize of existing generated sprite; no new painting.',previousArtSize=[20,24],newArtSize=[24,28],nativeTile=[32,32],diagonalFitMax=[30,30],sha256=hashes),indent=2),encoding='utf-8')
ps=(r/'scripts/capture-su-wave02.ps1').read_text(encoding='utf-8-sig').replace('su-wave02','su-wave03');(r/'scripts/capture-su-wave03.ps1').write_text(ps,encoding='utf-8')
print('Su wave enlarged from20x24 to24x28; all8directions preserved within32px')
