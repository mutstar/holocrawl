from pathlib import Path
from PIL import Image
import sys,shutil
r=Path(__file__).resolve().parents[1];d=r/'analysis/previews/street-stairs06'
for kind,source in zip(['up','down'],sys.argv[1:]):
 a=d/'assets';original=a/f'stairs-{kind}06-original.png';shutil.copy2(source,original)
 im=Image.open(original).convert('RGBA');assert im.getchannel('A').getextrema()[0]==0
 box=im.getchannel('A').point(lambda a:255 if a>200 else 0).getbbox()
 im.crop(box).resize((32,32),Image.Resampling.NEAREST).save(a/f'stairs-{kind}06-32.png')
 print(kind,box)


