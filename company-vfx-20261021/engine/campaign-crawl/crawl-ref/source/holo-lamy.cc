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
        hurt(mon,roll_dice(2,3+s.inv/6),BEAM_COLD,false);
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
struct spell_scope::context { std::vector<std::pair<mid_t,coord_def>> hits;std::set<mid_t> seen; };
namespace {spell_scope::context *current=nullptr;}
spell_scope::spell_scope(spell_type spell,bool ordinary):previous(current),cast(nullptr) {
    if(ordinary && enabled() && attack_spell(spell))cast=new context;
    // Nested god/shadow/evoked casts must not borrow the player's cast identity.
    current=cast;
}
void damage(monster &mon,const actor *source,int amount,beam_type flavour,kill_method_type kind) {
    if(!current || !tipsy() || amount<=0 || !source || !source->is_player()
        || internal_damage || !holo_campaign::ordinary_damage() || mon.attitude!=ATT_HOSTILE
        || kind==KILLED_BY_POISON || kind==KILLED_BY_CLOUD || flavour==BEAM_SHARED_PAIN
        || flavour==BEAM_STICKY_FLAME || flavour==BEAM_TORMENT_DAMAGE)return;
    if(current->seen.insert(mon.mid).second)current->hits.push_back({mon.mid,mon.pos()});
}
spell_scope::~spell_scope() {
    current=nullptr;
    if(cast && enabled() && tipsy() && !cast->hits.empty()) {
        std::set<mid_t> chilled;
        if(you.piety>=75 || five())for(const auto &hit:cast->hits) {
            auto *m=monster_by_mid(hit.first);if(m && m->alive()){chilled.insert(m->mid);chill(*m);}
        }
        if(five() && you.elapsed_time>=s.proc_ready) {
            s.proc_ready=you.elapsed_time+10;const auto centre=cast->hits.front().second;
            const int raw=roll_dice(2,5+s.inv/3);++s.totals.procs;
            const auto victims=enemies(centre,1,false,true);
            holo_visual::invocation("lamy",3,centre);
            for(auto id:victims) {
                auto *m=monster_by_mid(id);if(!m || !m->alive() || !line(centre,m->pos()))continue;
                hurt(*m,m->pos()==centre?raw:raw/2,BEAM_COLD,false);
                if(m->alive() && chilled.insert(id).second)chill(*m);
            }
        }
    }
    delete cast;current=previous;
}
}
