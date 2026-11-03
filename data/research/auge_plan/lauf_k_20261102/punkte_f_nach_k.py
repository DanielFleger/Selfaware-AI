# -*- coding: utf-8 -*-
"""B-142: Die 20 Punkte, die das Urteil von Lauf F auf "Lauf K" verschoben hat, gerechnet aus den Aufzeichnungen von Lauf K.

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/punkte_f_nach_k.py <basis> <basis_f> > data/research/auge_plan/lauf_k_20261102/punkte_f_nach_k.txt
"""
import collections
import json
import os
import pickle
import re
import struct
import sys

import numpy as np

from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

HIER = os.path.dirname(os.path.abspath(__file__))
basis, basis_f = sys.argv[1], sys.argv[2]
k = Feldkarte.laden(feldliste=FELDLISTE)
d1 = pickle.load(open(os.path.join(HIER, "reihen.pkl"), "rb"))
d6 = pickle.load(open(os.path.join(HIER, "reihen6.pkl"), "rb"))
KI = {1: 14, 2: 15, 3: 1, 4: 9, 5: 2, 6: 5, 7: 7, 8: 4}
FMT = {1: "<b", 2: "<h", 4: "<i"}
SPF = {f: k.adresse("DAT_GameState", "playerDataArray[]." + f) for f in ("aiType", "aivID", "availableIronGridTiles", "algoIronCooldown", "noWoodTracker", "top100TargetableBuildingsTracker", "willBuy", "moatsOwned", "countFletchersPoleturners", "canStartSpending", "aiRecruitIntervalTracker", "marketplace.id", "popularity", "taxesSetting", "aiNervousActionsTracker")}
RES = k.adresse("DAT_GameState", "playerDataArray[].currentResources[]")
WUNSCH = k.adresse("DAT_GameState", "playerDataArray[].resourcesToAcquireArray[]")
PREISE = k.adresse("DAT_GameState", "mapAndTime.buyAndSalesPriceArray[]")
TEAMS = k.adresse("DAT_GameState", "mapAndTime.playerTeams[]")
KAL = {f: k.adresse("DAT_GameState", "mapAndTime." + f) for f in ("dayTicks", "weekTicks", "monthTicks")}
AIC0 = k.adresse("DAT_AICState", "aics[].AttForceBase")[0] - 0x1F4
U = {f: k.adresse("DAT_UnitsState", "units[]." + f) for f in ("unitType", "owner", "logicalState", "maxHealth", "tile", "x", "y")}
AV = {f: k.adresse("DAT_AIVState", "aivs[]." + f) for f in ("totalSteps", "currentStepGoal", "keepXOffset", "keepYOffset")}
SCHRITT = k.adresse("DAT_AIVState", "aivs[].aivBuildingSteps[]")
ST_STATUS = k.adresse("DAT_AIVState", "aivs[].aivBuildingSteps[].buildStatus")
ST_ORT = k.adresse("DAT_AIVState", "aivs[].aivBuildingSteps[].location")
HEAT = {f: k.adresse("DAT_AIVState", "heatMaps[]." + f) for f in ("ironCount", "bouldersCount", "oilCount")}
MOATS = k.adresse("DAT_TileMapState", "moats[].owner")
HOLZ = k.adresse("DAT_AIVState", "mapExtraInfo.totalWoodAvailable")
LORDT = next(a for a, n in k.labels.items() if n == "DAT_AIType_MaxLordHealth_Mapping")
HANDEL = k.adresse("DAT_SkirmishDefinedData", "AIResourceTradeAICMapping[].aic")
roh = open(r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference\types.json", encoding="utf-8").read().replace("\\n", " ").replace("\\t", " ")
AIRTC = {int(z): n for n, z in re.findall(r"(AIRTC_[A-Z_]+): (\d+)", roh)}
print("Warengruppen", AIRTC)


def stand(r, t):
    w = None
    for a, b in r:
        if a > t:
            break
        w = b
    return w


def reihe(sp, f):
    return d1["t1"]["spieler"].get((sp, f), []) + d1["danach"]["spieler"].get((sp, f), [])


# Start
auf = aw.Aufzeichnung(basis + ".auge")
st, bas = {}, {b[0]: b[1] for b in auf.bereiche}
gesehen = False
for r, p, _ in auf.staende():
    st[auf.namen[r.bereich]] = p
    if len(st) == len(auf.namen) and r.takt >= 110 and not gesehen and auf.namen[r.bereich] == "DAT_UnitsState":
        gesehen = True
        gs, gb = st["DAT_GameState"], bas["DAT_GameState"]
        ad, ab = st["DAT_AIVState"], bas["DAT_AIVState"]
        ud, ub = st["DAT_UnitsState"], bas["DAT_UnitsState"]
        d, db = st["datenblock"], bas["datenblock"]
        print("\n=== Takt", r.takt, "P001 Teams", struct.unpack_from("<9i", gs, TEAMS[0] - gb))
        sp_w = lambda f, sp: struct.unpack_from(FMT[SPF[f][1]], gs, SPF[f][0] + sp * SPF[f][2] - gb)[0]  # noqa: E731
        ty, ow, ls, mh = (np.ndarray((U[f][3],), dtype={2: "<i2", 4: "<i4"}[U[f][1]], buffer=ud, offset=U[f][0] - ub, strides=(U[f][2],)) for f in ("unitType", "owner", "logicalState", "maxHealth"))
        print("=== P007 Tabelle", struct.unpack_from("<32i", d, LORDT - db))
        print("Lord maxHealth je Spieler", {int(o): int(m) for o, m in zip(ow[1:][(ty[1:] == 55) & (ls[1:] != 0)], mh[1:][(ty[1:] == 55) & (ls[1:] != 0)])}, "aiType", {sp: sp_w("aiType", sp) for sp in range(1, 9)})
        preise_k = [struct.unpack_from("<2i", gs, PREISE[0] + i * 8 - gb) for i in range(25)]
        print("=== P052 Eisen (Zaehler, Cooldown)", {sp: (sp_w("availableIronGridTiles", sp), sp_w("algoIronCooldown", sp)) for sp in range(1, 9)})
        print("=== P053 AIV")
        for sp in range(1, 9):
            i = sp_w("aivID", sp)
            ts = struct.unpack_from("<i", ad, AV["totalSteps"][0] + i * AV["totalSteps"][2] - ab)[0]
            ox = struct.unpack_from("<i", ad, AV["keepXOffset"][0] + i * AV["keepXOffset"][2] - ab)[0]
            oy = struct.unpack_from("<i", ad, AV["keepYOffset"][0] + i * AV["keepYOffset"][2] - ab)[0]
            status = collections.Counter()
            orte = []
            for s in range(1, min(ts, 2000) + 1):
                status[struct.unpack_from("<b", ad, ST_STATUS[0] + i * ST_STATUS[2] + s * SCHRITT[1] - ab)[0]] += 1
                orte.append(struct.unpack_from("<i", ad, ST_ORT[0] + i * ST_ORT[2] + s * SCHRITT[1] - ab)[0])
            orte_a = np.array(orte) if orte else np.zeros(1, dtype=int)
            print("  Spieler", sp, "aivID", i, "Schritte", ts, "Status", dict(status), "Versatz", (ox, oy), "Ort min, max", int(orte_a.min()), int(orte_a.max()))
        print("=== P054 Heatmap: Summe und Zellen ungleich 0")
        for f, v in HEAT.items():
            z = np.frombuffer(ad, dtype=np.uint8, offset=v[0] - ab, count=80 * 80 * 48)[::48]
            print(" ", f, "Summe", int(z.sum()), "Zellen", int((z != 0).sum()))
        hdl = {g: struct.unpack_from("<2i", d, HANDEL[0] - 4 + j * 8 - db) for j, g in enumerate(range(26))}
        handel = {a: b for a, b in hdl.values()}
        aic = {sp: {o: struct.unpack_from("<i", d, AIC0 + KI[sp] * 676 + o - db)[0] for o in (0x18, 0x1C, 0x20, 0x24, 0x28, 0x80, 0x9C, 0xA8, 0xAC, 0xB0, 0xB4, 0xB8, 0xBC, 0xC0)} for sp in KI}
        verbot = {sp: set(struct.unpack_from("<15i", d, AIC0 + KI[sp] * 676 + 0xD4 - db)) for sp in KI}
        print("Handelsgruppen Ware: Gruppe", handel)
        print("kritische Beliebtheit, niedrig, hoch", {sp: (aic[sp][0x18], aic[sp][0x1C], aic[sp][0x20]) for sp in KI}, "+0x9c", {sp: aic[sp][0x9C] for sp in KI})
        break
aF = aw.Aufzeichnung(basis_f + ".auge")
gF = aF.namen.index("DAT_GameState")
for r, p, _ in aF.staende():
    if r.bereich == gF:
        preise_f = [struct.unpack_from("<2i", p, PREISE[0] + i * 8 - aF.bereiche[gF][1]) for i in range(25)]
        break
print("=== P021 Preise Gefecht", preise_k[:25], "gleich Burgenbau (Lauf F)", preise_k == preise_f, "Unterschiede", [(i, a, b) for i, (a, b) in enumerate(zip(preise_k, preise_f)) if a != b][:6])

print("\n=== P181 Beliebtheit unter der kritischen Grenze gegen Steuer, im Wochentakt des Spielers")
for sp in KI:
    pop, tax = reihe(sp, "popularity"), reihe(sp, "taxesSetting")
    h = collections.Counter()
    for t in range(15200 + sp, 150400, 200):
        if stand(pop, t) is None:
            continue
        if stand(pop, t - 1) <= aic[sp][0x18]:
            h[stand(tax, t + 8)] += 1
    print(" Spieler", sp, "Grenze", aic[sp][0x18], "Beliebtheit min", min(v for t, v in pop if t > 15000), "Steuer dabei", dict(h))

print("\n=== P183, P184, P188, P189, P186, P194 strenge Fenster")
wille = collections.Counter()
holz = collections.Counter()
zaehl_top = collections.Counter()
wunsch9c = collections.Counter()
verkauf = collections.Counter()
verkauf_bsp = []
moats = collections.Counter()
woodhut = []
reihe_nw = collections.defaultdict(list)
for fn in ("t1", "t6", "t8"):
    auf = aw.Aufzeichnung(f"{basis}_{fn}.auge")
    bas = {b[0]: b[1] for b in auf.bereiche}
    i_b = auf.namen.index("befehle")
    st = {}
    alt = None
    for r, p, _ in auf.staende():
        st[auf.namen[r.bereich]] = p
        if r.bereich != i_b or "DAT_TileMapState" not in st:
            continue
        gs, gb = st["DAT_GameState"], bas["DAT_GameState"]
        jetzt = {sp: {f: struct.unpack_from(FMT[SPF[f][1]], gs, SPF[f][0] + sp * SPF[f][2] - gb)[0] for f in ("willBuy", "noWoodTracker", "top100TargetableBuildingsTracker", "moatsOwned", "countFletchersPoleturners", "canStartSpending", "marketplace.id", "aiNervousActionsTracker", "popularity")} for sp in KI}
        res = {sp: struct.unpack_from("<25i", gs, RES[0] + sp * RES[2] - gb) for sp in KI}
        wu = {sp: struct.unpack_from("<25i", gs, WUNSCH[0] + sp * WUNSCH[2] - gb) for sp in KI}
        tag = struct.unpack_from("<i", gs, KAL["dayTicks"][0] - gb)[0]
        mon = struct.unpack_from("<i", gs, KAL["monthTicks"][0] - gb)[0]
        for sp in KI:
            reihe_nw[sp].append((r.takt, jetzt[sp]["noWoodTracker"], wu[sp][2]))
        if alt is not None:
            for sp in KI:
                a, b = alt[0][sp], jetzt[sp]
                if b["marketplace.id"]:
                    wille[(tag == sp, a["willBuy"] != b["willBuy"])] += 1
                if a["noWoodTracker"] != b["noWoodTracker"]:
                    holz[b["noWoodTracker"] - a["noWoodTracker"]] += 1
                if a["top100TargetableBuildingsTracker"] != b["top100TargetableBuildingsTracker"]:
                    zaehl_top[b["top100TargetableBuildingsTracker"] - a["top100TargetableBuildingsTracker"]] += 1
                for w in range(25):
                    if wu[sp][w] != alt[2][sp][w] and wu[sp][w] != 0:
                        wunsch9c[(wu[sp][w] == aic[sp][0x9C], wu[sp][w] == 5, w == 2)] += 1
                    if res[sp][w] < alt[1][sp][w] and w != 15 and res[sp][15] > alt[1][sp][15] and tag == sp:
                        gr = handel.get(w)
                        name = AIRTC.get(gr, "?")
                        grenze = {"AIRTC_WOOD": aic[sp][0xAC], "AIRTC_FOOD": aic[sp][0x80], "AIRTC_STONE": aic[sp][0xB0], "AIRTC_WEAPONS": aic[sp][0xB8], "AIRTC_ALE": aic[sp][0xBC]}.get(name, aic[sp][0xB4]) + aic[sp][0xC0] + alt[2][sp][w]
                        vor = alt[1][sp][w]
                        grund = "kritisch oder nervoes" if b["popularity"] < aic[sp][0x18] or (b["aiNervousActionsTracker"] > 0 and alt[1][sp][15] < 500) else ("Verbot" if w in verbot[sp] else "normal")
                        verkauf[(grund, vor > grenze)] += 1
                        if len(verkauf_bsp) < 8:
                            verkauf_bsp.append((fn, r.takt, sp, w, name, vor, res[sp][w], "Grenze", grenze, "Gold", res[sp][15] - alt[1][sp][15], grund))
            if 1 <= mon <= 8:
                tm, tb = st["DAT_TileMapState"], bas["DAT_TileMapState"]
                bes = np.frombuffer(tm, dtype=np.int8, offset=MOATS[0] - tb, count=MOATS[3] * MOATS[2])[::MOATS[2]]
                c = collections.Counter(bes[bes != 0].tolist())
                for sp in KI:
                    moats[jetzt[sp]["moatsOwned"] == c[sp]] += 1
        alt = (jetzt, res, wu)
print("P189 (Tagestakt des Spielers, willBuy wechselt)", sorted(wille.items()))
print("P183 Schritte noWoodTracker", holz.most_common(5))
for sp, r in reihe_nw.items():
    bei = [(t, w) for t, n, w in r if n == 37]
    if max(n for _, n, _ in r) > 0:
        print("  Spieler", sp, "hoechster Zaehler", max(n for _, n, _ in r), "bei 37:", bei[:3])
print("P184 Schritte", zaehl_top.most_common(6))
print("P188 (Wert == +0x9c, Wert == 5, Ware Holz)", sorted(wunsch9c.items()))
print("P186 (Grund, Bestand ueber Grenze)", sorted(verkauf.items()), verkauf_bsp)
print("P194 moatsOwned == eigene Zaehlung", sorted(moats.items()))

print("\n=== P182, P191, P183 Hauptaufzeichnung")
for fn in (".auge", "_danach.auge"):
    auf = aw.Aufzeichnung(basis + fn)
    bas = {b[0]: b[1] for b in auf.bereiche}
    i_g, i_a = auf.namen.index("DAT_GameState"), auf.namen.index("DAT_AIVState")
    st = {}
    schritte = collections.Counter()
    alt = {}
    wood = []
    nw = collections.Counter()
    for r, p, _ in auf.staende():
        st[auf.namen[r.bereich]] = p
        if r.bereich == i_a:
            wood.append((r.takt, struct.unpack_from("<i", p, HOLZ[0] - bas["DAT_AIVState"])[0]))
        if r.bereich == i_g and "DAT_AIVState" in st:
            ad, ab = st["DAT_AIVState"], bas["DAT_AIVState"]
            for sp in KI:
                i = struct.unpack_from("<i", p, SPF["aivID"][0] + sp * SPF["aivID"][2] - bas["DAT_GameState"])[0]
                w = struct.unpack_from("<i", ad, AV["currentStepGoal"][0] + i * AV["currentStepGoal"][2] - ab)[0]
                g = struct.unpack_from("<i", p, RES[0] + sp * RES[2] + 60 - bas["DAT_GameState"])[0]
                if sp in alt and alt[sp] != w:
                    schritte[(min(w - alt[sp], 3), "bis 5000" if g <= 5000 else ("bis 16000" if g <= 16000 else "darueber"))] += 1
                alt[sp] = w
                n = struct.unpack_from("<i", p, SPF["noWoodTracker"][0] + sp * SPF["noWoodTracker"][2] - bas["DAT_GameState"])[0]
                wu2 = struct.unpack_from("<i", p, WUNSCH[0] + sp * WUNSCH[2] + 8 - bas["DAT_GameState"])[0]
                if n == 37:
                    nw[(sp, wu2)] += 1
    print(fn, "P191 (Schritt, Gold)", sorted(schritte.items()), "Holz Karte erste, letzte, kleinster", wood[0], wood[-1], min(x[1] for x in wood), "P183 bei 37 (Spieler, Wunsch Holz)", nw.most_common(6))
huetten = collections.defaultdict(int)
ereignisse = []
wood_ser = None
for fn in ("t1",):
    pass
print("P182 neue Huetten in t1, t6, t8 (Takt, Besitzer)", [(fn, x[0], x[3]) for fn in ("t1", "t6", "t8") for x in d6[fn]["neu_geb"] if x[2] == 3][:14])

print("\n=== P199, P201 Werte aus dem Lauf")
sp_j = {p["nr"]: p for p in json.load(open(basis + ".spielart.json", encoding="utf-8"))["punkte"]}
for nr in ("P199", "P201", "P184", "P188"):
    p = sp_j.get(nr, {})
    print(nr, p.get("urteil"), str(p.get("belege"))[:600])
