from pathlib import Path
from PIL import Image
import json,shutil,hashlib
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source';a=r/'assets/holocrawl/vivi-encore02';b=r/'analysis/native/vivi-encore02'
a.mkdir(parents=True,exist_ok=True);(b/'before').mkdir(parents=True,exist_ok=True);(b/'before-art').mkdir(exist_ok=True)
src=Path('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0/exec-9dd36725-ac40-4489-9ece-6db1a8363341.png');shutil.copy2(src,a/'pop-source.png')
im=Image.open(src).convert('RGBA');im=im.crop(im.getchannel('A').point(lambda v:255 if v>64 else 0).getbbox());hashes={}
for f,size in enumerate([(14,14),(22,22)]):
 p=s/f'rltiles/holo/fx_viviencore_echo{f}.png';shutil.copy2(p,b/'before-art'/p.name)
 out=Image.new('RGBA',(32,32));out.alpha_composite(im.resize(size,Image.Resampling.NEAREST),((32-size[0])//2,(32-size[1])//2));out.save(p);out.save(a/f'pop{f}.png');hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
(a/'generation.json').write_text(json.dumps(dict(source=str(src),nativeTile=[32,32],artSizes=[[14,14],[22,22]],integration='Alpha-bound crop and nearest-neighbor resize of generated pink pop. No manual drawing.',prompt='Instant compact magenta pop puff on enemy torso, white-pink center and rounded block lobes. No crescents, slashes, tail or projectile.',sha256=hashes,scope='Staged native VFX preview only; combat unchanged.'),indent=2),encoding='utf-8')
ps=(r/'scripts/capture-vivi-encore01.ps1').read_text(encoding='utf-8-sig').replace('vivi-encore01','vivi-encore02');(r/'scripts/capture-vivi-encore02.ps1').write_text(ps,encoding='utf-8')
print('Vivi Encore slash replaced by compact pop')
