from pathlib import Path
from PIL import Image
import json,shutil,hashlib
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source';run=root/'analysis/native/night-vfx01';run.mkdir(exist_ok=True)
assert not (run/'before').exists(),'Preserve existing run'
gods=list(json.loads((root/'assets/holocrawl/night-vfx01/inputs.json').read_text())['prompts'])
assert len(gods)==16
for g in gods:assert (root/'assets/holocrawl/night-vfx01/originals'/f'{g}.png').is_file(),g
files=['holo-visual.cc','holo-visual.h','tilereg-dgn.cc','holo-campaign.cc','holo-campaign-test.cc','rltiles/dc-holo-feat.txt']
for f in files:
    p=run/'before'/f;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/f,p)
shutil.copy2(root/'runtime/tiles01/HoloCrawl.exe',run/'before/HoloCrawl.exe')
hashes={p.relative_to(src).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (src/'rltiles/holo').glob('*.png') if not p.name.startswith('fx_chocoheart')}
for p in src.glob('holo-batch*.cc'):hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'preserved-files.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
def fit(path,size):
    im=Image.open(path).convert('RGBA');assert im.getextrema()[3][0]==0,path
    im=im.crop(im.getbbox());im.thumbnail((size,size),Image.Resampling.NEAREST);return im
def place(im,size,cx,cy):
    out=Image.new('RGBA',(size,size));out.alpha_composite(im,(cx-im.width//2,cy-im.height//2));return out
names=[]
for g in gods:
    for tier,size in [(1,32),(3,96),(5,160)]:
        name=f'night_{g}{tier}';names.append(name)
        for f in range(2):
            n=(10-f) if tier==1 else (68+12*f if tier==3 else 116+32*f)
            im=fit(root/'assets/holocrawl/night-vfx01/originals'/f'{g}.png',n)
            out=place(im,size,26 if tier==1 else size//2,7 if tier==1 else size//2)
            out.save(src/'rltiles/holo'/f'fx_{name}_{f}.png')
# Requested Choco marker stays strictly inside target's tile, upper-right corner.
corner=[]
for n in range(1,6):
    for f in range(2):
        out=place(fit(root/'assets/holocrawl/choco-vfx01/originals/heart.png',6+n+(1-f)),96,57,39)
        bbox=out.getbbox();assert bbox[0]>=32 and bbox[1]>=32 and bbox[2]<=64 and bbox[3]<=64,bbox
        out.save(src/'rltiles/holo'/f'fx_chocoheart{n}_{f}.png');corner.append({'stack':n,'frame':f,'alphaBounds':bbox})
(run/'corner-art-validation.json').write_text(json.dumps({'status':'passed','targetTileBounds':[32,32,64,64],'frames':corner},indent=2),encoding='utf-8')
# Additional selectable effects reuse established native motifs; no pixel repainting.
extras=[('night_polkaheal','charm',160),('night_polkachaos','circus',160),('night_radenstone','impact',96),('night_radencraft','shield',96)]
for name,base,size in extras:
    names.append(name)
    for f in range(2):place(fit(src/'rltiles/holo'/f'fx_{base}_{f}.png',size-12),size,size//2,size//2).save(src/'rltiles/holo'/f'fx_{name}_{f}.png')
def edit(f,a,b):
    p=src/f;s=p.read_text(encoding='utf-8');assert a in s,(f,a);p.write_text(s.replace(a,b),encoding='utf-8')
edit('holo-visual.h','chocoabsorb7,carrot','chocoabsorb7,'+','.join(names)+',carrot')
edit('holo-visual.h','void invocation(const std::string &god,int tier,const coord_def &pos);','void invocation(const std::string &god,int tier,const coord_def &pos,int option=0);')
edit('holo-visual.h','bool impact_phase=false);','bool impact_phase=false,int option=0);')
edit('rltiles/dc-holo-feat.txt','carrot HOLO_CARROT',''.join(f'fx_{n}_{f} HOLO_FX_{n.upper()}_{f}\n' for n in names for f in range(2))+'carrot HOLO_CARROT')
decl='const std::vector<std::string> night_gods={'+','.join('"'+g+'"' for g in gods)+'};'
helper=decl+'''
effect night_effect(const std::string &g,int tier,int option=0) {
    const auto it=std::find(night_gods.begin(),night_gods.end(),g);
    if(it==night_gods.end())return effect::none;
    if(g=="polka" && tier==5 && option==1)return effect::night_polkaheal;
    if(g=="polka" && tier==5 && option==2)return effect::night_polkachaos;
    if(g=="raden" && tier==3 && option==1)return effect::night_radenstone;
    if(g=="raden" && tier==3 && option==2)return effect::night_radencraft;
    return effect(int(effect::night_korone1)+3*int(it-night_gods.begin())+(tier==1?0:tier==3?1:2));
}
int night_span(effect e) {
    if(e>=effect::night_korone1 && e<=effect::night_mela5)return (int(e)-int(effect::night_korone1))%3==0?1:(int(e)-int(effect::night_korone1))%3==1?3:5;
    if(e==effect::night_polkaheal || e==effect::night_polkachaos)return 5;
    if(e==effect::night_radenstone || e==effect::night_radencraft)return 3;
    return 0;
}
effect night_status(const coord_def &p) {
    if(p!=you.pos() || !holo_campaign::active() || you.piety<30)return effect::none;
    const auto g=holo_worship::current();const auto &s=holo_batch::s;const int now=you.elapsed_time;
    bool on=false;
    if(g=="noel")on=holo_campaign::noel_fighting_bonus(1)>0 || holo_campaign::noel_commander();
    else if(g=="sopia")on=holo_sopia::visual_at(p+coord_def(1,0))!=effect::none;
    else if(g=="korone" || g=="lamy" || g=="hajime")on=s.resource>0;
    else if(g=="okayu")on=s.resource>0 || s.shield>0;
    else if(g=="watame")on=you.hp<you.hp_max || s.three_end>now || s.five_end>now;
    else if(g=="towa" || g=="su" || g=="mela")on=true; // passive readiness, not a hit assertion
    else if(g=="raden")on=true; // current exhibit readiness
    else if(g=="koyori")on=s.stock[0]+s.stock[1]+s.stock[2]>0 || holo_campaign::reactions_enabled();
    else if(g=="lui")on=!s.companions.empty();
    else if(g=="vivi" || g=="polka")on=s.one_end>now || s.five_end>now;
    return on?night_effect(g,1):effect::none;
}
'''
edit('holo-visual.cc','effect choco_mark(const coord_def &p) {',helper+'\neffect choco_mark(const coord_def &p) {')
edit('holo-visual.cc','void prepare_invocation(const std::string &g,int tier,const coord_def &p,bool impact_phase=false) {','void prepare_invocation(const std::string &g,int tier,const coord_def &p,bool impact_phase=false,int option=0) {')
# C++11: do not use a C++17 if-initializer.
edit('holo-visual.cc','flashes.clear();flash_kind=invocation_effect(g);','''flashes.clear();flash_kind=invocation_effect(g);
    const auto style=night_effect(g,tier,option);
    if(style!=effect::none) {
        flash_kind=style;coord_def centre=p;
        if(g=="towa" && tier==5)centre=holo_batch::s.centre;
        else if(tier==5 && g!="sopia" && g!="okayu" && !(g=="polka" && option==0))centre=you.pos();
        if(tier==1 && g!="pekora")centre=you.pos();
        flashes.push_back(centre);return;
    }''')
edit('holo-visual.cc','span_x=span_y=1;\n    if(choco_large','''span_x=span_y=1;
    const int ns=night_span(flash_kind);
    if(ns>1 && !flashes.empty()) {
        if(p==flashes.front()-coord_def(ns/2,ns/2)){span_x=span_y=ns;return flash_kind;}
        if(p==flashes.front())return effect::none;
    }
    if(choco_large''')
edit('holo-visual.cc','const auto choco=choco_mark(p);if(choco!=effect::none)return choco;','const auto choco=choco_mark(p);if(choco!=effect::none)return choco;\n    const auto ns=night_status(p);if(ns!=effect::none)return ns;')
edit('holo-visual.cc','void invocation(const std::string &g,int tier,const coord_def &p) {','void invocation(const std::string &g,int tier,const coord_def &p,int option) {')
edit('holo-visual.cc','g=="ayame" || g=="choco") { prepare_invocation(g,tier,p);','g=="ayame" || g=="choco" || night_effect(g,tier,option)!=effect::none) { prepare_invocation(g,tier,p,false,option);')
edit('holo-visual.cc','int tier,bool impact_phase) {','int tier,bool impact_phase,int option) {')
edit('holo-visual.cc','prepare_invocation(god,tier,pos,impact_phase);flash_frame=frame;','prepare_invocation(god,tier,pos,impact_phase,option);flash_frame=frame;')
edit('holo-visual.cc','void impact(const coord_def &p,int radius,bool fire){flash(fire?effect::fire:effect::impact,p,radius);}','''void impact(const coord_def &p,int radius,bool fire){
    const auto g=holo_worship::current();
    if(holo_campaign::active() && (g=="pekora" || g=="sopia")) {
        flashes.assign(1,p);flash_kind=night_effect(g,g=="pekora"?3:5);
        if(crawl_state.test) {
            if(const char *dir=getenv("HOLOCRAWL_NIGHT_REVIEW")) {
                static int seq=0;const int n=++seq;const auto before=fox_signature();
                for(int f=0;f<2;++f){flash_frame=f;capture(std::string(dir)+"/"+g+"-impact-"+std::to_string(n)+"-frame"+std::to_string(f)+".png");}
                if(before!=fox_signature())throw std::runtime_error("Impact capture changed gameplay");
            }
            clear();return;
        }
        animate_prepared();return;
    }
    flash(fire?effect::fire:effect::impact,p,radius);
}''')
# Do not imply an explosion when a delayed fuse is merely configured.
edit('holo-visual.cc','const auto style=night_effect(g,tier,option);','const auto style=(g=="pekora" && (tier==3 || tier==5))?night_effect(g,1):night_effect(g,tier,option);')
# Single visual-only gift hook; combat fields and gift RNG remain unchanged.
edit('holo-campaign.cc','mprf(MSGCH_GOD,"Noel sends equipment from the knightly order.");','holo_visual::invocation("noel",3,drop);\n    mprf(MSGCH_GOD,"Noel sends equipment from the knightly order.");')
edit('holo-campaign.cc','holo_visual::invocation(g,tier,aim?*aim:target?target->pos():you.pos());','holo_visual::invocation(g,tier,aim?*aim:target?target->pos():you.pos(),option);')
edit('tilereg-dgn.cc','(cue>=holo_visual::effect::chocoheart1 && cue<=holo_visual::effect::chocoheart5)\n                    || cue==holo_visual::effect::chocowings','''(cue>=holo_visual::effect::night_korone1 && cue<=holo_visual::effect::night_mela5
                        && (int(cue)-int(holo_visual::effect::night_korone1))%3!=0)
                    || (cue>=holo_visual::effect::night_polkaheal && cue<=holo_visual::effect::night_radencraft)
                    || cue==holo_visual::effect::chocowings''')
edit('holo-campaign-test.cc','stem+"-frame"+std::to_string(f)+".png",tier);','stem+"-frame"+std::to_string(f)+".png",tier,false,option);')
edit('holo-campaign-test.cc','#include "monster.h"','#include "monster.h"\n#include "mgen-data.h"\n#include "mon-place.h"')
# Actual upper-cell monster control for Choco's requested corner placement.
edit('holo-campaign-test.cc','grow(target,5,true);\n        you.hp','''grow(target,5,true);
        {const auto upper=target->pos()+coord_def(0,-1);auto mg=mgen_data::hostile_at(MONS_ORC,false,upper);mg.flags|=MG_FORCE_PLACE;
        auto *above=create_monster(mg,false);require(above && above->pos()==upper,"upper monster control failed");above->speed=0;above->hit_points=above->max_hit_points=10000;
        const auto before=signature();holo_visual::capture(std::string(shots)+"/choco-corner-upper.png");
        const int stacks=holo_batch::s.resource;holo_batch::s.resource=0;holo_visual::capture(std::string(shots)+"/choco-corner-upper-no-marker.png");holo_batch::s.resource=stacks;
        require(before==signature(),"corner control changed gameplay");}
        you.hp''')
passives='''    if(const char *shots=getenv("HOLOCRAWL_NIGHT_REVIEW")) {
        for(const std::string g:{"korone","okayu","watame","towa","hajime","su","mela"}) {
            auto *m=fixture(g);for(int x=25;x<=45;++x)for(int y=25;y<=45;++y)env.pgrid(coord_def(x,y))|=FPROP_SEEN_OR_NOEXP;you.trapped=false;
            if(g=="okayu") {for(auto &i:you.inv)if(i.defined() && i.base_type==OBJ_FOOD){eat_item(i);break;}}
            else if(g=="watame"){you.hp-=20;step(10);}
            else if(g=="hajime"){process_command(CMD_MOVE_UP);if(you.turn_is_over)step(you.time_taken);}
            else if(g=="korone" || g=="su")for(int n=0;n<12 && (g=="korone"?holo_batch::s.resource==0:holo_batch::s.hazards.empty());++n){bool hit=false;fight_melee(&you,m,&hit);finish_attack();step(std::max(1,you.time_taken));}
            const auto before=signature();holo_visual::capture(std::string(shots)+"/"+g+"-passive1.png");require(before==signature(),"passive capture changed state");
        }
    }
'''
edit('holo-campaign-test.cc','    int cast_count=0,roundtrips=0;',passives+'    int cast_count=0,roundtrips=0;')
edit('holo-campaign-test.cc','require(gifts==1,"native equipment gift missing");','''require(gifts==1,"native equipment gift missing");
    if(const char *shots=getenv("HOLOCRAWL_NIGHT_REVIEW")) {
        const auto before=signature();holo_visual::capture_invocation("noel",you.pos(),1,std::string(shots)+"/noel-supply3.png",3);
        require(before==signature(),"supply capture changed state");
    }''')
# Record real free catalyst toggle as state, rather than inventing a paid cast.
edit('holo-campaign-test.cc','require(invoke(3)==0 && reactions_enabled(),"restore catalyst toggle");cast(g,5','''require(invoke(3)==0 && reactions_enabled(),"restore catalyst toggle");
            if(const char *shots=getenv("HOLOCRAWL_NIGHT_REVIEW"))holo_visual::capture(std::string(shots)+"/koyori-catalyst3.png");
            cast(g,5''')
print('Prepared night-vfx01:16 draft motifs, Choco inside-corner, actual passive/gift controls. Build next.')
