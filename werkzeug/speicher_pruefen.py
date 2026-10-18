# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer erstes_spiel.speicher_nachbauen (18.10., Anlass 1018d). Vorher festgelegt:
  1. eigener Kornspeicher steht -> kein Nachbau
  2. nur der Kornspeicher des Gegners steht (unserer eingerissen) -> Nachbau
  3. keiner steht, aber einer ist bestellt -> kein zweiter
  4. keiner steht, letzter Versuch vor 100 Ticks -> warten; vor 201 Ticks -> Nachbau
Gegenprobe: mit "alt" wird das alte Verhalten nachgestellt (kein Weg baut den Kornspeicher nach) -> Faelle 2 und 4 rot.
Aufruf: python werkzeug/speicher_pruefen.py [alt]"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import erstes_spiel as E

nachbau = E.speicher_nachbauen
if len(sys.argv) > 1 and sys.argv[1] == "alt":
    nachbau = lambda *a, **k: False


def main():
    ok = []

    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))

    eigen = {1: {"typ": 19, "besitzer": 1, "x": 10, "y": 10}, 2: {"typ": 3, "besitzer": 1, "x": 20, "y": 20}}
    nur_feind = {1: {"typ": 19, "besitzer": 2, "x": 90, "y": 90}, 2: {"typ": 3, "besitzer": 1, "x": 20, "y": 20}}
    a = nachbau(eigen, [], 5000, -10 ** 6, sp=1)
    pruefe(1, "eigener steht: Nachbau %s" % a, a is False)
    b = nachbau(nur_feind, [], 5000, -10 ** 6, sp=1)
    pruefe(2, "nur der des Gegners steht: Nachbau %s" % b, b is True)
    c = nachbau(nur_feind, [{"typ": 19}], 5000, -10 ** 6, sp=1)
    pruefe(3, "bestellt: Nachbau %s" % c, c is False)
    d1, d2 = nachbau(nur_feind, [], 5000, 4900, sp=1), nachbau(nur_feind, [], 5101, 4900, sp=1)
    pruefe(4, "letzter Versuch vor 100 Ticks: %s, vor 201: %s" % (d1, d2), d1 is False and d2 is True)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
