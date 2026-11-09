from pathlib import Path
from PIL import Image
import json,shutil
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source';b=r/'analysis/native/vivi-encore01';a=r/'assets/holocrawl/vivi-encore01'
(b/'before').mkdir(parents=True,exist_ok=True);a.mkdir(parents=True,exist_ok=True)
for f in ['holo-visual.cc','tiledgnbuf.cc','tilereg-dgn.cc','holo-campaign-test.cc','rltiles/dc-holo-feat.txt']:
 shutil.copy2(r/'engine/tiles-crawl/crawl-ref/source'/f,b/'before'/Path(f).name)
src=Path('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0/exec-afce4546-36fa-410f-a5fe-4189d14dd52b.png');shutil.copy2(src,a/'echo-source.png')
im=Image.open(src).convert('RGBA');im=im.crop(im.getchannel('A').point(lambda v:255 if v>64 else 0).getbbox())
entries=[]
for f,size in enumerate([(16,18),(20,22)]):
 tile=Image.new('RGBA',(32,32));small=im.resize(size,Image.Resampling.NEAREST);tile.alpha_composite(small,((32-size[0])//2,(32-size[1])//2));tile.save(s/f'rltiles/holo/fx_viviencore_echo{f}.png');tile.save(a/f'echo{f}.png');entries.append(f'fx_viviencore_echo{f} HOLO_FX_VIVIENCORE_ECHO{f}')
lip=Image.open(r/'assets/holocrawl/vivi-lipstick01/lipstick-source.png').convert('RGBA');alpha=lip.getchannel('A').point(lambda v:255 if v>=200 else 0);lip.putalpha(alpha);lip=lip.crop(alpha.getbbox()).resize((7,12),Image.Resampling.NEAREST).rotate(-35,resample=Image.Resampling.NEAREST,expand=True)
tile=Image.new('RGBA',(32,32));tile.alpha_composite(lip,(18,0));tile.save(s/'rltiles/holo/fx_viviencore_ready.png');tile.save(a/'ready.png')
# Keep two echo frames consecutive in the atlas.
entries=['fx_viviencore_ready HOLO_FX_VIVIENCORE_READY']+entries
p=s/'rltiles/dc-holo-feat.txt';t=p.read_text(encoding='utf-8-sig');assert 'HOLO_FX_VIVIENCORE_READY' not in t;p.write_text(t+'\n'+'\n'.join(entries)+'\n',encoding='utf-8')
(a/'generation.json').write_text(json.dumps(dict(echoSource=str(src),nativeTile=[32,32],echoArtSizes=[[16,18],[20,22]],ready='Existing generated lipstick rotated35degrees clockwise',scope='Test-only staged VFX; no caster gameplay implemented.',prompt='Compact magenta magical echo impact: two overlapping angular crescent slivers and central white-pink flash; coarse transparent pixel art.'),indent=2),encoding='utf-8')
ps=(r/'scripts/capture-vivi-lipstick01.ps1').read_text(encoding='utf-8-sig').replace('vivi-lipstick01','vivi-encore01').replace('HOLOCRAWL_VIVI_ATTENTION_REVIEW','HOLOCRAWL_VIVI_ENCORE_REVIEW');(r/'scripts/capture-vivi-encore01.ps1').write_text(ps,encoding='utf-8')
print('Vivi encore ready and echo tiles prepared')
