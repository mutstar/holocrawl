"""Revise native visual draft: green heal cross, multiple petals, enclosing pale barrier."""
from pathlib import Path
from PIL import Image
import sys,shutil
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source'
b=r/'analysis/native/miko-bloom02';b.mkdir(exist_ok=False)
a=r/'assets/holocrawl/miko-bloom02';a.mkdir(parents=True,exist_ok=False)
q=b/'before/rltiles/holo';q.mkdir(parents=True)
shutil.copy2(s/'rltiles/holo/fx_mikoshield.png',q/'fx_mikoshield.png')
for name,path,canvas,size in [('shield',sys.argv[1],48,44),('cross',sys.argv[2],32,11)]:
    shutil.copy2(path,a/f'{name}-original.png')
    im=Image.open(path).convert('RGBA');assert im.getextrema()[3][0]==0
    im=im.crop(im.getbbox());im.thumbnail((size,size),Image.Resampling.NEAREST)
    tile=Image.new('RGBA',(canvas,canvas));tile.alpha_composite(im,((canvas-im.width)//2,(canvas-im.height)//2))
    tile.save(a/f'{name}.png');shutil.copy2(a/f'{name}.png',s/f'rltiles/holo/fx_miko{name}.png')
def edit(name,fn):
    p=s/name;old=p.read_text(encoding='utf-8');new=fn(old);assert new!=old,name
    q=b/'before'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(old,encoding='utf-8');p.write_text(new,encoding='utf-8')
edit('rltiles/dc-holo-feat.txt',lambda t:t+'\nfx_mikocross HOLO_FX_MIKOCROSS\n')
def renderer(t):
    start=t.index('        // Test-only draft motion: reuse generated raster sprites without combat hooks.')
    end=t.index('        // Reuse the generated32px raster, enlarged4/3',start)
    return t[:start]+'''        // Native draft: green healing cross rises while five sakura blossoms gather.
        if(tileidx==TILE_HOLO_FX_MIKOBLOSSOM && crawl_state.test) {
            const int f=you.props["holo_miko_bloom_frame"].get_int();
            const int dx=(4-f)*12;
            buffer.add(TILE_HOLO_FX_MIKOCROSS,x,y,0,-24-2*f);
            buffer.add(tileidx,x,y,dx+8,-20);
            buffer.add(tileidx,x,y,dx-4,-8);
            buffer.add(tileidx,x,y,dx+2,6);
            buffer.add(tileidx,x,y,dx-12,-24);
            buffer.add(tileidx,x,y,dx-16,2);
            return;
        }
        if(tileidx==TILE_HOLO_FX_MIKOPETALSHIELD) {
            //48px transparent-center barrier surrounds the32px character.
            buffer.add(tileidx,x,y,0,0,true,-1,32.0f,32.0f);
            return;
        }
'''+t[end:]
edit('tiledgnbuf.cc',renderer)
print('Prepared green cross/five blossoms and pale enclosing barrier draft.')
