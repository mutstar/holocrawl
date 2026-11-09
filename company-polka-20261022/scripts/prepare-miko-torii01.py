"""Integrate generated torii as a visual-only 5-star corner marker."""
from pathlib import Path
from PIL import Image
import sys,shutil,json
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source'
b=r/'analysis/native/miko-torii01';b.mkdir(exist_ok=False)
a=r/'assets/holocrawl/miko-torii01';a.mkdir(parents=True,exist_ok=False)
source=Path(sys.argv[1]);shutil.copy2(source,a/'generated-original.png')
im=Image.open(source).convert('RGBA')
assert im.getextrema()[3][0]==0,'Generated sprite needs actual alpha'
box=im.getbbox();im=im.crop(box)
im.thumbnail((26,27),Image.Resampling.NEAREST)
tile=Image.new('RGBA',(32,32));tile.alpha_composite(im,((32-im.width)//2,30-im.height))
tile.save(a/'torii32.png');tile.resize((320,320),Image.Resampling.NEAREST).save(a/'torii-preview.png')
shutil.copy2(a/'torii32.png',s/'rltiles/holo/fx_mikotorii.png')
def edit(name,fn):
    p=s/name;old=p.read_text(encoding='utf-8');text=fn(old);assert text!=old,name
    save=b/'before'/name;save.parent.mkdir(parents=True,exist_ok=True);save.write_text(old,encoding='utf-8');p.write_text(text,encoding='utf-8')
edit('holo-visual.h',lambda t:t.replace('suiseistars3 };','suiseistars3,mikotorii };'))
edit('rltiles/dc-holo-feat.txt',lambda t:t+'\nfx_mikotorii HOLO_FX_MIKOTORII\n')
def visual(t):
    t=t.replace('holo_batch::five() && ((std::abs(p.x-s.centre.x)==3 && std::abs(p.y-s.centre.y)==3) || p==s.centre)','holo_batch::five() && p==s.centre')
    anchor='    // Approved stack indicator: read combat state, without gameplay writes.'
    assert anchor in t
    t=t.replace(anchor,'''    // Visual boundary markers only: no actors, collision or additional terrain.
    if(holo_campaign::active() && holo_worship::current()=="miko"
        && holo_batch::s.one_end>you.elapsed_time && holo_batch::five()
        && std::abs(p.x-holo_batch::s.centre.x)==3
        && std::abs(p.y-holo_batch::s.centre.y)==3
        && area(p,holo_batch::s.centre,3))return effect::mikotorii;
'''+anchor)
    t=t.replace('    if(kind==effect::none)return 0;','    if(kind==effect::none)return 0;\n    if(kind==effect::mikotorii)return TILE_HOLO_FX_MIKOTORII;')
    return t
edit('holo-visual.cc',visual)
def test(t):
    t=t.replace('require(has(you.pos()+coord_def(3,3),holo_visual::effect::mikodomain),"great shrine edge missing");','''int sx=1,sy=1;
        for(int x:{-3,3})for(int y:{-3,3})
            require(holo_visual::invocation_sprite_at(you.pos()+coord_def(x,y),sx,sy)==holo_visual::effect::mikotorii && sx==1 && sy==1,"torii missing at domain corner");
        require(holo_visual::invocation_sprite_at(you.pos()+coord_def(2,2),sx,sy)!=holo_visual::effect::mikotorii,"torii inside domain");''')
    t=t.replace('require(!has(you.pos()+coord_def(3,3),holo_visual::effect::mikodomain),"expired domain still rendered");','require(holo_visual::invocation_sprite_at(you.pos()+coord_def(3,3),sx,sy)!=holo_visual::effect::mikotorii,"expired torii still rendered");')
    return t
edit('holo-campaign-test.cc',test)
(a/'generation.json').write_text(json.dumps({'tool':'built-in image_gen','original':str(source),'processing':'Transparent generated raster cropped to alpha bounds, nearest-neighbor fitted within26x27, centered on32x32. No hand-drawn replacement.','prompt':(a.parent.parent.parent/'scripts/miko-torii-prompt.txt').read_text(encoding='utf-8')},ensure_ascii=False,indent=2),encoding='utf-8')
print('Torii sprite and four native corner markers integrated.')
