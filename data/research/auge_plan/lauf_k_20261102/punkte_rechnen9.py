# -*- coding: utf-8 -*-
"""B-142 Lauf K, P258: Was zahlt die KI? Das Spiel zieht das Gold ab, wenn es einem Bauern die neue Art gibt (unitTypeToChangeInto, nonEuroRecruit 0x0052EC10); der Soldat erscheint erst spaeter.
Darum: In den strengen Fenstern je neu gesetzter Art die Goldaenderung genau in diesem Takt.

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/punkte_rechnen9.py <basis> > data/research/auge_plan/lauf_k_20261102/punkte_rechnung9.txt
"""
import collections
import os
import pickle
import sys

import numpy as np

from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

HIER = os.path.dirname(os.path.abspath(__file__))
basis = sys.argv[1]
k = Feldkarte.laden(feldliste=FELDLISTE)
d6 = pickle.load(open(os.path.join(HIER, "reihen6.pkl"), "rb"))
W = k.adresse("DAT_UnitsState", "units[].unitTypeToChangeInto")
O = k.adresse("DAT_UnitsState", "units[].owner")
TYP = {1: "<i1", 2: "<i2", 4: "<i4"}


def spalte(p, b, f):
    a, gr, s, n = f
    return np.ndarray(shape=(n,), dtype=TYP[gr], buffer=p, offset=a - b, strides=(s,))


je = collections.defaultdict(collections.Counter)
einzeln = []
for fn in ("t1", "t6", "t8"):
    R = d6[fn]["R"]
    auf = aw.Aufzeichnung(f"{basis}_{fn}.auge")
    i_u = auf.namen.index("DAT_UnitsState")
    b = auf.bereiche[i_u][1]
    alt = None
    for r, p, _ in auf.staende():
        if r.bereich != i_u:
            continue
        w = spalte(p, b, W)
        if alt is not None:
            o = spalte(p, b, O)
            t = r.takt
            pro = collections.Counter()
            neu = np.flatnonzero((w != alt) & (w != 0))
            neu = neu[neu != 0]  # Platz 0 ist ein Merkplatz: Das Spiel kopiert Einheiten dorthin, das sind keine Anwerbungen
            for i in neu:
                pro[int(o[i])] += 1
            for i in neu:
                ow = int(o[i])
                if 1 <= ow <= 8 and t in R and t - 1 in R:
                    d = R[t][ow]["gold"] - R[t - 1][ow]["gold"]
                    allein = pro[ow] == 1
                    je[int(w[i])][d if allein else f"{d} mit {pro[ow]}"] += 1
                    if int(w[i]) == 30:
                        einzeln.append((fn, t, ow, R[t - 1][ow]["gold"], R[t][ow]["gold"], R[t]["dayTicks"]))
        alt = w.copy()
for ty in sorted(je):
    print("Art", ty, je[ty].most_common(6))
print("Ingenieure", einzeln)
