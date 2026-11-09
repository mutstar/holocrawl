from pathlib import Path
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source'
b=r/'analysis/native/miko-passive01';b.mkdir(exist_ok=False)
def edit(name,fn):
    p=s/name;old=p.read_text(encoding='utf-8');new=fn(old);assert old!=new,name
    q=b/'before'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(old,encoding='utf-8');p.write_text(new,encoding='utf-8')
edit('holo-worship.cc',lambda t:t.replace('current()=="suisei" && you.piety>=50','(current()=="suisei" || current()=="miko") && you.piety>=50').replace('id=="suisei" && p>=50','(id=="suisei" || id=="miko") && p>=50').replace('current()=="suisei"?"30 / 50 / 75 / 100 / 120":"30 / 75 / 120"','current()=="suisei"?"30 / 50 / 75 / 100 / 120":current()=="miko"?"30 / 50 / 75 / 120":"30 / 75 / 120"'))
def campaign(t):
    t=t.replace('|| holo_worship::current()=="suisei") && before<threshold','|| holo_worship::current()=="suisei" || (threshold==50 && holo_worship::current()=="miko")) && before<threshold')
    t=t.replace('g=="suisei"?"30 / 50 / 75 / 100 / 120":"30 / 75 / 120"','g=="suisei"?"30 / 50 / 75 / 100 / 120":g=="miko"?"30 / 50 / 75 / 120":"30 / 75 / 120"')
    anchor='    if(g=="aki" && direct && (s.targets[m.mid].stacks>=3'
    i=t.index(anchor)
    t=t[:i]+'''    if(g=="miko" && direct && you.piety>=50 && you.hp>0
        && !you.duration[DUR_DEATHS_DOOR] && s.one_end>you.elapsed_time
        && seen(s.centre) && grid_distance(s.centre,you.pos())<=(five()?3:2)
        && grid_distance(s.centre,m.pos())<=(five()?3:2) && line(s.centre,m.pos())
        && you.elapsed_time>=s.proc_ready) {
        const int amount=2+s.inv/6,missing=max(0,you.hp_max-you.hp);
        heal(min(amount,missing));
        const int overflow=max(0,amount-missing);
        if(s.defence<=you.elapsed_time)s.shield=0;
        if(overflow>0){s.shield=min(4+s.inv/3,s.shield+overflow);s.defence=you.elapsed_time+50;}
        s.proc_ready=you.elapsed_time+20;++s.totals.procs;
        holo_visual::miko_recovery(m.pos());
    }
'''+t[i:]
    t=t.replace('    if(g=="raden")s.shield=0;','    if(g=="raden" || g=="miko")s.shield=0;\n    if(g=="miko")s.defence=0;')
    anchor='    if(g=="suisei")lines.push_back(std::string("2* Focused observation: ")'
    i=t.index(anchor);t=t[:i]+'''    if(g=="miko")lines.push_back(make_stringf("2* passive Blossom offering: %s | Shield %d/%d (%d aut)",you.piety<50?"locked (piety50)":"ready",s.shield,4+s.inv/3,max(0,s.defence-you.elapsed_time)));
'''+t[i:]
    anchor='    if(g=="suisei")lines.push_back("2* passive Focused observation'
    i=t.index(anchor);t=t[:i]+'''    if(g=="miko")lines.push_back("2* passive Blossom offering, piety50: direct XP-enemy kill with both in shrine heals2+Inv/6HP, once per2turns. Excess healing becomes shield, cap4+Inv/3HP, lasts5turns; renewed on overflow. Leaving shrine, floor change or new shrine removes it. No extra MP/piety/turn cost. Ordinary attacks, poison, clouds and traps can be absorbed; costs, torment and divine wrath are excluded.");
'''+t[i:]
    return t
edit('holo-campaign.cc',campaign)
def martial(t):
    t=t.replace('s.centre=you.pos();s.one_end=now+10+200','s.shield=0;s.defence=0;s.centre=you.pos();s.one_end=now+10+200')
    t=t.replace('void martial_tick(int at)\n{','void martial_tick(int at)\n{\n    if(is(god_id::miko) && (you.piety<50 || s.defence<=at || !in_shrine())){s.shield=0;s.defence=0;}')
    t=t.replace('void martial_move(const coord_def &old,bool voluntary)\n{','void martial_move(const coord_def &old,bool voluntary)\n{\n    if(is(god_id::miko) && !in_shrine()){s.shield=0;s.defence=0;}')
    anchor='    if(is(god_id::raden) && s.three_end>now && s.shield>0) {'
    code='''    if(is(god_id::miko)) {
        if(you.piety<50 || s.defence<=now || !in_shrine()){s.shield=0;s.defence=0;}
        const bool ordinary=kind==KILLED_BY_MONSTER || kind==KILLED_BY_BEAM || kind==KILLED_BY_DISINT
            || kind==KILLED_BY_POISON || kind==KILLED_BY_CLOUD || kind==KILLED_BY_TRAP
            || kind==KILLED_BY_FREEZING || kind==KILLED_BY_BURNING || kind==KILLED_BY_ACID
            || kind==KILLED_BY_CURARE || kind==KILLED_BY_SPORE || kind==KILLED_BY_HEADBUTT
            || kind==KILLED_BY_SPINES || kind==KILLED_BY_BARBS || kind==KILLED_BY_BEING_THROWN
            || kind==KILLED_BY_COLLISION;
        if(ordinary && damage>0 && s.shield>0){const int n=min(damage,s.shield);damage-=n;s.shield-=n;s.totals.absorbed+=n;}
    }
'''
    assert anchor in t;return t.replace(anchor,code+anchor)
edit('holo-batch-martial.cc',martial)
edit('holo-visual.h',lambda t:t.replace('void clear();','void miko_recovery(const coord_def &from);\nint miko_recovery_frame();\ncoord_def miko_recovery_delta();\nvoid clear();'))
def visual(t):
    t=t.replace('bool koyori_compact=false;','bool koyori_compact=false;\nint miko_live_frame=-1;\ncoord_def miko_live_from;')
    t=t.replace('void clear(){koyori_compact=false;','void clear(){miko_live_frame=-1;koyori_compact=false;')
    anchor='    // Visual boundary markers only: no actors, collision or additional terrain.'
    t=t.replace(anchor,'''    if(p==you.pos() && miko_live_frame>=1)return effect::mikoblossom;
    if(p==you.pos() && holo_campaign::active() && holo_worship::current()=="miko"
        && you.piety>=50 && holo_batch::s.shield>0 && holo_batch::s.defence>you.elapsed_time
        && holo_batch::s.one_end>you.elapsed_time && holo_batch::seen(holo_batch::s.centre)
        && grid_distance(p,holo_batch::s.centre)<=(holo_batch::five()?3:2))return effect::mikopetalshield;
'''+anchor)
    anchor='void choco_kiss(const coord_def &target,int damage,int healed) {'
    code='''int miko_recovery_frame() {
    return crawl_state.test && you.props.exists("holo_miko_bloom_frame")
        ?you.props["holo_miko_bloom_frame"].get_int():miko_live_frame;
}
coord_def miko_recovery_delta() {
    return miko_live_frame>=1?miko_live_from-you.pos():coord_def(1,0);
}
void miko_recovery(const coord_def &from) {
#ifdef USE_TILE_LOCAL
    if(holo_benchmark_active())return;
    const char *dir=crawl_state.test?getenv("HOLOCRAWL_MIKO_PASSIVE_REVIEW"):nullptr;
    if(crawl_state.test && !dir)return;
    const auto before=crawl_state.test?fox_signature():std::string();
    static int seq=0;const int n=++seq;miko_live_from=from;
    for(int f=1;f<=4;++f){
        miko_live_frame=f;const auto saved=rng::generators_to_vector();redraw_fox_actors();rng::load_generators(saved);
        if(dir)capture(std::string(dir)+"/miko-proc-"+std::to_string(n)+"-"+std::to_string(f)+".png",false);
        else scaled_delay(90);
    }
    miko_live_frame=-1;
    const auto saved=rng::generators_to_vector();redraw_fox_actors();rng::load_generators(saved);
    if(crawl_state.test && before!=fox_signature())throw std::runtime_error("Miko recovery animation changed gameplay/RNG");
#endif
}
'''
    assert anchor in t;return t.replace(anchor,code+anchor)
edit('holo-visual.cc',visual)
def renderer(t):
    t=t.replace('if(tileidx==TILE_HOLO_FX_MIKOBLOSSOM && crawl_state.test)','if(tileidx==TILE_HOLO_FX_MIKOBLOSSOM)')
    t=t.replace('const int f=you.props["holo_miko_bloom_frame"].get_int();\n            const int dx=(4-f)*12;','const int f=holo_visual::miko_recovery_frame();\n            const auto delta=holo_visual::miko_recovery_delta();\n            const int dx=(4-f)*12*delta.x,dy=(4-f)*12*delta.y;')
    for x,y in [('dx+8','-20'),('dx-4','-8'),('dx+2','6'),('dx-12','-24'),('dx-16','2')]:t=t.replace('x,y,'+x+','+y+');','x,y,'+x+',dy+('+y+'));')
    return t
edit('tiledgnbuf.cc',renderer)
print('Miko passive gameplay, saved fields, unlock/status, live approved VFX connected.')
