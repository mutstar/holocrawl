from pathlib import Path
import shutil,json,hashlib
root=Path(__file__).resolve().parents[1]
src=root/'engine/campaign-crawl/crawl-ref/source'
run=root/'analysis/native/fubuki-vfx05';run.mkdir(exist_ok=False)
files=['holo-visual.cc','holo-visual.h','holo-batch-summons.cc','rltiles/dc-holo-feat.txt']
for f in files:
    p=run/'before'/f;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/f,p)
shutil.copy2(root/'runtime/tiles01/HoloCrawl.exe',run/'before/HoloCrawl.exe')
def edit(f,a,b):
    p=src/f;s=p.read_text(encoding='utf-8');assert a in s,(f,a);p.write_text(s.replace(a,b),encoding='utf-8')
edit('holo-visual.h','foxshift,foxcircle,carrot','foxshift,foxcircle,foxhit,carrot')
edit('holo-visual.h','void fox_swap(const coord_def &from,const coord_def &to);','void fox_swap(const coord_def &from,const coord_def &to,const std::vector<coord_def> &hits);')
edit('rltiles/dc-holo-feat.txt','carrot HOLO_CARROT','fx_foxflame_0 HOLO_FX_FOXHIT_0\nfx_foxflame_1 HOLO_FX_FOXHIT_1\ncarrot HOLO_CARROT')
edit('holo-visual.cc','std::vector<coord_def> fox_arrivals;','std::vector<coord_def> fox_arrivals,fox_hits;')
edit('holo-visual.cc','if(fox_frame>=2 && area(p,fox_from,1))return effect::foxflame;','if(fox_frame>=2 && std::find(fox_hits.begin(),fox_hits.end(),p)!=fox_hits.end())return effect::foxhit;\n        if(fox_frame>=2 && area(p,fox_from,1))return effect::foxflame;')
edit('holo-visual.cc','fox_arrivals.clear();}','fox_arrivals.clear();fox_hits.clear();}')
edit('holo-visual.cc','void fox_swap(const coord_def &from,const coord_def &to) {','void fox_swap(const coord_def &from,const coord_def &to,const std::vector<coord_def> &hits) {')
edit('holo-visual.cc','fox_from=from;fox_to=to;play_fox_scene();','fox_from=from;fox_to=to;fox_hits=hits;play_fox_scene();')
edit('holo-visual.cc','kind==effect::foxshift || kind==effect::foxflame','kind==effect::foxshift || kind==effect::foxflame || kind==effect::foxhit')
# Record the actual hit count for every native scene frame.
edit('holo-visual.cc',',\\"newFoxes\\":',',\\"hitTargets\\":\\"PLACEHOLDER\\",\\"newFoxes\\":')
edit('holo-visual.cc','\\"PLACEHOLDER\\"','"<<fox_hits.size()<<"')
old='for(mid_t id:enemies(old,1)) { monster *mon=monster_by_mid(id);if(mon && mon->alive()) foxfire(*fox,*mon,roll_dice(1,6+s.inv/3),true); }'
new='''std::vector<coord_def> hit_positions;
                    for(mid_t id:enemies(old,1)) {
                        monster *mon=monster_by_mid(id);
                        if(mon && mon->alive()) {
                            const int before_hp=mon->hit_points;const coord_def hit_pos=mon->pos();
                            foxfire(*fox,*mon,roll_dice(1,6+s.inv/3),true);
                            if(mon->hit_points<before_hp)hit_positions.push_back(hit_pos);
                        }
                    }'''
edit('holo-batch-summons.cc',old,new)
edit('holo-batch-summons.cc','holo_visual::fox_swap(old,dest);','holo_visual::fox_swap(old,dest,hit_positions);')
# The original thorn/fire assets and all previously accepted art stay untouched.
preview=(root/'scripts/preview-fubuki-vfx04.py').read_text(encoding='utf-8').replace('fubuki-vfx04','fubuki-vfx05')
preview=preview.replace('불꽃은 실제 공격이 발생한 출발점을 기준으로 표시됩니다.','바닥 불꽃은 출발점을 기준으로 표시하고, 실제 HP 피해를 받은 적에게는 몸체 위 푸른 여우불을 따로 표시합니다. 지속 화상 상태를 추가하는 효과는 아닙니다.')
preview=preview.replace("assert review['afterFireHp']<review['beforeFireHp']","assert review['afterFireHp']<review['beforeFireHp']\nassert all(json.loads((raw/f'fubuki-swap-frame{f}-scene.json').read_text())['hitTargets']==1 for f in range(4))")
(root/'scripts/preview-fubuki-vfx05.py').write_text(preview,encoding='utf-8')
print('Prepared fubuki-vfx05; existing foxflame art reused as foreground hit cue.')
