#pragma once
#include <string>
#include <vector>
#include "coord.h"
class monster;
class MenuEntry;
struct dolls_data;
namespace holo_visual {
enum class effect { none,warning,urgent,shrine,garden,water,gravity,orbit,
    fire,exhibit,spotlight,frost,rhythm,shield,slime,impact,comet,foxflame,oni,charm,punch,sleep,carrotburst,devil,circus,reagent,ravenflight,starmark,cut_h,cut_d,cut_v,cut_u,cometfall,cometdrop,mikoflame,mikodomain,mikoexpand,thorn_e,thorn_se,thorn_s,thorn_sw,thorn_w,thorn_nw,thorn_n,thorn_ne,akibloom,foxshift,foxcircle,foxhit,carrot };
enum class sprite { none,rose,fox,raven,swordsman,hound };
enum class badge { five,shield,warning,urgent,wrath,cooldown,resource,active };
std::vector<badge> badges();
// These queries never refresh combat state, advance timers, or draw RNG.
std::vector<effect> at(const coord_def &pos);
sprite appearance(const monster &mon);
void bind_altar(const std::string &god);
std::string altar(const coord_def &pos);
void decorate(MenuEntry &entry,const std::string &god);
effect invocation_effect(const std::string &god);
void invocation(const std::string &god,int tier,const coord_def &pos);
void comet_impact(const coord_def &pos);
void rose_thorn_cell(const coord_def &from,const coord_def &to,const coord_def &cell);
void impact(const coord_def &pos,int radius,bool fire=false);
effect invocation_at(const coord_def &pos);
effect invocation_sprite_at(const coord_def &pos,int &span_x,int &span_y);
void fox_swap(const coord_def &from,const coord_def &to,const std::vector<coord_def> &hits);
void fox_gather(const std::vector<coord_def> &positions);
bool mask_fox_at(const coord_def &pos);
void clear();
void validate();
void capture_invocation(const std::string &god,const coord_def &pos,int frame,const std::string &path,int tier=0,bool impact_phase=false);
void capture(const std::string &path,bool refresh=true); // Native SDL framebuffer, test-only.
#ifdef USE_TILE
int god_tile(const std::string &god);
int altar_tile(const std::string &god);
int effect_tile(effect kind,int frame=-1);
int sprite_tile(sprite kind);
int badge_tile(badge kind);
void style_player(dolls_data &doll);
#endif
}
