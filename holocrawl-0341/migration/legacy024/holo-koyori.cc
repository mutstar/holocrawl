#include "AppHdr.h"
#include "holo-koyori.h"
#include "holo-batch-internal.h"
#include "holo-campaign.h"
#include "holo-visual.h"
#include "holo-worship.h"
#include "monster.h"
#include "mon-util.h"
#include "mon-ench.h"
#include "player.h"
#include "random.h"
#include "stringutil.h"
#include "spl-util.h"
#include <algorithm>
namespace holo_koyori {
using namespace holo_batch;
bool enabled(){return holo_campaign::active() && is(god_id::koyori);}
void initialise(){
    if(!enabled() || you.props.exists("holo_koyori_caster_v1"))return;
    // Old reagent inventory/coat/critical fields cannot become new charges.
    s.resource=s.offence=s.exhibit=s.one_end=s.three_end=s.five_end=0;
    s.one_ready=s.three_ready=s.five_ready=0;
    for(int &n:s.stock)n=0;
    s.targets.clear();s.hazards.clear();you.props["holo_koyori_caster_v1"]=true;
}
bool attack_spell(spell_type spell){
    if(spell==SPELL_NO_SPELL)return false;
    const auto flags=get_spell_flags(spell);const auto schools=get_spell_disciplines(spell);
    if(flags&(spflag::helpful|spflag::neutral|spflag::cloud))return false;
    if(schools&spschool::summoning)return false;
    if(spell==SPELL_POISONOUS_VAPOURS || spell==SPELL_OLGREBS_TOXIC_RADIANCE
        || spell==SPELL_TORNADO || spell==SPELL_FULMINANT_PRISM)return false;
    return spell_harms_target(spell)||spell_harms_area(spell);
}
bool range_bonus(spell_type spell,int maxrange){
    return enabled() && you.piety>=75 && maxrange>1 && attack_spell(spell)
        && spell!=SPELL_GLACIATE && spell!=SPELL_THUNDERBOLT
        && (get_spell_flags(spell)&spflag::targeting_mask);
}
int next_type(){
    if(s.five_end>you.elapsed_time && s.offence>0){static const int first[]={2,1,3};return first[std::max(0,s.exhibit)%3];}
    static const int order[]={2,3,1};return order[std::max(0,s.resource)%3];
}
int action(){
    if(!enabled() || !want(5) || manual_option!=0 || s.five_end>you.elapsed_time
        || s.five_ready>you.elapsed_time || !pay(6,10,120))return 0;
    s.five_end=you.elapsed_time+5+80;s.five_ready=you.elapsed_time+200;
    s.offence=4;s.exhibit=0;return 5;
}
std::string status(){
    static const char *names[]={"","Poison","Heat","Cold"};
    std::string text=std::string("Next reagent: ")+names[next_type()];
    if(s.five_end>you.elapsed_time && s.offence>0)
        {static const char *pairs[]={"Heat+Cold","Poison+Heat","Cold+Poison"};
        text=make_stringf("Next %s | Critical %d casts / %.1ft",pairs[std::max(0,s.exhibit)%3],s.offence,(s.five_end-you.elapsed_time)/10.0);}
    if(you.piety>=75)text+=" | attack spell range +1";
    return text;
}
int reaction_damage(int raw,int pair,bool critical){
    const int multiplier=critical?(pair==5?150:135):100;
    return std::max(1,raw*85*multiplier/10000);
}
namespace {
void single(monster &m,int type){
    auto &t=s.targets[m.mid];t.kind=type;t.expires=you.elapsed_time+60;t.stacks=0;
    if(type==1){t.stacks=2;t.next=you.elapsed_time+10;}
    else if(type==2)hurt(m,roll_dice(1,4+s.inv/6),BEAM_FIRE,false,true);
    else {t.root=you.elapsed_time+20;hurt(m,roll_dice(1,3+s.inv/9),BEAM_COLD,false,true);}
}
void reaction(monster &m,int pair,bool critical){
    auto &t=s.targets[m.mid];t.kind=t.stacks=t.expires=0;
    const auto centre=m.pos();++s.totals.procs;
    holo_campaign::reaction_scope credit(pair,m);
    if(pair==5){
        int raw=reaction_damage(roll_dice(3,6+s.inv/4),pair,critical);
        if(!critical)raw=m.apply_ac(raw,0,ac_type::half);
        hurt(m,raw,BEAM_MISSILE,false,true);
    }else{
        const int raw=reaction_damage(roll_dice(2,pair==3?5+s.inv/4:3+s.inv/6),pair,critical);
        for(mid_t id:enemies(centre,1,false,true)){
            auto *v=monster_by_mid(id);if(!v || !v->alive() || !line(centre,v->pos()))continue;
            if(pair==4){
                if(critical)s.targets[id].weak_until=you.elapsed_time+40;
                else s.targets[id].slowed_until=you.elapsed_time+30;
            }
            hurt(*v,raw,pair==3?BEAM_FIRE:BEAM_MISSILE,pair==4,true);
        }
    }
    holo_visual::koyori_reaction(centre,pair,critical);
}
}
void tick(int at){
    if(!enabled())return;
    if(at>=s.five_end)s.offence=0;
    for(auto &entry:s.targets){
        auto &t=entry.second;
        if(at>=t.expires){t.kind=t.stacks=0;continue;}
        auto *m=monster_by_mid(entry.first);
        if(m && m->alive() && t.kind==1 && t.stacks>0 && at>=t.next){
            t.next+=10;--t.stacks;hurt(*m,2+s.inv/12,BEAM_POISON,false,false);
        }
    }
}
int movement(const monster &m,int base){
    if(!enabled() || m.has_ench(ENCH_SLOW))return base;
    auto it=s.targets.find(m.mid);if(it==s.targets.end())return base;
    const auto &t=it->second;const int now=you.elapsed_time;
    const int percent=t.weak_until>now?50:t.slowed_until>now?35:t.root>now?15:0;
    return (base*(100+percent)+99)/100;
}
int mark(const coord_def &p){
    if(!enabled() || you.piety<30)return 0;
    if(p==you.pos())return next_type();
    auto *m=monster_at(p);if(!m || !you.can_see(*m))return 0;
    auto it=s.targets.find(m->mid);
    return it!=s.targets.end() && it->second.expires>you.elapsed_time?it->second.kind:0;
}
struct spell_scope::context{
    std::vector<std::pair<mid_t,coord_def>> hits;std::set<mid_t> seen;
    coord_def aim;int type=0,pair=0;bool critical=false;
};
namespace {spell_scope::context *current=nullptr;}
bool direct_cast(){return current && enabled();}
spell_scope::spell_scope(spell_type spell,bool ordinary,const coord_def &aim):previous(current),cast(nullptr){
    if(enabled() && you.piety>=30 && ordinary && attack_spell(spell)){
        cast=new context;cast->aim=aim;cast->type=next_type();
        cast->critical=s.five_end>you.elapsed_time && s.offence>0;
        if(cast->critical){static const int pairs[]={5,3,4};cast->pair=pairs[std::max(0,s.exhibit)%3];}
    }
    current=cast;
}
void damage(monster &m,const actor *source,int amount,beam_type flavour,kill_method_type kind){
    if(!current || amount<=0 || !source || !source->is_player() || internal_damage
        || !holo_campaign::ordinary_damage() || m.attitude!=ATT_HOSTILE
        || kind==KILLED_BY_POISON || kind==KILLED_BY_CLOUD
        || flavour==BEAM_SHARED_PAIN || flavour==BEAM_STICKY_FLAME || flavour==BEAM_TORMENT_DAMAGE)return;
    if(current->seen.insert(m.mid).second)current->hits.push_back({m.mid,m.pos()});
}
spell_scope::~spell_scope(){
    current=nullptr;
    if(cast && enabled() && !cast->hits.empty()){
        s.resource=(std::max(0,s.resource)+1)%3;
        std::stable_sort(cast->hits.begin(),cast->hits.end(),[&](const std::pair<mid_t,coord_def> &a,const std::pair<mid_t,coord_def> &b){
            return grid_distance(a.second,cast->aim)<grid_distance(b.second,cast->aim);
        });
        bool reacted=false;
        for(const auto &hit:cast->hits){
            auto *m=monster_by_mid(hit.first);if(!m || !m->alive())continue;
            const auto &t=s.targets[m->mid];const int old=t.expires>you.elapsed_time?t.kind:0;
            const int pair=cast->critical?cast->pair:old+cast->type;
            if(!reacted && you.piety>=75 && (cast->critical || (old && old!=cast->type))){
                reaction(*m,pair,cast->critical);reacted=true;
            }else single(*m,cast->type);
        }
        if(cast->critical){++s.exhibit;if(--s.offence<=0)s.five_end=0;}
        you.redraw_status_lights=true;
    }
    delete cast;current=previous;
}
}
