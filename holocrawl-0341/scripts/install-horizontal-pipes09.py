from pathlib import Path
from PIL import Image
import numpy as np
import shutil
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-explore01/assets'
p=Path('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0/exec-c5d8e9e3-3509-4434-bdd6-2fd5189414bc.png')
shutil.copyfile(p,out/'wall-pipe-horizontal09-original.png')
im=Image.open(p).convert('RGBA');a=np.asarray(im)[:,:,3]
ys=np.where((a>200).sum(axis=1)>30)[0];xs=np.where((a>200).sum(axis=0)>30)[0]
im=im.crop((int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1))
im=im.resize((96,14),Image.Resampling.LANCZOS).quantize(colors=20,method=Image.Quantize.FASTOCTREE).convert('RGBA')
im.putalpha(im.getchannel('A').point(lambda x:255 if x>100 else 0))
tile=Image.new('RGBA',(96,32));tile.alpha_composite(im,(0,9));tile.save(out/'wall-pipe-horizontal09-96.png')
print('Horizontal pipe strip:96x32, visible96x14; left/middle/right32px segments.')
