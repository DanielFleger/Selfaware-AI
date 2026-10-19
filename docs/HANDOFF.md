# GamerGrill / next-agent handoff

## Start here

This repository contains two clearly separated working areas:

- `src/selfaware/`: the new, installable offline framework and its tests.
- `werkzeug/` + `daten/` + root research documents: the existing live bot,
  measurement tools and evidence. Their behavior and paths remain unchanged.

The framework does not yet drive the real game. A green CI run proves the
offline contracts and legacy Python syntax; it does not prove live matches or
fix the original connector. Read [BACKLOG.md](BACKLOG.md) before live work.

This organization work starts from upstream `58a0d50`, which already includes
the opening optimization (`813a98b`) and the separate
[Audit_Sharky.html](../Audit_Sharky.html). Those upstream changes are preserved.
The earlier source audit in `audit/` remains pinned to its `7b994b7` baseline.

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
uv run selfaware replay daten/lage_20261018_162313_i1.jsonl.gz --player 1 --limit 3
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
   `werkzeug/instanz.py`. They are not contained in this repository. Capture
   their authoritative source/revision and hashes; do not fabricate replacements.
2. Copy `configs/local.example.toml` to `configs/local.toml` and fill actual
   paths and installed module SHA256. Run:

   ```sh
   uv run selfaware doctor --config configs/local.toml
   ```

   Exit code 2 means live setup remains blocked/unverified. The doctor only
   reads files and reports hashes; even matching files are not native API tests.
3. Read `bridge/README.md`, `audit/AUDIT.txt`, `README.md`'s match-record rule,
   and the map/opponent/environment entries in `Wissensregister.md`.
4. Legacy scripts still use the original Steam/sibling paths and `SHC_*`
   variables. New `SELFAWARE_*` settings configure diagnostics only. Explicitly
   check those old assumptions before invoking any live tool.
5. Resolve the connector blockers with isolated failure tests, then validate
   one controlled native operation at a time using the actual module.

## First implementation task

Pick `LIVE-01` from the backlog: implement and validate a single-owner UCP
GamePort with typed request/results and observation-based effect confirmation.
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
