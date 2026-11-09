from pathlib import Path
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source'
b=r/'analysis/native/miko-torii02';b.mkdir(exist_ok=False)
def edit(name,fn):
    p=s/name;old=p.read_text(encoding='utf-8');new=fn(old);assert new!=old
    q=b/'before'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(old,encoding='utf-8');p.write_text(new,encoding='utf-8')
def ground(t):
    old='''            base=holo_batch::five() && p==s.centre
                ?effect::mikodomain:effect::shrine;'''
    new='''            base=holo_batch::five() && std::abs(p.x-s.centre.x)==3 && std::abs(p.y-s.centre.y)==3
                ?effect::none:holo_batch::five() && p==s.centre?effect::mikodomain:effect::shrine;'''
    assert old in t;return t.replace(old,new)
edit('holo-visual.cc',ground)
def renderer(t):
    old='''        auto &buffer=under_actors?m_buf_holo_ground_vfx:m_buf_holo_vfx;'''
    new=old+'''
        // Reuse the generated32px raster, enlarged4/3 and raised above its corner.
        // No new terrain/collision footprint; preserve the existing7x7 domain.
        if(tileidx==TILE_HOLO_FX_MIKOTORII) {
            buffer.add(tileidx,x,y,4,8,true,-1,24.0f,24.0f);
            return;
        }'''
    assert old in t;return t.replace(old,new)
edit('tiledgnbuf.cc',renderer)
print('Torii render scale4/3; raised; corner floor glyph removed during tier5.')
