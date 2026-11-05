from pathlib import Path
from PIL import Image
import numpy as np

root=Path(__file__).resolve().parents[1]
out=root/'preview/city-complete03/assets'
for kind,limit in [('up',(28,30)),('down',(30,29))]:
    im=Image.open(out/f'stairs-{kind}-grounded-original.png').convert('RGBA')
    alpha=np.asarray(im)[:,:,3]
    # Ignore sparse generation specks outside the actual sprite when fitting a tile.
    ys=np.where((alpha>200).sum(axis=1)>40)[0]
    xs=np.where((alpha>200).sum(axis=0)>40)[0]
    im=im.crop((int(xs.min())-2,int(ys.min())-2,int(xs.max())+3,int(ys.max())+3))
    im.thumbnail(limit,Image.Resampling.LANCZOS)
    im=im.quantize(colors=20,method=Image.Quantize.FASTOCTREE).convert('RGBA')
    im.putalpha(im.getchannel('A').point(lambda x:255 if x>100 else 0))
    tile=Image.new('RGBA',(32,32))
    tile.alpha_composite(im,((32-im.width)//2,31-im.height if kind=='up' else (32-im.height)//2))
    tile.save(out/f'stairs-{kind}-grounded32.png')
    print(kind,im.size)
