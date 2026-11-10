# -*- coding: utf-8 -*-
"""B-182: Gegenprobe fuer s_taeter.py mit der Tabelle "eigen" (10.11. 23:07), ohne Spiel.

Zwei kuenstliche Schnappschuesse: Ein eigener Berittener (A_HARCHER 74) und ein eigener Bogenschuetze (E_ARCHER 22) stehen in
Reichweite eines gegnerischen Arbeiters, der danach verschwindet; ein eigener Schwertkaempfer (A_SWORDSMAN 75) und ein Sklave
(A_SLAVE 71) stehen am gegnerischen Gebaeude, das 100 Leben verliert. Laut Kern schiesst nur der Reiter auf den Arbeiter und nur
der Schwertkaempfer greift das Gebaeude an.
  mit Tabelle   Erwartet: Tod ganz beim Reiter (schuss), Gebaeudeschaden ganz beim Schwertkaempfer (nah_gebaeude_kern).
  ohne Tabelle  Erwartet wie vor dem 10.11.: Tod je halb bei Reiter und Bogenschuetze (schuss_frei), Schaden je halb (nah_gebaeude).
Aufruf: python s_taeter_pruefen.py   (Rueckgabe 1, wenn eine Erwartung nicht eintrifft)
"""
import gzip
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s_taeter as T  # noqa: E402

KOPF_E = "nr besitzer typ x y leben zielart zieleinheit laufx laufy nahziel"
KOPF_G = "nr besitzer typ x y leben uid feuer"
KOPF_K = "nr typ x y zielart zieleinheit zieluid schusseinheit schussziel_uid mauerx mauery planx plany nahziel"


def einheiten(mit_arbeiter):
    z = [
        "1 1 55 0 0 150000 0 0 0 0 0",       # eigener Lord
        "2 2 55 100 100 105000 0 0 100 100 0",  # gegnerischer Lord
        "10 1 74 10 10 15000 0 0 10 10 0",   # Reiter, ohne Befehl - er schiesst von selbst
        "11 1 22 12 10 10000 0 0 12 10 0",   # Bogenschuetze daneben, schiesst nicht
        "20 1 75 41 41 10000 0 0 41 41 0",   # Schwertkaempfer am Gebaeude
        "21 1 71 42 42 2500 0 0 42 42 0",    # Sklave daneben
    ]
    if mit_arbeiter:
        z.append("50 2 3 30 10 2500 0 0 30 10 0")
    return "tick 0\n" + KOPF_E + "\n" + "\n".join(z) + "\n"


def gebaeude(leben):
    return KOPF_G + "\n77 2 1 40 40 %d 900 0\n" % leben


EIGEN = ("kern_tick 0 ich 1\n" + KOPF_K + "\n"
         "1 55 0 0 0 0 0 0 0 0 0 0 0 0\n"
         "10 74 10 10 0 0 0 50 23928 0 0 0 0 0\n"
         "11 22 12 10 0 0 0 0 0 0 0 0 0 0\n"
         "20 75 41 41 0 0 0 0 0 40 41 41 42 0\n"
         "21 71 42 42 0 0 0 0 0 0 0 0 0 0\n")


def protokoll(pfad, mit_tabelle):
    with gzip.open(pfad, "wt", encoding="utf-8") as f:
        for t, arbeiter, leben in ((100, True, 1000), (105, False, 900)):
            z = {"t": t, "st": {"t": t}, "einheiten": einheiten(arbeiter), "gebaeude": gebaeude(leben)}
            if mit_tabelle:
                z["eigen"] = EIGEN
            f.write(json.dumps(z) + "\n")


def main():
    fehler = 0
    with tempfile.TemporaryDirectory() as d:
        for mit, tote_soll, geb_soll in (
            (True, {("schuss", 74, "arbeiter", 3): 1.0}, {("nah_gebaeude_kern", 75): 100.0}),
            (False, {("schuss_frei", 74, "arbeiter", 3): 0.5, ("schuss_frei", 22, "arbeiter", 3): 0.5},
             {("nah_gebaeude", 75): 50.0, ("nah_gebaeude", 71): 50.0}),
        ):
            p = os.path.join(d, "lage_%s.jsonl.gz" % mit)
            protokoll(p, mit)
            r = T.auswerten(p)
            tote, geb = dict(r["tote"]), dict(r["geb_schaden"])
            ok = tote == tote_soll and geb == geb_soll
            fehler += not ok
            print("%s Tabelle: %s | Tote %s | Gebaeude %s" % ("mit " if mit else "ohne", "OK" if ok else "FALSCH", tote, geb))
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
