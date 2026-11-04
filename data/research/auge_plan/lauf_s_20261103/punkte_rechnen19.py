# -*- coding: utf-8 -*-
"""B-142: P140 Warum steht foodTypesInStock auf 0, obwohl Essen da ist? P177 Was steht am Zielfeld der Tunnelsuche?

  PYTHONPATH="src;data/research/auge_plan/lauf_s_20261103" python data/research/auge_plan/lauf_s_20261103/punkte_rechnen19.py > data/research/auge_plan/lauf_s_20261103/punkte_rechnung19.txt
"""
import collections
import glob
import os

import punkte_lesen as pl

K = pl.karte
FT, _, SS, _ = K.adresse("DAT_GameState", "playerDataArray[].foodTypesInStock")
G = "DAT_GameState"


def namen():
    for o in (-0x803 * 4, -0x7b3 * 4, -20, -16, -12, -8):
        print("Versatz", o, "=", K.ziel(FT + SS + o))


def essen(p):
    """Die beiden Bedingungen des Codes je Spieler mitlesen: Ist eine davon 0, wenn das Feld 0 bleibt?"""
    felder = {"z": ("playerDataArray[].foodTypesInStock", 0), "a": ("playerDataArray[].foodTypesInStock", -0x803 * 4), "b": ("playerDataArray[].foodTypesInStock", -0x7b3 * 4)}
    for i, o in enumerate((-20, -16, -12, -8)):
        felder[f"e{i}"] = ("playerDataArray[].foodTypesInStock", o)
    c = collections.Counter()
    for t, w in pl.stand(p, G, felder):
        for n in range(1, 9):
            g = sum(1 for i in range(4) if int(w[f"e{i}"][n]) > 0)
            c[(int(w["z"][n]) == g, g > 0, int(w["a"][n]) > 0, int(w["b"][n]) > 0)] += 1
    print("P140", os.path.basename(p), "(Feld stimmt, Essen da, Bedingung a, Bedingung b): Rahmen", sorted(c.items()))


def tunnel(p):
    plan = pl.plan_von(p)
    print("sonder6_g Posten", [(k["posten"], k["x"], k["y"]) for k in plan["karte"]][:6], "von", plan["von"], "bis", plan["bis"])
    S = plan["von"]
    # Welche Gebaeude sind 22 und 24, und was liegt am Zielfeld?
    for t, w in pl.stand(p, "DAT_BuildingsState", {"typ": "buildings[].buildingType", "x": "buildings[].x", "y": "buildings[].y", "own": "buildings[].owner", "c": "buildings[].tunnelerCounter", "sx": "buildings[].someX", "sy": "buildings[].someY"}):
        if t in (1000, 1010, 2600):
            print("  Takt", t, {i: (int(w["typ"][i]), int(w["x"][i]), int(w["y"][i]), int(w["own"][i]), int(w["c"][i]), int(w["sx"][i]), int(w["sy"][i])) for i in (22, 24)})
    z = []
    for t, w in pl.stand(p, "DAT_PathFindingState", {"t": "ALG_TargetTile", "x": "ALG_TargetX", "y": "ALG_TargetY"}):
        z.append((t, w["t"], w["x"], w["y"]))
    print("  Rahmen Ziel", len(z), "um Takt 1000:", [q for q in z if 995 <= q[0] <= 1016])
    ziele = sorted({q[1] for q in z if q[1]})
    print("  Zielfelder", ziele)
    fe = {"logik": "LogicLayer[]", "mauer": "WallOwnerLayer[]", "bau": "BuildingLayer[]"}
    gesehen = {}
    n = 0
    try:
        for t, w in pl.stand(p, "DAT_TileMapState", fe):
            n += 1
            for f in ziele:
                s = (int(w["logik"][f]), int(w["mauer"][f]), int(w["bau"][f]))
                if gesehen.get(f, (None,))[-1] != s:
                    gesehen.setdefault(f, []).append((t, s))
        print("  Rahmen Karte", n)
        for f, l in gesehen.items():
            print("  Feld", f, "(Takt, (LogicLayer, WallOwnerLayer, BuildingLayer))", l[:8])
    except Exception as e:
        print("  Karte nicht lesbar", repr(e)[:200])


if __name__ == "__main__":
    namen()
    L = pl.L
    k = sorted(glob.glob(os.path.join(L, "lauf_k_*_234952.auge")))[-1]
    essen(k)
    p = pl.neueste("sonder6_g")
    tunnel(p)
