from pathlib import Path
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source';b=r/'analysis/native/aki-nutrient01';b.mkdir(exist_ok=False)
def edit(name,fn):
    p=s/name;old=p.read_text(encoding='utf-8');new=fn(old);assert old!=new,name
    q=b/'before'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(old,encoding='utf-8');p.write_text(new,encoding='utf-8')
def summons(t):
    t=t.replace('s.three_end>at?3:you.piety>=75?2:1','s.three_end>at?3:2')
    old='if(mon && mon->alive() && t.stacks>0) hurt(*mon,roll_dice(1,2+s.inv/6)+t.stacks);'
    new='''if(mon && mon->alive() && t.stacks>0) {
                    mon->props["holo_aki_garden_damage"]=true;
                    hurt(*mon,roll_dice(1,2+s.inv/6)+t.stacks);
                    if(mon->alive())mon->props.erase("holo_aki_garden_damage");
                }'''
    assert old in t;return t.replace(old,new)
edit('holo-batch-summons.cc',summons)
edit('holo-visual.cc',lambda t:t.replace('s.three_end>now?3:you.piety>=75?2:1','s.three_end>now?3:2'))
edit('holo-worship.cc',lambda t:t.replace('(current()=="suisei" || current()=="miko") && you.piety>=50','(current()=="suisei" || current()=="miko" || current()=="aki") && you.piety>=50').replace('(id=="suisei" || id=="miko") && p>=50','(id=="suisei" || id=="miko" || id=="aki") && p>=50').replace('current()=="miko"?"30 / 50 / 75 / 120"','(current()=="miko" || current()=="aki")?"30 / 50 / 75 / 120"'))
def campaign(t):
    t=t.replace('(threshold==50 && holo_worship::current()=="miko")','(threshold==50 && (holo_worship::current()=="miko" || holo_worship::current()=="aki"))')
    t=t.replace('g=="miko"?"30 / 50 / 75 / 120"','(g=="miko" || g=="aki")?"30 / 50 / 75 / 120"')
    anchor='    if(g=="aki" && direct && (s.targets[m.mid].stacks>=3 || m.props.exists("holo_bloom_three")))++extra;'
    new='''    if(g=="aki" && you.piety>=50 && s.one_end>you.elapsed_time && s.one_ready<=you.elapsed_time
        && grd(m.pos())==DNGN_FLOOR && grid_distance(s.centre,m.pos())<=(s.three_end>you.elapsed_time?3:2)
        && line(s.centre,m.pos()) && (s.targets[m.mid].stacks>=3 || m.props.exists("holo_bloom_three"))
        && you.elapsed_time>=s.rest[0]) {
        bool rose=false;
        if(pet && !invalid_monster_index(killer_index))for(const auto &c:s.companions)
            if(c.kind==1 && c.mid==menv[killer_index].mid){rose=true;break;}
        const bool own=direct || rose || m.props.exists("holo_aki_garden_damage")
            || (invoking==5 && m.props.exists("holo_bloom_three"));
        const int gain=std::min(std::min(3,1+s.inv/12),int(you.max_magic_points-you.magic_points));
        if(own && gain>0){inc_mp(gain);s.rest[0]=you.elapsed_time+30;++s.totals.procs;mprf(MSGCH_GOD,"Aki's garden restores %d MP.",gain);}
    }
'''+anchor
    assert anchor in t;t=t.replace(anchor,new)
    anchor='    if(g=="miko")lines.push_back(make_stringf("2* passive Blossom offering:'
    i=t.index(anchor);t=t[:i]+'''    if(g=="aki")lines.push_back(make_stringf("2* passive Rose nourishment: %s | MP gain %d | cooldown %d aut",you.piety<50?"locked (piety50)":"ready",std::min(3,1+s.inv/12),std::max(0,s.rest[0]-you.elapsed_time)));
'''+t[i:]
    anchor='    if(g=="miko")lines.push_back("2* passive Blossom offering,'
    i=t.index(anchor);t=t[:i]+'''    if(g=="aki")lines.push_back("1* active: MP3/1turn, fixed5x5 garden, blooms1turn after completion. 3* active: two attack roses, garden remains5x5. 5* active: temporary7x7 bloom. 2* passive Rose nourishment,piety50: XP foe with3thorn stacks dies inside garden to your direct attack,garden DoT or own rose: regain min(3,1+Inv/12)MP, max once per3turns. Bloom uses stacks before consumption. No extra resources/action. Full MP: no stored reward or cooldown spent.");
'''+t[i:]
    return t
edit('holo-campaign.cc',campaign)
print('Aki5/5/7 and MP-on-three-thorn-kill implemented; existing saved rest[0] used for cooldown.')
