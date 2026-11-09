from pathlib import Path
from PIL import Image
import json,shutil,hashlib
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source';b=r/'analysis/native/vivi-finale01';a=r/'assets/holocrawl/vivi-finale01'
(b/'before').mkdir(parents=True,exist_ok=True);a.mkdir(parents=True,exist_ok=True)
for f in ['holo-visual.cc','tiledgnbuf.cc','tilereg-dgn.cc','holo-campaign-test.cc','rltiles/dc-holo-feat.txt']:shutil.copy2(r/'engine/tiles-crawl/crawl-ref/source'/f,b/'before'/Path(f).name)
src=Path('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0/exec-81ed0ccd-211f-4314-b60e-e540d163ffb9.png');shutil.copy2(src,a/'finale-source.png')
def crop(path):
 im=Image.open(path).convert('RGBA');return im.crop(im.getchannel('A').point(lambda v:255 if v>64 else 0).getbbox())
im=crop(src);edge=crop(r/'assets/holocrawl/vivi-encore03/pearl-pop-source.png');entries=[];hashes={}
def save(name,picture,size,alpha=255,position=None):
 small=picture.resize(size,Image.Resampling.NEAREST)
 if alpha<255:small.putalpha(small.getchannel('A').point(lambda v:v*alpha//255))
 tile=Image.new('RGBA',(32,32));tile.alpha_composite(small,position or ((32-size[0])//2,(32-size[1])//2));p=s/f'rltiles/holo/fx_vivifinale_{name}.png';tile.save(p);tile.save(a/f'{name}.png');entries.append(f'fx_vivifinale_{name} HOLO_FX_VIVIFINALE_{name.upper()}');hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
save('mark',im,(12,12),position=(10,0))
for f,size in enumerate([(18,18),(28,28),(26,26)]):save('burst'+str(f),im,size,150 if f==2 else 255)
for f,size in enumerate([(10,10),(16,16),(14,14)]):save('edge'+str(f),edge,size,130 if f==2 else 255)
p=s/'rltiles/dc-holo-feat.txt';t=p.read_text(encoding='utf-8-sig');assert 'HOLO_FX_VIVIFINALE_MARK' not in t;p.write_text(t+'\n'+'\n'.join(entries)+'\n',encoding='utf-8')
(a/'generation.json').write_text(json.dumps(dict(source=str(src),references=['https://hololive.hololivepro.com/talents/kikirara-vivi/'],nativeTile=[32,32],centreSizes=[[18,18],[28,28],[26,26]],edgeSizes=[[10,10],[16,16],[14,14]],markSize=[12,12],integration='Generated gold-centred cosmetic finale, transparent crop/nearest resize/opacity. Surrounding pearl puff reuses approved generated Encore art.',sha256=hashes,scope='Staged native VFX only; new caster combat unimplemented.'),indent=2),encoding='utf-8')
ps=(r/'scripts/capture-vivi-encore04.ps1').read_text(encoding='utf-8-sig').replace('vivi-encore04','vivi-finale01').replace('HOLOCRAWL_VIVI_ENCORE_REVIEW','HOLOCRAWL_VIVI_FINALE_REVIEW');(r/'scripts/capture-vivi-finale01.ps1').write_text(ps,encoding='utf-8')
print('Vivi finale mark, central burst and neighbouring pearl tiles prepared')
