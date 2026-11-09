# HoloCrawl native engine development

DCSS 0.24.0, upstream commit `a7d21def0a8b0b39c6825b643a3b51f371b73583`.
The local checkout is `engine/crawl`. The exported patch is the portable source change;
the original handoff ZIP contains design documents, not the engine.

## Current scope

All 22 combat cores are connected to the explicit native benchmark. The 20 new
modules passed native fixture checks and all three 552-encounter forward/reverse
samples reproduced exactly. The 1,000-seed all-god cohorts were intentionally stopped for a home handoff;
development samples must not be presented as final balance results. See
`analysis/native/batch/VALIDATION_SCOPE.md` and `engine/implementation_status.json`.
Native hit rolls, AC/GDR, shields,
monster equipment, monster AI, regeneration, movement and world turns run normally.
Normal campaign integration, equipment gifts, worship/ability UI, campaign
piety/wrath, and save integration remain future work.

Noel's original native batch passed: **24,000 encounters**, eight scenarios, three variants,
1,000 seeds per group. The four complete shards have identical source/build/design
hashes and disjoint, contiguous seed ranges. See `analysis/native/RESULTS_NOEL.md`.
Forward/reverse replays matched on 120 encounters; the merged batch also exactly
matched 240 independently run encounters and 24 encounters at the former shaft-crash
seed 1882. Startup hook checks passed. No timeouts occurred; four encounters ended
through actual banishment and are reported separately from wins and HP deaths.

Sopia's new suite passed **32,000 encounters**: no god, current Noel, ring-only Sopia,
and full Sopia, with eight scenarios and 1,000 seeds per group. See
`analysis/native/sopia/RESULTS_SOPIA.md`. All 160 reverse-order overlaps and 320
independent overlaps match exactly; all 16,000 shared no-god/current-Noel combat
outcomes/resources/times match the earlier dataset. Six banishments, zero timeouts.
Native checks cover timer expiry/refresh, elapsed ticks, occupied/walled destinations,
stationary-target compression, ally exclusion, off-player centres, charge, detonation,
pushes and costs. The controller installs fields on the player's tile and waits for
three charges or impending expiry. Position optimisation and earlier detonation are
not tested. Periodic effects drain due logical aut ticks in the native post-monster
world phase; within-action intermediate monster positions are not reconstructed.

Pre-final runs are excluded. Fixes cover exploration shafts, pending monster action
queues on death/banishment, and distortion-brand banishment leaving the fixed room.
Native banishment is recorded as an encounter ending rather than disabled.
The earlier Windows Code Integrity execution block was resolved by the user turning
off Smart App Control; the agent did not change security settings. Historical evidence
is in `analysis/native/windows_execution_block.json`.

## Build and run (PowerShell, workspace root)

```powershell
./scripts/bootstrap-engine.ps1
./scripts/build-engine.ps1
./scripts/run-engine-bench.ps1 -Trials 10 -SeedStart 1880 -Name verified-forward
./scripts/run-engine-bench.ps1 -Trials 5 -SeedStart 1882 -Name verified-reverse -ReverseVariants
./.toolchain/msys64/mingw64/bin/python.exe analysis/compare_engine_replays.py runtime/results/verified-forward.jsonl runtime/results/verified-reverse.jsonl
./scripts/run-engine-bench.ps1 -Trials 1000 -Name verified-noel-1000
./.toolchain/msys64/mingw64/bin/python.exe analysis/summarize_engine_bench.py runtime/results/verified-noel-1000.jsonl
./scripts/run-engine-bench.ps1 -Suite sopia -Trials 1000 -Name verified-sopia-1000
./.toolchain/msys64/mingw64/bin/python.exe analysis/summarize_engine_bench.py runtime/results/verified-sopia-1000.jsonl
```

Run these only after execution is permitted by the machine's policy. Each run requires
a fresh name and preserves a binary snapshot, source patch, design snapshot and hash
manifest. Results are JSONL; duplicate/incomplete seed pairs are rejected. Replays must
match exactly regardless of batch position and variant order. Startup also checks
Noel's I12 skill bonus, unchanged HP, AC/SH display scaling, damage multiplier,
independent expiry and level-27 cap.

The bootstrap pins the MSYS2 archive checksum and the upstream source/submodule
revisions. A fresh download/install path has not been tested on a second machine;
existing-install bootstrap and the native build were verified here. Package versions
may change because MSYS2 package repositories are rolling. Toolchain files remain
project-local; no global PATH edits are required.

## Encounter interpretation

Eight fixed scenarios, three variants (`no_god`, `noel_v1`, `noel_v2`), matched enemy
seeds, Human Fighter with identical prescribed skills, HP, MP, equipment and piety.
Fixtures cover ogre, three orcs, ettin, three orc warriors, stone giant, two stone
giants, three ettins and late three orc warriors. All enemies start adjacent in an
open room. The controller casts available Noel buffs, then approaches/melees.
There are no potions, retreat decisions or equipment gifts. XP/training, exploration
traps and random reinforcements are excluded; piety is a fixed starting budget.
Monster combat rules and natural status/regen processing remain native.

HP depletion records a loss; no wizard immortality is used. Encounters exceeding
2,000 aut are timeouts, separately reported. A 1,000-seed batch is 24,000 encounters.
Banishment ends a fixed encounter as `banished`, which is neither a win nor HP death.
These are conditional encounter win rates, not dungeon completion or human player
win rates. The datasets cover fixed melee encounters and the implemented combat cores only.

## Remaining work

1. Add ranged, magic, terrain, resistance and build variants before balance changes.
2. Implement the other gods with their actual resource/timing/entity mechanics;
   never substitute generic stat multipliers for missing implementations.
3. Add normal gameplay integration, gifts, progression, wrath and persistence.

The source patch follows upstream licensing; see `LICENSE.upstream` and upstream's
per-component licenses. No commits, pushes or PRs were created.
