from pathlib import Path
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source';b=r/'analysis/native/ayame-zanshin01/before'
# The reward begins with the completed kill action, leaving the full3turn window.
p=s/'holo-batch-martial.cc';t=p.read_text(encoding='utf-8');old='''    if(is(god_id::ayame) && you.piety>=50 && mid==s.marked && s.one_end>you.elapsed_time
        && direct && ordinary && ctx.kind==attack_kind::melee && ctx.eligible
        && adjacent(you.pos(),ctx.position))s.tertiary=you.elapsed_time+30;
''';assert old in t;p.write_text(t.replace(old,''),encoding='utf-8')
p=s/'holo-batch.cc';t=p.read_text(encoding='utf-8');old='    if(ctx.damaged && ctx.eligible && !ctx.reward_kill && (!target || !target->alive())) on_kill(ctx.target,ctx.hd,true,true);';new='''    if(ctx.damaged && ctx.eligible && !ctx.reward_kill && (!target || !target->alive())) {
        if(is(god_id::ayame) && you.piety>=50 && aut>0 && ctx.kind==attack_kind::melee
            && ctx.target==s.marked && s.one_end>you.elapsed_time && adjacent(you.pos(),ctx.position))
            s.tertiary=you.elapsed_time+aut+30;
        on_kill(ctx.target,ctx.hd,true,true);
    }''';assert old in t;p.write_text(t.replace(old,new),encoding='utf-8')
p=s/'holo-campaign-test.cc';t=p.read_text(encoding='utf-8');(b/p.name).write_text(t,encoding='utf-8')
anchor='void close_save(){'
fn=r'''void ayame_test_melee(monster *m,bool spend=true) {
    you.turn_is_over=false;you.time_taken=10;
    {command_scope command;fight_melee(&you,m);}
    if(spend)step(std::max(1,you.time_taken));
}
''';assert anchor in t;t=t.replace(anchor,fn+anchor)
anchor='    if(getenv("HOLOCRAWL_FUBUKI_OPENING_RELOAD")) {'
code=r'''    if(getenv("HOLOCRAWL_AYAME_ZANSHIN_RELOAD")) {
        using namespace holo_batch;
        holo_reset_validation_fixture();reload_disk(dir+"/ayame-save",true);
        auto *m=monster_by_mid(you.props["ayame_test_target"].get_int());require(m,"restored Ayame target");
        require(holo_worship::rank()==2 && s.tertiary==you.elapsed_time+30,"Ayame bank3turn restore");
        ayame_test_melee(m);require(s.tertiary==0 && s.totals.procs==1,"restored first attack consumption");
        ayame_test_melee(m);require(s.totals.procs==1,"restored bank repeated");
        std::ifstream f(dir+"/ayame-expected.txt");std::string expected((std::istreambuf_iterator<char>(f)),{});
        require(signature()==expected,"Ayame exact native melee continuation differs");
        std::ofstream(dir+"/ayame-reload.json")<<"{\"status\":\"passed\",\"threeTurnBankRestored\":true,\"nativeMeleeStateAndRngExact\":true}";
        close_save();return 0;
    }
    if(const char *shots=getenv("HOLOCRAWL_AYAME_ZANSHIN_REVIEW")) {
        using namespace holo_batch;
        auto setup=[&](int faith) {auto *m=fixture("ayame",faith);m->type=MONS_RAT;m->set_hit_dice(1);m->hit_points=m->max_hit_points=10000;return m;};
        auto grant=[&](int faith) {
            auto *m=setup(faith);ayame_test_melee(m);
            require(s.marked==m->mid,"native initial melee did not mark opponent");
            m->hit_points=m->max_hit_points=1;
            for(int i=0;i<40 && m->alive();++i)ayame_test_melee(m);
            require(!m->alive(),"native marked melee kill");return m;
        };
        for(int faith:{49,50}){grant(faith);require(s.tertiary==(faith==50?you.elapsed_time+30:0),"native kill reward faith49/50 or completed-action duration");}
        for(int I:{0,12,27}) {
            auto *m=setup(50);s.inv=I;s.tertiary=you.elapsed_time+30;
            begin_attack(*m);require(to_hit(&you,m)==3+I/6 && slaying(m,false)==2+I/9 && slaying(m,true)==0,"first-swing accuracy/slaying scaling");
            require(evasion(m)==0 && s.tertiary>0,"bank grants early EV or consumed on preview");cancel_attack();require(s.tertiary>0,"cancel lost bank");
        }
        auto *m=setup(50);s.tertiary=you.elapsed_time+30;begin_attack(*m);end_attack(10);
        require(s.tertiary==0 && s.totals.procs==1 && s.marked==m->mid,"miss did not consume and establish ordinary mark");
        begin_attack(*m);require(to_hit(&you,m)==5 && slaying(m,false)==3,"second swing lost ordinary1star bonuses");end_attack(10);require(s.totals.procs==1,"second swing spent another bank");
        m=setup(50);s.tertiary=you.elapsed_time+30;begin_attack(*m);end_attack(0);require(s.tertiary>0,"zero-time action consumed bank");
        m=setup(50);s.tertiary=you.elapsed_time;begin_attack(*m);require(to_hit(&you,m)==0 && slaying(m,false)==0,"expired bank applied");cancel_attack();
        m=setup(49);s.tertiary=you.elapsed_time+30;begin_attack(*m);require(to_hit(&you,m)==0 && slaying(m,false)==0,"locked bank applied");cancel_attack();
        for(auto kind:{attack_kind::ranged,attack_kind::spell}){m=setup(50);s.tertiary=you.elapsed_time+30;begin_attack(*m,kind);end_attack(10);require(s.tertiary>0 && s.totals.procs==0,"non-melee consumed bank");}
        m=setup(50);s.tertiary=you.elapsed_time+30;require(m->move_to_pos(you.pos()+coord_def(2,0)),"reach fixture");begin_attack(*m);require(to_hit(&you,m)==0,"reach applied bank");end_attack(10);require(s.tertiary>0,"reach consumed bank");
        m=setup(50);m->flags|=MF_NO_REWARD;s.tertiary=you.elapsed_time+30;begin_attack(*m);require(to_hit(&you,m)==0,"no-XP target got bank");end_attack(10);require(s.tertiary>0,"no-XP target consumed bank");
        m=setup(50);s.tertiary=you.elapsed_time+30;leave_level();require(s.tertiary==0,"bank crossed floor");
        m=setup(50);s.tertiary=you.elapsed_time+1;step(10);require(s.tertiary==0,"bank expiry cleanup");
        m=setup(75);s.tertiary=you.elapsed_time+30;const int hp=m->hit_points;cast("ayame",3,m,m->pos());
        require(m->hit_points<hp && s.tertiary==0 && s.totals.procs==1 && s.marked==m->mid,"native Twin slash bank integration");
        m=setup(180);cast("ayame",5,m,m->pos());m->hit_points=m->max_hit_points=1;
        for(int i=0;i<40 && m->alive();++i)ayame_test_melee(m);
        require(!m->alive() && s.tertiary==you.elapsed_time+30 && !five() && s.three_ready<=you.elapsed_time,"five-star kill reward compatibility");
        grant(50);holo_visual::capture(std::string(shots)+"/ayame-zanshin-banked.png");
        auto mg=mgen_data::hostile_at(MONS_ORC,false,you.pos()+coord_def(1,0));mg.flags|=MG_FORCE_PLACE;
        auto *next=create_monster(mg,false);require(next,"next duel opponent");next->speed=next->speed_increment=0;next->hit_points=next->max_hit_points=10000;
        you.props["ayame_test_target"]=int(next->mid);holo_visual::capture(std::string(shots)+"/ayame-zanshin-before.png");
        save_disk(dir+"/ayame-save");close_save();ayame_test_melee(next);
        require(s.tertiary==0 && s.totals.procs==1,"native new opponent first melee did not spend bank");holo_visual::capture(std::string(shots)+"/ayame-zanshin-after.png");
        ayame_test_melee(next);require(s.totals.procs==1,"native following melee duplicated bank");
        std::ofstream(dir+"/ayame-expected.txt")<<signature();
        std::ofstream(dir+"/ayame-zanshin.json")<<"{\"status\":\"passed\",\"unlock\":50,\"completedKillBankAut\":30,\"accuracyAtInv12\":5,\"slayingAtInv12\":3,\"nativeMarkedMeleeKill\":true,\"nativeTwinSlash\":true,\"nativeNextOpponentMelee\":true,\"missConsumes\":true,\"cancelAndZeroTimePreserve\":true,\"fiveStarCompatible\":true,\"expiryFloorRangeAndSourceControls\":true}";
        close_save();return 0;
    }
'''
assert anchor in t;t=t.replace(anchor,code+anchor);p.write_text(t,encoding='utf-8')
base=(r/'scripts/capture-fubuki-opening01.ps1').read_text(encoding='utf-8')
base=base.replace('fubuki-opening01','ayame-zanshin01').replace("'fubuki'","'ayame'").replace("'fubuki-save'),(Join-Path $feature 'fubuki-spent'","'ayame-save'").replace('HOLOCRAWL_FUBUKI_OPENING_REVIEW','HOLOCRAWL_AYAME_ZANSHIN_REVIEW').replace('HOLOCRAWL_FUBUKI_OPENING_RELOAD','HOLOCRAWL_AYAME_ZANSHIN_RELOAD').replace('fubuki-opening.json','ayame-zanshin.json').replace('fubuki-reload.json','ayame-reload.json').replace("'fubuki-reload'","'ayame-reload'").replace('freshUnspentAndSpentRestore','freshZanshinRestore')
(r/'scripts/capture-ayame-zanshin01.ps1').write_text(base,encoding='utf-8')
print('Ayame actual melee kill/next swing/Twin slash and fresh restore tests added.')
