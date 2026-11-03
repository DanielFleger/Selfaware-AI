# -*- coding: utf-8 -*-
"""B-142 Lauf S, Einzelpunkte 1: Giftwolke, Feuer, Tunnel, Klettern, Hunde, Brennender Mann. Die Urteile stehen in Punkte_Lauf_S.md.

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/punkte_rechnen1.py > data/research/auge_plan/lauf_s_20261103/punkte_rechnung1.txt
"""
import collections

import numpy as np

import punkte_lesen as pl

E = {"art": "entityArray[].entityType", "da": "entityArray[].logicalState", "uid": "entityArray[].uid"}
EINHEIT = {"da": "units[].logicalState", "typ": "units[].unitType", "besitzer": "units[].owner"}


def p297():
    """Giftwolke: Takte bis logicalState 3."""
    p = pl.neueste("sonder2_g")
    w = {}
    start = None
    for t, e in pl.stand(p, "DAT_EntityState", {**E, "rng": "entityArray[].rng_2"}):
        start = t if start is None else start
        for i in np.nonzero((e["art"] == 22) & (e["da"] != 0))[0]:
            k = (int(i), int(e["uid"][i]))
            z = w.setdefault(k, {"von": t, "rng0": int(e["rng"][i]), "drei": None, "bis": t})
            z["bis"], z["rng1"] = t, int(e["rng"][i])
            if e["da"][i] == 3 and z["drei"] is None:
                z["drei"] = t
    print("P297 Giftwolken", len(w))
    for k, z in sorted(w.items(), key=lambda x: x[1]["von"]):
        print("  Platz", k[0], "Beginn", z["von"] - start, "logicalState 3 nach", (z["drei"] - z["von"]) if z["drei"] else None, "zuletzt nach", z["bis"] - z["von"], "rng_2 Anfang", z["rng0"], "Ende", z["rng1"])


def p298_p301():
    """Feuer an Huetten (sonder1, Posten feuer)."""
    p = pl.neueste("sonder1")
    plan = pl.plan_von(p)
    huetten = [g for g in plan["gebaeude"] if g.get("posten") == "feuer" and "nr" in g]
    nr = [g["nr"] for g in huetten]
    gv = {g["nr"]: [] for g in huetten}
    start = None
    for t, b in pl.stand(p, "DAT_BuildingsState", {"dauer": "buildings[].fireDuration", "ab": "buildings[].cooldownTimer", "leben": "buildings[].currentHealth"}):
        start = t if start is None else start
        for n in nr:
            w = (int(b["dauer"][n]), int(b["ab"][n]) > 0)
            if not gv[n] or gv[n][-1][1:] != w:
                gv[n].append((t, *w))
    print("P298/P301 Huetten: (Takt, fireDuration, cooldownTimer>0), nur die ersten und letzten Wechsel")
    for g in huetten:
        v = gv[g["nr"]]
        print("  Huette", g["nr"], (g["x"], g["y"]), "Wechsel", len(v), [(a - start, d, c) for a, d, c in v[:4]], "...", [(a - start, d, c) for a, d, c in v[-3:]])
    print("  P301: Takte mit fireDuration>0 und cooldownTimer>0:", sum(1 for g in huetten for a, d, c in gv[g["nr"]] if d > 0 and c))
    dauer = {}
    for t, b in pl.stand(p, "DAT_BuildingsState", {"dauer": "buildings[].fireDuration"}):
        dauer[t] = {n: int(b["dauer"][n]) for n in nr}
    paare = collections.Counter()
    neu = collections.Counter()
    faelle = []
    alt = {}
    for t, e in pl.stand(p, "DAT_EntityState", {**E, "tr": "entityArray[].someTracker", "st": "entityArray[].fireParameter_0xb6", "z": "entityArray[].someCounter_OR_hitGround", "mx": "entityArray[].microX", "my": "entityArray[].microY"}):
        if t not in dauer:
            continue
        ist = {}
        for i in np.nonzero((e["art"] == 9) & (e["da"] != 0))[0]:
            x, y = int(e["mx"][i]) // 8, int(e["my"][i]) // 8
            h = next((g for g in huetten if g["x"] <= x < g["x"] + g["groesse"] and g["y"] <= y < g["y"] + g["groesse"]), None)
            k = (int(i), int(e["uid"][i]))
            ist[k] = (x, y, int(e["st"][i]))
            if h is not None:
                d = dauer[t][h["nr"]]
                paare[(int(e["tr"][i]), d != 0)] += 1
            if k not in alt:
                nah = [v[2] for v in alt.values() if max(abs(v[0] - x), abs(v[1] - y)) <= 1]
                neu[(int(e["st"][i]), max(nah) if nah else None)] += 1
        alt = ist
    print("P298 je Rahmen (someTracker, fireDuration ungleich 0): Rahmen", sorted(paare.items(), key=lambda x: str(x[0])))
    print("P298 neue Feuer (Stufe, hoechste Stufe eines Nachbarn 1 Feld weit):", sorted(neu.items(), key=lambda x: str(x[0])))


def p340():
    """Brennender Mann, Art 2: Besitzer und dying."""
    for s in ("sonder2_g", "sonder1", "sonder5_g", "beschuss"):
        p = pl.neueste(s)
        z = {}
        for t, u in pl.stand(p, "DAT_UnitsState", {**EINHEIT, "dying": "units[].dying", "uid": "units[].uid"}):
            for i in np.nonzero((u["typ"] == 2) & (u["da"] != 0))[0]:
                if i == 0:
                    continue
                k = (int(i), int(u["uid"][i]))
                w = z.setdefault(k, {"von": t, "bis": t, "besitzer": collections.Counter(), "dying": collections.Counter()})
                w["bis"] = t
                w["besitzer"][int(u["besitzer"][i])] += 1
                w["dying"][int(u["dying"][i])] += 1
        print("P340", s, "Brennende:", len(z), "Besitzer", sum((w["besitzer"] for w in z.values()), collections.Counter()), "dying", sum((w["dying"] for w in z.values()), collections.Counter()), "Dauer", sorted(w["bis"] - w["von"] for w in z.values())[:8])


def p348():
    """Klettern: climbingState und field219 eines Steigers."""
    for s, rolle in (("sonder3", "steiger"), ("sonder5", "laeufer")):
        p = pl.neueste(s)
        plan = pl.plan_von(p)
        wer = [e["nr"] for e in plan["einheiten"] if e["rolle"] == rolle and "nr" in e]
        v = {n: [] for n in wer}
        h = {n: 0 for n in wer}
        start = None
        for t, u in pl.stand(p, "DAT_UnitsState", {"st": "units[].climbingState", "f": "units[].field219_0x35c"}):
            start = t if start is None else start
            for n in wer:
                w = int(u["st"][n])
                h[n] = max(h[n], int(u["f"][n]))
                if not v[n] or v[n][-1][1] != w:
                    v[n].append((t - start, w))
        print("P348", s, {n: {"climbingState": v[n], "field219 hoechstens": h[n]} for n in wer[:3]})


def p299_p349():
    """Tunnelgraeber: tunnelerFrame je Takt in Zustand 3 und 4, Schaden am Ziel."""
    for s in ("sonder6_g", "sonder7_g"):
        p = pl.neueste(s)
        plan = pl.plan_von(p)
        wer = [e for e in plan["einheiten"] if e["typ"] == 5 and e["rolle"] == "taeter" and "nr" in e]
        for e in wer:
            frames3, frames4, flag, sprung = [], [], [], []
            start = None
            letzter = None
            for t, u in pl.stand(p, "DAT_UnitsState", {"f": "units[].tunnelerFrame", "z": "units[].logicalState", "typ": "units[].unitType", "g": "units[].tunnelerFinishedDigging"}):
                start = t if start is None else start
                if u["typ"][e["nr"]] != 5:
                    break
                flag.append((t - start, int(u["g"][e["nr"]])))
                letzter = (t - start, int(u["f"][e["nr"]]))
                frames3.append(letzter)
            fr = pl.wechsel(frames3)
            hoch = max(f for _, f in fr)
            spitzen = [f for (_, f), (_, g) in zip(fr, fr[1:]) if g == 0 and f > 0]
            print("P349", s, e["posten"], "Nr", e["nr"], "hoechster Frame", hoch, "letzter", letzter, "Spitzen vor dem Sprung auf 0:", collections.Counter(spitzen).most_common(4), "Letzte Frames", fr[-5:], "Flag-Wechsel", pl.wechsel(flag)[-3:])


def p315_p364():
    """Pruefung der Hunde: Zahl und Wert der Feinde. Die letzten drei Laeufe sonder3_g."""
    import glob
    import os
    for p in sorted(glob.glob(os.path.join(pl.L, "lauf_s_*_sonder3_g.auge")), key=os.path.getmtime)[-2:]:
        z = collections.Counter()
        erster = {}
        for t, a in pl.stand(p, "DAT_PathFindingState", {"w": "ALGO_TotalTroopValue", "n": "ALGO_TotalTroopCount"}):
            k = (a["w"], a["n"])
            z[k] += 1
            erster.setdefault(k, t)
        print("P315", os.path.basename(p), "(Wert, Anzahl): Rahmen", z.most_common(10), "erster Takt", erster)


if __name__ == "__main__":
    for f in (p297, p298_p301, p340, p348, p299_p349, p315_p364):
        try:
            f()
        except Exception as e:
            import traceback
            print("FEHLER", f.__name__, repr(e))
            traceback.print_exc(limit=2)
