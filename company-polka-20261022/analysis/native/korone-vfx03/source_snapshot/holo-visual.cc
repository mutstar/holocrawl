#include "AppHdr.h"
#include "holo-visual.h"
#include "holo-worship.h"
#include "holo-campaign.h"
#include "holo-batch-internal.h"
#include "holo-sopia.h"
#include "holo-wrath.h"
#include "holocrawl.h"
#include "env.h"
#include "menu.h"
#include "player.h"
#include "state.h"
#include "random.h"
#include "store.h"
#include "stringutil.h"
#include "terrain.h"
#include "act-iter.h"
#include <algorithm>
#include <stdexcept>
#include <fstream>
#include <sstream>
#include "tags.h"
#include "show.h"
#include "coordit.h"
#ifdef USE_TILE
#include "tiledef-dngn.h"
#include "tiledef-main.h"
#include "tile-flags.h"
#include "tiledef-player.h"
#include "tiledoll.h"
#include "tilepick.h"
#include "tilepick-p.h"
#include "options.h"
#endif
#ifdef USE_TILE_LOCAL
#include "tilesdl.h"
#include "libutil.h"
#include "view.h"
#include "output.h"
#include "tileview.h"
#include "tiledoll.h"
#include "losglobal.h"
#include <SDL.h>
#include <SDL_opengl.h>
#include <SDL_image.h>
#endif

namespace holo_visual {
namespace {
const char *altar_key="holocrawl_altar_art";
std::string position(const coord_def &p){return make_stringf("%d,%d",p.x,p.y);}
std::vector<coord_def> flashes;
effect flash_kind=effect::none;
int flash_frame=0;
int fox_scene=0,fox_frame=0;
coord_def fox_from,fox_to;
std::vector<coord_def> fox_arrivals,fox_hits;
const std::vector<std::string> night_gods={"korone","okayu","pekora","noel","watame","towa","lamy","polka","koyori","lui","raden","hajime","su","vivi","sopia","mela"};
effect night_effect(const std::string &g,int tier,int option=0) {
    const auto it=std::find(night_gods.begin(),night_gods.end(),g);
    if(it==night_gods.end())return effect::none;
    if(g=="polka" && tier==5 && option==1)return effect::night_polkaheal;
    if(g=="polka" && tier==5 && option==2)return effect::night_polkachaos;
    if(g=="raden" && tier==3 && option==1)return effect::night_radenstone;
    if(g=="raden" && tier==3 && option==2)return effect::night_radencraft;
    return effect(int(effect::night_korone1)+3*int(it-night_gods.begin())+(tier==1?0:tier==3?1:2));
}
int night_span(effect e) {
    if(e>=effect::night_korone1 && e<=effect::night_mela5)return (int(e)-int(effect::night_korone1))%3==0?1:(int(e)-int(effect::night_korone1))%3==1?3:5;
    if(e==effect::night_polkaheal || e==effect::night_polkachaos)return 5;
    if(e==effect::night_radenstone || e==effect::night_radencraft)return 3;
    return 0;
}
effect night_status(const coord_def &p) {
    if(p!=you.pos() || !holo_campaign::active() || you.piety<30)return effect::none;
    const auto g=holo_worship::current();const auto &s=holo_batch::s;const int now=you.elapsed_time;
    bool on=false;
    if(g=="noel")on=holo_campaign::noel_fighting_bonus(1)>0 || holo_campaign::noel_commander();
    else if(g=="sopia")on=holo_sopia::visual_at(p+coord_def(1,0))!=effect::none;
    else if(g=="korone" || g=="lamy" || g=="hajime")on=s.resource>0;
    else if(g=="okayu")on=s.resource>0 || s.shield>0;
    else if(g=="watame")on=you.hp<you.hp_max || s.three_end>now || s.five_end>now;
    else if(g=="towa" || g=="su" || g=="mela")on=true; // passive readiness, not a hit assertion
    else if(g=="raden")on=true; // current exhibit readiness
    else if(g=="koyori")on=s.stock[0]+s.stock[1]+s.stock[2]>0 || holo_campaign::reactions_enabled();
    else if(g=="lui")on=!s.companions.empty();
    else if(g=="vivi" || g=="polka")on=s.one_end>now || s.five_end>now;
    return on?night_effect(g,1):effect::none;
}

effect choco_mark(const coord_def &p) {
    if(!holo_campaign::active() || holo_worship::current()!="choco")return effect::none;
    const auto &s=holo_batch::s;const auto *mon=monster_by_mid(s.marked);
    if(!mon || !mon->alive() || mon->pos()!=p || !you.can_see(*mon))return effect::none;
    if(s.secondary<0 && s.five_end>you.elapsed_time && mon->attitude==ATT_FRIENDLY
        && mon->props.exists("holo_charmed"))return effect::chocobond;
    if(s.secondary>=0 && s.one_end>you.elapsed_time && s.resource>0)
        return effect(int(effect::chocoheart1)+std::min(5,s.resource)-1);
    return effect::none;
}
bool choco_large(effect e) {
    return (e>=effect::chocoheart1 && e<=effect::chocoheart5) || e==effect::chocowings
        || e==effect::chocobond || (e>=effect::chocoabsorb0 && e<=effect::chocoabsorb7);
}
bool area(const coord_def &p,const coord_def &centre,int radius) {
    return grid_distance(p,centre)<=radius && holo_batch::line(centre,p);
}
effect fox_cue_at(const coord_def &p) {
    if(fox_scene==1) {
        if(fox_frame<2 && (p==fox_from || p==fox_to))return effect::foxshift;
        if(fox_frame>=2 && std::find(fox_hits.begin(),fox_hits.end(),p)!=fox_hits.end())return effect::foxhit;
        if(fox_frame>=2 && area(p,fox_from,1))return effect::foxflame;
    }
    if(fox_scene==2 && !fox_arrivals.empty()
        && p==fox_arrivals[std::min(int(fox_arrivals.size())-1,fox_frame/2)])return effect::foxcircle;
    return effect::none;
}
std::string fox_signature() {
    std::ostringstream o;std::vector<unsigned char> bytes;
    {writer out(&bytes);rng::generators_to_vector().write(out);}
    o<<you.pos().x<<','<<you.pos().y<<','<<you.trapped<<','<<you.exploration<<'|'<<you.hp<<' '<<you.magic_points<<' '<<int(you.piety)<<' '<<you.elapsed_time<<'|'<<holo_batch::save_campaign()<<'|'<<holo_sopia::save_campaign()<<'|'<<holo_wrath::status();
    for(auto n:bytes)o<<int(n)<<',';
    for(monster_iterator mi;mi;++mi)o<<'|'<<mi->mid<<':'<<mi->pos().x<<','<<mi->pos().y<<','<<mi->hit_points<<','<<mi->foe<<','<<int(mi->attitude);
    return o.str();
}
#ifdef USE_TILE_LOCAL
void redraw_fox_actors() {
    // Refresh only already-known actor cells. Full exploration updates would
    // roll native exploration traps and must wait for the normal game turn.
    // Rebase cached tiles after the real player position changed, updating
    // known actors without player_view_update()/exploration conduct or traps.
    tile_draw_floor();
    for(radius_iterator ri(you.pos(),LOS_DEFAULT);ri;++ri)
        if(in_bounds(*ri) && you.see_cell(*ri) && env.map_knowledge(*ri).known())show_update_at(*ri);
    tiles.invalidate_dungeon_overlays();viewwindow(false,true);update_screen();
}
#endif
void play_fox_scene() {
    const char *dir=crawl_state.test?getenv("HOLOCRAWL_FUBUKI_REVIEW"):nullptr;
    const int frames=fox_scene==1?4:2*fox_arrivals.size();
    const auto before=crawl_state.test?fox_signature():std::string();
    for(int f=0;f<frames;++f) {
        fox_frame=f;
        if(dir && *dir) {
            const auto stem=std::string(dir)+(fox_scene==1?"/fubuki-swap-frame":"/fubuki-gather-frame")+std::to_string(f);
#ifdef USE_TILE_LOCAL
            const auto rng_state=rng::generators_to_vector();
            redraw_fox_actors();rng::load_generators(rng_state);
#endif
            // Read the exact actor-refresh path used in normal animation.
            capture(stem+".png",false);
            std::ofstream meta(stem+"-scene.json");
            meta<<"{\"frame\":"<<f<<",\"scene\":"<<fox_scene<<",\"from\":["<<fox_from.x<<','<<fox_from.y<<"],\"to\":["<<fox_to.x<<','<<fox_to.y<<"],\"hitTargets\":"<<fox_hits.size()<<",\"newFoxes\":"<<fox_arrivals.size()<<",\"revealed\":"<<(fox_scene==2?(f+1)/2:0)<<"}\n";
        }
#ifdef USE_TILE_LOCAL
        else if(!crawl_state.test) {
            // Rebuild the actor view after the real position change, keeping
            // every gameplay RNG stream intact throughout the UI redraw.
            const auto rng_state=rng::generators_to_vector();
            redraw_fox_actors();
            rng::load_generators(rng_state);scaled_delay(95);
        }
#endif
    }
    clear();
    if(crawl_state.test && before!=fox_signature())throw std::runtime_error("Fox scene changed gameplay/RNG");
#ifdef USE_TILE_LOCAL
    if(!crawl_state.test) { const auto rng_state=rng::generators_to_vector();redraw_fox_actors();rng::load_generators(rng_state); }
#endif
}
void prepare_invocation(const std::string &g,int tier,const coord_def &p,bool impact_phase=false,int option=0) {
    flashes.clear();flash_kind=invocation_effect(g);
    const auto style=(g=="pekora" && (tier==3 || tier==5))?night_effect(g,1):night_effect(g,tier,option);
    if(style!=effect::none) {
        flash_kind=style;coord_def centre=p;
        if(g=="sopia" && (tier==3 || tier==5))centre=holo_sopia::field_centre();
        else if(g=="towa" && tier==5)centre=holo_batch::s.centre;
        else if(tier==5 && g!="sopia" && g!="okayu" && !(g=="polka" && option==0))centre=you.pos();
        if(tier==1 && g!="pekora")centre=you.pos();
        flashes.push_back(centre);return;
    }
    if(g=="choco") {
        flash_kind=tier==3?effect::chocokiss:tier==5?effect::chocowings:effect::chocoheart1;
        flashes.push_back(p);return;
    }
    if(g=="ayame" && (tier==3 || tier==5)) {
        flash_kind=tier==3?effect::ayameslash:effect::ayameduel;
        flashes.push_back(tier==3?p:holo_batch::s.centre);return;
    }
    if(g=="aki" && tier==5) {
        flash_kind=effect::akibloom;
        if(in_bounds(holo_batch::s.centre) && you.see_cell(holo_batch::s.centre))flashes.push_back(holo_batch::s.centre);
        return;
    }
    if(g=="miko" && tier==3) {
        flash_kind=effect::mikoflame;
        const int radius=holo_batch::five()?3:you.piety>=75?2:1;
        for(int x=-radius;x<=radius;++x)for(int y=-radius;y<=radius;++y) {
            const auto cell=holo_batch::s.centre+coord_def(x,y);
            if(in_bounds(cell) && you.see_cell(cell)
                && grid_distance(cell,holo_batch::s.centre)==radius
                && area(cell,holo_batch::s.centre,radius))flashes.push_back(cell);
        }
        return;
    }
    if(g=="miko" && tier==5) {
        flash_kind=effect::mikoexpand;
        if(in_bounds(holo_batch::s.centre) && you.see_cell(holo_batch::s.centre))
            flashes.push_back(holo_batch::s.centre);
        return;
    }
    if(g=="suisei" && impact_phase)flash_kind=effect::cometfall;
    else if(g=="suisei" && tier==1)flash_kind=effect::starmark;
    else if(g=="suisei" && tier==3) {
        coord_def d=p-you.pos();d.x=(d.x>0)-(d.x<0);d.y=(d.y>0)-(d.y<0);
        flash_kind=d.y==0?effect::cut_h:d.x==0?effect::cut_v:d.x==d.y?effect::cut_d:effect::cut_u;
        if(d.x || d.y)for(int i=1;i<=5;++i) {
            const auto cell=you.pos()+d*i;
            if(in_bounds(cell) && you.see_cell(cell))flashes.push_back(cell);
        }
        return;
    }
    if(in_bounds(p) && you.see_cell(p))flashes.push_back(p);
}
void animate_prepared() {
#ifdef USE_TILE_LOCAL
    if(crawl_state.test || holo_benchmark_active() || flashes.empty())return;
    const int frames=flash_kind==effect::cometfall?6:(flash_kind==effect::mikoexpand || flash_kind==effect::akibloom)?4:2;
    for(int frame=0;frame<frames;++frame) {
        flash_frame=frame;tiles.invalidate_dungeon_overlays();update_screen();
        scaled_delay(flash_kind==effect::night_korone3?110:flash_kind==effect::ayameslash || flash_kind==effect::ayameduel?110:flash_kind==effect::cometfall?(frame<4?65:100):(flash_kind==effect::mikoexpand || flash_kind==effect::akibloom)?95:55);
    }
    clear();tiles.invalidate_dungeon_overlays();update_screen();
#endif
}
void flash(effect kind,const coord_def &centre,int radius) {
    // Native fixture/benchmark runs must remain fast and independent of UI.
    // Only the SDL renderer animates; it redraws its existing view buffer,
    // never viewwindow(), monster safety/pathfinding, or gameplay timers.
#ifdef USE_TILE_LOCAL
    if(crawl_state.test || holo_benchmark_active())return;
    flashes.clear();
    for(int x=-radius;x<=radius;++x)for(int y=-radius;y<=radius;++y) {
        const auto p=centre+coord_def(x,y);
        if(in_bounds(p) && you.see_cell(p) && holo_batch::line(centre,p))flashes.push_back(p);
    }
    if(flashes.empty())return;
    flash_kind=kind;
    for(int frame=0;frame<2;++frame) {
        flash_frame=frame;tiles.invalidate_dungeon_overlays();update_screen();scaled_delay(35);
    }
    clear();tiles.invalidate_dungeon_overlays();update_screen();
#endif
}
}
void clear(){flashes.clear();flash_kind=effect::none;flash_frame=0;fox_scene=0;fox_frame=0;fox_arrivals.clear();fox_hits.clear();}
void bind_altar(const std::string &god) {
    if(holo_benchmark_active() || !feat_is_altar(grd(you.pos())))return;
    if(!env.properties.exists(altar_key))env.properties[altar_key].new_table();
    env.properties[altar_key].get_table()[position(you.pos())]=god;
}
std::string altar(const coord_def &p) {
    if(holo_benchmark_active() || !in_bounds(p) || !feat_is_altar(env.map_knowledge(p).feat())
        || !env.properties.exists(altar_key))return "";
    const auto &t=env.properties[altar_key].get_table();const auto key=position(p);
    return t.exists(key)?t.at(key).get_string():"";
}
sprite appearance(const monster &mon) {
    if(mon.props.exists("holo_wrath_god")) {
        const auto &g=mon.props["holo_wrath_god"].get_string();
        return g=="aki"?sprite::rose:g=="fubuki"?sprite::fox:g=="ayame"?sprite::swordsman:g=="korone"?sprite::hound:g=="lui"?sprite::raven:sprite::none;
    }
    // Saved native names support pre-art campaign saves without a migration
    // or storing compiled atlas indices in monster/player save data.
    if(!testbits(mon.flags,MF_NO_REWARD))return sprite::none;
    return mon.mname=="Holo rose"?sprite::rose:mon.mname=="Holo fox image"?sprite::fox:mon.mname=="Holo raven"?sprite::raven:sprite::none;
}
std::vector<effect> at(const coord_def &p) {
    std::vector<effect> result;
    if(holo_benchmark_active() || !in_bounds(p) || !you.see_cell(p))return result;
    if(holo_campaign::active()) {
        const auto g=holo_worship::current();const auto &s=holo_batch::s;const int now=you.elapsed_time;
        effect base=effect::none;
        if(g=="sopia")base=holo_sopia::visual_at(p);
        if(g=="miko" && s.one_end>now && area(p,s.centre,holo_batch::five()?3:you.piety>=75?2:1))
            base=holo_batch::five() && ((std::abs(p.x-s.centre.x)==3 && std::abs(p.y-s.centre.y)==3) || p==s.centre)
                ?effect::mikodomain:effect::shrine;
        if(g=="aki" && s.one_end>now && s.one_ready<=now && grd(p)==DNGN_FLOOR && area(p,s.centre,s.three_end>now?3:you.piety>=75?2:1))base=effect::garden;
        if(g=="towa" && s.one_end>now && area(p,s.centre,2))base=effect::spotlight;
        if(g=="su" && grd(p)==DNGN_FLOOR && s.five_end>now && area(p,you.pos(),2))base=effect::water;
        for(const auto &h:s.hazards) {
            if(g=="su" && h.kind==20 && h.end>now && h.pos==p)base=effect::water;
            if(g=="koyori" && h.kind==4 && h.end>now && area(p,h.pos,h.extra))base=effect::slime;
        }
        if(s.five_end>now && g=="hajime" && grid_distance(p,you.pos())==1 && area(p,you.pos(),1))base=effect::rhythm;
        if(s.five_end>now && p==you.pos()) {
            if(g=="vivi")base=effect::spotlight;
            if(g=="mela")base=effect::fire;
            if(g=="lamy")base=effect::frost;
            if(g=="raden")base=effect::exhibit;
        }
        if((g=="noel" && holo_campaign::noel_commander()) || (g=="watame" && s.three_end>now))
            if(p==you.pos())base=effect::shield;
        if(base!=effect::none)result.push_back(base);
        // Actual saved hazard geometry, not a second combat/targeting model.
        for(const auto &h:s.hazards) {
            const bool carrot=g=="pekora" && h.kind==10 && h.end>now;
            const bool strike=(g=="pekora" && h.kind==11 && h.arm>now)
                || (g=="suisei" && h.kind==1 && h.arm>now);
            if(carrot && h.pos==p)result.push_back(effect::carrot);
            if((carrot || strike) && area(p,h.pos,1)) {
                const int when=carrot && h.extra?h.next:h.arm;
                if(strike || (carrot && h.extra))result.push_back(when-now<=10?effect::urgent:effect::warning);
            }
        }
    }
    // Keep the actual 3x3 strike footprint visible during render-only descent.
    // No hazard lifetime, damage cell, or gameplay timer is extended.
    if(flash_kind==effect::cometfall && flash_frame<4 && !flashes.empty()
        && area(p,flashes.front(),1))result.push_back(effect::urgent);
    const int wrath=holo_wrath::visual_at(p);
    if(wrath==1 || wrath==2)result.push_back(wrath==2?effect::urgent:effect::warning);
    if(wrath==3)result.push_back(effect::fire);
    if(wrath==4)result.push_back(effect::slime);
    return result;
}
effect invocation_at(const coord_def &p) {
    if(!in_bounds(p) || !you.see_cell(p))return effect::none;
    const auto fox=fox_cue_at(p);if(fox!=effect::none)return fox;
    if(holo_campaign::active() && holo_worship::current()=="ayame") {
        const auto &s=holo_batch::s;const auto *mon=monster_by_mid(s.marked);
        if(p==you.pos() && s.one_end>you.elapsed_time && mon && mon->alive()
            && grid_distance(you.pos(),mon->pos())==1)return effect::ayameaura;
    }
    if(flash_kind!=effect::none && std::find(flashes.begin(),flashes.end(),p)!=flashes.end())return flash_kind;
    const auto choco=choco_mark(p);if(choco!=effect::none)return choco;
    const auto ns=night_status(p);if(ns!=effect::none)return ns;
    if(holo_campaign::active() && holo_worship::current()=="suisei") {
        const auto *marked=monster_by_mid(holo_batch::s.marked);
        if(marked && marked->alive() && marked->pos()==p)return effect::starmark;
    }
    if(holo_campaign::active() && holo_worship::current()=="miko") {
        const auto &s=holo_batch::s;const int now=you.elapsed_time;
        const int radius=holo_batch::five()?3:you.piety>=75?2:1;
        if(s.one_end>now && s.three_end>now && grid_distance(p,s.centre)==radius
            && area(p,s.centre,radius))return effect::mikoflame;
    }
    return effect::none;
}
effect invocation_sprite_at(const coord_def &p,int &span_x,int &span_y) {
    span_x=span_y=1;
    const int ns=night_span(flash_kind);
    if(ns>1 && !flashes.empty()) {
        if(p==flashes.front()-coord_def(ns/2,ns/2)){span_x=span_y=ns;return flash_kind;}
        if(p==flashes.front())return effect::none;
    }
    if(choco_large(flash_kind) && !flashes.empty()) {
        if(p==flashes.front()-coord_def(1,1)){span_x=span_y=3;return flash_kind;}
        if(p==flashes.front())return effect::none;
    }
    const auto mark=choco_mark(p+coord_def(1,1));
    if(mark!=effect::none && !(flash_kind!=effect::none && !flashes.empty()
        && flashes.front()==p+coord_def(1,1))) {span_x=span_y=3;return mark;}
    if(choco_mark(p)!=effect::none && flash_kind==effect::none)return effect::none;
    if((flash_kind==effect::ayameslash || flash_kind==effect::ayameduel) && !flashes.empty()) {
        const int r=flash_kind==effect::ayameslash?1:2;
        if(p==flashes.front()-coord_def(r,r)) {span_x=span_y=2*r+1;return flash_kind;}
        // The large cue is anchored once, never once per affected cell.
        if(p==flashes.front())return effect::none;
    }
    if(holo_campaign::active() && holo_worship::current()=="ayame" && holo_batch::five()
        && p==holo_batch::s.centre-coord_def(2,2)) {
        span_x=span_y=5;return effect::ayameduel;
    }
    if((flash_kind==effect::mikoexpand || flash_kind==effect::akibloom) && !flashes.empty()) {
        const int radius=std::min(1+flash_frame,3);
        const auto anchor=flashes.front()-coord_def(radius,radius);
        if(p==anchor) { span_x=span_y=2*radius+1;return flash_kind; }
        if(p==flashes.front())return effect::none;
    }
    if(flash_kind==effect::cometfall && !flashes.empty()) {
        const auto centre=flashes.front();
        const bool falling=flash_frame<4;
        const auto anchor=centre+coord_def(-1,falling?-5+flash_frame:-1);
        if(p==anchor) {
            span_x=span_y=3;
            return falling?effect::cometdrop:effect::cometfall;
        }
        if(p==centre)return effect::none;
    }
    const bool cut=flash_kind==effect::cut_h || flash_kind==effect::cut_d
        || flash_kind==effect::cut_v || flash_kind==effect::cut_u;
    if(cut && !flashes.empty()) {
        coord_def low=flashes.front(),high=low;
        for(const auto &cell:flashes) {
            low.x=std::min(low.x,cell.x);low.y=std::min(low.y,cell.y);
            high.x=std::max(high.x,cell.x);high.y=std::max(high.y,cell.y);
        }
        // A blade sweep needs room across the strike direction; this is
        // render-only padding, never additional damage cells.
        if(flash_kind==effect::cut_h) { --low.y; ++high.y; }
        else if(flash_kind==effect::cut_v) { --low.x; ++high.x; }
        if(p==low) { span_x=high.x-low.x+1;span_y=high.y-low.y+1;return flash_kind; }
        if(std::find(flashes.begin(),flashes.end(),p)!=flashes.end())return effect::none;
    }
    return invocation_at(p);
}
std::vector<badge> badges() {
    std::vector<badge> result;
    if(holo_benchmark_active())return result;
    const int now=you.elapsed_time;
    int warning=holo_wrath::indicator();
    if(holo_campaign::active()) {
        const auto &s=holo_batch::s;const auto g=holo_worship::current();
        auto saved=[](const char *name){
            if(!you.props.exists("holocrawl_campaign"))return 0;
            const auto &t=you.props["holocrawl_campaign"].get_table();
            return t.exists(name)?t.at(name).get_int():0;
        };
        const bool five=g=="noel"?holo_campaign::noel_commander():g=="sopia"?holo_sopia::five_active():s.five_end>now;
        const bool active=g=="noel"?saved("noel_skill_end")>now:g=="sopia"?holo_sopia::visual_at(you.pos()+coord_def(1,0))!=effect::none:s.one_end>now || s.three_end>now;
        if(five)result.push_back(badge::five);
        else if(active)result.push_back(badge::active);
        if(s.shield>0 || holo_campaign::noel_commander() || (g=="watame" && s.three_end>now))result.push_back(badge::shield);
        for(const auto &h:s.hazards)if(h.arm>now && ((g=="suisei" && h.kind==1) || (g=="pekora" && h.kind==11))) {
            const int level=h.arm-now<=10?2:1;
            warning=warning==3?level:std::max(warning,level);
        }
        const bool cooling=g=="noel"?saved("noel_ready")>now:g=="sopia"?holo_sopia::cooldown()>now:s.one_ready>now || s.three_ready>now || s.five_ready>now;
        if(cooling)result.push_back(badge::cooldown);
        else if(s.resource>0)result.push_back(badge::resource);
    }
    if(warning)result.push_back(warning==1?badge::warning:warning==2?badge::urgent:badge::wrath);
    return result;
}
effect invocation_effect(const std::string &g) {
    return g=="suisei"?effect::comet:g=="mela"?effect::fire:g=="su"?effect::water:g=="sopia"?effect::gravity:g=="miko"?effect::shrine:g=="raden"?effect::exhibit:g=="hajime"?effect::rhythm:g=="vivi"?effect::spotlight:g=="lamy"?effect::frost:g=="aki"?effect::garden:g=="noel" || g=="watame"?effect::shield:g=="fubuki"?effect::foxflame:g=="ayame"?effect::oni:g=="choco"?effect::charm:g=="korone"?effect::punch:g=="okayu"?effect::sleep:g=="pekora"?effect::carrotburst:g=="towa"?effect::devil:g=="polka"?effect::circus:g=="koyori"?effect::reagent:g=="lui"?effect::ravenflight:effect::impact;
}
void invocation(const std::string &g,int tier,const coord_def &p,int option) {
    // These two effects are emitted at the actual successful swap/spawn sites.
    if((g=="fubuki" && (tier==3 || tier==5)) || (g=="choco" && tier==3))return;
    if(holo_benchmark_active())return;
    if(tier<0 || (g=="sopia" && tier==6))return;
    // A casting cue identifies a successful invocation, not its damage footprint.
    // Persistent geometry remains sourced from actual saved combat state in at().
    if(g=="suisei" || g=="miko" || g=="aki" || g=="ayame" || g=="choco" || night_effect(g,tier,option)!=effect::none) { prepare_invocation(g,tier,p,false,option);animate_prepared();if(crawl_state.test)clear(); }
    else flash(invocation_effect(g),p,0);
}
void comet_impact(const coord_def &p) {
    if(holo_benchmark_active())return;
    if(crawl_state.test) {
        if(const char *dir=getenv("HOLOCRAWL_SUISEI_REVIEW")) {
            const auto before=holo_batch::save_campaign();const int hp=you.hp,mp=you.magic_points,piety=you.piety,now=you.elapsed_time;
            for(int f=0;f<6;++f)capture_invocation("suisei",p,f,std::string(dir)+"/comet-impact-frame"+std::to_string(f)+".png",5,true);
            if(before!=holo_batch::save_campaign() || hp!=you.hp || mp!=you.magic_points || piety!=you.piety || now!=you.elapsed_time)
                throw std::runtime_error("Comet impact capture changed combat state");
        }
        return;
    }
    prepare_invocation("suisei",5,p,true);animate_prepared();
}
void rose_thorn_cell(const coord_def &from,const coord_def &to,const coord_def &cell) {
    if(holo_benchmark_active() || !holo_campaign::active() || holo_worship::current()!="aki"
        || !in_bounds(cell) || !you.see_cell(cell))return;
    const char *dir=crawl_state.test?getenv("HOLOCRAWL_AKI_REVIEW"):nullptr;
    if(crawl_state.test && !dir)return;
    const int dx=(to.x>from.x)-(to.x<from.x),dy=(to.y>from.y)-(to.y<from.y);
    const int direction=dx>0?(dy>0?1:dy<0?7:0):dx<0?(dy>0?3:dy<0?5:4):dy>0?2:6;
    flashes.assign(1,cell);flash_kind=effect(int(effect::thorn_e)+direction);
    flash_frame=grid_distance(from,cell)%2;
    if(dir) {
        static int sequence=0;
        if(sequence<24) {
            auto signature=[]() {
                std::ostringstream o;std::vector<unsigned char> bytes;
                {writer out(&bytes);rng::generators_to_vector().write(out);}
                o<<you.hp<<' '<<you.magic_points<<' '<<int(you.piety)<<' '<<you.elapsed_time<<'|'<<holo_batch::save_campaign();
                for(auto n:bytes)o<<int(n)<<',';
                for(monster_iterator mi;mi;++mi)o<<'|'<<mi->mid<<':'<<mi->pos().x<<','<<mi->pos().y<<','<<mi->hit_points;
                return o.str();
            };
            const auto before=signature();const int index=++sequence;
            capture(std::string(dir)+"/rose-flight-"+std::to_string(index)+".png");
            if(before!=signature())throw std::runtime_error("Rose projectile capture changed gameplay/RNG");
            std::ofstream trace(std::string(dir)+"/rose-flight.jsonl",std::ios::app);
            trace<<"{\"frame\":"<<index<<",\"from\":["<<from.x<<','<<from.y<<"],\"to\":["<<to.x<<','<<to.y<<"],\"cell\":["<<cell.x<<','<<cell.y<<"]}\n";
        }
    }
#ifdef USE_TILE_LOCAL
    else { tiles.invalidate_dungeon_overlays();update_screen();scaled_delay(30); }
#endif
    clear();
#ifdef USE_TILE_LOCAL
    tiles.invalidate_dungeon_overlays();
#endif
}
void fox_swap(const coord_def &from,const coord_def &to,const std::vector<coord_def> &hits) {
    if(holo_benchmark_active() || (crawl_state.test && !getenv("HOLOCRAWL_FUBUKI_REVIEW")))return;
    clear();fox_scene=1;fox_from=from;fox_to=to;fox_hits=hits;play_fox_scene();
}
void choco_kiss(const coord_def &target,int damage,int healed) {
    if(holo_benchmark_active())return;
    const char *dir=crawl_state.test?getenv("HOLOCRAWL_CHOCO_REVIEW"):nullptr;
    if(crawl_state.test && (!dir || !*dir))return;
    const auto before=crawl_state.test?fox_signature():std::string();
    static int sequence=0;const int seq=dir?++sequence:0;
    const int dx=(you.pos().x>target.x)-(you.pos().x<target.x),dy=(you.pos().y>target.y)-(you.pos().y<target.y);
    const int direction=dx>0?(dy>0?1:dy<0?7:0):dx<0?(dy>0?3:dy<0?5:4):dy>0?2:6;
    const int frames=healed>0?4:2;
    for(int f=0;f<frames;++f) {
        flashes.assign(1,target);flash_frame=f%2;
        flash_kind=f<2?effect::chocokiss:effect(int(effect::chocoabsorb0)+direction);
#ifdef USE_TILE_LOCAL
        const auto saved_rng=rng::generators_to_vector();redraw_fox_actors();rng::load_generators(saved_rng);
#endif
        if(dir) {
            const auto stem=std::string(dir)+"/choco-kiss-"+std::to_string(seq)+"-frame"+std::to_string(f);
            capture(stem+".png",false);
            std::ofstream meta(stem+".json");meta<<"{\"frame\":"<<f<<",\"damage\":"<<damage<<",\"healed\":"<<healed<<",\"absorption\":"<<(f>=2?"true":"false")<<"}\n";
        }
#ifdef USE_TILE_LOCAL
        else scaled_delay(f>=2?170:110);
#endif
    }
    clear();
    if(crawl_state.test && before!=fox_signature())throw std::runtime_error("Choco kiss changed gameplay/RNG");
#ifdef USE_TILE_LOCAL
    if(!crawl_state.test){const auto saved_rng=rng::generators_to_vector();redraw_fox_actors();rng::load_generators(saved_rng);}
#endif
}
void fox_gather(const std::vector<coord_def> &positions) {
    if(positions.empty() || holo_benchmark_active() || (crawl_state.test && !getenv("HOLOCRAWL_FUBUKI_REVIEW")))return;
    clear();fox_scene=2;fox_arrivals=positions;play_fox_scene();
}
bool mask_fox_at(const coord_def &p) {
    if(fox_scene!=2 || !in_bounds(p))return false;
    const auto it=std::find(fox_arrivals.begin(),fox_arrivals.end(),p);
    if(it==fox_arrivals.end() || int(it-fox_arrivals.begin())<(fox_frame+1)/2)return false;
    const monster *mon=monster_at(p);
    return mon && appearance(*mon)==sprite::fox;
}
void impact(const coord_def &p,int radius,bool fire){
    const auto g=holo_worship::current();
    if(holo_campaign::active() && (g=="pekora" || g=="sopia")) {
        flashes.assign(1,p);flash_kind=night_effect(g,g=="pekora"?3:5);
        if(crawl_state.test) {
            if(const char *dir=getenv("HOLOCRAWL_NIGHT_REVIEW")) {
                static int seq=0;const int n=++seq;const auto before=fox_signature();
                for(int f=0;f<2;++f){flash_frame=f;capture(std::string(dir)+"/"+g+"-impact-"+std::to_string(n)+"-frame"+std::to_string(f)+".png");}
                if(before!=fox_signature())throw std::runtime_error("Impact capture changed gameplay");
            }
            clear();return;
        }
        animate_prepared();return;
    }
    flash(fire?effect::fire:effect::impact,p,radius);
}
void decorate(MenuEntry &entry,const std::string &g) {
#ifdef USE_TILE
    const int tile=god_tile(g);if(tile)entry.add_tile(tile_def(tile,TEX_FEAT));
#endif
}
#ifdef USE_TILE
int god_tile(const std::string &g) {
    const auto ids=holo_worship::gods();const auto it=std::find(ids.begin(),ids.end(),g);
    return it==ids.end()?0:TILE_HOLO_GOD_SUISEI+int(it-ids.begin());
}
int altar_tile(const std::string &g) {
    const auto ids=holo_worship::gods();const auto it=std::find(ids.begin(),ids.end(),g);
    return it==ids.end()?0:TILE_HOLO_ALTAR_SUISEI+int(it-ids.begin());
}
int effect_tile(effect kind,int frame) {
    if(kind==effect::none)return 0;
    if(kind==effect::carrot)return TILE_HOLO_CARROT;
    if(frame<0 && ((fox_scene==1 && (kind==effect::foxshift || kind==effect::foxflame || kind==effect::foxhit))
        || (fox_scene==2 && kind==effect::foxcircle)))frame=fox_frame%2;
    if(frame<0)frame=flash_kind!=effect::none && kind==flash_kind?flash_frame:(you.elapsed_time/10)%2;
    return TILE_HOLO_FX_WARNING_0+(int(kind)-1)*2+(frame%2);
}
int sprite_tile(sprite kind) {
    if(kind==sprite::none)return 0;
    return ((you.elapsed_time/10)%2?TILE_HOLO_ROSE_1:TILE_HOLO_ROSE)+int(kind)-1;
}
int badge_tile(badge kind){return TILE_HOLO_STATUS_FIVE+int(kind);}
void style_player(dolls_data &doll) {
    if(holo_benchmark_active() || you.form!=transformation::none || Options.tile_use_monster!=MONS_0)return;
    const auto ids=holo_worship::gods();const auto found=std::find(ids.begin(),ids.end(),holo_worship::current());
    if(holo_campaign::active() && found!=ids.end() && !doll.parts[TILEP_PART_HALO])doll.parts[TILEP_PART_HALO]=TILEP_HOLO_CHARM_SUISEI+int(found-ids.begin());
    // Render-only base swap: native armour, helmet, weapons and species/forms survive.
    if(you.species==SP_HUMAN && is_player_tile(doll.parts[TILEP_PART_BASE],TILEP_BASE_HUMAN)
        && player_doll.parts[TILEP_PART_BODY]==TILEP_SHOW_EQUIP) {
        doll.parts[TILEP_PART_BASE]=(doll.parts[TILEP_PART_BASE]-TILEP_BASE_HUMAN)%2==0?TILEP_HOLO_AVATAR_BASE_B:TILEP_HOLO_AVATAR_BASE_A;
        if(player_doll.parts[TILEP_PART_HAIR]==TILEP_SHOW_EQUIP)doll.parts[TILEP_PART_HAIR]=0;
    }
}
#endif
void validate() {
    auto require=[](bool ok){if(!ok)throw std::runtime_error("Holo visual regression");};
    require(at(coord_def(-1,-1)).empty());
    std::vector<effect> themed;
    for(const auto &g:std::vector<std::string>{"fubuki","ayame","choco","korone","okayu","pekora","towa","polka","koyori","lui"}) {
        const auto e=invocation_effect(g);
        require(e!=effect::impact && std::find(themed.begin(),themed.end(),e)==themed.end());
        themed.push_back(e);
    }
    monster fake;fake.flags|=MF_NO_REWARD;
    for(const auto &entry:std::vector<std::pair<std::string,sprite>>{{"Holo rose",sprite::rose},{"Holo fox image",sprite::fox},{"Holo raven",sprite::raven}}){fake.mname=entry.first;require(appearance(fake)==entry.second);}
    fake.mname="rat";require(appearance(fake)==sprite::none);
#ifdef USE_TILE
    require(TILE_HOLO_GOD_MELA-TILE_HOLO_GOD_SUISEI==21);
    require(TILE_HOLO_ALTAR_MELA-TILE_HOLO_ALTAR_SUISEI==21);
    require(altar_tile("unknown")==0);
    int altar_index=0;
    for(const auto &g:holo_worship::gods())
        require(altar_tile(g)==TILE_HOLO_ALTAR_SUISEI+altar_index++);
    require(TILE_HOLO_FX_COMET_1-TILE_HOLO_FX_WARNING_0==31);
    require(TILE_HOLO_FX_RAVENFLIGHT_1-TILE_HOLO_FX_FOXFLAME_0==19);
    for(int i=0;i<10;++i)for(int f=0;f<2;++f)
        require(effect_tile(effect(int(effect::foxflame)+i),f)==TILE_HOLO_FX_FOXFLAME_0+2*i+f);
    require(effect_tile(effect::carrot)==TILE_HOLO_CARROT);
    require(TILE_HOLO_FX_COMETFALL_1-TILE_HOLO_FX_STARMARK_0==11);
    require(effect_tile(effect::cometdrop,1)==TILE_HOLO_FX_COMETDROP_1);
    require(effect_tile(effect::mikoflame,1)==TILE_HOLO_FX_MIKOFLAME_1);
    require(effect_tile(effect::mikodomain,1)==TILE_HOLO_FX_MIKODOMAIN_1);
    require(TILE_HOLO_HOUND-TILE_HOLO_ROSE==4);
    require(TILE_HOLO_HOUND_1-TILE_HOLO_ROSE_1==4);
    require(TILE_HOLO_STATUS_ACTIVE-TILE_HOLO_STATUS_FIVE==7);
    require(TILEP_HOLO_CHARM_MELA-TILEP_HOLO_CHARM_SUISEI==21);
    require(TILEP_HOLO_AVATAR_BASE_B-TILEP_HOLO_AVATAR_BASE_A==1);
    for(const auto &g:holo_worship::gods())require(god_tile(g)>0);
#endif
}
void capture_invocation(const std::string &god,const coord_def &pos,int frame,const std::string &path,int tier,bool impact_phase,int option) {
#ifdef USE_TILE_LOCAL
    if(!crawl_state.test || frame<0 || frame>(impact_phase?5:((god=="miko" || god=="aki") && tier==5)?3:1))
        throw std::runtime_error("Invocation frame capture requires native test mode");
    if(!in_bounds(pos) || !you.see_cell(pos))
        throw std::runtime_error("Invocation capture position is not visible");
    // Same routing and overlay path as flash(); expose one frame for a native
    // framebuffer read without advancing time or redrawing the VFX in Python.
    prepare_invocation(god,tier,pos,impact_phase,option);flash_frame=frame;
    try { capture(path); } catch(...) { clear();throw; }
    clear();tiles.invalidate_dungeon_overlays();
#else
    throw std::runtime_error("Invocation frame capture needs native SDL");
#endif
}
void capture(const std::string &path,bool refresh) {
#ifdef USE_TILE_LOCAL
    if(!crawl_state.test)throw std::runtime_error("Visual capture requires native test mode");
    // Native tile setup also uses explicitly named RNG streams. Screenshot
    // setup is test-only: preserve every stream, not only the current one.
    struct visual_rng_guard {
        CrawlVector saved=rng::generators_to_vector();
        bool trapped=you.trapped;
        int exploration=you.exploration;
        std::vector<bool> explored;
        visual_rng_guard() {
            for(int x=0;x<GXM;++x)for(int y=0;y<GYM;++y)
                explored.push_back(!!(env.pgrid(coord_def(x,y)) & FPROP_SEEN_OR_NOEXP));
        }
        ~visual_rng_guard(){
            rng::load_generators(saved);you.trapped=trapped;you.exploration=exploration;
            int index=0;
            for(int x=0;x<GXM;++x)for(int y=0;y<GYM;++y) {
                auto &flags=env.pgrid(coord_def(x,y));
                if(explored[index++])flags|=FPROP_SEEN_OR_NOEXP;
                else flags&=~FPROP_SEEN_OR_NOEXP;
            }
        }
    } keep_rng;
    rng::subgenerator visual_rng(0x484F4C4F564658ULL);
    unwind_bool rendering(crawl_state.need_save,true);
    if(refresh) {
    invalidate_los();reset_show_terrain();
    init_player_doll();
    tile_init_default_flavour();
    tile_new_level(true,true);
    // The first pass initializes map knowledge after a synthetic fixture reset;
    // a second full native pass builds overlays from that initialized view.
    redraw_screen();tiles.invalidate_dungeon_overlays();tiles.redraw();
    redraw_screen();tiles.invalidate_dungeon_overlays();tiles.redraw();
    } else { tiles.invalidate_dungeon_overlays();tiles.redraw(); }
    SDL_Window *window=SDL_GL_GetCurrentWindow();
    if(!window)throw std::runtime_error("No native SDL OpenGL window for visual fixture");
    int w=0,h=0;SDL_GL_GetDrawableSize(window,&w,&h);
    std::vector<unsigned char> pixels(w*h*4),top_down(w*h*4);
    // Read the freshly rendered back buffer rather than a compositor-delayed
    // front buffer (which can still contain the previous ability/menu).
    tiles.render_current_regions();glFinish();
    glReadBuffer(GL_BACK);glPixelStorei(GL_PACK_ALIGNMENT,1);
    glReadPixels(0,0,w,h,GL_RGBA,GL_UNSIGNED_BYTE,pixels.data());
    for(int y=0;y<h;++y)std::copy(pixels.begin()+(h-y-1)*w*4,pixels.begin()+(h-y)*w*4,top_down.begin()+y*w*4);
    SDL_Surface *surface=SDL_CreateRGBSurfaceWithFormatFrom(top_down.data(),w,h,32,w*4,SDL_PIXELFORMAT_RGBA32);
    if(!surface)throw std::runtime_error(SDL_GetError());
    const int result=IMG_SavePNG(surface,path.c_str());SDL_FreeSurface(surface);
    if(result)throw std::runtime_error(IMG_GetError());
    std::ofstream meta(path+".json");int seen=0,altars=0,marks=0;
    for(int x=-7;x<=7;++x)for(int y=-7;y<=7;++y){const auto p=you.pos()+coord_def(x,y);if(you.see_cell(p))++seen;if(!altar(p).empty())++altars;marks+=at(p).size()+(invocation_at(p)!=effect::none?1:0);}
    int creatures[5]={0,0,0,0,0};
    for(monster_iterator mi;mi;++mi){const int kind=int(appearance(**mi));if(kind>0 && kind<=5 && you.see_cell(mi->pos()))++creatures[kind-1];}
    dolls_data dressed=player_doll;fill_doll_equipment(dressed);const auto before=dressed;
    style_player(dressed);
    const bool styled=dressed.parts[TILEP_PART_BASE]!=before.parts[TILEP_PART_BASE];
    for(int part:{TILEP_PART_HAND1,TILEP_PART_HAND2,TILEP_PART_BODY,TILEP_PART_HELM,TILEP_PART_BOOTS})
        if(dressed.parts[part]!=before.parts[part])throw std::runtime_error("Visual style changed equipped gear");
    meta<<"{\"seenCells\":"<<seen<<",\"boundAltars\":"<<altars<<",\"effectCells\":"<<marks<<",\"styledHuman\":"<<(styled?"true":"false")<<",\"gearPreserved\":true,\"creatures\":[";
    for(int i=0;i<5;++i){if(i)meta<<',';meta<<creatures[i];}
    meta<<"],\"badges\":[";const auto flags=badges();for(size_t i=0;i<flags.size();++i){if(i)meta<<',';meta<<int(flags[i]);}meta<<"]}\n";
#else
    throw std::runtime_error("Visual capture needs the SDL tiles executable");
#endif
}
}
