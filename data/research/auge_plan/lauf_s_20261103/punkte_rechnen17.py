# -*- coding: utf-8 -*-
"""B-142: Reste aus "Noch offen" von Lauf S, ohne neuen Lauf: eingestuerzter Gang, Kuh, Holztor, Schuesse ohne Verlust.

  PYTHONPATH="src;data/research/auge_plan/lauf_s_20261103" python data/research/auge_plan/lauf_s_20261103/punkte_rechnen17.py > data/research/auge_plan/lauf_s_20261103/punkte_rechnung17.txt
"""
import collections
import glob
import json
import os
import re

import numpy as np

import punkte_lesen as pl

FN = json.load(open(os.path.join(os.path.dirname(pl.__file__), "feldnummern.json"), encoding="utf-8"))
T = open(r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference\types.json", encoding="utf-8").read().replace("\\n", " ")


def gang():
    p = pl.neueste("sonder6_g")
    plan = pl.plan_von(p)
    S = plan["von"]
    print("Gang: Posten", [(k["posten"], k["x"], k["y"], k["breite"], k["hoehe"]) for k in plan["karte"]][:6])
    a = h = lg = None
    for t, m in pl.stand(p, "DAT_TileMapState", {"a": "PathConnectionLayer[]", "h": "HeightLayer[]", "l": "LogicLayer[]"}, rein=False):
        a, h, lg = np.array(m["a"]), np.array(m["h"]), np.array(m["l"])
        ende = t - S
    print("   letzter Rahmen Takt", ende)
    for k in plan["karte"][:2]:
        tief = []
        for j in range(k["hoehe"]):
            for i in range(k["breite"]):
                f = FN[k["y"] + j] + k["x"] + i
                if int(h[f]) < 8:
                    tief.append((k["x"] + i, k["y"] + j, int(h[f]), int(a[f]), hex(int(lg[f]) & 0xffffffff)))
        print("  ", k["posten"], "Felder unter Bodenhoehe (x, y, Hoehe, Flaeche, Logik): Anzahl", len(tief), "Flaechen", collections.Counter(z[3] for z in tief).most_common(4), "Beispiele", tief[:4])


def kuh():
    for sz in ("sonder5_g", "sonder4_g", "sonder5", "sonder3_g"):
        p = pl.neueste(sz)
        plan = pl.plan_von(p)
        if not any("kuh" in str(k.get("posten", "")).lower() for k in plan.get("karte", [])):
            continue
        S = plan["von"]
        print("Kuh in", sz)
        c = []
        for t, g in pl.stand(p, "DAT_GameState", {"c": "playerDataArray[].counter"}):
            if not c or c[-1][1] != int(g["c"][1]):
                c.append((t - S, int(g["c"][1])))
        print("   Kuh-Zaehler Spieler 1 (Takt, Wert):", c[:10])
        t_ = [e for e in plan["einheiten"] if e.get("rolle") == "geraet"]
        v = []
        for t, u in pl.stand(p, "DAT_UnitsState", {"z": "units[].targetingType", "m": "units[].stoneAmmunition"}):
            for e in t_[:1]:
                w = (int(u["z"][e["nr"]]), int(u["m"][e["nr"]]))
                if not v or v[-1][1:] != w:
                    v.append((t - S, *w))
        print("   Geraet (Takt, Anweisung, Munition):", v[:12])
        return
    print("Kuh: Szene nicht gefunden")


def holztor():
    print("Tore im Typ-Verzeichnis:", sorted({(n, int(v)) for n, v in re.findall(r"(BT_[A-Z0-9_]*(?:GATE|WOOD|DRAWBRIDGE)[A-Z0-9_]*): (\d+)", T)}, key=lambda z: z[1])[:12])
    print("Mapper:", sorted({(n, int(v)) for n, v in re.findall(r"(M_MAPPER_[A-Z0-9_]*(?:GATE|DRAWBRIDGE)[A-Z0-9_]*): (\d+)", T)}, key=lambda z: z[1])[:10])


def schuesse():
    g = sorted(glob.glob(os.path.join(os.path.dirname(pl.__file__), "*geschosse*")))
    print("Dateien:", [os.path.basename(x) for x in g][:6])
    f = os.path.join(pl.L, "*beschuss_g.geschosse.json")
    z = sorted(glob.glob(f))
    if not z:
        z = sorted(glob.glob(os.path.join(pl.L, "*beschuss*.geschosse.json")))
    if not z:
        print("keine geschosse.json")
        return
    d = json.load(open(z[-1], encoding="utf-8"))
    print("Datei", os.path.basename(z[-1]), "Felder", list(d[0].keys())[:14] if isinstance(d, list) else list(d.keys())[:8], "Anzahl", len(d))


def holztor_lauf():
    p = pl.neueste("sonder22")
    if not p:
        print("sonder22 fehlt")
        return
    plan = pl.plan_von(p)
    S = plan["von"]
    print("sonder22 Takte", plan["bis"] - S, "nicht gesetzt", plan["nicht_gesetzt"], [(g["typ"], g.get("nr"), g["x"], g["y"]) for g in plan["gebaeude"]])
    g = next((x for x in plan["gebaeude"] if "nr" in x), None)
    if not g:
        return
    v = []
    for t, b in pl.stand(p, "DAT_BuildingsState", {"le": "buildings[].currentHealth", "ty": "buildings[].buildingType", "w": "buildings[].widthOrHeight"}):
        w = (int(b["le"][g["nr"]]), int(b["ty"][g["nr"]]), int(b["w"][g["nr"]]))
        if not v or v[-1][1:] != w:
            v.append((t - S, *w))
    print("   Holztor (Takt, Leben, Art, Groesse):", v[:6], "...", v[-2:], "Verlust je Wechsel:", collections.Counter(a[1] - c[1] for a, c in zip(v, v[1:])).most_common(3))


def schuss_tabelle():
    z = sorted(glob.glob(os.path.join(pl.L, "*beschuss_g.auge.geschosse.json")))[-1]
    d = json.load(open(z, encoding="utf-8"))
    for art, w in d.items():
        print("  ", art, {k: w[k] for k in ("flogen", "gelandet", "traf", "verfehlt", "ziel_weg") if k in w})


if __name__ == "__main__":
    for f in (gang, kuh, holztor, schuesse, schuss_tabelle, holztor_lauf):
        try:
            f()
        except Exception as e:
            import traceback
            print("FEHLER", f.__name__, repr(e))
            traceback.print_exc(limit=2)
