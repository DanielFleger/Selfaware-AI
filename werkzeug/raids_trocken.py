# -*- coding: utf-8 -*-
"""B-168 Trockentest ohne Spiel: Runden eines Lageprotokolls durch Brandtrupp und Reiterjagd (mit gefahrenschutz.Lage) fuer
einen Spieler - Befehle werden nur mitgeschrieben. Zeigt je Runde Ziele, Risiko, Wegketten und die Zeit je Runde.
Aufruf: python werkzeug/raids_trocken.py <lage.jsonl.gz> <spieler> <freunde,...> [jede_n_te_runde]"""
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import gefecht
import gefahrenschutz as GS
import parteien
import raids as R
from lageprotokoll import runden


class Befehle:
    def __init__(self):
        self.liste = []

    def __call__(self, b, warte=1.0, bis=None):
        self.liste.append(b)
        return []


def main():
    pfad, sp = sys.argv[1], int(sys.argv[2])
    freunde = {int(v) for v in sys.argv[3].split(",")}
    jede = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    parteien.setzen(sp, freunde)
    brand = R.Brandtrupp(sp, lambda nr: 0)
    reiter = R.Reiterjagd(sp)
    zeiten, befehle_n, meldungen = [], 0, 0
    for i, (t, st, E, G) in enumerate(runden(pfad)):
        if i % jede:
            continue
        L = {e["nr"]: e for e in E}
        Gd = {g["nr"]: g for g in G}
        a = time.time()
        lage = GS.Lage(L, Gd, lambda b: b not in freunde | {0}, gefecht.FERN_REICH)
        b = Befehle()
        aus = brand.schritt(L, Gd, b, lage) + reiter.schritt(L, Gd, b, lage)
        zeiten.append(time.time() - a)
        befehle_n += len(b.liste)
        meldungen += len(aus)
        for m in aus:
            print("%6d %s" % (t, m[:200]))
    print("RUNDEN %d, Zeit je Runde mittel %.3f s, hoechstens %.3f s, Befehle %d, Meldungen %d" % (
        len(zeiten), sum(zeiten) / max(1, len(zeiten)), max(zeiten or [0]), befehle_n, meldungen))


if __name__ == "__main__":
    main()
