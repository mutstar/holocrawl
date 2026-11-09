from pathlib import Path
r=Path(__file__).resolve().parents[1];p=r/'engine/campaign-crawl/crawl-ref/source/holo-campaign-test.cc';s=p.read_text();anchor='    // Approved extension: real tool use and saved per-use cloud attribution.'
test='''    if(const char *shots=getenv("HOLOCRAWL_LAMY_BANQUET_REVIEW")) {
        using namespace holo_batch;
        auto *m=fixture("lamy");const auto origin=you.pos();const auto centre=origin+coord_def(2,0);
        require(m->move_to_pos(centre),"Lamy banquet target placement");
        auto enemy=[&](const coord_def &p){auto mg=mgen_data::hostile_at(MONS_ETTIN,false,p);mg.flags|=MG_FORCE_PLACE;auto *n=create_monster(mg,false);require(n,"Lamy banquet enemy placement");n->speed=n->speed_increment=0;n->hit_points=n->max_hit_points=10000;return n;};
        auto *adj=enemy(centre+coord_def(0,1));auto *outside=enemy(centre+coord_def(2,0));
        auto shot=[&](const char *name){const auto before=signature();holo_visual::capture(std::string(shots)+"/lamy5-"+name+".png");require(before==signature(),"Lamy banquet screenshot mutated state/RNG");};
        auto active=[&](const coord_def &p){const auto e=holo_visual::at(p);return std::find(e.begin(),e.end(),holo_visual::effect::lamybanquetactive)!=e.end();};
        s.resource=40;shot("before");const int mp=you.magic_points,faith=you.piety;
        require(invoke(5)==10 && s.resource==0 && you.magic_points==mp-6 && you.piety==faith-12,"Lamy banquet native cost");
        const auto stable=signature();for(int f=0;f<4;++f)holo_visual::capture_invocation("lamy",origin,f,std::string(shots)+"/lamy5-cast"+std::to_string(f)+".png",5);
        require(stable==signature(),"Lamy activation frames changed state/RNG");
        step(10);require(s.five_end-you.elapsed_time==80 && active(you.pos()),"Lamy banquet eight turns and wreath active");shot("active");
        roundtrip();require(active(you.pos()),"Lamy banquet wreath follows saved buff");
        const auto old_pos=you.pos();you.turn_is_over=false;process_command(CMD_MOVE_LEFT);require(you.turn_is_over && you.pos()!=old_pos,"Lamy banquet ordinary movement");step(you.time_taken);
        require(active(you.pos()) && !active(old_pos),"Lamy banquet wreath follows player");shot("moved");
        set_skill_level(SK_CONJURATIONS,27);set_skill_level(SK_SPELLCASTING,27);you.duration[DUR_BRILLIANCE]=100;
        const int mhp=m->hit_points,ahp=adj->hit_points,ohp=outside->hit_points,procs=s.totals.procs;
        shot("hit-before");you.prev_targ=m->mindex();macro_buf_add_cmd(CMD_TARGET_SELECT);
        require(your_spells(SPELL_MAGIC_DART,40,true)==spret::success,"Lamy banquet real spell hit");
        require(s.totals.procs==procs+1 && m->hit_points<mhp && adj->hit_points<ahp && outside->hit_points==ohp,"Lamy banquet true 3x3 centre/splash/outside");
        require(s.targets[m->mid].stacks==1 && s.targets[adj->mid].stacks==1,"Lamy banquet chill dedup preserved");shot("hit-after");step(10);
        // Actual wand route drives the same target-centred rendering callback.
        set_skill_level(SK_EVOCATIONS,27);auto &wand=you.inv[20];wand=item_def();wand.base_type=OBJ_WANDS;wand.sub_type=WAND_FLAME;wand.quantity=1;wand.charges=20;wand.link=20;wand.pos=ITEM_IN_INVENTORY;wand.flags|=ISFLAG_IDENT_MASK;
        const int before_tool=s.totals.procs;shot("tool-before");
        for(int attempt=0;attempt<3 && s.totals.procs==before_tool;++attempt){you.prev_targ=m->mindex();macro_buf_add_cmd(CMD_TARGET_SELECT);zap_wand(20);if(s.totals.procs==before_tool)step(10);}
        require(s.totals.procs==before_tool+1,"Lamy banquet actual wand burst");shot("tool-after");
        const int end=s.five_end;step(std::max(1,end-you.elapsed_time));require(!five() && !active(you.pos()),"Lamy banquet wreath expiration");shot("expired");
        // A separate render-only wall control uses the exact same cell filter.
        const auto wall=centre+coord_def(1,-1);grd(wall)=DNGN_ROCK_WALL;invalidate_los();shot("wall-before");
        const auto control=signature();holo_visual::lamy_banquet_burst(centre);require(control==signature(),"Lamy blocked render control mutated state");
        grd(wall)=DNGN_FLOOR;invalidate_los();
        std::ofstream(dir+"/lamy-banquet-vfx.json")<<"{\\"status\\":\\"passed\\",\\"nativeActivation\\":true,\\"durationTurns\\":8,\\"playerFollowingWreath\\":true,\\"nativeMovement\\":true,\\"savedBuff\\":true,\\"actualSpellBurst\\":true,\\"actualWandBurst\\":true,\\"centreAndAdjacentDamaged\\":true,\\"outsideUnchanged\\":true,\\"chillDedup\\":true,\\"wreathExpired\\":true,\\"renderingStateUnchanged\\":true,\\"wallControlCaptured\\":true}\\n";
    }
'''
assert anchor in s;s=s.replace(anchor,test+anchor,1);p.write_text(s)
capture=(r/'scripts/capture-lamy-tools05.ps1').read_text(encoding='utf-8').replace('analysis/native/lamy-tools05','analysis/native/lamy-banquet-vfx01')
capture=capture.replace('$env:HOLOCRAWL_LAMY_TOOL_REVIEW=$shots;','$env:HOLOCRAWL_LAMY_TOOL_REVIEW=$shots;$env:HOLOCRAWL_LAMY_BANQUET_REVIEW=$shots;')
capture=capture.replace(" if((Get-Content (Join-Path $output 'validation.json')", " if((Get-Content (Join-Path $output 'lamy-banquet-vfx.json') -Raw | ConvertFrom-Json).status -ne 'passed'){throw 'Lamy banquet VFX checks failed.'}\n if((Get-Content (Join-Path $output 'validation.json')",1)
(r/'scripts/capture-lamy-banquet-vfx01.ps1').write_text(capture,encoding='utf-8')
print('Added real activation, save, movement, spell/wand impact, footprint and expiration captures.')
