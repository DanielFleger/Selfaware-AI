# -*- coding: utf-8 -*-
"""B-133 (2v2 gegen die Team-Liga, 20.10.2026): die 6 Liga-Karten einmal live vermessen - wie viele Burgplaetze, wo
liegt welcher Platz. Je Karte ein Gefecht mit 4 Spielern auf festen Plaetzen (Spieler i auf Platz i-1, startliste
0,1,2,3), Tempo 300 bis Tick 150, dann die Bergfriede lesen (karten_holen.bergfriede: Besitzer -> Anker, Eingang).
Schreibt daten/liga_karten.json. Spielt nichts, baut nichts.
Aufruf: SHC_INSTANZ=5 python werkzeug/liga_karten_messen.py"""
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import befehl as kanal
from karten_holen import bergfriede
from laden import peek, TICK
from serie import zuruecksetzen

KARTEN = ["Liga_Battle Brother_s Strife", "Liga_Branching Fortunes", "Liga_Dwarven Dream", "Liga_Green Trench",
          "Liga_Grumpy Neighbors", "Liga_Paradise Plains"]


def main():
    aus = {}
    for karte in KARTEN:
        print("Zuruecksetzen:", zuruecksetzen(), flush=True)
        kanal.sende({"eigenesGefecht": True, "karte": karte, "ki": 1, "gegner": 3, "menschen": 1, "ausgleich": 3,
                     "startliste": [0, 1, 2, 3, 246, 246, 246, 246]}, 4, bis="LaunchSkirmishGame zurueck")
        kanal.sende({"tempo": 300}, 0.5)
        kanal.sende({"player": 1, "pause": False}, 0.5)
        t0 = time.time()
        while time.time() - t0 < 60 and (peek(TICK)[0] or 0) < 150:
            time.sleep(0.5)
        kanal.sende({"player": 1, "pause": True}, 0.5)
        b = bergfriede()
        aus[karte] = {"tick": peek(TICK)[0], "plaetze": {str(sp - 1): {"spieler": sp, "anker": list(v["anker"]),
                                                                       "eingang": list(v["eingang"])} for sp, v in sorted(b.items())}}
        print("%-32s Tick %s, %d Burgen: %s" % (karte, aus[karte]["tick"], len(b),
              {sp - 1: v["eingang"] for sp, v in sorted(b.items())}), flush=True)
    json.dump(aus, open(os.path.join(HIER, "..", "daten", "liga_karten.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("gesichert: daten/liga_karten.json")


if __name__ == "__main__":
    main()
