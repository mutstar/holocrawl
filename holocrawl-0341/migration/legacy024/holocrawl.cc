#include "AppHdr.h"
#include "holo-dungeon-test.h"
#include "holo-campaign.h"
#include "holocrawl.h"
#include "holo-sopia.h"
#include "holo-batch.h"
#include "holo-batch-internal.h"

#include <cstdlib>
#include <fstream>
#include <stdexcept>

#include "act-iter.h"
#include "beam.h"
#include "branch.h"
#include "dungeon.h"
#include "directn.h"
#include "env.h"
#include "fight.h"
#include "item-prop.h"
#include "items.h"
#include "los.h"
#include "message.h"
#include "mgen-data.h"
#include "mon-act.h"
#include "mon-place.h"
#include "mon-util.h"
#include "newgame-def.h"
#include "ng-setup.h"
#include "options.h"
#include "package.h"
#include "player.h"
#include "skills.h"
#include "shout.h"
#include "state.h"
#include "spl-cast.h"
#include "spl-util.h"
#include "throw.h"
#include "terrain.h"

extern void world_reacts();

namespace {
bool running = false;
bool dead = false;
bool left_by_banishment = false;
bool noel = false;
bool old_balance = false;
int skill_until = 0;
int commander_until = 0;
int commander_ready = 0;
int invocation = 0;
string build_kind="melee";

bool skill_active() { return running && noel && you.elapsed_time < skill_until; }
bool commander_active() { return running && noel && you.elapsed_time < commander_until; }

int environment_integer(const char *name, int fallback, int low, int high)
{
    const char *value = getenv(name);
    if (!value)
        return fallback;
    char *endptr = nullptr;
    const long parsed = strtol(value, &endptr, 10);
    if (!endptr || *endptr || parsed < low || parsed > high)
        throw std::runtime_error(string("Invalid environment value: ") + name);
    return parsed;
}

struct scenario {
    const char *name;
    int xl, skill, inv, hp, mp, piety;
    monster_type enemy;
    int count;
};

void populate_enemies(const scenario &test,uint64_t seed)
{
    rng::seed(seed);
    const coord_def melee_offsets[] = {coord_def(1,0),coord_def(0,1),coord_def(-1,0)};
    const coord_def ranged_offsets[] = {coord_def(6,0),coord_def(5,2),coord_def(-6,0)};
    for(int n=0;n<test.count;++n) {
        const coord_def position=you.pos()+(build_kind=="melee"?melee_offsets[n]:ranged_offsets[n]);
        if(actor_at(position)) throw std::runtime_error("Prepared companion blocks a fixed enemy start");
        mgen_data mg=mgen_data::hostile_at(test.enemy,false,position);mg.flags|=MG_FORCE_PLACE;
        monster *mon=create_monster(mg,false);
        if(!mon) throw std::runtime_error("Could not create benchmark enemy");
        mon->foe=MHITYOU;mon->behaviour=BEH_SEEK;mon->target=you.pos();
        if(holo_batch::active() && holo_batch::eligible(*mon)) holo_batch::s.eligible_sources.insert(mon->mid);
    }
}
void reset_character(const scenario &test, uint64_t seed,bool populate=true)
{
    holo_sopia::reset(false,0);
    holo_batch::reset();
    noel = false;
    dead = false;
    left_by_banishment = false;
    skill_until = commander_until = commander_ready = 0;
    Options.no_save = true;
    Options.seed = seed;
    crawl_state.seed = seed;
    if (you.save)
    {
        you.save->abort();
        delete you.save;
        you.save = nullptr;
    }
    newgame_def ng;
    ng.name = "HoloBench";
    ng.type = GAME_TYPE_CUSTOM_SEED;
    ng.species = SP_HUMAN;
    ng.job = JOB_FIGHTER;
    ng.weapon = WPN_LONG_SWORD;
    ng.seed = seed;
    setup_game(ng);
    you.turn_is_over=false;
    dgn_reset_level(false);
    // The fixture contains only its explicitly listed enemies.
    env.spawn_random_rate = 0;
    for (int x = 0; x < GXM; ++x)
        for (int y = 0; y < GYM; ++y)
            grd[x][y] = DNGN_ROCK_WALL;
    for (int x = 25; x <= 45; ++x)
        for (int y = 25; y <= 45; ++y)
            grd[x][y] = DNGN_FLOOR;
    you.moveto(coord_def(35,35));
    los_changed();
    you.experience_level = test.xl;
    you.max_level = test.xl;
    you.experience = exp_needed(test.xl);
    you.base_stats[STAT_STR] = 18;
    you.base_stats[STAT_INT] = 8;
    you.base_stats[STAT_DEX] = 12;
    you.stat_loss.init(0);
    for (int sk = 0; sk < NUM_SKILLS; ++sk)
    {
        you.skills[sk] = 0;
        you.skill_points[sk] = 0;
        you.ct_skill_points[sk] = 0;
    }
    for (skill_type sk : {SK_FIGHTING, SK_LONG_BLADES, SK_ARMOUR, SK_SHIELDS})
        set_skill_level(sk, test.skill);
    set_skill_level(SK_INVOCATIONS, test.inv);
    invocation = test.inv;
    you.hp = you.hp_max = test.hp;
    you.magic_points = you.max_magic_points = test.mp;
    you.piety = test.piety;
    you.religion = GOD_NO_GOD;
    you.hunger = 6000;
    // Stable kits; all gods get the same equipment, no random god gifts.
    if (you.weapon())
        you.weapon()->plus = test.xl >= 20 ? 4 : test.xl >= 12 ? 2 : 1;
    if (you.slot_item(EQ_BODY_ARMOUR))
    {
        you.slot_item(EQ_BODY_ARMOUR)->sub_type = test.xl >= 20 ? ARM_PLATE_ARMOUR : test.xl >= 12 ? ARM_CHAIN_MAIL : ARM_SCALE_MAIL;
        you.slot_item(EQ_BODY_ARMOUR)->plus = test.xl >= 20 ? 4 : test.xl >= 12 ? 2 : 0;
    }
    if (you.shield())
        you.shield()->plus = test.xl >= 20 ? 2 : test.xl >= 12 ? 1 : 0;
    if(build_kind!="melee") {
        you.received_weapon_warning=true;
        you.equip[EQ_SHIELD]=-1;
        set_skill_level(SK_SHIELDS,0);
        set_skill_level(SK_ARMOUR,0);
        set_skill_level(SK_DODGING,test.skill/2);
        you.slot_item(EQ_BODY_ARMOUR)->sub_type=build_kind=="magic"?ARM_ROBE:ARM_LEATHER_ARMOUR;
        you.slot_item(EQ_BODY_ARMOUR)->plus=test.xl>=20?4:test.xl>=12?2:0;
        if(build_kind=="ranged") {
            you.weapon()->sub_type=test.xl>=12?WPN_LONGBOW:WPN_SHORTBOW;
            set_skill_level(SK_BOWS,test.skill);
            item_def &arrows=you.inv[ENDOFPACK-1];arrows.clear();
            arrows.base_type=OBJ_MISSILES;arrows.sub_type=MI_ARROW;arrows.quantity=80;
            arrows.link=ENDOFPACK-1;arrows.pos=ITEM_IN_INVENTORY;arrows.slot='Z';
        } else {
            you.weapon()->sub_type=WPN_DAGGER;
            you.base_stats[STAT_STR]=8;you.base_stats[STAT_INT]=18;
            for(skill_type sk:{SK_SPELLCASTING,SK_CONJURATIONS,SK_FIRE_MAGIC}) set_skill_level(sk,test.skill);
            add_spell_to_memory(SPELL_MAGIC_DART);
            add_spell_to_memory(SPELL_THROW_FLAME);
            if(test.xl>=20) add_spell_to_memory(SPELL_BOLT_OF_FIRE);
        }
    }
    you.redraw_armour_class = true;
    update_vision_range();
    // Reset after character setup so equipment and enemies are matched by seed.
    clear_pending_noises();
    if(populate) populate_enemies(test,seed);
    else rng::seed(seed);
}

void spend_time(int aut)
{
    if(holo_benchmark_finished()) return;
    you.time_taken = aut;
    you.turn_is_over = true;
    world_reacts();
}
void safe_interwave_rest()
{
    const int start=you.elapsed_time;const coord_def centre(35,35);
    while(!holo_benchmark_finished() && (you.elapsed_time-start<200 || you.pos()!=centre)) {
        if(you.elapsed_time-start>=2000) throw std::runtime_error("Cannot complete fixed interwave return/rest");
        int cost=10;
        if(you.pos()!=centre && !you.cannot_act() && !you.cannot_move() && !you.caught()) {
            coord_def d=centre-you.pos();d.x=(d.x>0)-(d.x<0);d.y=(d.y>0)-(d.y<0);
            const coord_def dest=you.pos()+d,old=you.pos();
            if(in_bounds(dest) && grd(dest)==DNGN_FLOOR && !actor_at(dest)) {
                you.move_to_pos(dest);you.apply_location_effects(old);holo_batch::after_move(old,true);
                cost=player_speed()*player_movement_speed()/10;
            }
        }
        spend_time(cost);
    }
}

monster *nearest_enemy()
{
    monster *best = nullptr;
    for (monster_iterator mi; mi; ++mi)
        if (mi->alive() && mi->attitude == ATT_HOSTILE
            && (!best || grid_distance(you.pos(),mi->pos()) < grid_distance(you.pos(),best->pos())))
            best = *mi;
    return best;
}

bool noel_action()
{
    if (!noel)
        return false;
    if (you.piety >= 120 && you.elapsed_time >= commander_ready && you.magic_points >= 5)
    {
        you.magic_points -= 5;
        you.piety -= 10;
        commander_until = you.elapsed_time + 5 + 60 + 2*invocation;
        commander_ready = commander_until + 100;
        spend_time(5);
        return true;
    }
    if (you.piety >= 30 && you.elapsed_time >= skill_until && you.magic_points >= 2 && you.piety >= 2)
    {
        you.magic_points -= 2;
        you.piety -= 2;
        skill_until = you.elapsed_time + 10 + 80 + 4*invocation;
        spend_time(10);
        return true;
    }
    return false;
}

void validate_noel_hooks()
{
    const scenario fixture = {"hook_checks",12,12,12,95,22,180,MONS_ETTIN,1};
    reset_character(fixture, 42);
    const auto require = [](bool condition, const char *message) {
        if (!condition)
            throw std::runtime_error(string("Noel hook validation: ")+message);
    };
    require(holo_armour_bonus() == 0 && holo_shield_bonus() == 0
            && holo_melee_damage(100) == 100 && !holo_force_immune(),
            "no-god hooks must be inert");
    noel = true;
    skill_until = you.elapsed_time + 100;
    require(you.skill(SK_LONG_BLADES) == 18 && you.skill(SK_ARMOUR) == 18
            && you.skill(SK_SHIELDS) == 18, "I12 skill bonus must be six");
    require(you.skill(SK_FIGHTING) == 12 && holo_fighting_skill(1) == 18
            && you.hp_max == 95 && you.skill(SK_DODGING) == 0,
            "Fighting must affect attack calculations without increasing HP");
    const int skill_ac = you.armour_class();
    const int skill_sh = player_shield_class();
    old_balance = false;
    commander_until = you.elapsed_time + 50;
    require(you.armour_class() == skill_ac+6
            && player_shield_class() == skill_sh+8
            && holo_melee_damage(100) == 130 && holo_force_immune(),
            "v2 commander must add AC6 / displayed SH4 and 30 percent melee");
    old_balance = true;
    require(you.armour_class() == skill_ac+10
            && player_shield_class() == skill_sh+12,
            "v1 commander must add AC10 / displayed SH6");
    set_skill_level(SK_LONG_BLADES, 25);
    require(you.skill(SK_LONG_BLADES) == 27, "temporary skills must cap at 27");
    you.elapsed_time = commander_until;
    require(holo_armour_bonus() == 0 && !holo_force_immune(),
            "commander must expire at its exact deadline");
    you.elapsed_time = skill_until;
    require(you.skill(SK_LONG_BLADES) == 25 && holo_fighting_skill(1) == 12,
            "skill buff must expire independently");
    noel = false;
    fprintf(stderr,"HoloCrawl Noel hook checks passed\n");
}
}

bool holo_engine_benchmark_requested()
{
    const char *value = getenv("HOLOCRAWL_ENGINE_BENCH");
    return crawl_state.test && value && string(value)=="1";
}

bool holo_benchmark_active() { return running; }
void holo_reset_validation_fixture()
{
    const scenario fixture={"batch_checks",12,12,12,10000,200,180,MONS_ETTIN,1};
    reset_character(fixture,43);
    for(monster_iterator mi;mi;++mi) mi->hit_points=mi->max_hit_points=10000;
}
void holo_validation_spend_time(int aut) { spend_time(aut); }
bool holo_spell_target(dist &target,bolt &beam,int range)
{
    monster *mon=nearest_enemy();if(!mon || !you.can_see(*mon) || grid_distance(you.pos(),mon->pos())>range) return false;
    target.target=mon->pos();target.isValid=true;target.isTarget=true;
    beam.set_target(target);beam.source=you.pos();return true;
}
bool holo_benchmark_finished() { return (running && (dead || left_by_banishment)) || holo_dungeon::finished(); }
bool holo_record_benchmark_banishment()
{
    if (!running)
        return false;
    left_by_banishment = true;
    return true;
}
bool holo_record_benchmark_death()
{
    if (!running || you.hp > 0)
        return false;
    dead = true;
    return true;
}

int holo_armour_bonus() { if(holo_campaign::active())return holo_campaign::noel_armour();return commander_active() ? (old_balance ? 8 : 4)+invocation/6 : 0; }
int holo_shield_bonus() { if(holo_campaign::active())return holo_campaign::noel_shield();return commander_active() && you.shield() ? (old_balance ? 5 : 3)+invocation/9 : 0; }

int holo_skill_bonus(skill_type skill, int scale)
{
    if(holo_campaign::active())return holo_campaign::noel_skill_bonus(skill,scale);
    if (!skill_active())
        return 0;
    const skill_type weapon_skill = you.weapon() && is_weapon(*you.weapon()) ? item_attack_skill(*you.weapon()) : SK_UNARMED_COMBAT;
    return skill == weapon_skill || skill == SK_ARMOUR || skill == SK_SHIELDS ? (5+invocation/9)*scale : 0;
}

int holo_fighting_skill(int scale)
{
    const int base = you.skill(SK_FIGHTING,scale);
    if(holo_campaign::active())return min(27*scale,base+holo_campaign::noel_fighting_bonus(scale));
    return skill_active() ? min(27*scale,base+(5+invocation/9)*scale) : base;
}

int holo_melee_damage(int damage)
{
    return (commander_active() || holo_campaign::noel_commander()) ? div_rand_round(damage*130,100) : damage;
}

bool holo_force_immune() { return commander_active() || holo_campaign::noel_commander(); }

int holo_run_engine_benchmark()
{
    const int trials = environment_integer("HOLOCRAWL_TRIALS", 10, 1, 100000);
    const int seed_start = environment_integer("HOLOCRAWL_SEED_START", 1000, 1, 1000000000);
    const bool reverse_variants = environment_integer("HOLOCRAWL_REVERSE_VARIANTS", 0, 0, 1);
    const string suite=getenv("HOLOCRAWL_SUITE") ? getenv("HOLOCRAWL_SUITE") : "noel";
    if (suite!="noel" && suite!="sopia" && suite!="batch" && suite!="batch-dev")
        throw std::runtime_error("Unknown HOLOCRAWL_SUITE");
    const bool sopia_suite=suite=="sopia";
    const bool batch_suite=suite=="batch" || suite=="batch-dev";
    const string requested_build=getenv("HOLOCRAWL_BUILD")?getenv("HOLOCRAWL_BUILD"):"melee";
    if(requested_build!="melee" && requested_build!="ranged" && requested_build!="magic") throw std::runtime_error("Unknown HOLOCRAWL_BUILD");
    if(!batch_suite && requested_build!="melee") throw std::runtime_error("Legacy reference suites use their original melee kit");
    if(suite=="batch" && holo_batch::implemented().size()!=20)
        throw std::runtime_error("Full 22-god batch is not implemented yet; refusing placeholder win rates");
    std::vector<string> variants=sopia_suite
        ? std::vector<string>{"no_god","noel_v2","sopia_ring","sopia_full"}
        : std::vector<string>{"no_god","noel_v1","noel_v2"};
    if(batch_suite) {
        variants={"no_god","noel_v2","sopia_full"};
        for(const string &name:holo_batch::implemented()) variants.push_back(name);
    }
    const bool balance_campaign=environment_integer("HOLOCRAWL_BALANCE_CAMPAIGN",0,0,1);
    const string balance_profile=getenv("HOLOCRAWL_BALANCE_PROFILE")?getenv("HOLOCRAWL_BALANCE_PROFILE"):"fixed";
    if(balance_campaign && balance_profile!="fixed" && balance_profile!="candidateA" && balance_profile!="candidateB" && balance_profile!="final")
        throw std::runtime_error("Unknown balance profile");
    const int mela_level=balance_campaign?environment_integer("HOLOCRAWL_MELA_LEVEL",balance_profile=="candidateB"?2:balance_profile=="candidateA"?1:0,0,2):0;
    const int vivi_level=balance_campaign?environment_integer("HOLOCRAWL_VIVI_LEVEL",balance_profile=="candidateB"?2:balance_profile=="candidateA"?1:0,0,2):0;
    const bool diagnostic=balance_campaign || environment_integer("HOLOCRAWL_DIAGNOSTIC",0,0,1);
    const bool series=environment_integer("HOLOCRAWL_SERIES",0,0,1);
    if(series && !diagnostic) throw std::runtime_error("Series requires diagnostic suite");
    if(diagnostic && !balance_campaign) {
        if(!batch_suite) throw std::runtime_error("Diagnostic requires batch suite");
        variants=series?std::vector<string>{"no_god","polka","polka__no_acrobat","polka__bank3","polka__no_acrobat_bank3"}
            :std::vector<string>{"no_god","mela","mela__no_ultimate","mela__no_breath","mela__no_embers","mela__no_fire_ward",
            "vivi","vivi__no_ultimate","vivi__no_makeup","vivi__no_burst","vivi__no_blind",
            "miko","miko__shrine_only","miko__no_fire","miko__no_ultimate","miko__pre_shrine",
            "lui","lui__no_command","lui__no_ultimate","lui__pre_flock",
            "polka","polka__no_acrobat","polka__bank3","polka__bank6","polka__no_acrobat_bank3"};
    }
    if(balance_campaign && balance_profile=="candidateB") variants={"no_god","mela","vivi"};
    const bool policy_depth=balance_campaign && environment_integer("HOLOCRAWL_POLICY_DEPTH",0,0,1);
    const bool extra_policy=policy_depth && environment_integer("HOLOCRAWL_EXTRA_POLICY",0,0,1);
    const int final_policy_mask=balance_campaign?environment_integer("HOLOCRAWL_FINAL_POLICY_MASK",0,0,7):0;
    if(policy_depth) {
        if(balance_profile!="final") throw std::runtime_error("Policy depth requires frozen final base");
        variants=requested_build=="melee"?std::vector<string>{"no_god","miko"}
            :requested_build=="ranged"?std::vector<string>{"no_god","polka","pekora"}:std::vector<string>{"no_god"};
    }
    const char *output = getenv("HOLOCRAWL_RESULTS");
    if (!output)
        throw std::runtime_error("HOLOCRAWL_RESULTS must name an output JSONL file");
    std::ofstream results(output);
    if (!results)
        throw std::runtime_error("Cannot open benchmark results file");
    std::vector<scenario> cases = {
        {"early_ogre",6,6,6,50,12,60,MONS_OGRE,1},
        {"early_three_orcs",6,6,6,50,12,60,MONS_ORC,3},
        {"mid_ettin",12,12,12,95,22,100,MONS_ETTIN,1},
        {"mid_three_warriors",12,12,12,95,22,100,MONS_ORC_WARRIOR,3},
        {"late_stone_giant",20,18,18,155,35,180,MONS_STONE_GIANT,1},
        {"late_two_stone_giants",20,18,18,155,35,180,MONS_STONE_GIANT,2},
        {"late_three_ettins",20,18,18,155,35,180,MONS_ETTIN,3},
        {"late_three_warriors",20,18,18,155,35,180,MONS_ORC_WARRIOR,3},
    };
    if(diagnostic && !series) {
        cases.push_back({"mid_orc_sorcerer",12,12,12,95,22,100,MONS_ORC_SORCERER,1});
        cases.push_back({"mid_two_centaurs",12,12,12,95,22,100,MONS_CENTAUR,2});
        cases.push_back({"mid_three_wargs",12,12,12,95,22,100,MONS_WARG,3});
        cases.push_back({"late_fire_dragon",20,18,18,155,35,180,MONS_FIRE_DRAGON,1});
        cases.push_back({"late_two_fire_elementals",20,18,18,155,35,180,MONS_FIRE_ELEMENTAL,2});
        cases.push_back({"late_two_elf_mages",20,18,18,155,35,180,MONS_DEEP_ELF_MAGE,2});
    }
    const string panel=getenv("HOLOCRAWL_BALANCE_PANEL")?getenv("HOLOCRAWL_BALANCE_PANEL"):"all";
    if(balance_campaign && panel!="all") {
        if(panel=="base") cases.resize(8);
        else if(panel=="challenge") cases.erase(cases.begin(),cases.begin()+8);
        else throw std::runtime_error("Unknown balance panel");
    }
    no_messages quiet;
    crawl_state.show_more_prompt = false;
    crawl_state.disables.set(DIS_CONFIRMATIONS);
    crawl_state.disables.set(DIS_DELAY);
    crawl_state.disables.set(DIS_SPAWNS);
    running = true;
    validate_noel_hooks();
    const scenario sopia_checks={"sopia_checks",12,12,12,95,22,180,MONS_OGRE,1};
    reset_character(sopia_checks,42);
    holo_sopia::validate();
    if(batch_suite) holo_batch::validate();
    if(getenv("HOLOCRAWL_WARD_SELFTEST_ONLY")) { running=false;return 0; }
    build_kind=requested_build;
    int emitted=0;
    for (const scenario &test : cases)
        for (int trial = 0; trial < trials; ++trial)
            for (int slot = 0; slot < int(variants.size()); ++slot)
            {
                const int variant = reverse_variants ? int(variants.size())-1-slot : slot;
                const string variant_name=variants[variant];const size_t split=variant_name.find("__");
                const string name=variant_name.substr(0,split),probe=split==string::npos?"":variant_name.substr(split+2);
                const bool prepare=probe=="pre_shrine" || probe=="pre_flock";
                holo_batch::set_policy(false,requested_build);holo_batch::configure_balance(0,0);
                holo_batch::set_probe("");reset_character(test,seed_start+trial,!prepare);
                noel = name=="noel_v1" || name=="noel_v2";
                old_balance = name=="noel_v1";
                holo_sopia::reset(name=="sopia_ring" || name=="sopia_full",invocation,name=="sopia_ring");
                if(batch_suite && name!="no_god" && name!="noel_v2" && name!="sopia_full")
                    holo_batch::reset(name,invocation);
                holo_batch::set_probe(probe);
                const bool candidate=balance_campaign && balance_profile!="fixed";
                const bool selected_policy=candidate && (
                    (requested_build=="melee" && (name=="polka" || name=="koyori"))
                    || (requested_build=="ranged" && (name=="aki" || name=="koyori" || name=="hajime"))
                    || (requested_build=="magic" && (name=="aki" || name=="okayu" || name=="pekora" || name=="polka" || name=="koyori" || name=="hajime"))
                    || (extra_policy && ((requested_build=="melee" && name=="miko") || (requested_build=="ranged" && (name=="polka" || name=="pekora"))))
                    || ((final_policy_mask&1) && requested_build=="melee" && name=="miko")
                    || ((final_policy_mask&2) && requested_build=="ranged" && name=="polka")
                    || ((final_policy_mask&4) && requested_build=="ranged" && name=="pekora"));
                holo_batch::set_policy(selected_policy,requested_build);
                if(candidate) {
                    holo_batch::configure_balance(mela_level,vivi_level);
                    if(name=="lui" && requested_build=="magic") holo_batch::set_probe("no_command");
                }
                if(name=="mela" && probe=="no_embers") holo_batch::s.defence=1;
                if(name=="polka") {
                    if(probe=="bank3" || probe=="no_acrobat_bank3") holo_batch::s.resource=3;
                    if(probe=="bank6") holo_batch::s.resource=6;
                }
                int prep_mp_cost=0;
                if(prepare) {
                    holo_batch::set_probe(probe,true);
                    const int count=probe=="pre_shrine"?1:you.piety>=75?3:2;
                    for(int n=0;n<count;++n) {
                        const int before=you.magic_points;
                        const int aut=probe=="pre_shrine"?holo_batch::martial_action(nullptr):holo_batch::summon_action(nullptr);
                        if(aut!=10) throw std::runtime_error("Native preparation action failed");
                        prep_mp_cost+=before-you.magic_points;spend_time(aut);
                    }
                    holo_batch::set_probe(probe);populate_enemies(test,seed_start+trial);
                }
                const int prep_aut=you.elapsed_time,prep_mp_end=you.magic_points;
                for(int wave=0;wave<(series?3:1);++wave) {
                const int wave_seed=seed_start+trial+100000*wave;
                if(wave) populate_enemies(test,wave_seed);
                const int fight_start=you.elapsed_time,hp_start=you.hp,mp_start=you.magic_points,piety_start=you.piety,ap_start=holo_batch::s.resource;
                int rf_min=100,rf_max=-100,blindable=0,hostiles=0;
                for(monster_iterator mi;mi;++mi) if(mi->alive() && mi->attitude==ATT_HOSTILE) {
                    rf_min=min(rf_min,mi->res_fire());rf_max=max(rf_max,mi->res_fire());
                    blindable+=mons_can_be_blinded(mi->type);++hostiles;
                }
                int actions = 0;
                while (!holo_benchmark_finished() && (nearest_enemy() || holo_batch::pending_resolution()) && you.elapsed_time-fight_start < 2000 && actions++ < 1000)
                {
                    you.turn_is_over=false;
                    you.time_taken=10;
                    if(build_kind!="melee") you.received_weapon_warning=true;
                    if (you.cannot_act())
                    {
                        spend_time(10);
                        continue;
                    }
                    if (noel_action())
                        continue;
                    const int batch_time=holo_batch::choose_action(nearest_enemy());
                    if(batch_time) { spend_time(batch_time);continue; }
                    coord_def preferred=you.pos();
                    if(build_kind!="melee" && nearest_enemy() && you.can_see(*nearest_enemy())) {
                        preferred=nearest_enemy()->pos();
                        while(grid_distance(you.pos(),preferred)>4) {
                            const coord_def delta=preferred-you.pos();preferred-=coord_def((delta.x>0)-(delta.x<0),(delta.y>0)-(delta.y<0));
                        }
                    }
                    const int ability_time=holo_sopia::choose_action(build_kind=="melee"?nullptr:&preferred);
                    if (ability_time)
                    {
                        spend_time(ability_time);
                        continue;
                    }
                    monster *target = nearest_enemy();
                    if(!target) { spend_time(10);continue; }
                    if(build_kind=="ranged" && you.inv[ENDOFPACK-1].defined() && you.can_see(*target)) {
                        dist aim;aim.target=target->pos();aim.isValid=true;aim.isTarget=true;
                        bolt shot;you.time_taken=10;holo_batch::begin_attack(*target,holo_batch::attack_kind::ranged);
                        const bool fired=throw_it(shot,ENDOFPACK-1,&aim);
                        if(fired) { holo_batch::end_attack(max(1,you.time_taken));spend_time(max(1,you.time_taken));continue; }
                        holo_batch::cancel_attack();
                    }
                    if(build_kind=="magic" && you.can_see(*target) && you.magic_points>0) {
                        const spell_type spell=test.xl>=20 && you.magic_points>=6?SPELL_BOLT_OF_FIRE
                            :you.magic_points>=2?SPELL_THROW_FLAME:SPELL_MAGIC_DART;
                        you.time_taken=10;holo_batch::begin_attack(*target,holo_batch::attack_kind::spell);
                        const bool cast=cast_a_spell(false,spell);
                        if(cast) { holo_batch::end_attack(max(1,you.time_taken));spend_time(max(1,you.time_taken));continue; }
                        holo_batch::cancel_attack();
                    }
                    if (adjacent(you.pos(),target->pos()))
                    {
                        you.time_taken = 10;
                        holo_batch::begin_attack(*target);
                        fight_melee(&you,target);
                        holo_batch::end_attack(max(1,you.time_taken));
                        spend_time(max(1,you.time_taken));
                    }
                    else
                    {
                        coord_def delta = target->pos()-you.pos();
                        delta.x = (delta.x > 0)-(delta.x < 0);
                        delta.y = (delta.y > 0)-(delta.y < 0);
                        const coord_def destination = you.pos()+delta;
                        if(holo_batch::passable_companion(actor_at(destination))) holo_batch::expire_passable_at(destination);
                        const coord_def old=you.pos();
                        if(!you.cannot_move() && !you.caught() && holo_batch::swap_companion(destination)) holo_batch::after_move(old,true);
                        else if (!you.cannot_move() && !you.caught() && !actor_at(destination) && !feat_is_solid(grd(destination)))
                        {
                            you.move_to_pos(destination);
                            if(batch_suite) you.apply_location_effects(old);
                            holo_batch::after_move(old,true);
                        }
                        spend_time(player_speed()*player_movement_speed()/10);
                    }
                }
                const char *outcome = dead ? "loss" : left_by_banishment ? "banished"
                    : !nearest_enemy() && !holo_batch::pending_resolution() ? "win" : "timeout";
                const int battle_hp=you.hp,battle_max_hp=you.hp_max,battle_mp=you.magic_points,battle_piety=you.piety,battle_aut=you.elapsed_time,ap_end=holo_batch::s.resource;
                const auto battle_metrics=holo_batch::get_metrics();const auto sopia_metrics=holo_sopia::get_metrics();
                if(series && wave<2 && string(outcome)=="win") safe_interwave_rest();
                results << "{\"schema\":" << (balance_campaign?6:diagnostic?5:batch_suite ? 4 : sopia_suite ? 3 : 2) << ",\"engine\":\"dcss-0.24.0\",\"god\":\"" << name
                        << "\",\"scope\":\"" << (batch_suite ? "batch-native-fixed-kit-combat-cores" : sopia_suite ? "sopia-native-fixed-melee-combat-core" : "noel-combat-abilities-fixed-kit-no-gifts")
                        << "\",\"scenario\":\"" << test.name
                        << "\",\"seed\":" << seed_start+trial << ",\"outcome\":\"" << outcome
                        << "\",\"hp\":" << battle_hp << ",\"max_hp\":" << (diagnostic?battle_max_hp:test.hp)
                        << ",\"mp\":" << battle_mp << ",\"piety\":" << battle_piety
                        << ",\"aut\":" << battle_aut << ",\"actions\":" << actions;
                if(balance_campaign) results << ",\"balance_profile\":\"" << balance_profile << "\",\"mela_level\":" << mela_level << ",\"vivi_level\":" << vivi_level << ",\"selective_policy\":" << (selected_policy?"true":"false");
                if(policy_depth) results << ",\"policy_depth\":true,\"extra_policy\":" << (extra_policy?"true":"false");
                if(final_policy_mask) results << ",\"final_policy_mask\":" << final_policy_mask;
                if(diagnostic) results << ",\"variant\":\"" << variant_name << "\",\"wave\":" << wave << ",\"wave_seed\":" << wave_seed
                    << ",\"series_waves\":" << (series?3:1) << ",\"effects_are_cumulative\":true,\"combat_aut\":" << battle_aut-fight_start
                    << ",\"hp_start\":" << hp_start << ",\"mp_start\":" << mp_start << ",\"piety_start\":" << piety_start
                    << ",\"ap_start\":" << ap_start << ",\"ap_end\":" << ap_end << ",\"prep_aut\":" << prep_aut
                    << ",\"prep_mp_cost\":" << prep_mp_cost << ",\"prep_mp_end\":" << prep_mp_end
                    << ",\"initial_hostiles\":" << hostiles << ",\"initial_rf_min\":" << rf_min << ",\"initial_rf_max\":" << rf_max
                    << ",\"initial_blindable\":" << blindable << ",\"rest_aut\":" << you.elapsed_time-battle_aut
                    << ",\"hp_after_rest\":" << you.hp << ",\"mp_after_rest\":" << you.magic_points << ",\"piety_after_rest\":" << int(you.piety) << ",\"ap_after_rest\":" << holo_batch::s.resource
                    << ",\"post_rest_outcome\":\"" << (dead?"loss":left_by_banishment?"banished":"alive") << "\"";
                if (sopia_suite || batch_suite)
                {
                    if(batch_suite) results << ",\"build\":\"" << build_kind << "\"";
                    const auto &m=sopia_metrics;
                    results << ",\"effects\":{\"ring_casts\":" << m.ring_casts << ",\"ring_ticks\":" << m.ring_ticks
                        << ",\"ring_hits\":" << m.ring_hits << ",\"field_casts\":" << m.field_casts
                        << ",\"field_ticks\":" << m.field_ticks << ",\"field_hits\":" << m.field_hits
                        << ",\"pull_attempts\":" << m.pull_attempts << ",\"pulls\":" << m.pulls
                        << ",\"big_casts\":" << m.big_casts << ",\"detonations\":" << m.detonations
                        << ",\"damage\":" << m.damage;
                    if(batch_suite) {
                        const auto &b=battle_metrics;
                        results << ",\"batch_casts\":" << b.casts << ",\"batch_hits\":" << b.hits
                            << ",\"batch_damage\":" << b.damage << ",\"batch_healed\":" << b.healed
                            << ",\"batch_absorbed\":" << b.absorbed << ",\"batch_moves\":" << b.moves
                            << ",\"batch_summons\":" << b.summons << ",\"batch_procs\":" << b.procs
                            << ",\"batch_kills\":" << b.kills << ",\"batch_self_damage\":" << b.self_damage
                            << ",\"batch_deferred_paid\":" << b.deferred_paid;
                        if(diagnostic) results << ",\"ap_earned\":" << b.ap_earned << ",\"ap_spent\":" << b.ap_spent
                            << ",\"performances_started\":" << b.performances_started << ",\"performances_completed\":" << b.performances_completed
                            << ",\"performances_expired\":" << b.performances_expired << ",\"blind_attempts\":" << b.blind_attempts << ",\"blind_successes\":" << b.blind_successes;
                    }
                    results << "}";
                }
                results << "}\n";
                results.flush();
                ++emitted;
                if(string(outcome)!="win" || holo_benchmark_finished()) break;
                }
            }
    running = false;
    fprintf(stderr,"HoloCrawl native-engine benchmark complete: %d encounters\n",emitted);
    return 0;
}
