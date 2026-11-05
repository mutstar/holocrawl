from pathlib import Path
from PIL import Image
import numpy as np
import shutil
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-floor05/assets'
generated=Path('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0')
for kind,name in [('up','exec-8c4366ac-f328-4b5a-a973-2a4ce90326c1.png'),('down','exec-8781c8bd-c7dd-4403-88a0-b65c62a190f2.png')]:
 shutil.copyfile(generated/name,out/f'outlined-stairs-{kind}-original.png')
 im=Image.open(generated/name).convert('RGBA');a=np.asarray(im)[:,:,3]
 ys=np.where((a>200).sum(axis=1)>40)[0];xs=np.where((a>200).sum(axis=0)>40)[0]
 im=im.crop((int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1))
 im=im.resize((32,32),Image.Resampling.LANCZOS).quantize(colors=20,method=Image.Quantize.FASTOCTREE).convert('RGBA')
 im.putalpha(im.getchannel('A').point(lambda x:255 if x>100 else 0))
 im.save(out/f'outlined-stairs-{kind}32.png')
 print(kind,im.size)
