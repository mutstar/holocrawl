from pathlib import Path
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source';b=r/'analysis/native/fubuki-opening01/before'
p=s/'holo-campaign-test.cc';t=p.read_text(encoding='utf-8');(b/p.name).write_text(t,encoding='utf-8')
anchor='void close_save(){'
fn=r'''bool fubuki_test_hit(monster *m,int accuracy=AUTOMATIC_HIT) {
    bool landed=false;
    {command_scope command;bolt beam;beam.name="Fubuki native first-hit probe";beam.origin_spell=SPELL_MAGIC_DART;
    beam.source=you.pos();beam.target=m->pos();beam.range=6;beam.source_id=you.mid;beam.thrower=KILL_YOU;
    beam.flavour=BEAM_MMISSILE;beam.damage=dice_def(1,3);beam.hit=accuracy;
    beam.fire();landed=holo_batch::ctx.primary;you.turn_is_over=true;you.time_taken=10;}
    return landed;
}
'''
assert anchor in t;t=t.replace(anchor,fn+anchor)
anchor='    if(getenv("HOLOCRAWL_AKI_NUTRIENT_RELOAD")) {'
code=r'''    if(getenv("HOLOCRAWL_FUBUKI_OPENING_RELOAD")) {
        using namespace holo_batch;
        holo_reset_validation_fixture();reload_disk(dir+"/fubuki-save",true);
        auto *m=monster_by_mid(you.props["fubuki_test_target"].get_int());require(m,"restored Fubuki target");
        require(holo_worship::rank()==2 && s.targets[m->mid].kind==0,"unspent opening restore");
        fubuki_test_hit(m);require(s.totals.procs==1 && s.targets[m->mid].kind==1,"restored opening did not fire");
        fubuki_test_hit(m);require(s.totals.procs==1,"restored opening repeated");
        std::ifstream f(dir+"/fubuki-expected.txt");std::string expected((std::istreambuf_iterator<char>(f)),{});
        require(signature()==expected,"Fubuki exact unspent continuation differs");
        reload_disk(dir+"/fubuki-spent",true);m=monster_by_mid(you.props["fubuki_test_target"].get_int());
        require(m && s.targets[m->mid].kind==1,"spent opening restore");fubuki_test_hit(m);
        require(s.totals.procs==1 && signature()==expected,"spent opening save replay differs");
        std::ofstream(dir+"/fubuki-reload.json")<<"{\"status\":\"passed\",\"unspentAndSpentRestored\":true,\"nativeSpellHitAndRngExact\":true}";
        close_save();return 0;
    }
    if(const char *shots=getenv("HOLOCRAWL_FUBUKI_OPENING_REVIEW")) {
        using namespace holo_batch;
        auto setup=[&](int faith,bool prior_spent=false) {
            for(int trial=0;trial<64;++trial) {
                auto *m=fixture("fubuki",faith+1);m->type=MONS_RAT;m->set_hit_dice(1);m->hit_points=m->max_hit_points=10000;
                s.targets[m->mid].kind=prior_spent?1:0;rng::seed(9000+trial);
                cast("fubuki",1,nullptr,you.pos()+coord_def(0,1));
                if(!s.targets[m->mid].raven_hits.empty())return m;
            }
            require(false,"native deception never succeeded");return static_cast<monster*>(nullptr);
        };
        for(int faith:{49,50}) {
            auto *m=setup(faith);require(you.piety==faith,"normal summon piety cost");
            const int mp=you.magic_points;fubuki_test_hit(m);
            require(s.totals.procs==(faith==50?1:0) && s.targets[m->mid].kind==(faith==50?1:0),"Fubuki piety49/50 opening");
            require(mp==you.magic_points && you.piety==faith,"opening charged extra resources");
            fubuki_test_hit(m);require(s.totals.procs==(faith==50?1:0),"opening repeated on second hit");
        }
        bool missed=false;
        for(int trial=0;trial<64 && !missed;++trial){auto *m=setup(50);rng::seed(91000+trial);if(!fubuki_test_hit(m,0)){missed=true;require(s.targets[m->mid].kind==0 && s.totals.procs==0,"miss spent opening");fubuki_test_hit(m);require(s.totals.procs==1,"hit after miss did not use opening");}}
        require(missed,"native miss control");
        for(auto kind:{attack_kind::melee,attack_kind::ranged,attack_kind::spell}) {
            auto *m=setup(50);begin_attack(*m,kind);note_primary_hit(m);end_attack(10);require(s.totals.procs==1,"ordinary hit kind excluded");
        }
        auto *m=setup(50);begin_attack(*m);note_primary_hit(m);end_attack(0);require(s.totals.procs==0 && s.targets[m->mid].kind==0,"zero-time action spent opening");
        m=setup(50);for(auto &link:s.targets[m->mid].raven_hits)link.second=you.elapsed_time;fubuki_test_hit(m);require(s.totals.procs==0,"expired deception fired opening");
        m=setup(50);auto *fox=monster_by_mid(s.companions.front().mid);monster_die(*fox,KILL_DISMISSED,NON_MONSTER,true);fubuki_test_hit(m);require(s.totals.procs==0,"destroyed decoy fired opening");
        m=setup(50);fox=monster_by_mid(s.companions.front().mid);require(fox->move_to_pos(you.pos()+coord_def(-5,0)),"out-of-range decoy placement");fubuki_test_hit(m);require(s.totals.procs==0,"out-of-range decoy fired opening");
        m=setup(50,true);require(s.targets[m->mid].kind==0,"fresh successful deception did not refresh opening");
        const int before=m->hit_points;summon_after_attack(m,10);require(s.totals.procs==0 && s.targets[m->mid].kind==0 && m->hit_points<=before,"non-ordinary damage triggered opening");
        m=setup(50);begin_attack(*m,attack_kind::spell);note_primary_damage(m,1);end_attack(5);require(s.totals.procs==1,"fast paid action lost opening");
        m=setup(180);cast("fubuki",5,nullptr,you.pos());require(s.companions.size()==4,"four image fixture");fubuki_test_hit(m);require(s.totals.procs==1,"four images produced multiple extra shots");
        // Actual positive extra damage, with identical ordinary-shot RNG prefixes.
        m=setup(50);bool extra_damage=false;
        for(int seed=200;seed<264 && !extra_damage;++seed) {
            s.targets[m->mid].kind=0;s.totals.procs=0;m->hit_points=10000;rng::seed(seed);fubuki_test_hit(m);const int with=10000-m->hit_points;
            s.targets[m->mid].kind=1;m->hit_points=10000;rng::seed(seed);fubuki_test_hit(m);const int without=10000-m->hit_points;
            extra_damage=with>without;
        }
        require(extra_damage,"extra foxfire never dealt additional native damage");
        m=setup(50);you.props["fubuki_test_target"]=int(m->mid);
        holo_visual::capture(std::string(shots)+"/fubuki-opening-before.png");
        save_disk(dir+"/fubuki-save");close_save();
        fubuki_test_hit(m);require(s.totals.procs==1,"demo first hit");holo_visual::capture(std::string(shots)+"/fubuki-opening-after.png");
        save_disk(dir+"/fubuki-spent");close_save();
        fubuki_test_hit(m);require(s.totals.procs==1,"demo second hit");std::ofstream(dir+"/fubuki-expected.txt")<<signature();
        std::ofstream(dir+"/fubuki-opening.json")<<"{\"status\":\"passed\",\"unlock\":50,\"nativeDeceptionAndSpellHit\":true,\"oncePerSuccessfulDeception\":true,\"missRetains\":true,\"normalHitKinds\":true,\"fourImagesOneExtra\":true,\"realExtraDamage\":true,\"fastAttackAndZeroTime\":true,\"expiredDeadAndFarControls\":true}";
        close_save();return 0;
    }
'''
assert anchor in t;t=t.replace(anchor,code+anchor);p.write_text(t,encoding='utf-8')
base=(r/'scripts/capture-aki-nutrient01.ps1').read_text(encoding='utf-8')
base=base.replace('aki-nutrient01','fubuki-opening01').replace("'aki'","'fubuki'").replace("'aki-save'","'fubuki-save'),(Join-Path $feature 'fubuki-spent'").replace('HOLOCRAWL_AKI_NUTRIENT_REVIEW','HOLOCRAWL_FUBUKI_OPENING_REVIEW').replace('HOLOCRAWL_AKI_NUTRIENT_RELOAD','HOLOCRAWL_FUBUKI_OPENING_RELOAD').replace('aki-nutrient.json','fubuki-opening.json').replace('aki-reload.json','fubuki-reload.json').replace("'aki-reload'","'fubuki-reload'").replace('freshMpCooldownRestore','freshUnspentAndSpentRestore')
(r/'scripts/capture-fubuki-opening01.ps1').write_text(base,encoding='utf-8')
print('Added native opening and saved spent/unspent continuation checks.')
