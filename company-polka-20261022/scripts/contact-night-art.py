from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1];asset=root/'assets/holocrawl/night-vfx01'
files=sorted((asset/'originals').glob('*.png'));assert len(files)==16
sheet=Image.new('RGB',(1024,1024),'#17202c');draw=ImageDraw.Draw(sheet)
for i,p in enumerate(files):
    im=Image.open(p).convert('RGBA');assert im.getextrema()[3][0]==0
    im=im.crop(im.getbbox());im.thumbnail((230,220),Image.Resampling.NEAREST)
    x=i%4*256;y=i//4*256;sheet.paste(im,(x+(256-im.width)//2,y+25),im);draw.text((x+8,y+5),p.stem,fill='white')
sheet.save(asset/'originals-contact.png')
