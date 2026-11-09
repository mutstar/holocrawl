# Native benchmark datasets

- `RESULTS_NOEL.md`, `final-noel-1000.*`: original Noel 24,000-encounter dataset.
  Its implementation-status notes describe the stage before Sopia was added.
- `sopia/RESULTS_SOPIA.md`, `sopia/final-sopia-1000.*`: Sopia 32,000-encounter
  ring/full comparison, including current Noel and no-god reference groups.
- `validation.json` and `sopia/validation.json`: completed checks and scope.
- `invalidated_runs.json` and `sopia/run_history.json`: excluded preliminary runs.

Each dataset preserves raw JSONL, summary, manifest, source patch and design snapshot.
Shard manifests/results/logs are also preserved. Toolchain and executable snapshots
remain local under ignored paths; rebuild from pinned upstream plus the saved patch.
Current implementation status is `engine/implementation_status.json`: two combat
cores are tested, the other 20 gods and normal campaign integration remain unfinished.
