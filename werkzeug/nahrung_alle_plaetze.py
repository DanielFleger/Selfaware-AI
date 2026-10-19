# -*- coding: utf-8 -*-
"""Trockentest: Eroeffnung ohne Nahrung (A=0) + Nahrungswahl fuer JEDEN vermessenen Startplatz (daten/start_*.json).
Daniel 19.10. 21:08: "die Selfaware soll es berechnen, egal welche Map, egal welche Position"; 21:11: "bei jedem Test eine
andere Position, bis alle durch sind, dann eine andere Map". Dieser Lauf faengt vorher ab, was ohne Spiel zu sehen ist:
Abbrueche (fehlende Platzkarte, kein Feind eingetragen, kein Holzfaeller-Platz) und Plaetze ohne gedeckte Nahrung.
Spielt nichts, schreibt nichts. Aufruf: python werkzeug/nahrung_alle_plaetze.py [kurz ...]"""
import glob
import json
import os
import sys
import time
import traceback

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
D = os.path.join(HIER, "..", "daten")


def alle():
    return sorted(os.path.basename(p)[6:-5] for p in glob.glob(os.path.join(D, "start_*.json")) if "_platz_" not in p)


def main():
    import eroeffnung
    import nahrungswahl
    namen = sys.argv[1:] or alle()
    rot = 0
    for kurz in namen:
        t = time.time()
        try:
            p = eroeffnung.plane(K=14, A=0, start=kurz)
            if "fehler" in p:
                raise RuntimeError("Eroeffnung: %s" % p["fehler"])
            w = nahrungswahl.waehle(kurz, p, bev_ziel=90, ration="doppelt", horizont=900000)
            g = w["begruendung"]
            print("OK   %-30s %s | Speicher %s (%d zum Bergfried) | Plaetze %d, Herden %d | %.0f s" % (
                kurz, g["entscheidung"], w["kornspeicher"], g["kornspeicher_zum_bergfried"], g["plaetze_eigene_seite"],
                len(g["herden"]), time.time() - t), flush=True)
        except Exception as ex:
            rot += 1
            print("ROT  %-30s %s: %s | %s" % (kurz, type(ex).__name__, ex,
                                              traceback.format_exc().strip().splitlines()[-3].strip()), flush=True)
    print("%d von %d ohne Abbruch" % (len(namen) - rot, len(namen)))
    return 1 if rot else 0


if __name__ == "__main__":
    sys.exit(main())
