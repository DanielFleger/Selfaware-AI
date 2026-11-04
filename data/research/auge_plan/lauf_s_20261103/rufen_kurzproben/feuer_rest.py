# -*- coding: utf-8 -*-
import glob, os, collections
import numpy as np
from selfaware.tools.analysis import auge_regeln as ar
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
L = r"data/research/auge_plan/laeufe"
p = sorted(glob.glob(os.path.join(L, "lauf_s_*_beschuss.auge")), key=os.path.getmtime)[-1]
k = Feldkarte.laden(feldliste=FELDLISTE)
r, _ = ar.reihen_lesen(p, k)
g = ar.geschosse_lesen(p, k)
takte = [t for t, _ in r]
stand = dict(r)
print("erster Rahmen", takte[0], "letzter", takte[-1])
feuer = [x for x in g if x["art"] == "feuer"]
print("Feuer: Zahl", len(feuer), "Abschuss-Takte (Takt, Anzahl):", collections.Counter(x["von"] for x in feuer).most_common(8))
wer = {x["ziel"] for x in feuer if x["von"] == 7808697}
for z in sorted(wer)[:4]:
    fo = []
    for t in takte:
        v = (int(stand[t]["leben"][z]), int(stand[t]["typ"][z]), int(stand[t]["zustand"][z]))
        if not fo or fo[-1][1] != v:
            fo.append((t - 7808697, v))
    print("Ziel", z, [q for q in fo if q[0] >= -30][:10])
# Fuer alle Feuer: Abstand von der Landung bis zum ersten Lebensverlust des Ziels
ab = collections.Counter()
for x in feuer:
    if x["bis"] is None or x["ziel"] <= 0:
        ab["ohne Ziel"] += 1
        continue
    i = int(np.searchsorted(takte, x["bis"]))
    d_ = None
    for j in range(max(i - 2, 1), min(i + 60, len(takte))):
        a, b = stand[takte[j - 1]], stand[takte[j]]
        if b["leben"][x["ziel"]] < a["leben"][x["ziel"]] and b["typ"][x["ziel"]] == a["typ"][x["ziel"]]:
            d_ = takte[j] - x["bis"]
            break
    ab[d_] += 1
print("Feuer: Takte von der Landung bis zum ersten Verlust am Ziel:", sorted(ab.items(), key=lambda q: (q[0] is None, str(q[0]))))
print("Erstes Geschoss jeder Art (Takt, Art):", sorted({x["art"]: x["von"] for x in sorted(g, key=lambda q: -q["von"])}.items(), key=lambda q: q[1]))
