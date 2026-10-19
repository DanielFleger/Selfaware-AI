# Selfaware-AI

Research toward Stronghold Crusader AIs that adapt on their own - reacting to the
live game state instead of following a fixed build plan.

The repository now has an installable offline framework in `src/selfaware/`
alongside the existing bot and research tools in `werkzeug/`. Start with the
[agent handoff](docs/HANDOFF.md), [architecture](docs/ARCHITECTURE.md), and
[implementation backlog](docs/BACKLOG.md).

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

The new runtime currently operates on recorded observations. The existing live
bot still runs through its original scripts and environment. Missing external
VillageStudio files and known connector defects are documented in the backlog;
a green offline check does not establish live-game readiness.

This repository collects the reverse-engineering handbook behind that goal:
memory addresses, data structures and measured in-game behaviour for
Stronghold Crusader / Crusader Extreme under UCP3.

## Contents
- Wissensstand.md - the handbook: what is known about the AI build lists, units,
  tiles and walls, and the runtime. Every fact carries a confidence mark
  (proven / measured / read-from-code / assumed).

## Status
Early research. Assumptions are labelled and must not be relied on.

## Pflicht nach jeder Partie: alles ins Repo (Daniel 17.10.2026)

Jeder Rechner (Laptop, Desktop-PC, jede Sitzung) committet und pusht nach jeder
echten Partie, spaetestens vor dem Eintrag im `Wissensregister.md`:

1. **Die Mitschrift** `daten/<name>_konsole.txt`. Ihre ersten Zeilen sind
   `CODE-KENNUNG ...` und `START-BEFEHL Instanz N: python erstes_spiel.py ...`
   (schreibt `erstes_spiel.py` selbst). Wer nicht ueber `erstes_spiel.py`
   startet, schreibt den vollstaendigen Aufruf von Hand als erste Zeile.
2. **Alles, was die Partie neu angelegt hat und zum Nachspielen noetig ist:**
   `daten/start_<karte>*.json`/`.txt`, `daten/eroeffnung_plan_<karte>.json`,
   `daten/baeume_*`, `daten/rohstoffe_*`, Saat-Dateien.
3. **Das Lageprotokoll** `daten/lage_<stempel>_i<n>.jsonl.gz`, wenn es kleiner
   als 50 MB ist; sonst im Register vermerken, auf welchem Rechner es liegt.
4. **Die Umgebung, wenn sie anders ist als zuletzt notiert:** Karte, Gegner-KI
   und deren Plugin-Fassung, Instanz, geaenderte `ucp-config.yml`-Stellen und
   die Pruefsumme der `ucp/villagestudio/logik.lua`. Aendert sich die
   `logik.lua`, kommt die neue Fassung als Kopie nach `werkzeug/`.

Die Registerzeile einer Partie nennt den Dateinamen ihrer Mitschrift.
Ohne diese Dateien kann kein anderer Rechner einen Lauf nachspielen oder
auswerten (17.10.: der Laptop musste Karte und Schalter von 1017a-g raten).
