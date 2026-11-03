# -*- coding: utf-8 -*-
"""Warum sank die Zahl in der Lastprobe? Schaden 1 je Angreifer und Takt: Wer viele Angreifer hat, stirbt irgendwann.
Geprueft an jedem Toten: Leben am Anfang gegen die Summe der Angreifer ueber die Zeit.

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/last_tode.py data/research/auge_plan/laeufe/lauf_s_20261103_193744_last.auge
"""
import collections
import sys

import numpy as np

from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.analysis.auge_regeln import reihen_lesen

reihen, tab = reihen_lesen(sys.argv[1], Feldkarte.laden(feldliste=FELDLISTE))
print("Rahmen", len(reihen), "Tabelle Pikenier gegen Pikenier", int(tab["nah"][25, 25]), "Leben Pikenier", int(tab["leben"][25]))
t0, s0 = reihen[0]
pike = (s0["typ"] == 25) & (s0["da"] != 0)
pike[0] = False
start = np.nonzero(pike)[0]
leben0 = s0["leben"].copy()
angreifer_hoechstens = 0
letzte = {}
tot_bei = {}
for t, s in reihen:
    z = np.bincount(s["schlaegt"][(s["da"] != 0) & (s["typ"] == 25) & (s["schlaegt"] > 0)].astype(np.int64), minlength=2500)
    angreifer_hoechstens = max(angreifer_hoechstens, int(z.max()))
    for n in start:
        if n in tot_bei:
            continue
        if s["da"][n] and s["typ"][n] == 25 and s["leben"][n] > 0:
            letzte[n] = (t, int(s["leben"][n]), int(z[n]))
        else:
            tot_bei[n] = t
print("Tote", len(tot_bei), "von", len(start), "groesste Zahl Angreifer auf einen", angreifer_hoechstens)
print("erster Tod nach", min(tot_bei.values()) - t0 if tot_bei else None, "letzter nach", max(tot_bei.values()) - t0 if tot_bei else None)
print("Verlust bis Takt", reihen[-1][0] - t0, "nach Angreifern im letzten Rahmen, je Stufe: (Angreifer, Einheiten, mittlerer Verlust je Takt)")
tn, sn = reihen[-1]
v = collections.defaultdict(list)
z = np.bincount(sn["schlaegt"][(sn["da"] != 0) & (sn["typ"] == 25) & (sn["schlaegt"] > 0)].astype(np.int64), minlength=2500)
for n in start:
    if n not in tot_bei:
        v[int(z[n])].append((int(leben0[n]) - int(sn["leben"][n])) / (tn - t0))
for k in sorted(v):
    print(" ", k, len(v[k]), round(float(np.mean(v[k])), 2))
print("Tote nach Lage: Leben zuletzt, Takt zuletzt, Angreifer zuletzt, die ersten 10:", sorted((tot_bei[n] - t0, letzte[n][1], letzte[n][2]) for n in tot_bei)[:10])
