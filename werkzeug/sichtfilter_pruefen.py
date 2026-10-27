# -*- coding: utf-8 -*-
"""B-274 Sichtfilter ohne Spiel pruefen (FAIRNESS.md): Soll je Fall vorher festgelegt.
Feindliche Einheiten: Laufziel nur aus beobachteter Bewegung, Angriffsziel nur, wenn sichtbar angegriffen wird und das Ziel
Leben verliert. Eigene/verbuendete bleiben roh. Gegenprobe: ohne Filter (SICHT_SPIELER None) muessen die Faelle rot sein.
Aufruf: python sichtfilter_pruefen.py"""
import os
import sys
import tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import waechter as W
import parteien

KOPF = ("nr besitzer typ x y leben zustand zielart zieleinheit zieluid zielgebaeude ziel zielx ziely laufx laufy auswahlvon "
        "auswahlmarke gruppe gruppenuid ladung arbeitsplatz erreichbar nahziel nahangreifer")


def zeile(nr, sp, typ, x, y, leben, zustand=0, zielart=0, ziel=0, lauf=None, nahziel=-1):
    lx, ly = lauf or (x, y)
    return " ".join(str(v) for v in (nr, sp, typ, x, y, leben, zustand, zielart, ziel, 0, 0, 0, 0, 0, lx, ly, 0, 0, 0, 0, 0, 0,
                                     1, nahziel, 0))


def lage(t, zeilen):
    p = os.path.join(tempfile.gettempdir(), "sichtfilter_lagebild.txt")
    open(p, "w").write("tick %d\n%s\n%s\n" % (t, KOPF, "\n".join(zeilen)))
    W.LAGEBILD = p
    return W.lies_lagebild(neu_holen=False)


def faelle(mit_filter):
    W.SICHT_SPIELER = 1 if mit_filter else None
    W._SICHT.update({"t": None, "jetzt": {}, "vorher": {}})
    parteien.freunde_von = W.freunde_von = lambda sp: {sp, 3}       # Spieler 1 mit Verbuendetem 3; 2 ist Feind
    # Runde 1: Feindbogen 10 bei (100,100), will heimlich nach (150,150); eigener Speer 20 bei (120,100), Leben 1000
    lage(1000, [zeile(10, 2, 22, 100, 100, 3500, zustand=101, lauf=(150, 150)),
                zeile(20, 1, 24, 120, 100, 1000), zeile(30, 3, 24, 50, 50, 1000, zustand=101, lauf=(60, 70))])
    # Runde 2: Bogen ist 2 Felder nach Osten gelaufen, zielt (5) auf 20 - 20 hat noch KEIN Leben verloren
    L2 = lage(1100, [zeile(10, 2, 22, 102, 100, 3500, zustand=5, zielart=4, ziel=20, lauf=(150, 150)),
                     zeile(20, 1, 24, 120, 100, 1000), zeile(30, 3, 24, 52, 51, 1000, zustand=101, lauf=(60, 70))])
    # Runde 3: Bogen schiesst (4), 20 verliert Leben -> der Angriff ist sichtbar
    L3 = lage(1200, [zeile(10, 2, 22, 102, 100, 3500, zustand=4, zielart=4, ziel=20, lauf=(150, 150)),
                     zeile(20, 1, 24, 120, 100, 900), zeile(30, 3, 24, 52, 51, 1000)])
    e2, e3 = L2[10], L3[10]
    return [
        ("Laufziel Feind = Vorhersage nach Osten (117,100), nicht das heimliche (150,150)", (e2["laufx"], e2["laufy"]) == (117, 100)),
        ("Angriffsziel Feind versteckt, solange das Ziel kein Leben verliert", e2["zieleinheit"] == 0 and e2["zielart"] == 0),
        ("Angriffsziel Feind sichtbar, wenn er schiesst und das Ziel Leben verliert", e3["zieleinheit"] == 20),
        ("stehender Feind: Laufziel = eigenes Feld", (e3["laufx"], e3["laufy"]) == (102, 100)),
        ("Verbuendeter bleibt roh (Laufziel (60,70))", (L2[30]["laufx"], L2[30]["laufy"]) == (60, 70)),
    ]


if __name__ == "__main__":
    erg = faelle(True)
    for name, ok in erg:
        print("%s %s" % ("OK  " if ok else "ROT ", name))
    gegen = faelle(False)
    rot_ohne = sum(1 for n, ok in gegen if not ok)
    print("Gegenprobe ohne Filter: %d von %d Faellen rot (erwartet 3: Laufziel, versteckt, stehend)" % (rot_ohne, len(gegen)))
    gut = all(ok for _, ok in erg) and rot_ohne == 3
    print("%d von %d gruen, Gegenprobe %s" % (sum(ok for _, ok in erg), len(erg), "passt" if rot_ohne == 3 else "PASST NICHT"))
    sys.exit(0 if gut else 1)
