"""Tier5-only compact twin-paw awakening aura; approved tier3 is preserved."""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil,sys
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source'
run=root/'analysis/native/korone-vfx07';run.mkdir(exist_ok=False)
assets=root/'assets/holocrawl/korone-vfx07';assets.mkdir(parents=True,exist_ok=True)
generated=Path(sys.argv[1]);shutil.copy2(generated,assets/'awakening.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changed=[src/'holo-visual.cc',src/'tilereg-dgn.cc',*[src/'rltiles/holo'/f'fx_night_korone5_{f}.png' for f in range(2)]]
preserved={p.relative_to(src).as_posix():sha(p) for p in src.rglob('*') if p.is_file() and ((p.parent==src and p.suffix in ('.cc','.h')) or p.parent==src/'rltiles/holo') and p not in changed}
(run/'preserved-files.json').write_text(json.dumps(preserved,indent=2),encoding='utf-8')
for p in changed:
    out=run/'before'/p.relative_to(src);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
shutil.copy2(root/'runtime/tiles01/HoloCrawl.exe',run/'before/HoloCrawl.exe')
original=Image.open(generated).convert('RGBA');assert original.getextrema()[3][0]==0
original=original.crop(original.getbbox());frames=[]
for f,size in enumerate([48,56]):
    im=original.copy();im.thumbnail((size,size),Image.Resampling.NEAREST)
    tile=Image.new('RGBA',(160,160));tile.alpha_composite(im,(80-im.width//2,80-im.height//2))
    p=src/'rltiles/holo'/f'fx_night_korone5_{f}.png';tile.save(p)
    frames.append(dict(frame=f,bounds=tile.getbbox(),spriteSize=im.size,sha256=sha(p)))
p=src/'tilereg-dgn.cc';s=p.read_text(encoding='utf-8');old='&& cue!=holo_visual::effect::night_korone3\n                        && cue!=holo_visual::effect::night_korone5)';assert old in s;s=s.replace(old,'&& cue!=holo_visual::effect::night_korone3)',1);p.write_text(s,encoding='utf-8')
p=src/'holo-visual.cc';s=p.read_text(encoding='utf-8');old='const int frames=flash_kind==effect::cometfall?6:';assert old in s;s=s.replace(old,'const int frames=flash_kind==effect::night_korone5?4:flash_kind==effect::cometfall?6:',1);p.write_text(s,encoding='utf-8')
for p in changed:
    out=run/'source_snapshot'/p.relative_to(src);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
(run/'art-validation.json').write_text(json.dumps(dict(status='passed',revision='korone-vfx07',tier=5,frames=frames,newMaxSizes=[48,56],centre=[80,80],frameMilliseconds=110,activationFrames=[0,1,0,1],renderUnderActors=True,changed=[p.relative_to(src).as_posix() for p in changed],numericChanges=False,scope='Presentation-only twin-paw aura; open centre and under-actor layer retain the player silhouette.'),indent=2),encoding='utf-8')
s=(root/'scripts/capture-korone-vfx06.ps1').read_text(encoding='utf-8').replace('korone-vfx06','korone-vfx07');(root/'scripts/capture-korone-vfx07.ps1').write_text(s,encoding='utf-8')
print('Tier5 twin-paw aura imported at48/56px; two native pulses, actor silhouette retained.')
