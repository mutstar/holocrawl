#include "AppHdr.h"
#include "holo-visual.h"
#include "holo-wrath.h"
#include "holo-campaign.h"
#include "holo-worship.h"
#include "holo-batch-internal.h"
#include "holo-sopia.h"
#include "holocrawl.h"
#include <algorithm>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include "act-iter.h"
#include "beam.h"
#include "command-type.h"
#include "dungeon.h"
#include "env.h"
#include "files.h"
#include "fight.h"
#include "food.h"
#include "item-prop.h"
#include "macro.h"
#include "mon-death.h"
#include "mon-util.h"
#include "monster.h"
#include "mgen-data.h"
#include "mon-place.h"
#include "options.h"
#include "player.h"
#include "random.h"
#include "state.h"
#include "skills.h"
#include "spl-other.h"
#include "tags.h"

extern void process_command(command_type cmd);
namespace holo_campaign {
namespace {
void require(bool ok,const std::string &text){if(!ok){if(const char *d=getenv("HOLOCRAWL_CAMPAIGN_OUTPUT"))std::ofstream(std::string(d)+"/failure.txt")<<text;throw std::runtime_error("Campaign abilities: "+text);}}
monster *fixture(const std::string &god,int piety=180) {
    holo_reset_validation_fixture();
    // The battle fixture bypasses native floor entry; ordinary movement
    // expects the visit ledger that normal floor loading establishes.
    you.global_info.num_visits=you.global_info.levels_seen=1;
    you.get_place_info().num_visits=you.get_place_info().levels_seen=1;
    calc_hp();you.hp=you.hp_max;you.max_magic_points=you.magic_points=100;
    grd(you.pos())=DNGN_ALTAR_OKAWARU;
    require(holo_worship::join(god,false),"join "+god);
    grd(you.pos())=DNGN_FLOOR;you.piety=piety;
    advance();require(can_enable_skill(SK_INVOCATIONS),"ordinary Invocations training unavailable");monster *target=nullptr;
    for(monster_iterator mi;mi;++mi){mi->speed=0;mi->speed_increment=0;mi->hit_points=mi->max_hit_points=10000;target=*mi;}
    require(target,"native enemy fixture");return target;
}
void step(int aut){while(aut>0){const int n=std::min(aut,10);holo_validation_spend_time(n);aut-=n;}}
std::string signature();
int cast(const std::string &god,int tier,monster *m,const coord_def &aim,int option=0){
    const int n=invoke(tier,m,&aim,option,3);
    require(n>0,god+" tier "+std::to_string(tier)+" option "+std::to_string(option));
    if(const char *dir=getenv("HOLOCRAWL_INVOCATION_CAPTURE")) {
        static int sequence=0;
        const std::string stem=std::string(dir)+"/"+god+"-tier"+std::to_string(tier)+"-option"+std::to_string(option)+"-"+std::to_string(++sequence);
        const auto before=signature();
        for(int f=0;f<2;++f)holo_visual::capture_invocation(god,aim,f,stem+"-frame"+std::to_string(f)+".png",tier,false,option);
        holo_visual::capture(stem+"-state.png");
        if(before!=signature()) {
            std::ofstream(stem+"-before.txt")<<before;
            std::ofstream(stem+"-after.txt")<<signature();
            require(false,"invocation capture changed RNG/gameplay: "+god);
        }
    }
    step(n);return n;
}
void close_save(){if(you.save){you.save->abort();delete you.save;you.save=nullptr;}}
std::vector<unsigned char> rng_bytes() {
    std::vector<unsigned char> bytes;
    writer out(&bytes);
    rng::generators_to_vector().write(out);
    return bytes;
}
void roundtrip() {
    std::vector<unsigned char> bytes;{writer out(&bytes);tag_write(TAG_CHR,out);tag_write(TAG_YOU,out);}
    const auto batch=holo_batch::save_campaign(),sopia=holo_sopia::save_campaign();
    const auto wrath=holo_wrath::status();
    const auto rng_state=rng_bytes();const int hp=you.hp,mp=you.magic_points,piety=you.piety,now=you.elapsed_time;
    const auto god=holo_worship::current();close_save();you=player();
    reader in(bytes,TAG_MINOR_VERSION);int size=unmarshallInt(in);require(size>0 && size<100000,"character size");
    std::vector<unsigned char> header(size);in.read(header.data(),header.size());reader chr(header,TAG_MINOR_VERSION);
    auto format=unmarshallUByte(chr);tag_read_char(chr,format,TAG_MAJOR_VERSION,TAG_MINOR_VERSION);tag_read(in,TAG_YOU);
    // hp_max is derived by native startup after TAG_YOU, not stored in it.
    calc_hp();
    require(!in.valid(),"trailing player data");
    require(holo_worship::current()==god && hp==you.hp && mp==you.magic_points && piety==you.piety && now==you.elapsed_time,"player state roundtrip");
    require(batch==holo_batch::save_campaign() && sopia==holo_sopia::save_campaign(),"all combat fields roundtrip for "+god);
    require(rng_state==rng_bytes(),"RNG roundtrip for "+god);
    require(wrath==holo_wrath::status(),"wrath roundtrip for "+god);
}
std::string signature() {
    std::ostringstream o;o<<holo_worship::current()<<' '<<you.hp<<' '<<you.magic_points<<' '<<int(you.piety)<<' '<<you.elapsed_time<<' ';
    o<<holo_batch::save_campaign()<<'|'<<holo_sopia::save_campaign()<<'|'<<holo_wrath::status()<<'|';for(auto n:rng_bytes())o<<int(n)<<' ';
    std::vector<std::pair<mid_t,std::string>> actors;
    for(monster_iterator mi;mi;++mi){std::ostringstream m;m<<mi->pos().x<<' '<<mi->pos().y<<' '<<mi->hit_points<<' '<<mi->max_hit_points<<' '<<mi->speed_increment<<' '<<mi->attitude<<' '<<mi->behaviour<<' '<<mi->foe;actors.emplace_back(mi->mid,m.str());}
    std::sort(actors.begin(),actors.end());for(auto &m:actors)o<<'|'<<m.first<<' '<<m.second;return o.str();
}
void save_disk(const std::string &dir) {
    close_save();Options.no_save=false;Options.save_dir=dir;you.your_name="HoloAbilities01";
    you.save=new package(get_savedir_filename(you.your_name).c_str(),true,true);
    save_game(false);
    {writer out(you.save,level_id::current().describe());marshallUByte(out,TAG_MAJOR_VERSION);marshallUByte(out,TAG_MINOR_VERSION);tag_write(TAG_LEVEL,out);}
    you.save->commit();delete you.save;you.save=nullptr;
}
void reload_disk(const std::string &dir) {
    close_save();you=player();Options.no_save=false;Options.save_dir=dir;crawl_state.bypassed_startup_menu=true;
    require(restore_game(get_save_filename("HoloAbilities01")),"public restore of active abilities");
    calc_hp();
    const auto name=level_id::current().describe();
    dgn_reset_level(false);
    reader in(you.save,name,TAG_MINOR_VERSION);require(unmarshallUByte(in)==TAG_MAJOR_VERSION,"level major version");require(unmarshallUByte(in)==TAG_MINOR_VERSION,"level minor version");tag_read(in,TAG_LEVEL);
}
}
bool test_requested(){const char *v=getenv("HOLOCRAWL_CAMPAIGN_TEST");return crawl_state.test && v && std::string(v)=="1";}
int run_tests() {
    const char *path=getenv("HOLOCRAWL_CAMPAIGN_OUTPUT");require(path,"output directory required");const std::string dir(path);
    crawl_state.show_more_prompt=false;
    const char *mode=getenv("HOLOCRAWL_CAMPAIGN_RELOAD");
    if(mode && std::string(mode)=="1") {
        holo_reset_validation_fixture();reload_disk(dir);
        require(holo_worship::current()=="lui" && holo_batch::s.companions.size()==6,"native companions restored");
        for(auto c:holo_batch::s.companions){const auto *m=monster_by_mid(c.mid);require(m && m->alive(),"companion MID resolved after fresh-process load");}
        step(10);std::ifstream expected(dir+"/expected-step.txt");std::string data((std::istreambuf_iterator<char>(expected)),{});
        require(data==signature(),"fresh-process native world continuation differs");
        std::ofstream proof(dir+"/reload.json");proof<<"{\"status\":\"passed\",\"nativeLevel\":true,\"companions\":6,\"nextWorldStepExact\":true}\n";
        close_save();return 0;
    }
    // Noel: Heroism's duration roll +5 turns, fixed +6 to mundane combat.
    {
        for(int trial=0;trial<12;++trial) {
            fixture("noel");const int I=you.skill(SK_INVOCATIONS,1),now=you.elapsed_time,hp=you.hp_max;
            rng::seed(8800+trial);const int expected=10*min(110,15+random2avg(I*6,2));rng::seed(8800+trial);
            require(invoke(1)==10,"Noel knight cast time");
            const int until=you.props["holocrawl_campaign"]["noel_skill_end"].get_int();
            require(until-now==expected,"Noel Heroism plus5 duration");
            for(int sk=int(SK_FIRST_WEAPON);sk<=int(SK_LAST_MUNDANE);++sk)
                require(noel_skill_bonus(skill_type(sk),1)==6,"Noel all mundane skills +6");
            require(noel_fighting_bonus(1)==6 && noel_skill_bonus(SK_SPELLCASTING,1)==0 && you.hp_max==hp,"Noel Fighting/magic/HP controls");
            require(you.magic_points==98 && you.piety==178,"Noel costs unchanged");
            if(trial==0){roundtrip();require(you.props["holocrawl_campaign"]["noel_skill_end"].get_int()==until && noel_skill_bonus(SK_DODGING,1)==6,"Noel active buff save");}
            you.elapsed_time=until;require(noel_fighting_bonus(1)==0 && noel_skill_bonus(SK_DODGING,1)==0,"Noel buff expires");
        }
        std::ofstream(dir+"/noel-balance.json")<<"{\"status\":\"passed\",\"mundaneBonus\":6,\"heroismDurationExtraTurns\":5,\"maxDurationTurns\":110,\"costsUnchanged\":true,\"noMaxHPBonus\":true,\"activeSave\":true,\"expiry\":true}\n";
    }
    try {
    // Pekora quick planting, paid detonation, delayed save and chain propagation.
    {
        using namespace holo_batch;
        auto butterfly=[&](const coord_def &p) -> monster * {
            for(monster_iterator mi;mi;++mi)monster_die(**mi,KILL_DISMISSED,NON_MONSTER,true);
            auto mg=mgen_data::hostile_at(MONS_BUTTERFLY,false,p);mg.flags|=MG_FORCE_PLACE;
            auto *m=create_monster(mg,false);require(m,"Pekora butterfly fixture");
            m->speed=0;m->speed_increment=0;m->hit_points=m->max_hit_points=10000;return m;
        };
        auto plant=[&](const coord_def &p) {
            require(invoke(1,nullptr,&p,0,3)==5,"Pekora planting must cost5aut");
        };
        for(int option=0;option<2;++option) {
            fixture("pekora");const coord_def p=you.pos()+coord_def(3,0);monster *m=butterfly(p+coord_def(1,0));
            require(m->armour_class()==0,"Pekora damage fixture AC");
            plant(p);step(20);
            const int mp=you.magic_points,faith=you.piety;
            require(invoke(3,nullptr,&p,option,3)==5,"Pekora fuse action5aut");
            require(you.magic_points==mp-2 && you.piety==faith-2,"Pekora detonation costs once");
            if(option) {
                require(s.hazards[0].extra==150,"Pekora delayed bonus stored");
                roundtrip();require(s.hazards[0].extra==150,"Pekora delayed bonus roundtrip");
                m=monster_at(p+coord_def(1,0));require(m,"Pekora target after save");
                const int before=m->hit_points;step(20);require(m->hit_points==before,"Pekora premature delayed explosion");
                rng::seed(7711);const int raw=roll_dice(2,8+s.inv/3)*150/100;rng::seed(7711);
                you.elapsed_time+=5;space_tick(you.elapsed_time);require(before-m->hit_points==raw,"Pekora delayed +50 percent native damage: "+std::to_string(before-m->hit_points)+" expected "+std::to_string(raw));
            }
        }
        // Place the triggered bomb last in the vector: the earlier neighbour
        // must receive the same boost before either explosion is evaluated.
        for(int option=0;option<2;++option) {
            fixture("pekora");
            const coord_def root=you.pos()+coord_def(3,0),near=root+coord_def(1,0);
            monster *m=butterfly(near+coord_def(1,0));
            hazard a;a.kind=10;a.pos=near;a.arm=you.elapsed_time;a.end=you.elapsed_time+200;a.next=a.end+1;s.hazards.push_back(a);
            a.pos=root;s.hazards.push_back(a);
            if(option) {
                require(invoke(3,nullptr,&root,1,3)==5,"Pekora delayed chain setup");roundtrip();step(20);m=monster_at(near+coord_def(1,0));
            }
            const int before=m->hit_points;const int mult=option?150:130;
            rng::seed(7722);const int raw=roll_dice(2,8+s.inv/3)*mult/100;rng::seed(7722);
            if(option){you.elapsed_time+=5;space_tick(you.elapsed_time);}else require(invoke(3,nullptr,&root,0,3)==5,"Pekora immediate chain");
            require(before-m->hit_points==raw,"Pekora chain bonus no stacking/vector dependence: "+std::to_string(before-m->hit_points)+" expected "+std::to_string(raw));
            require(s.hazards[0].end==0 && s.hazards[1].end==0,"Pekora chain consumed each once");
        }
        std::ofstream(dir+"/pekora-balance.json")<<"{\"status\":\"passed\",\"plantAut\":5,\"immediatePercent\":130,\"delayedPercent\":150,\"chainOrderIndependent\":true,\"noStacking\":true,\"delayedSaveRoundtrip\":true}\n";
    }
    } catch(const std::exception &e){std::ofstream(dir+"/pekora-error.txt")<<e.what();throw;}
    // Okayu 3* standalone payoff. Use real invocation, native sleep, native
    // monster HP, ordinary melee/bolt entry points and existing save roundtrip.
    {
        auto sleeping=[&]() -> monster * {
            for(int trial=1;trial<=64;++trial) {
                auto *m=fixture("okayu",75);holo_batch::s.resource=50;
                rng::seed(41000+trial);
                require(invoke(3,m,&m->pos())==10,"Okayu nap unavailable before5*");
                step(70);
                if(m->asleep()) {require(you.piety==73 && holo_batch::s.targets[m->mid].kind==2,"sleep ready/cost mismatch");return m;}
            }
            require(false,"could not obtain actual nap success");return nullptr;
        };
        auto ordinary=[&](monster *m,holo_batch::attack_kind kind,int amount) {
            holo_batch::begin_attack(*m,kind);const int hp=m->hit_points;
            m->hurt(&you,amount,BEAM_MAGIC,KILLED_BY_BEAM);
            holo_batch::cancel_attack();return hp-m->hit_points;
        };
        auto *m=sleeping();const auto mid=m->mid;
        roundtrip();require(holo_batch::s.targets[mid].kind==2,"unspent sleep bonus not saved");
        require(ordinary(m,holo_batch::attack_kind::melee,20)==26,"3* standalone waking damage");
        require(!m->asleep() && holo_batch::s.targets[mid].kind==3,"hit did not consume/wake");
        require(ordinary(m,holo_batch::attack_kind::melee,20)==20,"repeated hit got second bonus");
        roundtrip();require(holo_batch::s.targets[mid].kind==3,"spent sleep bonus not saved");
        m=sleeping();require(ordinary(m,holo_batch::attack_kind::melee,1000)==1012,"stab-scale cap missing");
        m=sleeping();you.duration[DUR_QUAD_DAMAGE]=10;
        require(ordinary(m,holo_batch::attack_kind::melee,20)==92,"native multiplier bypasses waking cap");you.duration[DUR_QUAD_DAMAGE]=0;
        m=sleeping();m->type=MONS_DEEP_DWARF;
        require(ordinary(m,holo_batch::attack_kind::melee,1)==0 && holo_batch::s.targets[m->mid].kind==2,"fully absorbed hit consumed waking bonus");
        m=sleeping();require(ordinary(m,holo_batch::attack_kind::ranged,20)==26,"ranged waking hit missing");
        m=sleeping();require(ordinary(m,holo_batch::attack_kind::spell,20)==26,"targeted spell waking hit missing");
        m=sleeping();{
            holo_batch::waking_spell_scope spell(true);m->behaviour=BEH_SEEK;
            const int hp=m->hit_points;m->hurt(&you,20,BEAM_MAGIC,KILLED_BY_BEAM);
            require(hp-m->hit_points==26,"untargeted spell / early wake snapshot missing");
        }
        m=sleeping();holo_batch::begin_attack(*m);m->hurt(&you,0,BEAM_MAGIC,KILLED_BY_BEAM);
        require(holo_batch::s.targets[m->mid].kind==2,"zero damage consumed bonus");holo_batch::cancel_attack();
        m=sleeping();holo_batch::begin_attack(*m);m->hurt(m,20,BEAM_MAGIC,KILLED_BY_BEAM);
        require(holo_batch::s.targets[m->mid].kind==2,"non-player damage consumed bonus");holo_batch::cancel_attack();
        m=sleeping();holo_batch::begin_attack(*m);const int poison_hp=m->hit_points;m->hurt(&you,20,BEAM_POISON,KILLED_BY_POISON);
        require(poison_hp-m->hit_points==20 && holo_batch::s.targets[m->mid].kind==2,"poison consumed bonus");
        m->hurt(&you,20,BEAM_FIRE,KILLED_BY_CLOUD);require(holo_batch::s.targets[m->mid].kind==2,"cloud consumed bonus");holo_batch::cancel_attack();
        m=sleeping();holo_batch::begin_attack(*m);{damage_scope divine(true);const int hp=m->hit_points;m->hurt(&you,20,BEAM_MAGIC);require(hp-m->hit_points==20,"invocation double bonus");}
        require(holo_batch::s.targets[m->mid].kind==2,"invocation consumed ordinary-hit bonus");holo_batch::cancel_attack();
        m=sleeping();m->behaviour=BEH_SEEK;require(ordinary(m,holo_batch::attack_kind::melee,20)==20,"externally woken target got bonus");
        m=sleeping();step(20);require(ordinary(m,holo_batch::attack_kind::spell,20)==20,"expired sleep got bonus");
        m=fixture("okayu");m->put_to_sleep(&you,0);require(ordinary(m,holo_batch::attack_kind::melee,20)==20,"natural sleep got Okayu bonus");
        m=sleeping();holo_batch::s.targets[m->mid].kind=1;require(ordinary(m,holo_batch::attack_kind::melee,20)==26,"legacy saved nap compatibility");
        m=sleeping();rng::seed(424242);const int melee_hp=m->hit_points;fight_melee(&you,m);
        require(m->hit_points<melee_hp && holo_batch::s.targets[m->mid].kind==3,"native melee did not consume waking hit");
        m=sleeping();rng::seed(424242);{
            if(const char *shots=getenv("HOLOCRAWL_OKAYU_REVIEW"))holo_visual::capture(std::string(shots)+"/okayu-sleep-ready.png");
            command_scope cmd;bolt beam;beam.name="magic dart";beam.origin_spell=SPELL_MAGIC_DART;
            beam.source=you.pos();beam.target=m->pos();beam.range=5;beam.source_id=you.mid;
            beam.thrower=KILL_YOU;beam.flavour=BEAM_MMISSILE;beam.damage=dice_def(1,20);beam.hit=AUTOMATIC_HIT;
            beam.fire();require(holo_batch::s.targets[m->mid].kind==3,"native spell bolt did not consume waking hit");
            if(const char *shots=getenv("HOLOCRAWL_OKAYU_REVIEW"))holo_visual::capture(std::string(shots)+"/okayu-sleep-spell-hit.png");
        }
        int five_damage[2];
        for(int ready=0;ready<2;++ready) {
            m=sleeping();you.piety=180;holo_batch::s.resource=50;
            if(!ready)holo_batch::s.targets[m->mid].kind=3;
            rng::seed(434343);const int hp=m->hit_points;require(invoke(5,m,&m->pos())==10,"dream eater test cast");five_damage[ready]=hp-m->hit_points;
        }
        require(five_damage[0]==five_damage[1] && five_damage[0]>0,"5* sleep bonus double-stacked with3*");
        std::ofstream proof(dir+"/okayu-waking.json");proof<<"{\"status\":\"passed\",\"percent\":30,\"capAtInv12\":12,\"standaloneAtThreeStars\":true,\"nativeMelee\":true,\"nativeSpellBolt\":true,\"untargetedSpellSnapshot\":true,\"oneHitOnly\":true,\"zeroDamageControl\":true,\"petDotCloudControls\":true,\"expiryAndExternalWake\":true,\"naturalSleepExcluded\":true,\"legacyNapSave\":true,\"unspentAndSpentSaveRoundtrip\":true,\"fiveStarNoDoubleStack\":true}\n";
    }
    fixture("noel");holo_wrath::validate();holo_visual::validate();
    // Native TAG_LEVEL serialization must retain both v2 servant stats and AI
    // continuation, including real foxes versus pass-through decoys.
    const auto prior_save_dir=Options.save_dir;const bool prior_no_save=Options.no_save;
    for(const std::string g:{"aki","fubuki","ayame","korone","lui"}) {
        fixture("noel");holo_wrath::depart(g,120);
        you.elapsed_time+=100;holo_wrath::advance();you.elapsed_time+=20;holo_wrath::advance();
        save_disk(dir);step(10);const auto expected=signature();
        reload_disk(dir);step(10);require(signature()==expected,"v2 wrath servant save/AI continuation: "+g);
        int count=0;
        for(monster_iterator mi;mi;++mi)if(mi->props.exists("holo_wrath_god")) {
            require(mi->props["holo_wrath_revision"].get_int()==2,"servant revision was lost");
            int hp,ac,ev,hit,damage;require(holo_wrath::custom_monster(**mi,hp,ac,ev,hit,damage),"restored servant stats missing");
            require(mi->max_hit_points==hp && mi->armour_class()==ac,"restored servant profile changed");++count;
        }
        require(count>0,"restored wrath servants missing: "+g);
        close_save();Options.save_dir=prior_save_dir;Options.no_save=prior_no_save;
    }
    {std::ofstream proof(dir+"/wrath02-save.json");proof<<"{\"status\":\"passed\",\"nativeServantKinds\":5,\"nextWorldStepExact\":true,\"restoredProfiles\":true}\n";}
    if(const char *shots=getenv("HOLOCRAWL_SUISEI_REVIEW")) {
        monster *m=fixture("suisei");const auto origin=you.pos();
        cast("suisei",1,m,m->pos());
        require(holo_visual::invocation_at(m->pos())==holo_visual::effect::starmark,"persistent constellation marker missing");
        cast("suisei",3,m,m->pos());
        m->move_to_pos(origin+coord_def(3,0));
        const int before=m->hit_points;
        cast("suisei",5,nullptr,m->pos());
        require(m->hit_points==before,"comet dealt damage at designation");
        holo_visual::capture(std::string(shots)+"/comet-warning.png");
        step(10);
        require(m->hit_points==before,"comet dealt damage before deadline");
        holo_visual::capture(std::string(shots)+"/comet-urgent.png");
        step(10);
        require(m->hit_points<before,"delayed comet never impacted");
        holo_visual::capture(std::string(shots)+"/comet-aftermath.png");
        std::ofstream proof(dir+"/suisei-review.json");
        proof<<"{\"status\":\"passed\",\"tiers\":[1,3,5],\"persistentMarker\":true,\"damageOnlyAtImpact\":true,\"cutRange\":5,\"beforeImpactHp\":"<<before<<",\"afterImpactHp\":"<<m->hit_points<<"}\n";
        close_save();return 0;
    }
    if(const char *shots=getenv("HOLOCRAWL_MIKO_REVIEW")) {
        auto has=[](const coord_def &p,holo_visual::effect kind) {
            const auto fx=holo_visual::at(p);
            return std::find(fx.begin(),fx.end(),kind)!=fx.end();
        };
        fixture("miko",30);cast("miko",1,nullptr,you.pos());
        require(has(you.pos()+coord_def(1,0),holo_visual::effect::shrine),"low faith shrine missing");
        require(!has(you.pos()+coord_def(2,0),holo_visual::effect::shrine),"low faith shrine too wide");
        fixture("miko");cast("miko",1,nullptr,you.pos());
        cast("miko",3,nullptr,you.pos());
        require(holo_visual::invocation_at(you.pos()+coord_def(2,0))==holo_visual::effect::mikoflame,"boundary flame missing");
        require(holo_visual::invocation_at(you.pos()+coord_def(1,0))!=holo_visual::effect::mikoflame,"interior falsely burning");
        const int fire_end=holo_batch::s.three_end;
        cast("miko",5,nullptr,you.pos());
        require(has(you.pos()+coord_def(3,3),holo_visual::effect::mikodomain),"great shrine edge missing");
        require(holo_visual::invocation_at(you.pos()+coord_def(3,0))==holo_visual::effect::mikoflame,"expanded flame missing");
        const auto before=signature();
        for(int f=0;f<4;++f)holo_visual::capture_invocation("miko",you.pos(),f,std::string(shots)+"/miko-domain-frame"+std::to_string(f)+".png",5);
        require(before==signature(),"domain animation capture changed gameplay");
        step(std::max(0,fire_end-you.elapsed_time));
        require(holo_visual::invocation_at(you.pos()+coord_def(3,0))!=holo_visual::effect::mikoflame,"expired fire still rendered");
        holo_visual::capture(std::string(shots)+"/miko-fire-expired.png");
        step(std::max(0,holo_batch::s.five_end-you.elapsed_time));
        require(!has(you.pos()+coord_def(3,3),holo_visual::effect::mikodomain),"expired domain still rendered");
        holo_visual::capture(std::string(shots)+"/miko-domain-expired.png");
        std::ofstream proof(dir+"/miko-review.json");
        proof<<"{\"status\":\"passed\",\"lowFaithWidth\":3,\"highFaithWidth\":5,\"domainWidth\":7,\"boundaryOnlyFire\":true,\"expandedFire\":true,\"expiredFireGone\":true,\"expiredDomainGone\":true,\"capturePreservesGameplay\":true}\n";
        close_save();return 0;
    }
    if(const char *shots=getenv("HOLOCRAWL_AKI_REVIEW")) {
        auto *target=fixture("aki");const auto origin=you.pos();
        target->move_to_pos(origin+coord_def(3,0));
        cast("aki",1,nullptr,origin+coord_def(1,0));step(10);
        const int beforeShot=target->hit_points;
        holo_batch::manual_second=origin+coord_def(0,-1);
        cast("aki",3,nullptr,origin+coord_def(0,1));step(10);
        require(holo_batch::s.totals.hits>0,"roses never fired native bolt");
        const int afterShot=target->hit_points;
        const int beforeBloom=afterShot;
        cast("aki",5,nullptr,origin+coord_def(1,0));
        require(target->hit_points<beforeBloom,"full bloom dealt no damage");
        const auto state=signature();
        for(int f=0;f<4;++f)holo_visual::capture_invocation("aki",origin+coord_def(1,0),f,std::string(shots)+"/aki-bloom-frame"+std::to_string(f)+".png",5);
        require(state==signature(),"bloom capture changed gameplay");
        holo_visual::capture(std::string(shots)+"/aki-bloom-aftermath.png");
        std::ofstream proof(dir+"/aki-review.json");
        proof<<"{\"status\":\"passed\",\"nativeBoltTraversal\":true,\"bloomWidth\":7,\"capturePreservesGameplay\":true,\"beforeShotHp\":"<<beforeShot<<",\"afterShotHp\":"<<afterShot<<",\"beforeBloomHp\":"<<beforeBloom<<",\"afterBloomHp\":"<<target->hit_points<<"}\n";
        close_save();return 0;
    }
    if(const char *shots=getenv("HOLOCRAWL_CHOCO_REVIEW")) {
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
        {holo_visual::capture(std::string(shots)+"/choco-raised-no-upper.png");
        const int stacks_before_upper=holo_batch::s.resource;holo_batch::s.resource=0;
        holo_visual::capture(std::string(shots)+"/choco-raised-no-upper-no-marker.png");holo_batch::s.resource=stacks_before_upper;
        const auto upper=target->pos()+coord_def(0,-1);auto mg=mgen_data::hostile_at(MONS_ORC,false,upper);mg.flags|=MG_FORCE_PLACE;
        auto *above=create_monster(mg,false);require(above && above->pos()==upper,"upper monster control failed");above->speed=0;above->hit_points=above->max_hit_points=10000;
        const auto before=signature();holo_visual::capture(std::string(shots)+"/choco-corner-upper.png");
        const int stacks=holo_batch::s.resource;holo_batch::s.resource=0;holo_visual::capture(std::string(shots)+"/choco-corner-upper-no-marker.png");holo_batch::s.resource=stacks;
        require(before==signature(),"corner control changed gameplay");}
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
        std::ofstream proof(dir+"/choco-review.json");proof<<"{\"status\":\"passed\",\"realAttackStacks\":5,\"kissHealed\":true,\"fullHpControl\":true,\"successSeed\":"<<successSeed<<",\"failureSeed\":"<<failureSeed<<",\"charmExpiry\":true,\"mentalImmunityControl\":true}\n";
        close_save();return 0;
    }
    if(const char *shots=getenv("HOLOCRAWL_AYAME_REVIEW")) {
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
        you.piety=180;const int before=target->hit_points,mpBefore=you.magic_points,clockBefore=you.elapsed_time;
        cast("ayame",3,target,target->pos());
        require(target->hit_points<=before && you.magic_points==mpBefore-3 && you.elapsed_time>clockBefore
            && holo_batch::s.three_ready>clockBefore,"twin strike action/cost/cooldown invalid");
        const int after=target->hit_points;cast("ayame",5,target,target->pos());
        require(holo_batch::five() && holo_batch::s.centre==origin,"duel did not start");
        int sx=0,sy=0;require(holo_visual::invocation_sprite_at(origin-coord_def(2,2),sx,sy)==holo_visual::effect::ayameduel && sx==5 && sy==5,"duel geometry wrong");
        const auto active=signature();holo_visual::capture(std::string(shots)+"/ayame-duel-active.png");require(active==signature(),"duel capture mutated state");
        you.elapsed_time=holo_batch::s.five_end;
        require(holo_visual::invocation_sprite_at(origin-coord_def(2,2),sx,sy)!=holo_visual::effect::ayameduel,"expired duel retained");
        holo_visual::capture(std::string(shots)+"/ayame-duel-expired.png");
        std::ofstream proof(dir+"/ayame-review.json");
        proof<<"{\"status\":\"passed\",\"ordinaryMeleeAura\":true,\"auraExpiry\":true,\"duelWidth\":5,\"duelExpiry\":true,\"capturePreservesGameplay\":true,\"beforeStrikeHp\":"<<before<<",\"afterStrikeHp\":"<<after<<"}\n";
        close_save();return 0;
    }
    if(const char *shots=getenv("HOLOCRAWL_FUBUKI_REVIEW")) {
        auto *target=fixture("fubuki");const auto origin=you.pos(),dest=origin+coord_def(2,0);
        // This choreography fixture is an already-explored combat room.
        // Ordinary campaign exploration traps remain enabled and unchanged.
        for(int x=25;x<=45;++x)for(int y=25;y<=45;++y)
            env.pgrid(coord_def(x,y))|=FPROP_SEEN_OR_NOEXP;
        you.trapped=false;
        target->move_to_pos(origin+coord_def(0,1));
        cast("fubuki",1,nullptr,dest);
        require(holo_batch::s.companions.size()==1,"initial image missing");
        const auto image=holo_batch::s.companions.front().mid;
        const int beforeHp=target->hit_points;
        holo_visual::capture(std::string(shots)+"/fubuki-swap-before.png");
        cast("fubuki",3,monster_by_mid(image),dest);
        require(you.pos()==dest && monster_by_mid(image)->pos()==origin,"swap endpoints wrong");
        require(target->hit_points<beforeHp,"departure foxfire never damaged enemy");
        const int afterHp=target->hit_points;
        holo_visual::capture(std::string(shots)+"/fubuki-swap-after.png");
        holo_visual::capture(std::string(shots)+"/fubuki-gather-before.png");
        cast("fubuki",5,nullptr,you.pos());
        require(holo_batch::s.companions.size()==4,"gathering did not reach4 foxes");
        for(const auto &c:holo_batch::s.companions) {
            const auto *fox=monster_by_mid(c.mid);require(fox && fox->alive(),"missing real fox");
            require(!holo_visual::mask_fox_at(fox->pos()),"arrival mask leaked past animation");
        }
        holo_visual::capture(std::string(shots)+"/fubuki-gather-after.png");
        std::ofstream proof(dir+"/fubuki-review.json");
        proof<<"{\"status\":\"passed\",\"swapExact\":true,\"departureFireDamage\":true,\"foxCount\":4,\"newFoxes\":3,\"masksCleared\":true,\"beforeFireHp\":"<<beforeHp<<",\"afterFireHp\":"<<afterHp<<"}\n";
        close_save();return 0;
    }
    if(getenv("HOLOCRAWL_VISUAL_CAPTURE")) {
        fixture("miko");cast("miko",1,nullptr,you.pos());
        holo_visual::capture(dir+"/sanctuary.png");
        fixture("sopia");const auto centre=you.pos();cast("sopia",1,nullptr,centre);cast("sopia",5,nullptr,centre+coord_def(3,0));
        holo_visual::capture(dir+"/orbit-gravity.png");
        fixture("pekora");cast("pekora",1,nullptr,you.pos()+coord_def(0,-2));cast("pekora",1,nullptr,you.pos()+coord_def(-2,0));
        holo_wrath::depart("mela",120);you.elapsed_time+=100;holo_wrath::advance();
        holo_visual::capture(dir+"/bombs-warning.png");
        you.elapsed_time+=10;holo_visual::capture(dir+"/bombs-urgent.png");
        fixture("lui");cast("lui",5,nullptr,you.pos());
        holo_visual::capture(dir+"/ravens.png");
        you.elapsed_time+=10;holo_visual::capture(dir+"/ravens-frame-alt.png");
        fixture("aki");cast("aki",1,nullptr,you.pos());step(10);
        holo_batch::manual_second=you.pos()+coord_def(-1,2);cast("aki",3,nullptr,you.pos()+coord_def(0,2));
        holo_visual::capture(dir+"/garden-roses.png");
        fixture("fubuki");cast("fubuki",1,nullptr,you.pos()+coord_def(0,2));
        holo_visual::capture(dir+"/fox-spirits.png");
        for(const auto &g:std::vector<std::string>{"ayame","korone"}) {
            fixture("noel");holo_wrath::depart(g,120);you.elapsed_time+=100;holo_wrath::advance();you.elapsed_time+=20;holo_wrath::advance();step(1);
            holo_visual::capture(dir+(g=="ayame"?"/wrath-swordsman.png":"/wrath-hound.png"));
        }
        auto *water_target=fixture("su");cast("su",3,water_target,water_target->pos());cast("su",5,nullptr,you.pos());
        holo_visual::capture(dir+"/water-field.png");
        auto *fire_target=fixture("mela");cast("mela",3,fire_target,fire_target->pos());cast("mela",5,nullptr,you.pos());
        holo_visual::capture(dir+"/ghostfire.png");
        fixture("noel");cast("noel",5,nullptr,you.pos());holo_visual::capture(dir+"/commander-badges.png");
        fixture("noel");const auto origin=you.pos();const auto gods=holo_worship::gods();
        for(size_t i=0;i<gods.size();++i){const auto p=origin+coord_def(int(i%8)-4,int(i/8)-4);grd(p)=DNGN_ALTAR_OKAWARU;you.moveto(p);holo_visual::bind_altar(gods[i]);}
        you.moveto(origin);step(1);holo_visual::capture(dir+"/god-altars.png");
        std::ofstream proof(dir+"/visual-capture.json");proof<<"{\"status\":\"passed\",\"nativeSDL\":true,\"screenshots\":14}\n";close_save();return 0;
    }
    if(const char *shots=getenv("HOLOCRAWL_NIGHT_REVIEW")) {
        for(const std::string g:{"korone","okayu","watame","towa","hajime","su","mela"}) {
            auto *m=fixture(g);for(int x=25;x<=45;++x)for(int y=25;y<=45;++y)env.pgrid(coord_def(x,y))|=FPROP_SEEN_OR_NOEXP;you.trapped=false;
            if(g=="okayu") {for(auto &i:you.inv)if(i.defined() && i.base_type==OBJ_FOOD){eat_item(i);break;}}
            else if(g=="watame"){you.hp-=20;step(10);}
            else if(g=="hajime"){process_command(CMD_MOVE_UP);if(you.turn_is_over)step(you.time_taken);}
            else if(g=="korone" || g=="su")for(int n=0;n<12 && (g=="korone"?holo_batch::s.resource==0:holo_batch::s.hazards.empty());++n){bool hit=false;fight_melee(&you,m,&hit);finish_attack();step(std::max(1,you.time_taken));}
            const auto before=signature();holo_visual::capture(std::string(shots)+"/"+g+"-passive1.png");require(before==signature(),"passive capture changed state");
        }
    }
    if(getenv("HOLOCRAWL_NIGHT_REVIEW")) {
        // Selective visual diagnostics use explicitly prepared applause/paint.
        // These are not natural resource-income or win-rate measurements.
        for(int option=0;option<3;++option) {
            auto *m=fixture("polka");holo_batch::s.resource=3;you.hp-=25;
            cast("polka",5,m,m->pos(),option);
        }
        for(int option=1;option<=3;++option) {
            auto *m=fixture("polka");
            if(option==3)for(const auto p:{you.pos()+coord_def(2,1),you.pos()+coord_def(-1,1)}){
                auto mg=mgen_data::hostile_at(MONS_ETTIN,false,p);mg.flags|=MG_FORCE_PLACE;auto *extra=create_monster(mg,false);require(extra,"juggling enemies missing");extra->speed=0;extra->hit_points=extra->max_hit_points=10000;
            }
            cast("polka",1,m,m->pos(),option);
        }
        for(int option=0;option<3;++option) {
            auto *m=fixture("raden");if(option)cast("raden",1,nullptr,you.pos(),option);
            if(option==0){holo_batch::s.targets[m->mid].paint=3;holo_batch::s.targets[m->mid].paint_end=you.elapsed_time+100;}
            cast("raden",3,m,m->pos(),option);
        }
        for(int type=1;type<=3;++type){auto *m=fixture("koyori");cast("koyori",1,nullptr,you.pos(),type);cast("koyori",1,m,m->pos(),10+type);cast("koyori",5,nullptr,you.pos(),type+2);}
        fixture("sopia");const auto origin=you.pos();cast("sopia",5,nullptr,origin+coord_def(2,0));step(70);cast("sopia",6,nullptr,origin+coord_def(2,0));
        fixture("pekora");const auto bomb=you.pos()+coord_def(3,0);cast("pekora",1,nullptr,bomb);step(15);cast("pekora",3,nullptr,bomb,1);step(40);
        fixture("pekora");const auto centre=you.pos();holo_batch::manual_positions={centre+coord_def(3,-1),centre+coord_def(3,0),centre+coord_def(3,1)};cast("pekora",5,nullptr,centre+coord_def(3,0));step(70);
    }
    int cast_count=0,roundtrips=0;
    for(const auto &g:holo_worship::gods()) {
        monster *m=fixture(g);const auto origin=you.pos();coord_def aim=m->pos();
        const auto info_rng=rng_bytes();const auto info_batch=holo_batch::save_campaign(),info_sopia=holo_sopia::save_campaign();
        auto props_bytes=[](){std::vector<unsigned char> b;writer w(&b);you.props.write(w);return b;};
        const auto info_props=props_bytes();const int info_mp=you.magic_points,info_piety=you.piety,info_time=you.elapsed_time;
        macro_sendkeys_end_add_expanded(27);holo_worship::show_info(g);
        for(int repeat=0;repeat<10;++repeat){holo_visual::badges();require(!god_info(g).empty(),"missing god description");require(!status_lines().empty(),"missing ability status");for(int tier:{1,3,5})unavailable(tier);for(int dx=-6;dx<=6;++dx)for(int dy=-6;dy<=6;++dy)holo_visual::at(you.pos()+coord_def(dx,dy));}
        require(info_rng==rng_bytes() && info_props==props_bytes() && info_batch==holo_batch::save_campaign() && info_sopia==holo_sopia::save_campaign() && info_mp==you.magic_points && info_piety==you.piety && info_time==you.elapsed_time,"description/status changed gameplay for "+g);
        fprintf(stderr,"Campaign manual fixture: %s\n",g.c_str());
        if(g=="noel"){
            const int basehp=you.hp_max,base=you.skill(SK_LONG_BLADES,1,true);
            macro_sendkeys_end_add_expanded('a');process_command(CMD_USE_ABILITY);require(you.turn_is_over && you.magic_points==98,"normal ability menu / Noel cost");step(you.time_taken);++cast_count;
            require(you.skill(SK_LONG_BLADES,1,false)==std::min(27,base+6) && you.hp_max==basehp,"Noel native skills / no maxHP gain");
            if(const char *shots=getenv("HOLOCRAWL_NIGHT_REVIEW"))for(int f=0;f<2;++f)holo_visual::capture_invocation("noel",you.pos(),f,std::string(shots)+"/noel-menu1-frame"+std::to_string(f)+".png",1);
            cast(g,5,nullptr,origin);++cast_count;require(noel_armour()==6 && noel_shield()==4,"Noel native commander");
        } else if(g=="suisei"){
            cast(g,1,m,aim);cast(g,3,m,aim);const auto fixed=holo_sopia::field_centre();cast(g,5,m,origin+coord_def(3,0));require(holo_sopia::field_centre()==fixed,"Sopia upgrade moved actual centre");cast_count+=3;
        } else if(g=="miko"){
            cast(g,1,nullptr,origin);cast(g,3,nullptr,origin);cast(g,5,nullptr,origin);cast_count+=3;
        } else if(g=="aki"){
            aim=origin+coord_def(2,0);cast(g,1,nullptr,aim);step(10);holo_batch::manual_second=origin+coord_def(2,1);
            cast(g,3,nullptr,origin+coord_def(1,1));cast(g,5,nullptr,origin);cast_count+=3;
        } else if(g=="fubuki"){
            cast(g,1,nullptr,origin+coord_def(0,1));auto *fox=monster_by_mid(holo_batch::s.companions.front().mid);
            cast(g,3,fox,fox->pos());cast(g,5,nullptr,you.pos());cast_count+=3;
        } else if(g=="ayame"){
            cast(g,3,m,aim);cast(g,5,m,m->pos());cast_count+=2;
        } else if(g=="choco"){
            cast(g,1,m,aim);cast(g,3,m,aim);holo_batch::s.resource=3;cast(g,5,m,aim);cast_count+=3;
        } else if(g=="korone"){
            holo_batch::s.resource=4;cast(g,3,m,aim);holo_batch::s.resource=6;cast(g,5,nullptr,origin);cast_count+=2;
        } else if(g=="okayu"){
            item_def *food=nullptr;for(auto &item:you.inv)if(item.defined() && item.base_type==OBJ_FOOD){food=&item;break;}
            require(food && eat_item(*food),"native food consumption");require(holo_batch::s.resource>=38,"food enters fullness ledger");
            cast(g,3,m,aim);holo_batch::s.targets[m->mid].stacks=2;holo_batch::s.resource=30;cast(g,5,m,aim);cast_count+=2;
        } else if(g=="pekora"){
            aim=origin+coord_def(3,0);cast(g,1,nullptr,aim);step(15);cast(g,3,nullptr,aim);
            holo_batch::manual_positions={origin+coord_def(3,-1),origin+coord_def(3,0),origin+coord_def(3,1)};
            cast(g,5,nullptr,origin+coord_def(3,0));cast_count+=3;
        } else if(g=="watame"){
            cast(g,3,nullptr,origin);cast(g,5,nullptr,origin);cast_count+=2;
        } else if(g=="towa"){
            cast(g,3,nullptr,aim);cast(g,5,nullptr,origin);cast_count+=2;
        } else if(g=="lamy"){
            cast(g,1,nullptr,origin);cast(g,3,m,aim);holo_batch::s.resource=65;cast(g,5,nullptr,origin);cast_count+=3;
        } else if(g=="polka"){
            cast(g,1,m,aim,1);cast(g,3,m,aim);holo_batch::s.resource=3;cast(g,5,nullptr,you.pos(),1);cast_count+=3;
        } else if(g=="koyori"){
            cast(g,1,nullptr,origin,1);cast(g,1,m,aim,11);require(invoke(3)==0 && !reactions_enabled(),"free catalyst toggle");
            require(invoke(3)==0 && reactions_enabled(),"restore catalyst toggle");
            if(const char *shots=getenv("HOLOCRAWL_NIGHT_REVIEW"))holo_visual::capture(std::string(shots)+"/koyori-catalyst3.png");
            cast(g,5,nullptr,origin,3);cast_count+=3;
        } else if(g=="lui"){
            cast(g,1,nullptr,origin);cast(g,3,m,aim);cast(g,5,nullptr,origin);cast_count+=3;
        } else if(g=="raden"){
            cast(g,1,nullptr,origin,2);cast(g,3,nullptr,origin,2);cast(g,5,nullptr,origin);cast_count+=3;
        } else if(g=="hajime"){
            m->move_to_pos(origin+coord_def(3,0));cast(g,3,m,m->pos());cast(g,5,nullptr,you.pos());cast_count+=2;
        } else if(g=="su"){
            cast(g,3,m,aim);cast(g,5,nullptr,origin);cast_count+=2;
        } else if(g=="vivi"){
            cast(g,1,nullptr,origin);cast(g,3,nullptr,origin);cast(g,5,nullptr,origin);cast_count+=3;
        } else if(g=="sopia"){
            cast(g,1,nullptr,origin);cast(g,3,nullptr,origin+coord_def(2,0));cast(g,5,nullptr,origin+coord_def(2,0));step(20);cast(g,6,nullptr,origin);cast_count+=4;
        } else if(g=="mela"){
            require(invoke(-1)==0 && holo_batch::s.offence==0,"free ember toggle");cast(g,3,m,aim);cast(g,5,nullptr,origin);cast_count+=2;
        }
        std::vector<holo_visual::effect> drawing;
        const auto visual_rng=rng_bytes();const auto visual_batch=holo_batch::save_campaign(),visual_sopia=holo_sopia::save_campaign();
        const auto visual_props=props_bytes();
        for(int dx=-6;dx<=6;++dx)for(int dy=-6;dy<=6;++dy){const auto marks=holo_visual::at(you.pos()+coord_def(dx,dy));drawing.insert(drawing.end(),marks.begin(),marks.end());}
        require(visual_rng==rng_bytes() && visual_batch==holo_batch::save_campaign() && visual_sopia==holo_sopia::save_campaign() && visual_props==props_bytes(),"active visual query changed gameplay: "+g);
        roundtrip();++roundtrips;
        std::vector<holo_visual::effect> restored_drawing;
        for(int dx=-6;dx<=6;++dx)for(int dy=-6;dy<=6;++dy){const auto marks=holo_visual::at(you.pos()+coord_def(dx,dy));restored_drawing.insert(restored_drawing.end(),marks.begin(),marks.end());}
        require(drawing==restored_drawing,"active visual geometry changed after save: "+g);
        const int mp=you.magic_points,piety=you.piety;
        you.turn_is_over=false;you.piety=0;
        require(invoke(5,m,&aim)==0 && you.magic_points==mp && !you.turn_is_over,"locked power charged a cost");you.piety=piety;
    }
    // Natural kill credit is delivered by the real monster death path.
    for(const auto &g:holo_worship::gods()){
        fprintf(stderr,"Campaign natural kill: %s\n",g.c_str());
        auto *m=fixture(g,15);m->max_hit_points=100;m->hurt(&you,20000,BEAM_MISSILE);
        require(you.piety>=16,g+" natural kill did not grant piety");
    }
    auto *m=fixture("noel",29);m->max_hit_points=100;m->hurt(&you,20000,BEAM_MISSILE);require(you.piety>=30,"natural unlock at 30");
    fixture("noel",200);grant(5);require(you.piety==200,"piety cap");
    fprintf(stderr,"Campaign ordinary actions and rejection fixtures\n");
    auto contains=[](const coord_def &p,holo_visual::effect e){const auto marks=holo_visual::at(p);return std::find(marks.begin(),marks.end(),e)!=marks.end();};
    fixture("miko");cast("miko",1,nullptr,you.pos());require(contains(you.pos(),holo_visual::effect::shrine),"sanctuary floor missing");
    auto badge=[](holo_visual::badge b){const auto v=holo_visual::badges();return std::find(v.begin(),v.end(),b)!=v.end();};
    require(badge(holo_visual::badge::active) && !badge(holo_visual::badge::five),"ordinary power badge");
    fixture("noel");cast("noel",5,nullptr,you.pos());require(badge(holo_visual::badge::five) && badge(holo_visual::badge::shield),"commander active/protection badges");
    fixture("pekora");const auto planted=you.pos()+coord_def(0,2);cast("pekora",1,nullptr,planted);require(contains(planted,holo_visual::effect::carrot),"carrot sprite missing");
    fixture("sopia");cast("sopia",1,nullptr,you.pos());require(contains(you.pos()+coord_def(0,1),holo_visual::effect::orbit),"orbit footprint missing");
    fixture("suisei");holo_worship::renounce(false);you.elapsed_time+=100;holo_wrath::advance();const auto warned=you.pos();
    require(contains(warned,holo_visual::effect::warning) && badge(holo_visual::badge::warning),"wrath warning footprint/badge missing");you.elapsed_time+=10;require(contains(warned,holo_visual::effect::urgent) && badge(holo_visual::badge::urgent),"wrath urgent frame/badge missing");
    holo_wrath::leave_level();require(!contains(warned,holo_visual::effect::warning) && !contains(warned,holo_visual::effect::urgent),"wrath overlay leaked to next level");

    m=fixture("suisei");
    for(int n=0;n<10 && !holo_batch::s.resource;++n){process_command(CMD_MOVE_RIGHT);if(you.turn_is_over)step(you.time_taken);}
    require(holo_batch::s.resource>0 && !holo_batch::ctx.ordinary,"ordinary melee builds stars and closes context");
    m=fixture("hajime");cast("hajime",5,nullptr,you.pos());const int before_spin=m->hit_points;
    process_command(CMD_MOVE_UP);require(you.turn_is_over && holo_batch::s.resource==1 && m->hit_points<before_spin,"ordinary movement builds beat and spins");step(you.time_taken);
    fixture("noel");const int cancel_mp=you.magic_points,cancel_piety=you.piety;
    you.turn_is_over=false;macro_sendkeys_end_add_expanded(27);process_command(CMD_USE_ABILITY);
    require(!you.turn_is_over && you.magic_points==cancel_mp && you.piety==cancel_piety,"ability menu cancellation costs resources");
    fixture("ayame");you.turn_is_over=false;const auto rejected_rng=rng_bytes();
    require(invoke(3)==0 && !you.turn_is_over && rejected_rng==rng_bytes(),"invalid target consumes turn or RNG");
    m=fixture("noel",15);m->flags|=MF_NO_REWARD;m->max_hit_points=100;m->hurt(&you,20000,BEAM_MISSILE);
    require(you.piety==15,"no-reward monster grants faith");
    m=fixture("lui");cast("lui",1,nullptr,you.pos());monster *raven=monster_by_mid(holo_batch::s.companions.front().mid);
    const int pet_piety=you.piety;m->max_hit_points=100;m->hurt(raven,20000,BEAM_MISSILE);
    require(you.piety==pet_piety+2,"native raven kill credit / strong bonus");
    fixture("noel");cast("noel",5,nullptr,you.pos());const int before_berserk=you.piety;
    require(you.go_berserk(true) && !noel_commander() && you.piety==before_berserk-10,"voluntary berserk ends Noel power and applies conduct");
    fixture("watame");you.magic_points=20;const int before_blood=you.piety;
    require(cast_sublimation_of_blood(100,false)==spret::success && you.piety==before_blood-5,"blood sublimation charges Watame conduct once per cast");
    fixture("lamy",30);cast("lamy",1,nullptr,you.pos());require(you.piety==29 && holo_batch::s.resource>0,"paid drink crosses unlock line");
    step(120);require(holo_batch::s.resource==0,"drunkenness stuck below unlock");
    fixture("pekora",30);coord_def bomb=you.pos()+coord_def(3,0);cast("pekora",1,nullptr,bomb);
    require(you.piety==29 && combat_active(),"paid bomb disabled below unlock");step(220);
    require(!combat_active(),"expired bomb leaves the combat core active");
    fixture("sopia");cast("sopia",5,nullptr,you.pos());grd(you.pos())=DNGN_ALTAR_OKAWARU;
    holo_worship::renounce(false);const int sopia_ready=you.elapsed_time+150;holo_worship::join("sopia",false);
    require(holo_sopia::cooldown()==sopia_ready,"Sopia rejoin resets Big Bang cooldown");
    fprintf(stderr,"Campaign Noel supplies fixture\n");
    fixture("noel",75);
    auto &supplies=you.props["holo_noel_supplies"].get_table();supplies["half_points"]=208;
    you.piety=74;advance();require(supplies["gifts"].get_int()==0,"supplies delivered below unlock");
    you.piety=75;advance();require(supplies["gifts"].get_int()==1 && supplies["half_points"].get_int()==8,"Noel supply threshold and overflow");
    int gifts=0;
    for(const auto &item:mitm)if(item.defined() && item.props.exists("holo_gift")) {
        ++gifts;require(item.pos==you.pos() && !item.cursed() && item.plus>=(item.base_type==OBJ_WEAPONS?2:armour_is_enchantable(item)?1:0),"Noel usable uncursed minimum-enchantment delivery");
    }
    require(gifts==1,"native equipment gift missing");
    if(const char *shots=getenv("HOLOCRAWL_NIGHT_REVIEW")) {
        const auto before=signature();holo_visual::capture_invocation("noel",you.pos(),1,std::string(shots)+"/noel-supply3.png",3);
        require(before==signature(),"supply capture changed state");
    }
    supplies["half_points"]=500;advance();require(supplies["gifts"].get_int()==1,"supply minimum interval ignored");
    roundtrip();require(you.props["holo_noel_supplies"]["half_points"].get_int()==500,"supply progress save");
    for(monster_iterator mi;mi;++mi)monster_die(**mi,KILL_DISMISSED,NON_MONSTER,true);
    step(1000);
    require(you.props["holo_noel_supplies"]["gifts"].get_int()==2 && you.props["holo_noel_supplies"]["half_points"].get_int()==250,"deferred supply delivery / rising threshold");
    // No kills, healing, elapsed time or arbitrary casts create free piety.
    fprintf(stderr,"Campaign decay fixture\n");
    fixture("noel",60);for(monster_iterator mi;mi;++mi)monster_die(**mi,KILL_DISMISSED,NON_MONSTER,true);
    step(3000);require(you.piety==59,"300-turn decay / no rest income");
    fprintf(stderr,"Campaign debt fixture\n");
    fixture("korone");holo_batch::s.deferred=17;holo_batch::s.debt_ticks=5;holo_batch::s.debt_next=you.elapsed_time+10;
    require(holo_worship::renounce(false),"renounce with debt");require(you.props["holocrawl_campaign"]["debt"].get_int()==17,"debt lost on renunciation");
    roundtrip();fprintf(stderr,"Campaign debt restored: HP %d/%d\n",you.hp,you.hp_max);step(50);require(you.props["holocrawl_campaign"]["debt"].get_int()==0 && you.props["holocrawl_campaign"]["debt_paid"].get_int()==17,"integer debt total");
    fprintf(stderr,"Campaign stairs fixtures\n");
    fixture("polka");holo_batch::s.resource=5;holo_batch::s.five_ready=999;leave_level();require(holo_batch::s.resource==5 && holo_batch::s.five_ready==999,"applause/cooldown lost at stairs");
    fixture("koyori");holo_batch::s.stock[0]=3;holo_batch::s.five_end=100;leave_level();require(holo_batch::s.stock[0]==3 && holo_batch::s.five_end==0 && holo_batch::s.five_ready>=100,"stock/critical end at stairs");
    fixture("noel");cast("noel",5,nullptr,you.pos());const int ready=you.props["holocrawl_campaign"]["noel_ready"].get_int();
    grd(you.pos())=DNGN_ALTAR_OKAWARU;holo_worship::renounce(false);holo_worship::join("noel",false);require(you.props["holocrawl_campaign"]["noel_ready"].get_int()==ready,"rejoining reset cooldown");
    // Save native monsters and every ability field, then compare a fresh
    // process's next world step against uninterrupted native execution.
    fixture("suisei");holo_worship::renounce(false);you.elapsed_time+=100;holo_wrath::advance();
    require(holo_wrath::status().find("warning")!=std::string::npos,"abandoned god did not warn in combat");
    roundtrip();holo_wrath::leave_level();
    fixture("lui");cast("lui",5,nullptr,you.pos());require(holo_batch::s.companions.size()==6,"native raven host");
    holo_wrath::depart("noel",120);you.elapsed_time+=100;holo_wrath::advance();require(holo_wrath::effect("noel"),"saved wrath debuff missing");save_disk(dir);step(10);
    {std::ofstream proof(dir+"/playability.json");proof<<"{\"status\":\"passed\",\"readOnlyInfoGods\":22,\"wrathDispatchGods\":22,\"warnedAreaDodge\":true,\"fixedSquareHit\":true,\"xpDebt\":true,\"repeatedAbandonment\":true,\"warningTagRoundtrip\":true,\"debuffFreshProcessCovered\":true}\n";}
    {std::ofstream expected(dir+"/expected-step.txt");expected<<signature();}
    std::ofstream result(dir+"/validation.json");result<<"{\"status\":\"passed\",\"gods\":22,\"manualCasts\":"<<cast_count<<",\"runtimeRoundtrips\":"<<roundtrips<<",\"nativeKillIncomeGods\":22,\"debtPaidExactly\":17,\"decay\":true,\"menu\":true,\"stairsResources\":true,\"rejoinCooldown\":true,\"ordinaryMeleeAndMovement\":true,\"trainingAvailable\":true,\"paidEffectsBelowUnlock\":true,\"noRewardExclusion\":true,\"nativeRavenCredit\":true,\"abilityCancel\":true,\"noelSupplies\":true}\n";
    {std::ofstream proof(dir+"/tiles-model.json");proof<<"{\"status\":\"passed\",\"readOnlyGods\":22,\"activeStateGeometryRoundtrips\":22,\"shrine\":true,\"carrot\":true,\"orbit\":true,\"warningUrgency\":true,\"stairsCleanup\":true}\n";}
    close_save();fprintf(stderr,"Campaign abilities checks passed: %d casts, %d state roundtrips, 22 native kill paths\n",cast_count,roundtrips);return 0;
}
}

