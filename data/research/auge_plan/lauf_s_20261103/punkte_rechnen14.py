# -*- coding: utf-8 -*-
'''B-142: Befehle aus Lauf F, die nur im Code standen (sonder19_g), und die Mauerluecke (sonder19). Urteile in Punkte_Lauf_F.md und Ergebnis_Lauf_S.md.

  PYTHONPATH="src;data/research/auge_plan/lauf_s_20261103" python data/research/auge_plan/lauf_s_20261103/punkte_rechnen14.py > data/research/auge_plan/lauf_s_20261103/punkte_rechnung14.txt
'''
import collections
import json
import os

import numpy as np

import punkte_lesen as pl
from selfaware.tools.analysis import auge_regeln as ar

U = {"da": "units[].logicalState", "typ": "units[].unitType", "b": "units[].owner", "mx": "units[].microXPosition", "my": "units[].microYPosition", "z": ("units[].logicalState", ar.ZUSTAND_ABSTAND)}
FN = json.load(open(os.path.join(os.path.dirname(pl.__file__), "feldnummern.json"), encoding="utf-8"))


def luecke():
    p = pl.neueste("sonder19")
    plan = pl.plan_von(p)
    S = plan["von"]
    o = plan["karte"][0]
    print("sonder19 Takte", plan["bis"] - S, "Mauer fehlt", plan["mauer_fehlt"], "Posten", (o["x"], o["y"]))
    ge = next(e for e in plan["einheiten"] if e["rolle"] == "geher")
    v = []
    for t, u in pl.stand(p, "DAT_UnitsState", {**U, "px": "units[].plannedDestinationX"}):
        w = (int(u["mx"][ge["nr"]]) // 8, int(u["my"][ge["nr"]]) // 8, int(u["px"][ge["nr"]]))
        if not v or v[-1][1:] != w:
            v.append((t - S, *w))
    print("   Geher (Takt, x, y, Ziel x):", v[:3], "...", v[-3:], "im Ring:", next((x for x in v if o["x"] + 11 <= x[1] <= o["x"] + 17 and o["y"] + 1 <= x[2] <= o["y"] + 7), None))
    h = []
    feld = FN[o["y"] + 4] + o["x"] + 10
    for t, m in pl.stand(p, "DAT_TileMapState", {"h": "HeightLayer[]", "d": "DamageLayer[]"}, rein=False):
        w = (int(m["h"][feld]), int(m["d"][feld]))
        if not h or h[-1][1:] != w:
            h.append((t - S, *w))
    print("   Mauerstueck (Takt, Hoehe, Schaden):", h[:3], "...", h[-3:])


def befehle():
    p = pl.neueste("sonder19_g")
    plan = pl.plan_von(p)
    S = plan["von"]
    print("sonder19_g Takte", plan["bis"] - S, "Mauer fehlt", plan["mauer_fehlt"], "wiederholt", plan["mauer_wiederholt"], "kein Platz", plan["kein_platz"], "nicht gesetzt", plan["nicht_gesetzt"])
    ort = {k["posten"]: k for k in plan["karte"]}
    z = collections.defaultdict(list)
    for t, g in pl.stand(p, "DAT_GameState", {"s1": "playerDataArray[].taxesSliderUI", "s2": "playerDataArray[].taxesSetting2", "sx": "playerDataArray[].barracksAssemblyPoints[].x", "lim": "playerDataArray[].armySizeLimit", "h": "playerDataArray[].armySize", "gold": ("playerDataArray[].currentResources[]", 60), "st": ("playerDataArray[].currentResources[]", 16), "ho": ("playerDataArray[].currentResources[]", 8)}):
        for k in ("s1", "s2", "sx", "lim", "h", "gold", "st", "ho"):
            w = int(g[k][1])
            if not z[k] or z[k][-1][1] != w:
                z[k].append((t - S, w))
    print("P160 taxesSliderUI", z["s1"][:4], "taxesSetting2", z["s2"][:4])
    print("P172 Sammelpunkt x", z["sx"][:4], "Soll", ort["sammel"]["x"] + 3)
    print("P154/155 armySizeLimit", z["lim"][:4], "armySize", z["h"][:10])
    print("    Gold", z["gold"][:10])
    print("    Stein", z["st"][:12], "Holz", z["ho"][:8])
    gb = {g["typ"]: g for g in plan["gebaeude"] if "nr" in g}
    v = collections.defaultdict(list)
    for t, b in pl.stand(p, "DAT_BuildingsState", {"le": "buildings[].currentHealth", "da": "buildings[].logicalState"}):
        for ty in (74, 1, 9):
            if ty in gb:
                w = (int(b["le"][gb[ty]["nr"]]), int(b["da"][gb[ty]["nr"]]))
                if not v[ty] or v[ty][-1][1:] != w:
                    v[ty].append((t - S, *w))
    print("P166 Turm (Takt, Leben, Zustand):", v[74][:6], "P205 Huette:", v[1][:4], "...", v[1][-2:])
    o = ort["abriss"]
    a = None
    for t, m in pl.stand(p, "DAT_TileMapState", {"h": "HeightLayer[]"}, rein=False):
        w = [int(m["h"][FN[o["y"] + 2] + o["x"] + i]) for i in range(1, 9)]
        if w != a:
            if t - S < 800 or a is None:
                print("P198 Mauer, Takt", t - S, w)
            a = w
    o = ort["mauer_knapp"]
    m_ = None
    for t, m in pl.stand(p, "DAT_TileMapState", {"h": "HeightLayer[]"}, rein=False):
        m_ = [int(m["h"][FN[o["y"] + 1] + o["x"] + i]) for i in range(0, 15)]
    print("P200 Mauer knapp, Hoehen am Ende:", m_)
    hu = collections.Counter()
    erste = None
    op = [e for e in plan["einheiten"] if e.get("posten") == "hunde4" and e["rolle"] == "opfer"]
    for t, u in pl.stand(p, "DAT_UnitsState", U):
        n = int(((u["da"] != 0) & (u["typ"] == 69)).sum()) if False else 0
        m = (u["da"] != 0) & (u["b"] == 1) & np.isin(u["typ"], [68, 69, 66, 67])
        m[0] = False
        if m.any():
            for ty in u["typ"][m]:
                hu[int(ty)] += 1
            erste = erste or t - S
    print("Hunde bei 4 Speertraegern: Spieler-1-Einheiten der Hunde-Arten je Rahmen", hu.most_common(4), "erste bei Takt", erste, "Opfer", len(op), "Kaefig", 99 in gb)
    wer = [e for e in plan["einheiten"] if e.get("posten") == "lager"]
    la = None
    for t, b in pl.stand(p, "DAT_BuildingsState", {"ty": "buildings[].buildingType", "o": "buildings[].owner", "le": "buildings[].currentHealth", "da": "buildings[].logicalState"}, jeder=1):
        m = np.nonzero((b["ty"] == 10) & (b["o"] == 2) & (b["da"] != 0))[0]
        w = int(b["le"][m[0]]) if len(m) else None
        if la is None:
            la = []
        if not la or la[-1][1] != w:
            la.append((t - S, w))
    print("Lager von Spieler 2 (Takt, Leben):", la[:6], "...", la[-2:], "Schwertkaempfer", [e["nr"] for e in wer])


if __name__ == "__main__":
    for f in (luecke, befehle):
        try:
            f()
        except Exception as e:
            import traceback
            print("FEHLER", f.__name__, repr(e))
            traceback.print_exc(limit=2)
