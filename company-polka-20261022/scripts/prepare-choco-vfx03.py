"""Reuse the approved imagegen solid heart for the return animation."""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil
root=Path(__file__).resolve().parents[1]
src=root/'engine/campaign-crawl/crawl-ref/source'
run=root/'analysis/native/choco-vfx03';run.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changed=[*sorted((src/'rltiles/holo').glob('fx_chocoabsorb*.png')),src/'holo-visual.cc']
preserved={p.relative_to(src).as_posix():sha(p) for p in src.rglob('*') if p.is_file() and ((p.parent==src and p.suffix in ('.cc','.h')) or p.parent==src/'rltiles/holo') and p not in changed}
(run/'preserved-files.json').write_text(json.dumps(preserved,indent=2),encoding='utf-8')
for p in changed:
    out=run/'before'/p.relative_to(src);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
shutil.copy2(root/'runtime/tiles01/HoloCrawl.exe',run/'before/HoloCrawl.exe')
original=root/'assets/holocrawl/choco-vfx02/originals/heart-solid.png'
heart=Image.open(original).convert('RGBA');heart=heart.crop(heart.getbbox());heart.thumbnail((14,14),Image.Resampling.NEAREST)
assert heart.getpixel((heart.width//2,heart.height//2))[3]>=240
for d,(dx,dy) in enumerate([(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]):
    for f in range(2):
        tile=Image.new('RGBA',(96,96));cx=48+dx*(16+16*f);cy=48+dy*(16+16*f)-5
        tile.alpha_composite(heart,(cx-heart.width//2,cy-heart.height//2))
        tile.save(src/'rltiles/holo'/f'fx_chocoabsorb{d}_{f}.png')
p=src/'holo-visual.cc';s=p.read_text(encoding='utf-8');a=s.index('void choco_kiss(');b=s.index('\nvoid ',a+10)
part=s[a:b];assert 'else scaled_delay(110);' in part
part=part.replace('else scaled_delay(110);','else scaled_delay(f>=2?170:110);')
p.write_text(s[:a]+part+s[b:],encoding='utf-8')
(run/'art-validation.json').write_text(json.dumps(dict(status='passed',assetReuse=original.relative_to(root).as_posix(),originalGeneration='assets/holocrawl/choco-vfx02/generation.json',oldSize=10,newMaxSize=14,raisedPixels=5,returnFrameMilliseconds=170,solidCentre=True,changed=[p.relative_to(src).as_posix() for p in changed],numericChanges=False),indent=2),encoding='utf-8')
capture=(root/'scripts/capture-choco-vfx02.ps1').read_text(encoding='utf-8').replace('choco-vfx02','choco-vfx03')
(root/'scripts/capture-choco-vfx03.ps1').write_text(capture,encoding='utf-8')
print('Imported approved solid heart: 10 -> 14 pixels, 5 pixels higher, return frame 110 -> 170 ms.')
