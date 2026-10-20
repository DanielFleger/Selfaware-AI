# GamerGrill / next-agent handoff

## Start here

The current implementation has been moved into the package structure, not left
in a parallel flat source tree. See [ORGANIZATION.md](ORGANIZATION.md) for the
full repository map and [relocations.json](relocations.json) for every old/new
path and original content hash.

- `src/selfaware/runtime/live/`: current live runner and orchestration.
- `src/selfaware/{macro,micro,strategy,services,learning,telemetry}/`: existing
  policies, models, queries and analysis, sorted by responsibility.
- `src/selfaware/game/ucp/`: existing native/file-channel helpers.
- `src/selfaware/{domain,coordination,runtime,game,execution}/`: typed offline
  framework contracts alongside explicitly named current implementation modules.
- `src/selfaware/tools/`: setup, analysis, checks and live experiments.
- `data/research/`, `docs/research/`, `docs/plans/`, `research/native/`,
  `bridge/snapshots/`, `assets/ai/`: evidence, knowledge, plans and assets.

The current task/status source is [backlog/backlog.json](backlog/backlog.json);
read its focus with `uv run selfaware run backlog fokus`. The engineering
acceptance details in `BACKLOG.md` link back to those point IDs.

The framework does not yet drive the real game. A green CI run proves the
offline contracts, relocation integrity, selected existing checks and Python syntax; it does not prove live matches or
fix the original connector. Read [BACKLOG.md](BACKLOG.md) before live work.

This organization work starts from upstream `58a0d50`, which already includes
the opening optimization (`813a98b`) and the separate
[Audit_Sharky.html](research/Audit_Sharky.html). Those upstream changes are preserved.
Latest upstream through `a1f41a2` is merged, including the active backlog tool,
B-114 command/player research, the B-115 Rust DLL and Lua loader,
post-match training, the paired 1v1 learning loop and B-132 army budgeting.
Research, match records and Ghidra captures are preserved. The path manifest uses that updated source baseline. The earlier
source audit in `audit/` remains pinned to its `7b994b7` baseline.

## Fresh checkout

Install uv 0.12.9, then run from the repository root:

```sh
uv sync --locked --extra dev
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run selfaware doctor --offline
uv run selfaware replay tests/fixtures/legacy_sample.jsonl
uv build
```

Python 3.11 is the default in `.python-version`; CI covers Windows/Linux on
Python 3.11 and 3.14. `uv.lock` pins resolved dependencies. The base package has
no third-party runtime dependencies and never discovers/starts a game on import.

For optional legacy libraries and Lua audit probes:

```sh
uv sync --locked --extra dev --extra legacy --extra audit
```

Do not run every `*_pruefen.py` script indiscriminately: some launch or modify
real games. The new `tests/` suite is offline. The historical audit runner is a
separate read-only diagnostic described in [audit/README.md](../audit/README.md).

## Inspect real recorded state

```sh
uv run selfaware replay data/research/lage_20261018_162313_i1.jsonl.gz --player 1 --limit 3
```

Specify the actual player whose `st` values the trace records. A trace does not
reliably encode that identity itself. Omitting `--limit` reads the complete
file. The decoder verifies tick coherence and table shape; any failure names
its source line. Inspect damaged traces instead of suppressing the error.
For example, the real trace above has a known tick mismatch at line 37; see
`DATA-01` in the backlog. The three-sample command is a successful schema smoke
check, not an assertion that the entire archive is clean.

## Before actual-game debugging

1. Obtain the real VillageStudio project/module, its building catalogue and
   `VillageStudio/werkzeug/instanz.py`. They are not contained in this repository. Capture
   their authoritative source/revision and hashes; do not fabricate replacements.
2. Copy `configs/local.example.toml` to `configs/local.toml` and fill actual
   paths and installed module SHA256. Run:

   ```sh
   uv run selfaware doctor --config configs/local.toml
   ```

   Exit code 2 means live setup remains blocked/unverified. The doctor only
   reads files and reports hashes; even matching files are not native API tests.
3. Read `bridge/README.md`, `audit/AUDIT.txt`, `README.md`'s match-record rule,
   and the map/opponent/environment entries in `docs/research/Wissensregister.md`.
4. Existing scripts retain their Steam installation default and `SHC_*` instance/
   player settings. `SELFAWARE_VILLAGE_STUDIO_PATH` now also selects the external
   catalogue/helper folder used by the relocated tools. Read the path and
   runtime-state migration notes in [ORGANIZATION.md](ORGANIZATION.md) before
   invoking a live tool. TOML diagnostics do not reconfigure the old sender.
5. Resolve the connector blockers with isolated failure tests, then validate
   one controlled native operation at a time using the actual module.

## Next implementation boundaries

Read the [strategy expansion design](plans/STRATEGY_DESIGN.md) for the requested
aggressive/defensive repertoire, state transitions, castle construction phases,
technology prerequisites and evaluation scenarios. B-133 delivers that design;
B-134 through B-139 remain implementation points. Reuse the existing raid,
guard and granary-ring behavior as the first migration slices.

Follow the authoritative backlog focus. B-96 selects Rust for the native core,
and B-115 is built upstream. Its crate is now in `crates/samurai-kern/`;
[build it explicitly for 32-bit Windows](../crates/samurai-kern/README.md).
The upstream native-check evidence is preserved, and Windows CI compiles the DLL.
No game was run to revalidate native behavior during this organization work.
Keep the Python offline harness/current policies as a baseline while that core develops. `LIVE-01` describes acceptance for
a reliable single-owner UCP
GamePort with typed request/results and observation-based effect confirmation.
Apply the GamePort ownership/evidence contracts across that native boundary.
Use the existing channel as a starting transport. Its wire contract must be
verified against the missing init.lua before making it the new executor.

After that, migrate one defense/raid task behind `runtime.Engine` and route all
its commands through the coordinator. Do not enable a migrated task alongside
an unrestricted legacy writer that can command the same units.

## How to build on the framework

- Subclass `runtime.Engine`; override `propose(snapshot)` and optionally
  `on_start(session)`, `on_outcomes(outcomes)` and `on_end()`.
- Return immutable `Intent`s using logical `Command`s. Give each intent a
  producer-specific ID, source snapshot, deadline, explicit actors/targets,
  complete resource cost and reason. Higher numeric priority wins fresh conflicts.
- Reuse the ID while it is pending. A deliberate new attempt gets a new ID;
  historical IDs stay deduplicated for the game epoch.
- Implement/extend GamePort separately. A transport receipt is never game
  success. Verify postconditions from later samples and emit typed outcomes.
- Start with the failure scenarios in `tests/test_runtime.py`,
  `test_execution.py`, `test_coordination.py` and `test_replay.py`.
- Record behavior compatibility and policy-strength improvement separately.
  Replaying an old future does not measure the result of different actions.

## Repository transfer

No automated action transfers ownership or assumes GamerGrill credentials.
The workflow, package and local configuration contain no owner-specific API
credentials. After the owner transfer, update the clone's origin as needed,
check Actions availability/permissions, run the offline checks, and configure
the receiving machine's paths. Preserve the PR/commit history and research
provenance. Pinned reference links identify the sources used in the audit.

## Evidence and current limits

The audited live-code baseline is `7b994b7`. Original Python/Lua syntax and
data-schema checks succeeded; the legacy runtime was not played or benchmarked.
The audit found reproducible channel/rule/native-call defects and missing
VillageStudio dependencies. Its raw generated outputs are deliberately ignored;
the reproducible runner and written findings are versioned.

No real match was run during this organization work. After every future actual
match, preserve and commit/push the evidence required by the existing root rules.

The upstream backlog inventory references one console log absent from the source
checkout: `data/research/samurai_20261019_211644_sp2_konsole.txt` (B-105). The
backlog view continues to flag it as missing; obtain the original evidence
before reproducing or evaluating that run.
The B-116 desktop shortcut is also specific to the original machine and absent
here. Its external path remains in the backlog rather than being fabricated.
