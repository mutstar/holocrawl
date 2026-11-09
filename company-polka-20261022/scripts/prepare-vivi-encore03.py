from pathlib import Path
from PIL import Image
import json,shutil,hashlib
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source';a=r/'assets/holocrawl/vivi-encore03';b=r/'analysis/native/vivi-encore03'
a.mkdir(parents=True,exist_ok=True);(b/'before').mkdir(parents=True,exist_ok=True);(b/'before-art').mkdir(exist_ok=True)
for f in ['holo-visual.cc','holo-campaign-test.cc','rltiles/dc-holo-feat.txt']:shutil.copy2(r/'engine/tiles-crawl/crawl-ref/source'/f,b/'before'/Path(f).name)
src=Path('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0/exec-76d07449-87b4-4647-acf8-cce505105a04.png');shutil.copy2(src,a/'pearl-pop-source.png')
im=Image.open(src).convert('RGBA');im=im.crop(im.getchannel('A').point(lambda v:255 if v>64 else 0).getbbox());hashes={}
for f,size in enumerate([(16,16),(24,24),(22,22)]):
 p=s/f'rltiles/holo/fx_viviencore_echo{f}.png'
 if p.exists():shutil.copy2(p,b/'before-art'/p.name)
 small=im.resize(size,Image.Resampling.NEAREST)
 if f==2:small.putalpha(small.getchannel('A').point(lambda v:v*150//255))
 out=Image.new('RGBA',(32,32));out.alpha_composite(small,((32-size[0])//2,(32-size[1])//2));out.save(p);out.save(a/f'pop{f}.png');hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
p=s/'rltiles/dc-holo-feat.txt';t=p.read_text(encoding='utf-8-sig');assert 'HOLO_FX_VIVIENCORE_ECHO2' not in t;p.write_text(t+'\nfx_viviencore_echo2 HOLO_FX_VIVIENCORE_ECHO2\n',encoding='utf-8')
(a/'generation.json').write_text(json.dumps(dict(source=str(src),references=['https://hololive.hololivepro.com/talents/kikirara-vivi/','https://hololive.hololivepro.com/wp-content/uploads/2023/09/Kikirara-Vivi_pr-img_03.webp'],referenceUsed='Official character illustration only; no claim of viewing video footage.',motifs='Pink/lavender palette, white diamond glints, cosmetic gold highlights.',nativeTile=[32,32],artSizes=[[16,16],[24,24],[22,22]],fadeAlpha=150,integration='Generated edit, transparent alpha crop, nearest resize and final-frame opacity. No manual drawing.',sha256=hashes,scope='Staged VFX preview; caster combat unimplemented.'),indent=2),encoding='utf-8')
ps=(r/'scripts/capture-vivi-encore02.ps1').read_text(encoding='utf-8-sig').replace('vivi-encore02','vivi-encore03');(r/'scripts/capture-vivi-encore03.ps1').write_text(ps,encoding='utf-8')
print('Vivi official-art-inspired pearl pop prepared')
