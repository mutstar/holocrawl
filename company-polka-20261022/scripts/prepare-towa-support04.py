from pathlib import Path
from PIL import Image
import json,shutil,hashlib
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source';run=root/'analysis/native/towa-support04'
run.mkdir();(run/'before').mkdir()
changed=[f'rltiles/holo/fx_towa_bullet_{n}.png' for n in ['e','ne','n','nw','w','sw','s','se']]
for n in changed+['holo-visual.cc','rltiles/dc-holo-main.txt']:
 p=run/'before'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/n,p)
shutil.copy2(root/'runtime/tiles01/HoloCrawl.exe',run/'before/HoloCrawl.exe')
preserved={str(p.relative_to(src)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in list(src.glob('*.cc'))+list(src.glob('*.h'))+list((src/'rltiles/holo').glob('*.png')) if str(p.relative_to(src)).replace('\\','/') not in changed}
(run/'preserved-files.json').write_text(json.dumps(preserved,indent=2),encoding='utf-8')
asset=root/'assets/holocrawl/towa-support04';asset.mkdir(parents=True)
shutil.copy2('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0/exec-874d51f5-80e3-4493-9a28-fb2674c65563.png',asset/'devil-arrow.png')
im=Image.open(asset/'devil-arrow.png').convert('RGBA');a=im.getchannel('A').point(lambda x:255 if x>128 else 0);im.putalpha(a);im=im.crop(a.getbbox()).resize((20,8),Image.Resampling.NEAREST)
for i,n in enumerate(['e','ne','n','nw','w','sw','s','se']):
 b=im.rotate(45*i,resample=Image.Resampling.NEAREST,expand=True);tile=Image.new('RGBA',(32,32));tile.alpha_composite(b,((32-b.width)//2,(32-b.height)//2));tile.save(src/f'rltiles/holo/fx_towa_bullet_{n}.png')
p=root/'scripts/capture-towa-support04.ps1';p.write_text((root/'scripts/capture-towa-support03.ps1').read_text(encoding='utf-8').replace('towa-support03','towa-support04'),encoding='utf-8')
p=root/'scripts/publish-towa-support04.py';s=(root/'scripts/publish-towa-support03.py').read_text(encoding='utf-8').replace('towa-support03','towa-support04').replace('은빛 탄두·짧은 자주색 궤적','짧은 보라색 악마 화살').replace('은빛탄두+짧은자주색궤적','짧은보라색악마화살').replace('Generated silver/brass bullet with short magenta tracer','Generated short purple devil arrow with hooked spearhead');p.write_text(s,encoding='utf-8')
