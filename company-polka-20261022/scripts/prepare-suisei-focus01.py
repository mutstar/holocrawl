from pathlib import Path
import shutil

r=Path(__file__).resolve().parents[1];src=r/'engine/campaign-crawl/crawl-ref/source'
rev='suisei-focus01';base=r/'analysis/native'/rev
assert not base.exists(),'Preserve prior checkpoint'
(base/'before').mkdir(parents=True)
for f in ['holo-batch.h','holo-batch.cc','beam.cc','holo-worship.cc','holo-campaign.cc','holo-campaign-test.cc']:
    shutil.copy2(src/f,base/'before'/f)
p=src/'holo-batch.h';s=p.read_text(encoding='utf-8');a='int to_hit(const actor *attacker,const actor *defender);'
assert s.count(a)==1;s=s.replace(a,'int suisei_focus_accuracy(const actor *target);\n'+a,1);p.write_text(s,encoding='utf-8')
p=src/'holo-batch.cc';s=p.read_text(encoding='utf-8');a='int to_hit(const actor *attacker,const actor *defender)\n'
assert s.count(a)==1
s=s.replace(a,'''int suisei_focus_accuracy(const actor *target)
{
    if(!is(god_id::suisei) || you.piety<50 || !holo_campaign::ordinary_damage()
        || internal_damage || !target || !target->is_monster() || !target->alive()
        || target->as_monster()->attitude!=ATT_HOSTILE || target->mid!=s.marked
        || s.one_end<=you.elapsed_time || s.resource<2)return 0;
    return 3;
}
'''+a,1)
a='''    if(attacker->is_player() && defender->is_monster()) {
        int bonus=0;'''
assert s.count(a)==1;s=s.replace(a,a+'''
        if(ctx.ordinary && (ctx.kind==attack_kind::melee || ctx.kind==attack_kind::ranged))
            bonus+=suisei_focus_accuracy(defender);''',1);p.write_text(s,encoding='utf-8')
p=src/'beam.cc';s=p.read_text(encoding='utf-8');a='''    int beam_hit = hit;

    if (beam_hit != AUTOMATIC_HIT)
    {'''
assert s.count(a)==1
s=s.replace(a,a+'''
        // Target-specific spell accuracy. Weapon projectiles receive the
        // bonus through attack::calc_to_hit; never add it a second time here.
        // Engulfing/explosion and MR attacks have separate native rules.
        if(source_id==you.mid && origin_spell!=SPELL_NO_SPELL
            && !is_enchantment() && !engulfs && !is_explosion)
            beam_hit+=holo_batch::suisei_focus_accuracy(mon);
''',1);p.write_text(s,encoding='utf-8')
p=src/'holo-worship.cc';s=p.read_text(encoding='utf-8')
a='return you.piety>=120?5:you.piety>=75?3:you.piety>=30?1:0;'
assert s.count(a)==1;s=s.replace(a,'return you.piety>=120?5:you.piety>=75?3:current()=="suisei" && you.piety>=50?2:you.piety>=30?1:0;',1)
a='make_stringf("Piety %d/200; unlocked tier %d (30 / 75 / 120).",int(you.piety),rank())'
assert a in s;s=s.replace(a,'make_stringf("Piety %d/200; unlocked tier %d (%s).",int(you.piety),rank(),current()=="suisei"?"30 / 50 / 75 / 120":"30 / 75 / 120")',1)
s=s.replace('for(int p:{0,29,30,74,75,119,120,200})','for(int p:{0,29,30,49,50,74,75,119,120,200})',1)
s=s.replace('const int expected=p>=120?5:p>=75?3:p>=30?1:0;','const int expected=p>=120?5:p>=75?3:id=="suisei" && p>=50?2:p>=30?1:0;',1)
s=s.replace('fprintf(stderr,"worship01: all 176 player/character tag roundtrips passed\\n");','fprintf(stderr,"worship01: all %d player/character tag roundtrips passed\\n",roundtrips);',1)
p.write_text(s,encoding='utf-8')
p=src/'holo-campaign.cc';s=p.read_text(encoding='utf-8')
a='for(int threshold:{30,75,120})if(before<threshold && you.piety>=threshold)'
assert a in s;s=s.replace(a,'for(int threshold:{30,50,75,120})if((threshold!=50 || holo_worship::current()=="suisei") && before<threshold && you.piety>=threshold)',1)
a='make_stringf("[%s%s] Piety %d/200 | MP %d | unlocks 30 / 75 / 120",std::string(rank,\'*\').c_str(),std::string(5-rank,\'.\').c_str(),int(you.piety),int(you.magic_points))'
assert a in s;s=s.replace(a,'make_stringf("[%s%s] Piety %d/200 | MP %d | unlocks %s",std::string(rank,\'*\').c_str(),std::string(5-rank,\'.\').c_str(),int(you.piety),int(you.magic_points),g=="suisei"?"30 / 50 / 75 / 120":"30 / 75 / 120")',1)
a='    lines.push_back("Corner marks: upper-left power; lower-left protection; upper-right wrath; lower-right recovery/resource.");'
assert a in s;s=s.replace(a,'''    if(g=="suisei")lines.push_back(std::string("2* Focused observation: ")+(you.piety<50?"locked (piety50)":holo_batch::suisei_focus_accuracy(monster_by_mid(s.marked))?"active: accuracy +3 vs marked foe":"ready: needs 2+ stars on marked foe"));
'''+a,1)
a='    if(g=="okayu")lines.push_back("3*: A foe put to sleep'
assert a in s;s=s.replace(a,'''    if(g=="suisei")lines.push_back("2* passive Focused observation (piety50): +3 accuracy vs the live marked foe at2+stars. Ordinary melee/ranged and attack spells with normal hit checks only. No damage bonus, MP/piety/turn/star cost or Invocations scaling. Auto-hit, explosion/engulf and MR checks unchanged. Ends when stars fall below2, mark expires, target changes or piety falls below50.");
'''+a,1);p.write_text(s,encoding='utf-8')
p=src/'holo-campaign-test.cc';s=p.read_text(encoding='utf-8')
s=s.replace('#include "fight.h"','#include "fight.h"\n#include "melee-attack.h"\n#include "ranged-attack.h"',1)
a='    if(getenv("HOLOCRAWL_SUISEI_THREE_RELOAD")) {'
assert a in s
block=r'''    if(getenv("HOLOCRAWL_SUISEI_FOCUS_RELOAD")) {
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
        require(melee1-melee0==3,"native melee accuracy delta");cancel_attack();
        for(int subtype:{MI_STONE,MI_JAVELIN,MI_DART}) {
            item_def missile;missile.base_type=OBJ_MISSILES;missile.sub_type=subtype;missile.quantity=1;
            begin_attack(*m,attack_kind::ranged);ranged_attack ranged(&you,m,&missile,false);
            s.resource=1;const int before=ranged.calc_to_hit(false);s.resource=2;const int after=ranged.calc_to_hit(false);
            require(after-before==3,"native thrown projectile accuracy delta");cancel_attack();
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
        std::ofstream proof(dir+"/suisei-focus.json");proof<<"{\"status\":\"passed\",\"piety\":50,\"stars\":2,\"accuracy\":3,\"nativeMeleeDelta\":"<<melee1-melee0<<",\"nativeThrownTypes\":[\"stone\",\"javelin\",\"dart\"],\"nativeSpellTrialsPerCase\":64,\"spellHitsBefore\":"<<hits[0]<<",\"spellHitsAfter\":"<<hits[1]<<",\"autoHitDamageUnchanged\":true,\"mrOutcomeAndRngUnchanged\":true,\"noResourceCost\":true,\"expiryAndFaithControls\":true,\"divineExcluded\":true,\"fixedAcrossInvocations\":true}\n";
    }
'''
s=s.replace(a,block+a,1);p.write_text(s,encoding='utf-8')
t=(r/'scripts/capture-suisei-three03.ps1').read_text(encoding='utf-8-sig').replace('suisei-three03',rev)
t=t.replace("(Join-Path $output 'suisei-save')", "(Join-Path $output 'suisei-save'),(Join-Path $output 'focus-save')",1)
t=t.replace('$env:HOLOCRAWL_SUISEI_THREE_REVIEW=$shots;', '$env:HOLOCRAWL_SUISEI_THREE_REVIEW=$shots;$env:HOLOCRAWL_SUISEI_FOCUS_REVIEW=$shots;',1)
t=t.replace(' Remove-Item Env:HOLOCRAWL_SUISEI_THREE_REVIEW',' Remove-Item Env:HOLOCRAWL_SUISEI_THREE_REVIEW\n Remove-Item Env:HOLOCRAWL_SUISEI_FOCUS_REVIEW',1)
a=" $env:HOLOCRAWL_SUISEI_THREE_RELOAD='1';"
assert a in t;t=t.replace(a," $env:HOLOCRAWL_SUISEI_FOCUS_RELOAD='1';Run-Capture '-test holocrawl-campaign -no-throttle' 'focus-reload'\n if((Get-Content (Join-Path $output 'focus-reload.json') -Raw | ConvertFrom-Json).status -ne 'passed'){throw 'Focused observation restore failed'}\n Remove-Item Env:HOLOCRAWL_SUISEI_FOCUS_RELOAD\n"+a,1)
(r/'scripts/capture-suisei-focus01.ps1').write_text(t,encoding='utf-8')
print('Focused observation: weapon/spell accuracy, piety50 rank/status, native controls prepared.')
