# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer lordwache.py (19.10.). Vorher festgelegt (unser Lord, Spieler 1, 150.000 Leben bei (100, 100)):
  1. keine Feinde -> keine Gefahr
  2. 4 feindliche Sklaven (6.000 Leben) 10 Felder vor dem Lord -> KEINE Gefahr (Daniel 17:51: "keine Verteidigung, wenn
     der Gegner nur 4 Einheiten hat und dein Lord full live ist"). KORREKTUR 17:55: zuerst mit 4 arab. Schwertkaempfern
     erwartet - die Rechnung (Editor-Duelle) laesst sie den vollen Lord in ~370 Takten toeten; das ist jetzt Fall 5
  5. 4 feindliche arab. Schwertkaempfer (28.000 Leben) -> Gefahr (gemessenes Modell: ~180 Schaden je Takt und Einheit)
  3. 40 feindliche arab. Schwertkaempfer -> Gefahr, die Feinde nach Abstand sortiert
  4. 40 feindliche, aber 70 Felder weg -> keine Gefahr (ausserhalb ANMARSCH_R)
  NEU 19.10. 18:20 (1018o: Lordwache 195-mal, schon bei 2 Assassinen; Lord jetzt aus Partien gemessen, lord_messen.py):
  6. 2 feindliche Assassinen 10 Felder vor dem vollen Lord -> KEINE Gefahr (Lord 150 je Takt an ihnen, sie 100 an ihm)
  7. 40 arab. Schwertkaempfer 45 Felder weg, Laufziel weit weg (Raid woanders) -> keine Gefahr (nicht im Anmarsch)
  8. dieselben 40 mit Laufziel am Lord -> Gefahr
  9. Abwehr gegen 8 Assassinen am Lord (Gefahr): 10 Heimwache (Vorrang) bei ihm, 30 vom Feldzug 30 Felder weg -> gewaehlt
     wird eine kleine Gruppe NUR aus der Heimwache, und sie reicht (nicht das ganze Heer)
Gegenprobe: mit "alt" gilt jeder Feind im Anmarsch als Gefahr -> Fall 2 und 6 rot. Zweite Gegenprobe: ohne
data/research/lord_kampfwerte.json (Lord wieder Ersatzwert 20) -> Fall 6 rot.
Aufruf: uv run python -m selfaware.tools.checks.lordwache_pruefen [alt]"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.micro.tasks.lordwache as LW

if len(sys.argv) > 1 and sys.argv[1] == "alt":
    _alt = LW.bedrohung

    def _jeder(L, sp):
        g, t, f, ln = _alt(L, sp)
        return bool(f), t, f, ln
    LW.bedrohung = _jeder


def e(typ, sp, x, y, leben):
    return {"typ": typ, "besitzer": sp, "x": x, "y": y, "leben": leben, "zustand": 1}


def lage(n_feinde, abstand, typ=75, leben=28000, lauf=None):
    L = {1: e(55, 1, 100, 100, 150000)}
    for i in range(n_feinde):
        L[100 + i] = e(typ, 2, 100 + abstand + i % 5, 100 + i // 5, leben)
        if lauf:
            L[100 + i]["laufx"], L[100 + i]["laufy"] = lauf
    return L


def main():
    ok = []

    def pruefe(nr, text, bed):
        ok.append(bool(bed))
        print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text), flush=True)

    g1 = LW.bedrohung(lage(0, 10), 1)
    pruefe(1, "keine Feinde: %s" % (g1[:2],), not g1[0])
    g2 = LW.bedrohung(lage(4, 10, typ=71, leben=6000), 1)
    pruefe(2, "4 Sklaven: %s" % (g2[:2],), not g2[0])
    g5 = LW.bedrohung(lage(4, 10), 1)
    pruefe(5, "4 arab. Schwertkaempfer: %s" % (g5[:2],), g5[0])
    g3 = LW.bedrohung(lage(40, 10), 1)
    pruefe(3, "40 Schwertkaempfer: %s, erster Feind %s" % (g3[:2], g3[2][:1]), g3[0] and g3[2][0] == 100)
    g4 = LW.bedrohung(lage(40, 70), 1)
    pruefe(4, "40 in 70 Feldern: %s" % (g4[:2],), not g4[0])
    g6 = LW.bedrohung(lage(2, 10, typ=73, leben=12500), 1)
    pruefe(6, "2 Assassinen: %s" % (g6[:2],), not g6[0])
    g7 = LW.bedrohung(lage(40, 45, lauf=(250, 250)), 1)
    pruefe(7, "40 in 45 Feldern, Ziel woanders: %s" % (g7[:2],), not g7[0])
    g8 = LW.bedrohung(lage(40, 45, lauf=(102, 100)), 1)
    pruefe(8, "40 in 45 Feldern, Ziel am Lord: %s" % (g8[:2],), g8[0])
    L9 = lage(8, 3, typ=73, leben=12500)
    for i in range(10):
        L9[300 + i] = e(75, 1, 95 + i % 3, 96 + i // 3, 28000)
    for i in range(30):
        L9[400 + i] = e(75, 1, 130 + i % 5, 100 + i // 5, 28000)
    g9 = LW.bedrohung(L9, 1)
    hw = list(range(300, 310))
    w9 = LW.abwehr(L9, 1, g9[2], hw + list(range(400, 430)), vorrang=hw) if g9[0] else ([], False, "keine Gefahr erkannt")
    pruefe(9, "Abwehr 8 Assassinen: Gefahr %s, gewaehlt %s - %s" % (g9[0], w9[0], w9[2]),
           g9[0] and w9[1] and 0 < len(w9[0]) < 10 and set(w9[0]) <= set(hw))
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
