# -*- coding: utf-8 -*-
"""B-142 Lauf K: P242 Flaggen und P258 Gold der Ingenieure mit den richtigen Arten. Die Flaggen-Art steht im Code von updateEntities, Ingenieure sind Einheitentyp 30.

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/punkte_rechnen5.py <basis>
"""
import collections
import json
import os
import pickle
import re
import sys

import numpy as np

from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

HIER = os.path.dirname(os.path.abspath(__file__))
basis = sys.argv[1]
k = Feldkarte.laden(feldliste=FELDLISTE)
d1 = pickle.load(open(os.path.join(HIER, "reihen.pkl"), "rb"))
d2 = pickle.load(open(os.path.join(HIER, "reihen2.pkl"), "rb"))
EX = r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference\functions"
import glob

for p in glob.glob(os.path.join(EX, "*.json")):
    try:
        t = json.load(open(p, encoding="utf-8")).get("pseudocode") or ""
    except (OSError, ValueError):
        continue
    if "UpdateFlag_1_2_4_Entity();" in t or "UpdateFlag_1_2_4_Entity()" in t:
        z = t.splitlines()
        for i, l in enumerate(z):
            if "UpdateFlag_1_2_4_Entity" in l and "void" not in l:
                print(os.path.basename(p), [s.strip() for s in z[max(0, i - 6):i + 1]])
        break
g = collections.defaultdict(dict)
for a in (d1["t1"], d1["danach"]):
    for sp, r in a["gold"].items():
        for (t0, w0), (t1, w1) in zip(r, r[1:]):
            g[sp][t1] = w1 - w0
for typ in (30,):
    hist = collections.Counter()
    for a in (d2["t1"], d2["danach"]):
        for t, i, ty, o in a["neu"]:
            if ty == typ and o in g:
                hist[g[o].get(t, 0)] += 1
    print("Typ", typ, "Goldaenderung im Rahmen des neuen Eintrags", hist.most_common(10), "gesamt", sum(hist.values()))
a = aw.Aufzeichnung(basis + "_t1.auge")
E = a.namen.index("DAT_EntityState")
Eb = a.bereiche[E][1]
ER = {f: k.adresse("DAT_EntityState", "entityArray[]." + f) for f in ("logicalState", "entityType", "owner", "someTracker")}
TYP = {2: "<i2", 4: "<i4"}


def sp(p, f):
    return np.ndarray(shape=(f[3],), dtype=TYP[f[1]], buffer=p, offset=f[0] - Eb, strides=(f[2],))


arten = collections.defaultdict(lambda: collections.defaultdict(list))
for r, p, _ in a.staende():
    if r.bereich != E:
        continue
    l, ty, ow, tr = (sp(p, ER[x]) for x in ("logicalState", "entityType", "owner", "someTracker"))
    m = l != 0
    for art in (1, 2, 3, 4):
        z = collections.Counter(zip(ow[m & (ty == art)].tolist(), tr[m & (ty == art)].tolist()))
        for o in range(1, 9):
            w = tuple(sorted((v, c) for (b, v), c in z.items() if b == o))
            rr = arten[art][o]
            if not rr or rr[-1][1] != w:
                rr.append((r.takt, w))
for art, v in arten.items():
    print("Art", art, {o: r[:4] for o, r in v.items() if any(x[1] for x in r)})
print("Wahl in t1", {o: d1["t1"]["spieler"].get((o, "aiRecruitUnitChoiceState"), [])[:5] for o in range(1, 9)})
