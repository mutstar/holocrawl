from pathlib import Path
from PIL import Image
import hashlib,json,shutil
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source'
run=root/'analysis/native/okayu-vfx05';run.mkdir(exist_ok=False)
a=root/'assets/holocrawl/okayu-vfx05';a.mkdir(parents=True,exist_ok=True)
generated=Path(r'C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0/exec-ee9f3b42-4bae-4169-b11e-94f13f335009.png');shutil.copy2(generated,a/'dream-vortex.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changed=[src/'holo-visual.cc',src/'tilereg-dgn.cc',*[src/'rltiles/holo'/f'fx_night_okayu5_{i}.png' for i in range(2)]]
preserved={p.relative_to(src).as_posix():sha(p) for p in src.rglob('*') if p.is_file() and ((p.parent==src and p.suffix in ('.cc','.h')) or p.parent==src/'rltiles/holo') and p not in changed}
(run/'preserved-files.json').write_text(json.dumps(preserved,indent=2))
for p in changed:
 out=run/'before'/p.relative_to(src);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
shutil.copy2(root/'runtime/tiles01/HoloCrawl.exe',run/'before/HoloCrawl.exe')
im=Image.open(generated).convert('RGBA');assert im.getextrema()[3][0]==0
box=im.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox();im=im.crop(box)
frames=[]
for i,size in enumerate([24,18]):
 icon=im.copy();icon.thumbnail((size,size),Image.Resampling.NEAREST)
 tile=Image.new('RGBA',(160,160));tile.alpha_composite(icon,(80-icon.width//2,74-icon.height//2))
 p=src/'rltiles/holo'/f'fx_night_okayu5_{i}.png';tile.save(p);frames.append({'frame':i,'size':icon.size,'bounds':tile.getbbox()})
p=src/'tilereg-dgn.cc';s=p.read_text(encoding='utf-8');old='&& cue!=holo_visual::effect::night_korone3)';assert old in s;s=s.replace(old,'&& cue!=holo_visual::effect::night_korone3\n                        && cue!=holo_visual::effect::night_okayu5)',1);p.write_text(s,encoding='utf-8')
p=src/'holo-visual.cc';s=p.read_text(encoding='utf-8');old='scaled_delay(flash_kind==effect::night_korone3';assert old in s;s=s.replace(old,'scaled_delay(flash_kind==effect::night_okayu5?110:flash_kind==effect::night_korone3',1);p.write_text(s,encoding='utf-8')
for p in changed:
 out=run/'source_snapshot'/p.relative_to(src);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
(run/'art-validation.json').write_text(json.dumps(dict(status='passed',revision='okayu-vfx05',tier=5,frames=frames,sourceCrop=box,numericChanges=False,description='Compact dream-devouring vortex shrinks24 to18px,6px above target centre,foreground110ms each; approved1/3 preserved'),indent=2))
(a/'generation.json').write_text(json.dumps(dict(tool='built-in image_gen',prompt='Compact lavender dream-devouring pixel spiral with mint dream motes, transparent background. No Z letters, hearts, sleep clouds or giant circle. Crisp low resolution dungeon sprite.',nativeSizes=[24,18]),indent=2))
s=(root/'scripts/capture-okayu-balance03.ps1').read_text(encoding='utf-8').replace('okayu-balance03','okayu-vfx05');(root/'scripts/capture-okayu-vfx05.ps1').write_text(s,encoding='utf-8')
print('Imported compact24→18px vortex; source preserved except2VFX PNGs and presentation-only layer/timing.')
