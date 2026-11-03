# -*- coding: utf-8 -*-
"""B-142 Lauf S, Einzelpunkte 2: Munition, Besatzung, Schaden am Gebaeude, Lord, Tore. Die Urteile stehen in Punkte_Lauf_S.md.

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/punkte_rechnen2.py > data/research/auge_plan/lauf_s_20261103/punkte_rechnung2.txt
"""
import collections
import glob
import json
import os
import struct

import numpy as np

import punkte_lesen as pl
from selfaware.tools.analysis import auge_regeln as ar

STEIN, GOLD = 4, 15  # currentResources[]


def p308_p342_p359_p360():
    """Munition je Katapult (39) und Trebuchet (40): Wechsel, Schuesse, Stein des Spielers beim Nachladen."""
    for s in ("beschuss", "beschuss_g", "besatzung", "geraete_weite", "belagerung", "sonder2_g"):
        p = pl.neueste(s)
        plan = pl.plan_von(p)
        wer = {e["nr"]: e for e in plan["einheiten"] if e["typ"] in (39, 40) and "nr" in e}
        if not wer:
            continue
        v = {n: [] for n in wer}
        stein = {1: [], 2: []}
        start = None
        for t, u in pl.stand(p, "DAT_UnitsState", {"m": "units[].stoneAmmunition", "typ": "units[].unitType", "man": "units[].digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300"}):
            start = t if start is None else start
            for n, e in wer.items():
                if u["typ"][n] == e["typ"]:
                    w = int(u["m"][n])
                    if not v[n] or v[n][-1][1] != w:
                        v[n].append((t - start, w))
        for t, g in pl.stand(p, "DAT_GameState", {"s": ("playerDataArray[].currentResources[]", 4 * STEIN)}):
            for sp in (1, 2):
                w = int(g["s"][sp])
                if not stein[sp] or stein[sp][-1][1] != w:
                    stein[sp].append((t - start, w))
        g = ar.geschosse_lesen(p, pl.karte)
        schuesse = collections.Counter((x["schuetze"], x["art"]) for x in g if x["schuetze"] in wer)
        print("P308/P359/P360", s, "Stein Spieler 1:", stein[1][:6], "Spieler 2:", stein[2][:4])
        gezeigt = 0
        for n, e in wer.items():
            w = v[n]
            if len(w) < 2:
                continue
            ab = sum(a[1] - b[1] for a, b in zip(w, w[1:]) if b[1] < a[1])
            auf = [(b[0], b[1] - a[1]) for a, b in zip(w, w[1:]) if b[1] > a[1]]
            sch = {k[1]: c for k, c in schuesse.items() if k[0] == n}
            print("   Art", e["typ"], "Nr", n, "mann", e.get("mann"), "Anfang", w[0][1], "Ende", w[-1][1], "Summe Verbrauch", ab, "Nachladen (Takt, plus)", auf[:4], "Schuesse", sch)
            gezeigt += 1
            if gezeigt >= 8:
                break


def p328_p337_p341_p344():
    d = json.load(open(os.path.join(pl.HIER, "besatzung.regeln.json"), encoding="utf-8"))
    z = d["zeilen"]
    print("P328/P337 besatzung Spalten:", list(z[0].keys()))
    for x in z[:14]:
        print("  ", json.dumps(x, ensure_ascii=False)[:230])
    for s, posten in (("sonder2", "schild"), ("sonder3", "turmgeraet")):
        p = pl.neueste(s)
        plan = pl.plan_von(p)
        wer = [e for e in plan["einheiten"] if e.get("posten") == posten and "nr" in e]
        v = {e["nr"]: [] for e in wer}
        start = None
        for t, u in pl.stand(p, "DAT_UnitsState", {"z": ("units[].logicalState", ar.ZUSTAND_ABSTAND), "typ": "units[].unitType", "man": "units[].digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300", "mx": "units[].microXPosition", "my": "units[].microYPosition"}):
            start = t if start is None else start
            for e in wer:
                n = e["nr"]
                if u["typ"][n] != e["typ"]:
                    if not v[n] or v[n][-1][1] != "weg":
                        v[n].append((t - start, "weg"))
                    continue
                w = (int(u["z"][n]), int(u["man"][n]) if e["typ"] in (58, 59, 60) else 0)
                if not v[n] or v[n][-1][1:] != w:
                    v[n].append((t - start, *w, int(u["mx"][n]) // 8, int(u["my"][n]) // 8))
        print("P341/P344", s, posten)
        for e in wer:
            print("   ", e["rolle"], "Art", e["typ"], "Nr", e["nr"], "Wechsel", len(v[e["nr"]]), v[e["nr"]][:9], "...", v[e["nr"]][-2:])


def p345_p357():
    for s in ("gebaeude_nah", "belagerung"):
        d = json.load(open(os.path.join(pl.HIER, f"{s}.regeln.json"), encoding="utf-8"))
        z = d["zeilen"]
        print("P345/P357", s, "Spalten", list(z[0].keys()), "Zeilen", len(z))
        for x in z:
            if x.get("wer") in (28, 59, 75, 76, 25, 26, 27, 71) or s == "belagerung":
                print("  ", json.dumps(x, ensure_ascii=False)[:210])


def p313_p362():
    for p in sorted(glob.glob(os.path.join(pl.L, "lauf_s_*_lord_g.auge")), key=os.path.getmtime)[-2:]:
        v = collections.defaultdict(list)
        start = None
        for t, g in pl.stand(p, "DAT_GameState", {"tot": "playerDataArray[].lordKilledByPlayerID", "over": "mapAndTime.gameOver", "lebt": "mapAndTime.playerIsAlive[]", "gold": ("playerDataArray[].currentResources[]", 4 * GOLD)}):
            start = t if start is None else start
            for k, w in (("gameOver", g["over"]), ("tot1", int(g["tot"][1])), ("tot2", int(g["tot"][2])), ("lebt", tuple(int(x) for x in g["lebt"][:4])), ("gold1", int(g["gold"][1])), ("gold2", int(g["gold"][2]))):
                if not v[k] or v[k][-1][1] != w:
                    v[k].append((t - start, w))
        print("P313/P362", os.path.basename(p), "Beginn", start)
        for k, w in v.items():
            print("   ", k, w[:5], "...", w[-2:] if len(w) > 5 else "")
        lords = {}
        for t, u in pl.stand(p, "DAT_UnitsState", {"typ": "units[].unitType", "da": "units[].logicalState", "le": "units[].health", "b": "units[].owner", "dy": "units[].dying"}):
            for i in np.nonzero((u["typ"] == 55) & (u["da"] != 0))[0]:
                if i == 0:
                    continue
                k = (int(i), int(u["b"][i]))
                w = (int(u["le"][i]) // 1000, int(u["dy"][i]))
                if k not in lords or lords[k][-1][1:] != w:
                    lords.setdefault(k, []).append((t - start, *w))
        print("    Lords (Takt, Leben in 1000, dying), letzte:", {k: v_[-3:] for k, v_ in lords.items()})


def p303_p304():
    from selfaware.game.ucp.bauen import NACH_TYP
    tore = {t for t, v in NACH_TYP.items() if "GATE" in v["laufzeitName"]}
    print("P303/P304 Torarten:", {t: NACH_TYP[t]["laufzeitName"] for t in tore})
    for s in ("gebaeude_nah", "belagerung", "sonder2", "sonder3", "sonder_g", "punkt"):
        p = pl.neueste(s)
        if not p:
            continue
        v = {}
        typ = {}
        start = None
        for t, b in pl.stand(p, "DAT_BuildingsState", {"typ": "buildings[].buildingType", "da": "buildings[].logicalState", "z": "buildings[].gateState", "z2": "buildings[].gateState2", "ti": "buildings[].gateCloseOpenTimer", "pl": "buildings[].pathLinkageRelated2", "x": "buildings[].x", "y": "buildings[].y", "o": "buildings[].owner"}):
            start = t if start is None else start
            for i in np.nonzero(np.isin(b["typ"], list(tore)) & (b["da"] != 0))[0]:
                k = int(i)
                typ[k] = (int(b["typ"][i]), int(b["x"][i]), int(b["y"][i]), int(b["o"][i]))
                w = (int(b["z"][i]), int(b["pl"][i]), int(b["ti"][i]) > 0)
                if k not in v or v[k][-1][1:] != w:
                    v.setdefault(k, []).append((t - start, *w))
        print("   ", s, "Tore", len(v), "mit Wechsel", sum(1 for x in v.values() if len(x) > 1))
        for k, w in list(v.items())[:8]:
            if len(w) > 1:
                print("      ", typ[k], "(Takt, gateState, pathLinkage, Timer>0):", w[:10])


def p322():
    """Mauer unter Schlaegen: HeightLayer und DamageLayer."""
    basis = json.load(open(os.path.join(pl.HIER, "feldnummern.json"), encoding="utf-8"))
    p = pl.neueste("sonder3")
    plan = pl.plan_von(p)
    k = next(z for z in plan["karte"] if z["posten"] == "tunnel")
    felder = [(k["x"] + 24, k["y"] + 9 + i) for i in range(6)]
    kacheln = [basis[y] + x for x, y in felder]
    v = {f: [] for f in felder}
    start = None
    for t, m in pl.stand(p, "DAT_TileMapState", {"h": "HeightLayer[]", "d": "DamageLayer[]"}, rein=False):
        start = t if start is None else start
        for f, z in zip(felder, kacheln):
            w = (int(m["h"][z]), int(m["d"][z]))
            if not v[f] or v[f][-1][1:] != w:
                v[f].append((t - start, *w))
    print("P322 sonder3 Mauerfelder (Takt, Hoehe, Schaden):")
    for f in felder:
        print("   ", f, len(v[f]), v[f][:9], "...", v[f][-2:])
    print("    Abstand der Schlaege der Taeter an der Mauer: Rollen", [(e["rolle"], e["nr"]) for e in plan["einheiten"] if e.get("posten") == "tunnel"][:8])


if __name__ == "__main__":
    for f in (p308_p342_p359_p360, p328_p337_p341_p344, p345_p357, p313_p362, p303_p304, p322):
        try:
            f()
        except Exception as e:
            import traceback
            print("FEHLER", f.__name__, repr(e))
            traceback.print_exc(limit=3)
