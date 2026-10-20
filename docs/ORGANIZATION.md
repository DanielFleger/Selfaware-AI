# Current implementation and repository layout

All 184 Python files formerly in `werkzeug/` are now installed modules under
`src/selfaware/`, sorted by responsibility. The existing implementation is the
current bot; the typed runtime is the foundation for migrating its interfaces.
The same policy classes and live loop remain active. No match-strength or
connector fix is implied by moving a file.

## Where to work

| Location | Current contents and responsibility |
| --- | --- |
| `src/selfaware/runtime/live/` | `erstes_spiel` live entry point, `samurai_wache`, partner coordination, stillstand/zielwaechter watchdogs |
| `src/selfaware/game/ucp/` | Existing `befehl` transport, `laden`, `bauen`, `speichern`, `steuerkarte`, `aufbau` native queries/actions |
| `src/selfaware/macro/` | `wirtschaft`, `ertragsplaner`, `haushalt`, opening and production planning, food models, farm packing, storage placement |
| `src/selfaware/micro/tasks/` | Current `assassinen`, `waechter`, `lordwache`, `feldzug`, `raids`, `fallenwache` policies |
| `src/selfaware/micro/zuweisung.py` | Measured combat assignment and group sizing |
| `src/selfaware/strategy/` | `endspurt` policy and `bilanz` endgame calculations |
| `src/selfaware/services/` | World overview, combat/threat/visibility models, path and danger queries |
| `src/selfaware/execution/` | Existing `auftragsbuch`/`lordschutz`, alongside the new typed action ledger |
| `src/selfaware/learning/` | Existing `kausal`, `lernen`, post-match `partie_lernen` and paired 1v1 training |
| `src/selfaware/telemetry/` | `lageprotokoll`, `partie_vergleich`, `ablaufanalyse`, `gold_bilanz`, transitive code fingerprint |
| `src/selfaware/tools/{setup,analysis,checks,experiments,planning}/` | Existing command-line utilities; live probes and measurement setups are separate from analysis |
| `src/selfaware/{domain,coordination,runtime,game}/` | Immutable contracts, deterministic allocator, engine lifecycle/loop, replay adapter |
| `crates/samurai-kern/` | Existing B-115 Rust DLL, C ABI exports and explicit 32-bit Windows build |
| `tools/windows/` | PowerShell window/process helpers |
| `tools/research/` | AIV decoder client and Ghidra extraction script |
| `bridge/snapshots/` | Three original dated Lua snapshots; the complete external module is still missing |
| `assets/ai/SamurAI/` | Current AI metadata, portraits, dialogue and AIV assets |
| `data/research/` | Original observations, model inputs, map plans, console logs and measurements |
| `research/native/` | Existing C decompilation outputs and Java research captures |
| `docs/backlog/` | Authoritative live task JSON and generated HTML; Python commands in `selfaware.tools.planning.backlog` |
| `docs/research/`, `docs/plans/`, `docs/history/` | Preserved knowledge, proposals and historical handoff; see their indexes |
| `tests/` | Offline framework, relocation, import, launch and selected current-policy regression checks |

## Commands

From a checkout, install dependencies with `uv sync --locked --extra dev`.
The base framework uses only the standard library. Existing tools that need
Pillow, NumPy or YAML require `--extra legacy`; Lua audit probes need `--extra audit`.

List every old short name and its new module without importing the live bot:

```sh
uv run selfaware modules
uv run selfaware run backlog fokus
```

Execute an existing utility, preserving its original arguments and exit code:

```sh
uv run selfaware run partner_pruefen
uv run selfaware run bierkette_pruefen
uv run python -m selfaware.tools.analysis.stein_auswerten data/research/lage_....jsonl.gz
```

The current live entry point, once its documented game/module dependencies
are configured, is:

```sh
uv run selfaware run erstes_spiel tempo=40
# Equivalent package command, also used in recorded START-BEFEHL lines:
uv run python -m selfaware.runtime.live.erstes_spiel tempo=40
```

This is the existing live runner. The new `selfaware.runtime.BotRuntime`
currently runs replay observations. Integrating these policies with `Engine`
and a reliable live `GamePort` is the next implementation step in [BACKLOG.md](BACKLOG.md).

The `checks` directory is a source category, not a blanket guarantee that
executing every script is offline. Some import live helpers or require external
metadata. CI runs an explicit set of pure checks. `audit/run_checks.py` uses a
disconnected sender and guarded temporary writes for its separate legacy audit.

## Paths and process state

`selfaware.workspace` centralizes data, asset, external-project and state paths.
Checkout discovery is independent of the current directory. An installed wheel
can use these research tools with `SELFAWARE_WORKSPACE` pointing to a checkout.
The wheel and source distribution exclude the historical data corpus;
offline framework commands do not need it.

- `SELFAWARE_WORKSPACE`: checkout containing `data/research/` and assets.
- `SELFAWARE_VILLAGE_STUDIO_PATH`: actual external project/catalogue/helper root;
  defaults to the sibling `VillageStudio/` used before relocation. Python,
  PowerShell and the AIV JavaScript client use this setting.
- `SELFAWARE_STATE_DIR`: process state directory; defaults to `var/legacy/`.
  IDs, channel locks, partner barriers and stop files share this directory.
- `SHC_INSTANZ`, `SHC_SPIELER`, `SHC_PARTNER`: unchanged live instance/player
  settings. The original sender's Steam path default is preserved; diagnostic
  TOML/game-path settings do not silently change that sender.

Before switching a machine with running old scripts, stop those processes.
Move any local `werkzeug/.letzte_id*` counters to `var/legacy/` with their names
intact. Move a deliberately maintained `STOP` or `STOP_SAMURAI` flag there too. Training flags `daten/STOP_LERNEN` and
`daten/PAUSE_LERNEN` also move to the state directory (`var/legacy/` by default).
Discard stale locks/barriers only after their owners have stopped. All writers
for one game must use the same state directory; do not mix old-path runners
with relocated runners. No local counters or stop flags existed in this checkout.

Recorded matches, seeds and learned models stay under versioned `data/research/`.
Transient locks/counters stay out of source control. After a real match, follow
the evidence and commit/push rule in [README.md](../README.md).

## Preservation and cleanup

[relocations.json](relocations.json) records all 1,343 moves from upstream `a1f41a2`,
with each original SHA256 and whether its content needed path/import changes.
Research evidence, AI assets and Lua snapshots are verified byte for byte by
the relocation tests. Historical filenames and match identifiers remain intact.
The old flat directories and root research-document copies are retired; there
are no duplicate script trees or flat-import compatibility aliases.

Archived documents keep the paths/commands written at the time. Use the
manifest to translate them; this file, [HANDOFF.md](HANDOFF.md) and
[ARCHITECTURE.md](ARCHITECTURE.md) describe the current layout.

Relocated sources retain their original formatting and are explicitly listed
in Ruff's exclusions. New files in the same packages are checked normally.
This keeps style cleanup separate from relocation while the existing audit
and selected policy checks establish behavior compatibility. The code
fingerprint now walks qualified package imports and records relative paths,
so a change in a relocated policy still changes the match's code identity.

Latest upstream task B-102 tracks this organization. Existing B-94/B-95 and
Sharky implementation points retain their gameplay status. Upstream B-96 now selects Rust for the native core; B-115 is built upstream; its DLL, Lua loader and recorded native checks are preserved.
Build instructions are in [the crate README](../crates/samurai-kern/README.md). The
Python package remains the offline contract harness and current policy baseline,
not a decision to replace that approved native-core direction.
