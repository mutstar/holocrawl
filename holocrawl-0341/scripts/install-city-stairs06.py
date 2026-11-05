from pathlib import Path
from PIL import Image
import numpy as np
import shutil
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-floor06/assets'
p=Path('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0/exec-2745cde5-5190-4671-8b67-5364cd89ff27.png')
shutil.copyfile(p,out/'thick-stairs-up-original.png')
im=Image.open(p).convert('RGBA');a=np.asarray(im)[:,:,3]
ys=np.where((a>200).sum(axis=1)>40)[0];xs=np.where((a>200).sum(axis=0)>40)[0]
im=im.crop((int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1))
im=im.resize((32,32),Image.Resampling.LANCZOS).quantize(colors=20,method=Image.Quantize.FASTOCTREE).convert('RGBA')
im.putalpha(im.getchannel('A').point(lambda x:255 if x>100 else 0))
im.save(out/'thick-stairs-up32.png')
assert (out/'city-stairs-down-final32.png').read_bytes()==(root/'preview/city-floor05/assets/city-stairs-down-final32.png').read_bytes()
print('Thick ascent installed; approved descent byte-identical.')
