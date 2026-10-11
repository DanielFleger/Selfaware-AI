# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel: gute Tauschgeschaefte (12.10. 01:47, Daniel: "nur gute Trades eingehen oder schlauer angreifen").
Vorher festgelegt:
  1. Apfelplantage (WERT unter TEUER) ohne Schuetzen -> wird Ziel
  2. dieselbe mit 2 Bogenschuetzen 30 Felder daneben (in Reichweite 40, aber ausserhalb des alten Umkreises 20) -> KEIN Ziel
  3. Kaserne (teuer) mit denselben 2 Schuetzen -> Ziel (teuer darf 2)
Gegenprobe: SCHUETZEN_MAX = 9 -> Fall 2 rot.
Aufruf: python werkzeug/tausch_pruefen.py [locker]"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
LOCKER = len(sys.argv) > 1 and sys.argv[1] == "locker"
sys.argv = sys.argv[:1]
import assassinen as A
from ausweichen_pruefen import einheit, ORTE

if LOCKER:
    A.Einzeln.SCHUETZEN_MAX = 9


def ziel(typ_geb, schuetzen):
    t = A.Einzeln(1, pruefe_begehbar=lambda pkt: set(pkt), wegtest=lambda nr, p: [True] * len(p))
    t.aufnehmen([100])
    L = {100: einheit(73, 1, 100, 200)}
    for i, p in enumerate(schuetzen):
        L[601 + i] = einheit(22, 2, p[0], p[1], leben=5000)
    G = {900: {"besitzer": 2, "typ": typ_geb, "x": 200, "y": 200, "leben": 100, "uid": 1, "erreichbar": 1}}
    t.schritt(L, G, sichere_orte=ORTE)
    return t.ziel.get(100)


def main():
    ok = []
    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))
    zwei = [(230, 200), (230, 205)]
    z = ziel(32, [])
    pruefe(1, "Apfelplantage ohne Schuetzen: Ziel %s" % z, z == 900)
    z = ziel(32, zwei)
    pruefe(2, "Apfelplantage, 2 Schuetzen 30 Felder daneben: Ziel %s (soll keins)" % z, z != 900)
    z = ziel(9, zwei)
    pruefe(3, "Kaserne (teuer), 2 Schuetzen: Ziel %s" % z, z == 900)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
