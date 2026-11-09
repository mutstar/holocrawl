"""Check native framebuffer paw visibility against the unchanged source pixels."""
from pathlib import Path
from PIL import Image
import json,math
root=Path(__file__).resolve().parents[1];run=root/'analysis/native/korone-vfx09'
checks=[]
for f in range(2):
    tile=Image.open(root/f'engine/campaign-crawl/crawl-ref/source/rltiles/holo/fx_night_korone5_{f}.png').convert('RGBA')
    shot=Image.open(run/f'native/shots/korone-tier5-option0-19-frame{f}.png').convert('RGB')
    old=Image.open(root/f'analysis/native/korone-vfx07/native/shots/korone-tier5-option0-19-frame{f}.png').convert('RGB')
    bx,by,ex,ey=tile.getbbox();w,h=ex-bx,ey-by
    for side,l,r in [('left',0,.36),('right',.64,1)]:
        samples=matched=before=0
        for y in range(math.ceil(by+h*.39)+1,math.floor(by+h*.82)-1):
            for x in range(math.ceil(bx+w*l)+1,math.floor(bx+w*r)-1):
                pixel=tile.getpixel((x,y))
                if pixel[3]<250:continue
                samples+=1;expected=pixel[:3]
                close=lambda actual: max(abs(a-b) for a,b in zip(actual,expected))<=7
                matched+=close(shot.getpixel((291+x,260+y)))
                before+=close(old.getpixel((291+x,260+y)))
        checks.append(dict(frame=f,side=side,opaqueSamples=samples,matchingAfter=matched,matchingBefore=before,visibleFraction=matched/max(1,samples)))
        assert samples>20 and matched/samples>.9,checks[-1]
        if side=='right':assert matched>before,checks[-1]
(run/'paw-layer-validation.json').write_text(json.dumps(dict(status='passed',checks=checks,scope='Fixed arena sample verifies both opaque paw interiors on top of actors; art/scale/position unchanged.'),indent=2),encoding='utf-8')
print(json.dumps(checks))
