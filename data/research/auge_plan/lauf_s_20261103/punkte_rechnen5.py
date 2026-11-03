# -*- coding: utf-8 -*-
"""B-142 Lauf S, Einzelpunkte 5: der Rest. Die Urteile stehen in Punkte_Lauf_S.md.

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/punkte_rechnen5.py > data/research/auge_plan/lauf_s_20261103/punkte_rechnung5.txt
"""
import collections
import json
import os

import numpy as np

import punkte_lesen as pl
from selfaware.tools.analysis import auge_regeln as ar

U = {"da": "units[].logicalState", "typ": "units[].unitType", "b": "units[].owner", "mx": "units[].microXPosition", "my": "units[].microYPosition", "z": ("units[].logicalState", ar.ZUSTAND_ABSTAND)}


def p351():
    """Hinsetzen bis Abstand 400: Wie nah an 400?"""
    p = pl.neueste("sonder6_g")
    c = collections.Counter()
    alt = {}
    for t, u in pl.stand(p, "DAT_UnitsState", {**U, "d": "units[].closestEnemyMicroDistance"}):
        m = (u["typ"] == 22) & (u["da"] != 0)
        m[0] = False
        for i in np.nonzero(m)[0]:
            i = int(i)
            z, d = int(u["z"][i]), int(u["d"][i])
            if alt.get(i) not in (11, None) and z == 11:
                c[d // 10 * 10] += 1
            alt[i] = z
    print("P351 Abstand beim Hinsetzen, auf 10 abgerundet:", sorted(c.items()))


def p335():
    p = pl.neueste("sonder3")
    plan = pl.plan_von(p)
    trag = [e for e in plan["einheiten"] if e["rolle"] == "leiter" and "nr" in e]
    v = {e["nr"]: [] for e in trag}
    start = None
    for t, u in pl.stand(p, "DAT_UnitsState", {**U}):
        start = t if start is None else start
        for e in trag:
            w = int(u["z"][e["nr"]]) if u["typ"][e["nr"]] == 29 else "weg"
            if not v[e["nr"]] or v[e["nr"]][-1][1] != w:
                v[e["nr"]].append((t - start, w))
    print("P335 Leitertraeger, Zustaende:", {n: w[:8] for n, w in v.items()})


def p371():
    p = pl.neueste("schlacht_araber")
    plan = pl.plan_von(p)
    wer = [e for e in plan["einheiten"] if e["typ"] == 74 and "nr" in e][:3]
    v = {e["nr"]: [] for e in wer}
    start = None
    for t, u in pl.stand(p, "DAT_UnitsState", {**U}):
        start = t if start is None else start
        for e in wer:
            w = int(u["z"][e["nr"]]) if u["typ"][e["nr"]] == 74 else "weg"
            o = (int(u["mx"][e["nr"]]) // 8, int(u["my"][e["nr"]]) // 8)
            if not v[e["nr"]] or v[e["nr"]][-1][1] != w:
                v[e["nr"]].append((t - start, w, o))
    print("P371 schlacht_araber (Takt, Zustand, Ort):", {n: w[:7] for n, w in v.items()})


def p316():
    """Wer stirbt im Gefecht und aendert die Todeskarte? Brennende haben Besitzer 0."""
    for s in ("beschuss_g", "nahkampf_g"):
        p = pl.neueste(s)
        tod = collections.Counter()
        alt = {}
        for t, u in pl.stand(p, "DAT_UnitsState", {**U, "dy": "units[].dying"}):
            for i in np.nonzero((u["dy"] != 0) & (u["da"] != 0))[0]:
                i = int(i)
                if i and i not in alt:
                    alt[i] = 1
                    tod[(int(u["typ"][i]), int(u["b"][i]))] += 1
        print("P316", s, "beim ersten Sterben (Art, Besitzer):", tod.most_common(8), "Summe Besitzer 0:", sum(n for k, n in tod.items() if k[1] == 0))


def p342():
    p = pl.neueste("besatzung")
    plan = pl.plan_von(p)
    g = ar.geschosse_lesen(p, pl.karte)
    k = next(e for e in plan["einheiten"] if e["typ"] == 39 and e.get("mann") == 2 and e.get("rolle") == "geraet")
    zeiten = sorted(x["von"] for x in g if x["schuetze"] == k["nr"])
    print("P342 Katapult Nr", k["nr"], "Schuesse", len(zeiten), "letzter bei", zeiten[-1] - plan["von"], "Lauf bis", plan["bis"] - plan["von"])


def p306_p370_p320():
    d = json.load(open(os.path.join(pl.HIER, "punkte_lauf_s.json"), encoding="utf-8"))["punkte"]
    for p in d:
        if p["nr"] in ("P306", "P320", "P331", "P370", "P302", "P317"):
            print(p["nr"], p["urteil"], [(b["global"], b["feld"], b["aenderungen"], b["min"], b["max"]) for b in p.get("belege", [])][:3])
    print("Stand der Punkte:", json.load(open(os.path.join(pl.HIER, "punkte_lauf_s.json"), encoding="utf-8"))["zaehlung"])


def p304():
    """Alle Tore: Takte von pathLinkage 1 auf 2 und alle gesehenen gateState."""
    from selfaware.game.ucp.bauen import NACH_TYP
    tore = {t for t, v in NACH_TYP.items() if "GATE" in v["laufzeitName"]}
    for s in ("gebaeude_nah", "belagerung"):
        p = pl.neueste(s)
        eins, dauer, zustand = {}, [], collections.Counter()
        alt = {}
        for t, b in pl.stand(p, "DAT_BuildingsState", {"typ": "buildings[].buildingType", "da": "buildings[].logicalState", "pl": "buildings[].pathLinkageRelated2", "z": "buildings[].gateState"}):
            for i in np.nonzero(np.isin(b["typ"], list(tore)) & (b["da"] != 0))[0]:
                i = int(i)
                w = int(b["pl"][i])
                zustand[int(b["z"][i])] += 1
                if w == 1 and alt.get(i) == 0:
                    eins[i] = t
                if w == 2 and alt.get(i) == 1 and i in eins:
                    dauer.append(t - eins[i])
                alt[i] = w
        print("P304", s, "Tore", len(alt), "Takte von 1 auf 2:", sorted(dauer), "gateState gesehen:", sorted(zustand.items()))


if __name__ == "__main__":
    for f in (p351, p335, p371, p316, p342, p306_p370_p320, p304):
        try:
            f()
        except Exception as e:
            import traceback
            print("FEHLER", f.__name__, repr(e))
            traceback.print_exc(limit=2)
