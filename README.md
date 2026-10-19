# Selfaware-AI

Research toward Stronghold Crusader AIs that adapt on their own - reacting to the
live game state instead of following a fixed build plan.

The current bot and offline framework are organized together in `src/selfaware/`,
with separate packages for game access, live orchestration, macro, micro,
strategy, learning and telemetry. Start with the [repository map](docs/ORGANIZATION.md),
[agent handoff](docs/HANDOFF.md), [architecture](docs/ARCHITECTURE.md), and
[engineering acceptance details](docs/BACKLOG.md). Task status is maintained in
[the authoritative backlog](docs/backlog/backlog.json).

## Development quick start

With uv 0.12.9 installed, run from a fresh checkout:

```sh
uv sync --locked --extra dev
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run selfaware doctor --offline
uv run selfaware replay tests/fixtures/legacy_sample.jsonl
```

The package supports Python 3.11+; CI covers Windows/Linux with Python 3.11 and
3.14. Offline checks require no game installation. `uv build` builds the package.
Use `--extra legacy` for the old tools' Python libraries and `--extra audit` for
Lua audit probes. Dependency resolution is recorded in `uv.lock`.

The new `BotRuntime` currently operates on recorded observations. The current
live bot is `selfaware.runtime.live.erstes_spiel`; its policies and external
game requirements are preserved. Launch existing modules with `uv run selfaware
run <name> [arguments]`, or `uv run python -m <module>`. `uv run selfaware modules`
lists all 179 relocated module names. Missing external
VillageStudio files and known connector defects are documented in the backlog;
a green offline check does not establish live-game readiness.

This repository collects the reverse-engineering handbook behind that goal:
memory addresses, data structures and measured in-game behaviour for
Stronghold Crusader / Crusader Extreme under UCP3.

## Contents
- [Wissensstand.md](docs/research/Wissensstand.md) - the handbook: what is known about the AI build lists, units,
  tiles and walls, and the runtime. Every fact carries a confidence mark
  (proven / measured / read-from-code / assumed).

## Status
Early research. Assumptions are labelled and must not be relied on.

## Pflicht nach jeder Partie: alles ins Repo (Daniel 17.10.2026)

Jeder Rechner (Laptop, Desktop-PC, jede Sitzung) committet und pusht nach jeder
echten Partie, spaetestens vor dem Eintrag im `docs/research/Wissensregister.md`:

1. **Die Mitschrift** `data/research/<name>_konsole.txt`. Ihre ersten Zeilen sind
   `CODE-KENNUNG ...` und `START-BEFEHL Instanz N: uv run python -m selfaware.runtime.live.erstes_spiel ...`
   (schreibt `erstes_spiel.py` selbst). Wer nicht ueber `erstes_spiel.py`
   startet, schreibt den vollstaendigen Aufruf von Hand als erste Zeile.
2. **Alles, was die Partie neu angelegt hat und zum Nachspielen noetig ist:**
   `data/research/start_<karte>*.json`/`.txt`, `data/research/eroeffnung_plan_<karte>.json`,
   `data/research/baeume_*`, `data/research/rohstoffe_*`, Saat-Dateien.
3. **Das Lageprotokoll** `data/research/lage_<stempel>_i<n>.jsonl.gz`, wenn es kleiner
   als 50 MB ist; sonst im Register vermerken, auf welchem Rechner es liegt.
4. **Die Umgebung, wenn sie anders ist als zuletzt notiert:** Karte, Gegner-KI
   und deren Plugin-Fassung, Instanz, geaenderte `ucp-config.yml`-Stellen und
   die Pruefsumme der `ucp/villagestudio/logik.lua`. Aendert sich die
   `logik.lua`, kommt die neue Fassung als Kopie nach `bridge/snapshots/`.

Die Registerzeile einer Partie nennt den Dateinamen ihrer Mitschrift.
Ohne diese Dateien kann kein anderer Rechner einen Lauf nachspielen oder
auswerten (17.10.: der Laptop musste Karte und Schalter von 1017a-g raten).
