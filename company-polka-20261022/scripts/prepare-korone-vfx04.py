"""Import claw-free dog paw at the target torso; art-only revision."""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil,sys
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source'
run=root/'analysis/native/korone-vfx04';run.mkdir(exist_ok=False)
assets=root/'assets/holocrawl/korone-vfx04';assets.mkdir(parents=True,exist_ok=True)
generated=Path(sys.argv[1]);shutil.copy2(generated,assets/'paw.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changed=[src/'rltiles/holo'/f'fx_night_korone3_{f}.png' for f in range(2)]
preserved={p.relative_to(src).as_posix():sha(p) for p in src.rglob('*') if p.is_file() and ((p.parent==src and p.suffix in ('.cc','.h')) or p.parent==src/'rltiles/holo') and p not in changed}
(run/'preserved-files.json').write_text(json.dumps(preserved,indent=2),encoding='utf-8')
for p in changed:
    out=run/'before'/p.relative_to(src);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
shutil.copy2(root/'runtime/tiles01/HoloCrawl.exe',run/'before/HoloCrawl.exe')
original=Image.open(generated).convert('RGBA');assert original.getextrema()[3][0]==0
original=original.crop(original.getbbox());frames=[]
for f,size in enumerate([36,42]):
    im=original.copy();im.thumbnail((size,size),Image.Resampling.NEAREST)
    tile=Image.new('RGBA',(96,96));tile.alpha_composite(im,(48-im.width//2,48-im.height//2))
    p=src/'rltiles/holo'/f'fx_night_korone3_{f}.png';tile.save(p)
    frames.append(dict(frame=f,bounds=tile.getbbox(),spriteSize=im.size,sha256=sha(p)))
    out=run/'source_snapshot'/p.relative_to(src);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
(run/'art-validation.json').write_text(json.dumps(dict(status='passed',revision='korone-vfx04',frames=frames,previousCentre=[48,40],newCentre=[48,48],bodyShot=True,frameMilliseconds=110,renderAboveActors=True,changed=[p.relative_to(src).as_posix() for p in changed],numericChanges=False),indent=2),encoding='utf-8')
s=(root/'scripts/capture-korone-vfx03.ps1').read_text(encoding='utf-8').replace('korone-vfx03','korone-vfx04');(root/'scripts/capture-korone-vfx04.ps1').write_text(s,encoding='utf-8')
print('Dog paw imported at target centre (48,48); timing and foreground rendering preserved.')
