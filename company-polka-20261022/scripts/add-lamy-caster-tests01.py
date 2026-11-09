from pathlib import Path
r=Path(__file__).resolve().parents[1];p=r/'engine/campaign-crawl/crawl-ref/source/holo-campaign-test.cc';s=p.read_text(encoding='utf-8').replace('#include "holo-lamy.h"','#include "holo-lamy.h"\n#include "spl-cast.h"\n#include "spl-util.h"')
needle='    if(const char *shots=getenv("HOLOCRAWL_LAMY_HUD_REVIEW")) {'
block=r'''    // Lamy caster redesign: actual damage attribution, costs, saves and HUD.
    {
        using namespace holo_batch;
        auto *m=fixture("lamy");const auto origin=you.pos();
        s.resource=0;const int base_ev=you.evasion();
        const int base_power=calc_spell_power(SPELL_FIREBALL,true,false,false);
        const char *shots=getenv("HOLOCRAWL_LAMY_CASTER_REVIEW");
        if(shots)holo_visual::capture(std::string(shots)+"/lamy1-before.png");
        const int mp=you.magic_points,faith=you.piety;
        require(invoke(1)==10 && s.resource==40 && you.magic_points==mp-2 && you.piety==faith-1,"Lamy drink actual cost/40 intox");
        require(holo_lamy::power_bonus()==16 && you.evasion()==base_ev,"Lamy proper intox power/EV");
        const int buff_power=calc_spell_power(SPELL_FIREBALL,true,false,false);
        require(buff_power==base_power*116/100,"Lamy native spell power boost");
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
        you.skills[SK_ICE_MAGIC]=you.skills[SK_SPELLCASTING]=27;you.duration[DUR_BRILLIANCE]=100;rng::seed(554433);
        require(your_spells(SPELL_OZOCUBUS_REFRIGERATION,40,true)==spret::success,"Lamy native area spell cast");
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
        fixture("towa");require(holo_lamy::power_bonus()==0 && holo_lamy::power(SPELL_FIREBALL,100)==100 && holo_lamy::evasion_penalty()==0,"Lamy changes other god");
        std::ofstream proof(dir+"/lamy-caster.json");proof<<"{\"status\":\"passed\",\"invocation\":12,\"baseSpellPower\":"<<base_power<<",\"buffSpellPower\":"<<buff_power<<",\"drink\":40,\"overdoseEV\":-3,\"nativeAreaCast\":true,\"perCastDedup\":true,\"dotPetDivineExcluded\":true,\"banquetTurns\":8,\"banquetCooldown\":15,\"saved\":true}\n";
    }
'''
assert needle in s;s=s.replace(needle,block+needle,1);p.write_text(s,encoding='utf-8')
s=(r/'scripts/capture-lamy-hud01.ps1').read_text(encoding='utf-8').replace('lamy-hud01','lamy-caster01').replace('$env:HOLOCRAWL_LAMY_HUD_REVIEW=$shots;','$env:HOLOCRAWL_LAMY_HUD_REVIEW=$shots;$env:HOLOCRAWL_LAMY_CASTER_REVIEW=$shots;');(r/'scripts/capture-lamy-caster01.ps1').write_text(s,encoding='utf-8')
