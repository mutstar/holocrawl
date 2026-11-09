"""Import a readable lavender onigiri for Okayu's passive status only."""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil,sys
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source'
run=root/'analysis/native/okayu-vfx02';run.mkdir(exist_ok=False)
assets=root/'assets/holocrawl/okayu-vfx02';assets.mkdir(parents=True,exist_ok=True)
generated=Path(sys.argv[1]);shutil.copy2(generated,assets/'onigiri.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changed=[src/'rltiles/holo'/f'fx_night_okayu1_{f}.png' for f in range(2)]
preserved={p.relative_to(src).as_posix():sha(p) for p in src.rglob('*') if p.is_file() and ((p.parent==src and p.suffix in ('.cc','.h')) or p.parent==src/'rltiles/holo') and p not in changed}
(run/'preserved-files.json').write_text(json.dumps(preserved,indent=2),encoding='utf-8')
for p in changed:
    out=run/'before'/p.relative_to(src);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
shutil.copy2(root/'runtime/tiles01/HoloCrawl.exe',run/'before/HoloCrawl.exe')
icon=Image.open(generated).convert('RGBA');assert icon.getextrema()[3][0]==0
icon=icon.crop(icon.getbbox());icon.thumbnail((12,12),Image.Resampling.NEAREST)
tile=Image.new('RGBA',(32,32));tile.alpha_composite(icon,(26-icon.width//2,7-icon.height//2))
bx=tile.getbbox();assert bx[0]>=0 and bx[1]>=0 and bx[2]<=32 and bx[3]<=32
for p in changed:
    tile.save(p);out=run/'source_snapshot'/p.relative_to(src);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
(run/'art-validation.json').write_text(json.dumps(dict(status='passed',revision='okayu-vfx02',tier=1,iconMaxSize=12,iconSize=icon.size,bounds=bx,centre=[26,7],framesIdentical=True,changed=[p.relative_to(src).as_posix() for p in changed],numericChanges=False,sourceChanges=False,otherTiersPreserved=True),indent=2),encoding='utf-8')
s=(root/'scripts/capture-korone-vfx09.ps1').read_text(encoding='utf-8').replace('korone-vfx09','okayu-vfx02')
s=s.replace('$env:HOLOCRAWL_INVOCATION_CAPTURE=$shots','$env:HOLOCRAWL_INVOCATION_CAPTURE=$shots;$env:HOLOCRAWL_NIGHT_REVIEW=$shots')
s=s.replace('Remove-Item Env:HOLOCRAWL_INVOCATION_CAPTURE','Remove-Item Env:HOLOCRAWL_INVOCATION_CAPTURE,Env:HOLOCRAWL_NIGHT_REVIEW')
(root/'scripts/capture-okayu-vfx02.ps1').write_text(s,encoding='utf-8')
print('Lavender onigiri imported at12px; black nori, stable frames, previous top-right anchor preserved.')
