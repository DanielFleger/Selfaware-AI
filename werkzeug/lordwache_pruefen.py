# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer lordwache.py (19.10.). Vorher festgelegt (unser Lord, Spieler 1, 150.000 Leben bei (100, 100)):
  1. keine Feinde -> keine Gefahr
  2. 4 feindliche Sklaven (6.000 Leben) 10 Felder vor dem Lord -> KEINE Gefahr (Daniel 17:51: "keine Verteidigung, wenn
     der Gegner nur 4 Einheiten hat und dein Lord full live ist"). KORREKTUR 17:55: zuerst mit 4 arab. Schwertkaempfern
     erwartet - die Rechnung (Editor-Duelle) laesst sie den vollen Lord in ~370 Takten toeten; das ist jetzt Fall 5
  5. 4 feindliche arab. Schwertkaempfer (28.000 Leben) -> Gefahr (gemessenes Modell: ~180 Schaden je Takt und Einheit)
  3. 40 feindliche arab. Schwertkaempfer -> Gefahr, die Feinde nach Abstand sortiert
  4. 40 feindliche, aber 70 Felder weg -> keine Gefahr (ausserhalb ANMARSCH_R)
Gegenprobe: mit "alt" gilt jeder Feind im Anmarsch als Gefahr -> Fall 2 rot.
Aufruf: python werkzeug/lordwache_pruefen.py [alt]"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import lordwache as LW

if len(sys.argv) > 1 and sys.argv[1] == "alt":
    _alt = LW.bedrohung

    def _jeder(L, sp):
        g, t, f, ln = _alt(L, sp)
        return bool(f), t, f, ln
    LW.bedrohung = _jeder


def e(typ, sp, x, y, leben):
    return {"typ": typ, "besitzer": sp, "x": x, "y": y, "leben": leben, "zustand": 1}


def lage(n_feinde, abstand, typ=75, leben=28000):
    L = {1: e(55, 1, 100, 100, 150000)}
    for i in range(n_feinde):
        L[100 + i] = e(typ, 2, 100 + abstand + i % 5, 100 + i // 5, leben)
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
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
