# -*- coding: utf-8 -*-
"""Aus der Szene Beschuss (Editor, Tempo 40, jeder Takt): je Geschossart Zahl, Flugtempo, Treffer; Abstand von der Landung zum Lebensverlust; Zielwahl; wer ohne Verlust blieb.

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/geschosse_beschuss.py > data/research/auge_plan/lauf_s_20261103/geschosse_beschuss.txt
"""
import collections
import glob
import json
import os

import numpy as np

from selfaware.tools.analysis import auge_regeln as ar
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

HIER = os.path.dirname(os.path.abspath(__file__))
p = sorted(glob.glob(os.path.join(HIER, "..", "laeufe", "lauf_s_*_beschuss.auge")), key=os.path.getmtime)[-1]
k = Feldkarte.laden(feldliste=FELDLISTE)
r, _ = ar.reihen_lesen(p, k)
g = ar.geschosse_lesen(p, k)
print(os.path.basename(p), len(r), "Rahmen,", len(g), "Geschosse")
print(json.dumps(ar.geschosse_werten(g, r), ensure_ascii=False))
s = r[len(r) // 2][1]
print("Schuetze hat den Besitzer des Geschosses:", sum(int(s["besitzer"][x["schuetze"]]) == x["besitzer"] for x in g), "von", len(g), "; Ziel hat ihn:", sum(int(s["besitzer"][x["ziel"]]) == x["besitzer"] for x in g))
takte = [t for t, _ in r]
stand = dict(r)
versatz, fehl, naeher = collections.Counter(), collections.Counter(), collections.Counter()
for x in g:
    if x["bis"] is None or x["ziel"] <= 0:
        continue
    i = int(np.searchsorted(takte, x["bis"]))
    if i == 0 or i >= len(takte) - 3:
        continue
    d_ = None
    for d in range(-2, 4):
        if 0 < i + d < len(takte):
            a, b = stand[takte[i + d - 1]], stand[takte[i + d]]
            if b["leben"][x["ziel"]] < a["leben"][x["ziel"]] and b["typ"][x["ziel"]] == a["typ"][x["ziel"]]:
                d_ = d
                break
    versatz[d_] += 1
    if d_ is None:
        fehl[(x["art"], int(stand[takte[i]]["typ"][x["ziel"]]))] += 1
print("Landung zu Lebensverlust in Takten:", sorted(versatz.items(), key=str))
print("Ohne Verlust im Fenster, je Geschoss und Opfer:", fehl.most_common(30))
for x in g:
    if x["ziel"] <= 0:
        continue
    i = int(np.searchsorted(takte, x["von"]))
    if i >= len(takte):
        continue
    s = stand[takte[i]]
    fe = (s["da"] != 0) & (s["besitzer"] != s["besitzer"][x["schuetze"]]) & (s["besitzer"] > 0)
    fe[0] = False
    d = np.maximum(np.abs(s["mx"].astype(int) - int(s["mx"][x["schuetze"]])), np.abs(s["my"].astype(int) - int(s["my"][x["schuetze"]])))
    dz = max(abs(int(s["mx"][x["ziel"]]) - int(s["mx"][x["schuetze"]])), abs(int(s["my"][x["ziel"]]) - int(s["my"][x["schuetze"]])))
    n = int(((d < dz) & fe).sum())
    naeher["keiner naeher" if n == 0 else "1 bis 3 naeher" if n <= 3 else "mehr naeher"] += 1
print("Zielwahl, Feinde naeher als das Ziel beim Abschuss:", dict(naeher))
