from pathlib import Path
from PIL import Image
import sys,shutil
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source'
b=r/'analysis/native/miko-bloom03';b.mkdir(exist_ok=False)
a=r/'assets/holocrawl/miko-bloom03';a.mkdir(parents=True,exist_ok=False)
q=b/'before/rltiles/holo';q.mkdir(parents=True)
shutil.copy2(s/'rltiles/holo/fx_mikoshield.png',q/'fx_mikoshield.png')
shutil.copy2(sys.argv[1],a/'circle-original.png')
im=Image.open(sys.argv[1]).convert('RGBA');assert im.getextrema()[3][0]==0
im=im.crop(im.getbbox()).resize((36,36),Image.Resampling.NEAREST)
tile=Image.new('RGBA',(48,48));tile.alpha_composite(im,(6,6));tile.save(a/'circle48.png')
shutil.copy2(a/'circle48.png',s/'rltiles/holo/fx_mikoshield.png')
p=s/'tiledgnbuf.cc';old=p.read_text(encoding='utf-8');q=b/'before/tiledgnbuf.cc';q.write_text(old,encoding='utf-8')
text=old.replace('//48px transparent-center barrier surrounds the32px character.','//36px circular barrier is centered on the32px character body.')
anchor='buffer.add(tileidx,x,y,0,0,true,-1,32.0f,32.0f);'
assert anchor in text;text=text.replace(anchor,'buffer.add(tileidx,x,y,0,8,true,-1,32.0f,32.0f);')
p.write_text(text,encoding='utf-8')
f=r/'scripts/finish-miko-bloom02.py'
text=f.read_text(encoding='utf-8').replace('miko-bloom02','miko-bloom03').replace('연한 분홍색 타원 보호막','연한 분홍색 원형 보호막').replace('pale pink transparent-center oval barrier','pale pink transparent-center circular barrier')
(r/'scripts/finish-miko-bloom03.py').write_text(text,encoding='utf-8')
print('Prepared36px circle,body-centered; existing healing effect retained.')
