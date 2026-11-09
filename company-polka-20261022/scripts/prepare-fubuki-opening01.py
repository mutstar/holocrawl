from pathlib import Path
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source';b=r/'analysis/native/fubuki-opening01';b.mkdir(exist_ok=False)
def edit(name,fn):
    p=s/name;old=p.read_text(encoding='utf-8');new=fn(old);assert old!=new,name
    q=b/'before'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(old,encoding='utf-8');p.write_text(new,encoding='utf-8')
def summon(t):
    t=t.replace('t.raven_hits.clear();t.raven_hits[c.mid]=now+30;','t.raven_hits.clear();t.raven_hits[c.mid]=now+30;t.kind=0; // Fresh successful deception refreshes one opening.')
    anchor='''    const mid_t id=target->mid;
    for(auto &c:s.companions) {'''
    code='''    const mid_t id=target->mid;
    mid_t opening=MID_NOBODY;
    auto &deception=s.targets[id];
    if(you.piety>=50 && ctx.ordinary && ctx.primary && ctx.target==id && deception.kind==0) {
        for(const auto &link:deception.raven_hits) {
            monster *fox=monster_by_mid(link.first);const companion *c=find(link.first);
            if(link.second>you.elapsed_time && c && c->kind==2 && c->expires>you.elapsed_time
                && fox && fox->alive() && target->can_see(*fox) && you.can_see(*target) && you.can_see(*fox)
                && grid_distance(fox->pos(),target->pos())<=(five()?5:4) && line(fox->pos(),target->pos())) {
                opening=link.first;break;
            }
        }
    }
    for(auto &c:s.companions) {'''
    assert anchor in t;t=t.replace(anchor,code,1)
    anchor='''            foxfire(*fox,*target,div_rand_round(roll_dice(1,6+s.inv/3)*min(aut,10),10),false);
    }
}'''
    code='''            foxfire(*fox,*target,div_rand_round(roll_dice(1,6+s.inv/3)*min(aut,10),10),false);
    }
    target=monster_by_mid(id);monster *fox=monster_by_mid(opening);
    if(opening!=MID_NOBODY && target && target->alive() && fox && fox->alive()) {
        deception.kind=1;++s.totals.procs;
        foxfire(*fox,*target,div_rand_round(roll_dice(1,6+s.inv/3)*min(aut,10),10),false);
    }
}'''
    assert anchor in t;t=t.replace(anchor,code,1);return t
edit('holo-batch-summons.cc',summon)
edit('holo-worship.cc',lambda t:t.replace('current()=="miko" || current()=="aki"','current()=="miko" || current()=="aki" || current()=="fubuki"').replace('id=="miko" || id=="aki"','id=="miko" || id=="aki" || id=="fubuki"'))
def campaign(t):
    t=t.replace('holo_worship::current()=="miko" || holo_worship::current()=="aki"','holo_worship::current()=="miko" || holo_worship::current()=="aki" || holo_worship::current()=="fubuki"')
    t=t.replace('g=="miko" || g=="aki")?"30 / 50 / 75 / 120"','g=="miko" || g=="aki" || g=="fubuki")?"30 / 50 / 75 / 120"')
    anchor='    if(g=="aki")lines.push_back(make_stringf("2* passive Rose nourishment:'
    i=t.index(anchor);t=t[:i]+'''    if(g=="fubuki")lines.push_back(std::string("2* passive Fox opening: ")+(you.piety<50?"locked (piety50)":"first direct hit on deceived foe: its decoy fires one extra foxfire"));
'''+t[i:]
    anchor='    if(g=="aki")lines.push_back("1* active: MP3/1turn, fixed5x5 garden'
    i=t.index(anchor);t=t[:i]+'''    if(g=="fubuki")lines.push_back("2* passive Fox opening,piety50: first successful ordinary melee/ranged/direct spell hit on a living deceived foe triggers one extra foxfire from the decoy that deceived it. Once per successful deception, not per image. Miss retains it; expiry/dead or hidden decoy invalidates it. Normal hit,resistance and min(actionAut,10)/10 scaling apply. No extra MP/piety/turn cost. Divine powers,DoT,pets and0-time actions excluded.");
'''+t[i:]
    return t
edit('holo-campaign.cc',campaign)
print('Fubuki first-hit extra foxfire connected; existing saved target.kind tracks spent opening.')
