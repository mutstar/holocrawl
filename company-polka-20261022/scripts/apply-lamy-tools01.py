from pathlib import Path
import shutil,json,hashlib
r=Path(__file__).resolve().parents[1];src=r/'engine/campaign-crawl/crawl-ref/source';run=r/'analysis/native/lamy-tools01'
run.mkdir();(run/'before').mkdir()
names=['holo-lamy.h','holo-lamy.cc','spl-cast.cc','evoke.cc','cloud.cc','holo-campaign-test.cc']
for n in names:shutil.copy2(src/n,run/'before'/n)
shutil.copy2(r/'runtime/tiles01/HoloCrawl.exe',run/'before/HoloCrawl.exe')
(run/'plan.json').write_text(json.dumps(dict(revision='lamy-tools01',scope='Lamy tier3 tools/cloud support; tier1 power formula unchanged; tier5 shares use attribution and cloud burst limited once per use',rules=['direct damaging tool use: each hostile target once per use','all cloud cells/spread from same spell/tool use: each hostile target once on first positive damage','direct damage and cloud from same use deduplicated','zero damage/immune/friendly/enemy/pet/divine/shadow excluded','existing clouds before upgrade remain untagged','save through native level properties; no native save schema change'],checks=['actual wand zap','actual lamp of fire','cloud tick/movement/copy/expiry/replacement','direct+cloud dedup','3 stacks explosion','save and fresh-process continuation','22-god native regressions']),ensure_ascii=False,indent=2),encoding='utf-8')
p=src/'holo-lamy.h';s=p.read_text();s=s.replace('class actor;','class actor;\nstruct coord_def;')
s=s.replace('bool attack_spell', '''int cloud_use(const coord_def &pos);
void cloud_created(const coord_def &pos,const actor *agent);
void cloud_copy(const coord_def &from,const coord_def &to);
void cloud_clear(const coord_def &pos);
void cloud_swap(const coord_def &a,const coord_def &b);
bool attack_spell''',1)
s=s.replace('spell_scope(spell_type spell,bool ordinary);','spell_scope(spell_type spell,bool ordinary,bool tool=false,int cloud=0);');p.write_text(s)
p=src/'holo-lamy.cc';s=p.read_text();s=s.replace('#include <set>','#include <set>\n#include "env.h"\n#include "store.h"\n#include "stringutil.h"')
a=s.index('struct spell_scope::context');b=s.index('spell_scope::~spell_scope()',a)
s=s[:a]+'''// Per-level provenance uses native serialized env.properties. A whole cloud
// field and all of its descendants share one use and one set of hit MIDs.
namespace {
const char *cloud_key="holo_lamy_cloud_uses_v1";
CrawlHashTable &cloud_data() {
    if(!env.properties.exists(cloud_key))env.properties[cloud_key].new_table();
    auto &t=env.properties[cloud_key].get_table();
    if(!t.exists("cells"))t["cells"].new_table();
    if(!t.exists("uses"))t["uses"].new_table();
    if(!t.exists("next"))t["next"]=0;
    return t;
}
std::string cell_key(const coord_def &p){return make_stringf("%d,%d",p.x,p.y);}
CrawlHashTable &use_data(int id){return cloud_data()["uses"].get_table()[std::to_string(id)].get_table();}
int new_use() {
    auto &d=cloud_data();const int id=d["next"].get_int()+1;d["next"]=id;
    auto &v=d["uses"].get_table()[std::to_string(id)];v.new_table();v.get_table()["seen"].new_table();v.get_table()["burst"]=false;return id;
}
}
struct spell_scope::context {
    std::vector<std::pair<mid_t,coord_def>> hits;std::set<mid_t> seen;
    bool tool=false,cloud_tick=false;int group=0;
};
namespace {spell_scope::context *current=nullptr;}
int cloud_use(const coord_def &pos) {
    if(!env.properties.exists(cloud_key))return 0;
    auto &d=cloud_data();auto &cells=d["cells"].get_table();const auto key=cell_key(pos);
    return cells.exists(key)?cells[key].get_int():0;
}
void cloud_clear(const coord_def &pos) {
    if(env.properties.exists(cloud_key))cloud_data()["cells"].get_table().erase(cell_key(pos));
}
void cloud_copy(const coord_def &from,const coord_def &to) {
    const int id=cloud_use(from);cloud_clear(to);
    if(id)cloud_data()["cells"].get_table()[cell_key(to)]=id;
}
void cloud_swap(const coord_def &a,const coord_def &b) {
    const int x=cloud_use(a),y=cloud_use(b);cloud_clear(a);cloud_clear(b);
    if(y)cloud_data()["cells"].get_table()[cell_key(a)]=y;
    if(x)cloud_data()["cells"].get_table()[cell_key(b)]=x;
}
void cloud_created(const coord_def &pos,const actor *agent) {
    cloud_clear(pos);
    if(!current || !enabled() || !agent || !agent->is_player()
        || !holo_campaign::ordinary_damage() || internal_damage)return;
    if(!current->group) {
        current->group=new_use();auto &seen=use_data(current->group)["seen"].get_table();
        for(auto mid:current->seen)seen[std::to_string(mid)]=true;
    }
    cloud_data()["cells"].get_table()[cell_key(pos)]=current->group;
}
spell_scope::spell_scope(spell_type spell,bool ordinary,bool tool,int cloud):previous(current),cast(nullptr) {
    // Nested spell helpers of a real miscellaneous tool share its use identity.
    if(previous && previous->tool && !ordinary && !tool && !cloud) {current=previous;return;}
    const bool cloud_spell=spell!=SPELL_NO_SPELL && (get_spell_flags(spell)&spflag::cloud);
    if(enabled() && (tool || cloud>0 || (ordinary && (attack_spell(spell)||cloud_spell)))) {
        cast=new context;cast->tool=tool;cast->cloud_tick=cloud>0;cast->group=cloud;
    }
    // Divine/shadow helpers outside an actual item use cannot borrow a cast.
    current=cast;
}
void damage(monster &mon,const actor *source,int amount,beam_type flavour,kill_method_type kind) {
    if(!current || !tipsy() || amount<=0 || !source || !source->is_player()
        || internal_damage || !holo_campaign::ordinary_damage() || mon.attitude!=ATT_HOSTILE
        || kind==KILLED_BY_POISON || (kind==KILLED_BY_CLOUD && !current->cloud_tick)
        || flavour==BEAM_SHARED_PAIN || flavour==BEAM_STICKY_FLAME || flavour==BEAM_TORMENT_DAMAGE)return;
    if(current->group) {
        auto &seen=use_data(current->group)["seen"].get_table();const auto mid=std::to_string(mon.mid);
        if(seen.exists(mid))return;
        seen[mid]=true;
    }
    if(current->seen.insert(mon.mid).second)current->hits.push_back({mon.mid,mon.pos()});
}
'''+s[b:]
s=s.replace('if(five() && you.elapsed_time>=s.proc_ready) {','if(five() && you.elapsed_time>=s.proc_ready\n+            && (!cast->group || !use_data(cast->group)["burst"].get_bool())) {'.replace('\n+','\n'))
s=s.replace('            s.proc_ready=you.elapsed_time+10;','            if(cast->group)use_data(cast->group)["burst"]=true;\n            s.proc_ready=you.elapsed_time+10;',1)
p.write_text(s)
p=src/'spl-cast.cc';s=p.read_text().replace('holo_lamy::spell_scope lamy_cast(spell,allow_fail && fail==0 && !evoked_item);','holo_lamy::spell_scope lamy_cast(spell,allow_fail && fail==0 && !evoked_item,evoked_item && fail==0);');p.write_text(s)
p=src/'evoke.cc';s=p.read_text().replace('#include "evoke.h"','#include "evoke.h"\n#include "holo-lamy.h"',1)
needle='    if (entry && entry->evoke_func)\n'
assert needle in s;s=s.replace(needle,'    holo_lamy::spell_scope lamy_tool(SPELL_NO_SPELL,false,\n        item.base_type==OBJ_MISCELLANY || (entry && entry->evoke_func));\n\n'+needle,1);p.write_text(s)
p=src/'cloud.cc';s=p.read_text().replace('#include "cloud.h"','#include "cloud.h"\n#include "holo-lamy.h"',1)
# Every native copy/spread/move path carries the original use identity.
s=s.replace('env.cloud[*ai] = cloud;','env.cloud[*ai] = cloud;\n        holo_lamy::cloud_copy(cloud.pos,*ai);')
s=s.replace('            _los_cloud_changed(p, env.cloud[p].type, old);','            holo_lamy::cloud_copy(cloud.pos,p);\n            _los_cloud_changed(p, env.cloud[p].type, old);',1)
s=s.replace('    env.cloud.erase(p);','    holo_lamy::cloud_clear(p);\n    env.cloud.erase(p);',1)
s=s.replace('    env.cloud[newpos] = env.cloud[src];','    holo_lamy::cloud_copy(src,newpos);\n    holo_lamy::cloud_clear(src);\n    env.cloud[newpos] = env.cloud[src];',1)
s=s.replace('    cloud_struct temp = env.cloud[p1];','    holo_lamy::cloud_swap(p1,p2);\n    cloud_struct temp = env.cloud[p1];',1)
s=s.replace('    _los_cloud_changed(ctarget, env.cloud[ctarget].type, old);','    holo_lamy::cloud_created(ctarget,agent);\n    _los_cloud_changed(ctarget, env.cloud[ctarget].type, old);',1)
s=s.replace('        act->hurt(oppressor, final_damage, BEAM_MISSILE,','        holo_lamy::spell_scope lamy_cloud(SPELL_NO_SPELL,false,false,holo_lamy::cloud_use(act->pos()));\n        act->hurt(oppressor, final_damage, BEAM_MISSILE,',1);p.write_text(s)
print('Applied provenance-aware tool/cloud use scopes. Existing tier1 formula and visuals unchanged.')
