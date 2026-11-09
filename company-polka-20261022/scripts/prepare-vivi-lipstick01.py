from pathlib import Path
from PIL import Image
import json,shutil,hashlib
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source';a=r/'assets/holocrawl/vivi-lipstick01';b=r/'analysis/native/vivi-lipstick01'
(b/'before').mkdir(parents=True,exist_ok=True);(b/'before-art').mkdir(exist_ok=True);a.mkdir(parents=True,exist_ok=True)
src=Path('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0/exec-3ac23a7e-3723-4c5b-83bf-8f30d5bb9d95.png');shutil.copy2(src,a/'lipstick-source.png')
im=Image.open(src).convert('RGBA');alpha=im.getchannel('A').point(lambda v:255 if v>=200 else 0);im.putalpha(alpha);icon=im.crop(alpha.getbbox()).resize((7,12),Image.Resampling.NEAREST)
hashes={}
for n in [1,2,3]:
 p=s/f'rltiles/holo/fx_viviattention{n}.png';shutil.copy2(p,b/'before-art'/p.name)
 out=Image.new('RGBA',(32,32))
 for i in range(n):out.alpha_composite(icon,(22-9*(n-1-i),0))
 out.save(p);out.save(a/f'attention{n}.png');hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
(a/'generation.json').write_text(json.dumps(dict(source=str(src),reference='https://hololive.hololivepro.com/talents/kikirara-vivi/',referenceImage='https://hololive.hololivepro.com/wp-content/uploads/2023/09/Kikirara-Vivi_pr-img_01_a.webp',nativeTile=[32,32],lipstickSize=[7,12],stages=[1,2,3],integration='Alpha threshold200 to omit soft generated glow, transparent bounding crop, nearest-neighbor resize and repetition. No manual painting.',prompt='Single tiny upright lipstick inspired by Vivi belt cosmetics: pink slanted tip, gold sleeve, charcoal base, chunky transparent pixel art.',sha256=hashes,scope='Staged visual preview only; combat unchanged.'),indent=2),encoding='utf-8')
ps=(r/'scripts/capture-vivi-attention02.ps1').read_text(encoding='utf-8-sig').replace('vivi-attention02','vivi-lipstick01');(r/'scripts/capture-vivi-lipstick01.ps1').write_text(ps,encoding='utf-8')
print('Lipstick sprites prepared')
