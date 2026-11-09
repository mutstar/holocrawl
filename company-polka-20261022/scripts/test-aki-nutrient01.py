from pathlib import Path
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source';b=r/'analysis/native/aki-nutrient01/before'
p=s/'holo-campaign.cc';t=p.read_text(encoding='utf-8').replace('&& line(s.centre,m.pos()) && (s.targets[m.mid].stacks>=3 || m.props.exists("holo_bloom_three"))','&& line(s.centre,m.pos()) && ((s.targets[m.mid].stacks>=3 && s.targets[m.mid].expires>you.elapsed_time) || m.props.exists("holo_bloom_three"))');p.write_text(t,encoding='utf-8')
p=s/'holo-campaign-test.cc';t=p.read_text(encoding='utf-8');(b/p.name).write_text(t,encoding='utf-8')
anchor='void close_save(){'
fn=r'''void aki_test_hit(monster *m) {
    command_scope command;bolt beam;beam.name="Aki ordinary native kill probe";beam.origin_spell=SPELL_MAGIC_DART;
    beam.source=you.pos();beam.target=m->pos();beam.range=6;beam.source_id=you.mid;beam.thrower=KILL_YOU;
    beam.flavour=BEAM_MMISSILE;beam.damage=dice_def(4,20);beam.hit=AUTOMATIC_HIT;
    beam.fire();you.turn_is_over=true;you.time_taken=10;
}
'''
assert anchor in t;t=t.replace(anchor,fn+anchor)
anchor='    if(getenv("HOLOCRAWL_MIKO_PASSIVE_RELOAD")) {'
code=r'''    if(getenv("HOLOCRAWL_AKI_NUTRIENT_RELOAD")) {
        using namespace holo_batch;
        holo_reset_validation_fixture();reload_disk(dir+"/aki-save",true);
        require(holo_worship::current()=="aki" && holo_worship::rank()==2 && s.rest[0]==you.elapsed_time+30,"Aki tier2 cooldown restore");
        aki_test_hit(monster_by_mid(you.props["aki_first"].get_int()));require(you.magic_points==10,"restored cooldown bypass");
        step(30);aki_test_hit(monster_by_mid(you.props["aki_second"].get_int()));require(you.magic_points==12,"restored cooldown expiry");
        std::ifstream f(dir+"/aki-expected.txt");std::string expected((std::istreambuf_iterator<char>(f)),{});
        require(signature()==expected,"Aki exact continuation differs");
        std::ofstream(dir+"/aki-reload.json")<<"{\"status\":\"passed\",\"cooldownRestored\":true,\"nativeKillsAndRngExact\":true}";
        close_save();return 0;
    }
    if(const char *shots=getenv("HOLOCRAWL_AKI_NUTRIENT_REVIEW")) {
        using namespace holo_batch;
        auto prep=[](monster *m){m->type=MONS_RAT;m->set_hit_dice(1);m->hit_points=m->max_hit_points=1;m->speed=m->speed_increment=0;};
        auto setup=[&](int faith) {
            auto *m=fixture("aki",faith);cast("aki",1,nullptr,you.pos());step(10);prep(m);
            auto &q=s.targets[m->mid];q.stacks=3;q.expires=you.elapsed_time+200;q.next=you.elapsed_time+10;
            you.magic_points=10;return m;
        };
        for(int faith:{30,50,75}) {
            auto *m=setup(faith);const auto corner=you.pos()+coord_def(2,2);
            const auto fx=holo_visual::at(corner);
            require(std::find(fx.begin(),fx.end(),holo_visual::effect::garden)!=fx.end(),"Aki5x5 corner missing");
            const auto outside=holo_visual::at(you.pos()+coord_def(3,0));
            require(std::find(outside.begin(),outside.end(),holo_visual::effect::garden)==outside.end(),"Aki normal exceeds5x5");
            if(faith==30)holo_visual::capture(std::string(shots)+"/aki-tier1-5x5.png");
        }
        for(int faith:{49,50}) {auto *m=setup(faith);aki_test_hit(m);require(!m->alive() && you.magic_points==(faith==50?12:10),"Aki native direct faith49/50");}
        for(int inv:{0,12,27}){auto *m=setup(50);s.inv=inv;aki_test_hit(m);require(you.magic_points==10+std::min(3,1+inv/12),"Aki MP scaling");}
        auto *m=setup(50);you.magic_points=you.max_magic_points;aki_test_hit(m);require(you.magic_points==you.max_magic_points && s.rest[0]==0,"full MP handling");
        m=setup(50);s.targets[m->mid].stacks=2;aki_test_hit(m);require(you.magic_points==10,"two stacks rewarded");
        m=setup(50);s.targets[m->mid].expires=you.elapsed_time;aki_test_hit(m);require(you.magic_points==10,"expired stacks rewarded");
        m=setup(50);m->flags|=MF_NO_REWARD;aki_test_hit(m);require(you.magic_points==10,"no-XP kill rewarded");
        m=setup(50);require(m->move_to_pos(you.pos()+coord_def(3,0)),"outside target placement");aki_test_hit(m);require(you.magic_points==10,"outside garden rewarded");
        m=setup(50);s.proc_ready=you.elapsed_time;summon_tick(you.elapsed_time);require(!m->alive() && you.magic_points==12,"garden DoT MP reward");
        m=setup(180);s.targets[m->mid].stacks=2;const int before=you.magic_points;
        cast("aki",5,nullptr,you.pos());require(!m->alive() && you.magic_points==before-6+2,"bloom consumed stacks before MP reward");
        holo_visual::capture(std::string(shots)+"/aki-tier5-7x7.png");
        m=setup(75);require(m->move_to_pos(you.pos()+coord_def(2,0)),"plant victim placement");
        manual_second=you.pos()+coord_def(0,-1);cast("aki",3,nullptr,you.pos()+coord_def(0,1));
        you.magic_points=10;s.proc_ready=you.elapsed_time+1000;
        for(int n=0;n<64 && m->alive();++n){for(auto &c:s.companions)c.next=you.elapsed_time;summon_tick(you.elapsed_time);}
        require(!m->alive() && you.magic_points==12,"own rose native bolt MP reward");
        holo_visual::capture(std::string(shots)+"/aki-tier3-5x5.png");
        m=setup(50);holo_visual::capture(std::string(shots)+"/aki-mp-before.png");aki_test_hit(m);
        require(you.magic_points==12,"MP demo reward");holo_visual::capture(std::string(shots)+"/aki-mp-after.png");
        auto spawn=[&](coord_def p) {
            auto mg=mgen_data::hostile_at(MONS_RAT,false,p);mg.flags|=MG_FORCE_PLACE;auto *n=create_monster(mg,false);require(n,"cooldown rat");prep(n);
            auto &q=s.targets[n->mid];q.stacks=3;q.expires=you.elapsed_time+200;q.next=you.elapsed_time+10;return n;
        };
        auto *first=spawn(you.pos()+coord_def(1,0));auto *second=spawn(you.pos()+coord_def(-1,0));
        you.props["aki_first"]=int(first->mid);you.props["aki_second"]=int(second->mid);
        you.magic_points=10;s.proc_ready=you.elapsed_time+1000;
        save_disk(dir+"/aki-save");close_save();
        aki_test_hit(first);require(you.magic_points==10,"cooldown bypass");step(30);aki_test_hit(second);require(you.magic_points==12,"cooldown failed to end");
        std::ofstream(dir+"/aki-expected.txt")<<signature();
        std::ofstream(dir+"/aki-nutrient.json")<<"{\"status\":\"passed\",\"widths\":[5,5,7],\"unlock\":50,\"mpAtInv0_12_27\":[1,2,3],\"nativeDirectDotRoseBloomKills\":true,\"cooldown\":30,\"fullMpNoStorage\":true,\"controls\":true}";
        close_save();return 0;
    }
'''
assert anchor in t;t=t.replace(anchor,code+anchor);p.write_text(t,encoding='utf-8')
base=(r/'scripts/capture-miko-passive01.ps1').read_text(encoding='utf-8')
base=base.replace('miko-passive01','aki-nutrient01').replace("'miko'","'aki'").replace("'miko-save'","'aki-save'").replace('HOLOCRAWL_MIKO_PASSIVE_REVIEW','HOLOCRAWL_AKI_NUTRIENT_REVIEW').replace('HOLOCRAWL_MIKO_PASSIVE_RELOAD','HOLOCRAWL_AKI_NUTRIENT_RELOAD').replace('miko-passive.json','aki-nutrient.json').replace('miko-reload.json','aki-reload.json').replace("'miko-reload'","'aki-reload'")
(r/'scripts/capture-aki-nutrient01.ps1').write_text(base,encoding='utf-8')
print('Aki native direct/DoT/rose/bloom controls and fresh-process MP cooldown replay tests added.')
