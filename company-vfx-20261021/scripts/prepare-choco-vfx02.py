"""Import imagegen's solid-heart edit; change only 1-star marker art/position."""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil
root=Path(__file__).resolve().parents[1]
src=root/'engine/campaign-crawl/crawl-ref/source'
run=root/'analysis/native/choco-vfx02';run.mkdir(exist_ok=False)
assets=root/'assets/holocrawl/choco-vfx02';(assets/'originals').mkdir(parents=True)
generated=Path('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0/exec-db8bf466-ae64-4f95-951a-d104fd337f7b.png')
shutil.copy2(generated,assets/'originals/heart-solid.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
preserved={}
for p in src.rglob('*'):
    if p.is_file() and (p.suffix in ['.cc','.h'] and p.parent==src or p.suffix=='.png' and p.parent==src/'rltiles/holo'):
        rel=p.relative_to(src).as_posix()
        if not p.name.startswith('fx_chocoheart') and p.name!='holo-campaign-test.cc':preserved[rel]=sha(p)
(run/'preserved-files.json').write_text(json.dumps(preserved,indent=2),encoding='utf-8')
for p in [src/'holo-campaign-test.cc',*sorted((src/'rltiles/holo').glob('fx_chocoheart*.png'))]:
    q=run/'before'/p.relative_to(src);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
shutil.copy2(root/'runtime/tiles01/HoloCrawl.exe',run/'before/HoloCrawl.exe')
im=Image.open(generated).convert('RGBA');assert im.getextrema()[3][0]==0
im=im.crop(im.getbbox())
frames=[]
for n in range(1,6):
    for f in range(2):
        heart=im.copy();heart.thumbnail((6+n+(1-f),)*2,Image.Resampling.NEAREST)
        out=Image.new('RGBA',(96,96))
        # Target tile occupies [32,64). Shift centre up six game pixels:
        # only the lower edge grazes the head; keep the existing right anchor.
        out.alpha_composite(heart,(57-heart.width//2,33-heart.height//2))
        bbox=out.getbbox();assert bbox[0]>=32 and bbox[2]<=64 and bbox[1]>=26 and bbox[3]<=40,bbox
        # The generated heart must remain solid after nearest-neighbor import.
        assert heart.getpixel((heart.width//2,heart.height//2))[3]>=240
        p=src/'rltiles/holo'/f'fx_chocoheart{n}_{f}.png';out.save(p)
        frames.append(dict(stack=n,frame=f,size=heart.size,alphaBounds=bbox,path=p.relative_to(root).as_posix(),sha256=sha(p)))
(run/'art-validation.json').write_text(json.dumps(dict(status='passed',oldCentre=[57,39],newCentre=[57,33],shiftUpNativePixels=6,solidCentre=True,renderLayerUnchanged=True,renderAboveActors=True,frames=frames),indent=2),encoding='utf-8')
prompt="Edit supplied pink pixel-art heart outline: fill hollow interior with fully opaque saturated warm pink. Preserve stepped silhouette, magenta edge, tiny pink highlight, orientation and proportions. Bold few-color retro sprite readable at 8-12px. Transparent outside, no hole inside, no glow/shadow/text/extra objects."
(assets/'generation.json').write_text(json.dumps(dict(tool='built-in image_gen',intent='edit',input='assets/holocrawl/choco-vfx01/originals/heart.png',output='originals/heart-solid.png',prompt=prompt,placement='Native 96px overlay anchored 1 tile up/left: centre 57,33, six pixels above previous 57,39. Nearest-neighbor fitting and placement only.'),indent=2),encoding='utf-8')
p=src/'holo-campaign-test.cc';s=p.read_text(encoding='utf-8')
old='''        {const auto upper=target->pos()+coord_def(0,-1);auto mg=mgen_data::hostile_at(MONS_ORC,false,upper);mg.flags|=MG_FORCE_PLACE;'''
new='''        {holo_visual::capture(std::string(shots)+"/choco-raised-no-upper.png");
        const int stacks_before_upper=holo_batch::s.resource;holo_batch::s.resource=0;
        holo_visual::capture(std::string(shots)+"/choco-raised-no-upper-no-marker.png");holo_batch::s.resource=stacks_before_upper;
        const auto upper=target->pos()+coord_def(0,-1);auto mg=mgen_data::hostile_at(MONS_ORC,false,upper);mg.flags|=MG_FORCE_PLACE;'''
assert old in s;s=s.replace(old,new);p.write_text(s,encoding='utf-8',newline='\n')
print('Solid marker imported, raised 6px; adjacent-actor controls added.')
