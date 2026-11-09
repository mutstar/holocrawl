from pathlib import Path
from PIL import Image
import json,shutil,hashlib
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source';a=r/'assets/holocrawl/vivi-encore04';b=r/'analysis/native/vivi-encore04'
a.mkdir(parents=True,exist_ok=True);(b/'before').mkdir(parents=True,exist_ok=True);(b/'before-art').mkdir(exist_ok=True)
src=r/'assets/holocrawl/vivi-encore03/pearl-pop-source.png';shutil.copy2(src,a/'pearl-pop-source.png')
im=Image.open(src).convert('RGBA');im=im.crop(im.getchannel('A').point(lambda v:255 if v>64 else 0).getbbox());hashes={}
for f,size in enumerate([(18,18),(28,28),(26,26)]):
 p=s/f'rltiles/holo/fx_viviencore_echo{f}.png';shutil.copy2(p,b/'before-art'/p.name)
 small=im.resize(size,Image.Resampling.NEAREST)
 if f==2:small.putalpha(small.getchannel('A').point(lambda v:v*150//255))
 out=Image.new('RGBA',(32,32));out.alpha_composite(small,((32-size[0])//2,(32-size[1])//2));out.save(p);out.save(a/f'pop{f}.png');hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
metadata=json.loads((r/'assets/holocrawl/vivi-encore03/generation.json').read_text(encoding='utf-8'));metadata.update(source=str(src.relative_to(r)),revision='vivi-encore04',previousArtSizes=[[16,16],[24,24],[22,22]],artSizes=[[18,18],[28,28],[26,26]],integration='Nearest-neighbor size adjustment of existing generated pearl burst; same palette and opacity.',sha256=hashes)
(a/'generation.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
ps=(r/'scripts/capture-vivi-encore03.ps1').read_text(encoding='utf-8-sig').replace('vivi-encore03','vivi-encore04');(r/'scripts/capture-vivi-encore04.ps1').write_text(ps,encoding='utf-8')
print('Vivi pearl pop peak24px ->28px')
