# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer fallenwache.py (19.10.). Vorher festgelegt (eigenes Gebaeude Typ 3, 3x3 bei (100,100)):
  1. feindliche Assassine bei (90,101), Laufziel (99,101) direkt neben dem Gebaeude -> Falle genau auf (99,101)
  2. Laufziel (95,101) - 5 Felder vom Gebaeude -> keine Falle
  3. eigene Einheit mit Laufziel (99,101) -> keine; feindliche Einheit 2 Felder vor dem Laufziel -> keine (steht gleich drauf)
  4. 8 Holz -> keine Falle; 30 Holz und 3 Angreifer mit verschiedenen Laufzielen -> hoechstens 2 in dieser Runde
  5. dasselbe Feld wird 1.000 Ticks spaeter nicht erneut versucht, nach 2.000 wieder
  6. Laufziel AUF dem Gebaeude (Feld/Hof) -> keine Falle
Gegenprobe: mit "alt" zaehlt jedes Laufziel (ohne NAH-Grenze) -> Fall 2 rot.
Aufruf: python werkzeug/fallenwache_pruefen.py [alt]"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fallenwache as F

F.GROESSE[3] = 3
if len(sys.argv) > 1 and sys.argv[1] == "alt":
    F.NAH = 10 ** 6

G = {1: {"besitzer": 1, "typ": 3, "x": 100, "y": 100}}


def e(sp, x, y, lx, ly, typ=73):
    return {"besitzer": sp, "typ": typ, "x": x, "y": y, "laufx": lx, "laufy": ly, "leben": 12500}


def wache():
    gesetzt = []
    return F.Fallenwache(1, lambda x, y: gesetzt.append((x, y)) or True), gesetzt


def main():
    ok = []

    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))

    w, g = wache()
    w.schritt(1000, {5: e(2, 90, 101, 99, 101)}, G, 30)
    pruefe(1, "Laufziel neben dem Gebaeude: Fallen %s" % g, g == [(99, 101)])
    w, g = wache()
    w.schritt(1000, {5: e(2, 85, 101, 95, 101)}, G, 30)
    pruefe(2, "Laufziel 5 Felder weg: Fallen %s" % g, g == [])
    w, g = wache()
    w.schritt(1000, {5: e(1, 90, 101, 99, 101), 6: e(2, 97, 101, 99, 101)}, G, 30)
    pruefe(3, "eigene Einheit / Feind 2 Felder davor: Fallen %s" % g, g == [])
    w, g = wache()
    w.schritt(1000, {5: e(2, 90, 101, 99, 101)}, G, 8)
    w2, g2 = wache()
    w2.schritt(1000, {5: e(2, 90, 101, 99, 101), 6: e(2, 90, 103, 99, 102), 7: e(2, 110, 100, 103, 100)}, G, 30)
    pruefe(4, "8 Holz: %s; 30 Holz, 3 Angreifer: %s" % (g, g2), g == [] and len(g2) == 2)
    w, g = wache()
    L = {5: e(2, 90, 101, 99, 101)}
    w.schritt(1000, L, G, 30)
    w.schritt(2000, L, G, 30)
    n1 = len(g)
    w.schritt(3000, L, G, 30)
    pruefe(5, "Versuche bei 1000/2000/3000: %d nach 2000, %d nach 3000" % (n1, len(g)), n1 == 1 and len(g) == 2)
    w, g = wache()
    w.schritt(1000, {5: e(2, 90, 101, 101, 101)}, G, 30)
    pruefe(6, "Laufziel auf dem Gebaeude: Fallen %s" % g, g == [])
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
