from pathlib import Path
import shutil

r=Path(__file__).resolve().parents[1];src=r/'engine/campaign-crawl/crawl-ref/source'
rev='suisei-inherit01';base=r/'analysis/native'/rev
assert not base.exists(),'Preserve existing checkpoint'
(base/'before').mkdir(parents=True)
for f in ['holo-batch-internal.h','holo-batch.cc','holo-batch-resources.cc','holo-worship.cc','holo-campaign.cc','holo-campaign-test.cc']:
    shutil.copy2(src/f,base/'before'/f)
p=src/'holo-batch-internal.h';s=p.read_text(encoding='utf-8');a='    bool dream_sleep=false;mid_t dream_target=MID_NOBODY;'
assert a in s;s=s.replace(a,'    bool star_inheritance=false; // Per-action only; the banked reward uses existing saved fields.\n'+a,1);p.write_text(s,encoding='utf-8')
p=src/'holo-batch.cc';s=p.read_text(encoding='utf-8')
a='            if(mon && mon->alive()) { hurt(*mon,bonus);ctx.reward_kill=!mon->alive(); }'
b='''            if(mon && mon->alive()) {
                ctx.damaged|=hurt(*mon,bonus)>0;ctx.reward_kill=!mon->alive();
                ctx.star_inheritance=you.piety>=100 && ctx.stars_before==0 && ctx.damaged && !ctx.reward_kill;
            }'''
assert s.count(a)==1;s=s.replace(a,b,1)
a='        if(target && target->alive()) { hurt(*target,bonus);ctx.reward_kill=!target->alive(); }'
b='''        if(target && target->alive()) {
            ctx.damaged|=hurt(*target,bonus)>0;ctx.reward_kill=!target->alive();
            ctx.star_inheritance=you.piety>=100 && ctx.stars_before==0 && ctx.damaged && !ctx.reward_kill;
        }'''
assert s.count(a)==1;s=s.replace(a,b,1)
a='    martial_after_attack(target,aut);resource_after_attack(target,aut);'
assert s.count(a)==1;s=s.replace(a,'''    // A reward-only kill must clear the dead mark without earning a new reward.
    if(is(god_id::suisei) && ctx.reward_kill && s.marked==ctx.target) {s.marked=MID_NOBODY;s.resource=0;}
'''+a,1);p.write_text(s,encoding='utf-8')
p=src/'holo-batch-resources.cc';s=p.read_text(encoding='utf-8')
a='        if(s.marked==ctx.target) { s.resource=min(3,s.resource+1);s.one_end=now+100; }'
b='''        if(s.marked==ctx.target) {
            const bool inherited=ctx.star_inheritance && s.resource==0 && target->attitude==ATT_HOSTILE;
            s.resource=min(3,s.resource+(inherited?2:1));s.one_end=now+100;
        }'''
assert s.count(a)==1;s=s.replace(a,b,1);p.write_text(s,encoding='utf-8')
p=src/'holo-worship.cc';s=p.read_text(encoding='utf-8')
s=s.replace('return you.piety>=120?5:you.piety>=75?3:current()=="suisei" && you.piety>=50?2:you.piety>=30?1:0;','return you.piety>=120?5:current()=="suisei" && you.piety>=100?4:you.piety>=75?3:current()=="suisei" && you.piety>=50?2:you.piety>=30?1:0;',1)
s=s.replace('"30 / 50 / 75 / 120"','"30 / 50 / 75 / 100 / 120"')
s=s.replace('for(int p:{0,29,30,49,50,74,75,119,120,200})','for(int p:{0,29,30,49,50,74,75,99,100,119,120,200})',1)
s=s.replace('const int expected=p>=120?5:p>=75?3:id=="suisei" && p>=50?2:p>=30?1:0;','const int expected=p>=120?5:id=="suisei" && p>=100?4:p>=75?3:id=="suisei" && p>=50?2:p>=30?1:0;',1);p.write_text(s,encoding='utf-8')
p=src/'holo-campaign.cc';s=p.read_text(encoding='utf-8')
s=s.replace('for(int threshold:{30,50,75,120})if((threshold!=50 || holo_worship::current()=="suisei")','for(int threshold:{30,50,75,100,120})if(((threshold!=50 && threshold!=100) || holo_worship::current()=="suisei")',1)
s=s.replace('"30 / 50 / 75 / 120"','"30 / 50 / 75 / 100 / 120"')
a='    lines.push_back("Corner marks: upper-left power; lower-left protection; upper-right wrath; lower-right recovery/resource.");'
assert a in s;s=s.replace(a,'''    if(g=="suisei")lines.push_back(std::string("4* Star inheritance: ")+(you.piety<100?"locked (piety100)":s.offence>0 && s.three_end>you.elapsed_time?"ready: reward hit starts new foe at2 stars":"waiting for a marked-kill reward"));
'''+a,1)
a='    if(g=="okayu")lines.push_back("3*: A foe put to sleep'
assert a in s;s=s.replace(a,'''    if(g=="suisei")lines.push_back("4* passive Star inheritance (piety100): consume a marked-kill next-hit reward on a fresh marked foe; if that ordinary direct hit deals positive damage and the foe survives, start at2 stars instead of1. No extra MP/piety/time cost. Miss keeps reward. One-shot/reward-only kill grants no inherited stars or recursive reward. Existing stars just gain the normal1. Original3-turn reward window and max3 stars unchanged.");
'''+a,1);p.write_text(s,encoding='utf-8')
p=src/'holo-campaign-test.cc';s=p.read_text(encoding='utf-8')
a='    if(getenv("HOLOCRAWL_SUISEI_FOCUS_RELOAD")) {'
assert a in s
block=r'''    if(getenv("HOLOCRAWL_SUISEI_INHERIT_RELOAD")) {
        holo_reset_validation_fixture();reload_disk(dir+"/inherit-save");
        auto *m=monster_by_mid(you.props["inherit_test_mid"].get_int());
        require(m && holo_worship::rank()==4 && holo_batch::s.offence>0,"inheritance bank not restored");
        {command_scope command;you.prev_targ=m->mindex();macro_buf_add_cmd(CMD_TARGET_SELECT);
         require(cast_a_spell(false,SPELL_MAGIC_DART),"restored inheritance native spell");}
        require(holo_batch::s.marked==m->mid && holo_batch::s.resource==2 && holo_batch::s.offence==0,"restored reward did not start at2");
        step(you.time_taken);std::ifstream expected(dir+"/inherit-expected.txt");std::string text((std::istreambuf_iterator<char>(expected)),{});
        require(text==signature(),"inheritance fresh-process actual spell continuation differs");
        std::ofstream(dir+"/inherit-reload.json")<<"{\"status\":\"passed\",\"bankedRewardRestored\":true,\"actualSpellStartsAt2\":true,\"exactContinuation\":true}\n";
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
        const int hp=b_target->hit_points;normal_cast(b_target);
        require(b_target->alive() && b_target->hit_points<hp && s.marked==b_target->mid && s.resource==2 && s.offence==0 && s.three_end==0,"real reward spell did not start B at2");
        require(suisei_focus_accuracy(b_target)==3,"inherited stars did not activate tier2");
        std::ofstream(dir+"/inherit-expected.txt")<<signature();holo_visual::capture(folder+"/inherit-b2.png");
        normal_cast(b_target);require(s.resource==3,"next normal hit did not cap B at3");holo_visual::capture(folder+"/inherit-b3.png");
        std::ofstream proof(dir+"/suisei-inherit.json");proof<<"{\"status\":\"passed\",\"unlockPiety\":100,\"startsAt\":2,\"maxStars\":3,\"nativeSpellCommands\":6,\"nativeMPAndTimeCosts\":true,\"actualMarkedKill\":true,\"rewardDamage\":"<<reward<<",\"actualNextTargetDamage\":"<<hp-b_target->hit_points<<",\"missKeepsReward\":true,\"oneShotExcluded\":true,\"rewardOnlyKillNoRecursion\":true,\"deadMarkCleared\":true,\"existingStacksOnlyPlus1\":true,\"expiryAndFaithControls\":true,\"divineExcluded\":true,\"tier2ActivatedAt2\":true}\n";
    }
'''
s=s.replace(a,block+a,1)
# An old core test intentionally runs at3* (below the new passive's unlock).
a='m=fixture("suisei");s.marked=m->mid;s.resource=3;s.one_end=100;direct(m,200);'
# The actual old kill fixture has an explicit rat setup; change only that fixture's faith.
s=s.replace('m=fixture("suisei");m->type=MONS_RAT;m->max_hit_points=m->hit_points=1;s.marked=m->mid;s.resource=3;s.one_end=100;direct(m,200);','m=fixture("suisei",99);m->type=MONS_RAT;m->max_hit_points=m->hit_points=1;s.marked=m->mid;s.resource=3;s.one_end=100;direct(m,200);',1)
# Native kill grants piety; explicitly keep this legacy consumption control below100.
s=s.replace('direct(next);require(s.offence==0 && s.three_end==0 && s.resource==1,"Suisei reward consumption or unapproved inheritance");','you.piety=99;direct(next);require(s.offence==0 && s.three_end==0 && s.resource==1,"Suisei reward consumption below tier4");',1)
p.write_text(s,encoding='utf-8')
t=(r/'scripts/capture-suisei-focus02.ps1').read_text(encoding='utf-8-sig').replace('suisei-focus02',rev)
t=t.replace("(Join-Path $output 'focus-save')", "(Join-Path $output 'focus-save'),(Join-Path $output 'inherit-save')",1)
t=t.replace('$env:HOLOCRAWL_SUISEI_FOCUS_REVIEW=$shots;', '$env:HOLOCRAWL_SUISEI_FOCUS_REVIEW=$shots;$env:HOLOCRAWL_SUISEI_INHERIT_REVIEW=$shots;',1)
t=t.replace(' Remove-Item Env:HOLOCRAWL_SUISEI_FOCUS_REVIEW',' Remove-Item Env:HOLOCRAWL_SUISEI_FOCUS_REVIEW\n Remove-Item Env:HOLOCRAWL_SUISEI_INHERIT_REVIEW',1)
a=" $env:HOLOCRAWL_SUISEI_FOCUS_RELOAD='1';"
assert a in t;t=t.replace(a," $env:HOLOCRAWL_SUISEI_INHERIT_RELOAD='1';Run-Capture '-test holocrawl-campaign -no-throttle' 'inherit-reload'\n if((Get-Content (Join-Path $output 'inherit-reload.json') -Raw | ConvertFrom-Json).status -ne 'passed'){throw 'Star inheritance restore failed'}\n Remove-Item Env:HOLOCRAWL_SUISEI_INHERIT_RELOAD\n"+a,1)
(r/'scripts/capture-suisei-inherit01.ps1').write_text(t,encoding='utf-8')
print('Suisei tier4 inheritance core, native spell sequence and fresh-save controls prepared.')
