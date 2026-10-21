# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer gefahr.py (B-157, Daniel 21.10.2026 "maximale Sicherheit, dann minimaler Widerstand").
Vorher festgelegt:
  1. Bogenschuetze (Reichweite 20) mitten auf der geraden Strecke (100,150)->(100,90): sicherer Weg hat Gefahr 0, die Gerade > 0
  2. Todeszone Torhaus Typ 75 bei (100,120): der Weg meidet sie (Gefahr 0)
  3. zwei Schuetzen decken alles bis 30 Felder: es gibt einen Weg, und er ist weniger gefaehrlich als die Gerade
  4. Feuer (100,110 r4) und Schuetze (115,125 r12): der Weg fuehrt durch kein Feuer und hat Gefahr 0
  5. mindestzahl: 10.000 Leben in 100 Takten -> 1; 60.000 -> 5
Aufruf: python werkzeug/gefahr_pruefen.py (Rueckgabe 0 = gruen)"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gefahr as Z

ok = []


def pruefe(nr, text, bed):
    ok.append(bool(bed))
    print("%s %d %s" % ("OK  " if bed else "ROT ", nr, text))


feind = lambda b: b == 2
REICH = {22: 20, 23: 12}
S, Z1 = (100, 150), (100, 90)
L1 = {1: {"besitzer": 2, "typ": 22, "x": 100, "y": 120, "leben": 5000}}
b1 = Z.bedrohungen(L1, {}, feind, REICH)
w1 = Z.sicherer_weg(S, Z1, b1)
pruefe(1, "Schuetze auf der Geraden: Weg %s Gefahr %d | Gerade %d" % (w1, Z.weg_gefahr(S, w1, b1), Z.weg_gefahr(S, [Z1], b1)),
       w1 and w1[-1] == Z1 and Z.weg_gefahr(S, w1, b1) == 0 and Z.weg_gefahr(S, [Z1], b1) > 0)
b2 = Z.bedrohungen({}, {7: {"besitzer": 2, "typ": 75, "x": 100, "y": 120}}, feind, REICH)
w2 = Z.sicherer_weg(S, Z1, b2)
pruefe(2, "Todeszone Torhaus: Weg %s Gefahr %d" % (w2, Z.weg_gefahr(S, w2, b2)), w2 and Z.weg_gefahr(S, w2, b2) == 0)
L3 = {1: {"besitzer": 2, "typ": 22, "x": 80, "y": 120, "leben": 5000}, 2: {"besitzer": 2, "typ": 22, "x": 120, "y": 120, "leben": 5000}}
REICH3 = {22: 30}
b3 = Z.bedrohungen(L3, {}, feind, REICH3)
w3 = Z.sicherer_weg(S, Z1, b3)
pruefe(3, "alles gedeckt: Weg %s Gefahr %s | Gerade %d" % (w3, w3 and Z.weg_gefahr(S, w3, b3), Z.weg_gefahr(S, [Z1], b3)),
       w3 and Z.weg_gefahr(S, w3, b3) < Z.weg_gefahr(S, [Z1], b3))
L4 = {1: {"besitzer": 2, "typ": 23, "x": 115, "y": 125, "leben": 5000}}
b4 = Z.bedrohungen(L4, {}, feind, REICH)
feuer4 = [(100, 110, 4)]
w4 = Z.sicherer_weg(S, Z1, b4, feuer=feuer4)
punkte4 = []
a = S
for b in (w4 or []):
    punkte4 += Z._strecke(a, b); a = b
pruefe(4, "Feuer + Schuetze: Weg %s Gefahr %s, im Feuer %d" % (w4, w4 and Z.weg_gefahr(S, w4, b4),
       sum(1 for p in punkte4 if Z.schach(p, (100, 110)) <= 4)),
       w4 and Z.weg_gefahr(S, w4, b4) == 0 and not any(Z.schach(p, (100, 110)) <= 4 for p in punkte4))
pruefe(5, "mindestzahl 10.000/100 -> %d, 60.000/100 -> %d" % (Z.mindestzahl(10000, 100), Z.mindestzahl(60000, 100)),
       Z.mindestzahl(10000, 100) == 1 and Z.mindestzahl(60000, 100) == 5)
print("%d von %d gruen" % (sum(ok), len(ok)))
raise SystemExit(0 if all(ok) else 1)
