# Selfaware-AI

Research toward Stronghold Crusader AIs that adapt on their own - reacting to the
live game state instead of following a fixed build plan.

This repository collects the reverse-engineering handbook behind that goal:
memory addresses, data structures and measured in-game behaviour for
Stronghold Crusader / Crusader Extreme under UCP3.

## Contents
- Wissensstand.md - the handbook: what is known about the AI build lists, units,
  tiles and walls, and the runtime. Every fact carries a confidence mark
  (proven / measured / read-from-code / assumed).

## Status
Early research. Assumptions are labelled and must not be relied on.

Local installation and its current limits are described in
[distribution/README.md](distribution/README.md). The Store proposal was withdrawn
after maintainer feedback on 24 October 2026. The separate local app works with
the legacy development bridge; this is not a Store-compatible release.

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
