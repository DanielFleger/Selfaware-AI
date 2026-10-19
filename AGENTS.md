# Arbeitsregel fuer dieses Repo

Nach jeder echten Partie: Mitschrift (mit START-BEFEHL-Zeile), neu angelegte Karten-/Plan-Dateien,
Lageprotokoll (unter 50 MB) und geaenderte Umgebung committen und pushen.
Einzelheiten: README.md, Abschnitt "Pflicht nach jeder Partie" (Daniel 17.10.2026).

## Development and agent handoff

Read `docs/HANDOFF.md`, `docs/ARCHITECTURE.md` and `docs/BACKLOG.md` before new
implementation, then consult `docs/ORGANIZATION.md`. The current bot is sorted
into `src/selfaware/` by responsibility; `runtime/live/erstes_spiel.py` remains
its live entry point. Research evidence is in `data/research/`, archived
knowledge/plans in `docs/research/` and `docs/plans/`, Lua copies in
`bridge/snapshots/`, and AI assets in `assets/ai/`. `docs/relocations.json` maps
every old path and records original content hashes. Preserve that provenance.

Use `uv sync --locked --extra dev`, `uv run pytest`, `uv run ruff check .`,
and `uv run ruff format --check .`. The `tests/` suite is offline. Some existing
`selfaware.tools` modules start or modify a real game; inspect them before execution.

Policies receive immutable snapshots and return proposals. Keep game I/O and
native addresses in the adapter/execution boundary. Instance/player/game epoch
must be explicit; a receipt or queued command is not an observed effect.

The live GamePort and original connector defects remain implementation work.
Do not claim a live fix from offline tests alone. Record actual native/module
versions, postconditions and match evidence separately from policy improvement.
