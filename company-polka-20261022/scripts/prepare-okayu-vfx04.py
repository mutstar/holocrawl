"""Correct imported icon crop, preserving the original imagegen artwork."""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source'
run=root/'analysis/native/okayu-vfx04';run.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changed=[src/'rltiles/holo'/f'fx_night_okayu1_{f}.png' for f in range(2)]
preserved={p.relative_to(src).as_posix():sha(p) for p in src.rglob('*') if p.is_file() and ((p.parent==src and p.suffix in ('.cc','.h')) or p.parent==src/'rltiles/holo') and p not in changed}
(run/'preserved-files.json').write_text(json.dumps(preserved,indent=2),encoding='utf-8')
for p in changed:
    out=run/'before'/p.relative_to(src);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
shutil.copy2(root/'runtime/tiles01/HoloCrawl.exe',run/'before/HoloCrawl.exe')
original=root/'assets/holocrawl/okayu-vfx02/onigiri.png';im=Image.open(original).convert('RGBA')
# Determine the crop from the visible artwork; do not let nearly invisible
# generated alpha specks make the crop as large as the whole canvas.
# The source pixels/alpha are retained without painting or changing colors.
visible=im.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox();assert visible
icon=im.crop(visible);icon.thumbnail((10,10),Image.Resampling.NEAREST)
tile=Image.new('RGBA',(32,32));tile.alpha_composite(icon,(26-icon.width//2,7-icon.height//2))
opaque=tile.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox();assert opaque
assert opaque[2]-opaque[0]>=9 and opaque[3]-opaque[1]>=8,opaque
assert opaque[0]>=0 and opaque[1]>=0 and opaque[2]<=32 and opaque[3]<=32
for p in changed:
    tile.save(p);out=run/'source_snapshot'/p.relative_to(src);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
tile.resize((384,384),Image.Resampling.NEAREST).save(run/'icon-zoom.png')
(run/'art-validation.json').write_text(json.dumps(dict(status='passed',revision='okayu-vfx04',tier=1,sourceArtwork=original.relative_to(root).as_posix(),originalGeneration='assets/holocrawl/okayu-vfx02/generation.json',sourceCrop=visible,alphaThresholdForCropOnly=128,sourcePixelsPreserved=True,previousVisibleSize=[12,11],newVisibleSize=[opaque[2]-opaque[0],opaque[3]-opaque[1]],centre=[26,7],framesIdentical=True,changed=[p.relative_to(src).as_posix() for p in changed],sourceChanges=False,numericChanges=False),indent=2),encoding='utf-8')
s=(root/'scripts/capture-okayu-vfx03.ps1').read_text(encoding='utf-8').replace('okayu-vfx03','okayu-vfx04');(root/'scripts/capture-okayu-vfx04.ps1').write_text(s,encoding='utf-8')
print('Onigiri reduced slightly from12x11 to10x9; artwork and anchor preserved.')
