from pathlib import Path
r=Path(__file__).resolve().parents[1];src=r/'engine/campaign-crawl/crawl-ref/source'
p=src/'holo-lamy.cc';s=p.read_text();s=s.replace('const bool cloud_spell=spell!=SPELL_NO_SPELL && (get_spell_flags(spell)&spflag::cloud);','const bool cloud_spell=spell!=SPELL_NO_SPELL && ((get_spell_flags(spell)&spflag::cloud)\n        || spell==SPELL_CONJURE_FLAME || spell==SPELL_POISONOUS_VAPOURS);');p.write_text(s)
p=src/'holo-campaign-test.cc';s=p.read_text();s=s.replace('#include "holo-lamy.h"','#include "holo-lamy.h"\n#include "cloud.h"\n#include "evoke.h"',1)
anchor='    const char *mode=getenv("HOLOCRAWL_CAMPAIGN_RELOAD");'
test_reload='''    if(getenv("HOLOCRAWL_LAMY_TOOL_RELOAD")) {
        holo_reset_validation_fixture();reload_disk(dir+"/lamy-cloud-save");
        auto *m=monster_by_mid(you.props["lamy_test_mid"].get_int());
        require(m && holo_worship::current()=="lamy","Lamy fresh cloud player/monster restore");
        const int group=holo_lamy::cloud_use(m->pos());
        require(group==you.props["lamy_test_group"].get_int() && group>0,"Lamy cloud provenance restored with level");
        const auto stacks=holo_batch::s.targets[m->mid].stacks;
        require(actor_apply_cloud(m)>0 && holo_batch::s.targets[m->mid].stacks==stacks,"Lamy saved cloud repeats after fresh process");
        std::ifstream expected(dir+"/lamy-cloud-expected.txt");std::string data((std::istreambuf_iterator<char>(expected)),{});
        require(data==signature(),"Lamy cloud fresh continuation RNG/damage mismatch");
        std::ofstream(dir+"/lamy-cloud-reload.json")<<"{\\"status\\":\\"passed\\",\\"nativeCloudRestored\\":true,\\"dedupRestored\\":true,\\"continuationExact\\":true}\\n";
        close_save();return 0;
    }
'''
s=s.replace(anchor,test_reload+anchor,1)
anchor='    // Lamy caster redesign: actual damage attribution, costs, saves and HUD.'
test='''    // Approved extension: real tool use and saved per-use cloud attribution.
    {
        using namespace holo_batch;
        auto *m=fixture("lamy");s.resource=40;const auto origin=you.pos();
        require(m->move_to_pos(origin+coord_def(2,0)),"Lamy tools target position");
        set_skill_level(SK_EVOCATIONS,27);
        auto &wand=you.inv[20];wand=item_def();wand.base_type=OBJ_WANDS;wand.sub_type=WAND_FLAME;wand.quantity=1;wand.charges=30;wand.link=20;wand.pos=coord_def(-1,-1);wand.flags|=ISFLAG_IDENT_MASK;
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
        auto &lamp=you.inv[21];lamp=item_def();lamp.base_type=OBJ_MISCELLANY;lamp.sub_type=MISC_LAMP_OF_FIRE;lamp.quantity=1;lamp.link=21;lamp.pos=coord_def(-1,-1);lamp.flags|=ISFLAG_IDENT_MASK;
        evoker_debt(MISC_LAMP_OF_FIRE)=0;holo_visual::capture(dir+"/lamy-lamp-target.png");macro_buf_add_cmd(CMD_TARGET_SELECT);
        require(evoke_item(21) && s.targets[m->mid].stacks==1,"Lamy actual lamp direct multi-beam dedup");
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
        {holo_lamy::spell_scope tool(SPELL_NO_SPELL,false,true);place_cloud(CLOUD_FIRE,m->pos(),100,&you,0);}
        const int procs=s.totals.procs;actor_apply_cloud(m);require(s.totals.procs==procs+1,"Lamy banquet cloud first proc");
        you.elapsed_time+=10;actor_apply_cloud(m);require(s.totals.procs==procs+1,"Lamy banquet repeated cloud proc");
        // A dedicated native level save proves provenance and consumed hits persist.
        delete_all_clouds();m=fixture("lamy");s.resource=40;
        {holo_lamy::spell_scope spell(SPELL_CONJURE_FLAME,true);place_cloud(CLOUD_FIRE,m->pos(),100,&you,0);}
        actor_apply_cloud(m);require(s.targets[m->mid].stacks==1,"Lamy save fixture first tick");
        you.props["lamy_test_mid"]=int(m->mid);you.props["lamy_test_group"]=holo_lamy::cloud_use(m->pos());
        save_disk(dir+"/lamy-cloud-save");actor_apply_cloud(m);
        {std::ofstream expected(dir+"/lamy-cloud-expected.txt");expected<<signature();}close_save();
        std::ofstream(dir+"/lamy-tools.json")<<"{\\"status\\":\\"passed\\",\\"nativeFlameWand\\":true,\\"nativeLamp\\":true,\\"wandChargesPaid\\":true,\\"directCloudDedup\\":true,\\"cloudCrossCellDedup\\":true,\\"nativeCloudSpread\\":true,\\"separateRecastStacks\\":true,\\"threeStackBurst\\":true,\\"immuneZeroExcluded\\":true,\\"enemyDivineSoberExcluded\\":true,\\"banquetCloudOncePerUse\\":true,\\"nativeCloudSavePrepared\\":true}\\n";
    }
'''
assert anchor in s;s=s.replace(anchor,test+anchor,1);p.write_text(s)
print('Added actual wand/lamp, cloud lifecycle, immunity, dedup and fresh-process level-save checks.')
