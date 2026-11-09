#include "AppHdr.h"
#include "holo-visual.h"
#include "holo-wrath.h"
#include "describe.h"
#include "holo-campaign.h"
#include "holo-worship.h"

#include <algorithm>
#include <cstdlib>
#include <fstream>
#include <stdexcept>
#include "env.h"
#include "files.h"
#include "god-prayer.h"
#include "holocrawl.h"
#include "libutil.h"
#include "macro.h"
#include "menu.h"
#include "message.h"
#include "output.h"
#include "options.h"
#include "player.h"
#include "player-save-info.h"
#include "prompt.h"
#include "random.h"
#include "religion.h"
#include "skills.h"
#include "state.h"
#include "store.h"
#include "stringutil.h"
#include "tags.h"
#include "terrain.h"
#include "view.h"

namespace holo_worship {
namespace {
const char *key="holocrawl_worship";
const char *ids[]={"suisei","miko","aki","fubuki","ayame","choco",
    "korone","okayu","pekora","noel","watame","towa","lamy","polka",
    "koyori","lui","raden","hajime","su","vivi","sopia","mela"};
const char *names[]={"Suisei","Miko","Aki Rosenthal","Fubuki","Ayame","Choco",
    "Korone","Okayu","Pekora","Noel","Watame","Towa","Lamy","Polka",
    "Koyori","Lui","Raden","Hajime","Su","Vivi","Sopia","Mela"};

bool known(const std::string &id)
{
    const auto all=gods();
    return std::find(all.begin(),all.end(),id)!=all.end();
}
const CrawlHashTable *existing()
{
    if(!you.props.exists(key)) return nullptr;
    if(you.props[key].get_type()!=SV_HASH)
        throw std::runtime_error("Invalid HoloCrawl worship save table");
    return &you.props[key].get_table();
}
CrawlHashTable &data()
{
    if(!existing()) {
        auto &t=you.props[key].new_table();
        t["version"]=1;
        t["current"]=std::string();
        t["history"].new_table();
        t["departures"].new_table();
    }
    return you.props[key].get_table();
}
void redraw()
{
    you.redraw_title=true;
    you.redraw_status_lights=true;
}
void require(bool ok,const char *what)
{
    if(!ok) throw std::runtime_error(std::string("Holo worship regression: ")+what);
}
std::vector<unsigned char> player_tag()
{
    std::vector<unsigned char> bytes;
    writer out(&bytes);
    tag_write(TAG_CHR,out);
    tag_write(TAG_YOU,out);
    require(out.succeeded(),"native player tag write failed");
    return bytes;
}
void load_character_header(reader &in)
{
    const int size=unmarshallInt(in);
    require(size>0 && size<1024*1024,"invalid test character header size");
    std::vector<unsigned char> bytes(size);
    in.read(bytes.data(),bytes.size());
    reader chr(bytes,TAG_MINOR_VERSION);
    const auto format=unmarshallUByte(chr);
    tag_read_char(chr,format,TAG_MAJOR_VERSION,TAG_MINOR_VERSION);
}
void load_tag(const std::vector<unsigned char> &bytes)
{
    require(!you.save,"cannot reset a player with an open save");
    // Normal startup constructs a fresh player. Re-reading into an existing
    // player would append native exercise lists and invalidate later saves.
    you=player();
    reader in(bytes,TAG_MINOR_VERSION);
    load_character_header(in);
    tag_read(in,TAG_YOU);
    // The 0.24 fail_if_not_eof helper has inverted buffer-mode EOF logic.
    // valid() directly tests whether any buffered bytes remain.
    require(!in.valid(),"native player tag has trailing bytes");
}
}
std::vector<std::string> gods() { return {std::begin(ids),std::end(ids)}; }
std::string current()
{
    const auto *t=existing();
    if(!t) return "";
    if(!t->exists("current") || t->at("current").get_type()!=SV_STR)
        throw std::runtime_error("Invalid HoloCrawl worship identity");
    return t->at("current").get_string();
}
bool active() { return !current().empty(); }
std::string display_name()
{
    for(size_t i=0;i<ARRAYSZ(ids);++i) if(current()==ids[i]) return names[i];
    return "No Holo god";
}
int history_count()
{
    const auto *t=existing();
    return t && t->exists("history") ? int(t->at("history").get_table().size()) : 0;
}
int rank()
{
    if(!active()) return 0;
    return you.piety>=120?5:current()=="suisei" && you.piety>=100?4:you.piety>=75?3:(current()=="suisei" || current()=="miko") && you.piety>=50?2:you.piety>=30?1:0;
}
void validate_save()
{
    const auto *t=existing();
    if(!t) return; // Native 0.24 saves without this extension need no migration.
    if(!t->exists("version") || t->at("version").get_type()!=SV_INT
        || t->at("version").get_int()!=1)
        throw std::runtime_error("Unsupported HoloCrawl worship save version");
    for(const char *field:{"history","departures"})
        if(!t->exists(field) || t->at(field).get_type()!=SV_HASH)
            throw std::runtime_error("Invalid HoloCrawl worship history");
    const auto id=current();
    if(!id.empty() && (!known(id) || you.religion!=GOD_NO_GOD
        || you.piety>200 || !t->at("history").get_table().exists(id)))
        throw std::runtime_error("Inconsistent HoloCrawl worship save");
}
bool renounce(bool announce)
{
    validate_save();
    if(!active()) return false;
    const auto old=current(),name=display_name();
    holo_campaign::leaving_god();
    auto &t=data();
    holo_wrath::depart(old,you.piety);
    t["current"]=std::string();
    you.stop_train.insert(SK_INVOCATIONS);
    update_can_currently_train();
    you.piety=0;
    you.turn_is_over=true;
    you.time_taken=BASELINE_DELAY;
    redraw();
    if(announce) mprf("You leave %s. Your past worship is remembered.",name.c_str());
    return true;
}
bool join(const std::string &id,bool announce)
{
    validate_save();
    if(!known(id) || you.species==SP_DEMIGOD || !feat_is_altar(grd(you.pos()))
        || current()==id) return false;
    // Legality is checked before changing either religion or charging a turn.
    if(active()) renounce(false);
    if(you.religion!=GOD_NO_GOD) excommunication(true,GOD_NO_GOD);
    auto &t=data();
    auto &history=t["history"].get_table();
    const bool first=!history.exists(id);
    t["current"]=id;
    if(first) history[id]=you.elapsed_time;
    you.piety=first?15:0;
    holo_campaign::joined();
    holo_visual::bind_altar(id);
    you.start_train.insert(SK_INVOCATIONS);
    update_can_currently_train();
    you.turn_is_over=true;
    you.time_taken=BASELINE_DELAY;
    redraw();
    if(announce) mprf("You worship %s. Piety: %d. First unlock: 30.",
                      display_name().c_str(),int(you.piety));
    return true;
}
bool altar_menu()
{
    Menu menu(MF_SINGLESELECT);
    menu.set_title(new MenuEntry("HoloCrawl altar: choose a god (Esc cancels)",MEL_TITLE));
    for(size_t i=0;i<ARRAYSZ(ids);++i){auto *entry=new MenuEntry(names[i],MEL_ITEM,1,'a'+i);holo_visual::decorate(*entry,ids[i]);menu.add_entry(entry);}
    menu.add_entry(new MenuEntry("Browse god descriptions",MEL_ITEM,1,'?'));
    menu.add_entry(new MenuEntry("Original altar's god",MEL_ITEM,1,'w'));
    if(active()) menu.add_entry(new MenuEntry("Renounce Holo worship",MEL_ITEM,1,'x'));
    menu.show();
    std::vector<MenuEntry*> selected;menu.get_selected(&selected);
    if(selected.empty()) { redraw_screen();return true; }
    const int choice=selected[0]->hotkeys[0];
    redraw_screen();
    if(choice=='?') {
        Menu info(MF_SINGLESELECT);info.set_title(new MenuEntry("Read about a god (Esc returns)",MEL_TITLE));
        for(size_t i=0;i<ARRAYSZ(ids);++i){auto *entry=new MenuEntry(names[i],MEL_ITEM,1,'a'+i);holo_visual::decorate(*entry,ids[i]);info.add_entry(entry);}
        const auto chosen=info.show();redraw_screen();
        if(!chosen.empty())show_info(ids[chosen[0]->hotkeys[0]-'a']);
        return true;
    }
    if(choice=='w') return false;
    if(choice=='x') {
        if(yesno("Renounce Holo worship? Combat wrath will follow until appeased.",false,'n')) renounce();
        return true;
    }
    if(choice<'a' || choice>='a'+int(ARRAYSZ(ids))) return true;
    if(current()==ids[choice-'a']) { mpr("You already worship this god.");return true; }
    if(yesno("Join this Holo god? Your previous worship will end.",false,'n'))
        join(ids[choice-'a']);
    return true;
}
void show_info(const std::string &god)
{
    describe_info info;info.title="HoloCrawl: "+god;
    for(const auto &line:holo_campaign::god_info(god))info.body<<line<<"\n\n";
    show_description(info);
}
void religion_menu()
{
    Menu menu(MF_SINGLESELECT);
    menu.set_title(new MenuEntry("HoloCrawl: "+display_name(),MEL_TITLE));
    menu.add_entry(new MenuEntry(make_stringf("Piety %d/200; unlocked tier %d (%s).",int(you.piety),rank(),current()=="suisei"?"30 / 50 / 75 / 100 / 120":current()=="miko"?"30 / 50 / 75 / 120":"30 / 75 / 120"),MEL_SUBTITLE));
    menu.add_entry(new MenuEntry("Use a to choose invocations. Natural kills grant piety; decay is 1 per 300 turns.",MEL_SUBTITLE));
    for(const auto &line:holo_campaign::status_lines())menu.add_entry(new MenuEntry(line,MEL_SUBTITLE));
    if(active())menu.add_entry(new MenuEntry("God description and worship rules",MEL_ITEM,1,'?'));
    if(!active() && !holo_wrath::status().empty())menu.add_entry(new MenuEntry("Wrath: "+holo_wrath::status(),MEL_SUBTITLE));
    if(active())menu.add_entry(new MenuEntry("Renounce worship",MEL_ITEM,1,'r'));
    menu.show();
    std::vector<MenuEntry*> selected;menu.get_selected(&selected);
    redraw_screen();
    if(!selected.empty() && selected[0]->hotkeys[0]=='?'){show_info(current());return;}
    if(!selected.empty() && yesno("Renounce Holo worship? Combat wrath will follow until appeased.",false,'n')) renounce();
}
bool test_requested()
{
    const char *v=getenv("HOLOCRAWL_WORSHIP_TEST");
    return crawl_state.test && v && std::string(v)=="1";
}
int run_tests()
{
    holo_reset_validation_fixture();
    // setup_game owns an in-memory no-save package for this fixture.
    if(you.save) {you.save->abort();delete you.save;you.save=nullptr;}
    // Combat fixtures deliberately use MP200, beyond 0.24's signed-byte
    // max-MP save field. Test real character-derived HP/MP, not fixture caps.
    calc_hp();you.hp=you.hp_max;
    calc_mp();you.magic_points=you.max_magic_points;
    grd(you.pos())=DNGN_ALTAR_OKAWARU;
    you.props.erase(key);you.piety=0;you.religion=GOD_NO_GOD;
    const char *result=getenv("HOLOCRAWL_WORSHIP_TEST_OUTPUT");
    const char *load=getenv("HOLOCRAWL_WORSHIP_LOAD");
    if(load && std::string(load)=="1") {
        require(result,"fresh-process test needs an output path");
        require(!active(),"fresh process already contains worship state");
        Options.save_dir=get_parent_directory(result);Options.no_save=false;
        crawl_state.bypassed_startup_menu=true;
        you=player();
        require(restore_game(get_save_filename("HoloWorship01")),"fresh-process restore failed");
        require(current()=="noel" && you.piety==119 && history_count()==22,
                "fresh-process membership/history mismatch");
        player_save_info info;info=you;
        require(info.short_desc().find(" of Noel")!=std::string::npos,
                "save browser hides Holo religion");
        uint64_t expected=0;
        std::ifstream rng_file(std::string(result)+".next-rng");
        rng_file >> expected;
        require(!rng_file.fail() && rng::peek_uint64()==expected,"fresh-process RNG mismatch");
        std::ofstream proof(std::string(result)+".reload.json");
        proof << "{\"status\":\"passed\",\"freshProcessRestore\":true,\"rngExact\":true,\"history\":22,\"god\":\"noel\",\"piety\":119}\n";
        require(proof.good(),"fresh-process proof write failed");
        delete you.save;you.save=nullptr;
        fprintf(stderr,"HoloCrawl worship01 fresh-process save/RNG restore passed\n");
        return 0;
    }
    validate_save();require(!active(),"legacy character became a worshipper");
    const auto native_tag=player_tag();
    load_tag(native_tag);require(!active(),"legacy save migration");
    int roundtrips=0;
    for(const auto &id:gods()) {
        const auto before=rng::get_states();
        require(join(id,false),"first join rejected");
        require(you.piety==15 && rank()==0,"initial piety/unlock");
        require(rng::get_states()==before,"membership consumed RNG");
        you.turn_is_over=false;you.time_taken=0;
        const int mp=you.magic_points;
        require(!join(id,false) && !you.turn_is_over && you.time_taken==0
            && you.piety==15 && you.magic_points==mp,"same-god join changed resources/time");
        for(int p:{0,29,30,49,50,74,75,99,100,119,120,200}) {
            you.piety=p;
            const int expected=p>=120?5:id=="suisei" && p>=100?4:p>=75?3:(id=="suisei" || id=="miko") && p>=50?2:p>=30?1:0;
            require(rank()==expected,"unlock boundary");
            const auto states=rng::get_states();
            auto bytes=player_tag();
            you.props.erase(key);you.piety=0;
            load_tag(bytes);
            require(current()==id && you.piety==p && rank()==expected,"native TAG_YOU roundtrip");
            require(rng::get_states()==states,"native save RNG roundtrip");
            ++roundtrips;
        }
        // Keep this serializer-only fixture before the first native timer;
        // executing gameplay timers belongs to the later campaign tests.
        ++you.elapsed_time;
        require(renounce(false) && !active() && you.piety==0,"renunciation");
        const auto old=data()["departures"].get_table()[id].get_table();
        auto bytes=player_tag();you.props.erase(key);load_tag(bytes);
        require(data()["departures"].get_table()[id].get_table()["at_aut"].get_int()==old.at("at_aut").get_int(),"departure timestamp changed on save");
        require(join(id,false) && you.piety==0,"rejoin granted initial piety again");
        renounce(false);
    }
    require(history_count()==22,"distinct worship history");
    fprintf(stderr,"worship01: all %d player/character tag roundtrips passed\n",roundtrips);
    you.turn_is_over=false;you.time_taken=0;
    require(!join("unknown",false) && !you.turn_is_over,"unknown god accepted");
    grd(you.pos())=DNGN_FLOOR;
    require(!join("noel",false) && !you.turn_is_over,"conversion away from altar");
    grd(you.pos())=DNGN_ALTAR_OKAWARU;
    you.species=SP_DEMIGOD;
    require(!join("noel",false),"demigod converted");you.species=SP_HUMAN;
    data()["version"]=99;
    bool rejected=false;
    try {validate_save();} catch(const std::runtime_error &) {rejected=true;}
    require(rejected,"future schema silently accepted");data()["version"]=1;
    // Drive the same native altar/menu functions used by ordinary play.
    crawl_state.show_more_prompt=false;
    you.turn_is_over=false;you.time_taken=0;
    macro_sendkeys_end_add_expanded(27);
    try_god_conversion(GOD_OKAWARU);
    require(!active() && !you.turn_is_over,"altar cancel costs a turn");
    macro_sendkeys_end_add_expanded('j');macro_sendkeys_end_add_expanded('n');
    try_god_conversion(GOD_OKAWARU);
    require(!active() && !you.turn_is_over,"declined altar conversion changed state");
    macro_sendkeys_end_add_expanded('j');macro_sendkeys_end_add_expanded('Y');
    try_god_conversion(GOD_OKAWARU);
    require(current()=="noel" && you.piety==0 && you.turn_is_over,
            "ordinary altar menu did not join Noel");
    you.turn_is_over=false;
    macro_sendkeys_end_add_expanded('j');try_god_conversion(GOD_OKAWARU);
    require(!you.turn_is_over && you.piety==0,"same-god altar awarded a turn/resource");
    macro_sendkeys_end_add_expanded('r');macro_sendkeys_end_add_expanded('n');religion_menu();
    require(active() && !you.turn_is_over,"declined renunciation changed worship");
    macro_sendkeys_end_add_expanded('r');macro_sendkeys_end_add_expanded('Y');religion_menu();
    require(!active() && you.turn_is_over,"religion screen renunciation failed");
    join("noel",false);
    join_religion(GOD_OKAWARU);
    require(!active() && you.religion==GOD_OKAWARU,"native conversion retained dual worship");
    require(join("noel",false) && you.religion==GOD_NO_GOD,
            "Holo conversion did not leave native religion");
    fprintf(stderr,"worship01: ordinary altar/religion menus and native conversion passed\n");
    join("noel",false);you.piety=119;
    if(result) {
        const std::string path=std::string(result)+".player-save";
        { package disk(path.c_str(),true,true);
          { writer out(&disk,"you");tag_write(TAG_CHR,out);tag_write(TAG_YOU,out); }
          disk.commit(); }
        you.props.erase(key);you.piety=0;
        you=player();
        { package disk(path.c_str(),false);
          reader in(&disk,"you",TAG_MINOR_VERSION);load_character_header(in);tag_read(in,TAG_YOU); }
        require(current()=="noel" && you.piety==119,"on-disk player save roundtrip");
        // Use the public gameplay save/restore entry points as well as the
        // player serializer. A fresh test output directory owns this save.
        Options.save_dir=get_parent_directory(result);
        Options.no_save=false;
        crawl_state.bypassed_startup_menu=true;
        you.your_name="HoloWorship01";
        const auto save_rng=rng::get_states();
        require(!you.save,"fixture unexpectedly owns a save");
        you.save=new package(get_savedir_filename(you.your_name).c_str(),true,true);
        save_game(false);
        delete you.save;you.save=nullptr;
        you=player();
        require(restore_game(get_save_filename("HoloWorship01")),"public restore_game failed");
        require(current()=="noel" && you.piety==119 && history_count()==22,
                "public save/restore lost membership or history");
        player_save_info info;info=you;
        require(info.short_desc().find(" of Noel")!=std::string::npos,
                "save browser does not display Holo religion");
        require(rng::get_states()==save_rng,"public save/restore changed RNG");
        { std::ofstream expected(std::string(result)+".next-rng");
          expected << rng::peek_uint64();require(expected.good(),"RNG proof write failed"); }
        delete you.save;you.save=nullptr;
        std::ofstream report(result);
        report << "{\"status\":\"passed\",\"version\":\"worship01\",\"gods\":22,"
            << "\"nativePlayerTagRoundtrips\":" << roundtrips
            << ",\"ordinaryAltarMenus\":true,\"nativeReligionExclusivity\":true,\"publicSaveRestore\":true,\"diskPlayerChunkRoundtrip\":true,\"legacySave\":true,\"rejoinExploitBlocked\":true,"
            << "\"unlockBoundaries\":true,\"rngRoundtrips\":true,\"combatIntegration\":false}\n";
        require(report.good(),"cannot write regression report");
    }
    fprintf(stderr,"HoloCrawl worship01 passed: 22 gods, %d native player tag/RNG roundtrips, join/rejoin/save legality\n",roundtrips);
    return 0;
}
}
