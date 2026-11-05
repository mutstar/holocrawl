from pathlib import Path
from PIL import Image
import numpy as np
import shutil,json
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-explore01/assets'
p=Path('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0/exec-af88e1d8-a5fd-49dd-8283-e7a57a84f33b.png')
shutil.copyfile(p,out/'wall-pipe-elbows10-original.png')
im=Image.open(p).convert('RGBA');a=np.asarray(im)[:,:,3]
ys=np.where((a>200).sum(axis=1)>30)[0];xs=np.where((a>200).sum(axis=0)>30)[0]
im=im.crop((int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1))
im=im.resize((96,30),Image.Resampling.LANCZOS).quantize(colors=20,method=Image.Quantize.FASTOCTREE).convert('RGBA')
im.putalpha(im.getchannel('A').point(lambda x:255 if x>100 else 0))
tile=Image.new('RGBA',(96,32));tile.alpha_composite(im,(0,1));tile.save(out/'wall-pipe-elbows10-96.png')
a=np.asarray(tile)[:,:,3];left=np.where((a[:,:12]>128).any(axis=1))[0];right=np.where((a[:,-12:]>128).any(axis=1))[0]
assert left.min()<right.min() and left.max()<right.max(),(left.tolist(),right.tolist())
(out.parent/'pipe-elbows10-direction.json').write_text(json.dumps({'leftAlphaRows':[int(left.min()),int(left.max())],'rightAlphaRows':[int(right.min()),int(right.max())],'left':'up','right':'down'},indent=2),encoding='utf-8')
print('Opposite pipe elbows verified: left up, right down.')
