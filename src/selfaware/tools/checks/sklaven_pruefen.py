# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel (12.10. 01:37, Daniel: "es macht keinen Sinn, vor den Sklaven wegzurennen"). Vorher festgelegt:
  1. 1 eigene Assassine gegen 3 feindliche Sklaven (2 Felder) -> KEIN Ausweichen (Sklave powerLevel 1, Assassine 20)
  2. 1 gegen 3 feindliche Assassinen -> Ausweichen (wie bisher, ausweichen_pruefen Fall 1)
  3. 1 gegen 2 arabische Schwertkaempfer (powerLevel 16 -> 0,8 je) -> Ausweichen (1,6 > 1)
Gegenprobe: mit der alten Zaehlung (jeder Nahkaempfer 1) muss Fall 1 rot werden.
Aufruf: uv run python -m selfaware.tools.checks.sklaven_pruefen [alt]"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))

ALT = len(sys.argv) > 1 and sys.argv[1] == "alt"
sys.argv = sys.argv[:1]
import selfaware.micro.tasks.assassinen as A
from selfaware.tools.checks.ausweichen_pruefen import einheit, ORTE

if ALT:
    A.Einzeln.NAH_GEFAHR = {}           # alle 1.0 = alte Zaehlung


def lauf(feind_typ, n):
    t = A.Einzeln(1, pruefe_begehbar=lambda pkt: set(pkt), wegtest=lambda nr, p: [True] * len(p))
    t.aufnehmen([100])
    L = {100: einheit(73, 1, 198, 270)}
    for i in range(n):
        L[501 + i] = einheit(feind_typ, 2, 200, 270 + i, leben=6000 if feind_typ == 71 else 12500)
    G = {900: {"besitzer": 2, "typ": 32, "x": 200, "y": 270, "leben": 100, "uid": 1, "erreichbar": 1}}
    t.schritt(L, G, sichere_orte=ORTE)
    return 100 in t.flucht


def main():
    ok = []
    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))
    f = lauf(71, 3)
    pruefe(1, "1 gegen 3 Sklaven: ausweichen %s (soll nein)" % f, not f)
    f = lauf(73, 3)
    pruefe(2, "1 gegen 3 Assassinen: ausweichen %s (soll ja)" % f, f)
    f = lauf(75, 2)
    pruefe(3, "1 gegen 2 arabische Schwertkaempfer: ausweichen %s (soll ja)" % f, f)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
