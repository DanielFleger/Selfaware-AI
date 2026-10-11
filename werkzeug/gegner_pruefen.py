# -*- coding: utf-8 -*-
"""Gegner-Probe (Daniel 11.10. 14:41 "mach weiter mit dem Nomade"): ein Liga-Gefecht mit Gegner-KI-Art ki starten und
nach ein paar hundert Ticks Lords und Einheitentypen je Spieler zaehlen. Kein Lenker, keine leere KI.
ki = aiType + 1 (logik.lua eigenesGefecht): 1 = Ratte (Rotkaeppchen), 7 = Sultan (Instanz 4: (no)made).
Aufruf: SHC_INSTANZ=4 python gegner_pruefen.py ki=7 [ticks=400]"""
import sys
import time
from collections import Counter

import befehl as kanal


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    ki, dauer = int(arg.get("ki", 1)), int(arg.get("ticks", 400))
    import erstes_spiel as E
    from laden import peek, TICK
    from serie import zuruecksetzen
    print("Zuruecksetzen:", zuruecksetzen(), flush=True)
    E.befehl({"tempo": 100}, 1.0, bis="TEMPO")
    saat = E.saat_laden()
    zeilen = kanal.sende(dict(E.LIGA_GEFECHT, ki=ki, **({"saat": saat} if saat else {})), 4, bis="LaunchSkirmishGame zurueck")
    print("Start:", " | ".join(z for z in zeilen if "GEFECHT" in z or "Launch" in z)[:400], flush=True)
    E.befehl({"pause": False}, 0.5)
    t0, ende = time.time(), None
    while time.time() - t0 < 120:
        t = peek(TICK)[0]
        if t >= dauer:
            break
        time.sleep(0.3)
    st, L, G = E.runde_lesen()
    print("Tick", st.get("t"), flush=True)
    for sp in (1, 2):
        lords = [(e["x"], e["y"], e["leben"]) for e in L.values() if e["besitzer"] == sp and e["typ"] == 55]
        print("Spieler %d: Lord %s, Einheiten %s" % (sp, lords or "KEINER",
              sorted(Counter(e["typ"] for e in L.values() if e["besitzer"] == sp).items())), flush=True)
    E.befehl({"pause": True}, 0.5)


if __name__ == "__main__":
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
