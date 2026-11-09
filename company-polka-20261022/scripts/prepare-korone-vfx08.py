"""Split existing aura texture at render time; no bitmap changes."""
from pathlib import Path
import hashlib,json,shutil
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source'
run=root/'analysis/native/korone-vfx08';run.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=src/'tiledgnbuf.cc'
preserved={q.relative_to(src).as_posix():sha(q) for q in src.rglob('*') if q.is_file() and ((q.parent==src and q.suffix in ('.cc','.h')) or q.parent==src/'rltiles/holo') and q!=p}
(run/'preserved-files.json').write_text(json.dumps(preserved,indent=2),encoding='utf-8')
(run/'before').mkdir();shutil.copy2(p,run/'before/tiledgnbuf.cc');shutil.copy2(root/'runtime/tiles01/HoloCrawl.exe',run/'before/HoloCrawl.exe')
s=p.read_text(encoding='utf-8');s=s.replace('#include "tilebuf', '#include "tilebuf',1)
assert '#include "tiletex.h"' not in s;s=s.replace('#include "tilepick.h"','#include "tilepick.h"\n#include "tiletex.h"',1)
old='''        buffer.add(tileidx,x,y,(inf.width-TILE_X)/2,inf.height-TILE_Y,
            true,-1,float(inf.width)/span_x,float(inf.height)/span_y);
'''
new=old+'''        // Korone's awakening: keep the complete aura beneath actors, then
        // reveal only the two paw glyphs above actors using the same texture.
        // UV cropping preserves every source pixel, position and scale.
        if(under_actors && (tileidx==holo_visual::effect_tile(holo_visual::effect::night_korone5,0)
            || tileidx==holo_visual::effect_tile(holo_visual::effect::night_korone5,1))) {
            const auto *texture=static_cast<const TilesTexture *>(m_buf_holo_vfx.current_texture());
            float sx=x,sy=y,ex,ey,tx,ty,ux,uy;
            if(texture->get_coords(tileidx,(inf.width-TILE_X)/2,inf.height-TILE_Y,
                sx,sy,ex,ey,tx,ty,ux,uy,true,-1,-1,
                float(inf.width)/span_x,float(inf.height)/span_y)) {
                auto paw=[&](float left,float top,float right,float bottom) {
                    GLWPrim rect(sx+(ex-sx)*left,sy+(ey-sy)*top,
                        sx+(ex-sx)*right,sy+(ey-sy)*bottom);
                    rect.set_tex(tx+(ux-tx)*left,ty+(uy-ty)*top,
                        tx+(ux-tx)*right,ty+(uy-ty)*bottom);
                    m_buf_holo_vfx.add_primitive(rect);
                };
                paw(0.0f,0.42f,0.36f,0.80f);
                paw(0.64f,0.42f,1.0f,0.80f);
            }
        }
'''
assert old in s;s=s.replace(old,new,1);p.write_text(s,encoding='utf-8')
(run/'source_snapshot').mkdir();shutil.copy2(p,run/'source_snapshot/tiledgnbuf.cc')
(run/'art-validation.json').write_text(json.dumps(dict(status='passed',revision='korone-vfx08',tier=5,bitmapChanges=False,sourceTexture='assets/holocrawl/korone-vfx07/awakening.png',splitLayers='Whole aura under actors; only two UV-cropped paw glyphs above actors',pawRegions=[[0,.42,.36,.80],[.64,.42,1,.80]],sizes=[48,56],frameMilliseconds=110,activationFrames=[0,1,0,1],changed=['tiledgnbuf.cc'],numericChanges=False),indent=2),encoding='utf-8')
s=(root/'scripts/capture-korone-vfx07.ps1').read_text(encoding='utf-8').replace('korone-vfx07','korone-vfx08');(root/'scripts/capture-korone-vfx08.ps1').write_text(s,encoding='utf-8')
print('Existing texture split at render time: aura behind, two cropped paws in front; art/timing unchanged.')
