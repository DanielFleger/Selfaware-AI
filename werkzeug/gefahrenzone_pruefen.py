# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer gefahrenzone.py (19.10.). Vorher festgelegt (wir = Spieler 1):
  1. Runde 1: eigene Gebaeude A (100,100) und B (150,150); Runde 2 bei Tick 5.000: A fehlt -> genau ein Verlust bei (100,100)
  2. bei Tick 6.000: Holzfaeller bei (110,105) verboten, bei (125,100) erlaubt (25 Felder), Kornspeicher bei (105,100) erlaubt
  3. bei Tick 8.100 (3.100 nach dem Verlust): Holzfaeller bei (110,105) wieder erlaubt
  4. eine eigene Fallgrube, ein eigener Lagerplatz und ein feindliches Gebaeude verschwinden -> kein Verlust
  5. Sperrflaechen fuer den Planer bei Tick 6.000: genau [(80, 80, 120, 120)]
Gegenprobe: mit "alt" ist der Umkreis 0 -> Faelle 2 und 5 rot.
Aufruf: python werkzeug/gefahrenzone_pruefen.py [alt]"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import gefahrenzone as GZ

if len(sys.argv) > 1 and sys.argv[1] == "alt":
    GZ.R = 0


def geb(uid, sp, typ, x, y):
    return {"uid": uid, "besitzer": sp, "typ": typ, "x": x, "y": y}


def main():
    ok = []

    def pruefe(nr, text, bed):
        ok.append(bool(bed))
        print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text), flush=True)

    z = GZ.Gefahrenzonen(1)
    z.runde(1000, {1: geb(11, 1, 3, 100, 100), 2: geb(12, 1, 32, 150, 150), 3: geb(13, 1, 67, 140, 140), 4: geb(14, 2, 3, 200, 200)})
    z.runde(5000, {2: geb(12, 1, 32, 150, 150), 3: geb(13, 1, 67, 140, 140), 4: geb(14, 2, 3, 200, 200)})
    pruefe(1, "Verluste %s" % z.verluste, [v[1] for v in z.verluste] == [(100, 100)])
    z.t = 6000
    e = (z.erlaubt(3, 110, 105), z.erlaubt(3, 125, 100), z.erlaubt(19, 105, 100))
    pruefe(2, "erlaubt Holzf. (110,105), Holzf. (125,100), Kornspeicher (105,100): %s" % (e,), e == (False, True, True))
    pruefe(5, "Sperrflaechen %s" % z.rechtecke(), z.rechtecke() == [(80, 80, 120, 120)])
    z.runde(8100, {2: geb(12, 1, 32, 150, 150), 3: geb(13, 1, 67, 140, 140), 4: geb(14, 2, 3, 200, 200), 5: geb(15, 1, 10, 160, 160)})
    pruefe(3, "bei 8.100 Holzf. (110,105) erlaubt: %s" % z.erlaubt(3, 110, 105), z.erlaubt(3, 110, 105))
    z.runde(8200, {2: geb(12, 1, 32, 150, 150)})
    pruefe(4, "Grube und feindliches Gebaeude weg: Verluste %s" % z.verluste, not z.verluste)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
