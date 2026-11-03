# -*- coding: utf-8 -*-
"""Ist der Nahkampf im Gefecht derselbe wie im Editor? Vergleich je Paar und je Takt seit dem Weiterlaufen, ohne die Regel dazwischen.
Der Pruefer sah im Gefecht je Paar einen Treffer mit doppeltem Wert, immer den ersten. Ist das eine andere Spielregel, unterscheiden sich die Leben auch danach.

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/gefecht_gegen_editor.py data/research/auge_plan/laeufe/lauf_s_20261103_191555_nahkampf.auge data/research/auge_plan/laeufe/lauf_s_20261103_200835_nahkampf_g.auge > data/research/auge_plan/lauf_s_20261103/gefecht_gegen_editor.txt
"""
import collections
import json
import sys

import numpy as np

from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.analysis.auge_regeln import reihen_lesen

k = Feldkarte.laden(feldliste=FELDLISTE)
daten = []
for pfad in sys.argv[1:3]:
    plan = json.load(open(pfad + ".plan.json", encoding="utf-8"))
    reihen, tab = reihen_lesen(pfad, k)
    paare = collections.defaultdict(dict)
    for e in plan["einheiten"]:
        if "paar" in e:
            paare[(min(e["typ"], 999), e["rolle"])] = e
    daten.append((plan, reihen, tab))

(p_e, r_e, tab_e), (p_g, r_g, tab_g) = daten
print("Tabellen gleich:", all(np.array_equal(tab_e[n], tab_g[n]) for n in tab_e), [n for n in tab_e if not np.array_equal(tab_e[n], tab_g[n])])


def je_paar(plan):
    aus = {}
    p = collections.defaultdict(dict)
    for e in plan["einheiten"]:
        if "paar" in e:
            p[e["paar"]][e["rolle"]] = e
    for x in p.values():
        aus[(x["a"]["typ"], x["b"]["typ"])] = (x["a"], x["b"])
    return aus


pe, pg = je_paar(p_e), je_paar(p_g)
gemeinsam = sorted(set(pe) & set(pg))
print("Paare im Editor", len(pe), "im Gefecht", len(pg), "gemeinsam", len(gemeinsam))
t_e, t_g = r_e[0][0], r_g[0][0]
n = min(len(r_e), len(r_g))
print("Rahmen je Takt seit dem Start:", all(r_e[i][0] - t_e == i for i in range(n)), all(r_g[i][0] - t_g == i for i in range(n)), "Takte verglichen", n - 1)

je_takt = collections.Counter()
beispiele = []
gleiche_am_ende = 0
ungleich_paare = {}
for key in gemeinsam:
    (a_e, b_e), (a_g, b_g) = pe[key], pg[key]
    ungleich = []
    for i in range(1, n):
        s_e, s_g = r_e[i][1], r_g[i][1]
        w = (int(s_e["leben"][a_e["nr"]]), int(s_e["leben"][b_e["nr"]]))
        v = (int(s_g["leben"][a_g["nr"]]), int(s_g["leben"][b_g["nr"]]))
        lebt = s_e["typ"][a_e["nr"]] == a_e["typ"] and s_e["typ"][b_e["nr"]] == b_e["typ"] and s_g["typ"][a_g["nr"]] == a_g["typ"] and s_g["typ"][b_g["nr"]] == b_g["typ"]
        if not lebt:
            break
        if w != v:
            ungleich.append(i)
            je_takt[i] += 1
    if ungleich:
        ungleich_paare[key] = ungleich
    else:
        gleiche_am_ende += 1
print("Paare ohne jeden Unterschied:", gleiche_am_ende, "von", len(gemeinsam))
print("Paare mit Unterschied:", len(ungleich_paare))
print("Unterschied je Takt seit Start (Takt: Paare):", sorted(je_takt.items())[:12])
nur_erster = {p: u for p, u in ungleich_paare.items() if u != [1]}
print("Paare, die sich nach Takt 1 noch unterscheiden:", len(nur_erster))
for key, u in sorted(nur_erster.items())[:20]:
    (a_e, b_e), (a_g, b_g) = pe[key], pg[key]
    i = u[0] if u[0] != 1 else u[1]
    print("  ", key, "ab Takt", i, "Zahl", len(u), "Editor", int(r_e[i][1]["leben"][a_e["nr"]]), int(r_e[i][1]["leben"][b_e["nr"]]), "Gefecht", int(r_g[i][1]["leben"][a_g["nr"]]), int(r_g[i][1]["leben"][b_g["nr"]]))

# Sieht der erste Rahmen im Gefecht aus wie der Stand davor?
a, b = r_g[0][1], r_g[1][1]
print("Gefecht, Takt 0 gegen 1:", {f: int((a[f] != b[f]).sum()) for f in a}, "| Editor:", {f: int((r_e[0][1][f] != r_e[1][1][f]).sum()) for f in a})
