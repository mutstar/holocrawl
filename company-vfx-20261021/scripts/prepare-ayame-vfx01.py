from pathlib import Path
from PIL import Image
import json,shutil,hashlib
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source';run=root/'analysis/native/ayame-vfx01'
run.mkdir(exist_ok=False)
files=['holo-visual.cc','holo-visual.h','tilereg-dgn.cc','holo-campaign-test.cc','rltiles/dc-holo-feat.txt']
for f in files:
    p=run/'before'/f;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/f,p)
shutil.copy2(root/'runtime/tiles01/HoloCrawl.exe',run/'before/HoloCrawl.exe')
hashes={p.relative_to(src).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (src/'rltiles/holo').glob('*.png')}
for p in src.glob('holo-batch*.cc'):hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'preserved-files.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
assets=root/'assets/holocrawl/ayame-vfx01'
for name,size in [('aura',32),('slash',96),('duel',160)]:
    im=Image.open(assets/'originals'/f'{name}.png').convert('RGBA');assert im.getextrema()[3][0]==0
    im=im.crop(im.getbbox());im.thumbnail((size-2,size-2),Image.Resampling.NEAREST)
    tile=Image.new('RGBA',(size,size));tile.alpha_composite(im,((size-im.width)//2,(size-im.height)//2))
    tile.save(src/'rltiles/holo'/f'fx_ayame_{name}_0.png')
    other=tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT) if name=='slash' else tile.transpose(Image.Transpose.ROTATE_180) if name=='aura' else tile
    other.save(src/'rltiles/holo'/f'fx_ayame_{name}_1.png')
def edit(f,a,b):
    p=src/f;s=p.read_text(encoding='utf-8');assert a in s,(f,a);p.write_text(s.replace(a,b),encoding='utf-8')
edit('holo-visual.h','foxcircle,foxhit,carrot','foxcircle,foxhit,ayameaura,ayameslash,ayameduel,carrot')
lines=''.join(f'fx_ayame_{name}_{f} HOLO_FX_AYAME_{name.upper()}_{f}\n' for name in ['aura','slash','duel'] for f in range(2))
edit('rltiles/dc-holo-feat.txt','carrot HOLO_CARROT',lines+'carrot HOLO_CARROT')
edit('holo-visual.cc','flashes.clear();flash_kind=invocation_effect(g);','''flashes.clear();flash_kind=invocation_effect(g);
    if(g=="ayame" && (tier==3 || tier==5)) {
        flash_kind=tier==3?effect::ayameslash:effect::ayameduel;
        flashes.push_back(tier==3?p:holo_batch::s.centre);return;
    }''')
edit('holo-visual.cc','scaled_delay(flash_kind==effect::cometfall?', 'scaled_delay(flash_kind==effect::ayameslash || flash_kind==effect::ayameduel?110:flash_kind==effect::cometfall?')
edit('holo-visual.cc','g=="suisei" || g=="miko" || g=="aki") { prepare_invocation','g=="suisei" || g=="miko" || g=="aki" || g=="ayame") { prepare_invocation')
edit('holo-visual.cc','const auto fox=fox_cue_at(p);if(fox!=effect::none)return fox;','''const auto fox=fox_cue_at(p);if(fox!=effect::none)return fox;
    if(holo_campaign::active() && holo_worship::current()=="ayame") {
        const auto &s=holo_batch::s;const auto *mon=monster_by_mid(s.marked);
        if(p==you.pos() && s.one_end>you.elapsed_time && mon && mon->alive()
            && grid_distance(you.pos(),mon->pos())==1)return effect::ayameaura;
    }''')
edit('holo-visual.cc','span_x=span_y=1;\n    if((flash_kind', '''span_x=span_y=1;
    if((flash_kind==effect::ayameslash || flash_kind==effect::ayameduel) && !flashes.empty()) {
        const int r=flash_kind==effect::ayameslash?1:2;
        if(p==flashes.front()-coord_def(r,r)) {span_x=span_y=2*r+1;return flash_kind;}
        // The large cue is anchored once, never once per affected cell.
        if(p==flashes.front())return effect::none;
    }
    if(holo_campaign::active() && holo_worship::current()=="ayame" && holo_batch::five()
        && p==holo_batch::s.centre-coord_def(2,2)) {
        span_x=span_y=5;return effect::ayameduel;
    }
    if((flash_kind''')
edit('tilereg-dgn.cc','cue==holo_visual::effect::akibloom || cue==holo_visual::effect::foxshift','cue==holo_visual::effect::ayameduel || cue==holo_visual::effect::akibloom || cue==holo_visual::effect::foxshift')
# Test only: real ordinary melee, real double strike, real duel; no combat rules edited.
fixture='''    if(const char *shots=getenv("HOLOCRAWL_AYAME_REVIEW")) {
        auto *target=fixture("ayame",30);const auto origin=you.pos();
        for(int x=25;x<=45;++x)for(int y=25;y<=45;++y)env.pgrid(coord_def(x,y))|=FPROP_SEEN_OR_NOEXP;
        you.trapped=false;target->move_to_pos(origin+coord_def(1,0));
        require(holo_visual::invocation_at(origin)!=holo_visual::effect::ayameaura,"aura before melee");
        holo_visual::capture(std::string(shots)+"/ayame-before.png");
        bool hit=false;fight_melee(&you,target,&hit);finish_attack();
        require(holo_batch::s.marked==target->mid && holo_batch::s.one_end>you.elapsed_time,"ordinary melee did not establish interval");
        require(holo_visual::invocation_at(origin)==holo_visual::effect::ayameaura,"active interval aura missing");
        const auto stable=signature();
        for(int f=0;f<2;++f) {you.elapsed_time+=f*10;holo_visual::capture(std::string(shots)+"/ayame-aura-frame"+std::to_string(f)+".png");you.elapsed_time-=f*10;}
        require(stable==signature(),"aura capture mutated state");
        const int oneEnd=holo_batch::s.one_end;you.elapsed_time=oneEnd;
        require(holo_visual::invocation_at(origin)!=holo_visual::effect::ayameaura,"expired aura retained");
        holo_visual::capture(std::string(shots)+"/ayame-aura-expired.png");
        you.piety=180;const int before=target->hit_points;cast("ayame",3,target,target->pos());
        require(target->hit_points<before,"twin strike did not damage fixture");
        const int after=target->hit_points;cast("ayame",5,target,target->pos());
        require(holo_batch::five() && holo_batch::s.centre==origin,"duel did not start");
        int sx=0,sy=0;require(holo_visual::invocation_sprite_at(origin-coord_def(2,2),sx,sy)==holo_visual::effect::ayameduel && sx==5 && sy==5,"duel geometry wrong");
        const auto active=signature();holo_visual::capture(std::string(shots)+"/ayame-duel-active.png");require(active==signature(),"duel capture mutated state");
        you.elapsed_time=holo_batch::s.five_end;
        require(holo_visual::invocation_sprite_at(origin-coord_def(2,2),sx,sy)!=holo_visual::effect::ayameduel,"expired duel retained");
        holo_visual::capture(std::string(shots)+"/ayame-duel-expired.png");
        std::ofstream proof(dir+"/ayame-review.json");
        proof<<"{\\"status\\":\\"passed\\",\\"ordinaryMeleeAura\\":true,\\"auraExpiry\\":true,\\"duelWidth\\":5,\\"duelExpiry\\":true,\\"capturePreservesGameplay\\":true,\\"beforeStrikeHp\\":"<<before<<",\\"afterStrikeHp\\":"<<after<<"}\\n";
        close_save();return 0;
    }
'''
edit('holo-campaign-test.cc','    if(const char *shots=getenv("HOLOCRAWL_FUBUKI_REVIEW")) {',fixture+'    if(const char *shots=getenv("HOLOCRAWL_FUBUKI_REVIEW")) {')
cap=(root/'scripts/capture-fubuki-vfx.ps1').read_text(encoding='utf-8').replace('fubuki-vfx01','ayame-vfx01').replace('FUBUKI_REVIEW','AYAME_REVIEW').replace('fubuki-review.json','ayame-review.json').replace('Fubuki','Ayame')
cap=cap.replace("'HOLOCRAWL_AYAME_REVIEW')","'HOLOCRAWL_AYAME_REVIEW','HOLOCRAWL_FUBUKI_REVIEW')")
(root/'scripts/capture-ayame-vfx.ps1').write_text(cap,encoding='utf-8')
print('Ayame VFX01 source prepared, combat source and existing PNG hashes recorded.')
