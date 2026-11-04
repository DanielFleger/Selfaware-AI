# -*- coding: utf-8 -*-
"""B-142 Lauf S, zweiter Nachlauf im Gefecht (sonder10_g, sonder11_g, sonder15_g, sonder16_g). Die Urteile stehen in Punkte_Lauf_S.md.

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/punkte_rechnen12.py > data/research/auge_plan/lauf_s_20261103/punkte_rechnung12.txt
"""
import collections
import json
import os

import numpy as np

import punkte_lesen as pl
from selfaware.tools.analysis import auge_regeln as ar

U = {"da": "units[].logicalState", "typ": "units[].unitType", "b": "units[].owner", "mx": "units[].microXPosition", "my": "units[].microYPosition", "z": ("units[].logicalState", ar.ZUSTAND_ABSTAND)}
STEIN, GOLD = 4, 15


def laden(szene):
    p = pl.neueste(szene)
    plan = pl.plan_von(p)
    wer = collections.defaultdict(list)
    for e in plan["einheiten"]:
        if "nr" in e:
            wer[e.get("posten")].append(e)
    gb = collections.defaultdict(list)
    for g in plan["gebaeude"]:
        if "nr" in g:
            gb[g.get("posten")].append(g)
    return p, plan, wer, gb, plan["von"]


def kopf(szene, p, plan):
    print("=====", szene, "Takte", plan["bis"] - plan["von"], "Mauer fehlt", plan.get("mauer_fehlt"), "wiederholt", plan.get("mauer_wiederholt"), "kein Platz", plan["kein_platz"], "nicht gesetzt", plan["nicht_gesetzt"])
    if os.path.exists(p + ".regeln.json"):
        z = json.load(open(p + ".regeln.json", encoding="utf-8"))["zeilen"]
        print("fremd:", {r["posten"]: r["fremd"] for r in z if r["fremd"]["schlaeger"] or r["fremd"]["geschosse"]})


def angst():
    p, plan, wer, gb, S = laden("sonder10_g")
    kopf("sonder10_g", p, plan)
    a = next(e for e in wer["angst"] if e["rolle"] == "taeter")
    b = next(e for e in wer["angst"] if e["rolle"] == "opfer")
    print("P332 Gebaeude:", collections.Counter((g["typ"], g["spieler"]) for g in plan["gebaeude"] if "nr" in g))
    st = []
    for t, g in pl.stand(p, "DAT_GameState", {"f": "playerDataArray[].fearFactorLevel", "gut": "playerDataArray[].goodStuffCount", "boese": "playerDataArray[].badStuffCount"}):
        w = (int(g["f"][1]), int(g["f"][2]), int(g["gut"][1]), int(g["boese"][1]), int(g["gut"][2]), int(g["boese"][2]))
        if not st or st[-1][1:] != w:
            st.append((t - S, *w))
    print("   (Takt, Stufe 1, Stufe 2, gut 1, schlecht 1, gut 2, schlecht 2):", st[:10], "...", st[-2:])
    le = {a["nr"]: [], b["nr"]: []}
    for t, u in pl.stand(p, "DAT_UnitsState", {**U, "l": "units[].health"}):
        for n in le:
            w = int(u["l"][n]) if u["typ"][n] == 27 and u["da"][n] else None
            if not le[n] or le[n][-1][1] != w:
                le[n].append((t - S, w))
    for n, w in le.items():
        sch = [x[1] - y[1] for x, y in zip(w, w[1:]) if x[1] is not None and y[1] is not None]
        print("   ", "Spieler 1 traf" if n == b["nr"] else "Spieler 2 traf", "Schaden je Treffer:", collections.Counter(sch).most_common(4), "Treffer", len(sch), "Folge", w[:5], "...", w[-2:])
    print("P305/P306 vorher:", {k: [x for x in v if x] for k, v in plan["verluste"]["vorher"].items()})
    print("   nachher:", {k: [(i, x) for i, x in enumerate(v) if x] for k, v in plan["verluste"]["nachher"].items()})
    print("   Verlust-Paar:", [(e["rolle"], e["typ"], e["spieler"]) for e in wer["verlust"]])
    z = {}
    for t, g in pl.stand(p, "DAT_GameState", {"tl": "playerDataArray[].troopsLost", "wl": "playerDataArray[].weightedLosses", "le": "playerDataArray[].lastlastEncounteredEnemyPlayerID"}):
        for sp in (1, 2):
            w = (int(g["tl"][sp]), int(g["wl"][sp]), int(g["le"][sp]))
            z.setdefault(sp, [])
            if not z[sp] or z[sp][-1][1:] != w:
                z[sp].append((t - S, *w))
    print("   (Takt, troopsLost, weightedLosses, letzter Gegner) Spieler 1:", z[1][:6], "...", z[1][-2:], "Spieler 2:", z[2][:6], "...", z[2][-2:])


def loeschen():
    p, plan, wer, gb, S = laden("sonder10_g")
    h = next((g for g in gb["loeschen"] if g["typ"] == 1), None)
    br = next((g for g in gb["loeschen"] if g["typ"] == 27), None)
    print("Loeschen: Huette", h and (h["nr"], h["x"], h["y"]), "Brunnen", br and (br["nr"], br["x"], br["y"]))
    if not h:
        return
    v = []
    for t, b in pl.stand(p, "DAT_BuildingsState", {"f": "buildings[].fireDuration", "le": "buildings[].currentHealth", "da": "buildings[].logicalState"}):
        w = (int(b["da"][h["nr"]]), int(b["f"][h["nr"]]) > 0, int(b["le"][h["nr"]]))
        if not v or v[-1][1:3] != w[:2]:
            v.append((t - S, *w))
    print("   Huette (Takt, Zustand, brennt, Leben):", v[:14], "Ende", v[-2:])
    arb = []
    wa = collections.Counter()
    for t, u in pl.stand(p, "DAT_UnitsState", {**U, "wo": "units[].workplaceBuildingID_1"}):
        m = (u["da"] != 0) & (u["b"] == 1) & (u["typ"] == 53)
        m[0] = False
        for i in np.nonzero(m)[0]:
            i = int(i)
            w = (int(u["z"][i]), int(u["mx"][i]) // 8, int(u["my"][i]) // 8)
            wa[int(u["wo"][i])] += 1
            if not arb or arb[-1][1:] != (i, *w):
                arb.append((t - S, i, *w))
    print("   Feuerwache (Art 53): Arbeitsplatz je Rahmen", wa.most_common(3), "Folge (Takt, Platz, Zustand, x, y):", arb[:16], "Anzahl", len(arb))
    tr = collections.Counter()
    for t, u in pl.stand(p, "DAT_UnitsState", U, jeder=50):
        m = (u["da"] != 0) & (u["b"] == 1)
        m[0] = False
        for a in u["typ"][m]:
            tr[int(a)] += 1
    print("   Spieler 1 je Art, jeder 50. Rahmen:", tr.most_common(8))


def munition():
    p, plan, wer, gb, S = laden("sonder10_g")
    k = [e for e in wer["munition"] if e["typ"] == 39]
    print("Munition: Katapulte", [e["nr"] for e in k])
    v = {e["nr"]: [] for e in k}
    for t, u in pl.stand(p, "DAT_UnitsState", {**U, "m": "units[].stoneAmmunition"}):
        for e in k:
            w = int(u["m"][e["nr"]])
            if not v[e["nr"]] or v[e["nr"]][-1][1] != w:
                v[e["nr"]].append((t - S, w))
    for e in k:
        print("   Katapult", e["nr"], "(Takt, Munition):", v[e["nr"]][:18])
    st = []
    for t, s in pl.stand(p, "DAT_GameState", {"s": ("playerDataArray[].currentResources[]", 4 * STEIN)}):
        w = int(s["s"][1])
        if not st or st[-1][1] != w:
            st.append((t - S, w))
    print("   Stein Spieler 1 (Takt, Menge):", st[:30])


def pech():
    p, plan, wer, gb, S = laden("sonder11_g")
    kopf("sonder11_g", p, plan)
    leute = [e for e in wer["pech"] if e["rolle"] == "geher"]
    v = {e["nr"]: [] for e in leute}
    for t, u in pl.stand(p, "DAT_UnitsState", {**U, "c": "units[].counter", "f": "units[].field312_0x40a", "l": "units[].health"}):
        for e in leute:
            n = e["nr"]
            w = (int(u["c"][n]), int(u["f"][n]))
            if not v[n] or v[n][-1][1:3] != w:
                v[n].append((t - S, *w, int(u["mx"][n]) // 8, int(u["my"][n]) // 8, int(u["l"][n])))
    for n, w in v.items():
        print("   P314 Geher", n, "(Takt, counter, field312, x, y, Leben):", w[:8], "Wechsel", len(w))
    h = ar.geschosse_lesen(p, pl.karte)
    print("   Geschosse je Art:", collections.Counter(x["art"] for x in h).most_common(5))


def schalter():
    p, plan, wer, gb, S = laden("sonder15_g")
    kopf("sonder15_g", p, plan)
    z = {"as": [], "an": [], "gold": [], "modus": []}
    for t, g in pl.stand(p, "DAT_GameState", {"as": "playerDataArray[].totalAssassinTroops", "an": "playerDataArray[].totalAttackTroops", "gold": ("playerDataArray[].currentResources[]", 4 * GOLD)}):
        for k in ("as", "an", "gold"):
            w = int(g[k][1])
            if not z[k] or z[k][-1][1] != w:
                z[k].append((t - S, w))
    for t, g in pl.stand(p, "DAT_GameCore", {"m": "gameMode_2"}):
        w = int(g["m"])
        if not z["modus"] or z["modus"][-1][1] != w:
            z["modus"].append((t - S, w))
    print("P370 totalAssassinTroops:", z["as"][:10], "totalAttackTroops:", z["an"][:10])
    print("P312 gameMode_2:", z["modus"], "Gold Spieler 1:", z["gold"][:14])
    e = []
    for t, g in pl.stand(p, "DAT_EntityState", {"art": "entityArray[].entityType", "da": "entityArray[].logicalState", "mx": "entityArray[].microX", "my": "entityArray[].microY"}):
        m = (g["da"] != 0) & (g["art"] == 14)
        n = int(m.sum())
        if not e or e[-1][1] != n:
            e.append((t - S, n))
    print("   Feuerkoerbe (Takt, Anzahl):", e[:8])


def rush():
    p = pl.neueste("sonder16_g")
    if not p:
        print("sonder16_g fehlt")
        return
    p, plan, wer, gb, S = laden("sonder16_g")
    kopf("sonder16_g", p, plan)
    a = next(e for e in wer["rush"] if e["rolle"] == "taeter")
    b = next(e for e in wer["rush"] if e["rolle"] == "opfer")
    r = []
    for t, g in pl.stand(p, "DAT_GameState", {"n": "mapAndTime.totalNoRushTicks", "l": "mapAndTime.noRushTicksLeftUnk"}, jeder=20):
        r.append((t - S, int(g["n"]), int(g["l"])))
    print("P331 (Takt, totalNoRushTicks, noRushTicksLeftUnk), jeder 20. Rahmen:", r[:6], "...", r[-3:])
    v = []
    for t, u in pl.stand(p, "DAT_UnitsState", {**U, "l": "units[].health"}):
        w = (int(u["z"][a["nr"]]), int(u["z"][b["nr"]]), int(u["l"][a["nr"]]), int(u["l"][b["nr"]]), int(u["mx"][a["nr"]]) // 8)
        if not v or v[-1][1:] != w:
            v.append((t - S, *w))
    print("   (Takt, Zustand a, Zustand b, Leben a, Leben b, x von a):", v[:24], "...", v[-3:])


if __name__ == "__main__":
    for f in (angst, loeschen, munition, pech, schalter, rush):
        try:
            f()
        except Exception as e:
            import traceback
            print("FEHLER", f.__name__, repr(e))
            traceback.print_exc(limit=3)
