# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer die gemessenen Ketten im Kausalmodell (12.10., Daniel 01:09 "Cash von Steinen/Eisen/Brot",
01:26 "kohaerente Idee"). Vorher festgelegt, was gelten muss:
  1. Genug Bauern (10 am Feuer), je ein Platz Holz/Hopfen/Eisen/Stein bei 30 Feldern: die ERSTE Handlung ist Hopfen
     (hoechstes Gold je Arbeiter, L72), Eisen kommt vor Stein.
  2. Steinbruch-Paket bei 64 Feldern verlangt 3 Ochsen (L71: Ochse 7 je Fahrt), bei 10 Feldern 2.
  3. Nur 4 Bauern: der Steinbruch (3 + Ochsen Arbeiter) wird NICHT gebaut, Hopfen und Eisen schon.
Gegenprobe: Sortierung nach Wert je Gebaeude (alte Regel) -> Fall 1 rot (das Steinbruch-Paket kaeme zuerst).
Aufruf: python werkzeug/kausal_ketten_pruefen.py [je_gebaeude]"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import kausal as K

if len(sys.argv) > 1 and sys.argv[1] == "je_gebaeude":
    import inspect
    quelle = inspect.getsource(K.entscheide).replace("-x[0] / float(x[4])", "-x[0]")
    exec(compile(quelle, "entscheide_alt", "exec"), K.__dict__)


def main():
    ok = []
    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))
    lager = (100, 100)
    def kand(d):
        aus = []
        for typ, ort in ((3, (100 + d, 100)), (31, (100, 100 + d)), (5, (100 - d, 100)), (20, (100, 100 - d))):
            dd = K.schach(ort, lager)
            kost = {"holz": 25 if typ == 20 else 5}
            aus.append((typ, ort, kost, K.arbeiter(typ, dd)))
        return aus
    st = {"feuer": 10, "platz": 40, "leute": 40, "holz": 500, "gold": 500, "stein": 0}
    h = K.entscheide(1000, 20000, st, kand(30), (100, 100), {3: lager, 31: lager, 5: lager, 20: lager}, 6)
    reihe = [x[1] for x in h if x[1] != 1]
    pruefe(1, "Reihenfolge bei 10 Bauern: %s (31 Hopfen, 5 Eisen, 3 Holz, 20 Stein)" % reihe,
           reihe and reihe[0] == 31 and (5 not in reihe or 20 not in reihe or reihe.index(5) < reihe.index(20)))
    pruefe(2, "Ochsen je Bruch: 64 Felder %d, 10 Felder %d" % (K.ochsen_fuer(64), K.ochsen_fuer(10)),
           K.ochsen_fuer(64) == 3 and K.ochsen_fuer(10) == 2)
    st4 = dict(st, feuer=4)
    h4 = [x[1] for x in K.entscheide(1000, 20000, st4, kand(30), (100, 100), {3: lager, 31: lager, 5: lager, 20: lager}, 6) if x[1] != 1]
    pruefe(3, "nur 4 Bauern: %s - Steinbruch nicht dabei, Hopfen und Eisen schon" % h4, 20 not in h4 and 31 in h4 and 5 in h4)
    # 4. (01:36, 1012h) Bei Tick 11.000 mit mitlaufendem Fenster (jetzt + 16.000) werden Hopfen und Eisen gewaehlt
    h11 = [x[1] for x in K.entscheide(11000, 27000, st, kand(30), (100, 100), {3: lager, 31: lager, 5: lager, 20: lager}, 6) if x[1] != 1]
    h11f = [x[1] for x in K.entscheide(11000, 16753, st, kand(30), (100, 100), {3: lager, 31: lager, 5: lager, 20: lager}, 6) if x[1] != 1]
    pruefe(4, "Tick 11.000, Fenster bis 27.000: %s (festes Ende 16.753 zum Vergleich: %s)" % (h11, h11f), 31 in h11 and 5 in h11)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
