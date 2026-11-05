from pathlib import Path
from PIL import Image
import shutil
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-floor04/assets'
generated=Path('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0')
for kind,name in [('up','exec-d4070af2-a770-4dd5-9d24-011027eff095.png'),('down','exec-5309640b-6128-4233-aedb-db51e4cf9673.png')]:
 source=generated/name
 shutil.copyfile(source,out/f'city-stairs-{kind}-original.png')
 im=Image.open(source).convert('RGBA')
 if kind=='down':im=im.crop((22,22,im.width-22,im.height-22))
 else:im=im.crop(im.getchannel('A').point(lambda x:255 if x>128 else 0).getbbox())
 im=im.resize((32,32),Image.Resampling.LANCZOS).quantize(colors=20,method=Image.Quantize.FASTOCTREE).convert('RGBA')
 im.putalpha(im.getchannel('A').point(lambda x:255 if x>100 else 0))
 im.save(out/f'city-stairs-{kind}32.png')
 print(kind,im.size)
