# -*- coding: utf-8 -*-
"""Lauftempo je Einheitenart aus Lageprotokollen (SAI 17.10., Daniel 09:41: "deren Laufgeschwindigkeit" - wer kann eine
Assassine einholen, wem kann sie davonlaufen).

Gezaehlt wird ein Rundenpaar einer Einheit nur, wenn sie in BEIDEN Runden laeuft (Zustand 101), ihr Laufziel gleich
bleibt und sie in der zweiten Runde noch mindestens 3 Felder (Schach) vom Ziel entfernt ist - sonst misst man Warten,
Ankommen oder Kampf mit. Tempo = Schachfelder / Takte; Ergebnis je Art: Median der Takte je Feld und Streuung (Quartile),
Zahl der Paare. Die Spieltabelle (DAT_UNIT_MOVEMENT_SPEED_ARRAY, live 17.10.) steht daneben als "Klasse".
VORHER FESTGELEGT: Stimmen die gemessenen Takte je Feld fuer Holzfaeller (24) und Steinbrucharbeiter (16) nicht mit L68
ueberein (mehr als 15 % daneben), misst das Werkzeug falsch und seine anderen Zahlen gelten nicht.
Aufruf: uv run python -m selfaware.tools.analysis.tempo_messen data/research/lage_....jsonl.gz [...]"""
import os
import statistics as S
import sys
from collections import defaultdict

HIER = os.path.dirname(os.path.abspath(__file__))

from selfaware.telemetry.lageprotokoll import runden

KLASSE = {1: 1, 3: 2, 5: 1, 6: 1, 7: 2, 8: 2, 9: 3, 22: 1, 23: 2, 24: 1, 25: 2, 26: 1, 27: 3, 28: 1, 29: 1, 30: 1,
          37: 2, 55: 2, 70: 1, 71: 1, 72: 1, 73: 1, 74: 1, 75: 2, 76: 2}
NAME = {1: "Bauer", 3: "Holzfaeller", 5: "Tunnelgraeber", 6: "Jaeger", 7: "Steinmetz", 8: "Steinbrucharbeiter", 9: "Ochse",
        22: "Bogenschuetze", 23: "Armbrust", 24: "Speer", 25: "Pike", 26: "Streitkolben", 27: "Schwert", 28: "Ritter",
        29: "Leitermann", 30: "Ingenieur", 37: "Moench", 55: "Lord", 70: "arab. Bogen", 71: "Sklave", 72: "Schleuder",
        73: "Assassine", 74: "Pferdebogen", 75: "arab. Schwert", 76: "Feuerwerfer"}


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def main():
    je = defaultdict(list)
    for pfad in sys.argv[1:]:
        vorher = {}
        for t, st, E, G in runden(pfad):
            jetzt = {}
            for e in E:
                k = (e["nr"], e["typ"], e["besitzer"])
                jetzt[k] = (t, (e["x"], e["y"]), e.get("zustand"), (e.get("laufx"), e.get("laufy")))
                a = vorher.get(k)
                if not a or a[2] != 101 or e.get("zustand") != 101 or a[3] != jetzt[k][3] or t <= a[0]:
                    continue
                if schach(jetzt[k][1], jetzt[k][3]) < 3:
                    continue
                felder = schach(a[1], jetzt[k][1])
                if felder >= 2:
                    je[e["typ"]].append((t - a[0]) / float(felder))
            vorher = jetzt
    print("%-16s %6s %8s %14s %7s" % ("Art", "Klasse", "Takte/F", "Quartile", "Paare"))
    for typ, w in sorted(je.items(), key=lambda x: S.median(x[1])):
        if len(w) < 20:
            continue
        q = S.quantiles(w, n=4)
        print("%-16s %6s %8.1f %6.1f-%-7.1f %7d" % (NAME.get(typ, typ), KLASSE.get(typ, "?"), S.median(w), q[0], q[2], len(w)))


if __name__ == "__main__":
    main()
