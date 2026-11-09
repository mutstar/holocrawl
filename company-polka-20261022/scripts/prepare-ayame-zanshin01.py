from pathlib import Path
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source';b=r/'analysis/native/ayame-zanshin01';b.mkdir(exist_ok=False)
def edit(name,fn):
    p=s/name;old=p.read_text(encoding='utf-8');new=fn(old);assert new!=old,name
    q=b/'before'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(old,encoding='utf-8');p.write_text(new,encoding='utf-8')
edit('holo-batch-internal.h',lambda t:t.replace('bool dream_sleep=false;','int ayame_zanshin_end=0; // Per-action snapshot; saved bank is state.tertiary.\n    bool dream_sleep=false;'))
def batch(t):
    anchor='    ctx.eligible=eligible(target);'
    t=t.replace(anchor,anchor+'''
    if(is(god_id::ayame) && you.piety>=50 && kind==attack_kind::melee && ctx.eligible
        && adjacent(you.pos(),target.pos()) && s.tertiary>you.elapsed_time
        && (s.marked!=target.mid || s.one_end<=you.elapsed_time))ctx.ayame_zanshin_end=s.tertiary;''')
    anchor='    if(ctx.damaged && ctx.eligible && !ctx.reward_kill && (!target || !target->alive())) on_kill('
    i=t.index(anchor);t=t[:i]+'''    if(is(god_id::ayame) && ctx.ayame_zanshin_end>0 && aut>0) {
        if(s.tertiary==ctx.ayame_zanshin_end)s.tertiary=0;
        ++s.totals.procs;
    }
'''+t[i:]
    anchor='            && adjacent(you.pos(),defender->pos())) bonus+=3+s.inv/6+(five() ? 4 : 0);'
    assert anchor in t;t=t.replace(anchor,anchor+'''
        else if(is(god_id::ayame) && ctx.ayame_zanshin_end>0 && ctx.target==defender->mid
            && adjacent(you.pos(),defender->pos()))bonus+=3+s.inv/6;''')
    anchor='        && adjacent(you.pos(),defender->pos())) return 2+s.inv/9+(five() ? 3 : 0);'
    assert anchor in t;t=t.replace(anchor,anchor+'''
    if(is(god_id::ayame) && ctx.ayame_zanshin_end>0 && ctx.target==defender->mid
        && adjacent(you.pos(),defender->pos()))return 2+s.inv/9;''')
    return t
edit('holo-batch.cc',batch)
def martial(t):
    t=t.replace('    if(is(god_id::ayame)) {\n        monster *mon=monster_by_mid(s.marked);','    if(is(god_id::ayame)) {\n        if(s.tertiary<=at || you.piety<50)s.tertiary=0;\n        monster *mon=monster_by_mid(s.marked);')
    anchor='    if(is(god_id::ayame) && five() && mid==s.marked) {'
    code='''    if(is(god_id::ayame) && you.piety>=50 && mid==s.marked && s.one_end>you.elapsed_time
        && direct && ordinary && ctx.kind==attack_kind::melee && ctx.eligible
        && adjacent(you.pos(),ctx.position))s.tertiary=you.elapsed_time+30;
'''
    assert anchor in t;return t.replace(anchor,code+anchor)
edit('holo-batch-martial.cc',martial)
edit('holo-worship.cc',lambda t:t.replace('current()=="aki" || current()=="fubuki"','current()=="aki" || current()=="fubuki" || current()=="ayame"').replace('id=="aki" || id=="fubuki"','id=="aki" || id=="fubuki" || id=="ayame"'))
def campaign(t):
    t=t.replace('holo_worship::current()=="aki" || holo_worship::current()=="fubuki"','holo_worship::current()=="aki" || holo_worship::current()=="fubuki" || holo_worship::current()=="ayame"')
    t=t.replace('g=="aki" || g=="fubuki")?"30 / 50 / 75 / 120"','g=="aki" || g=="fubuki" || g=="ayame")?"30 / 50 / 75 / 120"')
    anchor='    if(g=="fubuki")lines.push_back(std::string("2* passive Fox opening:'
    i=t.index(anchor);t=t[:i]+'''    if(g=="ayame")lines.push_back(make_stringf("2* passive Oni zanshin: %s | remaining %d aut",you.piety<50?"locked (piety50)":s.tertiary>you.elapsed_time?"ready: next new adjacent melee target gets1* hit/slaying":"needs a marked melee kill",std::max(0,s.tertiary-you.elapsed_time)));
'''+t[i:]
    anchor='    if(g=="fubuki")lines.push_back("2* passive Fox opening,'
    i=t.index(anchor);t=t[:i]+'''    if(g=="ayame")lines.push_back("2* passive Oni zanshin,piety50: direct adjacent melee kill of a live marked XP foe grants3turns of zanshin. Next new adjacent ordinary melee target gets1* accuracy3+Inv/6 and slaying2+Inv/9 on its first swing; consumes on attempt, even miss. Twin slash supports this; second swing uses ordinary mark bonuses. No extra EV,5* bonus,MP/piety/action cost or stacking. Cancelled/0time actions keep it; ranged/spell/reach/non-XP targets do not consume it.");
'''+t[i:]
    t=t.replace('    if(g=="miko")s.defence=0;','    if(g=="miko")s.defence=0;\n    if(g=="ayame")s.tertiary=0;')
    return t
edit('holo-campaign.cc',campaign)
print('Ayame zanshin bank, first-swing bonuses, attempt consumption and tier2 status implemented.')
