from pathlib import Path
from PIL import Image
import json,shutil

r=Path(__file__).resolve().parents[1];out=r/'preview/city-market02';props=out/'assets/props';originals=props/'originals';originals.mkdir(parents=True,exist_ok=True)
jobs=json.loads((r/'analysis/market02/art-jobs.json').read_text(encoding='utf-8'));manifest=[]
for job in jobs:
    source=Path(job['source']);shutil.copy2(source,originals/(job['id']+'.png'))
    image=Image.open(source).convert('RGBA');assert image.getchannel('A').getextrema()[0]==0,job['id']
    bounds=image.getchannel('A').point(lambda a:255 if a>200 else 0).getbbox();assert bounds
    canvas=Image.new('RGBA',(job['w'],job['h']))
    if job['kind']=='wall':size=(64,32)
    elif job['id']=='paper-rubbish':size=(28,19)
    elif job['id']=='acrylic-rack':size=(28,28)
    else:size=(26,26)
    sprite=image.crop(bounds).resize(size,Image.Resampling.NEAREST);canvas.alpha_composite(sprite,((job['w']-size[0])//2,job['h']-size[1]))
    canvas.save(props/(job['id']+'.png'));manifest.append(dict(id=job['id'],size=[job['w'],job['h']],kind=job['kind'],source='originals/'+job['id']+'.png',prompt=job['prompt'],mode='built-in image_gen',processing='alpha bounds / nearest resize / transparent padding'))
shutil.copy2(r/'preview/city-market01/assets/market-delivery-boxes32.png',props/'delivery-boxes.png')
manifest.append(dict(id='delivery-boxes',size=[32,32],kind='floor',source='../market-delivery-boxes-original.png',mode='reuse existing approved-style generated art'))
(out/'art-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Installed20 distinct fixtures, including19 new generated assets.')
