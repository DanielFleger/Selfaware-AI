# -*- coding: utf-8 -*-
"""B-142: Die rund 5 Prozent Schuesse ohne Verlust. Vorher festgelegt: Die These "trifft einen anderen" ist widerlegt, wenn am Landeort niemand sonst Leben verliert.

Je Fall: Wo stand das Ziel bei der Landung, wo landete das Geschoss, und wer verlor im Fenster bis 3 Felder um den Landeort Leben?

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/geschosse_ohne_verlust.py > data/research/auge_plan/lauf_s_20261103/geschosse_ohne_verlust.txt
"""
import collections
import glob
import os

import numpy as np

from selfaware.tools.analysis import auge_regeln as ar
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

HIER = os.path.dirname(os.path.abspath(__file__))
p = sorted(glob.glob(os.path.join(HIER, "..", "laeufe", "lauf_s_*_beschuss.auge")), key=os.path.getmtime)[-1]
k = Feldkarte.laden(feldliste=FELDLISTE)
r, _ = ar.reihen_lesen(p, k)
g = ar.geschosse_lesen(p, k)
print("Felder eines Geschosses:", sorted(g[0]))
takte = [t for t, _ in r]
stand = dict(r)
print("Felder einer Reihe:", sorted(r[0][1]))
ohne = []
for x in g:
    if x["bis"] is None or x["ziel"] <= 0:
        continue
    i = int(np.searchsorted(takte, x["bis"]))
    if i == 0 or i >= len(takte) - 3:
        continue
    treffer = False
    for d in range(-2, 4):
        if 0 < i + d < len(takte):
            a, b = stand[takte[i + d - 1]], stand[takte[i + d]]
            if b["leben"][x["ziel"]] < a["leben"][x["ziel"]] and b["typ"][x["ziel"]] == a["typ"][x["ziel"]]:
                treffer = True
                break
    if not treffer:
        ohne.append((x, i))
print("Faelle ohne Verlust am Ziel:", len(ohne))
gruende = collections.Counter()
rest = []
beispiele = {}
for x, i in ohne:
    s = stand[takte[i]]
    ziel = x["ziel"]
    # Wo war das Ziel beim Abschuss und bei der Landung? In Mikro-Einheiten, 8 = ein Feld
    j = int(np.searchsorted(takte, x["von"]))
    s0 = stand[takte[min(j, len(takte) - 1)]]
    weg = max(abs(int(s["mx"][ziel]) - int(s0["mx"][ziel])), abs(int(s["my"][ziel]) - int(s0["my"][ziel]))) // 8
    # Wer verlor im Fenster Leben, gemessen vom Ziel-Ort beim Abschuss aus?
    cx, cy = int(s0["mx"][ziel]), int(s0["my"][ziel])
    andere = []
    for d in range(-2, 4):
        if 0 < i + d < len(takte):
            a, b = stand[takte[i + d - 1]], stand[takte[i + d]]
            ver = (b["leben"] < a["leben"]) & (b["typ"] == a["typ"]) & (b["da"] != 0)
            ver[0] = False
            for n in ver.nonzero()[0]:
                if max(abs(int(b["mx"][n]) - cx), abs(int(b["my"][n]) - cy)) <= 3 * 8:
                    andere.append(int(n))
    gefeuert = x["art"]
    leben = int(s["leben"][ziel])
    typ = int(s["typ"][ziel])
    da = int(s["da"][ziel])
    besitzer_gleich = int(s["besitzer"][ziel]) == int(s["besitzer"][x["schuetze"]])
    if not da:
        grund = "Ziel ist weg"
    elif leben <= 0:
        grund = "Ziel war schon tot"
    elif weg >= 2:
        grund = "Ziel lief weg (2 Felder oder mehr)"
    elif set(andere) - {ziel}:
        grund = "anderer verlor Leben am Ort"
    else:
        grund = "niemand verlor Leben am Ort"
    gruende[(gefeuert, grund)] += 1
    beispiele.setdefault((gefeuert, grund), {"von": x["von"], "bis": x["bis"], "ziel": ziel, "typ": typ, "leben": leben, "weg_felder": weg, "andere": sorted(set(andere))[:4]})
    if grund == "niemand verlor Leben am Ort":
        pk, zu = x.get("punkt"), x.get("zuletzt")
        rest.append((gefeuert, x["von"], x["bis"], x["bis"] - x["von"], ziel, typ, leben, weg, (int(s["mx"][ziel]) // 8, int(s["my"][ziel]) // 8), pk, zu, x["start"]))
print("Gruende (Geschoss, Grund):", gruende.most_common())
for k_, v in sorted(beispiele.items(), key=str):
    print("  ", k_, v)
print("Rest: (Geschoss, von, bis, Flug, Ziel, Art, Leben, Ziel lief Felder, Ziel Feld, punkt, zuletzt, start)")
for z in rest[:20]:
    print("  ", z)
