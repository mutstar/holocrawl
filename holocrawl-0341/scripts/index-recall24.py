from pathlib import Path
from datetime import datetime
from PIL import Image,ImageDraw,ImageFont
import json
src=Path('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0');out=Path(__file__).resolve().parents[1]/'analysis/recall24';out.mkdir(parents=True,exist_ok=True)
files=sorted((p for p in src.glob('*.png')if datetime.fromtimestamp(p.stat().st_mtime)>=datetime(2026,10,30)),key=lambda p:p.stat().st_mtime)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
for start in range(0,len(files),30):
 sheet=Image.new('RGB',(1250,1320),(36,39,39));d=ImageDraw.Draw(sheet)
 for n,p in enumerate(files[start:start+30]):
  im=Image.open(p).convert('RGBA');im.thumbnail((244,190));x=n%5*250;y=n//5*220;sheet.paste(im,(x+(250-im.width)//2,y),im);d.text((x+5,y+194),f'{start+n}: '+datetime.fromtimestamp(p.stat().st_mtime).strftime('%m-%d %H:%M'),font=font,fill='white')
 sheet.save(out/f'sheet-{start//30}.jpg',quality=90)
(out/'index.json').write_text(json.dumps([str(p)for p in files],indent=2),encoding='utf-8')
print(len(files))
