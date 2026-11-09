from pathlib import Path
from PIL import Image
import sys,shutil,json
r=Path(__file__).resolve().parents[1];d=r/'analysis/previews/street-walls01';a=d/'assets'
shutil.copy2(sys.argv[1],a/'fence-cutout-original.png')
im=Image.open(a/'fence-cutout-original.png').convert('RGBA')
assert im.getchannel('A').getextrema()[0]==0,'Generated asset must have real transparency'
im.resize((32,22),Image.Resampling.NEAREST).save(a/'fence-cutout32.png')
p=d/'app.js';s=p.read_text(encoding='utf-8').replace("const sources={floor:","const sources={fence:'assets/fence-cutout32.png',floor:")
s=s.replace("texture([319,134,30,17],prop.x*t,prop.y*t+t*.4,t,t*.6);","ctx.drawImage(images.fence,prop.x*t,prop.y*t+t*.31,t,t*.69);")
p.write_text(s,encoding='utf-8')
p=d/'index.html';p.write_text(p.read_text(encoding='utf-8').replace('v=fence-view','v=fence-alpha01'),encoding='utf-8')
json.dump({'mode':'built-in image_gen','prompt':'Extract/recreate a single silver crowd-control fence in the reference pixel-art style. True alpha background including all gaps between bars, no pavement or black backing; five vertical bars, tubular frame, two feet; crisp readable at 32x18 pixels.','asset':'assets/fence-cutout32.png','alphaMinimum':0,'runtimeChanged':False},open(d/'fence-cutout-generation.json','w'),indent=2)
print('Installed transparent fence sprite.')
