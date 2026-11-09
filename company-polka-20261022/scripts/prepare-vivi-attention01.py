from pathlib import Path
from PIL import Image
import json,shutil
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source';b=r/'analysis/native/vivi-attention01';a=r/'assets/holocrawl/vivi-attention01'
(b/'before').mkdir(parents=True,exist_ok=True);a.mkdir(parents=True,exist_ok=True)
for f in ['holo-visual.cc','tiledgnbuf.cc','holo-campaign-test.cc','rltiles/dc-holo-feat.txt']:
 shutil.copy2(r/'engine/tiles-crawl/crawl-ref/source'/f,b/'before'/Path(f).name)
src=Path('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0/exec-8f7a299f-fcf5-4817-9787-caeefac4211d.png');shutil.copy2(src,a/'gem-source.png')
im=Image.open(src).convert('RGBA');box=im.getchannel('A').point(lambda v:255 if v>32 else 0).getbbox();gem=im.crop(box).resize((8,10),Image.Resampling.NEAREST)
entries=[]
for n in [1,2,3]:
 out=Image.new('RGBA',(32,32))
 for i in range(n):out.alpha_composite(gem,(22-9*(n-1-i),0))
 out.save(s/f'rltiles/holo/fx_viviattention{n}.png');out.save(a/f'attention{n}.png');entries.append(f'fx_viviattention{n} HOLO_FX_VIVIATTENTION{n}')
p=s/'rltiles/dc-holo-feat.txt';t=p.read_text(encoding='utf-8-sig');assert 'HOLO_FX_VIVIATTENTION1' not in t;p.write_text(t+'\n'+'\n'.join(entries)+'\n',encoding='utf-8')
(a/'generation.json').write_text(json.dumps(dict(source=str(src),nativeTile=[32,32],gemSize=[8,10],stages=[1,2,3],integration='Transparent alpha crop, nearest-neighbor resize, repetition of same generated sprite. No manual drawing.',prompt='Single glamorous magenta faceted diamond with attached white glint; tiny chunky pixel-art status sprite on transparent background.',scope='Staged visual preview only; combat not implemented.'),indent=2),encoding='utf-8')
ps=(r/'scripts/capture-su-five01.ps1').read_text(encoding='utf-8-sig').replace('su-five01','vivi-attention01').replace('HOLOCRAWL_SU_FIVE_REVIEW','HOLOCRAWL_VIVI_ATTENTION_REVIEW');(r/'scripts/capture-vivi-attention01.ps1').write_text(ps,encoding='utf-8')
print('Vivi gem sprites prepared')
