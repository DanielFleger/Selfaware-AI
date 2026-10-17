# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel: Assassinen nehmen den sicheren Weg (assassinen.py Abschnitt 6 + schussfeld.py, 12.10., Daniel 01:03/
01:08). Vorher festgelegt, was gelten muss:
  1. Assassine bei (60,200), feindliches Gebaeude bei (300,200), drei Bogenschuetzen bei x=180 auf der Geraden: der erste
     Befehl ist ein LAUFBEFEHL (kein Gebaeude-Angriff), die Route hat Wegpunkte, an keinem wird er beschossen.
     17.10. bewusst geaendert: vorher "keiner in Schussweite (Schach 40)"; seit sicht.py darf die Route in Reichweite liegen,
     solange ihn dort kein waehlbarer Feind sieht (L75) - beschossen = sicht.Lage.beschuss > 0.
  2. Laeuft er Wegpunkt fuer Wegpunkt: in keiner Runde gilt er als "laeuft nicht zu seinem Ziel" (Abschnitt 3), und nach dem
     letzten Wegpunkt kommt der Gebaeude-Angriff.
  3. Ohne Schuetzen: sofort der Gebaeude-Angriff (keine Route).
  4. Ohne Gelaende (mit_wegen bleibt an, gelaende None): sofort der Gebaeude-Angriff (altes Verhalten).
Gegenprobe: mit mit_wegen=False muss Fall 1 rot werden.
Aufruf: python werkzeug/wege_pruefen.py [aus]"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
AUS = len(sys.argv) > 1 and sys.argv[1] == "aus"
sys.argv = sys.argv[:1]             # ausweichen_pruefen liest argv[1] als Dateipfad
import assassinen as A
import schussfeld as S
import sicht
from ausweichen_pruefen import einheit

ORTE = [(40, 200)]


def neu(gelaende=True, aus=False):
    t = A.Einzeln(1, pruefe_begehbar=lambda pkt: set(pkt), wegtest=lambda n, p: [True] * len(p))
    t.gelaende = ["G" * 400 for _ in range(400)] if gelaende else None
    t.mit_wegen = not aus
    t.aufnehmen([100])
    return t


def befehle_fuer(bef, n):
    return [b for b in bef if n in b.get("angriff", {}).get("einheiten", [])]


def main():
    aus = AUS
    ok = []
    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))
    G = {900: {"besitzer": 2, "typ": 32, "x": 300, "y": 200, "leben": 100, "uid": 1, "erreichbar": 1}}
    schuetzen = {601 + i: einheit(22, 2, 180, 190 + 10 * i, leben=5000) for i in range(3)}
    L = {100: einheit(73, 1, 60, 200)}
    L.update(schuetzen)
    t = neu(aus=aus)
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    b = befehle_fuer(bef, 100)
    lauf = [x["angriff"]["lauf"] for x in b if "lauf" in x["angriff"]]
    lage = sicht.Lage(L, G, 1)
    punkte = t.route.get(100, {}).get("punkte", [])
    pruefe(1, "erster Befehl %s, Route %d Wegpunkte, beschossen an %s" % (
        b, len(punkte), [p for p in punkte if lage.beschuss(p)]),
        lauf and not any("gebaeude" in x["angriff"] for x in b) and punkte and not any(lage.beschuss(p) for p in punkte))
    # 2. Wegpunkt fuer Wegpunkt laufen
    abweich, angriff_am_ende, runden = 0, False, 0
    while t.route.get(100) and runden < 40:
        runden += 1
        p = t.route[100]["punkte"][0]
        L[100].update(x=p[0], y=p[1], laufx=p[0], laufy=p[1])
        erg, bef = t.schritt(L, G, sichere_orte=ORTE)
        abweich += sum(1 for z in erg if "liefen nicht zu ihrem Ziel" in z)
        if any("gebaeude" in x["angriff"] for x in befehle_fuer(bef, 100)):
            angriff_am_ende = True
    pruefe(2, "%d Runden auf der Route, Abweichler-Meldungen %d, Gebaeude-Angriff nach dem letzten Wegpunkt %s" % (
        runden, abweich, angriff_am_ende), (aus or runden > 0) and abweich == 0 and angriff_am_ende)
    t3 = neu(aus=aus)
    erg, bef = t3.schritt({100: einheit(73, 1, 60, 200)}, G, sichere_orte=ORTE)
    pruefe(3, "ohne Schuetzen: %s" % befehle_fuer(bef, 100),
           any("gebaeude" in x["angriff"] for x in befehle_fuer(bef, 100)) and 100 not in t3.route)
    t4 = neu(gelaende=False, aus=aus)
    L4 = {100: einheit(73, 1, 60, 200)}
    L4.update(schuetzen)
    erg, bef = t4.schritt(L4, G, sichere_orte=ORTE)
    pruefe(4, "ohne Gelaende: %s" % befehle_fuer(bef, 100), any("gebaeude" in x["angriff"] for x in befehle_fuer(bef, 100)))
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
