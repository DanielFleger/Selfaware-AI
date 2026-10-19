# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer lordwache.fluchtpunkt (19.10. 19:02). Vorher festgelegt:
  1. kein Brand -> None (Lord bleibt)
  2. Brand 4 Felder rechts vom Lord (104,100) -> Fluchtpunkt links (x < 100), 8 Felder weit, naechster Brand >= 12 Felder
  3. Braende rechts UND oben -> Punkt links unten (x < 100, y > 100)
  4. das beste Feld (links) ist belegt -> ein anderes, aber weiter weg vom Brand als der Lord jetzt
Gegenprobe: python werkzeug/lordfeuer_pruefen.py alt  (Fluchtpunkt = Richtung ZUM Brand) -> 2, 3 und 4 rot."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lordwache as LW

if len(sys.argv) > 1 and sys.argv[1] == "alt":
    _f = LW.fluchtpunkt
    LW.fluchtpunkt = lambda l, b, belegt=(): (b[0] if b else None)


def main():
    ok = []

    def pruefe(nr, text, bed):
        ok.append(bool(bed))
        print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text), flush=True)

    p1 = LW.fluchtpunkt((100, 100), [])
    pruefe(1, "kein Brand: %s" % (p1,), p1 is None)
    p2 = LW.fluchtpunkt((100, 100), [(104, 100)])
    pruefe(2, "Brand rechts: %s" % (p2,), p2 and p2[0] < 100 and LW.schach(p2, (104, 100)) >= 12)
    p3 = LW.fluchtpunkt((100, 100), [(104, 100), (100, 96)])
    pruefe(3, "Brand rechts + oben: %s" % (p3,), p3 and p3[0] < 100 and p3[1] > 100)
    p4 = LW.fluchtpunkt((100, 100), [(104, 100)], belegt=[(92, 100), (92, 92), (92, 108)])
    pruefe(4, "links belegt: %s" % (p4,), p4 and p4 not in [(92, 100), (92, 92), (92, 108)]
           and LW.schach(p4, (104, 100)) > LW.schach((100, 100), (104, 100)))
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
