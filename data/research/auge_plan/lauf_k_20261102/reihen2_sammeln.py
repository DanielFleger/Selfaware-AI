# -*- coding: utf-8 -*-
"""B-142: Zweiter Durchgang fuer die Einzelpunkte von Lauf K: Felder, die reihen_sammeln.py nicht hat. Speichert nach reihen2.pkl (bleibt lokal).

Aufruf aus dem Arbeitsbaum: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/reihen2_sammeln.py <basis>
"""
import collections
import os
import pickle
import struct
import sys

import numpy as np

from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

HIER = os.path.dirname(os.path.abspath(__file__))
k = Feldkarte.laden(feldliste=FELDLISTE)
AV = k.adresse("DAT_GameState", "mapAndTime.attackVectors[]")
SP = k.adresse("DAT_GameState", "mapAndTime.signpostEntryData[]")
SIEGE = k.adresse("DAT_GameState", "playerDataArray[].aiSiegeCreationInformation[]")
IDX = k.adresse("DAT_GameState", "mapAndTime.playerBuildingInfoIndex[]")
EN = k.adresse("DAT_GameState", "mapAndTime.playerEnemyBuildingIDs[]")
ST = k.adresse("DAT_GameState", "mapAndTime.startingTroops[]")
CNT = k.adresse("DAT_TroopValueState", "attackInfo.tentPoints")
TPV = k.adresse("DAT_TroopValueState", "attackInfo.tentPointsValues[]")
SZ = k.adresse("DAT_TroopValueState", "attackInfo.aiTribeSizesPerTribeType")
PI = {f: k.adresse("DAT_TroopValueState", "attackInfo.playerInfo[]." + f) for f in ("moat2", "gate2", "wide3")}
ER = {f: k.adresse("DAT_EntityState", "entityArray[]." + f) for f in ("logicalState", "entityType", "owner", "someTracker")}
ZONE = k.adresse("DAT_TileMapState", "AIZoneLayer[]")
UNIT = {f: k.adresse("DAT_UnitsState", "units[]." + f) for f in ("logicalState", "unitType", "owner", "uid")}
GEB = {f: k.adresse("DAT_BuildingsState", "buildings[]." + f) for f in ("buildingType", "owner", "logicalState")}
GOLD = k.adresse("DAT_GameState", "playerDataArray[].currentResources[]")
TYP = {1: "<i1", 2: "<i2", 4: "<i4"}
ATTACK_REQ = k.adresse("DAT_SkirmishDefinedData", "attackUnitRequired[].required")
AI_NAMEN = ["AttForceBase", "AttForceRandom", "RaidUnitsBase", "RaidUnitsRandom", "TargetChoice", "HarassingSiegeEnginesMax"]


def spalte(p, basis, f):
    a, gr, s, n = f
    return np.ndarray(shape=(n,), dtype=TYP.get(gr, "<i4"), buffer=p, offset=a - basis, strides=(s,))


def sammeln(pfad):
    auf = aw.Aufzeichnung(pfad)
    bas = {auf.bereiche[i][0]: auf.bereiche[i][1] for i in range(len(auf.bereiche))}
    aus = {"av": collections.defaultdict(list), "signpost": collections.defaultdict(list), "siege": collections.defaultdict(list), "index": collections.defaultdict(list), "start": collections.defaultdict(list),
           "tent": [], "tent_werte": [], "groessen": [], "pi": collections.defaultdict(list), "flagge": collections.defaultdict(list), "flagge_zahl": collections.Counter(), "zone": [], "neu": [], "geb_stichprobe": [],
           "enemy": [], "required": [], "aic": None, "weg": []}
    letzt = {}
    uid_alt = None
    gold_alt = None
    naechste_zone = naechste_geb = naechste_flagge = 0
    gb = None

    def merke(tab, kk, t, w):
        if letzt.get((id(tab), kk)) != w:
            tab[kk].append((t, w))
            letzt[(id(tab), kk)] = w

    for r, p, _ in auf.staende():
        name = auf.namen[r.bereich]
        t = r.takt
        if name == "DAT_GameState":
            b = bas[name]
            gold_jetzt = spalte(p, b, (GOLD[0] + 15 * 4, 4, GOLD[2], 9)).copy()
            gold_alt = (gold_jetzt, t) if gold_alt is None else gold_alt
            for sp in range(1, 9):
                w = struct.unpack_from("<4i", p, AV[0] + sp * AV[1] - b)
                merke(aus["av"], sp, t, w)
                merke(aus["signpost"], sp - 1, t, struct.unpack_from("<4i", p, SP[0] + (sp - 1) * SP[1] - b))
                merke(aus["siege"], sp, t, struct.unpack_from("<15i", p, SIEGE[0] + sp * SIEGE[2] - b))
                merke(aus["index"], sp, t, struct.unpack_from("<i", p, IDX[0] + sp * 4 - b)[0])
                merke(aus["start"], sp - 1, t, struct.unpack_from("<20i", p, ST[0] + (sp - 1) * ST[1] - b))
            gb = (t, bytes(p[EN[0] - b:EN[0] - b + EN[1] * 9]), [struct.unpack_from("<i", p, IDX[0] + sp * 4 - b)[0] for sp in range(9)])
            aus["_gold"] = gold_jetzt
        elif name == "DAT_TroopValueState":
            b = bas[name]
            n = struct.unpack_from("<i", p, CNT[0] - b)[0]
            if letzt.get("tent") != n:
                aus["tent"].append((t, n))
                letzt["tent"] = n
                if n > 0:
                    aus["tent_werte"].append((t, [struct.unpack_from("<8i", p, TPV[0] + i * TPV[1] - b) for i in range(min(n, 8))]))
            w = struct.unpack_from("<40i", p, SZ[0] - b)
            if letzt.get("gr") != w:
                aus["groessen"].append((t, w))
                letzt["gr"] = w
            for f, v in PI.items():
                for sp in range(8):
                    merke(aus["pi"], (sp, f), t, struct.unpack_from("<i", p, v[0] + sp * v[2] - b)[0])
        elif name == "DAT_EntityState" and t >= naechste_flagge:
            b = bas[name]
            l, ty, ow, tr = (spalte(p, b, ER[f]) for f in ("logicalState", "entityType", "owner", "someTracker"))
            for i in np.flatnonzero(l != 0):
                aus["flagge_zahl"][int(ty[i])] += 1
            naechste_flagge = t + 200
            for i in np.flatnonzero((l != 0) & (tr != 0)):
                pass
            aus["_flagge"] = None
            for i in np.flatnonzero((l != 0) & (ty == aus.get("_ftyp", -1))):
                merke(aus["flagge"], (int(i), int(ow[i])), t, int(tr[i]))
        elif name == "DAT_TileMapState" and t >= naechste_zone:
            b = bas[name]
            z = np.frombuffer(p, dtype=np.uint8, offset=ZONE[0] - b, count=ZONE[3])
            werte, zahl = np.unique(z, return_counts=True)
            aus["zone"].append((t, dict(zip(werte.tolist(), zahl.tolist()))))
            weg = np.frombuffer(p, dtype=np.uint8, offset=0x01EE2998 - b, count=80400 * 9) if 0x01EE2998 - b + 80400 * 9 <= len(p) else None
            if weg is not None:
                aus["weg"].append((t, [dict(zip(*[x.tolist() for x in np.unique(weg[i * 80400:(i + 1) * 80400], return_counts=True)])) for i in range(1, 9)]))
            naechste_zone = t + 2000
        elif name == "DAT_UnitsState":
            b = bas[name]
            u = spalte(p, b, UNIT["uid"]).copy()
            ty = spalte(p, b, UNIT["unitType"])
            ow = spalte(p, b, UNIT["owner"])
            ls = spalte(p, b, UNIT["logicalState"])
            if uid_alt is not None:
                for i in np.flatnonzero((u != uid_alt) & (u != 0) & (ls != 0)):
                    aus["neu"].append((t, int(i), int(ty[i]), int(ow[i])))
            uid_alt = u
        elif name == "DAT_BuildingsState" and t >= naechste_geb and gb is not None and gb[0] == t:
            b = bas[name]
            ty, ow, ls = (spalte(p, b, GEB[f]) for f in ("buildingType", "owner", "logicalState"))
            je = collections.Counter(ow[(ty != 0) & (ls != 0)].tolist())
            enemy = {sp: struct.unpack_from(f"<{min(gb[2][sp], 40)}i", gb[1], EN[1] * sp) if gb[2][sp] > 0 else () for sp in range(1, 9)}
            aus["geb_stichprobe"].append((t, dict(je), gb[2], {sp: len(v) for sp, v in enemy.items()}, {sp: [(int(ty[x]), int(ow[x])) for x in v[:12] if 0 <= x < len(ty)] for sp, v in enemy.items()}))
            naechste_geb = t + 5000
        elif name == "datenblock":
            b = bas[name]
            w = struct.unpack_from("<11i", b"".join(struct.pack("<i", struct.unpack_from("<i", p, ATTACK_REQ[0] + i * ATTACK_REQ[2] - b)[0]) for i in range(11)))
            if letzt.get("req") != w:
                aus["required"].append((t, w))
                letzt["req"] = w
            if aus["aic"] is None:
                aus["aic"] = {n: [struct.unpack_from("<i", p, k.adresse("DAT_AICState", "aics[]." + n)[0] + i * 676 - b)[0] for i in range(20)] for n in AI_NAMEN}
                aus["aic_roh"] = {i: {"+14c": struct.unpack_from("<i", p, k.adresse("DAT_AICState", "aics[]." + AI_NAMEN[0])[0] - 0x1F4 + i * 676 + 0x14C - b)[0],
                                      "+150": struct.unpack_from("<i", p, k.adresse("DAT_AICState", "aics[]." + AI_NAMEN[0])[0] - 0x1F4 + i * 676 + 0x150 - b)[0],
                                      "+154": struct.unpack_from("<i", p, k.adresse("DAT_AICState", "aics[]." + AI_NAMEN[0])[0] - 0x1F4 + i * 676 + 0x154 - b)[0],
                                      "+158": struct.unpack_from("<i", p, k.adresse("DAT_AICState", "aics[]." + AI_NAMEN[0])[0] - 0x1F4 + i * 676 + 0x158 - b)[0],
                                      "+118": struct.unpack_from("<i", p, k.adresse("DAT_AICState", "aics[]." + AI_NAMEN[0])[0] - 0x1F4 + i * 676 + 0x118 - b)[0],
                                      "+11c": struct.unpack_from("<i", p, k.adresse("DAT_AICState", "aics[]." + AI_NAMEN[0])[0] - 0x1F4 + i * 676 + 0x11C - b)[0]} for i in range(20)}
    aus.pop("_gold", None)
    aus.pop("_flagge", None)
    for kk in ("av", "signpost", "siege", "index", "start", "pi", "flagge"):
        aus[kk] = dict(aus[kk])
    return aus


if __name__ == "__main__":
    basis = sys.argv[1]
    daten = {}
    for kk, e in (("haupt", ".auge"), ("t1", "_t1.auge"), ("danach", "_danach.auge")):
        if os.path.exists(basis + e):
            daten[kk] = sammeln(basis + e)
            print(kk, "neue Einheiten", len(daten[kk]["neu"]), "Zonen", len(daten[kk]["zone"]), "Stichproben", len(daten[kk]["geb_stichprobe"]), flush=True)
    with open(os.path.join(HIER, "reihen2.pkl"), "wb") as f:
        pickle.dump(daten, f)
    print("geschrieben")
