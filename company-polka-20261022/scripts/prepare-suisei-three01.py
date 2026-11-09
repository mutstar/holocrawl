from pathlib import Path
import shutil

r=Path(__file__).resolve().parents[1]
src=r/'engine/campaign-crawl/crawl-ref/source'
base=r/'analysis/native/suisei-three01'
assert not base.exists(), 'Preserve existing checkpoint'
(base/'before').mkdir(parents=True)
for f in ['holo-batch.cc','holo-batch-resources.cc','holo-campaign.cc','holo-campaign-test.cc','holo-visual.cc']:
    shutil.copy2(src/f,base/'before'/f)

p=src/'holo-batch-resources.cc';s=p.read_text(encoding='utf-8')
replacements={
 '(marked?3*stars:0)':'(marked?5*stars:0)',
 '(id==h.target?5*h.extra:0)':'(id==h.target?(h.end==-1?5*h.extra:8*h.extra):0)',
 's.resource=min(5,s.resource+1);s.one_end=now+100;':'s.resource=min(3,s.resource+1);s.one_end=now+100;',
 'roll_dice(1,5+2*ctx.stars_before)':'roll_dice(1,3+4*ctx.stars_before)',
 'int stars=marked?s.resource:0;hurt(*m,roll_dice(2,8+s.inv/2)+3*stars);':'int stars=marked && s.one_end>now?s.resource:0;hurt(*m,roll_dice(2,8+s.inv/2)+5*stars);',
 'if(marked && grid_distance(h.pos,marked->pos())<=1)':'if(marked && marked->alive() && s.one_end>now && grid_distance(h.pos,marked->pos())<=1)'
}
for a,b in replacements.items():
    assert s.count(a)==1,(a,s.count(a))
    s=s.replace(a,b,1)
p.write_text(s,encoding='utf-8')

p=src/'holo-batch.cc';s=p.read_text(encoding='utf-8')
a='std::ostringstream o;o<<1<<" "<<int(s.god)<<" ";'
assert a in s;s=s.replace(a,'std::ostringstream o;o<<(s.god==god_id::suisei?2:1)<<" "<<int(s.god)<<" ";',1)
a='if(v!=1 || g<0 || g>20)throw std::runtime_error("Unsupported combat save state");'
assert a in s;s=s.replace(a,'if((v!=1 && !(v==2 && g==int(god_id::suisei))) || g<0 || g>20)throw std::runtime_error("Unsupported combat save state");',1)
a='throw std::runtime_error("Invalid combat save payload");s=n;ctx=action_context();'
assert a in s;s=s.replace(a,'''throw std::runtime_error("Invalid combat save payload");
if(n.god==god_id::suisei) {
 // Preserve proportional progress from legacy 5-star saves. An already
 // rolled kill reward stays unchanged. In-flight old comets keep +5/old star.
 if(v==1) {
  n.resource=(3*max(0,min(5,n.resource))+4)/5;
  for(auto &h:n.hazards)if(h.kind==1 && h.arm>0)h.end=-1;
 }
 n.resource=max(0,min(3,n.resource));
}
s=n;ctx=action_context();''',1)
p.write_text(s,encoding='utf-8')

p=src/'holo-visual.cc';s=p.read_text(encoding='utf-8')
s=s.replace('if(marked && marked->alive() && marked->pos()==p)return effect::starmark;', 'if(marked && marked->alive() && marked->pos()==p && holo_batch::s.one_end>you.elapsed_time)return effect::starmark;',1)
a='''    // Opt-in visual review only: read genuine direct-hit stacks, no gameplay writes.
    if(crawl_state.test && you.props.exists("holo_suisei_stars_preview")
        && holo_campaign::active() && holo_worship::current()=="suisei"'''
b='''    // Approved stack indicator: read combat state, without gameplay writes.
    if(holo_campaign::active() && holo_worship::current()=="suisei"'''
assert a in s;s=s.replace(a,b,1)
p.write_text(s,encoding='utf-8')

p=src/'holo-campaign.cc';s=p.read_text(encoding='utf-8')
a='    lines.push_back("Corner marks: upper-left power; lower-left protection; upper-right wrath; lower-right recovery/resource.");'
assert a in s;s=s.replace(a,'''    if(g=="suisei")lines.push_back(make_stringf("Constellation stars: %d/3 | next-hit reward: %d (%s)",s.resource,s.three_end>you.elapsed_time?s.offence:0,turns(s.three_end).c_str()));
'''+a,1)
a='    if(g=="okayu")lines.push_back("3*: A foe put to sleep'
assert a in s;s=s.replace(a,'''    if(g=="suisei")lines.push_back("1* passive: one star per positive direct attack, max3, expires10 turns since last hit. A marked kill grants next-hit1d(3+4*stars) for3 turns, AC applies. Manual retarget costs1 turn. 3* active: MP3/piety3/1turn, range5 piercing,2d(8+Inv/2)+5 per marked star; consumes stars only on hit. 5* active: MP6/piety10/1turn, range6 fixed3x3, lands2turns after completion;3d(10+Inv/2)+8 per snapshotted marked star, AC applies. No tracking. Allies/self may be hit.");
'''+a,1)
p.write_text(s,encoding='utf-8')

p=src/'holo-campaign-test.cc';s=p.read_text(encoding='utf-8')
a='    if(const char *shots=getenv("HOLOCRAWL_MELA_DISPATCH_REVIEW")) {'
assert a in s
block=r'''    if(getenv("HOLOCRAWL_SUISEI_THREE_RELOAD")) {
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
        m=fixture("suisei");s.marked=m->mid;s.resource=3;s.one_end=100;m->hit_points=1;direct(m,200);
        require(!m->alive() && s.offence>=1 && s.offence<=15 && s.three_end==you.elapsed_time+30,"Suisei actual kill reward");
        const auto p=you.pos()+coord_def(2,0);auto mg=mgen_data::hostile_at(MONS_RAT,false,p);mg.flags|=MG_FORCE_PLACE;
        auto *next=create_monster(mg,false);require(next,"Suisei next enemy");next->hit_points=next->max_hit_points=10000;next->speed=next->speed_increment=0;
        direct(next);require(s.offence==0 && s.three_end==0 && s.resource==1,"Suisei reward consumption or unapproved inheritance");
        // Compare raw post-AC deltas on a native zero-AC rat, with identical
        // RNG/Invocations. Covers both active formulas, costs and consumption.
        int cut[4]={0},comet[4]={0};
        for(int stars=0;stars<=3;++stars) {
            m=fixture("suisei");m->type=MONS_RAT;require(m->armour_class()==0,"zero AC cut fixture");
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
'''
s=s.replace(a,block+a,1)
p.write_text(s,encoding='utf-8')

t=(r/'scripts/capture-suisei-stars03.ps1').read_text(encoding='utf-8-sig').replace('suisei-stars03','suisei-three01')
t=t.replace("(Join-Path $output 'su-water-save')", "(Join-Path $output 'su-water-save'),(Join-Path $output 'suisei-save')",1)
t=t.replace('$env:HOLOCRAWL_SUISEI_STARS_REVIEW=$shots', '$env:HOLOCRAWL_SUISEI_THREE_REVIEW=$shots')
t=t.replace('Remove-Item Env:HOLOCRAWL_SUISEI_STARS_REVIEW','Remove-Item Env:HOLOCRAWL_SUISEI_THREE_REVIEW')
a=" $env:HOLOCRAWL_SU_WATER_RELOAD='1';"
t=t.replace(a," $env:HOLOCRAWL_SUISEI_THREE_RELOAD='1';Run-Capture '-test holocrawl-campaign -no-throttle' 'suisei-reload'\n if((Get-Content (Join-Path $output 'suisei-reload.json') -Raw | ConvertFrom-Json).status -ne 'passed'){throw 'Suisei fresh restore failed'}\n Remove-Item Env:HOLOCRAWL_SUISEI_THREE_RELOAD\n"+a,1)
(r/'scripts/capture-suisei-three01.ps1').write_text(t,encoding='utf-8')
print('Suisei cap3 combat, approved VFX, save migration and native integration checks prepared.')
