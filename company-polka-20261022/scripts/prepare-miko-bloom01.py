"""Native visual draft only. No kill/heal/shield gameplay hooks added."""
from pathlib import Path
from PIL import Image
import json,sys,shutil
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source'
b=r/'analysis/native/miko-bloom01';b.mkdir(exist_ok=False)
a=r/'assets/holocrawl/miko-bloom01';a.mkdir(parents=True,exist_ok=False)
for name,path,size in [('shield',sys.argv[1],16),('blossom',sys.argv[2],12)]:
    shutil.copy2(path,a/f'{name}-original.png')
    im=Image.open(path).convert('RGBA');assert im.getextrema()[3][0]==0
    im=im.crop(im.getbbox());im.thumbnail((size,size),Image.Resampling.NEAREST)
    tile=Image.new('RGBA',(32,32));tile.alpha_composite(im,((32-im.width)//2,(32-im.height)//2))
    tile.save(a/f'{name}32.png');shutil.copy2(a/f'{name}32.png',s/f'rltiles/holo/fx_miko{name}.png')
def edit(name,fn):
    p=s/name;old=p.read_text(encoding='utf-8');new=fn(old);assert new!=old,name
    q=b/'before'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(old,encoding='utf-8');p.write_text(new,encoding='utf-8')
edit('holo-visual.h',lambda t:t.replace('mikotorii };','mikotorii,mikoblossom,mikopetalshield };'))
edit('rltiles/dc-holo-feat.txt',lambda t:t+'\nfx_mikoblossom HOLO_FX_MIKOBLOSSOM\nfx_mikoshield HOLO_FX_MIKOPETALSHIELD\n')
def visual(t):
    anchor='    // Visual boundary markers only: no actors, collision or additional terrain.'
    t=t.replace(anchor,'''    if(crawl_state.test && you.props.exists("holo_miko_bloom_frame") && p==you.pos()) {
        const int f=you.props["holo_miko_bloom_frame"].get_int();
        if(f>=1 && f<=4)return effect::mikoblossom;
        if(f>=5 && you.props["holo_miko_bloom_mode"].get_int()==2)return effect::mikopetalshield;
    }
'''+anchor)
    t=t.replace('    if(kind==effect::mikotorii)return TILE_HOLO_FX_MIKOTORII;','    if(kind==effect::mikotorii)return TILE_HOLO_FX_MIKOTORII;\n    if(kind==effect::mikoblossom)return TILE_HOLO_FX_MIKOBLOSSOM;\n    if(kind==effect::mikopetalshield)return TILE_HOLO_FX_MIKOPETALSHIELD;')
    return t
edit('holo-visual.cc',visual)
def renderer(t):
    anchor='        // Reuse the generated32px raster, enlarged4/3 and raised above its corner.'
    new='''        // Test-only draft motion: reuse generated raster sprites without combat hooks.
        if(tileidx==TILE_HOLO_FX_MIKOBLOSSOM && crawl_state.test) {
            const int f=you.props["holo_miko_bloom_frame"].get_int();
            const int dx=(4-f)*12;
            buffer.add(tileidx,x,y,dx,-12);
            if(f<4) {
                buffer.add(tileidx,x,y,dx+6,-22);
                buffer.add(tileidx,x,y,dx+12,-2);
            }
            return;
        }
        if(tileidx==TILE_HOLO_FX_MIKOPETALSHIELD) {
            buffer.add(tileidx,x,y,18,-16);
            return;
        }
'''
    assert anchor in t;return t.replace(anchor,new+anchor)
edit('tiledgnbuf.cc',renderer)
def tests(t):
    anchor='        std::ofstream proof(dir+"/miko-review.json");'
    new='''        if(const char *bloom=getenv("HOLOCRAWL_MIKO_BLOOM_REVIEW")) {
            fixture("miko",50);cast("miko",1,nullptr,you.pos());
            you.props["holo_miko_bloom_mode"]=1;
            for(int mode=1;mode<=2;++mode) {
                you.props["holo_miko_bloom_mode"]=mode;
                for(int f=0;f<=6;++f) {
                    you.props["holo_miko_bloom_frame"]=f;
                    const auto stable=signature();
                    holo_visual::capture(std::string(bloom)+"/miko-bloom-"+std::to_string(mode)+"-"+std::to_string(f)+".png");
                    require(stable==signature(),"Miko bloom draft changed gameplay/RNG");
                    int sx=1,sy=1;
                    const auto cue=holo_visual::invocation_sprite_at(you.pos(),sx,sy);
                    if(f>=1 && f<=4)require(cue==holo_visual::effect::mikoblossom,"blossom missing");
                    if(f>=5 && mode==2)require(cue==holo_visual::effect::mikopetalshield,"shield missing");
                    if(f>=5 && mode==1)require(cue!=holo_visual::effect::mikopetalshield,"shield on heal-only draft");
                }
            }
            you.props.erase("holo_miko_bloom_frame");you.props.erase("holo_miko_bloom_mode");
            int sx=1,sy=1;
            require(holo_visual::invocation_sprite_at(you.pos(),sx,sy)!=holo_visual::effect::mikopetalshield,"draft shield leaked");
            std::ofstream(dir+"/miko-bloom.json")<<"{\\"status\\":\\"passed\\",\\"visualDraftOnly\\":true,\\"combatImplemented\\":false,\\"modes\\":2,\\"frames\\":14,\\"capturePreservesStateAndRng\\":true}";
        }
'''
    assert anchor in t;return t.replace(anchor,new+anchor)
edit('holo-campaign-test.cc',tests)
capture=(r/'scripts/capture-miko-vfx.ps1').read_text(encoding='utf-8-sig')
capture=capture.replace('miko-vfx01','miko-bloom01').replace("@('PATH',","@('PATH','HOLOCRAWL_MIKO_BLOOM_REVIEW',")
capture=capture.replace('$env:HOLOCRAWL_MIKO_REVIEW=$shots','$env:HOLOCRAWL_MIKO_REVIEW=$shots;$env:HOLOCRAWL_MIKO_BLOOM_REVIEW=$shots')
capture=capture.replace('Remove-Item Env:HOLOCRAWL_MIKO_REVIEW,Env:HOLOCRAWL_INVOCATION_CAPTURE','Remove-Item Env:HOLOCRAWL_MIKO_BLOOM_REVIEW,Env:HOLOCRAWL_MIKO_REVIEW,Env:HOLOCRAWL_INVOCATION_CAPTURE')
(r/'scripts/capture-miko-bloom01.ps1').write_text(capture,encoding='utf-8')
print('Native bloom draft prepared; no combat integration.')
