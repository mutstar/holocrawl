from pathlib import Path
r=Path(__file__).resolve().parents[1];src=r/'engine/campaign-crawl/crawl-ref/source'
def edit(n,fn):
 p=src/n;s=p.read_text(encoding='utf-8');p.write_text(fn(s),encoding='utf-8')
def include(s):return s.replace('#include "AppHdr.h"','#include "AppHdr.h"\n#include "holo-lamy.h"',1)
edit('Makefile.obj',lambda s:s.replace('holo-sopia.o \\','holo-sopia.o \\\nholo-lamy.o \\',1))
edit('spl-cast.cc',lambda s:include(s).replace('    const int cap = spell_power_cap(spell);','    if(!fail_rate_check)power=holo_lamy::power(spell,power);\n    const int cap = spell_power_cap(spell);',1).replace('    spret cast_result = _do_cast(', '    holo_lamy::spell_scope lamy_cast(spell,allow_fail && fail==0 && !evoked_item);\n    spret cast_result = _do_cast(',1))
edit('monster.cc',lambda s:include(s).replace('        hit_points -= amount;','        hit_points -= amount;\n        holo_lamy::damage(*this,agent,amount,flavour,kill_type);',1))
edit('player.cc',lambda s:include(s).replace('invis_penalty+holo_wrath::evasion()','invis_penalty+holo_wrath::evasion()-holo_lamy::evasion_penalty()',1))
def batch(s):
 s=include(s)
 s=s.replace('        if(is(god_id::lamy) && !five()) bonus-=s.resource>80 ? 8 : s.resource>60 ? 4 : 0;','')
 s=s.replace('    if(is(god_id::lamy) && !five() && s.resource>60) percent+=15;','')
 s=s.replace('    if(flavour==BEAM_COLD && is(god_id::lamy) && ((passive() && s.resource>=20) || five())) return 1;','')
 a=s.index('int spell_failure(int raw)');b=s.index('int monster_armour',a);s=s[:a]+'int spell_failure(int raw) { return raw; }\n'+s[b:]
 s=s.replace('if(is(god_id::lamy) && moving && t.expires>now)\n        percent+=t.stacks*(mon.res_cold()>=2?5:10);','if(is(god_id::lamy) && moving && t.slowed_until>now)\n        percent=max(percent,150);')
 s=s.replace('multiplier(100)==115 && resistance(BEAM_COLD)==1','multiplier(100)==100 && resistance(BEAM_COLD)==0 && holo_lamy::power_bonus()==16 && holo_lamy::evasion_penalty()==3').replace('"high drunkenness has wrong direct damage"','"Lamy caster retained old melee/resistance modifiers"')
 return s
edit('holo-batch.cc',batch)
def resources(s):
 s=include(s)
 a=s.index('void chill(monster &mon');b=s.index('coord_def direction',a);s=s[:a]+s[b:]
 a=s.index('bool cone(');b=s.index('\n}\nint resource_action',a);s=s[:a]+s[b:]
 a=s.index('    if(is(god_id::lamy)) {');b=s.index('    return 0;',a);s=s[:a]+'    if(is(god_id::lamy))return holo_lamy::action();\n'+s[b:]
 a=s.index('    if(is(god_id::lamy)) {');b=s.index('\n}\nvoid resource_after_attack',a);s=s[:a]+'    if(is(god_id::lamy))holo_lamy::tick(at);'+s[b:]
 a=s.index('    if(is(god_id::lamy) && (passive()');b=s.index('\n}\nvoid resource_move',a);s=s[:a]+s[b:]
 return s
edit('holo-batch-resources.cc',resources)
def campaign(s):
 s=include(s).replace('if(g=="lamy")return {{"Drink (MP2, piety1)",1,0,0,0},{"Cold breath (MP3, piety3)",3,0,1,4},{"Banquet (MP6, piety12)",5,0,0,0}};','if(g=="lamy")return {{"Drink (MP2, piety1)",1,0,0,0},{"Snow banquet (MP6, piety12, intox40)",5,0,0,0}};')
 s=s.replace('    if(g=="okayu" && c.tier==1 && s.resource>=100)return "fullness is full";','    if(g=="lamy" && holo_batch::five())return "banquet active";\n    if(g=="lamy" && c.tier==1 && s.resource>=100)return "intoxication is full";\n    if(g=="lamy" && c.tier==5 && s.resource<40)return "need 40 intoxication";\n    if(g=="okayu" && c.tier==1 && s.resource>=100)return "fullness is full";')
 s=s.replace('if(g=="lamy" && direct && ((s.resource>=20&&s.resource<=60)||five()))++extra;','if(g=="lamy" && ordinary && ctx.kind==attack_kind::spell && holo_lamy::power_bonus()>0)++extra;')
 s=s.replace('Manage intoxication through drinking. Cold breath and banquet reward controlled levels.','Drink for attack-spell power. Direct spells build chill; Snow banquet adds frost bursts. Overdrinking reduces EV by3.')
 key='    if(g=="okayu")lines.push_back("3*: A foe'
 i=s.index(key);s=s[:i]+'''    if(g=="lamy")lines.push_back("1*: MP2/piety1, +40 intoxication, decay1/turn; >=20 attack spell power +(12+Inv/3)%, capped normally. >=70 EV-3; no failure penalty. 3*: passive, one chill/target/cast, expires6turns; third stack:2d(3+Inv/6) cold and movement +50% for2turns. 5*: requires40, consumes all; MP6/piety12,1turn; aftercast6+Inv/6 turns, treats intoxication as20. One burst/cast and per10aut:2d(5+Inv/3) cold at first hit, half adjacent, once-per-target chill. Cooldown15turns after end. No recursive/pet/cloud/poison procs.");
'''+s[i:]
 return s
edit('holo-campaign.cc',campaign)
def status(s):
 s=include(s).replace('// Current combat thresholds: new caster design remains a proposal.','// Caster redesign: 20..69 proper; >=70 overdrunk.')
 s=s.replace('amount>60','amount>=70')
 s=s.replace('        inf.short_text=make_stringf("Lamy:', '        const int bonus=holo_lamy::power_bonus();\n        if(bonus>0)inf.light_text+=make_stringf(" P+%d%%",bonus);\n        if(holo_lamy::evasion_penalty())inf.light_text+=" EV-3";\n        inf.short_text=make_stringf("Lamy:',1)
 return s
edit('status.cc',status)
def tests(s):
 s=include(s).replace('"Tipsy 40/100","Drunk 80/100","Banquet 6t"','"Tipsy 40/100 P+16%","Drunk 80/100 P+16% EV-3","Banquet 6t P+16%"').replace('info.light_text=="Banquet 5t"','info.light_text=="Banquet 5t P+16%"').replace('\\"combatRedesignApplied\\":false','\\"combatRedesignApplied\\":true')
 s=s.replace('cast(g,1,nullptr,origin);cast(g,3,m,aim);holo_batch::s.resource=65;cast(g,5,nullptr,origin);cast_count+=3;','cast(g,1,nullptr,origin);require(invoke(3,m,&aim)==0,"Lamy tier3 is passive");holo_batch::s.resource=65;cast(g,5,nullptr,origin);cast_count+=2;')
 s=s.replace('step(120);require(holo_batch::s.resource==0,"drunkenness stuck below unlock")','step(410);require(holo_batch::s.resource==0,"drunkenness stuck below unlock")')
 return s
edit('holo-campaign-test.cc',tests)
print('Caster hooks and legacy removal applied.')
