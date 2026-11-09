#pragma once
#include <string>
#include <vector>
#include "coord.h"
class monster;
class MenuEntry;
struct dolls_data;
namespace holo_visual {
enum class effect { none,warning,urgent,shrine,garden,water,gravity,orbit,
    fire,exhibit,spotlight,frost,rhythm,shield,slime,impact,comet,foxflame,oni,charm,punch,sleep,carrotburst,devil,circus,reagent,ravenflight,starmark,cut_h,cut_d,cut_v,cut_u,cometfall,cometdrop,mikoflame,mikodomain,mikoexpand,thorn_e,thorn_se,thorn_s,thorn_sw,thorn_w,thorn_nw,thorn_n,thorn_ne,akibloom,foxshift,foxcircle,foxhit,ayameaura,ayameslash,ayameduel,chocoheart1,chocoheart2,chocoheart3,chocoheart4,chocoheart5,chocokiss,chocowings,chocobond,chocoabsorb0,chocoabsorb1,chocoabsorb2,chocoabsorb3,chocoabsorb4,chocoabsorb5,chocoabsorb6,chocoabsorb7,night_korone1,night_korone3,night_korone5,night_okayu1,night_okayu3,night_okayu5,night_pekora1,night_pekora3,night_pekora5,night_noel1,night_noel3,night_noel5,night_watame1,night_watame3,night_watame5,night_towa1,night_towa3,night_towa5,night_lamy1,night_lamy3,night_lamy5,night_polka1,night_polka3,night_polka5,night_koyori1,night_koyori3,night_koyori5,night_lui1,night_lui3,night_lui5,night_raden1,night_raden3,night_raden5,night_hajime1,night_hajime3,night_hajime5,night_su1,night_su3,night_su5,night_vivi1,night_vivi3,night_vivi5,night_sopia1,night_sopia3,night_sopia5,night_mela1,night_mela3,night_mela5,night_polkaheal,night_polkachaos,night_radenstone,night_radencraft,lamychill1,lamychill2,lamyslow,lamyburst0,lamyburst1,lamyburst2,lamyburst3,lamybanquetcast0,lamybanquetcast1,lamybanquetactive,lamybanquetburst00,lamybanquetburst01,lamybanquetburst02,lamybanquetburst03,lamybanquetburst04,lamybanquetburst05,lamybanquetburst06,lamybanquetburst07,lamybanquetburst08,lamybanquetburst10,lamybanquetburst11,lamybanquetburst12,lamybanquetburst13,lamybanquetburst14,lamybanquetburst15,lamybanquetburst16,lamybanquetburst17,lamybanquetburst18,lamybanquetburst20,lamybanquetburst21,lamybanquetburst22,lamybanquetburst23,lamybanquetburst24,lamybanquetburst25,lamybanquetburst26,lamybanquetburst27,lamybanquetburst28,lamybanquetburst30,lamybanquetburst31,lamybanquetburst32,lamybanquetburst33,lamybanquetburst34,lamybanquetburst35,lamybanquetburst36,lamybanquetburst37,lamybanquetburst38,koyoriheat,koyoricold,koyoripoison,koyoriblast,koyorithermal,koyorislime,koyoriblastedge,koyorislimeedge,koyoriblastborder,koyorithermalborder,koyorislimeborder,carrot,suiseistars1,suiseistars2,suiseistars3,mikotorii,mikoblossom,mikopetalshield };
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
void invocation(const std::string &god,int tier,const coord_def &pos,int option=0);
void comet_impact(const coord_def &pos);
void rose_thorn_cell(const coord_def &from,const coord_def &to,const coord_def &cell);
bool lamy_banquet_cell(const coord_def &pos);
bool vivi_finale_cell(const coord_def &pos);
bool mela_breath_preview_cell(const coord_def &pos,int &frame,int &distance);
bool mela_dispatch_preview_cell(const coord_def &pos);
bool sopia_gravity_preview_cell(const coord_def &pos,coord_def &delta,int &radius,int &frame);
void lamy_banquet_burst(const coord_def &pos);
void lamy_chill_burst(const coord_def &pos);
void koyori_reaction(const coord_def &pos,int pair,bool critical=false);
void impact(const coord_def &pos,int radius,bool fire=false);
void towa_support(const coord_def &from,const coord_def &to);
void hawk_attack(const monster &hawk,const coord_def &target,bool hit);
bool mask_hawk_at(const coord_def &pos);
effect invocation_at(const coord_def &pos);
effect invocation_sprite_at(const coord_def &pos,int &span_x,int &span_y);
void fox_swap(const coord_def &from,const coord_def &to,const std::vector<coord_def> &hits);
void choco_kiss(const coord_def &target,int damage,int healed);
void fox_gather(const std::vector<coord_def> &positions);
bool mask_fox_at(const coord_def &pos);
void clear();
void validate();
void capture_invocation(const std::string &god,const coord_def &pos,int frame,const std::string &path,int tier=0,bool impact_phase=false,int option=0);
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
