#include "AppHdr.h"
#include "holo-lamy.h"
#include "holo-koyori.h"
#include "cloud.h"
#include "losglobal.h"
#include "evoke.h"
#include "item-status-flag-type.h"
#include "spl-cast.h"
#include "spl-util.h"
#include "status.h"
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
#include "melee-attack.h"
#include "ranged-attack.h"
#include "food.h"
#include "item-prop.h"
#include "macro.h"
#include "mon-death.h"
#include "mon-util.h"
#include "monster.h"
#include "mgen-data.h"
#include "mon-place.h"
#include "mon-project.h"
#include "options.h"
#include "player.h"
#include "random.h"
#include "state.h"
#include "skills.h"
#include "spl-other.h"
#include "tags.h"
#include "terrain.h"
#include "timed-effects.h"

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
void reload_disk(const std::string &dir,bool preserve_player_rng=false) {
    close_save();you=player();Options.no_save=false;Options.save_dir=dir;crawl_state.bypassed_startup_menu=true;
    require(restore_game(get_save_filename("HoloAbilities01")),"public restore of active abilities");
    calc_hp();
    // Synthetic fixture teardown/tile reconstruction is not a gameplay turn.
    // Keep the exact RNG restored by TAG_YOU while replacing the old test level.
    const auto restored_rng=rng::generators_to_vector();
    const auto name=level_id::current().describe();
    dgn_reset_level(false);
    reader in(you.save,name,TAG_MINOR_VERSION);require(unmarshallUByte(in)==TAG_MAJOR_VERSION,"level major version");require(unmarshallUByte(in)==TAG_MINOR_VERSION,"level minor version");tag_read(in,TAG_LEVEL);
    if(preserve_player_rng)rng::load_generators(restored_rng);
}
}
bool test_requested(){const char *v=getenv("HOLOCRAWL_CAMPAIGN_TEST");return crawl_state.test && v && std::string(v)=="1";}
int run_tests() {
    const char *path=getenv("HOLOCRAWL_CAMPAIGN_OUTPUT");require(path,"output directory required");const std::string dir(path);
    crawl_state.show_more_prompt=false;
    if(getenv("HOLOCRAWL_MIKO_PASSIVE_RELOAD")) {
        holo_reset_validation_fixture();reload_disk(dir+"/miko-save",true);
        require(holo_worship::current()=="miko" && holo_worship::rank()==2,"Miko tier2 restore");
        require(holo_batch::s.shield==4 && holo_batch::s.defence>you.elapsed_time,"Miko shield restore");
        require(holo_batch::incoming(7,KILLED_BY_MONSTER,MID_NOBODY)==3 && holo_batch::s.shield==0,"restored absorption");
        std::ifstream f(dir+"/miko-expected.txt");std::string expected((std::istreambuf_iterator<char>(f)),{});
        require(signature()==expected,"Miko exact combat continuation after fresh restore");
        std::ofstream(dir+"/miko-reload.json")<<"{\"status\":\"passed\",\"shieldRestored\":true,\"exactCombatAndRng\":true}";
        close_save();return 0;
    }
    if(const char *shots=getenv("HOLOCRAWL_MIKO_PASSIVE_REVIEW")) {
        using namespace holo_batch;
        auto direct=[&](monster *m) {
            command_scope command;bolt beam;beam.name="Miko actual kill probe";beam.origin_spell=SPELL_MAGIC_DART;
            beam.source=you.pos();beam.target=m->pos();beam.range=6;beam.source_id=you.mid;beam.thrower=KILL_YOU;
            beam.flavour=BEAM_MMISSILE;beam.damage=dice_def(4,20);beam.hit=AUTOMATIC_HIT;
            beam.fire();you.turn_is_over=true;you.time_taken=10;
        };
        auto setup=[&](int faith,int missing) {
            auto *m=fixture("miko",faith);cast("miko",1,nullptr,you.pos());
            require(s.inv==12,"Miko fixture Invocations12");
            m->type=MONS_RAT;m->set_hit_dice(1);m->hit_points=m->max_hit_points=1;
            you.hp=you.hp_max-missing;return m;
        };
        for(int faith:{49,50}) {
            auto *m=setup(faith,8);const int hp=you.hp;
            if(faith==50)holo_visual::capture(std::string(shots)+"/miko-heal-before.png");
            direct(m);require(!m->alive() && you.hp-hp==(faith==50?4:0) && s.shield==0,"native kill heal49/50");
            if(faith==50)holo_visual::capture(std::string(shots)+"/miko-heal-after.png");
        }
        auto *m=setup(50,1);direct(m);require(you.hp==you.hp_max && s.shield==3,"partial overflow");
        m=setup(50,0);holo_visual::capture(std::string(shots)+"/miko-shield-before.png");
        direct(m);require(s.shield==4 && s.defence==you.elapsed_time+50,"full HP overflow shield");
        holo_visual::capture(std::string(shots)+"/miko-shield-after.png");
        auto spawn=[&]() {
            auto mg=mgen_data::hostile_at(MONS_RAT,false,you.pos()+coord_def(2,0));mg.flags|=MG_FORCE_PLACE;
            auto *n=create_monster(mg,false);require(n,"extra rat");n->hit_points=n->max_hit_points=1;n->speed=n->speed_increment=0;return n;
        };
        direct(spawn());require(s.shield==4,"cooldown bypass");
        step(20);direct(spawn());require(s.shield==8,"shield accumulation cap");
        require(incoming(3,KILLED_BY_DIVINE_WRATH,MID_NOBODY)==3 && s.shield==8,"shield absorbed wrath");
        require(incoming(3,KILLED_BY_SOMETHING,MID_NOBODY)==3 && s.shield==8,"shield absorbed cost/torment");
        require(incoming(3,KILLED_BY_MONSTER,MID_NOBODY)==0 && s.shield==5,"ordinary absorption");
        require(incoming(8,KILLED_BY_CLOUD,MID_NOBODY)==3 && s.shield==0,"cloud absorption");
        m=setup(50,0);direct(m);s.defence=you.elapsed_time;require(incoming(3,KILLED_BY_BEAM,MID_NOBODY)==3 && s.shield==0,"expired shield");
        m=setup(50,0);direct(m);const auto old=you.pos();you.moveto(s.centre+coord_def(3,0));after_move(old,true);require(s.shield==0,"leaving shrine retained shield");
        m=setup(50,0);direct(m);cast("miko",1,nullptr,you.pos());require(s.shield==0,"reinstall retained shield");
        m=setup(50,0);direct(m);leave_level();require(s.shield==0 && s.defence==0,"floor change retained shield");
        m=setup(50,8);m->flags|=MF_NO_REWARD;const int hp=you.hp;direct(m);require(you.hp==hp && s.shield==0,"no-XP kill rewarded");
        m=setup(50,8);require(m->move_to_pos(you.pos()+coord_def(3,0)),"outside target placement");const int before=you.hp;direct(m);require(you.hp==before,"outside enemy rewarded");
        m=setup(50,8);you.duration[DUR_DEATHS_DOOR]=10;direct(m);require(s.shield==0 && you.hp==you.hp_max-8,"blocked heal became shield");
        m=setup(50,0);direct(m);you.piety=49;require(incoming(1,KILLED_BY_MONSTER,MID_NOBODY)==1 && s.shield==0,"lost faith retained shield");
        m=setup(50,0);direct(m);save_disk(dir+"/miko-save");close_save();
        require(incoming(7,KILLED_BY_MONSTER,MID_NOBODY)==3,"saved fixture absorption");
        std::ofstream(dir+"/miko-expected.txt")<<signature();
        std::ofstream(dir+"/miko-passive.json")<<"{\"status\":\"passed\",\"combatImplemented\":true,\"healAtInv12\":4,\"capAtInv12\":8,\"unlock\":50,\"nativeKills\":true,\"cooldown\":true,\"expiryAndExit\":true,\"excludedSources\":true}";
        close_save();return 0;
    }
    if(getenv("HOLOCRAWL_KOYORI_RELOAD")) {
        holo_reset_validation_fixture();reload_disk(dir+"/koyori-save");step(10);
        std::ifstream f(dir+"/koyori-expected.txt");std::string expected((std::istreambuf_iterator<char>(f)),{});
        require(signature()==expected,"Koyori fresh-process state/RNG/poison/critical restore");
        std::ofstream(dir+"/koyori-reload.json")<<"{\"status\":\"passed\"}\n";close_save();return 0;
    }
    if(getenv("HOLOCRAWL_LAMY_TOOL_RELOAD")) {
        holo_reset_validation_fixture();reload_disk(dir+"/lamy-cloud-save");
        auto *m=monster_by_mid(you.props["lamy_test_mid"].get_int());
        require(m && holo_worship::current()=="lamy","Lamy fresh cloud player/monster restore");
        const int group=holo_lamy::cloud_use(m->pos());
        require(group==you.props["lamy_test_group"].get_int() && group>0,"Lamy cloud provenance restored with level");
        const auto stacks=holo_batch::s.targets[m->mid].stacks;
        require(actor_apply_cloud(m)>0 && holo_batch::s.targets[m->mid].stacks==stacks,"Lamy saved cloud repeats after fresh process");
        std::ifstream expected(dir+"/lamy-cloud-expected.txt");std::string data((std::istreambuf_iterator<char>(expected)),{});
        require(data==signature(),"Lamy cloud fresh continuation RNG/damage mismatch");
        std::ofstream(dir+"/lamy-cloud-reload.json")<<"{\"status\":\"passed\",\"nativeCloudRestored\":true,\"dedupRestored\":true,\"continuationExact\":true}\n";
        close_save();return 0;
    }
    const char *mode=getenv("HOLOCRAWL_CAMPAIGN_RELOAD");
    if(getenv("HOLOCRAWL_SU_WATER_RELOAD")) {
        holo_reset_validation_fixture();reload_disk(dir+"/su-water-save");
        const auto p=you.pos()+coord_def(1,0);
        require(grd(p)==DNGN_SHALLOW_WATER && is_temp_terrain(p),"Su native water missing after fresh restore");
        const int dry_speed=player_movement_speed();require(you.move_to_pos(p),"Su restored player enters water");
        require(!you.floundering() && player_movement_speed()==dry_speed && !you.fumbles_attack(),"Su shallow-water immunity missing after restore");
        timeout_terrain_changes(1000);
        require(grd(p)==DNGN_FLOOR && !is_temp_terrain(p),"Su restored terrain did not expire");
        std::ofstream(dir+"/su-water-reload.json")<<"{\"status\":\"passed\",\"nativeTerrainRestored\":true,\"expiryRestored\":true}\n";
        close_save();return 0;
    }
    if(mode && std::string(mode)=="1") {
        holo_reset_validation_fixture();reload_disk(dir);
        require(holo_worship::current()=="lui" && holo_batch::s.companions.size()==6,"native companions restored");
        for(auto c:holo_batch::s.companions){const auto *m=monster_by_mid(c.mid);require(m && m->alive(),"companion MID resolved after fresh-process load");}
        step(10);std::ifstream expected(dir+"/expected-step.txt");std::string data((std::istreambuf_iterator<char>(expected)),{});
        require(data==signature(),"fresh-process native world continuation differs");
        std::ofstream proof(dir+"/reload.json");proof<<"{\"status\":\"passed\",\"nativeLevel\":true,\"companions\":6,\"nextWorldStepExact\":true}\n";
        close_save();return 0;
    }
    if(getenv("HOLOCRAWL_SUISEI_INHERIT_RELOAD")) {
        holo_reset_validation_fixture();reload_disk(dir+"/inherit-save",true);
        auto *m=monster_by_mid(you.props["inherit_test_mid"].get_int());
        require(m && holo_worship::rank()==4 && holo_batch::s.offence>0,"inheritance bank not restored");
        // The uninterrupted replay had a framebuffer capture just before
        // casting. Warm the restored native view identically, without RNG use.
        holo_visual::capture(dir+"/inherit-reloaded-ready.png");
        std::ofstream(dir+"/inherit-bank-actual.txt")<<signature();
        std::ifstream bank_file(dir+"/inherit-bank-expected.txt");std::string bank_text((std::istreambuf_iterator<char>(bank_file)),{});
        require(bank_text==signature(),"banked reward/player/actors/RNG were not restored exactly");
        // process_command normally supplies the default action time before casting.
        you.time_taken=10;you.turn_is_over=false;
        {command_scope command;you.prev_targ=m->mindex();macro_buf_add_cmd(CMD_TARGET_SELECT);
         require(cast_a_spell(false,SPELL_MAGIC_DART),"restored inheritance native spell");}
        require(holo_batch::s.marked==m->mid && holo_batch::s.resource==2 && holo_batch::s.offence==0,"restored reward did not start at2");
        step(you.time_taken);std::ifstream expected(dir+"/inherit-expected.txt");std::string text((std::istreambuf_iterator<char>(expected)),{});
        const bool full_ui_rng_match=text==signature();
        if(!full_ui_rng_match)std::ofstream(dir+"/inherit-actual.txt")<<signature();
        auto gameplay=[](const std::string &value){size_t start=0;for(int n=0;n<3;++n){start=value.find('|',start);if(start==std::string::npos)throw std::runtime_error("bad signature");++start;}const auto end=value.find('|',start);return value.substr(0,start)+(end==std::string::npos?std::string():value.substr(end));};
        require(gameplay(text)==gameplay(signature()),"actual UI spell outcome/time/resources/actors differ after restore");
        // Separately replay the ordinary combat hit without targeting/UI,
        // preserving the strict full-state and RNG invariant for combat code.
        reload_disk(dir+"/inherit-save",true);m=monster_by_mid(you.props["inherit_test_mid"].get_int());require(m,"restored combat probe target");
        holo_visual::capture(dir+"/inherit-combat-ready-actual.png");
        std::ofstream(dir+"/inherit-combat-bank-actual.txt")<<signature();
        you.time_taken=10;you.turn_is_over=false;
        {command_scope command;bolt beam;beam.name="inheritance probe";beam.origin_spell=SPELL_MAGIC_DART;
         beam.source=you.pos();beam.target=m->pos();beam.range=6;beam.source_id=you.mid;beam.thrower=KILL_YOU;
         beam.flavour=BEAM_MMISSILE;beam.damage=dice_def(4,20);beam.hit=AUTOMATIC_HIT;beam.fire();you.turn_is_over=true;you.time_taken=10;}
        require(holo_batch::s.resource==2 && holo_batch::s.offence==0,"restored ordinary combat inheritance");
        std::ifstream core_file(dir+"/inherit-combat-expected.txt");std::string core_text((std::istreambuf_iterator<char>(core_file)),{});
        if(core_text!=signature())std::ofstream(dir+"/inherit-combat-actual.txt")<<signature();
        require(core_text==signature(),"ordinary combat hit/RNG continuation differs after restore");
        std::ofstream(dir+"/inherit-reload.json")<<"{\"status\":\"passed\",\"bankedRewardAndRngRestoredExactly\":true,\"actualSpellStartsAt2\":true,\"actualSpellGameplayContinuationMatches\":true,\"ordinaryCombatHitAndRngMatch\":true,\"fullRngAfterUiCastMatches\":"<<(full_ui_rng_match?"true":"false")<<",\"scope\":\"Targeting UI RNG replay is diagnostic, isolated from combat and bank restoration checks.\"}\n";
        close_save();return 0;
    }
    if(const char *shots=getenv("HOLOCRAWL_SUISEI_INHERIT_REVIEW")) {
        using namespace holo_batch;
        auto hit=[&](monster *m,int sides=20,int accuracy=AUTOMATIC_HIT) {
            command_scope command;bolt beam;beam.name="inheritance probe";beam.origin_spell=SPELL_MAGIC_DART;
            beam.source=you.pos();beam.target=m->pos();beam.range=6;beam.source_id=you.mid;beam.thrower=KILL_YOU;
            beam.flavour=BEAM_MMISSILE;beam.damage=dice_def(4,sides);beam.hit=accuracy;
            beam.fire();you.turn_is_over=true;you.time_taken=10;
        };
        for(int faith:{99,100}) {
            auto *m=fixture("suisei",faith);require(m->move_to_pos(you.pos()+coord_def(2,0)),"inheritance faith target");
            s.offence=13;s.three_end=100;hit(m);
            require(s.resource==(faith==100?2:1) && s.offence==0 && you.piety==faith,"inheritance faith99/100 or free-resource rule");
            require(holo_worship::rank()==(faith==100?4:3),"Suisei four-star rank");
        }
        auto *m=fixture("suisei",100);require(m->move_to_pos(you.pos()+coord_def(2,0)),"inheritance miss target");
        bool missed=false;
        for(int trial=0;trial<64 && !missed;++trial){s.marked=MID_NOBODY;s.resource=0;s.offence=13;s.three_end=100;m->hit_points=10000;rng::seed(81000+trial);hit(m,20,0);missed=m->hit_points==10000;}
        require(missed && s.offence==13 && s.three_end==100 && s.resource==0,"native miss consumed reward or inherited stars");
        m=fixture("suisei",100);m->type=MONS_RAT;m->set_hit_dice(1);m->hit_points=m->max_hit_points=1;s.offence=13;s.three_end=100;hit(m);
        require(!m->alive() && s.resource==0 && s.offence==0,"one-shot inherited stars or renewed reward");
        m=fixture("suisei",100);m->type=MONS_RAT;m->set_hit_dice(1);m->hit_points=m->max_hit_points=3;
        s.marked=m->mid;s.resource=2;s.one_end=100;s.offence=13;s.three_end=100;
        {command_scope command;bolt beam;beam.name="small inheritance probe";beam.origin_spell=SPELL_MAGIC_DART;
         beam.source=you.pos();beam.target=m->pos();beam.range=6;beam.source_id=you.mid;beam.thrower=KILL_YOU;
         beam.flavour=BEAM_MMISSILE;beam.damage=dice_def(1,1);beam.hit=AUTOMATIC_HIT;beam.fire();you.turn_is_over=true;you.time_taken=10;}
        require(!m->alive() && s.resource==0 && s.marked==MID_NOBODY && s.offence==0,"reward-only kill recursed or retained dead mark");
        for(int prior:{1,2}){m=fixture("suisei",100);s.marked=m->mid;s.resource=prior;s.one_end=100;s.offence=13;s.three_end=100;hit(m);require(s.resource==prior+1,"inheritance doubled existing stacks");}
        m=fixture("suisei",100);s.offence=13;s.three_end=you.elapsed_time;hit(m);require(s.resource==1,"expired reward inherited stars");
        m=fixture("suisei",100);hit(m);require(s.resource==1,"ordinary hit inherited without reward");
        m=fixture("suisei",100);s.offence=13;s.three_end=100;const auto aim=m->pos();
        require(invoke(3,m,&aim)==10 && s.offence==13 && s.three_end==100 && s.resource==0,"divine power consumed inheritance");
        // Actual memorised Magic Dart commands, with native MP and action cost.
        auto *a_target=fixture("suisei",100);a_target->type=MONS_ORC;a_target->set_hit_dice(1);a_target->inv.init(NON_ITEM);
        require(a_target->move_to_pos(you.pos()+coord_def(2,0)),"inheritance actor A placement");
        auto mg=mgen_data::hostile_at(MONS_GOBLIN,false,you.pos()+coord_def(4,0));mg.flags|=MG_FORCE_PLACE;
        auto *b_target=create_monster(mg,false);require(b_target,"inheritance actor B");b_target->inv.init(NON_ITEM);b_target->speed=b_target->speed_increment=0;b_target->hit_points=b_target->max_hit_points=1000;
        require(a_target->armour_class()==0 && b_target->armour_class()==0,"inheritance display zero-AC targets");
        set_skill_level(SK_CONJURATIONS,27);set_skill_level(SK_SPELLCASTING,27);you.duration[DUR_BRILLIANCE]=100;
        require(add_spell_to_memory(SPELL_MAGIC_DART),"inheritance learn native spell");
        auto normal_cast=[&](monster *target) {
            const int mp=you.magic_points;
            you.time_taken=10;you.turn_is_over=false;
            {command_scope command;you.prev_targ=target->mindex();macro_buf_add_cmd(CMD_TARGET_SELECT);
             require(cast_a_spell(false,SPELL_MAGIC_DART),"inheritance normal spell command");}
            require(you.magic_points==mp-1 && you.turn_is_over && you.time_taken>0,"inheritance changed spell MP/action cost");
            step(you.time_taken);
        };
        const std::string folder(shots);holo_visual::capture(folder+"/inherit-before.png");
        for(int count=1;count<=3;++count){normal_cast(a_target);require(s.marked==a_target->mid && s.resource==count,"native spell did not build A stars");holo_visual::capture(folder+"/inherit-a"+std::to_string(count)+".png");}
        a_target->hit_points=a_target->max_hit_points=1;normal_cast(a_target);
        require(!a_target->alive() && s.offence>0 && s.three_end>you.elapsed_time && s.resource==0,"native kill did not bank reward");
        const int reward=s.offence;holo_visual::capture(folder+"/inherit-bank.png");
        // Save between real kill and real next-hit reward consumption.
        you.props["inherit_test_mid"]=int(b_target->mid);auto prior_dir=Options.save_dir;const bool no_save=Options.no_save;
        save_disk(dir+"/inherit-save");close_save();Options.save_dir=prior_dir;Options.no_save=no_save;
        std::ofstream(dir+"/inherit-bank-expected.txt")<<signature();
        const int hp=b_target->hit_points;normal_cast(b_target);
        require(b_target->alive() && b_target->hit_points<hp && s.marked==b_target->mid && s.resource==2 && s.offence==0 && s.three_end==0,"real reward spell did not start B at2");
        require(suisei_focus_accuracy(b_target)==3,"inherited stars did not activate tier2");
        std::ofstream(dir+"/inherit-expected.txt")<<signature();holo_visual::capture(folder+"/inherit-b2.png");
        normal_cast(b_target);require(s.resource==3,"next normal hit did not cap B at3");holo_visual::capture(folder+"/inherit-b3.png");
        // Replay from the same native bank save without the targeting UI.
        const int ui_followup_total_damage=hp-b_target->hit_points;
        reload_disk(dir+"/inherit-save",true);auto *probe=monster_by_mid(you.props["inherit_test_mid"].get_int());require(probe,"ordinary combat probe target");
        holo_visual::capture(dir+"/inherit-combat-ready-expected.png");
        std::ofstream(dir+"/inherit-combat-bank-expected.txt")<<signature();
        you.time_taken=10;you.turn_is_over=false;hit(probe);
        require(s.resource==2 && s.offence==0,"ordinary combat probe inheritance");
        std::ofstream(dir+"/inherit-combat-expected.txt")<<signature();close_save();Options.save_dir=prior_dir;Options.no_save=no_save;
        std::ofstream proof(dir+"/suisei-inherit.json");proof<<"{\"status\":\"passed\",\"unlockPiety\":100,\"startsAt\":2,\"maxStars\":3,\"nativeSpellCommands\":6,\"nativeMPAndTimeCosts\":true,\"actualMarkedKill\":true,\"rewardDamage\":"<<reward<<",\"actualNextTargetDamage\":"<<ui_followup_total_damage<<",\"missKeepsReward\":true,\"oneShotExcluded\":true,\"rewardOnlyKillNoRecursion\":true,\"deadMarkCleared\":true,\"existingStacksOnlyPlus1\":true,\"expiryAndFaithControls\":true,\"divineExcluded\":true,\"tier2ActivatedAt2\":true}\n";
        // Keep real spell/menu/kill fixture state isolated from older regressions.
        close_save();return 0;
    }
    if(getenv("HOLOCRAWL_SUISEI_FOCUS_RELOAD")) {
        holo_reset_validation_fixture();reload_disk(dir+"/focus-save");
        auto *m=monster_by_mid(holo_batch::s.marked);
        require(you.piety==50 && holo_worship::rank()==2 && m && holo_batch::suisei_focus_accuracy(m)==3,"Suisei focused observation restore");
        step(10);std::ifstream expected(dir+"/focus-expected.txt");std::string text((std::istreambuf_iterator<char>(expected)),{});
        require(text==signature(),"Suisei focus native continuation differs");
        std::ofstream(dir+"/focus-reload.json")<<"{\"status\":\"passed\",\"derivedPassiveRestored\":true,\"piety\":50,\"rank\":2,\"exactContinuation\":true}\n";
        close_save();return 0;
    }
    if(const char *shots=getenv("HOLOCRAWL_SUISEI_FOCUS_REVIEW")) {
        using namespace holo_batch;
        auto *m=fixture("suisei",50);s.marked=m->mid;s.resource=2;s.one_end=100;
        const auto stable=signature();require(suisei_focus_accuracy(m)==3 && stable==signature(),"Suisei focus query mutated world/RNG");
        require(holo_worship::rank()==2,"Suisei faith50 not rank2");
        you.piety=49;require(suisei_focus_accuracy(m)==0 && holo_worship::rank()==1,"focus unlocked below50");you.piety=50;
        for(int stars=0;stars<=3;++stars){s.resource=stars;require(suisei_focus_accuracy(m)==(stars>=2?3:0),"focus stack threshold");}
        s.resource=2;s.one_end=you.elapsed_time;require(suisei_focus_accuracy(m)==0,"expired focus");s.one_end=100;
        const auto marked=s.marked;s.marked=MID_NOBODY;require(suisei_focus_accuracy(m)==0,"focus affects unmarked foe");s.marked=marked;
        require(suisei_focus_accuracy(&you)==0,"focus affects player");
        {damage_scope god_damage(true);require(suisei_focus_accuracy(m)==0,"divine power got focus");}
        for(int inv:{0,12,27}){s.inv=inv;require(suisei_focus_accuracy(m)==3,"focus scales with Invocations");}
        s.inv=12;
        // Inspect the same native weapon attack object before hit randomisation.
        begin_attack(*m,attack_kind::melee);melee_attack melee(&you,m);
        s.resource=1;const int melee0=melee.calc_to_hit(false);s.resource=2;const int melee1=melee.calc_to_hit(false);
        require(to_hit(&you,m)==3 && melee1-melee0>=1 && melee1-melee0<=2,"native melee raw+3 and average delta");cancel_attack();
        for(int subtype:{MI_STONE,MI_JAVELIN,MI_DART}) {
            item_def missile;missile.base_type=OBJ_MISSILES;missile.sub_type=subtype;missile.quantity=1;
            begin_attack(*m,attack_kind::ranged);ranged_attack ranged(&you,m,&missile,false);
            s.resource=1;const int before=ranged.calc_to_hit(false);s.resource=2;const int after=ranged.calc_to_hit(false);
            require(to_hit(&you,m)==3 && after-before>=1 && after-before<=2,"native thrown raw+3 and average delta");cancel_attack();
        }
        // Native bolt path: use identical seeds on a foe with ordinary EV.
        // Accuracy5/8 is deliberately low enough to expose the +3 delta.
        int hits[2]={0},automatic_damage[2]={0},slow_duration[2]={0};
        std::vector<unsigned char> automatic_rng,slow_rng;
        for(int focused=0;focused<=1;++focused) {
            m=fixture("suisei",50);require(m->move_to_pos(you.pos()+coord_def(2,0)),"focus spell target");
            for(int seed=0;seed<64;++seed) {
                s.marked=m->mid;s.resource=focused?2:1;s.one_end=100;m->hit_points=10000;
                command_scope command;bolt beam;beam.name="focus test bolt";beam.origin_spell=SPELL_THROW_FLAME;
                beam.source=you.pos();beam.target=m->pos();beam.range=5;beam.source_id=you.mid;beam.thrower=KILL_YOU;
                beam.flavour=BEAM_FIRE;beam.damage=dice_def(4,20);beam.hit=5;rng::seed(71000+seed);
                beam.fire();you.turn_is_over=true;you.time_taken=10;hits[focused]+=m->hit_points<10000;
            }
            m=fixture("suisei",50);require(m->move_to_pos(you.pos()+coord_def(2,0)),"focus auto-hit target");s.marked=m->mid;s.resource=focused?2:1;s.one_end=100;
            {command_scope command;bolt beam;beam.name="magic dart";beam.origin_spell=SPELL_MAGIC_DART;
             beam.source=you.pos();beam.target=m->pos();beam.range=5;beam.source_id=you.mid;beam.thrower=KILL_YOU;
             beam.flavour=BEAM_MMISSILE;beam.damage=dice_def(4,20);beam.hit=AUTOMATIC_HIT;rng::seed(72000);
             beam.fire();require(beam.hit==AUTOMATIC_HIT,"auto-hit sentinel changed");you.turn_is_over=true;you.time_taken=10;}
            automatic_damage[focused]=10000-m->hit_points;
            if(!focused)automatic_rng=rng_bytes();else require(automatic_rng==rng_bytes(),"focus changed auto-hit RNG");
            m=fixture("suisei",50);require(m->move_to_pos(you.pos()+coord_def(2,0)),"focus MR target");s.marked=m->mid;s.resource=focused?2:1;s.one_end=100;
            bolt slow;zappy(ZAP_SLOW,40,false,slow);slow.source=you.pos();slow.target=m->pos();slow.range=5;slow.source_id=you.mid;slow.thrower=KILL_YOU;
            rng::seed(73000);slow.fire();slow_duration[focused]=m->has_ench(ENCH_SLOW)?m->get_ench(ENCH_SLOW).duration:0;
            if(!focused)slow_rng=rng_bytes();else require(slow_rng==rng_bytes(),"focus changed MR RNG");
        }
        require(hits[1]>hits[0],"focused native spell hit checks did not improve");
        require(automatic_damage[0]==automatic_damage[1] && slow_duration[0]==slow_duration[1],"focus changed auto-hit damage or MR outcome");
        m=fixture("suisei",50);require(m->move_to_pos(you.pos()+coord_def(2,0)),"focus indicator target");
        for(int count=1;count<=3;++count){s.marked=m->mid;s.resource=count;s.one_end=100;holo_visual::capture(std::string(shots)+"/focus"+std::to_string(count)+".png");}
        s.resource=2;const int hp=you.hp,mp=you.magic_points,faith=you.piety,now=you.elapsed_time;const auto query_rng=rng_bytes();
        for(int n=0;n<10;++n)require(suisei_focus_accuracy(m)==3,"focus query unstable");
        require(hp==you.hp && mp==you.magic_points && faith==you.piety && now==you.elapsed_time && query_rng==rng_bytes(),"passive query consumed resources/time/RNG");
        auto prior=Options.save_dir;const bool no_save=Options.no_save;save_disk(dir+"/focus-save");step(10);std::ofstream(dir+"/focus-expected.txt")<<signature();
        close_save();Options.save_dir=prior;Options.no_save=no_save;
        std::ofstream proof(dir+"/suisei-focus.json");proof<<"{\"status\":\"passed\",\"piety\":50,\"stars\":2,\"accuracy\":3,\"nativeMeleeDelta\":"<<3<<",\"nativeMeleeAverageDelta\":"<<melee1-melee0<<",\"nativeThrownTypes\":[\"stone\",\"javelin\",\"dart\"],\"nativeSpellTrialsPerCase\":64,\"spellHitsBefore\":"<<hits[0]<<",\"spellHitsAfter\":"<<hits[1]<<",\"autoHitDamageUnchanged\":true,\"mrOutcomeAndRngUnchanged\":true,\"noResourceCost\":true,\"expiryAndFaithControls\":true,\"divineExcluded\":true,\"fixedAcrossInvocations\":true}\n";
    }
    if(getenv("HOLOCRAWL_SUISEI_THREE_RELOAD")) {
        holo_reset_validation_fixture();reload_disk(dir+"/suisei-save");
        require(holo_worship::current()=="suisei" && holo_batch::s.resource==3,"Suisei fresh-process stars lost");
        require(holo_batch::s.hazards.size()==1 && holo_batch::s.hazards[0].extra==3,"Suisei pending comet lost");
        step(10);std::ifstream expected(dir+"/suisei-expected.txt");std::string text((std::istreambuf_iterator<char>(expected)),{});
        require(text==signature(),"Suisei fresh-process world/RNG continuation mismatch");
        std::ofstream(dir+"/suisei-reload.json")<<"{\"status\":\"passed\",\"nativeLevel\":true,\"stars\":3,\"pendingComet\":true,\"exactContinuation\":true}\n";
        close_save();return 0;
    }
    if(const char *shots=getenv("HOLOCRAWL_SUISEI_THREE_REVIEW")) {
        using namespace holo_batch;
        auto direct=[&](monster *m,int sides=20) {
            command_scope command;bolt beam;beam.name="magic dart";beam.origin_spell=SPELL_MAGIC_DART;
            beam.source=you.pos();beam.target=m->pos();beam.range=5;beam.source_id=you.mid;
            beam.thrower=KILL_YOU;beam.flavour=BEAM_MMISSILE;beam.damage=dice_def(4,sides);beam.hit=AUTOMATIC_HIT;
            beam.fire();you.turn_is_over=true;you.time_taken=10;
        };
        auto *m=fixture("suisei",30);require(m->move_to_pos(you.pos()+coord_def(2,0)),"Suisei three hit placement");
        holo_visual::capture(std::string(shots)+"/three-0.png");
        for(int hit=1;hit<=4;++hit) {
            const int hp=m->hit_points;direct(m);
            require(m->hit_points<hp && s.resource==std::min(3,hit),"Suisei positive direct hit/cap3");
            const auto stable=signature();holo_visual::capture(std::string(shots)+"/three-"+std::to_string(hit)+".png");
            require(stable==signature(),"Suisei live indicator mutated world/RNG");
        }
        int sx=1,sy=1;require(holo_visual::invocation_sprite_at(m->pos(),sx,sy)==holo_visual::effect::suiseistars3,"live indicator missing without preview prop");
        begin_attack(*m,attack_kind::spell);note_primary_damage(m,0);end_attack(10);
        require(s.resource==3,"zero damage changes stars");
        roundtrip();require(s.resource==3,"Suisei three-stack save roundtrip");
        step(100);require(s.resource==0,"Suisei stack expiry not10turns");
        // Seeded core kill hook checks the rolled reward against the full
        // 1/2/3-star formula, independently of later damage/AC rolls.
        for(int stars=1;stars<=3;++stars) {
            m=fixture("suisei");s.marked=m->mid;s.resource=stars;s.one_end=100;
            begin_attack(*m);rng::seed(62000+stars);const int expected=roll_dice(1,3+4*stars);
            rng::seed(62000+stars);resource_kill(m->mid,m->get_experience_level(),true,true);
            require(s.offence==expected && s.three_end==you.elapsed_time+30,"Suisei reward formula/window");cancel_attack();
        }
        // Genuine ordinary spell kill grants and consumes the reward once.
        m=fixture("suisei",99);m->type=MONS_RAT;m->max_hit_points=m->hit_points=1;s.marked=m->mid;s.resource=3;s.one_end=100;direct(m,200);
        require(!m->alive() && s.offence>=1 && s.offence<=15 && s.three_end==you.elapsed_time+30,"Suisei actual kill reward");
        const auto p=you.pos()+coord_def(2,0);auto mg=mgen_data::hostile_at(MONS_RAT,false,p);mg.flags|=MG_FORCE_PLACE;
        auto *next=create_monster(mg,false);require(next,"Suisei next enemy");next->hit_points=next->max_hit_points=10000;next->speed=next->speed_increment=0;
        you.piety=99;direct(next);require(s.offence==0 && s.three_end==0 && s.resource==1,"Suisei reward consumption below tier4");
        // Compare raw post-AC deltas on a native low-AC rat, with identical
        // RNG/Invocations. Covers both active formulas, costs and consumption.
        int cut[4]={0},comet[4]={0};
        for(int stars=0;stars<=3;++stars) {
            m=fixture("suisei");m->type=MONS_RAT;require(m->armour_class()<=1,"low AC cut fixture");
            require(m->move_to_pos(you.pos()+coord_def(3,0)),"cut target placement");
            s.marked=m->mid;s.resource=stars;s.one_end=100;const auto aim=m->pos();
            int hp=m->hit_points;const int mp=you.magic_points,faith=you.piety;rng::seed(424242);
            require(invoke(3,m,&aim)==10 && you.magic_points==mp-3 && you.piety==faith-3,"Suisei cut cost");
            cut[stars]=hp-m->hit_points;require(cut[stars]>0 && s.resource==0,"Suisei cut hit/consume");
            m=fixture("suisei");m->type=MONS_RAT;require(m->move_to_pos(you.pos()+coord_def(3,0)),"comet target placement");
            s.marked=m->mid;s.resource=stars;s.one_end=100;const auto centre=m->pos();hp=m->hit_points;
            require(invoke(5,nullptr,&centre)==10 && you.magic_points==94 && you.piety==170,"Suisei comet cost");
            require(s.resource==0 && s.hazards.back().extra==stars,"Suisei comet star snapshot");
            step(20);require(m->hit_points==hp,"Suisei comet lands before2turns after cast");
            rng::seed(424242);step(10);comet[stars]=hp-m->hit_points;require(comet[stars]>0,"Suisei comet did not land");
        }
        for(int stars=1;stars<=3;++stars)require(cut[stars]-cut[0]==5*stars && comet[stars]-comet[0]==8*stars,"Suisei active star scaling");
        // Legacy 5-star progress, rolled reward and an already queued comet.
        m=fixture("suisei");s.marked=m->mid;s.one_end=100;s.resource=5;s.offence=13;s.three_end=30;
        hazard old;old.kind=1;old.pos=m->pos();old.target=m->mid;old.extra=5;old.arm=30;s.hazards.push_back(old);
        auto legacy=save_campaign();legacy[0]='1';load_campaign(legacy);
        require(s.resource==3 && s.offence==13 && s.hazards[0].end==-1 && s.hazards[0].extra==5,"Suisei legacy conversion");
        auto converted=save_campaign();load_campaign(converted);require(converted==save_campaign(),"Suisei legacy conversion repeated");
        // Save the whole native level with cap3 and an independently pending comet.
        m=fixture("suisei");require(m->move_to_pos(you.pos()+coord_def(3,0)),"Suisei save target");
        s.marked=m->mid;s.resource=3;s.one_end=100;hazard pending;pending.kind=1;pending.pos=m->pos();pending.target=m->mid;pending.extra=3;pending.arm=30;s.hazards.push_back(pending);
        auto prior=Options.save_dir;const bool no_save=Options.no_save;save_disk(dir+"/suisei-save");step(10);
        std::ofstream(dir+"/suisei-expected.txt")<<signature();close_save();Options.save_dir=prior;Options.no_save=no_save;
        std::ofstream result(dir+"/suisei-three.json");result<<"{\"status\":\"passed\",\"cap\":3,\"realDirectHits\":4,\"zeroDamageControl\":true,\"rewardFormulaAndConsumption\":true,\"cutPerStar\":5,\"cometPerStar\":8,\"costsAndDelay\":true,\"legacyMigrationIdempotent\":true,\"liveVfxWithoutPreviewProp\":true,\"cutDamage\":["<<cut[0]<<','<<cut[1]<<','<<cut[2]<<','<<cut[3]<<"],\"cometDamage\":["<<comet[0]<<','<<comet[1]<<','<<comet[2]<<','<<comet[3]<<"]}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_MELA_DISPATCH_REVIEW")) {
        auto *m=fixture("mela");const auto origin=you.pos(),aim=origin+coord_def(6,0);
        require(m->pos()==origin+coord_def(1,0) || m->move_to_pos(origin+coord_def(1,0)),"Mela dispatch target placement");
        for(const auto &d:std::vector<coord_def>{coord_def(3,0),coord_def(6,0),coord_def(3,1),coord_def(7,0)}) {
            auto mg=mgen_data::hostile_at(MONS_ORC,false,origin+d);mg.flags|=MG_FORCE_PLACE;
            auto *n=create_monster(mg,false);require(n,"Mela dispatch comparison placement");
            n->speed=n->speed_increment=0;n->hit_points=n->max_hit_points=10000;
        }
        const auto stable=signature();
        you.props["holo_mela_heat_preview"]=0;
        holo_visual::capture_invocation("mela",aim,0,std::string(shots)+"/dispatch-before.png",1);
        you.props["holo_mela_dispatch_preview"]=1;you.props["holo_mela_heat_preview"]=3;
        for(int f=0;f<4;++f)holo_visual::capture_invocation("mela",origin,f,std::string(shots)+"/dispatch-activate"+std::to_string(f)+".png",5);
        you.props["holo_mela_breath_preview"]=3;you.props["holo_mela_heat_preview"]=0;
        for(int f=0;f<4;++f)holo_visual::capture_invocation("mela",aim,f,std::string(shots)+"/dispatch-beam"+std::to_string(f)+".png",3);
        you.props.erase("holo_mela_breath_preview");
        holo_visual::capture_invocation("mela",origin,1,std::string(shots)+"/dispatch-empty.png",5);
        you.props["holo_mela_heat_preview"]=1;
        holo_visual::capture_invocation("mela",origin,1,std::string(shots)+"/dispatch-recharge.png",5);
        you.props.erase("holo_mela_dispatch_preview");you.props["holo_mela_heat_preview"]=0;
        holo_visual::capture_invocation("mela",aim,0,std::string(shots)+"/dispatch-ended.png",1);
        you.props.erase("holo_mela_heat_preview");
        require(stable==signature(),"Mela dispatch VFX changed heat/HP/world/RNG");
        std::ofstream(std::string(shots)+"/dispatch.json")<<"{\"status\":\"passed\",\"nativeSDL\":true,\"renderOnly\":true,\"gameplayUnchanged\":true,\"rngStable\":true,\"protectionRadius\":2,\"proposedEnhancedBeamRange\":6,\"heatStages\":[0,3,0,1,0]}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_MELA_BREATH_REVIEW")) {
        auto *m=fixture("mela");const auto origin=you.pos(),aim=origin+coord_def(5,0);
        require(m->pos()==origin+coord_def(1,0) || m->move_to_pos(origin+coord_def(1,0)),"Mela breath near target placement");
        for(const auto &d:std::vector<coord_def>{coord_def(3,0),coord_def(5,0),coord_def(3,1),coord_def(6,0)}) {
            auto mg=mgen_data::hostile_at(MONS_ORC,false,origin+d);mg.flags|=MG_FORCE_PLACE;
            auto *n=create_monster(mg,false);require(n,"Mela breath comparison placement");
            n->speed=n->speed_increment=0;n->hit_points=n->max_hit_points=10000;
        }
        const auto stable=signature();
        for(int heat:std::vector<int>{0,3}) {
            you.props["holo_mela_heat_preview"]=heat;
            holo_visual::capture_invocation("mela",aim,0,std::string(shots)+"/breath-h"+std::to_string(heat)+"-before.png",1);
            you.props["holo_mela_heat_preview"]=0;you.props["holo_mela_breath_preview"]=heat;
            for(int f=0;f<4;++f)holo_visual::capture_invocation("mela",aim,f,std::string(shots)+"/breath-h"+std::to_string(heat)+"-f"+std::to_string(f)+".png",3);
            you.props.erase("holo_mela_breath_preview");
            holo_visual::capture_invocation("mela",aim,0,std::string(shots)+"/breath-h"+std::to_string(heat)+"-ended.png",1);
            require(stable==signature(),"Mela breath VFX changed gameplay/RNG");
        }
        you.props.erase("holo_mela_heat_preview");
        std::ofstream(std::string(shots)+"/breath.json")<<"{\"status\":\"passed\",\"nativeSDL\":true,\"renderOnly\":true,\"gameplayUnchanged\":true,\"rngStable\":true,\"direction\":\"east\",\"width\":1,\"range\":5,\"heatCompared\":[0,3]}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_SUISEI_STARS_REVIEW")) {
        auto *m=fixture("suisei",30);const auto origin=you.pos();
        require(m->move_to_pos(origin+coord_def(2,0)),"Suisei star target placement");
        you.props["holo_suisei_stars_preview"]=true;
        const std::string output(shots);
        holo_visual::capture(output+"/stars0.png");
        for(int count=1;count<=3;++count) {
            const int hp=m->hit_points;
            { command_scope command;bolt beam;beam.name="magic dart";beam.origin_spell=SPELL_MAGIC_DART;
              beam.source=you.pos();beam.target=m->pos();beam.range=5;beam.source_id=you.mid;
              beam.thrower=KILL_YOU;beam.flavour=BEAM_MMISSILE;beam.damage=dice_def(4,20);beam.hit=AUTOMATIC_HIT;
              beam.fire();you.turn_is_over=true;you.time_taken=10; }
            require(m->hit_points<hp && holo_batch::s.resource==count,"Suisei native direct hit did not add one star: expected="+std::to_string(count)+" actual="+std::to_string(holo_batch::s.resource)+" damage="+std::to_string(hp-m->hit_points)+" god="+std::to_string(int(holo_batch::s.god))+" piety="+std::to_string(int(you.piety)));
            int sx=1,sy=1;
            require(holo_visual::invocation_sprite_at(m->pos(),sx,sy)==holo_visual::effect(int(holo_visual::effect::suiseistars1)+count-1),"Suisei displayed star count mismatch");
            const auto before=signature();holo_visual::capture(output+"/stars"+std::to_string(count)+".png");
            require(before==signature(),"Suisei stars render changed world/resources/RNG");
        }
        roundtrip();require(holo_batch::s.resource==3,"Suisei native stacks roundtrip");
        require(m->move_to_pos(origin+coord_def(3,0)),"Suisei moving marked target placement");
        int sx=1,sy=1;
        require(holo_visual::invocation_sprite_at(m->pos(),sx,sy)==holo_visual::effect::suiseistars3,"Suisei stars did not follow target");
        require(holo_visual::invocation_sprite_at(origin+coord_def(2,0),sx,sy)==holo_visual::effect::none,"Suisei stale marker left behind");
        holo_visual::capture(output+"/stars3-moved.png");
        holo_batch::s.one_end=you.elapsed_time;
        require(holo_visual::invocation_sprite_at(m->pos(),sx,sy)!=holo_visual::effect::suiseistars3,"Suisei expired count visible");
        holo_visual::capture(output+"/stars-expired.png");
        you.props.erase("holo_suisei_stars_preview");
        std::ofstream(output+"/stars.json")<<"{\"status\":\"passed\",\"nativeSDL\":true,\"realDirectHitStacks\":[1,2,3],\"renderRngAndWorldStable\":true,\"followsTarget\":true,\"expires\":true,\"stackSaveRoundtrip\":true,\"combatCapChanged\":false,\"runtimeDeployed\":false}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_MELA_ONIBI_REVIEW")) {
        auto *m=fixture("mela");const auto aim=you.pos()+coord_def(2,0);
        require(m->move_to_pos(aim),"Mela onibi target placement");
        const auto stable=signature();const int hp=m->hit_points;
        for(int heat:std::vector<int>{0,1,3}) {
            you.props["holo_mela_heat_preview"]=heat;
            holo_visual::capture_invocation("mela",aim,0,std::string(shots)+"/onibi-heat"+std::to_string(heat)+".png",1);
        }
        you.props["holo_mela_heat_preview"]=2;you.props["holo_mela_hit_preview"]=1;
        for(int f=0;f<4;++f)holo_visual::capture_invocation("mela",aim,f,std::string(shots)+"/onibi-hit"+std::to_string(f)+".png",1);
        you.props.erase("holo_mela_hit_preview");
        holo_visual::capture_invocation("mela",aim,0,std::string(shots)+"/onibi-after.png",1);
        you.props.erase("holo_mela_heat_preview");
        require(stable==signature() && hp==m->hit_points,"Mela onibi VFX changed heat/world/HP/RNG");
        std::ofstream(std::string(shots)+"/onibi.json")<<"{\"status\":\"passed\",\"nativeSDL\":true,\"renderOnly\":true,\"gameplayUnchanged\":true,\"rngStable\":true,\"heatStages\":[0,1,3,2],\"targetHpUnchanged\":true}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_SOPIA_TEACHER_REVIEW")) {
        auto *m=fixture("sopia");const auto origin=you.pos();
        require(m->move_to_pos(origin+coord_def(2,0)),"Sopia teacher comparison target placement");
        const auto stable=signature();const int mp=you.magic_points,hp=m->hit_points;
        you.props["holo_sopia_teacher_preview"]=-1;holo_visual::capture(std::string(shots)+"/teacher-before.png");
        for(int phase=0;phase<2;++phase) {
            you.props["holo_sopia_teacher_preview"]=phase;
            for(int f=0;f<4;++f)holo_visual::capture_invocation("sopia",origin,f,std::string(shots)+"/teacher-"+(phase==0?"mana":"book")+std::to_string(f)+".png",1);
            you.props["holo_sopia_teacher_preview"]=-1;
            holo_visual::capture(std::string(shots)+"/teacher-"+(phase==0?"mana":"book")+"-ended.png");
            require(stable==signature() && mp==you.magic_points && hp==m->hit_points,"Sopia teacher VFX changed MP/world/RNG");
        }
        you.props.erase("holo_sopia_teacher_preview");
        std::ofstream(std::string(shots)+"/teacher.json")<<"{\"status\":\"passed\",\"nativeSDL\":true,\"renderOnly\":true,\"gameplayUnchanged\":true,\"rngStable\":true,\"mpUnchanged\":true,\"spellGiftNotApplied\":true}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_SOPIA_BIGBANG_REVIEW")) {
        auto *m=fixture("sopia");const auto centre=you.pos()+coord_def(3,0);
        require(m->move_to_pos(centre+coord_def(1,0)),"Sopia Big Bang target placement");
        for(const auto &d:std::vector<coord_def>{coord_def(-2,1),coord_def(3,2),coord_def(4,0)}) {
            auto mg=mgen_data::hostile_at(MONS_ORC,false,centre+d);mg.flags|=MG_FORCE_PLACE;
            auto *n=create_monster(mg,false);require(n,"Sopia Big Bang comparison placement");
            n->speed=n->speed_increment=0;n->hit_points=n->max_hit_points=10000;
        }
        const auto stable=signature();
        for(int radius=2;radius<=3;++radius) {
            you.props["holo_sopia_gravity_preview"]=radius;
            for(int phase=0;phase<=4;++phase) {
                you.props["holo_sopia_bigbang_preview"]=phase;
                for(int f=0;f<4;++f)holo_visual::capture_invocation("sopia",centre,f,std::string(shots)+"/bigbang-r"+std::to_string(radius)+"-c"+std::to_string(phase)+"-f"+std::to_string(f)+".png",5);
                require(stable==signature(),"Sopia Big Bang VFX changed world/RNG");
            }
            you.props.erase("holo_sopia_bigbang_preview");you.props.erase("holo_sopia_gravity_preview");
            holo_visual::capture(std::string(shots)+"/bigbang-r"+std::to_string(radius)+"-ended.png");
        }
        require(stable==signature(),"Sopia Big Bang fixture state changed");
        std::ofstream(std::string(shots)+"/bigbang.json")<<"{\"status\":\"passed\",\"nativeSDL\":true,\"renderOnly\":true,\"gameplayUnchanged\":true,\"rngStable\":true,\"chargeStages\":[0,1,2,3],\"fieldRadii\":[2,3],\"burstRadius\":2}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_SOPIA_GRAVITY_REVIEW")) {
        auto *m=fixture("sopia");const auto centre=you.pos()+coord_def(3,0);
        require(m->move_to_pos(centre+coord_def(1,0)),"Sopia core neighbour");
        for(const auto &d:std::vector<coord_def>{coord_def(-2,1),coord_def(3,2),coord_def(4,0)}) {
            auto mg=mgen_data::hostile_at(MONS_ORC,false,centre+d);mg.flags|=MG_FORCE_PLACE;
            auto *n=create_monster(mg,false);require(n,"Sopia range comparison placement");
            n->speed=n->speed_increment=0;n->hit_points=n->max_hit_points=10000;
        }
        const auto stable=signature();
        for(int radius=1;radius<=3;++radius) {
            you.props["holo_sopia_gravity_preview"]=radius;
            for(int f=0;f<4;++f)holo_visual::capture_invocation("sopia",centre,f,std::string(shots)+"/gravity-r"+std::to_string(radius)+"-f"+std::to_string(f)+".png",3);
            require(stable==signature(),"Sopia gravity VFX changed world/RNG");
        }
        you.props.erase("holo_sopia_gravity_preview");
        require(stable==signature(),"Sopia gravity fixture state changed");
        std::ofstream(std::string(shots)+"/gravity.json")<<"{\"status\":\"passed\",\"nativeSDL\":true,\"renderOnly\":true,\"gameplayUnchanged\":true,\"rngStable\":true,\"radii\":[1,2,3]}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_VIVI_FINALE_REVIEW")) {
        auto *m=fixture("vivi");const auto origin=you.pos(),aim=origin+coord_def(3,0);
        require(m->move_to_pos(aim),"Vivi finale central placement");
        auto enemy=[&](const coord_def &p){auto mg=mgen_data::hostile_at(MONS_ORC,false,p);mg.flags|=MG_FORCE_PLACE;auto *n=create_monster(mg,false);require(n,"Vivi finale neighbour placement");n->speed=n->speed_increment=0;n->hit_points=n->max_hit_points=10000;return n;};
        auto *near=enemy(aim+coord_def(0,1)),*outside=enemy(aim+coord_def(0,2));
        const int hp=m->hit_points,near_hp=near->hit_points,out_hp=outside->hit_points;const auto stable=signature();
        you.props["holo_vivi_vfx_preview"]=0;holo_visual::capture(std::string(shots)+"/finale-before.png");
        for(int phase=0;phase<4;++phase) {
            you.props["holo_vivi_finale_preview"]=phase;
            const std::string name=phase==0?"cast":phase==1?"mark":phase==2?"spell":"burst";
            for(int f=0;f<(phase==3?6:2);++f)holo_visual::capture_invocation("vivi",aim,f,std::string(shots)+"/finale-"+name+std::to_string(f)+".png",5);
            require(stable==signature(),"Vivi finale capture changed gameplay/RNG");
        }
        you.props.erase("holo_vivi_finale_preview");holo_visual::capture(std::string(shots)+"/finale-ended.png");you.props.erase("holo_vivi_vfx_preview");
        require(stable==signature() && m->hit_points==hp && near->hit_points==near_hp && outside->hit_points==out_hp,"Vivi finale staged visuals dealt damage");
        std::ofstream(std::string(shots)+"/finale.json")<<"{\"status\":\"passed\",\"nativeSDL\":true,\"stagedVisualPreview\":true,\"stages\":[\"cast\",\"marked\",\"second-hit\",\"surrounding-burst\",\"ended\"],\"combatChanged\":false,\"rngStable\":true,\"targetHpUnchanged\":true,\"previewFlagsRemoved\":true}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_VIVI_ENCORE_REVIEW")) {
        auto *m=fixture("vivi",100);const auto origin=you.pos(),aim=origin+coord_def(3,0);
        require(m->move_to_pos(aim),"Vivi encore concept placement");
        const auto stable=signature();const int hp=m->hit_points;
        you.props["holo_vivi_vfx_preview"]=3;holo_visual::capture(std::string(shots)+"/encore-stacks.png");
        you.props["holo_vivi_vfx_preview"]=0;
        for(int phase=0;phase<3;++phase) {
            you.props["holo_vivi_encore_preview"]=phase;
            const std::string name=phase==0?"ready":phase==1?"spell":"echo";
            for(int f=0;f<(phase==2?3:2);++f)holo_visual::capture_invocation("vivi",aim,f,std::string(shots)+"/encore-"+name+std::to_string(f)+".png",3);
            require(stable==signature(),"Vivi encore visual changed gameplay/RNG");
        }
        you.props.erase("holo_vivi_encore_preview");holo_visual::capture(std::string(shots)+"/encore-ended.png");you.props.erase("holo_vivi_vfx_preview");
        require(stable==signature() && m->hit_points==hp,"Vivi staged encore dealt damage or altered gameplay");
        std::ofstream(std::string(shots)+"/encore.json")<<"{\"status\":\"passed\",\"nativeSDL\":true,\"stagedVisualPreview\":true,\"stages\":[\"stacks\",\"ready\",\"primary-hit\",\"echo-hit\",\"ended\"],\"combatChanged\":false,\"rngStable\":true,\"targetHpUnchanged\":true,\"previewFlagsRemoved\":true}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_VIVI_ATTENTION_REVIEW")) {
        auto *m=fixture("vivi",50);const auto origin=you.pos();
        require(m->pos()==origin+coord_def(1,0) || m->move_to_pos(origin+coord_def(1,0)),"Vivi concept target placement");
        const auto before=signature();
        for(int n=0;n<=3;++n) {
            you.props["holo_vivi_vfx_preview"]=n;
            require(holo_visual::invocation_at(origin)==(n? holo_visual::effect::night_vivi1:holo_visual::effect::none),"Vivi concept stage cue");
            holo_visual::capture(std::string(shots)+"/attention-"+std::to_string(n)+".png");
            require(before==signature(),"Vivi concept screenshot changed gameplay/RNG");
        }
        you.props["holo_vivi_vfx_preview"]=0;holo_visual::capture(std::string(shots)+"/attention-ended.png");
        you.props.erase("holo_vivi_vfx_preview");
        require(before==signature(),"Vivi concept stage cleanup changed gameplay/RNG");
        std::ofstream(std::string(shots)+"/attention.json")<<"{\"status\":\"passed\",\"nativeSDL\":true,\"stagedVisualPreview\":true,\"stages\":[0,1,2,3,0],\"combatChanged\":false,\"rngStable\":true,\"previewFlagRemoved\":true}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_SU_FIVE_REVIEW")) {
        auto *m=fixture("su");const auto origin=you.pos(),natural=origin+coord_def(0,-1);
        for(int x=25;x<=45;++x)for(int y=25;y<=45;++y)env.pgrid(coord_def(x,y))|=FPROP_SEEN_OR_NOEXP;
        you.trapped=false;you.skills[SK_INVOCATIONS]=12;holo_batch::s.inv=12;
        require(m->move_to_pos(origin+coord_def(1,1)),"Su five target placement");
        auto enemy=[&](const coord_def &p){auto mg=mgen_data::hostile_at(MONS_ORC,false,p);mg.flags|=MG_FORCE_PLACE;auto *n=create_monster(mg,false);require(n,"Su five extra target");n->speed=n->speed_increment=0;n->hit_points=n->max_hit_points=10000;return n;};
        auto *near=enemy(origin+coord_def(-1,1)),*outside=enemy(origin+coord_def(4,0));
        grd(natural)=DNGN_SHALLOW_WATER;
        auto shot=[&](const std::string &name){const auto before=signature();holo_visual::capture(std::string(shots)+"/tide-"+name+".png");require(before==signature(),"Su tide capture changed RNG/state");};
        shot("before");const int mp=you.magic_points,faith=you.piety,hp=m->hit_points,near_hp=near->hit_points,out_hp=outside->hit_points;
        require(invoke(5,nullptr,&origin)==10,"Su five invocation");
        const auto stable=signature();for(int f=0;f<2;++f)holo_visual::capture_invocation("su",origin,f,std::string(shots)+"/tide-cast"+std::to_string(f)+".png",5);
        require(stable==signature(),"Su tide activation capture changed RNG/state");step(10);shot("active");
        const int remaining=holo_batch::s.five_end-you.elapsed_time;
        require(remaining==84 && you.magic_points==mp-6 && you.piety==faith-12,"Su five cost/duration");
        require(grd(origin)==DNGN_SHALLOW_WATER && !you.floundering() && player_movement_speed()==10,"Su five field or grace");
        step(10);shot("pulse");require(near->hit_points<near_hp,"Su five water pulse caused no damage");
        you.turn_is_over=false;process_command(CMD_MOVE_LEFT);require(you.turn_is_over && you.pos()==origin+coord_def(-1,0),"Su five native left movement");step(you.time_taken);shot("left");
        require(grd(origin+coord_def(2,0))==DNGN_FLOOR && grd(origin+coord_def(-3,0))==DNGN_SHALLOW_WATER,"Su five field does not follow movement");
        you.turn_is_over=false;process_command(CMD_MOVE_RIGHT);require(you.turn_is_over && you.pos()==origin,"Su five native return movement");step(you.time_taken);shot("return");
        require(outside->hit_points==out_hp,"Su five damaged outside field");
        step(holo_batch::s.five_end-you.elapsed_time);shot("ended");
        require(!holo_batch::five() && grd(origin)==DNGN_FLOOR && grd(natural)==DNGN_SHALLOW_WATER,"Su five expiry/original terrain restoration");
        std::ofstream(std::string(shots)+"/tide.json")<<"{\"status\":\"passed\",\"invocations\":12,\"mpCost\":6,\"pietyCost\":12,\"remainingAfterCastAut\":"<<remaining<<",\"nativeMovement\":true,\"movingField\":true,\"playerGrace\":true,\"outsideUnaffected\":true,\"naturalWaterPreserved\":true,\"expired\":true,\"damageA\":"<<hp-m->hit_points<<",\"damageB\":"<<near_hp-near->hit_points<<"}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_SU_WAVE_REVIEW")) {
        std::ofstream report(std::string(shots)+"/wave.json");report<<"{\"status\":\"passed\",\"scenes\":[";
        for(int wet=0;wet<2;++wet) {
            auto *m=fixture("su",100);const auto origin=you.pos(),aim=origin+coord_def(3,0);
            for(int x=25;x<=45;++x)for(int y=25;y<=45;++y)env.pgrid(coord_def(x,y))|=FPROP_SEEN_OR_NOEXP;
            you.trapped=false;you.skills[SK_INVOCATIONS]=12;holo_batch::s.inv=12;
            if(wet) {
                const auto puddle=origin+coord_def(2,0);require(m->pos()==puddle || m->move_to_pos(puddle),"Su wave puddle target");
                require(you.move_to_pos(origin+coord_def(1,0)),"Su wave puddle setup approach");
                for(int n=0;n<40 && grd(puddle)==DNGN_FLOOR;++n){bool hit=false;fight_melee(&you,m,&hit);finish_attack();step(std::max(1,you.time_taken));}
                require(grd(puddle)==DNGN_SHALLOW_WATER,"Su wave lacks ordinary-attack puddle");
                require(you.move_to_pos(origin),"Su wave puddle setup return");
            }
            require(m->move_to_pos(aim),"Su wave centre target");
            auto enemy=[&](const coord_def &p){auto mg=mgen_data::hostile_at(MONS_ORC,false,p);mg.flags|=MG_FORCE_PLACE;auto *n=create_monster(mg,false);require(n,"Su wave side target");n->speed=n->speed_increment=0;n->hit_points=n->max_hit_points=10000;return n;};
            auto *side=enemy(aim+coord_def(0,1)),*outside=enemy(aim+coord_def(0,2));
            const int hp=m->hit_points,side_hp=side->hit_points,out_hp=outside->hit_points,mp=you.magic_points,faith=you.piety;
            const std::string stem=std::string(shots)+(wet?"/wave-wet":"/wave-dry");
            auto shot=[&](const std::string &name){const auto before=signature();holo_visual::capture(stem+"-"+name+".png");require(before==signature(),"Su wave capture changed RNG/state");};
            shot("before");require(invoke(3,m,&aim)==10,"Su wave invocation");
            const auto stable=signature();for(int f=0;f<5;++f)holo_visual::capture_invocation("su",aim,f,stem+"-cast"+std::to_string(f)+".png",3);
            require(stable==signature(),"Su wave invocation capture changed RNG/state");
            step(10);shot("after");
            require(you.magic_points==mp-3 && you.piety==faith-3,"Su wave costs");
            require(m->pos()==aim+coord_def(1,0),"Su wave centre push");
            require(side->pos()==aim+coord_def(wet?1:0,1),"Su wave dry/wet side footprint");
            require(wet?side->hit_points<side_hp:side->hit_points==side_hp,"Su wave wet/dry side damage");
            require(outside->hit_points==out_hp && outside->pos()==aim+coord_def(0,2),"Su wave damaged outside footprint");
            require(holo_batch::s.three_ready-you.elapsed_time==30,"Su wave cooldown");
            if(wet)report<<",";report<<"{\"water\":"<<(wet?"true":"false")<<",\"mainDamage\":"<<hp-m->hit_points<<",\"sideDamage\":"<<side_hp-side->hit_points<<",\"push\":1,\"mpCost\":3,\"pietyCost\":3,\"cooldownAfterCastAut\":30}";
        }
        report<<"],\"nativePuddleTrigger\":true,\"outsideUnaffected\":true,\"captureRngStable\":true}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_SU_WATER_REVIEW")) {
        auto *m=fixture("su",50);const auto origin=you.pos(),p=origin+coord_def(1,0);
        for(int x=25;x<=45;++x)for(int y=25;y<=45;++y)env.pgrid(coord_def(x,y))|=FPROP_SEEN_OR_NOEXP;
        you.trapped=false;you.skills[SK_INVOCATIONS]=12;holo_batch::s.inv=12;
        m->type=MONS_ORC;require(m->pos()==p || m->move_to_pos(p),"Su target placement");
        auto shot=[&](const std::string &name){holo_visual::capture(std::string(shots)+"/water-"+name+".png");};
        shot("before");
        for(int n=0;n<40 && grd(p)==DNGN_FLOOR;++n){bool hit=false;fight_melee(&you,m,&hit);finish_attack();step(std::max(1,you.time_taken));}
        require(grd(p)==DNGN_SHALLOW_WATER && m->floundering(),"Su ordinary attack did not produce native floundering terrain");
        require(holo_batch::monster_energy(*m,EUT_MOVE,10)==10,"Su double-counts native water movement");
        shot("hit");int enemy_fumbles=0;for(int n=0;n<256;++n)enemy_fumbles+=m->fumbles_attack();
        require(enemy_fumbles>0 && enemy_fumbles<256,"Su water does not use native monster fumbles");
        require(m->move_to_pos(origin+coord_def(2,1)),"Su target leaves water");shot("water");
        const int dry_speed=player_movement_speed();
        require(you.move_to_pos(p),"Su player enters water");require(!you.floundering() && player_movement_speed()==dry_speed,"Su shallow water immunity lacks movement or stable footing");
        int player_fumbles=0;for(int n=0;n<256;++n)player_fumbles+=you.fumbles_attack();
        require(player_fumbles==0,"Su worshipper fumbles in shallow water");shot("player");
        require(you.move_to_pos(origin),"Su player leaves water");
        // Refresh the same puddle without spending world time, then save both
        // native TAG_LEVEL terrain markers and the campaign ledger.
        holo_batch::begin_attack(*m);holo_batch::note_primary_damage(m,1);holo_batch::end_attack(10);
        const auto prior=Options.save_dir;const bool no_save=Options.no_save;
        save_disk(dir+"/su-water-save");close_save();Options.save_dir=prior;Options.no_save=no_save;
        timeout_terrain_changes(1000);require(grd(p)==DNGN_FLOOR,"Su puddle did not restore original floor");shot("ended");
        // Native water also widens the 3-star wave; 5-star water follows the
        // player and removes only its own marker outside the moving field.
        you.piety=180;const auto natural=origin+coord_def(0,-1);grd(natural)=DNGN_SHALLOW_WATER;
        require(invoke(5,nullptr,&origin)==10,"Su five activation");
        require(grd(origin)==DNGN_SHALLOW_WATER && grd(origin+coord_def(-2,0))==DNGN_SHALLOW_WATER,"Su five field terrain");
        require(you.move_to_pos(origin+coord_def(1,0)),"Su five move");holo_batch::after_move(origin,true);
        require(grd(origin+coord_def(-2,0))==DNGN_FLOOR && grd(origin+coord_def(3,0))==DNGN_SHALLOW_WATER,"Su moving field restoration");
        timeout_terrain_changes(1000);require(grd(origin)==DNGN_FLOOR && grd(natural)==DNGN_SHALLOW_WATER,"Su expiry removed natural water");
        require(you.move_to_pos(natural),"Su natural pool entry");you.piety=0;
        require(!you.floundering() && player_movement_speed()==dry_speed,"Su natural pool or low-piety immunity missing");
        grd(natural)=DNGN_DEEP_WATER;
        require(you.floundering() && player_movement_speed()==dry_speed+6 && !you.can_swim(),"Su shallow grace grants deep-water swimming");
        grd(natural)=DNGN_SHALLOW_WATER;require(holo_worship::renounce(false),"Su immunity departure control");
        require(you.floundering() && player_movement_speed()==dry_speed+6,"Su immunity persists after renouncing");
        int departed_fumbles=0;for(int n=0;n<256;++n)departed_fumbles+=you.fumbles_attack();
        require(departed_fumbles>0 && departed_fumbles<256,"Non-worshipper lost native water fumbles");
        std::ofstream(std::string(shots)+"/water.json")<<"{\"status\":\"passed\",\"nativeMeleeTrigger\":true,\"playerShallowImmunity\":true,\"naturalPoolImmunity\":true,\"lowPietyImmunity\":true,\"deepWaterUnchanged\":true,\"renounceRemovesImmunity\":true,\"monsterPenalty\":true,\"noExtraSlow\":true,\"expiry\":true,\"movingFiveField\":true,\"naturalWaterPreserved\":true}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_HAJIME_FIVE_REVIEW")) {
        auto *m=fixture("hajime");const auto origin=you.pos();
        for(int x=25;x<=45;++x)for(int y=25;y<=45;++y)env.pgrid(coord_def(x,y))|=FPROP_SEEN_OR_NOEXP;
        you.trapped=false;require(m->move_to_pos(origin+coord_def(1,1)),"Hajime five target placement");
        auto enemy=[&](const coord_def &p){auto mg=mgen_data::hostile_at(MONS_ETTIN,false,p);mg.flags|=MG_FORCE_PLACE;auto *n=create_monster(mg,false);require(n,"Hajime five extra target placement");n->speed=n->speed_increment=0;n->hit_points=n->max_hit_points=10000;return n;};
        auto *near=enemy(origin+coord_def(-1,1));auto *outside=enemy(origin+coord_def(3,2));
        auto shot=[&](const std::string &name){const auto stable=signature();holo_visual::capture(std::string(shots)+"/bancho-"+name+".png");require(stable==signature(),"Hajime five capture changed gameplay/RNG");};
        shot("before");const int mp=you.magic_points,piety=you.piety;
        const int aut=invoke(5,nullptr,&origin);require(aut==10 && you.magic_points==mp-6 && you.piety==piety-12,"Hajime five activation costs differ");
        const auto stable=signature();for(int f=0;f<2;++f)holo_visual::capture_invocation("hajime",origin,f,std::string(shots)+"/bancho-cast"+std::to_string(f)+".png",5);
        require(stable==signature(),"Hajime five invocation capture changed gameplay/RNG");step(aut);shot("active");
        const int remaining=holo_batch::s.five_end-you.elapsed_time;
        require(remaining==60+2*holo_batch::s.inv && holo_batch::s.five_ready-holo_batch::s.five_end==150,"Hajime five duration/cooldown differs");
        const int hp=m->hit_points,near_hp=near->hit_points,out_hp=outside->hit_points;step(10);
        require(m->hit_points==hp && near->hit_points==near_hp,"Hajime five dealt damage while waiting");shot("wait");
        std::ofstream events(std::string(shots)+"/movement.json");events<<"[";
        const command_type moves[]={CMD_MOVE_RIGHT,CMD_MOVE_LEFT,CMD_MOVE_UP,CMD_MOVE_DOWN};
        for(int i=0;i<4;++i){
            const auto old=you.pos();const int a=m->hit_points,b=near->hit_points;
            you.turn_is_over=false;process_command(moves[i]);require(you.turn_is_over && you.pos()!=old,"Hajime five native movement failed");
            step(you.time_taken);shot("move"+std::to_string(i+1));
            require(outside->hit_points==out_hp,"Hajime five damaged outside adjacent range");
            if(i)events<<",";events<<"{\"move\":"<<i+1<<",\"targetA\":"<<a-m->hit_points<<",\"targetB\":"<<b-near->hit_points<<"}";
        }
        events<<"]\n";
        require(hp-m->hit_points+near_hp-near->hit_points>0,"Hajime five native movement caused no damage");
        step(holo_batch::s.five_end-you.elapsed_time);shot("ended");require(!holo_batch::five(),"Hajime five did not expire");
        std::ofstream(std::string(shots)+"/bancho.json")<<"{\"status\":\"passed\",\"nativeMovementCommands\":true,\"moveCount\":4,\"invocations\":"<<holo_batch::s.inv<<",\"mpCost\":6,\"pietyCost\":12,\"remainingAfterCastAut\":"<<remaining<<",\"waitDoesNotDamage\":true,\"outsideRangePreserved\":true,\"damageA\":"<<hp-m->hit_points<<",\"damageB\":"<<near_hp-near->hit_points<<",\"expired\":true}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_HAJIME_DIVE_REVIEW")) {
        auto *m=fixture("hajime",100);const auto origin=you.pos();
        for(int x=25;x<=45;++x)for(int y=25;y<=45;++y)env.pgrid(coord_def(x,y))|=FPROP_SEEN_OR_NOEXP;
        you.trapped=false;require(m->move_to_pos(origin+coord_def(3,0)),"Hajime dive target placement");
        holo_batch::s.resource=3;holo_batch::s.one_end=you.elapsed_time+30;
        auto shot=[&](const std::string &name){const auto stable=signature();holo_visual::capture(std::string(shots)+"/dive-"+name+".png");require(stable==signature(),"Hajime dive screenshot changed gameplay/RNG");};
        shot("before");
        const int now=you.elapsed_time,mp=you.magic_points,piety=you.piety,hp=m->hit_points;
        const auto aim=m->pos();const int aut=invoke(3,m,&aim);
        require(aut==10 && you.pos()==origin+coord_def(2,0) && adjacent(you.pos(),m->pos()),"Hajime dive failed two-cell native movement");
        require(you.magic_points==mp-3 && you.piety==piety-3 && holo_batch::s.resource==0,"Hajime dive costs/rhythm consumption differ");
        require(holo_batch::s.three_ready-now==40,"Hajime dive cooldown differs");
        const auto stable=signature();
        for(int f=0;f<2;++f)holo_visual::capture_invocation("hajime",aim,f,std::string(shots)+"/dive-cast"+std::to_string(f)+".png",3);
        require(stable==signature(),"Hajime dive invocation capture changed gameplay/RNG");
        step(aut);shot("after");
        std::ofstream(std::string(shots)+"/dive.json")<<"{\"status\":\"passed\",\"nativeAbility\":true,\"startTargetDistance\":3,\"cellsMoved\":2,\"rhythmBefore\":3,\"rhythmAfter\":0,\"mpCost\":3,\"pietyCost\":3,\"costAut\":10,\"cooldownAfterCastAut\":30,\"invocations\":"<<holo_batch::s.inv<<",\"damage\":"<<hp-m->hit_points<<",\"continuousTravelAnimation\":false,\"captureStateRngUnchanged\":true}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_HAJIME_RHYTHM_REVIEW")) {
        auto *m=fixture("hajime",50);const auto origin=you.pos();
        // Already-explored choreography room, matching other movement reviews.
        // Native campaign exploration trap rules are unchanged.
        for(int x=25;x<=45;++x)for(int y=25;y<=45;++y)env.pgrid(coord_def(x,y))|=FPROP_SEEN_OR_NOEXP;
        you.trapped=false;
        set_skill_level(SK_INVOCATIONS,12);advance();
        require(m->move_to_pos(origin+coord_def(1,1)),"Hajime rhythm target placement");
        auto shot=[&](const std::string &name){const auto stable=signature();holo_visual::capture(std::string(shots)+"/rhythm-"+name+".png");require(stable==signature(),"Hajime rhythm screenshot changed gameplay/RNG");};
        require(holo_batch::s.resource==0,"Hajime rhythm fixture starts charged");shot("0");
        const int mp=you.magic_points,piety=you.piety;
        const command_type commands[]={CMD_MOVE_RIGHT,CMD_MOVE_LEFT,CMD_MOVE_RIGHT};
        std::vector<int> tiles_seen;
        for(int i=0;i<3;++i) {
            const auto old=you.pos();you.turn_is_over=false;process_command(commands[i]);
            require(you.turn_is_over && you.pos()!=old,"Hajime ordinary move failed");
            std::ofstream(std::string(shots)+"/movement.log",std::ios::app)<<i<<" before step rhythm="<<holo_batch::s.resource<<" now="<<you.elapsed_time<<" end="<<holo_batch::s.one_end<<" moveAut="<<you.time_taken<<" player="<<you.pos().x<<","<<you.pos().y<<" enemy="<<m->pos().x<<","<<m->pos().y<<"\n";
            step(you.time_taken);
            require(holo_batch::s.resource==i+1,"Hajime ordinary movement expected "+std::to_string(i+1)+" rhythm, got "+std::to_string(holo_batch::s.resource)+" now="+std::to_string(you.elapsed_time)+" end="+std::to_string(holo_batch::s.one_end));
#ifdef USE_TILE
            const int tile=holo_visual::effect_tile(holo_visual::effect::night_hajime1);
            require(std::find(tiles_seen.begin(),tiles_seen.end(),tile)==tiles_seen.end(),"Hajime rhythm counts have duplicate sprites");tiles_seen.push_back(tile);
#endif
            shot(std::to_string(i+1));
        }
        require(you.magic_points==mp && you.piety==piety,"Hajime rhythm movement spent MP/piety");
        const int hp=m->hit_points;you.turn_is_over=false;process_command(CMD_MOVE_DOWN);
        require(you.turn_is_over && you.pos()==origin+coord_def(1,0) && holo_batch::s.resource==0,"Hajime native melee attempt did not consume rhythm");
        step(you.time_taken);shot("spent");
        require(holo_visual::invocation_at(you.pos())!=holo_visual::effect::night_hajime1,"Hajime spent rhythm badge persists");
        std::ofstream(std::string(shots)+"/rhythm.json")<<"{\"status\":\"passed\",\"nativeMovementCommands\":true,\"nativeMeleeCommand\":true,\"stacks\":[0,1,2,3,0],\"invocations\":12,\"mpPietyCost\":0,\"attackDamage\":"<<hp-m->hit_points<<",\"captureStateRngUnchanged\":true}\n";
    }
    // Exercise the real damage/AC and shield budgets at low, mid and max Invo.
    for(int I:{0,6,12,18,27})for(bool exhibition:{false,true})for(int option=0;option<3;++option) {
        auto *m=fixture("raden");const auto origin=you.pos();
        require(m->move_to_pos(origin+coord_def(3,0)),"Raden balance target placement");
        auto &rs=holo_batch::s;rs.inv=I;rs.exhibit=option;
        const int now=you.elapsed_time;
        if(exhibition)rs.five_end=now+1000;
        if(option==0){rs.targets[m->mid].paint=3;rs.targets[m->mid].paint_end=now+100;}
        int expected_damage=0;
        if(option<2) {
            const auto saved_rng=rng::generators_to_vector();
            const int raw=option==0?roll_dice(exhibition?3:2,8+I/2)+18:roll_dice(exhibition?4:3,6+I/3)+I/2;
            expected_damage=m->apply_ac(raw);rng::load_generators(saved_rng);
        }
        const int hp=m->hit_points,mp=you.magic_points,piety=you.piety;
        const auto aim=option==2?origin:m->pos();
        require(holo_batch::manual_action(3,m,aim,option)==10,"Raden balanced action unavailable");
        require(you.magic_points==mp-3 && you.piety==piety-3,"Raden balance changed action costs");
        if(option<2) {
            require(hp-m->hit_points==expected_damage,"Raden native damage/AC differs from new scaling");
            if(option==0)require(rs.targets[m->mid].paint==0,"Raden explosion did not consume paint");
            else require(grid_distance(origin,m->pos())==(exhibition?5:4),"Raden push distance changed");
        } else {
            const int shield=exhibition?22+3*I/2:14+I;
            require(rs.shield==shield && rs.three_end-now==10+10*((exhibition?8:6)+I/6),"Raden shield amount/duration scaling differs");
            require(holo_batch::martial_incoming(shield+7,KILLED_BY_MONSTER,m->mid)==7 && rs.shield==0,"Raden shield absorption budget differs");
        }
        require(rs.rest[option]-now==50,"Raden recovery changed");
    }
    std::ofstream(dir+"/raden-balance.json")<<"{\"status\":\"passed\",\"invocations\":[0,6,12,18,27],\"normalAndExhibition\":true,\"nativeDamageAndAC\":true,\"shieldAbsorptionAndDuration\":true,\"costsAndRecoveryUnchanged\":true}\n";
    if(const char *shots=getenv("HOLOCRAWL_RADEN_FIVE_REVIEW")) {
        auto *m=fixture("raden");const auto origin=you.pos();
        require(m->move_to_pos(origin+coord_def(3,0)),"Raden exhibition target placement");
        auto shot=[&](const std::string &name){const auto stable=signature();holo_visual::capture(std::string(shots)+"/exhibition-"+name+".png");require(stable==signature(),"Raden exhibition capture changed gameplay/RNG");};
        shot("before");
        const int now=you.elapsed_time,mp=you.magic_points,piety=you.piety;
        cast("raden",5,nullptr,origin);
        const auto &rs=holo_batch::s;const int I=rs.inv;
        require(you.magic_points==mp-6 && you.piety==piety-12,"Raden exhibition activation costs changed");
        require(rs.five_end-you.elapsed_time==60+2*I && rs.five_ready-rs.five_end==150,"Raden exhibition duration/cooldown changed");
        require(holo_batch::armour()==2+I/9,"Raden exhibition sculpture blessing missing");
        const auto stable=signature();
        for(int f=0;f<4;++f)holo_visual::capture_invocation("raden",origin,f,std::string(shots)+"/exhibition-cast"+std::to_string(f)+".png",5);
        require(stable==signature(),"Raden exhibition invocation capture changed gameplay/RNG");
        int crest_x=0,crest_y=0;
        require(holo_visual::invocation_sprite_at(origin,crest_x,crest_y)==holo_visual::effect::night_raden5 && crest_x==1 && crest_y==1,"Raden exhibition crest is not compact and player anchored");
        const auto ground=holo_visual::at(origin);
        require(std::find(ground.begin(),ground.end(),holo_visual::effect::exhibit)==ground.end(),"Raden retained old separate exhibit decoration");
        shot("active");
        const int remaining=rs.five_end-you.elapsed_time;step(remaining);shot("ended");
        require(!holo_batch::five(),"Raden exhibition did not expire");
        require(holo_visual::invocation_at(origin)==holo_visual::effect::night_raden1,"Raden crest did not return to ordinary exhibit after expiry");
        std::ofstream(std::string(shots)+"/exhibition.json")<<"{\"status\":\"passed\",\"invocations\":"<<I<<",\"remainingAfterCastAut\":"<<remaining<<",\"costAut\":"<<10<<",\"mpCost\":6,\"pietyCost\":12,\"cooldownAfterEndAut\":150,\"expired\":true}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_RADEN_THREE_REVIEW")) {
        for(int option=0;option<3;++option) {
            auto *m=fixture("raden");const auto origin=you.pos();
            require(m->move_to_pos(origin+coord_def(3,0)),"Raden third-star target placement");
            if(option)cast("raden",1,nullptr,origin,option);
            if(option==0){holo_batch::s.targets[m->mid].paint=3;holo_batch::s.targets[m->mid].paint_end=you.elapsed_time+100;}
            const auto aim=option==2?origin:m->pos();
            cast("raden",3,m,aim,option);
            const auto stable=signature();
            for(int f=0;f<(option==1?3:2);++f)
                holo_visual::capture_invocation("raden",aim,f,std::string(shots)+"/raden-tier3-option"+std::to_string(option)+"-review-frame"+std::to_string(f)+".png",3,false,option);
            require(stable==signature(),"Raden third-star capture changed gameplay/RNG");
        }
    }
    if(const char *shots=getenv("HOLOCRAWL_RADEN_REVIEW")) {
        fixture("raden");
        const auto origin=you.pos();
        std::vector<int> exhibit_tiles;
        holo_visual::capture(std::string(shots)+"/raden1-default.png");
        for(int option:{1,2,0}) {
            cast("raden",1,nullptr,origin,option);
            const auto stable=signature();
#ifdef USE_TILE
            const int tile=holo_visual::effect_tile(holo_visual::effect::night_raden1);
            require(std::find(exhibit_tiles.begin(),exhibit_tiles.end(),tile)==exhibit_tiles.end(),"Raden exhibits must have distinct badges");
            exhibit_tiles.push_back(tile);
            require(tile==holo_visual::effect_tile(holo_visual::effect::night_raden1,0)
                && tile==holo_visual::effect_tile(holo_visual::effect::night_raden1,1),"Raden cast and persistent badge differ");
#endif
            for(int f=0;f<2;++f)
                holo_visual::capture_invocation("raden",origin,f,std::string(shots)+"/raden1-"+std::to_string(option)+"-frame"+std::to_string(f)+".png",1,false,option);
            holo_visual::capture(std::string(shots)+"/raden1-"+std::to_string(option)+"-active.png");
            require(stable==signature(),"Raden badge capture changed gameplay/RNG");
        }
        std::ofstream(std::string(shots)+"/raden-badges.json")<<"{\"status\":\"passed\",\"distinctExhibits\":3,\"castAndPersistentMatch\":true,\"gameplayRngUnchanged\":true}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_LAMY_BANQUET_REVIEW")) {
        using namespace holo_batch;
        auto *m=fixture("lamy");const auto origin=you.pos();const auto centre=origin+coord_def(2,0);
        require(m->move_to_pos(centre),"Lamy banquet target placement");
        auto enemy=[&](const coord_def &p){auto mg=mgen_data::hostile_at(MONS_ETTIN,false,p);mg.flags|=MG_FORCE_PLACE;auto *n=create_monster(mg,false);require(n,"Lamy banquet enemy placement");n->speed=n->speed_increment=0;n->hit_points=n->max_hit_points=10000;return n;};
        auto *adj=enemy(centre+coord_def(0,1));auto *outside=enemy(centre+coord_def(2,0));
        auto shot=[&](const char *name){const auto before=signature();holo_visual::capture(std::string(shots)+"/lamy5-"+name+".png");require(before==signature(),"Lamy banquet screenshot mutated state/RNG");};
        auto active=[&](const coord_def &p){int x=1,y=1;return holo_visual::invocation_sprite_at(p-coord_def(1,1),x,y)==holo_visual::effect::lamybanquetactive && x==3 && y==3;};
        s.resource=40;shot("before");const int mp=you.magic_points,faith=you.piety;
        require(invoke(5)==10 && s.resource==0 && you.magic_points==mp-6 && you.piety==faith-12,"Lamy banquet native cost");
        const auto stable=signature();for(int f=0;f<4;++f)holo_visual::capture_invocation("lamy",origin,f,std::string(shots)+"/lamy5-cast"+std::to_string(f)+".png",5);
        require(stable==signature(),"Lamy activation frames changed state/RNG");
        step(10);require(s.five_end-you.elapsed_time==80 && active(you.pos()),"Lamy banquet eight turns and wreath active");shot("active");
        roundtrip();require(active(you.pos()),"Lamy banquet wreath follows saved buff");
        const auto old_pos=you.pos();you.turn_is_over=false;process_command(CMD_MOVE_LEFT);require(you.turn_is_over && you.pos()!=old_pos,"Lamy banquet ordinary movement");step(you.time_taken);
        require(active(you.pos()) && !active(old_pos),"Lamy banquet wreath follows player");shot("moved");
        set_skill_level(SK_CONJURATIONS,27);set_skill_level(SK_SPELLCASTING,27);you.duration[DUR_BRILLIANCE]=100;
        const int mhp=m->hit_points,ahp=adj->hit_points,ohp=outside->hit_points,procs=s.totals.procs;
        shot("hit-before");you.prev_targ=m->mindex();macro_buf_add_cmd(CMD_TARGET_SELECT);
        require(your_spells(SPELL_MAGIC_DART,40,true)==spret::success,"Lamy banquet real spell hit");
        require(s.totals.procs==procs+1 && m->hit_points<mhp && adj->hit_points<ahp && outside->hit_points==ohp,"Lamy banquet true 3x3 centre/splash/outside");
        require(s.targets[m->mid].stacks==1 && s.targets[adj->mid].stacks==1,"Lamy banquet chill dedup preserved");shot("hit-after");step(10);
        // Actual wand route drives the same target-centred rendering callback.
        set_skill_level(SK_EVOCATIONS,27);auto &wand=you.inv[20];wand=item_def();wand.base_type=OBJ_WANDS;wand.sub_type=WAND_FLAME;wand.quantity=1;wand.charges=20;wand.link=20;wand.pos=ITEM_IN_INVENTORY;wand.flags|=ISFLAG_IDENT_MASK;
        const int before_tool=s.totals.procs;shot("tool-before");
        for(int attempt=0;attempt<3 && s.totals.procs==before_tool;++attempt){you.prev_targ=m->mindex();macro_buf_add_cmd(CMD_TARGET_SELECT);zap_wand(20);if(s.totals.procs==before_tool)step(10);}
        require(s.totals.procs==before_tool+1,"Lamy banquet actual wand burst");shot("tool-after");
        const int end=s.five_end;step(std::max(1,end-you.elapsed_time));require(!five() && !active(you.pos()),"Lamy banquet wreath expiration");shot("expired");
        // A separate render-only wall control uses the exact same cell filter.
        const auto wall=centre+coord_def(1,-1);grd(wall)=DNGN_ROCK_WALL;invalidate_los();shot("wall-before");
        const auto control=signature();holo_visual::lamy_banquet_burst(centre);require(control==signature(),"Lamy blocked render control mutated state");
        grd(wall)=DNGN_FLOOR;invalidate_los();
        std::ofstream(dir+"/lamy-banquet-vfx.json")<<"{\"status\":\"passed\",\"nativeActivation\":true,\"durationTurns\":8,\"playerFollowingWreath\":true,\"nativeMovement\":true,\"savedBuff\":true,\"actualSpellBurst\":true,\"actualWandBurst\":true,\"centreAndAdjacentDamaged\":true,\"outsideUnchanged\":true,\"chillDedup\":true,\"wreathExpired\":true,\"renderingStateUnchanged\":true,\"wallControlCaptured\":true}\n";
    }
    // Approved extension: real tool use and saved per-use cloud attribution.
    {
        using namespace holo_batch;
        auto *m=fixture("lamy");s.resource=40;const auto origin=you.pos();
        require(m->move_to_pos(origin+coord_def(2,0)),"Lamy tools target position");
        set_skill_level(SK_EVOCATIONS,27);
        auto &wand=you.inv[20];wand=item_def();wand.base_type=OBJ_WANDS;wand.sub_type=WAND_FLAME;wand.quantity=1;wand.charges=30;wand.link=20;wand.pos=ITEM_IN_INVENTORY;wand.flags|=ISFLAG_IDENT_MASK;
        // Native targeting consumes an explicit select command, not a test-only hit.
        holo_visual::capture(dir+"/lamy-tools-target.png");
        int attempts=0;
        while(s.targets[m->mid].stacks==0 && attempts++<12) {
            const int charges=wand.charges;macro_buf_add_cmd(CMD_TARGET_SELECT);zap_wand(20);
            require(wand.charges==charges-1,"Lamy native wand charge consumption");
        }
        require(s.targets[m->mid].stacks==1,"Lamy actual flame wand failed to chill");
        if(const char *shots=getenv("HOLOCRAWL_LAMY_TOOL_REVIEW"))holo_visual::capture(std::string(shots)+"/wand-stack.png");
        // The miscellaneous item path (lamp beams) does not call your_spells.
        m=fixture("lamy");s.resource=40;require(m->move_to_pos(you.pos()+coord_def(2,0)),"Lamy lamp target position");set_skill_level(SK_EVOCATIONS,27);
        auto &lamp=you.inv[21];lamp=item_def();lamp.base_type=OBJ_MISCELLANY;lamp.sub_type=MISC_LAMP_OF_FIRE;lamp.quantity=1;lamp.link=21;lamp.pos=ITEM_IN_INVENTORY;lamp.flags|=ISFLAG_IDENT_MASK;
        holo_visual::capture(dir+"/lamy-lamp-target.png");
        for(int trial=0;trial<8 && s.targets[m->mid].stacks==0;++trial) {
            evoker_debt(MISC_LAMP_OF_FIRE)=0;macro_buf_add_cmd(CMD_TARGET_SELECT);
            const int hp=m->hit_points;const bool worked=evoke_item(21);
            std::ofstream(dir+"/lamp-trials.log",std::ios::app)<<trial<<" worked="<<worked<<" damage="<<hp-m->hit_points<<" stacks="<<s.targets[m->mid].stacks<<"\n";
            require(worked,"Lamy actual lamp action failed");
        }
        require(s.targets[m->mid].stacks==1,"Lamy actual lamp direct multi-beam dedup");
        if(const char *shots=getenv("HOLOCRAWL_LAMY_TOOL_REVIEW"))holo_visual::capture(std::string(shots)+"/lamp-stack.png");
        // A direct hit plus its cloud field is one use, not two stacks.
        m=fixture("lamy");s.resource=40;const auto mid=m->mid;const auto p=m->pos();
        {holo_lamy::spell_scope tool(SPELL_NO_SPELL,false,true);m->hurt(&you,1,BEAM_FIRE,KILLED_BY_BEAM);place_cloud(CLOUD_FIRE,p,100,&you,0);place_cloud(CLOUD_FIRE,p+coord_def(1,0),100,&you,0);}
        const int first=holo_lamy::cloud_use(p);require(first>0 && holo_lamy::cloud_use(p+coord_def(1,0))==first,"Lamy cloud field use identity");
        require(s.targets[mid].stacks==1 && actor_apply_cloud(m)>0 && s.targets[mid].stacks==1,"Lamy direct and cloud double stack");
        require(m->move_to_pos(p+coord_def(1,0)),"Lamy cloud cross-cell move");actor_apply_cloud(m);require(s.targets[mid].stacks==1,"Lamy crossing same cloud field repeats");
        const auto moved=p+coord_def(0,1);move_cloud(p,moved);require(holo_lamy::cloud_use(moved)==first && holo_lamy::cloud_use(p)==0,"Lamy native cloud move identity");
        for(int i=0;i<3;++i)actor_apply_cloud(m);require(s.targets[mid].stacks==1,"Lamy lingering cloud repeats");
        delete_all_clouds();
        for(int cast=2;cast<=3;++cast) {
            {holo_lamy::spell_scope spell(SPELL_CONJURE_FLAME,true);place_cloud(CLOUD_FIRE,m->pos(),100,&you,0);}
            require(holo_lamy::cloud_use(m->pos())!=first,"Lamy separate cloud recast identity");
            actor_apply_cloud(m);require(s.targets[mid].stacks==cast%3,"Lamy separate cloud casts stack/explode");delete_all_clouds();
        }
        // Native spread copies are grouped, including clouds turned into steam.
        m=fixture("lamy");s.resource=40;
        {holo_lamy::spell_scope spell(SPELL_FREEZING_CLOUD,true);place_cloud(CLOUD_COLD,m->pos(),100,&you,100);}
        const int spread=holo_lamy::cloud_use(m->pos());manage_clouds();
        require(env.cloud.size()>1,"Lamy native spread fixture");
        for(const auto &entry:env.cloud)require(holo_lamy::cloud_use(entry.first)==spread,"Lamy spread split use identity");
        actor_apply_cloud(m);require(s.targets[m->mid].stacks==1,"Lamy damaging cold cloud first tick");
        if(const char *shots=getenv("HOLOCRAWL_LAMY_TOOL_REVIEW"))holo_visual::capture(std::string(shots)+"/cloud-stack.png");
        // Zero damage, other owners, pets/divine and sober states remain excluded.
        delete_all_clouds();m->type=MONS_ICE_BEAST;s.targets.clear();
        {holo_lamy::spell_scope spell(SPELL_FREEZING_CLOUD,true);place_cloud(CLOUD_COLD,m->pos(),100,&you,0);}
        require(actor_apply_cloud(m)==0 && s.targets.empty(),"Lamy immune cloud grants chill");
        delete_all_clouds();m=fixture("lamy");s.resource=40;
        {holo_lamy::spell_scope tool(SPELL_NO_SPELL,false,true);place_cloud(CLOUD_FIRE,m->pos(),100,m,0);}
        actor_apply_cloud(m);require(s.targets.empty() && holo_lamy::cloud_use(m->pos())==0,"Lamy enemy cloud attribution");
        delete_all_clouds();
        {holo_lamy::spell_scope tool(SPELL_NO_SPELL,false,true);damage_scope god(false);place_cloud(CLOUD_FIRE,m->pos(),100,&you,0);m->hurt(&you,1,BEAM_FIRE);}
        actor_apply_cloud(m);require(s.targets.empty() && holo_lamy::cloud_use(m->pos())==0,"Lamy divine cloud attribution");
        delete_all_clouds();s.resource=19;
        {holo_lamy::spell_scope tool(SPELL_NO_SPELL,false,true);m->hurt(&you,1,BEAM_FIRE);place_cloud(CLOUD_FIRE,m->pos(),100,&you,0);}
        actor_apply_cloud(m);require(s.targets.empty(),"Lamy sober tool/cloud chill");
        // Banquet cloud first-hit qualifies once for the entire cloud use.
        delete_all_clouds();s.resource=40;require(invoke(5)==10,"Lamy tools banquet activation");step(10);
        auto mg=mgen_data::hostile_at(MONS_ETTIN,false,m->pos()+coord_def(1,0));mg.flags|=MG_FORCE_PLACE;
        auto *adj=create_monster(mg,false);require(adj,"Lamy cloud banquet neighbour setup");adj->speed=adj->speed_increment=0;adj->hit_points=adj->max_hit_points=10000;
        {holo_lamy::spell_scope tool(SPELL_NO_SPELL,false,true);place_cloud(CLOUD_FIRE,m->pos(),100,&you,0);place_cloud(CLOUD_FIRE,adj->pos(),100,&you,0);}
        const int procs=s.totals.procs;actor_apply_cloud(m);require(s.totals.procs==procs+1,"Lamy banquet cloud first proc");
        require(s.targets[adj->mid].stacks==1,"Lamy banquet cloud neighbour initial chill");actor_apply_cloud(adj);
        require(s.targets[adj->mid].stacks==1,"Lamy banquet splash and later cloud double chill");
        you.elapsed_time+=10;actor_apply_cloud(m);require(s.totals.procs==procs+1,"Lamy banquet repeated cloud proc");
        // A dedicated native level save proves provenance and consumed hits persist.
        delete_all_clouds();m=fixture("lamy");s.resource=40;
        {holo_lamy::spell_scope spell(SPELL_CONJURE_FLAME,true);place_cloud(CLOUD_FIRE,m->pos(),100,&you,0);}
        actor_apply_cloud(m);require(s.targets[m->mid].stacks==1,"Lamy save fixture first tick");
        you.props["lamy_test_mid"]=int(m->mid);you.props["lamy_test_group"]=holo_lamy::cloud_use(m->pos());
        const auto original_save_dir=Options.save_dir;
        save_disk(dir+"/lamy-cloud-save");actor_apply_cloud(m);
        {std::ofstream expected(dir+"/lamy-cloud-expected.txt");expected<<signature();}close_save();Options.save_dir=original_save_dir;
        std::ofstream(dir+"/lamy-tools.json")<<"{\"status\":\"passed\",\"nativeFlameWand\":true,\"nativeLamp\":true,\"wandChargesPaid\":true,\"directCloudDedup\":true,\"cloudCrossCellDedup\":true,\"nativeCloudSpread\":true,\"separateRecastStacks\":true,\"threeStackBurst\":true,\"immuneZeroExcluded\":true,\"enemyDivineSoberExcluded\":true,\"banquetCloudOncePerUse\":true,\"splashLaterCloudDedup\":true,\"nativeCloudSavePrepared\":true}\n";
    }
    // Koyori caster01: true normal casting, per-cast identity and saved state.
    {
        using namespace holo_batch;
        const char *shots=getenv("HOLOCRAWL_KOYORI_CASTER_REVIEW");
        // Native tier3 clips: a saved reagent mark reacts to a real Magic Dart.
        if(shots)for(int index=0;index<3;++index){
            auto *m=fixture("koyori",90);const auto origin=you.pos();
            require(m->move_to_pos(origin+coord_def(2,0)),"Koyori reaction target placement");
            auto mg=mgen_data::hostile_at(MONS_ETTIN,false,m->pos()+coord_def(0,1));mg.flags|=MG_FORCE_PLACE;
            auto *near=create_monster(mg,false);require(near,"Koyori reaction neighbour");
            near->hit_points=near->max_hit_points=10000;near->speed=near->speed_increment=0;
            s.resource=index;const int old[]={1,2,3};s.targets[m->mid].kind=old[index];s.targets[m->mid].expires=you.elapsed_time+60;
            set_skill_level(SK_CONJURATIONS,27);set_skill_level(SK_SPELLCASTING,27);you.duration[DUR_BRILLIANCE]=100;
            require(add_spell_to_memory(SPELL_MAGIC_DART),"Koyori reaction learn dart");
            const std::string stem=std::string(shots)+"/koyori3-"+std::to_string(index);
            holo_visual::capture(stem+"-before.png");const int n=s.totals.procs,hp=near->hit_points;
            // Native dart may deal zero through AC; show the first actual damaging hit.
            for(int attempt=0;attempt<12 && s.totals.procs==n;++attempt){
                holo_visual::capture(stem+"-before.png");
                you.prev_targ=m->mindex();macro_buf_add_cmd(CMD_TARGET_SELECT);
                require(cast_a_spell(false,SPELL_MAGIC_DART),"Koyori reaction true cast");
            }
            require(s.totals.procs==n+1 && s.targets[m->mid].kind==0,"Koyori tier3 reaction consumes mark: procs="+std::to_string(s.totals.procs)+" before="+std::to_string(n)+" kind="+std::to_string(s.targets[m->mid].kind)+" cycle="+std::to_string(s.resource)+" mp="+std::to_string(you.magic_points));
            require(index==0?near->hit_points<hp:index==1?near->hit_points==hp:holo_koyori::movement(*near,100)==135,"Koyori tier3 reaction footprint");
            holo_visual::capture(stem+"-after.png");
        }
        if(const char *five=getenv("HOLOCRAWL_KOYORI_FIVE_REVIEW")){
            auto *target=fixture("koyori",150);const auto origin=you.pos();
            require(target->move_to_pos(origin+coord_def(2,0)),"Koyori five target");
            auto mg=mgen_data::hostile_at(MONS_ETTIN,false,target->pos()+coord_def(0,1));mg.flags|=MG_FORCE_PLACE;
            auto *near=create_monster(mg,false);require(near,"Koyori five neighbour");near->hit_points=near->max_hit_points=10000;near->speed=near->speed_increment=0;
            set_skill_level(SK_CONJURATIONS,27);set_skill_level(SK_SPELLCASTING,27);you.duration[DUR_BRILLIANCE]=100;
            require(add_spell_to_memory(SPELL_MAGIC_DART),"Koyori five learn dart");
            holo_visual::capture(std::string(five)+"/koyori5-before.png");
            const int mp=you.magic_points,faith=you.piety;
            require(invoke(5)==5 && you.magic_points==mp-6 && you.piety==faith-10,"Koyori five activation cost");
            for(int f=0;f<2;++f)holo_visual::capture_invocation("koyori",origin,f,std::string(five)+"/koyori5-activate"+std::to_string(f)+".png",5);
            step(5);require(s.offence==4,"Koyori five four charges");holo_visual::capture(std::string(five)+"/koyori5-ready.png");
            for(int index=0;index<4;++index){
                const auto stem=std::string(five)+"/koyori5-cast"+std::to_string(index);const int count=s.totals.procs;
                for(int attempt=0;attempt<20 && s.totals.procs==count;++attempt){
                    holo_visual::capture(stem+"-before.png");you.prev_targ=target->mindex();macro_buf_add_cmd(CMD_TARGET_SELECT);
                    require(cast_a_spell(false,SPELL_MAGIC_DART),"Koyori five native spell");
                }
                require(s.totals.procs==count+1 && s.offence==3-index,"Koyori five one charge per damaging spell");
                holo_visual::capture(stem+"-after.png");
            }
            require(s.five_end==0 && invoke(5)==0,"Koyori five depletion/cooldown");
            std::ofstream(dir+"/koyori-five-review.json")<<"{\"status\":\"passed\",\"activationMP\":6,\"activationPiety\":10,\"activationAut\":5,\"nativeDamagingSpells\":4,\"chargesConsumed\":4,\"cooldownRetained\":true}\n";
        }
        const int kinds[]={2,3,1};
        for(int index=0;index<3;++index){
            auto *m=fixture("koyori",60);const auto origin=you.pos();
            require(m->move_to_pos(origin+coord_def(2,0)),"Koyori visible spell target");
            s.resource=index;set_skill_level(SK_CONJURATIONS,27);set_skill_level(SK_SPELLCASTING,27);
            you.duration[DUR_BRILLIANCE]=100;require(add_spell_to_memory(SPELL_MAGIC_DART),"Koyori learn native dart");
            const std::string stem=shots?std::string(shots)+"/koyori1-"+std::to_string(index):"";
            if(shots)holo_visual::capture(stem+"-before.png");
            const int mp=you.magic_points,faith=you.piety;
            you.prev_targ=m->mindex();macro_buf_add_cmd(CMD_TARGET_SELECT);
            require(cast_a_spell(false,SPELL_MAGIC_DART),"Koyori normal cast command");
            require(you.magic_points==mp-1 && you.piety==faith,"Koyori passive charges extra MP/piety");
            require(s.resource==(index+1)%3 && s.targets[m->mid].kind==kinds[index],"Koyori cycle/mark from actual spell");
            require(s.targets[m->mid].expires==you.elapsed_time+60,"Koyori six-turn mark");
            const auto stable=signature();if(shots)holo_visual::capture(stem+"-after.png");
            require(stable==signature(),"Koyori rendering changed state/RNG");
            if(index==1)require(holo_koyori::movement(*m,100)==115,"Koyori cold move-only 15 percent");
            if(index==2){
                const int hp=m->hit_points;step(10);require(hp-m->hit_points==3 && s.targets[m->mid].stacks==1,"Koyori poison first tick");
                step(10);require(hp-m->hit_points==6 && s.targets[m->mid].stacks==0,"Koyori poison second tick");
                step(10);require(hp-m->hit_points==6,"Koyori poison extra tick");
            }else step(10);
            if(shots)holo_visual::capture(stem+"-settled.png");
            roundtrip();require(s.resource==(index+1)%3,"Koyori cycle save roundtrip");
        }
        auto *m=fixture("koyori",74);const int base=spell_range(SPELL_FLAME_TONGUE,40,true);
        you.piety=75;require(spell_range(SPELL_FLAME_TONGUE,40,true)==std::min(int(you.current_vision),base+1),"Koyori range +1 at75");
        require(spell_range(SPELL_FLAME_TONGUE,40,false)==base,"Koyori bonus-disabled range");
        require(!holo_koyori::range_bonus(SPELL_BLINK,5) && !holo_koyori::range_bonus(SPELL_FREEZE,1)
            && !holo_koyori::range_bonus(SPELL_OZOCUBUS_REFRIGERATION,7),"Koyori excluded range types");
        require(holo_koyori::reaction_damage(16,3,false)==13 && holo_koyori::reaction_damage(27,5,false)==22
            && holo_koyori::reaction_damage(10,4,false)==8 && holo_koyori::reaction_damage(27,5,true)==34
            && holo_koyori::reaction_damage(16,3,true)==18,"Koyori 85-percent/critical single rounding");
        m=fixture("koyori");
        auto mg=mgen_data::hostile_at(MONS_ETTIN,false,you.pos()+coord_def(1,1));mg.flags|=MG_FORCE_PLACE;
        auto *second=create_monster(mg,false);require(second,"Koyori AoE target");second->hit_points=second->max_hit_points=10000;second->speed=0;
        const auto aim=m->pos();
        {holo_koyori::spell_scope cast(SPELL_FIREBALL,true,aim);m->hurt(&you,1,BEAM_MAGIC);m->hurt(&you,1,BEAM_MAGIC);second->hurt(&you,1,BEAM_MAGIC);}
        require(s.resource==1 && s.targets[m->mid].kind==2 && s.targets[second->mid].kind==2,"Koyori AoE uses same reagent and one cycle");
        const int procs=s.totals.procs;
        {holo_koyori::spell_scope cast(SPELL_FIREBALL,true,aim);m->hurt(&you,1,BEAM_MAGIC);second->hurt(&you,1,BEAM_MAGIC);}
        require(s.totals.procs==procs+1 && s.targets[m->mid].kind==0 && s.targets[second->mid].kind==3,"Koyori one aimed reaction centre per cast");
        const int hp=you.hp;
        s.resource=0;s.targets[m->mid].kind=1;s.targets[m->mid].expires=you.elapsed_time+60;
        {holo_koyori::spell_scope cast(SPELL_MAGIC_DART,true,aim);m->hurt(&you,1,BEAM_MAGIC);}
        require(you.hp==hp,"Koyori reaction hurts self");
        m=fixture("koyori",60);set_skill_level(SK_ICE_MAGIC,27);set_skill_level(SK_SPELLCASTING,27);you.duration[DUR_BRILLIANCE]=100;
        require(your_spells(SPELL_OZOCUBUS_REFRIGERATION,40,true)==spret::success && s.resource==1 && s.targets[m->mid].kind==2,"Koyori true native area spell");
        m=fixture("koyori",60);require(m->move_to_pos(you.pos()+coord_def(4,0)),"Koyori native orb target");
        set_skill_level(SK_CONJURATIONS,27);set_skill_level(SK_SPELLCASTING,27);you.duration[DUR_BRILLIANCE]=100;
        you.prev_targ=m->mindex();macro_buf_add_cmd(CMD_TARGET_SELECT);
        require(your_spells(SPELL_IOOD,80,true)==spret::success,"Koyori delayed orb native cast");
        for(int n=0;n<30 && s.resource==0;++n)step(10);
        require(s.resource==1 && s.targets[m->mid].kind==2,"Koyori direct delayed orb applies exactly one reagent");
        m=fixture("koyori");
        auto immune_mg=mgen_data::hostile_at(MONS_IRON_GOLEM,false,you.pos()+coord_def(2,1));immune_mg.flags|=MG_FORCE_PLACE;
        auto *immune=create_monster(immune_mg,false);require(immune,"Koyori poison immune fixture");immune->hit_points=immune->max_hit_points=10000;immune->speed=0;s.resource=2;
        {holo_koyori::spell_scope cast(SPELL_MAGIC_DART,true,immune->pos());immune->hurt(&you,1,BEAM_MAGIC);}
        require(s.targets[immune->mid].kind==1 && immune->res_poison()>=3,"Koyori immune target retains reagent mark");
        const int immune_hp=immune->hit_points;step(20);require(immune->hit_points==immune_hp,"Koyori poison bypassed immunity");
        auto *ally=fixture("koyori");ally->attitude=ATT_FRIENDLY;
        auto hostile_mg=mgen_data::hostile_at(MONS_ETTIN,false,you.pos()+coord_def(1,1));hostile_mg.flags|=MG_FORCE_PLACE;
        auto *hostile=create_monster(hostile_mg,false);require(hostile,"Koyori friendly splash fixture");hostile->hit_points=hostile->max_hit_points=10000;
        s.targets[hostile->mid].kind=1;s.targets[hostile->mid].expires=you.elapsed_time+60;const int ally_hp=ally->hit_points;
        {holo_koyori::spell_scope cast(SPELL_MAGIC_DART,true,hostile->pos());hostile->hurt(&you,1,BEAM_MAGIC);}
        require(ally->hit_points==ally_hp,"Koyori combustion hurts ally");
        m=fixture("koyori");const int seq=s.resource;
        {holo_koyori::spell_scope cast(SPELL_MAGIC_DART,true,m->pos());m->hurt(&you,0,BEAM_MAGIC);m->hurt(&you,1,BEAM_POISON,KILLED_BY_POISON);m->hurt(&you,1,BEAM_FIRE,KILLED_BY_CLOUD);m->hurt(m,1,BEAM_MAGIC);{damage_scope divine(false);m->hurt(&you,1,BEAM_MAGIC);}}
        {holo_koyori::spell_scope cast(SPELL_MAGIC_DART,false,m->pos());m->hurt(&you,1,BEAM_MAGIC);}
        require(s.resource==seq && s.targets.empty(),"Koyori zero/tool/pet/poison/cloud/divine exclusions");
        m=fixture("koyori");const int mp=you.magic_points,faith=you.piety,now=you.elapsed_time;
        require(invoke(5)==5 && you.magic_points==mp-6 && you.piety==faith-10 && s.offence==4,"Koyori actual critical cost/charges");
        step(5);require(s.five_end-you.elapsed_time==80 && s.five_ready==now+200,"Koyori critical duration/cooldown");
        const int critical_procs=s.totals.procs;
        for(int i=0;i<4;++i){holo_koyori::spell_scope cast(SPELL_MAGIC_DART,true,m->pos());m->hurt(&you,1,BEAM_MAGIC);}
        require(s.offence==0 && s.five_end==0 && s.totals.procs==critical_procs+4 && invoke(5)==0,"Koyori four critical casts and cooldown");
        s.targets[m->mid].root=you.elapsed_time+20;s.targets[m->mid].slowed_until=you.elapsed_time+30;s.targets[m->mid].weak_until=you.elapsed_time+40;
        require(holo_koyori::movement(*m,100)==150,"Koyori strongest slow only");
        m=fixture("koyori");s.resource=2;auto &t=s.targets[m->mid];t.kind=1;t.stacks=2;t.next=you.elapsed_time+10;t.expires=you.elapsed_time+60;
        require(invoke(5)==5,"Koyori saved critical activation");step(5);roundtrip();
        const auto old_save_dir=Options.save_dir;save_disk(dir+"/koyori-save");step(10);
        std::ofstream(dir+"/koyori-expected.txt")<<signature();close_save();Options.save_dir=old_save_dir;
        std::ofstream(dir+"/koyori-caster.json")<<"{\"status\":\"passed\",\"nativeNormalCasting\":true,\"onlyNativeSpellMP\":true,\"threeReagents\":true,\"rangePlusOne\":true,\"reactionScale85\":true,\"oneCentrePerCast\":true,\"criticalCostAndFourCharges\":true,\"poisonTwoTicks\":true,\"saved\":true}\n";
    }
    // Lamy caster redesign: actual damage attribution, costs, saves and HUD.
    {
        using namespace holo_batch;
        auto *m=fixture("lamy");const auto origin=you.pos();
        set_skill_level(SK_CONJURATIONS,12);set_skill_level(SK_FIRE_MAGIC,12);set_skill_level(SK_SPELLCASTING,12);
        s.resource=0;const int base_ev=you.evasion();
        const int base_power=calc_spell_power(SPELL_FIREBALL,true,false,false);
        const char *shots=getenv("HOLOCRAWL_LAMY_CASTER_REVIEW");
        if(shots)holo_visual::capture(std::string(shots)+"/lamy1-before.png");
        const int mp=you.magic_points,faith=you.piety;
        require(invoke(1)==10 && s.resource==40 && you.magic_points==mp-2 && you.piety==faith-1,"Lamy drink actual cost/40 intox");
        require(holo_lamy::power_bonus()==16 && you.evasion()==base_ev,"Lamy proper intox power/EV");
        const int buff_power=calc_spell_power(SPELL_FIREBALL,true,false,false);
        require(base_power>0 && buff_power>base_power && buff_power==base_power*116/100,"Lamy native spell power boost");
        if(shots){for(int f=0;f<2;++f)holo_visual::capture_invocation("lamy",origin,f,std::string(shots)+"/lamy1-cast"+std::to_string(f)+".png",1,false,0);holo_visual::capture(std::string(shots)+"/lamy1-proper.png");}
        step(10);require(s.resource==39,"Lamy one per ordinary turn decay");
        require(invoke(1)==10 && s.resource==79 && you.evasion()==base_ev-3,"Lamy second sip overdoses/EV-3");
        require(calc_spell_power(SPELL_FIREBALL,true,false,false)==buff_power,"Lamy overdose gives no extra power");
        for(int raw=0;raw<=100;++raw)require(spell_failure(raw)==raw,"Lamy retained old failure penalty");
        require(to_hit(&you,m)==0 && multiplier(100)==100 && resistance(BEAM_COLD)==0,"Lamy old physical/resist passives survived");
        if(shots)holo_visual::capture(std::string(shots)+"/lamy1-over.png");
        roundtrip();require(s.resource==79 && holo_lamy::evasion_penalty()==3,"Lamy intox save/restore");
        for(int amount:{0,19,20,69,70,100}){s.resource=amount;require((holo_lamy::power_bonus()>0)==(amount>=20) && (holo_lamy::evasion_penalty()==3)==(amount>=70),"Lamy 20/70 boundary");}
        require(holo_lamy::power(SPELL_FIREBALL,100)==116 && holo_lamy::power(SPELL_BLINK,100)==100 && !holo_lamy::attack_spell(SPELL_FREEZING_CLOUD),"Lamy utility/cloud classifier");
        for(int I:{0,12,27}){s.inv=I;require(holo_lamy::power(SPELL_FIREBALL,100)==112+I/3,"Lamy invocation scaling");}s.inv=12;
        const int magic_cap=spell_power_cap(SPELL_MAGIC_DART);require(calc_spell_power(SPELL_MAGIC_DART,true)<=magic_cap,"Lamy bypasses native spell cap");
        auto hit=[&](monster *victim,int n=1){holo_lamy::spell_scope scope(SPELL_FIREBALL,true);for(int i=0;i<n;++i)victim->hurt(&you,1,BEAM_MAGIC,KILLED_BY_BEAM);};
        m=fixture("lamy");s.resource=40;const mid_t mid=m->mid;
        hit(m,4);require(s.targets[mid].stacks==1,"Lamy multi-hit stacks more than once per cast");
        hit(m);require(s.targets[mid].stacks==2,"Lamy second cast chill");
        const int hp=m->hit_points;hit(m);require(s.targets[mid].stacks==0 && hp-m->hit_points>=3 && hp-m->hit_points<=11,"Lamy third cast 2d5 cold proc");
        require(monster_energy(*m,EUT_MOVE,10)==15 && monster_energy(*m,EUT_ATTACK,10)==10,"Lamy slow must affect movement only");
        roundtrip();m=monster_by_mid(mid);require(s.targets[mid].slowed_until>you.elapsed_time,"Lamy slow save");
        step(20);require(monster_energy(*m,EUT_MOVE,10)==10,"Lamy slow expiry");
        hit(m);step(60);require(s.targets[mid].stacks==0,"Lamy chill expiry6turns");
        m=fixture("lamy");s.resource=40;
        {holo_lamy::spell_scope scope(SPELL_FIREBALL,true);m->hurt(&you,1,BEAM_POISON,KILLED_BY_POISON);m->hurt(&you,1,BEAM_FIRE,KILLED_BY_CLOUD);m->hurt(m,1,BEAM_MAGIC);{damage_scope divine(false);m->hurt(&you,1,BEAM_MAGIC);}}
        require(s.targets.empty(),"Lamy pet/poison/cloud/divine incorrectly proc");
        {holo_lamy::spell_scope scope(SPELL_FIREBALL,false);m->hurt(&you,1,BEAM_MAGIC,KILLED_BY_BEAM);}require(s.targets.empty(),"Lamy evoked/fake spell procs");
        {holo_lamy::spell_scope scope(SPELL_FIREBALL,true);{holo_lamy::spell_scope shadow(SPELL_FIREBALL,false);m->hurt(&you,1,BEAM_MAGIC,KILLED_BY_BEAM);}}require(s.targets.empty(),"Lamy nested fake cast inherited scope");
        // Untargeted native casting exercises the real spl-cast.cc scope.
        set_skill_level(SK_ICE_MAGIC,27);set_skill_level(SK_SPELLCASTING,27);you.duration[DUR_BRILLIANCE]=100;rng::seed(554433);
        const auto native_result=your_spells(SPELL_OZOCUBUS_REFRIGERATION,40,true);
        require(native_result==spret::success,"Lamy native area spell cast result="+std::to_string(int(native_result))+" fail="+std::to_string(raw_spell_fail(SPELL_OZOCUBUS_REFRIGERATION))+" reason="+spell_uselessness_reason(SPELL_OZOCUBUS_REFRIGERATION,true,true,false));
        require(s.targets[m->mid].stacks==1,"Lamy native area spell missing chill");
        m=fixture("lamy");s.resource=40;const int pre_mp=you.magic_points,pre_faith=you.piety;
        require(invoke(3,m,&m->pos())==0,"Lamy tier3 still active skill");
        require(invoke(5)==10 && s.resource==0 && you.magic_points==pre_mp-6 && you.piety==pre_faith-12,"Lamy banquet activation/cost/consume");
        step(10);require(s.five_end-you.elapsed_time==80 && holo_lamy::power_bonus()==16 && holo_lamy::evasion_penalty()==0,"Lamy banquet8turn maintenance");
        const int end=s.five_end,ready=s.five_ready;require(ready==end+150,"Lamy banquet cooldown15turns");roundtrip();m=monster_by_mid(m->mid);
        require(s.five_end==end && s.five_ready==ready,"Lamy banquet save");
        const int procs=s.totals.procs;hit(m,3);require(s.totals.procs==procs+1 && s.targets[m->mid].stacks==1,"Lamy banquet once/cast and direct+burst chill dedup");
        hit(m);require(s.totals.procs==procs+1,"Lamy banquet more than once per turn");
        step(10);hit(m);require(s.totals.procs==procs+2,"Lamy banquet next turn burst missing");
        const int passive_hp=m->hit_points;step(20);require(m->hit_points==passive_hp,"Lamy old passive damage aura remains");
        you.elapsed_time=end;resource_tick(end);require(holo_lamy::power_bonus()==0 && s.resource==0 && invoke(5)==0,"Lamy banquet end/empty/cooldown");
        m=fixture("lamy");require(m->move_to_pos(you.pos()+coord_def(2,0)),"Lamy splash centre setup");
        auto mg=mgen_data::hostile_at(MONS_ETTIN,false,you.pos()+coord_def(2,1));mg.flags|=MG_FORCE_PLACE;
        auto *adj=create_monster(mg,false);require(adj,"Lamy splash neighbour setup");adj->speed=adj->speed_increment=0;adj->hit_points=adj->max_hit_points=1000;
        s.resource=40;require(invoke(5)==10,"Lamy splash banquet activation");step(10);
        const int centre_hp=m->hit_points,adj_hp=adj->hit_points;hit(m);
        const int centre_extra=centre_hp-m->hit_points-1;
        require(centre_extra>=2 && centre_extra<=18 && adj_hp-adj->hit_points==centre_extra/2,"Lamy burst centre2d9 and half splash");
        require(s.targets[m->mid].stacks==1 && s.targets[adj->mid].stacks==1,"Lamy AoE/direct chill dedup");
        fixture("towa");require(holo_lamy::power_bonus()==0 && holo_lamy::power(SPELL_FIREBALL,100)==100 && holo_lamy::evasion_penalty()==0,"Lamy changes other god");
        std::ofstream proof(dir+"/lamy-caster.json");proof<<"{\"status\":\"passed\",\"invocation\":12,\"baseSpellPower\":"<<base_power<<",\"buffSpellPower\":"<<buff_power<<",\"drink\":40,\"overdoseEV\":-3,\"nativeAreaCast\":true,\"perCastDedup\":true,\"dotPetDivineExcluded\":true,\"banquetTurns\":8,\"banquetCooldown\":15,\"saved\":true}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_LAMY_CHILL_REVIEW")) {
        using namespace holo_batch;
        auto *m=fixture("lamy");const mid_t mid=m->mid;const auto origin=you.pos();
        require(m->move_to_pos(origin+coord_def(2,0)),"Lamy chill visible target setup");
        s.resource=40;
        set_skill_level(SK_ICE_MAGIC,27);set_skill_level(SK_SPELLCASTING,27);
        you.duration[DUR_BRILLIANCE]=100;
        auto shot=[&](const char *name){const auto stable=signature();holo_visual::capture(std::string(shots)+"/lamy3-"+name+".png");require(stable==signature(),"Lamy chill capture mutated gameplay/RNG");};
        shot("before");
        for(int i=1;i<=3;++i) {
            require(your_spells(SPELL_OZOCUBUS_REFRIGERATION,40,true)==spret::success,"Lamy chill actual spell");
            require(s.targets[mid].stacks==i%3,"Lamy chill real spell stack progression");
            shot(("cast"+std::to_string(i)).c_str());step(10);
        }
        require(s.targets[mid].slowed_until>you.elapsed_time,"Lamy chill slow active");
        roundtrip();m=monster_by_mid(mid);shot("restored");
        step(20);shot("slow-expired");
        require(holo_visual::invocation_at(m->pos())==holo_visual::effect::none,"Lamy slow marker expiry");
        require(your_spells(SPELL_OZOCUBUS_REFRIGERATION,40,true)==spret::success,"Lamy expiry cast");
        shot("expiry-stack");step(60);shot("stack-expired");
        require(holo_visual::invocation_at(m->pos())==holo_visual::effect::none,"Lamy stack marker expiry");
        fixture("towa");require(holo_visual::invocation_at(you.pos()+coord_def(2,0))==holo_visual::effect::none,"Lamy marker other god");
        std::ofstream(dir+"/lamy-chill-vfx.json")<<"{\"status\":\"passed\",\"realSpellCasts\":4,\"stackProgression\":[1,2,0],\"expiry\":true,\"saveRestore\":true,\"renderingStateUnchanged\":true}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_LAMY_HUD_REVIEW")) {
        fixture("lamy");const int amounts[]={12,40,80,0};const char *names[]={"sober","tipsy","drunk","banquet"};
        const char *labels[]={"Sober 12/100","Tipsy 40/100 P+16%","Drunk 80/100 P+16% EV-3","Banquet 6t P+16%"};
        const int colours[]={LIGHTGREY,LIGHTCYAN,LIGHTRED,LIGHTMAGENTA};
        for(int i=0;i<4;++i) {
            holo_batch::s.resource=amounts[i];holo_batch::s.five_end=i==3?you.elapsed_time+60:0;
            status_info info;require(fill_status_info(STATUS_HOLO_LAMY,info) && info.light_text==labels[i] && info.light_colour==colours[i],"Lamy HUD label/colour");
            const auto before=signature();holo_visual::capture(std::string(shots)+"/lamy-"+names[i]+".png");require(before==signature(),"Lamy HUD rendering mutated gameplay");
        }
        you.elapsed_time+=10;status_info info;require(fill_status_info(STATUS_HOLO_LAMY,info) && info.light_text=="Banquet 5t P+16%","Lamy HUD live countdown");
        fixture("towa");require(!fill_status_info(STATUS_HOLO_LAMY,info),"Lamy status leaked to another god");
        std::ofstream(dir+"/lamy-hud.json")<<"{\"status\":\"passed\",\"states\":4,\"countdown\":true,\"otherGodHidden\":true,\"renderingStateUnchanged\":true,\"combatRedesignApplied\":true}\n";
    }
    if(const char *shots=getenv("HOLOCRAWL_TOWA_CROSSFIRE_REVIEW")) {
        auto *left=fixture("towa");const auto origin=you.pos();
        require(left->move_to_pos(origin+coord_def(-1,-2)),"Crossfire left setup");
        auto mg=mgen_data::hostile_at(MONS_ETTIN,false,origin+coord_def(1,-2));mg.flags|=MG_FORCE_PLACE;
        auto *right=create_monster(mg,false);require(right,"Crossfire right setup");
        for(auto *m:{left,right}){m->speed=0;m->speed_increment=0;m->hit_points=m->max_hit_points=100;}
        require(invoke(3,nullptr,&origin)==10,"Crossfire real tier3 prerequisite");step(10);
        const std::string stem=std::string(shots)+"/crossfire";
        holo_visual::capture(stem+"-before.png");
        require(invoke(5,nullptr,&origin)==5 && holo_batch::s.resource==8,"Crossfire real tier5 activation eight ammo");
        for(int f=0;f<2;++f)holo_visual::capture_invocation("towa",origin,f,stem+"-cast"+std::to_string(f)+".png",5,false,0);
        step(5);holo_visual::capture(stem+"-active.png");
        std::ofstream proof(dir+"/towa-crossfire.json");proof<<"{\"status\":\"passed\",\"tier\":5,\"volleys\":[";
        for(int volley=0;volley<2;++volley) {
            const int before=left->hit_points+right->hit_points,ammo=holo_batch::s.resource;
            int side=-1;for(auto *m:{left,right}) {
                const auto old=m->pos();const auto dest=origin+coord_def(side*(volley==0?2:1),-2);side=1;
                require(m->move_to_pos(dest),"Crossfire enemy movement");holo_batch::after_monster(*m,old);
            }
            you.elapsed_time+=10;rng::seed(99001+volley);holo_batch::space_tick(you.elapsed_time);
            require(holo_batch::s.resource==ammo-2,"Crossfire two native shots in one turn");
            const int damage=before-left->hit_points-right->hit_points;require(damage>0,"Crossfire real HP loss");
            holo_visual::capture(stem+"-after"+std::to_string(volley)+".png");
            if(volley)proof<<",";proof<<"{\"ammoBefore\":"<<ammo<<",\"ammoAfter\":"<<holo_batch::s.resource<<",\"damage\":"<<damage<<"}";
        }
        proof<<"],\"nativeMovementTrigger\":true,\"shotsPerTurn\":2,\"artOnly\":true}\n";
    }
    if(!getenv("HOLOCRAWL_TOWA_CROSSFIRE_REVIEW")) if(const char *shots=getenv("HOLOCRAWL_TOWA_SHOT_REVIEW")) {
        std::ofstream proof(dir+"/towa-support.json");proof<<"{\"status\":\"passed\",\"cases\":[";
        for(int distance=1;distance<=2;++distance) {
            auto *m=fixture("towa");const auto origin=you.pos();
            const bool diagonal=getenv("HOLOCRAWL_TOWA_DIAGONAL_REVIEW");
            const auto initial=origin+coord_def(diagonal?1:(distance==1?0:1),-2),dest=origin+coord_def(diagonal?distance:0,-distance);
            require(m->move_to_pos(initial),"Towa initial enemy position");m->hit_points=m->max_hit_points=40;
            require(invoke(3,nullptr,&origin)==10,"Towa actual covering zone invocation");step(10);
            const std::string stem=std::string(shots)+"/towa-demo-"+std::to_string(distance);
            holo_visual::capture(stem+"-zone.png");
            const auto old=m->pos();require(m->move_to_pos(dest),"Towa enemy one-step movement");holo_batch::after_monster(*m,old);
            require(grid_distance(you.pos(),m->pos())==distance && holo_batch::s.candidates.count(m->mid),"Towa movement registered at requested distance");
            holo_visual::capture(stem+"-moved.png");
            int seed=0;
            for(int trial=1;trial<1000;++trial) {rng::seed(99000+trial);if(holo_batch::roll_hit(*m,22+holo_batch::s.inv) && roll_dice(2,5+holo_batch::s.inv/3)>=12){seed=99000+trial;break;}}
            require(seed,"Towa reproducible hit fixture");rng::seed(seed);
            const int hp=m->hit_points,ammo=holo_batch::s.resource;
            ++you.elapsed_time;holo_batch::space_tick(you.elapsed_time);
            require(holo_batch::s.resource==ammo-1 && m->hit_points<hp,"Towa actual support shot damage/ammo");
            holo_visual::capture(stem+"-after.png");
            if(distance==2)proof<<",";
            proof<<"{\"distance\":"<<distance<<",\"damage\":"<<hp-m->hit_points<<",\"ammoBefore\":"<<ammo<<",\"ammoAfter\":"<<holo_batch::s.resource<<"}";
        }
        proof<<"],\"nativeMovementTrigger\":true,\"visualRngUnchanged\":true}\n";
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
        require(has(you.pos()+coord_def(2,2),holo_visual::effect::shrine),"low faith 5x5 corner missing");
        require(!has(you.pos()+coord_def(3,0),holo_visual::effect::shrine),"low faith shrine exceeds5x5");
        require(holo_batch::s.one_end-you.elapsed_time==200+5*holo_batch::s.inv,"shrine duration changed");
        fixture("miko");cast("miko",1,nullptr,you.pos());
        cast("miko",3,nullptr,you.pos());
        require(holo_visual::invocation_at(you.pos()+coord_def(2,0))==holo_visual::effect::mikoflame,"boundary flame missing");
        require(holo_visual::invocation_at(you.pos()+coord_def(1,0))!=holo_visual::effect::mikoflame,"interior falsely burning");
        const int fire_end=holo_batch::s.three_end;
        cast("miko",5,nullptr,you.pos());
        int sx=1,sy=1;
        for(int x:{-3,3})for(int y:{-3,3})
            require(holo_visual::invocation_sprite_at(you.pos()+coord_def(x,y),sx,sy)==holo_visual::effect::mikotorii && sx==1 && sy==1,"torii missing at domain corner");
        require(holo_visual::invocation_sprite_at(you.pos()+coord_def(2,2),sx,sy)!=holo_visual::effect::mikotorii,"torii inside domain");
        require(holo_visual::invocation_at(you.pos()+coord_def(3,0))==holo_visual::effect::mikoflame,"expanded flame missing");
        const auto before=signature();
        for(int f=0;f<4;++f)holo_visual::capture_invocation("miko",you.pos(),f,std::string(shots)+"/miko-domain-frame"+std::to_string(f)+".png",5);
        require(before==signature(),"domain animation capture changed gameplay");
        step(std::max(0,fire_end-you.elapsed_time));
        require(holo_visual::invocation_at(you.pos()+coord_def(3,0))!=holo_visual::effect::mikoflame,"expired fire still rendered");
        holo_visual::capture(std::string(shots)+"/miko-fire-expired.png");
        step(std::max(0,holo_batch::s.five_end-you.elapsed_time));
        require(holo_visual::invocation_sprite_at(you.pos()+coord_def(3,3),sx,sy)!=holo_visual::effect::mikotorii,"expired torii still rendered");
        holo_visual::capture(std::string(shots)+"/miko-domain-expired.png");
        if(const char *bloom=getenv("HOLOCRAWL_MIKO_BLOOM_REVIEW")) {
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
            std::ofstream(dir+"/miko-bloom.json")<<"{\"status\":\"passed\",\"visualDraftOnly\":true,\"combatImplemented\":false,\"modes\":2,\"frames\":14,\"capturePreservesStateAndRng\":true}";
        }
        std::ofstream proof(dir+"/miko-review.json");
        proof<<"{\"status\":\"passed\",\"lowFaithWidth\":5,\"highFaithWidth\":5,\"domainWidth\":7,\"boundaryOnlyFire\":true,\"expandedFire\":true,\"expiredFireGone\":true,\"expiredDomainGone\":true,\"capturePreservesGameplay\":true}\n";
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
    if(const char *shots=getenv("HOLOCRAWL_POLKA_LEAP_REVIEW")) {
        auto *m=fixture("polka");const auto start=you.pos();
        require(m->pos()==start+coord_def(1,0) || m->move_to_pos(start+coord_def(1,0)),"Polka adjacent target");
        const auto target=m->pos(),landing=target*2-start;
        auto stable=signature();holo_visual::capture(std::string(shots)+"/polka3-before.png");
        require(stable==signature(),"Polka pre-jump capture changed state");
        const int mp=you.magic_points,piety=you.piety;
        require(invoke(3,m,&target,0)==10,"Polka actual native leap");
        require(you.pos()==landing && m->pos()==target,"Polka crosses fixed enemy to opposite cell");
        require(you.magic_points==mp-3 && you.piety==piety-2,"Polka leap costs");
        stable=signature();
        for(int f=0;f<2;++f)holo_visual::capture_invocation("polka",target,f,std::string(shots)+"/polka3-land"+std::to_string(f)+".png",3);
        holo_visual::capture(std::string(shots)+"/polka3-after.png");
        require(stable==signature(),"Polka landing capture changed state");
        step(10);holo_visual::capture(std::string(shots)+"/polka3-settled.png");
        std::ofstream(std::string(shots)+"/polka3-proof.json")<<"{\"status\":\"passed\",\"nativeAbility\":true,\"crossedEnemy\":true,\"mpCost\":3,\"pietyCost\":2,\"timeCostAut\":10,\"renderPreservesState\":true,\"interpolatedAirFrames\":false}\n";
        close_save();return 0;
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
        fixture("koyori");cast("koyori",5,nullptr,you.pos());
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
            cast(g,1,nullptr,origin);require(invoke(3,m,&aim)==0,"Lamy tier3 is passive");holo_batch::s.resource=65;cast(g,5,nullptr,origin);cast_count+=2;
        } else if(g=="polka"){
            cast(g,1,m,aim,1);cast(g,3,m,aim);holo_batch::s.resource=3;cast(g,5,nullptr,you.pos(),1);cast_count+=3;
        } else if(g=="koyori"){
            require(invoke(1)==0 && invoke(3)==0,"Koyori passives are not invocation buttons");
            cast(g,5,nullptr,origin);++cast_count;
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
    require(raven && raven->mname=="Holo hawk","Lui new summon must be a hawk");
    const int hawk_hp=raven->hit_points;const auto hawk_mid=raven->mid;
    raven->mname="Holo raven";advance();
    require(raven->mname=="Holo hawk" && raven->mid==hawk_mid && raven->hit_points==hawk_hp,"Lui legacy name migration changed actor state");

    const int pet_piety=you.piety;m->max_hit_points=100;m->hurt(raven,20000,BEAM_MISSILE);
    require(you.piety==pet_piety+2,"native raven kill credit / strong bonus");
    if(const char *review=getenv("HOLOCRAWL_LUI_ARMY_REVIEW")) {
        m=fixture("lui",180);m->move_to_pos(you.pos()+coord_def(4,0));
        for(int n=0;n<3;++n)cast("lui",1,nullptr,you.pos());
        holo_visual::capture(std::string(review)+"/lui-army-before.png");
        const int mp_before=you.magic_points,faith_before=you.piety,now=you.elapsed_time;
        const int cost=invoke(5,nullptr,nullptr,0,3);
        require(cost==10 && you.magic_points==mp_before-7 && you.piety==faith_before-14,"Lui army costs");
        require(holo_batch::s.companions.size()==6,"Lui army six companions");
        require(holo_batch::s.five_end==now+10+60+2*holo_batch::s.inv && holo_batch::s.five_ready==holo_batch::s.five_end+150,"Lui army duration/cooldown");
        for(const auto &c:holo_batch::s.companions){auto *h=monster_by_mid(c.mid);require(h && c.shield==6+holo_batch::s.inv/3 && h->evasion()==14+holo_batch::s.inv/3+4 && holo_batch::monster_energy(*h,EUT_MOVE,10)==6 && holo_batch::monster_energy(*h,EUT_ATTACK,10)==10,"Lui army shield/evasion/energy");}
        for(int f=0;f<2;++f)holo_visual::capture_invocation("lui",you.pos(),f,std::string(review)+"/lui-army-cast"+std::to_string(f)+".png",5);
        step(cost);const int remaining=holo_batch::s.five_end-you.elapsed_time;
        holo_visual::capture(std::string(review)+"/lui-army-active.png");
        int sx=0,sy=0;require(holo_visual::invocation_sprite_at(you.pos()-coord_def(2,2),sx,sy)!=holo_visual::effect::night_lui5,"Lui army legacy 5x5 anchor");
        step(remaining);holo_visual::capture(std::string(review)+"/lui-army-ended.png");
        int survivors=0;
        for(const auto &c:holo_batch::s.companions){auto *h=monster_by_mid(c.mid);if(h && h->alive()){++survivors;require(c.shield==0,"Lui army shield did not expire");}}
        require(survivors==3,"Lui army extra summons did not expire");
        std::ofstream proof(std::string(review)+"/lui-army.json");
        proof<<"{\"status\":\"passed\",\"invocations\":"<<holo_batch::s.inv<<",\"mpCost\":7,\"pietyCost\":14,\"hawksActive\":6,\"hawksAfterExpiry\":3,\"remainingAutAfterCast\":"<<remaining<<",\"shieldPerHawk\":"<<6+holo_batch::s.inv/3<<",\"evasionBonus\":4,\"moveEnergy\":6,\"attackEnergy\":10,\"cooldownAfterEndAut\":150}";
    }
    if(const char *review=getenv("HOLOCRAWL_LUI_COMMAND_REVIEW")) {
        m=fixture("lui",100);
        for(int n=0;n<3;++n)cast("lui",1,nullptr,you.pos());
        require(m->move_to_pos(you.pos()+coord_def(3,0)),"Lui command enemy placement");
        const coord_def starts[]={you.pos()+coord_def(0,-1),you.pos()+coord_def(1,-1),you.pos()+coord_def(0,1)};
        int i=0;for(const auto &c:holo_batch::s.companions) {
            auto *hawk=monster_by_mid(c.mid);require(hawk && hawk->move_to_pos(starts[i++]),"Lui command hawk placement");
        }
        holo_visual::capture(std::string(review)+"/lui-command-before.png");
        const int hp_before=m->hit_points,mp_before=you.magic_points,faith_before=you.piety;
        const int now=you.elapsed_time;const int cost=invoke(3,m,nullptr,0,3);
        require(cost==10 && you.magic_points==mp_before-3 && you.piety==faith_before-3,"Lui command cost");
        require(holo_batch::s.three_ready==now+50,"Lui command cooldown");
        for(const auto &c:holo_batch::s.companions){auto *hawk=monster_by_mid(c.mid);require(hawk && grid_distance(hawk->pos(),m->pos())==1,"Lui command landing");}
        holo_visual::capture(std::string(review)+"/lui-command-after.png");
        std::ofstream proof(std::string(review)+"/lui-command.json");
        proof<<"{\"status\":\"passed\",\"hawks\":"<<holo_batch::s.companions.size()<<",\"damage\":"<<hp_before-m->hit_points<<",\"mpCost\":3,\"pietyCost\":3,\"actionAut\":"<<cost<<",\"cooldownAut\":50}";
    }
    if(getenv("HOLOCRAWL_LUI_ATTACK_REVIEW")) {
        m=fixture("lui",30);cast("lui",1,nullptr,you.pos());
        raven=monster_by_mid(holo_batch::s.companions.front().mid);
        require(m->move_to_pos(you.pos()+coord_def(3,0)) && raven->move_to_pos(you.pos()+coord_def(2,0)),"Lui attack fixture positions");
        m->max_hit_points=m->hit_points=10000;const int initial_hp=m->hit_points;
        bool landed=false;
        for(int n=0;n<40 && m->hit_points==initial_hp;++n)fight_melee(raven,m,&landed);
        require(landed && m->hit_points<initial_hp && !holo_visual::mask_hawk_at(raven->pos()),"Lui native attack/animation cleanup");
        holo_visual::capture(std::string(getenv("HOLOCRAWL_LUI_ATTACK_REVIEW"))+"/lui-attack-result.png");
        std::ofstream result(std::string(getenv("HOLOCRAWL_LUI_ATTACK_REVIEW"))+"/lui-attack-result.json");
        result<<"{\"status\":\"passed\",\"piety\":"<<int(you.piety)<<",\"damage\":"<<initial_hp-m->hit_points<<"}";
    }
    fixture("noel");cast("noel",5,nullptr,you.pos());const int before_berserk=you.piety;
    require(you.go_berserk(true) && !noel_commander() && you.piety==before_berserk-10,"voluntary berserk ends Noel power and applies conduct");
    fixture("watame");you.magic_points=20;const int before_blood=you.piety;
    require(cast_sublimation_of_blood(100,false)==spret::success && you.piety==before_blood-5,"blood sublimation charges Watame conduct once per cast");
    fixture("lamy",30);cast("lamy",1,nullptr,you.pos());require(you.piety==29 && holo_batch::s.resource>0,"paid drink crosses unlock line");
    step(410);require(holo_batch::s.resource==0,"drunkenness stuck below unlock");
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
    if(const char *shots=getenv("HOLOCRAWL_NIGHT_REVIEW"))holo_visual::capture(std::string(shots)+"/noel-supply-before.png");
    you.piety=75;advance();require(supplies["gifts"].get_int()==1 && supplies["half_points"].get_int()==8,"Noel supply threshold and overflow");
    int gifts=0;
    for(const auto &item:mitm)if(item.defined() && item.props.exists("holo_gift")) {
        ++gifts;require(item.pos==you.pos() && !item.cursed() && item.plus>=(item.base_type==OBJ_WEAPONS?2:armour_is_enchantable(item)?1:0),"Noel usable uncursed minimum-enchantment delivery");
    }
    require(gifts==1,"native equipment gift missing");
    if(const char *shots=getenv("HOLOCRAWL_NIGHT_REVIEW")) {
        const auto before=signature();
        for(int f=0;f<2;++f)holo_visual::capture_invocation("noel",you.pos(),f,std::string(shots)+"/noel-supply-effect"+std::to_string(f)+".png",3);
        holo_visual::capture_invocation("noel",you.pos(),1,std::string(shots)+"/noel-supply3.png",3);
        holo_visual::capture(std::string(shots)+"/noel-supply-after.png");
        require(before==signature(),"supply capture changed state");
        const auto delivery=you.pos();you.turn_is_over=false;process_command(CMD_MOVE_LEFT);
        require(you.turn_is_over && you.pos()==delivery+coord_def(-1,0),"Noel gift reveal movement");step(you.time_taken);
        bool gift_stays=false;for(const auto &item:mitm)if(item.defined() && item.props.exists("holo_gift") && item.pos==delivery)gift_stays=true;
        require(gift_stays,"Noel gift must remain on floor after stepping aside");
        holo_visual::capture(std::string(shots)+"/noel-supply-revealed.png");
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
    fixture("koyori");holo_batch::s.resource=2;holo_batch::s.five_end=100;holo_batch::s.five_ready=200;leave_level();require(holo_batch::s.resource==2 && holo_batch::s.five_end==0 && holo_batch::s.five_ready==200,"Koyori sequence/cooldown at stairs");
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


