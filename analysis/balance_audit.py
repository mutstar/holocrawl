"""Exact formula audit of custom design, not a DCSS combat simulation.

Run from any directory. Writes balance_results.json alongside this script.
Enemy AC sensitivity is explicitly a simplified uniform subtraction model.
"""
from collections import Counter
from pathlib import Path
import json
import math
import hashlib
import re


def dice(n, sides, bonus=0):
    counts = Counter({bonus: 1})
    for _ in range(n):
        nxt = Counter()
        for value, count in counts.items():
            for roll in range(1, sides + 1):
                nxt[value + roll] += count
        counts = nxt
    total = sum(counts.values())
    return {value: count / total for value, count in counts.items()}


def mean(n, sides, bonus=0):
    return n * (sides + 1) / 2 + bonus


def after_ac(dist, ac):
    # Sensitivity model only: independent uniform AC roll, no GDR/EV/SH.
    return sum(p * sum(max(0, damage - r) for r in range(ac + 1))
               / (ac + 1) for damage, p in dist.items())


def monster_fire(dist, resistance):
    if resistance >= 3:
        return 0.0
    denominator = (1,2,5)[resistance]
    return sum(p*(damage//denominator) for damage,p in dist.items())


def metrics(i, tuned=True):
    f = lambda divisor: i // divisor
    duration = (60 + 2 * i) / 10
    return {
        "스이세이": {"cut_unmarked": mean(2, 8+f(2)), "cut_stars5": mean(2, 8+f(2), 15), "meteor_unmarked": mean(3, 10+f(2)), "meteor_stars5": mean(3, 10+f(2), 25), "next_star_reward_stars1": mean(1,7 if tuned else 4), "next_star_reward_stars3": mean(1,11 if tuned else 6), "next_star_reward_stars5": mean(1,15 if tuned else 8)},
        "미코": {"heal_per_turn": (1+i/12)/2, "ranged_reduction_pct": 10+f(3), "ultimate_reduction_pct": 15+f(3), "combined_ranged_reduction_pct": 100*(1-(1-(10+f(3))/100)*(1-(15+f(3))/100))},
        "아키": {"thorns3_per_turn": mean(1, 2+f(6), 3)/2, "two_plants_per_turn_all_hit": 2*mean(1, 4+f(3))/1.5, "bloom_stacks3": mean(2, 8+f(2), 18)},
        "후부키": {"two_clones_per_action_all_hit": 2*mean(1, 6+f(3)), "four_clones_per_action_all_hit": 4*mean(1, 6+f(3)), "ultimate_duration_turns": (40+i)/10, "attack_time_scaling_below_10aut": tuned},
        "아야메": {"passive_accuracy": 3+f(6), "passive_slay": 2+f(9), "passive_ev": 2+f(9), "ultimate_slay": 5+f(9), "ultimate_ev": 5+f(9), "double_slash_extra_weapon_attacks": 1},
        "초코": {"kiss_stacks5": mean(2, 6+f(3), 15), "kiss_heal_upper_before_floor_overkill": .4*mean(2, 6+f(3), 15), "charm_stacks5_hd10_pct": min(85, max(15, 50+2*i+25-30)), "charm_hd10_duration_turns": min(80, max(20, 40+2*i-10))/10},
        "코로네": {"passive_max_slay": 3, "ultimate_extra_fist_per_action_all_hit": mean(1, 6+f(2)), "deferred_damage_fraction": .25, "deferred_damage_forgiven": 0},
        "오카유": {"shield_full_food": 4+f(3)+5, "dream_stacks4": mean(2, 8+f(2), 20), "dream_sleeping_stacks4": 1.3*mean(2, 8+f(2), 20), "max_slow_time_multiplier": 1.32, "food_cast_cost_low_high": (10 if tuned else 20)+25, "food_kill_refund": 23},
        "페코라": {"bomb": mean(2, 8+f(3)), "five_bombs_same_target": 5*mean(2, 8+f(3)), "five_bombs_setup_mp": 12, "five_bombs_setup_piety": 7, "five_bombs_setup_actions_turns": 5.5, "ultimate_one_blast": mean(3, 8+f(3)), "ultimate_three_overlaps": 3*mean(3, 8+f(3))},
        "노엘": {"skill_bonus": 5+f(9), "ultimate_melee_pct": 30, "ultimate_ac": (4 if tuned else 8)+f(6), "ultimate_sh": (3 if tuned else 5)+f(9), "skill_duration_turns": (80+4*i)/10},
        "와타메": {"passive_heal_per_turn": .3+i/90, "barrier_max_total": 3*(5+f(3)), "barrier_three_hits_of_10": 3*min(5+f(3), math.floor(10*.4)), "ultimate_regen_total_continuous": 3*(.3+i/90)*(80+2*i)/10, "ultimate_regen_increment_continuous": 2*(.3+i/90)*(80+2*i)/10, "lethal_rescue_max_hp_pct": 15},
        "토와": {"cover_four_shots_all_hit": 4*mean(2, 5+f(3)), "ultimate_eight_shots_all_hit": 8*mean(2, 5+f(3)), "full_combo_mp": 10, "full_combo_piety": 16, "ultimate_target_ac_multiplier": .7},
        "라미": {"bonus_cold_per_action": mean(1, 3+f(6)), "breath": mean(2, 7+f(3)), "tipsy_breath": 1.15*mean(2, 7+f(3)), "banquet_drunk80_per_tick": mean(1, 6+f(3), 4), "banquet_base_duration_aut": 60+2*i, "banquet_tipsy_duration_aut": math.floor((60+2*i)*1.15), "banquet_base_ticks_strict_expiry": (60+2*i-1)//20, "banquet_tipsy_ticks_strict_expiry": (math.floor((60+2*i)*1.15)-1)//20},
        "폴카": {"finale_applause6": mean(2, 8+f(3), 24), "curtain_heal_applause6": 8+f(2)+24, "confuse_hd10_applause6_pct": min(85,max(15,45+2*i+18-30)), "confuse_duration_turns": (10+30+f(3))/10},
        "코요리": {"reaction_fire": mean(2, 6+f(3)), "reaction_shock": mean(3, 4+f(3)), "critical_fire": mean(4 if tuned else 3, 8+f(3)), "critical_shock": mean(4, 6+f(3)), "critical_fire_text_ignores_rf": not tuned, "critical_shock_ac_reduction": 6, "critical_total_mp_including_two_reagents": 8, "critical_total_piety": 10, "critical_actions_turns_including_manufacture": 3.5},
        "루이": {"crow_one_hit": mean(1,5+f(3)), "three_crows_per_turn_all_hit_in_position": 3*mean(1,5+f(3)), "six_crows_per_turn_all_hit_in_position": 6*mean(1,5+f(3)), "three_crows_dive_all_hit": 3*(mean(1,5+f(3))+3+f(6)), "six_crows_dive_all_hit": 6*(mean(1,5+f(3))+3+f(6)), "crow_hp": 12+i, "crow_ev": 14+f(3)},
        "라덴": {"painting_extra_per_action": mean(1,2+f(6)), "painting_extra_ignores_ac": tuned, "sculpture_ac": 2+f(9), "craft_kill_heal": 2+f(6), "explosion_stacks3": mean(2,6+f(3),12), "wave": mean(2,5+f(3)), "shield": 10+2*i//3, "ultimate_explosion_stacks3": mean(3,6+f(3),12), "ultimate_shield": 16+i},
        "하지메": {"beat1_bonus": 3+f(6), "beat3_bonus": 3*(3+f(6)), "charge_beat3": mean(2,6+f(3),9), "ultimate_move_hit": mean(2,4+f(3)), "ultimate_duration_turns": duration},
        "스우": {"wave": mean(2,7+f(3)), "ultimate_pulse": mean(2,3+f(6)), "ultimate_ticks_strict_expiry": (60+2*i-1)//10, "ultimate_pulse_total_full_residence": mean(2,3+f(6))*((60+2*i-1)//10), "ultimate_wave": mean(2,7+f(3),3+f(3))},
        "비비": {"makeup_pct": 10+f(6), "ultimate_one_attention_pct": 15+f(6), "ultimate_five_attention_pct": 35+f(6), "flash_base": mean(2,6+f(3)), "flash_makeup": mean(2,6+f(3))*(1+(10+f(6))/100), "flash_max_attention": mean(2,6+f(3))*(1+(35+f(6))/100)},
        "소피아": {"ring_per_turn": mean(1,4+f(3)), "field_per_two_turns": mean(1,4+f(3)), "ring_plus_field_per_turn": 1.5*mean(1,4+f(3)), "pull_hd10_pct": min(90,max(15,65+2*i-30)), "bang_charge1": mean(3,8+f(3),6), "bang_charge3": mean(3,8+f(3),18)},
        "메라": {"ember": mean(1,3+f(6)), "spray_heat0": mean(2,6+f(3)), "spray_heat6": mean(2,6+f(3),24), "ultimate_spray_heat6": mean(3,6+f(3),24), "ultimate_self_fire_taken_without_other_rf": (1/3)*.5},
    }


result = {
    "revision": "v2-first-balance-adjustments",
    "scope": "Formula comparison; no engine, AI, win rate, hit chance or real battle simulation.",
    "formula_source": "Manually transcribed custom formulas from HOLOCRAWL_DESIGN.md. Update this script when formulas change.",
    "design_sha256_at_run": hashlib.sha256(Path(__file__).resolve().parents[1].joinpath("HOLOCRAWL_DESIGN.md").read_bytes()).hexdigest(),
    "skill_samples": {str(i): metrics(i) for i in (0,6,12,18,27)},
    "damage_ac_sensitivity_i12": {},
    "attack_speed_sensitivity_i12": {},
    "resistance_sensitivity": {},
    "percentage_bonus_before_defence": {
        str(base): {"vivi_passive12": base*.12,
                    "vivi_ultimate_max37": base*.37,
                    "noel_ultimate30": base*.30}
        for base in (12,25,40)
    },
    "source_references": {
        "normal_ac_branch": "https://github.com/crawl/crawl/blob/0.24.0/crawl-ref/source/actor.cc#L319",
        "resistance": "https://github.com/crawl/crawl/blob/0.24.0/crawl-ref/source/fight.cc#L486",
        "caveat": "Normal uniform AC subtraction branch only, no guarantee custom effects use this AC rule. GDR/EV/SH/AI absent. Fire resistance figures are pre-integer rounding.",
    },
}
for ac in (0,10,20):
    result["damage_ac_sensitivity_i12"][str(ac)] = {
        "raden_extra_per_successful_main_hit": mean(1,4),
        "raden_v1_extra_per_successful_main_hit": after_ac(dice(1,4),ac),
        "sopia_ring_per_tick": after_ac(dice(1,8),ac),
        "sopia_ring_plus_field_per_turn": 1.5*after_ac(dice(1,8),ac),
        "su_ultimate_per_tick": after_ac(dice(2,5),ac),
        "hajime_move_per_hit": after_ac(dice(2,8),ac),
        "lui_three_crows_per_turn_before_accuracy": 3*after_ac(dice(1,9),ac),
        "lui_six_crows_per_turn_before_accuracy": 6*after_ac(dice(1,9),ac),
    }
for delay in (.5,.7,1.0,1.5):
    result["attack_speed_sensitivity_i12"][str(delay)] = {
        "fubuki_four_clones_raw_extra_per_turn_all_hit": 22*min(delay,1)/delay,
        "fubuki_v1_four_clones_raw_extra_per_turn_all_hit": 22/delay,
        "rejected_strict_10aut_cooldown_raw_per_turn": 22/(math.ceil(1/delay)*delay),
        "korone_fist_raw_extra_per_turn_all_hit": 6.5/delay,
        "raden_chip_raw_extra_per_turn_before_main_accuracy": 2.5/delay,
        "hajime_move_raw_per_turn_if_move_delay": 9/delay,
    }
for resistance, fraction in ((0,1),(1,.5),(2,.2),(3,0)):
    result["resistance_sensitivity"][str(resistance)] = {
        "mera_spray_heat6": 35*fraction,
        "mera_ultimate_spray_heat6": 40.5*fraction,
        "polka_finale6": 37*fraction,
        "koyori_v1_critical_fire_ignoring_rf": 19.5,
        "koyori_v2_critical_fire_before_integer_rounding": 26*fraction,
        "koyori_v2_critical_fire_integer_exact": monster_fire(dice(4,12),resistance),
    }

assert all(len(profile)==22 for profile in result["skill_samples"].values())
for n, sides in ((1,4),(1,8),(2,5),(2,8),(3,12)):
    distribution = dice(n,sides)
    assert math.isclose(sum(distribution.values()),1)
    assert math.isclose(after_ac(distribution,0),mean(n,sides))
    assert after_ac(distribution,20) <= after_ac(distribution,10) <= mean(n,sides)

baseline_path = Path(__file__).with_name("baseline_v1") / "balance_results.json"
archived = json.loads(baseline_path.read_text(encoding="utf-8"))
def god_sections(path):
    return {match.group(2):match.group(0) for match in re.finditer(
        r"^## (\d+) (.+)\n[\s\S]*?(?=^## |\Z)",
        path.read_text(encoding="utf-8"),re.MULTILINE)}

old_sections = god_sections(baseline_path.with_name("HOLOCRAWL_DESIGN.md"))
new_sections = god_sections(Path(__file__).resolve().parents[1]/"HOLOCRAWL_DESIGN.md")
assert len(old_sections) == len(new_sections) == 22
changed_sections = sorted(name for name in old_sections if old_sections[name] != new_sections[name])
assert set(changed_sections) == {"스이세이","후부키","오카유","노엘","코요리","주우후테이 라덴"}, changed_sections
comparison = {
    "scope": result["scope"],
    "baseline": str(baseline_path.resolve()),
    "design_sha256_at_run": result["design_sha256_at_run"],
    "all_22_gods": {},
    "changed_gods": [],
    "changed_design_sections": changed_sections,
    "raden_ac_i12": result["damage_ac_sensitivity_i12"],
    "fubuki_attack_speed_i12": result["attack_speed_sensitivity_i12"],
    "koyori_rf_i12": result["resistance_sensitivity"],
    "suisei_reward_ac": {},
    "fubuki_full_ultimate_window_i12_raw": {},
    "resource_cycle": {
        "okayu_before": {"food_cost":45,"kill_refund":23,"net_cost":22,"ordinary_direct_kills_to_repay":8},
        "okayu_after": {"food_cost":35,"kill_refund":23,"net_cost":12,"ordinary_direct_kills_to_repay":4},
        "note": "Repayment assumes +3 food per ordinary direct kill, no food items/natural decay. Missed dream kill gives no refund; foodless species still disadvantaged.",
    },
}
# Validate every previously saved metric before relying on before/after output.
for skill in (0,6,12,18,27):
    before,after = metrics(skill,False),metrics(skill,True)
    for god,old_metrics in archived["skill_samples"][str(skill)].items():
        for key,value in old_metrics.items():
            assert before[god][key] == value, (skill,god,key)
    comparison["all_22_gods"][str(skill)] = {
        god: {"changed": {key:{"before":before[god][key],"after":value}
                          for key,value in stats.items() if before[god][key] != value},
              "before": before[god], "after": stats}
        for god,stats in after.items()
    }
comparison["changed_gods"] = [god for god,record in comparison["all_22_gods"]["12"].items() if record["changed"]]
assert set(comparison["changed_gods"]) == {"스이세이","후부키","오카유","노엘","코요리","라덴"}
for stars in (1,3,5):
    comparison["suisei_reward_ac"][str(stars)] = {
        str(ac): {"before":after_ac(dice(1,3+stars),ac),
                  "after":after_ac(dice(1,5+2*stars),ac)} for ac in (0,10,20)
    }
for delay_aut in (5,7,10,15):
    actions = (52-1)//delay_aut  # Complete attacks while clones are still active.
    comparison["fubuki_full_ultimate_window_i12_raw"][str(delay_aut)] = {
        "actions":actions,"before":actions*22,
        "after":actions*22*min(delay_aut,10)/10,
        "note":"All four clones alive and in range, all hit; no defences. 52aut effect window, no setup attacks included.",
    }
assert monster_fire(dice(4,12),0) == 26
assert math.isclose(monster_fire(dice(4,12),1),12.75)
assert monster_fire(dice(4,12),3) == 0
assert comparison["resource_cycle"]["okayu_after"]["net_cost"] == 12

output = Path(__file__).with_name("balance_results.json")
output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
comparison_output = Path(__file__).with_name("balance_comparison_v2.json")
comparison_output.write_text(json.dumps(comparison,ensure_ascii=False,indent=2),encoding="utf-8")
print(f"22 gods x 5 skill samples calculated: {output}")
print(json.dumps({"changed_gods":comparison["changed_gods"],
                  "before_after_i12":{god:comparison["all_22_gods"]["12"][god]["changed"] for god in comparison["changed_gods"]},
                  "fubuki_speed":result["attack_speed_sensitivity_i12"],
                  "koyori_rf":result["resistance_sensitivity"]},ensure_ascii=False,indent=2))
