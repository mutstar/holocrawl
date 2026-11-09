from pathlib import Path
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source';b=r/'analysis/native/miko-passive01/before'
p=s/'holo-campaign.cc';t=p.read_text(encoding='utf-8')
for a,c in [('missing=max(','missing=std::max('),('heal(min(','heal(std::min('),('overflow=max(','overflow=std::max('),('s.shield=min(','s.shield=std::min('),('max(0,s.defence-you.elapsed_time)','std::max(0,s.defence-you.elapsed_time)')]:t=t.replace(a,c)
p.write_text(t,encoding='utf-8')
p=s/'holo-campaign-test.cc';t=p.read_text(encoding='utf-8');(b/p.name).write_text(t,encoding='utf-8')
anchor='    if(getenv("HOLOCRAWL_KOYORI_RELOAD")) {'
code=r'''    if(getenv("HOLOCRAWL_MIKO_PASSIVE_RELOAD")) {
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
'''
assert anchor in t;t=t.replace(anchor,code+anchor);p.write_text(t,encoding='utf-8')
print('Added isolated native kill, overflow, absorption, controls and fresh restore checks.')
