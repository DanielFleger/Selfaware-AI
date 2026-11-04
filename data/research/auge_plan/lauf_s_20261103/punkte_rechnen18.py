# -*- coding: utf-8 -*-
"""B-142: Lauf-F-Reste, die ohne neuen Lauf gehen: P116 Startgold, P140 Essensarten, P177 und P214 Tunnelsuche.

  PYTHONPATH="src;data/research/auge_plan/lauf_s_20261103" python data/research/auge_plan/lauf_s_20261103/punkte_rechnen18.py > data/research/auge_plan/lauf_s_20261103/punkte_rechnung18.txt
"""
import collections
import glob
import os

import punkte_lesen as pl
from selfaware.tools.analysis.auge_auswertung import Aufzeichnung

K = pl.karte
ST, SG, SS, _ = K.adresse("DAT_GameState", "playerDataArray[].startResources[]")
CU, _, _, _ = K.adresse("DAT_GameState", "playerDataArray[].currentResources[]")
FT = K.adresse("DAT_GameState", "playerDataArray[].foodTypesInStock")[0]


def bereiche(p):
    a = Aufzeichnung(p)
    return a.namen


def startgold(p):
    """P116: Rest startResources[15] und Konto currentResources[15] je Spieler, nur die Wechsel des Rests."""
    felder = {"rest": ("playerDataArray[].startResources[]", 60), "konto": ("playerDataArray[].currentResources[]", 60)}
    letzt, erste = {}, {}
    wechsel = collections.defaultdict(list)
    for t, w in pl.stand(p, "DAT_GameState", felder):
        for n in range(1, 9):
            r = int(w["rest"][n])
            k = int(w["konto"][n])
            if n not in erste:
                erste[n] = (t, r, k)
            if n in letzt and r != letzt[n]:
                wechsel[n].append((t, letzt[n], r, k))
            letzt[n] = r
    print("P116", os.path.basename(p), "erster Rahmen (Takt, Rest, Konto):", erste)
    for n, l in sorted(wechsel.items()):
        ab = collections.Counter(a - b for _, a, b, _ in l)
        print("   Spieler", n, "Wechsel", len(l), "Schritte", ab.most_common(4), "erste", l[:5], "letzte", l[-2:])
        ta = [b[0] - a[0] for a, b in zip(l, l[1:])]
        print("      Takte zwischen zwei Wechseln:", collections.Counter(ta).most_common(5))


def essen(p):
    """P140: foodTypesInStock gegen die Zahl der vier Felder davor (Versatz -20 bis -8) groesser 0."""
    felder = {"z": ("playerDataArray[].foodTypesInStock", 0)}
    for i, o in enumerate((-20, -16, -12, -8)):
        felder[f"e{i}"] = ("playerDataArray[].foodTypesInStock", o)
    c = collections.Counter()
    bei = {}
    for t, w in pl.stand(p, "DAT_GameState", felder):
        for n in range(1, 9):
            e = [int(w[f"e{i}"][n]) for i in range(4)]
            g = sum(1 for x in e if x > 0)
            z = int(w["z"][n])
            c[(z, g)] += 1
            bei.setdefault((z, g), (t, n, e))
    print("P140", os.path.basename(p), "(Feld, Zahl der Sorten ueber 0), Rahmen je Spieler:", sorted(c.items()))
    print("   Beispiele", sorted(bei.items())[:12])


def tunnel(p):
    plan = pl.plan_von(p)
    print("P214", os.path.basename(p), "Bereiche", bereiche(p))
    tc = K.adresse("DAT_BuildingsState", "buildings[].tunnelerCounter")
    letzt = None
    wechsel = collections.defaultdict(list)
    for t, w in pl.stand(p, "DAT_BuildingsState", {"c": "buildings[].tunnelerCounter", "typ": "buildings[].mapper" if False else "buildings[].tunnelerCounter"}):
        c = w["c"]
        if letzt is not None:
            for i in (c != letzt).nonzero()[0]:
                wechsel[int(i)].append((t, int(letzt[i]), int(c[i])))
        letzt = c.copy()
    for i, l in sorted(wechsel.items())[:12]:
        print("   Gebaeude", i, l[:14])
    print("   Gebaeude mit Wechsel:", len(wechsel), "Plan:", {k: v for k, v in plan.items() if k in ("von", "bis")})
    try:
        for f in ("ALG_TargetTile", "ALG_TargetX", "ALG_TargetY"):
            print("   ", f, K.adresse("DAT_PathFindingState", f))
        reihe = [(t, w["t"], w["x"], w["y"]) for t, w in pl.stand(p, "DAT_PathFindingState", {"t": "ALG_TargetTile", "x": "ALG_TargetX", "y": "ALG_TargetY"})]
        print("   Wechsel Ziel", pl.wechsel([(a, (b, c, d)) for a, b, c, d in reihe])[:40])
    except Exception as e:
        print("   Ziel nicht lesbar:", repr(e)[:120])


if __name__ == "__main__":
    L = pl.L
    letzte_b = sorted(glob.glob(os.path.join(L, "buendnis_k_*_danach.auge")), key=os.path.getmtime)[-1]
    kopf_b = letzte_b.replace("_danach", "")
    kopf_k = sorted(glob.glob(os.path.join(L, "lauf_k_*_234952.auge")))[-1]
    for p in (kopf_k, kopf_b):
        startgold(p)
    for p in (kopf_k, kopf_k.replace(".auge", "_danach.auge")):
        essen(p)
    for s in ("sonder6_g",):
        p = pl.neueste(s)
        if p:
            tunnel(p)
    for s in sorted(glob.glob(os.path.join(L, "lauf_k_*_234952_t*.auge")))[:0]:
        tunnel(s)
