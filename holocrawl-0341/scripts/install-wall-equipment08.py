from pathlib import Path
from PIL import Image
import numpy as np
import shutil
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-explore01/assets'
generated=Path('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0')
for name,filename,limit in [('pipe','exec-10cf81b4-1963-4ec9-b7ba-a13c03fc0231.png',(24,28)),('cabinet','exec-fddcd922-5da0-42d1-b3e8-7ede01d90604.png',(24,20))]:
 p=generated/filename
 shutil.copyfile(p,out/f'wall-{name}08-original.png')
 im=Image.open(p).convert('RGBA');a=np.asarray(im)[:,:,3]
 ys=np.where((a>200).sum(axis=1)>30)[0];xs=np.where((a>200).sum(axis=0)>30)[0]
 im=im.crop((int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1))
 im=im.resize(limit,Image.Resampling.LANCZOS)
 im=im.quantize(colors=20,method=Image.Quantize.FASTOCTREE).convert('RGBA')
 im.putalpha(im.getchannel('A').point(lambda x:255 if x>100 else 0))
 tile=Image.new('RGBA',(32,32));tile.alpha_composite(im,((32-im.width)//2,(32-im.height)//2));tile.save(out/f'wall-{name}08-32.png')
 print(name,im.size)
