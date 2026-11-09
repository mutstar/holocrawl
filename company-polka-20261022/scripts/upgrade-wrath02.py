"""One-time, assertion-guarded source migration; retained for review."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
src=root/'engine/campaign-crawl/crawl-ref/source'
p=src/'holo-wrath.cc';s=p.read_text(encoding='utf-8')
def rep(a,b):
    global s
    assert a in s,a[:100]
    s=s.replace(a,b)
rep('coord_def centre()', '''// Missing revisions identify legacy active effects: their saved rules stay intact.
bool modern() {return get("revision")>=2;}
int lifetime(int xl) {return 200+5*xl;}
struct servant_stats {int hp,ac,ev,hit,damage,speed,hd;};
servant_stats servant(const std::string &g,int x,bool decoy=false) {
    if(decoy)return {1,0,0,0,0,10,1};
    if(g=="aki")return {30+5*x,3+x/4,8,0,0,10,6+x/2};
    if(g=="fubuki")return {24+4*x,2+x/6,14+x/4,16+x,6+x,15,4+x/2};
    if(g=="ayame")return {40+6*x,3+x/3,10+x/5,16+x,8+7*x/5,x<10?10:12,5+x/2};
    if(g=="korone")return {32+5*x,2+x/5,12+x/6,16+x,7+x,15,4+x/2};
    return {20+3*x,1+x/8,14+x/4,14+x,5+3*x/4,15,4+x/2};
}
int group_size(const std::string &g,int x) {return g=="lui"?2+x/8:g=="aki" || g=="korone"?1+x/10:1+x/12;}
int slow_percent() {return effect("okayu")?(modern()?130+get("xl")/3:115):100;}
coord_def centre()''')
rep('void harm(const coord_def &p,int sides,bool fire,bool single=false)', 'void harm(const coord_def &p,int sides,bool fire,bool single=false,int dice=2)')
rep('roll_dice(2,sides)','roll_dice(dice,sides)')
rep('void spawn(const std::string &g,int count,int duration,int xl)', 'void spawn(const std::string &g,int count,int duration,int xl,bool fake=false)')
rep('mgen_data mg(MONS_RAT,BEH_HOSTILE,cells[i],MHITYOU,MG_FORCE_PLACE);', '''const monster_type body=!modern() || fake?MONS_RAT:g=="aki"?MONS_OKLOB_PLANT:g=="ayame"?MONS_ORC_KNIGHT:g=="lui"?MONS_HARPY:MONS_WOLF;
        mgen_data mg(body,BEH_HOSTILE,cells[i],MHITYOU,MG_FORCE_PLACE);''')
rep('g=="fubuki"?"fox-tail decoy"', 'g=="fubuki"?(fake?"fox-tail decoy":"wrath spirit fox")')
rep('m->props["holo_wrath_god"]=g;', '''// Native templates supply bodies, not equipment, acid spells or loot.
        m->destroy_inventory();m->spells.clear();
        m->props["holo_wrath_revision"]=modern()?2:1;
        m->props["holo_wrath_decoy"]=fake;
        m->props["holo_wrath_god"]=g;''')
rep('m->speed=10;m->speed_increment=0;', '''m->speed=10;m->speed_increment=0;
        if(modern()) {
            const auto v=servant(g,xl,fake);m->hit_points=m->max_hit_points=v.hp;
            m->speed=v.speed;m->set_hit_dice(v.hd);
        }''')
rep('t["god"]=g;t["xl"]=xl;', 't["god"]=g;t["revision"]=2;t["xl"]=xl;')
rep('t["hits"]=3;', 't["hits"]=6;')
rep('t["end"]=you.elapsed_time+(is_debuff(g)?50:is_summon(g)?g=="fubuki"?50:g=="ayame" || g=="korone"?100:80:g=="miko" || (g=="koyori" && get("variant"))?60:20);', 't["end"]=you.elapsed_time+(is_debuff(g)?100+5*xl:is_summon(g)?20+lifetime(xl):g=="miko" || (g=="koyori" && get("variant"))?120+3*xl:20);')
rep('"%s\'s wrath afflicts you for 5 turns. See ^ for effects.",g.c_str()', '"%s\'s wrath afflicts you for %.1f turns. See ^ for effects.",g.c_str(),(get("end")-you.elapsed_time)/10.0')
rep('noisy(15,you.pos())', 'noisy(20+xl/2,you.pos())')
rep('''    } else if(g=="fubuki") {
        spawn(g,2,50,xl);mprf(MSGCH_WARN,"White fox-tail decoys appear. They cannot attack; walk through them or hit them.");
    } else {''', '''    } else {''')
rep('// Legacy version-1 saves with eight outstanding events remain valid.\n    d["wrath_remaining"]=std::max(0,old_count)+std::min(6,3+piety/60);\n    d["xp_remaining"]=std::max(0,old_xp)+std::max(200,40*you.experience_level*you.experience_level);', '''// Native 50 penance commonly decays by 1..3 per event (~25 events).
    // Preserve existing debts; only new abandonment adds the new obligation.
    d["revision"]=2;
    d["wrath_remaining"]=std::max(0,old_count)+18+std::max(0,std::min(200,piety))/25;
    const int xl=you.experience_level;
    d["xp_remaining"]=std::max(0,old_xp)+std::max(200,int(exp_needed(xl+2)-exp_needed(xl)));''')
a=s.index('int accuracy(bool melee)');b=s.index('bool custom_monster',a)
s=s[:a]+'''int accuracy(bool melee) {return effect("choco") || effect("lamy") || effect("polka")?-(modern()?6+get("xl")/10:5):effect("hajime") && melee?-(modern()?4+get("xl")/10:3):effect("lui")?-get("accuracy"):0;}
int armour(){return effect("noel")?-(modern()?4+get("xl")/6:4):0;}
int shield(){return armour();}
int skill_penalty(){return effect("noel")?(modern()?5+get("xl")/8:5):0;}
int evasion(){return effect("hajime")?-(modern()?4+get("xl")/8:3):0;}
int cold(int resistance){return effect("lamy") && resistance>-1?resistance-1:resistance;}
int regen(int rate){return effect("okayu") || effect("watame") || (effect("miko") && get("arm")<=you.elapsed_time && in_zone())?0:rate;}
int healing(int amount){if(!effect("choco") || amount<=0)return amount;const int scaled=amount*(modern()?60:75)+get("healing_fraction");data()["healing_fraction"]=scaled%100;return scaled/100;}
int action_time(int time,bool native_slow){return effect("okayu") && !native_slow?(time*slow_percent()+99)/100:time;}
void charge_action(bool native_slow){if(!effect("okayu") || native_slow || you.time_taken<=0)return;const int scaled=you.time_taken*slow_percent()+get("time_fraction");data()["time_fraction"]=scaled%100;you.time_taken=scaled/100;}
int movement(int cost){int percent=effect("korone") && get("hound")>you.elapsed_time?(modern()?130:120):100;if(effect("koyori") && get("variant") && get("arm")<=you.elapsed_time && in_zone())percent=modern()?175:150;return (cost*percent+99)/100;}
bool revealing(){return effect("vivi") || (modern() && effect("polka"));}
int incoming(int damage,kill_method_type cause,mid_t source) {
    if(damage<=0 || source==MID_NOBODY || (cause!=KILLED_BY_MONSTER && cause!=KILLED_BY_BEAM))return damage;
    if(modern() && effect("vivi"))return damage+std::min(10+get("xl")/2,(damage+2)/3);
    if(!effect("watame") || get("hits")<=0)return damage;
    data()["hits"]=get("hits")-1;
    return damage+std::min(modern()?10+get("xl")/2:10,modern()?(damage*2+4)/5:(damage+4)/5);
}
bool decoy(const actor *a){return a && a->is_monster() && summoned(*a->as_monster()) && a->as_monster()->props["holo_wrath_god"].get_string()=="fubuki" && (number(a->as_monster()->props,"holo_wrath_revision")<2 || number(a->as_monster()->props,"holo_wrath_decoy"));}
void expire_at(const coord_def &p){monster *m=monster_at(p);if(decoy(m))monster_die(*m,KILL_DISMISSED,NON_MONSTER,true);}
''' +s[b:]
rep('hit=14+xl/2;damage=3+xl/4;', '''hit=14+xl/2;damage=3+xl/4;
    if(number(m.props,"holo_wrath_revision")>=2) {
        const auto v=servant(g,xl,decoy(&m));hp=v.hp;ac=v.ac;ev=v.ev;hit=v.hit;damage=v.damage;
    }''')
rep('if(g=="fubuki" || g=="aki")damage=0;', 'if(decoy(&m) || g=="aki")damage=0;')
rep('data()["hound"]=you.elapsed_time+20', 'data()["hound"]=you.elapsed_time+(modern()?30:20)')
rep('if(g!="aki" && g!="fubuki")return true;', 'if(g!="aki" && !decoy(&m))return true;')
rep('if(grid_distance(m.pos(),you.pos())<=4 && holo_batch::line(m.pos(),you.pos()))\n            ouch(you.apply_ac(roll_dice(1,4+number(m.props,"holo_wrath_xl")/6)),', '''const bool v2=number(m.props,"holo_wrath_revision")>=2;const int xl=number(m.props,"holo_wrath_xl");
        if(grid_distance(m.pos(),you.pos())<=(v2?6:4) && holo_batch::line(m.pos(),you.pos()))
            ouch(you.apply_ac(roll_dice(v2?2:1,v2?5+xl/2:4+xl/6)),''')
rep('if(is_summon(g) && g!="fubuki")spawn(g,g=="lui"?3:1,g=="lui" || g=="aki"?60:80,xl);', '''if(is_summon(g)) {
                if(modern()) {
                    spawn(g,group_size(g,xl),lifetime(xl),xl);
                    if(g=="fubuki")spawn(g,2+xl/12,lifetime(xl),xl,true);
                } else if(g!="fubuki")spawn(g,g=="lui"?3:1,g=="lui" || g=="aki"?60:80,xl);
            }''')
rep('5+xl/4,false);', '(modern()?8+xl/2:5+xl/4),false);')
rep('else harm(centre(),g=="suisei"?6+xl/2:g=="koyori"?5+xl/4:6+xl/3,g=="mela" || g=="koyori",g=="towa");', '''else {
                    const int sides=modern()?(g=="suisei" || g=="sopia"?8+xl:g=="mela"?6+xl:g=="koyori"?5+xl:g=="su"?6+xl:7+xl):(g=="suisei"?6+xl/2:g=="koyori"?5+xl/4:6+xl/3);
                    harm(centre(),sides,g=="mela" || g=="koyori",g=="towa",modern()?3:2);
                }''')
rep('roll_dice(1,4+get("xl")/4)', 'roll_dice(1,modern()?8+get("xl")/2:4+get("xl")/4)')
rep('start(g,number(t,"xl"));return;', 'start(g,int(you.experience_level));return;')
rep('void leave_level(){if(!god().empty() && !is_debuff(god()))finish();else cleanup();}', '''void leave_level(){
    // Resolved v2 servants remain native level actors: stairs cannot dismiss them.
    // Off-level servants retain their own expiry, checked when they next act.
    if(modern() && is_summon(god()) && !get("arm"))return;
    if(!god().empty() && !is_debuff(god()))finish();else cleanup();
}''')
rep('&& g!="fubuki") {', '&& (g!="fubuki" || modern())) {')
rep('''        result+=g=="choco"?''','''        if(modern())result+=" | "+description(g);
        else result+=g=="choco"?''')
# Keep explicit legacy tests and update only newly-started effect expectations.
rep('data()["god"]=g;data()["end"]=now+50;', 'data()["revision"]=1;data()["god"]=g;data()["end"]=now+50;')
rep('if(g=="fubuki")require(decoy(&**mi) && !before_monster(**mi));', 'if(decoy(&**mi))require(!before_monster(**mi));else if(g=="fubuki")require(before_monster(**mi));')
rep('"wrath_remaining")==5)', '"wrath_remaining")==22)')
rep('"wrath_remaining")==8)', '"wrath_remaining")==40)')
rep('==24);', '==28);')
rep('==110);', '==116);')
rep('you.time_taken==11', 'you.time_taken==13')
rep('you.time_taken==12', 'you.time_taken==13')
rep('received==3', 'received==2')
# Add descriptions used by both info menus and live status; current XL is explicit.
at=s.index('void validate()')
s=s[:at]+'''std::string description(const std::string &g) {
    const int x=you.experience_level;
    const double turns=(100+5*x)/10.0;
    if(is_summon(g)) {
        const auto v=servant(g,x);
        std::string result=make_stringf("Wrath at current XL %d: %d hostile %s, after 2 turns for %.1f turns; each HP %d, AC %d, EV %d, speed %d, hit %d, damage %d.",x,group_size(g,x),g=="aki"?"roses":g=="fubuki"?"spirit foxes":g=="ayame"?"swordsmen":g=="korone"?"hounds":"ravens",lifetime(x)/10.0,v.hp,v.ac,v.ev,v.speed,v.hit,v.damage);
        if(g=="aki")result+=make_stringf(" Stationary; range 6 thorns, 2d%d physical every 1.5 turns; AC applies.",5+x/2);
        if(g=="fubuki")result+=make_stringf(" Plus %d harmless 1-HP decoys; only decoys can be walked through.",2+x/12);
        if(g=="ayame")result+=" Consecutive hits add up to +12 accuracy; resets after 3 turns without a hit.";
        if(g=="korone")result+=" A hit adds 30% movement time for 3 turns; does not stack.";
        if(g=="lui")result+=" Flying; different ravens give up to -6 accuracy on contact.";
        return result+" No XP or loot; resolved servants persist across stairs until expiry.";
    }
    std::string d;
    if(g=="choco")d=make_stringf("accuracy -%d; received healing -40%%",6+x/10);
    if(g=="okayu")d=make_stringf("action time +%d%%, no natural HP regen; native Slow takes precedence",30+x/3);
    if(g=="noel")d=make_stringf("effective weapon/unarmed skill -%d, AC/SH -%d; trained points unchanged",5+x/8,4+x/6);
    if(g=="watame")d=make_stringf("no natural HP regen; next 6 direct hits +40%% damage, capped at +%d per hit",10+x/2);
    if(g=="lamy")d=make_stringf("accuracy -%d, rC -1 (minimum rC-)",6+x/10);
    if(g=="polka")d=make_stringf("accuracy -%d, invisibility suppressed, stealth 0; noise %d",6+x/10,20+x/2);
    if(g=="hajime")d=make_stringf("EV -%d, melee accuracy -%d",4+x/8,4+x/10);
    if(g=="vivi")d=make_stringf("stealth 0, invisibility suppressed; direct hits +33%% damage, capped at +%d",10+x/2);
    if(!d.empty())return make_stringf("Wrath at current XL %d: %.1f turns: ",x,turns)+d+".";
    if(g=="miko")return make_stringf("Wrath: fixed 3x3 sanctuary warns for 2 turns, then lasts %.1f turns; no natural regen inside, 1d%d fire each turn; rF applies.",(100+3*x)/10.0,8+x/2);
    if(g=="pekora")return make_stringf("Wrath: two fixed radius-1 bombs after 2 turns, each 2d%d physical; AC applies; an adjacent escape cell stays clear.",8+x/2);
    if(g=="koyori")return make_stringf("Wrath: fixed 3x3 zone after 2 turns; either 3d%d fire (rF applies), or %.1f turns of +75%% movement time inside slime.",5+x,(100+3*x)/10.0);
    const int sides=g=="suisei" || g=="sopia"?8+x:g=="mela"?6+x:g=="su"?6+x:7+x;
    return make_stringf("Wrath at current XL %d: fixed %s after 2 turns, 3d%d %s; %s applies. Walls block it; allies may be hit.",x,g=="towa"?"single cell":"3x3 strike",sides,g=="mela"?"fire":"physical",g=="mela"?"rF":"AC");
}
''' +s[at:]
p.write_text(s,encoding='utf-8',newline='\n')
p=src/'holo-wrath.h';s=p.read_text(encoding='utf-8').replace('int shield();','int shield();\nint skill_penalty();\nstd::string description(const std::string &god);');p.write_text(s,encoding='utf-8',newline='\n')
p=src/'player.cc';s=p.read_text(encoding='utf-8');assert 'level-5*scale);' in s;s=s.replace('level-5*scale);','level-holo_wrath::skill_penalty()*scale);');p.write_text(s,encoding='utf-8',newline='\n')
p=src/'holo-campaign.cc';s=p.read_text(encoding='utf-8');a=s.index('    const std::vector<std::string> wrath={');b=s.index('    std::vector<std::string> lines=',a);s=s[:a]+s[b:];s=s.replace('lines.push_back(wrath[it-ids.begin()]);','lines.push_back(holo_wrath::description(g));').replace('Wrath ends after its event count or XP debt is paid. Rejoining never erases the debt.','New abandonment: 18 + piety/25 events (18-26), or XP equal to two XL advances (minimum 200). Current XL sets each new event. Rejoining never erases debt.');p.write_text(s,encoding='utf-8',newline='\n')
print('Updated wrath implementation, skill hook and player descriptions.')
