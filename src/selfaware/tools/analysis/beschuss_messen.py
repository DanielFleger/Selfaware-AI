# -*- coding: utf-8 -*-
"""Schaden je feindlichem Schuetzen und Tick an einer Assassine - aus Lageprotokollen (12.10. 01:50, Daniel: Risiko gegen
Ertrag abwaegen statt fester Umkreise). Je Runde und eigener Assassine: Lebensverlust, Zeit seit der Vorrunde, Zahl der
feindlichen Fernkaempfer, deren Reichweite (schussfeld.REICHWEITE, Schach) sie erreicht; nur Runden OHNE feindlichen
Nahkaempfer/Lord/Arbeiter im Umkreis 3 (sonst mischt sich Nahkampfschaden hinein). Ergebnis: Schaden je Schuetze und Tick
(Summe Verlust / Summe Schuetzen x Ticks) und die Verteilung.
Aufruf: uv run python -m selfaware.tools.analysis.beschuss_messen data/research/lage_....jsonl.gz [...]"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))

from selfaware.telemetry.lageprotokoll import runden
import selfaware.services.schussfeld as S


def main():
    summe_d, summe_st, n, nullrunden = 0.0, 0.0, 0, 0
    je = {}
    for pfad in sys.argv[1:]:
        vorher = {}
        for t, st, E, G in runden(pfad):
            eig = {e["nr"]: e for e in E if e["typ"] == 73 and e["besitzer"] == 1}
            sch = [((e["x"], e["y"]), S.REICHWEITE[e["typ"]]) for e in E if e["besitzer"] not in (0, 1) and e["typ"] in S.REICHWEITE]
            nah = [(e["x"], e["y"]) for e in E if e["besitzer"] not in (0, 1) and e["typ"] not in S.REICHWEITE and e["typ"] not in (44, 45)]
            for nr, e in eig.items():
                a = vorher.get(nr)
                if a and t > a[0]:
                    ort = (e["x"], e["y"])
                    if any(S.schach(ort, p) <= 3 for p in nah):
                        continue
                    k = S.gefahr_am(ort, sch)
                    d = max(0, a[1] - e["leben"])
                    if k:
                        summe_d += d; summe_st += k * (t - a[0]); n += 1
                        je.setdefault(k, [0, 0])
                        je[k][0] += d; je[k][1] += t - a[0]
                    elif d:
                        nullrunden += 1
            vorher = {nr: (t, e["leben"]) for nr, e in eig.items()}
    print("Runden mit Schuetzen in Reichweite: %d, Schaden je Schuetze und Tick: %.2f" % (n, summe_d / summe_st if summe_st else 0))
    print("je Schuetzenzahl (Schaden je Tick):", {k: round(v[0] / v[1], 1) for k, v in sorted(je.items()) if v[1]})
    print("Runden mit Schaden OHNE Schuetzen in Reichweite (und ohne Nahkampf im Umkreis 3):", nullrunden)


if __name__ == "__main__":
    main()
