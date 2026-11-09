from pathlib import Path
from PIL import Image
import json,shutil,hashlib
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source';run=root/'analysis/native/choco-vfx01';run.mkdir(exist_ok=False)
files=['holo-visual.cc','holo-visual.h','tilereg-dgn.cc','holo-batch-resources.cc','holo-campaign-test.cc','rltiles/dc-holo-feat.txt']
for f in files:
    p=run/'before'/f;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/f,p)
shutil.copy2(root/'runtime/tiles01/HoloCrawl.exe',run/'before/HoloCrawl.exe')
hashes={p.relative_to(src).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (src/'rltiles/holo').glob('*.png')}
for p in src.glob('holo-batch*.cc'):
    if p.name!='holo-batch-resources.cc':hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'preserved-files.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
assets=root/'assets/holocrawl/choco-vfx01'
def fit(name,n):
    im=Image.open(assets/'originals'/f'{name}.png').convert('RGBA');assert im.getextrema()[3][0]==0
    im=im.crop(im.getbbox());im.thumbnail((n,n),Image.Resampling.NEAREST);return im
def tile(im,size,cx,cy):
    out=Image.new('RGBA',(size,size));out.alpha_composite(im,(cx-im.width//2,cy-im.height//2));return out
names=[]
def save(name,ims):
    names.append(name)
    for f,im in enumerate(ims):im.save(src/'rltiles/holo'/f'fx_{name}_{f}.png')
for n in range(1,6):save(f'chocoheart{n}',[tile(fit('heart',12+4*n-f*2),96,48,15) for f in range(2)])
save('chocokiss',[tile(fit('kiss',30-f*2),32,16,16) for f in range(2)])
save('chocowings',[tile(fit('wings',88-f*4),96,48,48) for f in range(2)])
save('chocobond',[tile(fit('wings',42-f*2),96,48,14) for f in range(2)])
dirs=[(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]
for d,(dx,dy) in enumerate(dirs):save(f'chocoabsorb{d}',[tile(fit('heart',10),96,48+dx*(16+16*f),48+dy*(16+16*f)) for f in range(2)])
def edit(f,a,b):
    p=src/f;s=p.read_text(encoding='utf-8');assert a in s,(f,a);p.write_text(s.replace(a,b),encoding='utf-8')
edit('holo-visual.h','ayameduel,carrot','ayameduel,'+','.join(names)+',carrot')
edit('holo-visual.h','void fox_gather(', 'void choco_kiss(const coord_def &target,int damage,int healed);\nvoid fox_gather(')
edit('rltiles/dc-holo-feat.txt','carrot HOLO_CARROT',''.join(f'fx_{n}_{f} HOLO_FX_{n.upper()}_{f}\n' for n in names for f in range(2))+'carrot HOLO_CARROT')
edit('holo-visual.cc','bool area(const coord_def &p,','''effect choco_mark(const coord_def &p) {
    if(!holo_campaign::active() || holo_worship::current()!="choco")return effect::none;
    const auto &s=holo_batch::s;const auto *mon=monster_by_mid(s.marked);
    if(!mon || !mon->alive() || mon->pos()!=p || !you.can_see(*mon))return effect::none;
    if(s.secondary<0 && s.five_end>you.elapsed_time && mon->attitude==ATT_FRIENDLY
        && mon->props.exists("holo_charmed"))return effect::chocobond;
    if(s.secondary>=0 && s.one_end>you.elapsed_time && s.resource>0)
        return effect(int(effect::chocoheart1)+std::min(5,s.resource)-1);
    return effect::none;
}
bool choco_large(effect e) {
    return (e>=effect::chocoheart1 && e<=effect::chocoheart5) || e==effect::chocowings
        || e==effect::chocobond || (e>=effect::chocoabsorb0 && e<=effect::chocoabsorb7);
}
bool area(const coord_def &p,''')
edit('holo-visual.cc','flashes.clear();flash_kind=invocation_effect(g);','''flashes.clear();flash_kind=invocation_effect(g);
    if(g=="choco") {
        flash_kind=tier==3?effect::chocokiss:tier==5?effect::chocowings:effect::chocoheart1;
        flashes.push_back(p);return;
    }''')
edit('holo-visual.cc','if(flash_kind!=effect::none && std::find(flashes.begin(),flashes.end(),p)!=flashes.end())return flash_kind;','''if(flash_kind!=effect::none && std::find(flashes.begin(),flashes.end(),p)!=flashes.end())return flash_kind;
    const auto choco=choco_mark(p);if(choco!=effect::none)return choco;''')
edit('holo-visual.cc','span_x=span_y=1;\n    if((flash_kind','''span_x=span_y=1;
    if(choco_large(flash_kind) && !flashes.empty()) {
        if(p==flashes.front()-coord_def(1,1)){span_x=span_y=3;return flash_kind;}
        if(p==flashes.front())return effect::none;
    }
    const auto mark=choco_mark(p+coord_def(1,1));
    if(mark!=effect::none && !(flash_kind!=effect::none && !flashes.empty()
        && flashes.front()==p+coord_def(1,1))) {span_x=span_y=3;return mark;}
    if(choco_mark(p)!=effect::none && flash_kind==effect::none)return effect::none;
    if((flash_kind''')
edit('holo-visual.cc','if(g=="fubuki" && (tier==3 || tier==5))return;','if((g=="fubuki" && (tier==3 || tier==5)) || (g=="choco" && tier==3))return;')
edit('holo-visual.cc','g=="aki" || g=="ayame") { prepare_invocation','g=="aki" || g=="ayame" || g=="choco") { prepare_invocation')
edit('holo-visual.cc','void fox_gather(const std::vector<coord_def> &positions) {','''void choco_kiss(const coord_def &target,int damage,int healed) {
    if(holo_benchmark_active())return;
    const char *dir=crawl_state.test?getenv("HOLOCRAWL_CHOCO_REVIEW"):nullptr;
    if(crawl_state.test && (!dir || !*dir))return;
    const auto before=crawl_state.test?fox_signature():std::string();
    static int sequence=0;const int seq=dir?++sequence:0;
    const int dx=(you.pos().x>target.x)-(you.pos().x<target.x),dy=(you.pos().y>target.y)-(you.pos().y<target.y);
    const int direction=dx>0?(dy>0?1:dy<0?7:0):dx<0?(dy>0?3:dy<0?5:4):dy>0?2:6;
    const int frames=healed>0?4:2;
    for(int f=0;f<frames;++f) {
        flashes.assign(1,target);flash_frame=f%2;
        flash_kind=f<2?effect::chocokiss:effect(int(effect::chocoabsorb0)+direction);
#ifdef USE_TILE_LOCAL
        const auto saved_rng=rng::generators_to_vector();redraw_fox_actors();rng::load_generators(saved_rng);
#endif
        if(dir) {
            const auto stem=std::string(dir)+"/choco-kiss-"+std::to_string(seq)+"-frame"+std::to_string(f);
            capture(stem+".png",false);
            std::ofstream meta(stem+".json");meta<<"{\\"frame\\":"<<f<<",\\"damage\\":"<<damage<<",\\"healed\\":"<<healed<<",\\"absorption\\":"<<(f>=2?"true":"false")<<"}\\n";
        }
#ifdef USE_TILE_LOCAL
        else scaled_delay(110);
#endif
    }
    clear();
    if(crawl_state.test && before!=fox_signature())throw std::runtime_error("Choco kiss changed gameplay/RNG");
#ifdef USE_TILE_LOCAL
    if(!crawl_state.test){const auto saved_rng=rng::generators_to_vector();redraw_fox_actors();rng::load_generators(saved_rng);}
#endif
}
void fox_gather(const std::vector<coord_def> &positions) {''')
# Only read-only records and visual callback added at actual damage/heal site.
edit('holo-batch-resources.cc','s.resource=0;const int dealt=hurt(*target,raw,BEAM_MAGIC,false,true);','const coord_def kiss_pos=target->pos();const int hp_before_kiss=you.hp;\n                s.resource=0;const int dealt=hurt(*target,raw,BEAM_MAGIC,false,true);')
edit('holo-batch-resources.cc','if(credit && !nonliving) heal(dealt*(ecstatic?60:40)/(undead?200:100));\n                s.three_ready=now+40;return 10;','if(credit && !nonliving) heal(dealt*(ecstatic?60:40)/(undead?200:100));\n                s.three_ready=now+40;holo_visual::choco_kiss(kiss_pos,dealt,you.hp-hp_before_kiss);return 10;')
# Keep marker/bat ornaments underneath any other actor that occupies their space.
edit('tilereg-dgn.cc','cue==holo_visual::effect::ayameduel ||', '''(cue>=holo_visual::effect::chocoheart1 && cue<=holo_visual::effect::chocoheart5)
                    || cue==holo_visual::effect::chocowings || cue==holo_visual::effect::chocobond
                    || cue==holo_visual::effect::ayameduel ||''')
fixture='''    if(const char *shots=getenv("HOLOCRAWL_CHOCO_REVIEW")) {
        auto setup=[&]() {
            auto *m=fixture("choco");for(int x=25;x<=45;++x)for(int y=25;y<=45;++y)env.pgrid(coord_def(x,y))|=FPROP_SEEN_OR_NOEXP;
            you.trapped=false;m->move_to_pos(you.pos()+coord_def(1,0));return m;
        };
        auto grow=[&](monster *m,int stacks,bool record) {
            const coord_def aim=m->pos();require(invoke(1,m,&aim,0,3)>0,"initial temptation rejected");step(10);
            int prior=0;
            for(int n=0;n<100 && holo_batch::s.resource<stacks;++n) {
                if(record && prior!=holo_batch::s.resource){prior=holo_batch::s.resource;holo_visual::capture(std::string(shots)+"/choco-stack"+std::to_string(prior)+".png");}
                bool hit=false;fight_melee(&you,m,&hit);finish_attack();step(std::max(1,you.time_taken));
            }
            require(holo_batch::s.resource==stacks,"real attacks failed to build temptation");
            if(record)holo_visual::capture(std::string(shots)+"/choco-stack"+std::to_string(stacks)+".png");
        };
        auto *target=setup();holo_visual::capture(std::string(shots)+"/choco-before.png");grow(target,5,true);
        you.hp=you.hp_max-40;const int beforeHp=you.hp,beforeEnemy=target->hit_points;
        cast("choco",3,target,target->pos());require(target->hit_points<beforeEnemy && you.hp>beforeHp,"kiss damage/heal missing");
        const auto stable=signature();holo_visual::capture(std::string(shots)+"/choco-kiss-after.png");require(stable==signature(),"kiss after capture mutated state");
        // Full HP is a real zero-heal control: no returning healing particles.
        target=setup();grow(target,3,false);you.hp=you.hp_max;cast("choco",3,target,target->pos());
        bool success=false,failure=false;int successSeed=0,failureSeed=0;
        for(int trial=1;trial<=128 && !(success && failure);++trial) {
            target=setup();grow(target,3,false);rng::seed(19000+trial);const auto p=target->pos();
            cast("choco",5,target,p);const bool charmed=holo_batch::s.secondary<0;
            if(charmed && !success) {
                success=true;successSeed=19000+trial;require(target->attitude==ATT_FRIENDLY,"charmed actor not friendly");
                require(holo_visual::invocation_at(target->pos())==holo_visual::effect::chocobond,"success marker missing");
                for(int f=0;f<2;++f)holo_visual::capture_invocation("choco",p,f,std::string(shots)+"/choco-success-frame"+std::to_string(f)+".png",5);
                holo_visual::capture(std::string(shots)+"/choco-success-active.png");
                step(std::max(1,holo_batch::s.five_end-you.elapsed_time+1));
                require(holo_batch::s.secondary>=0 && holo_visual::invocation_at(target->pos())!=holo_visual::effect::chocobond,"charm expiry marker retained");
                holo_visual::capture(std::string(shots)+"/choco-success-expired.png");
            } else if(!charmed && !failure) {
                failure=true;failureSeed=19000+trial;require(target->attitude==ATT_HOSTILE,"failed charm actor changed attitude");
                require(holo_visual::invocation_at(target->pos())!=holo_visual::effect::chocobond,"false success marker");
                holo_visual::capture(std::string(shots)+"/choco-failed-state.png");
            }
        }
        require(success && failure,"seeded charm success/failure controls incomplete");
        target=setup();const auto p=target->pos();require(invoke(1,target,&p,0,3)>0,"immune mark setup");
        target->type=MONS_STONE_GOLEM;holo_batch::s.resource=3;
        require(holo_batch::mental_immune(*target),"immune control not mentally immune");cast("choco",5,target,p);
        require(target->attitude==ATT_HOSTILE && holo_batch::s.secondary>=0 && holo_visual::invocation_at(p)!=holo_visual::effect::chocobond,"immune control falsely charmed");
        holo_visual::capture(std::string(shots)+"/choco-immune-state.png");
        std::ofstream proof(dir+"/choco-review.json");proof<<"{\\"status\\":\\"passed\\",\\"realAttackStacks\\":5,\\"kissHealed\\":true,\\"fullHpControl\\":true,\\"successSeed\\":"<<successSeed<<",\\"failureSeed\\":"<<failureSeed<<",\\"charmExpiry\\":true,\\"mentalImmunityControl\\":true}\\n";
        close_save();return 0;
    }
'''
edit('holo-campaign-test.cc','    if(const char *shots=getenv("HOLOCRAWL_AYAME_REVIEW")) {',fixture+'    if(const char *shots=getenv("HOLOCRAWL_AYAME_REVIEW")) {')
cap=(root/'scripts/capture-ayame-vfx.ps1').read_text(encoding='utf-8').replace('ayame-vfx01','choco-vfx01').replace('AYAME_REVIEW','CHOCO_REVIEW').replace('ayame-review.json','choco-review.json').replace('Ayame','Choco')
cap=cap.replace("'HOLOCRAWL_FUBUKI_REVIEW')","'HOLOCRAWL_FUBUKI_REVIEW','HOLOCRAWL_AYAME_REVIEW')")
(root/'scripts/capture-choco-vfx.ps1').write_text(cap,encoding='utf-8')
print('Choco source/art prepared. Runtime not installed until native tests and visual review pass.')
