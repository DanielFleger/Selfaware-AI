# -*- coding: utf-8 -*-
"""B-142: P093 Stand der Weizenfarm beim Wechsel auf 8 gegen die Felder. P122 Wann kommt der Stein am Stapel an, und was passiert bei 47?

  PYTHONPATH="src;data/research/auge_plan/lauf_s_20261103" python data/research/auge_plan/lauf_s_20261103/punkte_rechnen26.py > data/research/auge_plan/lauf_s_20261103/punkte_rechnung26.txt
"""
import collections
import os

import numpy as np

import punkte_lesen as pl

F = os.path.join(pl.L, "lauf_f_20261102_214240.auge")
B, TM = "DAT_BuildingsState", "DAT_TileMapState"
FARM, BRUCH, STAPEL = 67, 55, 56
BIS = 60000


def weizen():
    wechsel = []
    alt = None
    for t, w in pl.stand(F, B, {"s": "buildings[].wheatGrowStateRelated"}):
        v = int(w["s"][FARM])
        if alt is not None and v != alt:
            wechsel.append((t, alt, v))
        alt = v
        if t > BIS:
            break
    karten = []
    for t, w in pl.stand(F, TM, {"bau": "BuildingLayer[]", "sch": "DamageLayer[]"}):
        if t > BIS:
            break
        fe = (np.asarray(w["bau"]) == FARM).nonzero()[0]
        s = np.asarray(w["sch"])[fe].astype(np.uint8)
        karten.append((t, int((s == 121).sum())))
    z = np.array([k[0] for k in karten])
    auf8 = []
    for t, a, b in wechsel:
        if b == 8:
            i = int(np.searchsorted(z, t, side="right")) - 1
            j = min(i + 1, len(karten) - 1)
            auf8.append((t, a, karten[i], karten[j]))
    print("P093 Wechsel auf 8 (Takt, von, (Takt Karte, Felder auf 121 davor), (danach)):", auf8[:16])
    print("   Felder auf 121 davor, Haeufigkeit:", collections.Counter(q[2][1] for q in auf8).most_common(), "danach:", collections.Counter(q[3][1] for q in auf8).most_common())


def stein():
    a, wechsel, stapel = None, [], []
    zustand = []
    stein_alt, s_alt = None, None
    for t, w in pl.stand(F, B, {"st": "buildings[].resourceStone", "f": "buildings[].killingPitField", "s": "buildings[].state"}):
        f = (int(w["f"][BRUCH]) >> 16) & 0xffff
        if a == 1 and f == 0:
            wechsel.append(t)
        a = f
        v = int(w["st"][STAPEL])
        if stein_alt is not None and v != stein_alt:
            stapel.append((t, v - stein_alt, v))
        stein_alt = v
        sb = int(w["s"][BRUCH])
        if sb != s_alt:
            zustand.append((t, sb, v))
        s_alt = sb
    w = np.array(wechsel)
    ab = []
    for t, d, v in stapel:
        if d > 0:
            i = int(np.searchsorted(w, t, side="right")) - 1
            if i >= 0:
                ab.append(t - int(w[i]))
    print("P122 Steine am Stapel", len([s for s in stapel if s[1] > 0]), "Wechsel 1 auf 0:", len(wechsel), "Abstand vom letzten Wechsel bis zum Stein, Takte: kleinster, groesster:", (min(ab), max(ab)) if ab else None, "haeufig:", collections.Counter(x // 10 * 10 for x in ab).most_common(6))
    voll = [q for q in stapel if q[2] >= 47]
    print("   Stapel erreicht 47:", voll[:5])
    if voll:
        t0 = voll[0][0]
        print("   Zustaende des Bruchs danach (Takt, Zustand, Stapel):", [q for q in zustand if q[0] >= t0][:12])
        nach = [q for q in stapel if q[0] > t0]
        print("   Aenderungen am Stapel danach:", nach[:10])


weizen()
stein()
