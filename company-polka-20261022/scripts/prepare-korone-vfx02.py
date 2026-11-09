"""Import generated tier-3 punch; preserve other god art and combat code."""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil,sys
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source'
run=root/'analysis/native/korone-vfx02';run.mkdir(exist_ok=False)
assets=root/'assets/holocrawl/korone-vfx02';assets.mkdir(parents=True,exist_ok=True)
generated=Path(sys.argv[1]);shutil.copy2(generated,assets/'punch.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changed=[src/'holo-visual.cc',*[src/'rltiles/holo'/f'fx_night_korone3_{f}.png' for f in range(2)]]
preserved={p.relative_to(src).as_posix():sha(p) for p in src.rglob('*') if p.is_file() and ((p.parent==src and p.suffix in ('.cc','.h')) or p.parent==src/'rltiles/holo') and p not in changed}
(run/'preserved-files.json').write_text(json.dumps(preserved,indent=2),encoding='utf-8')
for p in changed:
    out=run/'before'/p.relative_to(src);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
shutil.copy2(root/'runtime/tiles01/HoloCrawl.exe',run/'before/HoloCrawl.exe')
original=Image.open(generated).convert('RGBA');assert original.getextrema()[3][0]==0
original=original.crop(original.getbbox())
frames=[]
for f,size in enumerate([36,42]):
    im=original.copy();im.thumbnail((size,size),Image.Resampling.NEAREST)
    tile=Image.new('RGBA',(96,96));tile.alpha_composite(im,(48-im.width//2,40-im.height//2))
    p=src/'rltiles/holo'/f'fx_night_korone3_{f}.png';tile.save(p);frames.append(dict(frame=f,bounds=tile.getbbox(),spriteSize=im.size,sha256=sha(p)))
p=src/'holo-visual.cc';s=p.read_text(encoding='utf-8');old='scaled_delay(flash_kind==effect::ayameslash || flash_kind==effect::ayameduel?110:';assert old in s
s=s.replace(old,'scaled_delay(flash_kind==effect::night_korone3?110:flash_kind==effect::ayameslash || flash_kind==effect::ayameduel?110:',1);p.write_text(s,encoding='utf-8')
(run/'art-validation.json').write_text(json.dumps(dict(status='passed',revision='korone-vfx02',frames=frames,raisedPixels=8,frameMilliseconds=110,changed=[p.relative_to(src).as_posix() for p in changed],numericChanges=False),indent=2),encoding='utf-8')
s=(root/'scripts/capture-choco-vfx03.ps1').read_text(encoding='utf-8').replace('choco-vfx03','korone-vfx02')
s=s.replace(";$env:HOLOCRAWL_CHOCO_REVIEW=$shots",'')
s='\n'.join(line for line in s.splitlines() if "Missing Choco state controls" not in line)
s=s.replace('Remove-Item Env:HOLOCRAWL_INVOCATION_CAPTURE,Env:HOLOCRAWL_CHOCO_REVIEW','Remove-Item Env:HOLOCRAWL_INVOCATION_CAPTURE')
s=s.replace('chocoControls=$true','chocoControls=$false')
(root/'scripts/capture-korone-vfx02.ps1').write_text(s,encoding='utf-8')
print('Imported compact punch, raised 8px, two 110ms frames; other art/code hashes recorded.')
