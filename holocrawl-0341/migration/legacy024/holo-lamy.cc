#include "AppHdr.h"
#include "holo-lamy.h"
#include "holo-batch-internal.h"
#include "holo-campaign.h"
#include "holo-visual.h"
#include "mon-util.h"
#include "monster.h"
#include "player.h"
#include "spl-util.h"
#include "spl-cast.h"
#include <set>
#include "env.h"
#include "store.h"
#include "stringutil.h"
namespace holo_lamy {
using namespace holo_batch;
namespace {
bool enabled(){return is(god_id::lamy);}
bool tipsy(){return enabled() && (five() || s.resource>=20);}
void redraw(){you.redraw_status_lights=true;you.redraw_evasion=true;}
void chill(monster &mon) {
    auto &t=s.targets[mon.mid];const int now=you.elapsed_time;
    if(t.expires<=now)t.stacks=0;
    ++t.stacks;t.expires=now+60;
    if(t.stacks>=3) {
        t.stacks=0;t.slowed_until=now+20;
        const auto pos=mon.pos();
        hurt(mon,roll_dice(2,3+s.inv/6),BEAM_COLD,false);
        holo_visual::lamy_chill_burst(pos);
    }
}
}
bool attack_spell(spell_type spell) {
    if(spell==SPELL_NO_SPELL)return false;
    const auto flags=get_spell_flags(spell);const auto schools=get_spell_disciplines(spell);
    if(flags & (spflag::helpful|spflag::neutral|spflag::cloud))return false;
    if(schools & spschool::summoning)return false;
    if(!(spell_harms_target(spell)||spell_harms_area(spell)))return false;
    if(spell==SPELL_POISONOUS_VAPOURS || spell==SPELL_OLGREBS_TOXIC_RADIANCE
        || spell==SPELL_TORNADO || spell==SPELL_FULMINANT_PRISM)return false;
    return !(schools & spschool::hexes) || (schools & spschool::conjuration);
}
int power_bonus(){return tipsy()?12+s.inv/3:0;}
int power(spell_type spell,int base){return attack_spell(spell)?base*(100+power_bonus())/100:base;}
int evasion_penalty(){return enabled() && !five() && s.resource>=70?3:0;}
int action() {
    if(!enabled())return 0;const int now=you.elapsed_time;
    if(want(5) && !five() && s.resource>=40 && now>=s.five_ready && pay(6,12,120)) {
        s.resource=0;s.five_end=now+10+10*(6+s.inv/6);s.five_ready=s.five_end+150;s.proc_ready=now;
        redraw();return 10;
    }
    if(want(1) && !five() && s.resource<100 && pay(2,1)) {
        s.resource=min(100,s.resource+40);redraw();return 10;
    }
    return 0;
}
void tick(int at) {
    if(!enabled())return;
    if(at%10==0 && at>=s.five_end && s.resource>0){--s.resource;redraw();}
    for(auto &p:s.targets)if(p.second.expires<=at)p.second.stacks=0;
}
// Per-level provenance uses native serialized env.properties. A whole cloud
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
    const bool cloud_spell=spell!=SPELL_NO_SPELL && ((get_spell_flags(spell)&spflag::cloud)
        || spell==SPELL_CONJURE_FLAME || spell==SPELL_POISONOUS_VAPOURS);
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
spell_scope::~spell_scope() {
    current=nullptr;
    if(cast && enabled() && tipsy() && !cast->hits.empty()) {
        std::set<mid_t> chilled;
        if(you.piety>=75 || five())for(const auto &hit:cast->hits) {
            auto *m=monster_by_mid(hit.first);if(m && m->alive()){chilled.insert(m->mid);chill(*m);}
        }
        if(five() && you.elapsed_time>=s.proc_ready
            && (!cast->group || !use_data(cast->group)["burst"].get_bool())) {
            if(cast->group)use_data(cast->group)["burst"]=true;
            s.proc_ready=you.elapsed_time+10;const auto centre=cast->hits.front().second;
            const int raw=roll_dice(2,5+s.inv/3);++s.totals.procs;
            const auto victims=enemies(centre,1,false,true);
            holo_visual::lamy_banquet_burst(centre);
            for(auto id:victims) {
                auto *m=monster_by_mid(id);if(!m || !m->alive() || !line(centre,m->pos()))continue;
                hurt(*m,m->pos()==centre?raw:raw/2,BEAM_COLD,false);
                if(m->alive() && chilled.insert(id).second) {
                    if(cast->group) {
                        auto &seen=use_data(cast->group)["seen"].get_table();const auto mid=std::to_string(id);
                        if(seen.exists(mid))continue;
                        seen[mid]=true;
                    }
                    chill(*m);
                }
            }
        }
    }
    delete cast;current=previous;
}
}
