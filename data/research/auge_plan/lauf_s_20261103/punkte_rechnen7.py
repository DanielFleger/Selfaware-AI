# -*- coding: utf-8 -*-
"""B-142 Lauf S, Nachlauf im Gefecht (sonder8_g, sonder9_g, lord2_g), dazu Sklave und Assassine an der Mauer aus sonder8. Die Urteile stehen in Punkte_Lauf_S.md.

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/punkte_rechnen7.py > data/research/auge_plan/lauf_s_20261103/punkte_rechnung7.txt
"""
import collections

import numpy as np

import punkte_lesen as pl
from selfaware.tools.analysis import auge_regeln as ar

U = {"da": "units[].logicalState", "typ": "units[].unitType", "b": "units[].owner", "mx": "units[].microXPosition", "my": "units[].microYPosition", "z": ("units[].logicalState", ar.ZUSTAND_ABSTAND)}
STEIN, GOLD = 4, 15


def einheiten(p, start, liste, felder=None):
    f = {**U, **(felder or {})}
    v = {e["nr"]: [] for e in liste}
    ende = {}
    for t, u in pl.stand(p, "DAT_UnitsState", f):
        for e in liste:
            n = e["nr"]
            if u["typ"][n] != e["typ"] or not u["da"][n]:
                if not v[n] or v[n][-1][1] != "weg":
                    v[n].append((t - start, "weg"))
                continue
            w = (int(u["z"][n]),) + tuple(int(u[k][n]) for k in (felder or {}))
            if not v[n] or v[n][-1][1:] != w:
                v[n].append((t - start, *w))
            ende[n] = (int(u["mx"][n]) // 8, int(u["my"][n]) // 8)
    return v, ende


def mauer_rest():
    p = pl.neueste("sonder8")
    plan = pl.plan_von(p)
    wer = [e for e in plan["einheiten"] if e.get("posten") == "mauer_art" and e["typ"] in (71, 73) and "nr" in e]
    v, ende = einheiten(p, plan["von"], wer, {"ziel": "units[].targetingType"})
    for e in wer:
        print("Mauer Art", e["typ"], "von", (e["x"], e["y"]), "Ende", ende.get(e["nr"]), "(Takt, Zustand, Anweisung)", v[e["nr"]][:7])


def nachladen():
    p = pl.neueste("sonder8_g")
    plan = pl.plan_von(p)
    start = plan["von"]
    print("sonder8_g Takte", plan["bis"] - start, "kein Platz", plan["kein_platz"], "nicht gesetzt", plan["nicht_gesetzt"])
    g = [e for e in plan["einheiten"] if e.get("posten") == "nachladen" and e["typ"] == 39]
    v, _ = einheiten(p, start, g, {"m": "units[].stoneAmmunition", "man": "units[].digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300"})
    for e in g:
        w = v[e["nr"]]
        auf = [(b[0], b[2] - a[2]) for a, b in zip(w, w[1:]) if len(a) > 2 and len(b) > 2 and b[2] > a[2]]
        print("Katapult Nr", e["nr"], "Anfang", w[0][2:], "letzte", w[-1][:4], "Nachladen (Takt, plus):", auf[:5], "Wechsel", len(w))
    stein = []
    for t, s in pl.stand(p, "DAT_GameState", {"s": ("playerDataArray[].currentResources[]", 4 * STEIN), "st": ("playerDataArray[].startResources[]", 4 * STEIN)}):
        stein.append((t - start, int(s["s"][1]), int(s["st"][1])))
    ab = [(a, b) for a, b in zip(stein, stein[1:]) if b[1] < a[1]]
    print("Stein (Takt, im Lager, noch Start): Anfang", stein[0], "Mitte", stein[len(stein) // 2], "Ende", stein[-1], "Rueckgaenge (Takt, von, auf):", [(b[0], a[1], b[1]) for a, b in ab][:8])
    h = ar.geschosse_lesen(p, pl.karte)
    for e in g:
        z = sorted(x["von"] - start for x in h if x["schuetze"] == e["nr"])
        print("   Schuesse Nr", e["nr"], len(z), z[:3], "...", z[-3:])


def oel():
    p = pl.neueste("sonder8_g")
    plan = pl.plan_von(p)
    start = plan["von"]
    h = ar.geschosse_lesen(p, pl.karte)
    for name in ("oel_aggressiv", "oel_defensiv", "oel_stehen"):
        wer = [e for e in plan["einheiten"] if e.get("posten") == name and "nr" in e]
        v, ende = einheiten(p, start, wer, {"ziel": "units[].targetingType", "d": "units[].closestEnemyMicroDistance"})
        ing = next(e for e in wer if e["rolle"] == "oel")
        fe = next(e for e in wer if e["rolle"] == "feind")
        zw = [(w[0], w[2]) for w in v[ing["nr"]] if len(w) > 2]
        z20 = next((t for t, a in zw if a == 20), None)
        nah = next((w[0] for w in v[ing["nr"]] if len(w) > 3 and w[3] <= 80), None)
        print(name, "Anweisung 20 ab", z20, "Feind unter 10 Felder ab", nah, "Ende Ing", ende.get(ing["nr"]), "Ende Feind", ende.get(fe["nr"]), "Anweisungen", pl.wechsel(zw)[:6])
    k = {x["art"]: 0 for x in h}
    for x in h:
        k[x["art"]] += 1
    print("Geschosse in sonder8_g:", k)


def grenze():
    p = pl.neueste("sonder8_g")
    plan = pl.plan_von(p)
    start = plan["von"]
    print("P324 gesetzt:", [(e["rolle"], e["typ"], e["x"], e["y"], e.get("abstand")) for e in plan["einheiten"] if e.get("posten") == "grenze"])
    nah = []
    for t, x in pl.stand(p, "DAT_TroopValueState", {"n": "attackInfo.playerTotalTroopValueOfTroopsNearKeep[]"}):
        w = int(x["n"][1])
        if not nah or nah[-1][1] != w:
            nah.append((t - start, w))
    print("   Wert Spieler 1 (Takt, Wert):", nah[:12])
    im = collections.Counter()
    for e in plan["einheiten"]:
        im[e["typ"]] += 1
    print("   Arten im Plan:", im.most_common(6))


def pech():
    p = pl.neueste("sonder9_g")
    plan = pl.plan_von(p)
    start = plan["von"]
    print("sonder9_g Takte", plan["bis"] - start, "kein Platz", plan["kein_platz"])
    wer = [e for e in plan["einheiten"] if e["rolle"] == "geher"]
    v, ende = einheiten(p, start, wer, {"c": "units[].counter", "f": "units[].field312_0x40a"})
    for e in wer:
        z = [w for w in v[e["nr"]] if len(w) > 3 and (w[2] or w[3])]
        print("   Geher von", (e["x"], e["y"]), "Ende", ende.get(e["nr"]), "counter oder field312 ungleich 0:", z[:5])


def lord():
    p = pl.neueste("lord2_g")
    if not p:
        print("lord2_g fehlt")
        return
    plan = pl.plan_von(p)
    start = plan["von"]
    print("lord2_g", {k: plan.get(k) for k in ("per_befehl", "gefallen", "tod", "ende_gemerkt", "gameover")}, "Takte", plan["bis"] - start)
    v = collections.defaultdict(list)
    for t, g in pl.stand(p, "DAT_GameState", {"tot": "playerDataArray[].lordKilledByPlayerID", "over": "mapAndTime.gameOver", "lebt": "mapAndTime.playerIsAlive[]", "gold": ("playerDataArray[].currentResources[]", 4 * GOLD)}):
        for k, w in (("gameOver", g["over"]), ("tot2", int(g["tot"][2])), ("lebt", tuple(int(x) for x in g["lebt"][:3])), ("gold1", int(g["gold"][1])), ("gold2", int(g["gold"][2]))):
            if not v[k] or v[k][-1][1] != w:
                v[k].append((t - start, w))
    for k, w in v.items():
        print("   ", k, w[:3], "...", w[-3:])
    le = []
    for t, u in pl.stand(p, "DAT_UnitsState", {**U, "l": "units[].health", "dy": "units[].dying", "kl": "units[].lastEncounteredEnemyPlayerID"}):
        m = (u["typ"] == 55) & (u["b"] == 2) & (u["da"] != 0)
        m[0] = False
        for i in np.nonzero(m)[0]:
            w = (int(u["dy"][i]), int(u["kl"][i]))
            if not le or le[-1][2:] != w:
                le.append((t - start, int(u["l"][i]), *w))
    print("    Lord (Takt, Leben, dying, letzter Gegner):", le[:6], "...", le[-2:])


if __name__ == "__main__":
    for f in (mauer_rest, nachladen, oel, grenze, pech, lord):
        try:
            f()
        except Exception as e:
            import traceback
            print("FEHLER", f.__name__, repr(e))
            traceback.print_exc(limit=2)
