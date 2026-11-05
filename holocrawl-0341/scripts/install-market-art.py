from pathlib import Path
from PIL import Image
import shutil,json

r=Path(__file__).resolve().parents[1];out=r/'preview/city-market01';a=out/'assets'
generated=Path('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0')
jobs=[('shopfront','exec-93c9d99e-3f34-4ae5-a1ce-7233ce4f0349.png',(64,32),(64,32)),('merch-rack','exec-1038d12c-7cfa-43c0-9c45-ee93011de2e5.png',(32,32),(24,27)),('delivery-boxes','exec-620795ed-db0c-4486-98f3-bbd7f9b5d402.png',(32,32),(26,24))]
manifest=[]
for name,file,canvas_size,object_size in jobs:
    original=a/f'market-{name}-original.png';shutil.copy2(generated/file,original)
    image=Image.open(original).convert('RGBA');assert image.getchannel('A').getextrema()[0]==0
    bounds=image.getchannel('A').point(lambda v:255 if v>200 else 0).getbbox();assert bounds
    sprite=image.crop(bounds).resize(object_size,Image.Resampling.NEAREST)
    canvas=Image.new('RGBA',canvas_size);canvas.alpha_composite(sprite,((canvas_size[0]-object_size[0])//2,canvas_size[1]-object_size[1]))
    target=a/f'market-{name}{canvas_size[0]}.png';canvas.save(target)
    manifest.append(dict(name=name,file=target.name,size=canvas_size,original=original.name,mode='built-in image_gen',processing='alpha crop, nearest resize, transparent padding'))
(out/'art-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
profiles=json.loads((r/'design/city-market01.json').read_text(encoding='utf-8'))['profiles']
(out/'market-profiles.js').write_text('globalThis.MarketProfiles='+json.dumps(profiles,ensure_ascii=False)+';\nif(typeof module!=="undefined"&&module.exports)module.exports=globalThis.MarketProfiles;\n',encoding='utf-8')
p=out/'index.html';html=p.read_text(encoding='utf-8');html=html.replace('<script src="market-generator.js"></script>','<script src="market-profiles.js"></script><script src="market-generator.js"></script>');p.write_text(html,encoding='utf-8')
print('Installed market shopfront64 and two32px props; native runtime unchanged.')
