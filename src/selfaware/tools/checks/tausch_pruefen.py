# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel: Zielwahl nach RISIKO GEGEN ERTRAG (12.10. 01:54; Daniel 01:49 "frei entscheiden, Risk/Reward abwaegen
statt fixem Umkreis", 01:47 "nur gute Trades"). Gefahr seit 17.10. aus sicht.py (sichtbar + Schusslinie, gemessene Raten). Vorher festgelegt:
  1. Apfelplantage, keine Feinde -> Ziel
  2. dieselbe, 12 Bogenschuetzen 2 Felder daneben (entdeckt, offen) -> KEIN Ziel (Saldo negativ)
  3. dieselbe, 12 Bogenschuetzen 30 Felder weg (in Reichweite 40, aber kein waehlbarer Feind <= 20 Felder = unsichtbar) -> Ziel
     (die alte feste Regel "hoechstens 1 Schuetze in Reichweite" haette es verboten)
Gegenprobe: Beschussraten 0 (sicht.RATE_FREI/RATE_ZU) -> Fall 2 rot.
Aufruf: uv run python -m selfaware.tools.checks.tausch_pruefen [ohne_schaden]"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))

OHNE = len(sys.argv) > 1 and sys.argv[1] == "ohne_schaden"
sys.argv = sys.argv[:1]
import selfaware.micro.tasks.assassinen as A
import selfaware.services.schussfeld as S
from selfaware.tools.checks.ausweichen_pruefen import einheit, ORTE

import selfaware.services.sicht as sicht
if OHNE:
    sicht.RATE, sicht.RATE_FREI, sicht.RATE_ZU = {}, 0.0, 0.0     # 17.10.: auch die gemessene Tabelle (sonst hohl)


def ziel(schuetzen):
    t = A.Einzeln(1, pruefe_begehbar=lambda pkt: set(pkt), wegtest=lambda nr, p: [True] * len(p))
    t.gelaende = ["G" * 400 for _ in range(400)]
    t.aufnehmen([100])
    L = {100: einheit(73, 1, 100, 200)}
    for i, p in enumerate(schuetzen):
        L[601 + i] = einheit(22, 2, p[0], p[1], leben=5000)
    G = {900: {"besitzer": 2, "typ": 32, "x": 200, "y": 200, "leben": 100, "uid": 1, "erreichbar": 1}}
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    return t.ziel.get(100), [z for z in erg if z.startswith("ZIELWAHL")][:1]


def main():
    ok = []
    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))
    z, e = ziel([])
    pruefe(1, "keine Feinde: Ziel %s %s" % (z, e), z == 900)
    z, e = ziel([(202, 195 + i) for i in range(12)])
    pruefe(2, "12 Schuetzen 2 Felder daneben: Ziel %s (soll keins) %s" % (z, e), z != 900)
    z, e = ziel([(230, 190 + i) for i in range(12)])
    pruefe(3, "12 Schuetzen 30 Felder weg: Ziel %s %s" % (z, e), z == 900)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
