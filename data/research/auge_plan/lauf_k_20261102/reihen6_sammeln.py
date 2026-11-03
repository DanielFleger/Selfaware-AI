# -*- coding: utf-8 -*-
"""B-142 Lauf K: Takt fuer Takt aus den strengen Fenstern t1 (Frieden), t6 und t8 (Kampf): alles, was die letzten Einzelpunkte brauchen. Speichert nach reihen6.pkl (bleibt lokal).

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/reihen6_sammeln.py <basis>
Ein Bereich gilt erst, wenn sein Rahmen dieses Takts da ist, darum wird am letzten Bereich des Takts gerechnet.
"""
import os
import pickle
import struct
import sys

import numpy as np

from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

HIER = os.path.dirname(os.path.abspath(__file__))
k = Feldkarte.laden(feldliste=FELDLISTE)
TYP = {1: "<i1", 2: "<i2", 4: "<i4"}
FMT = {1: "<b", 2: "<h", 4: "<i"}
FELDER = ["aiType", "aiPlayerState", "attackedPlayerID", "attackedPlayerID_2Unk", "aiRecruitUnitChoiceState", "aiBuildingDestroyChoiceTracker", "aiNervousActionsTracker", "aiStrengthState", "aiStrengthFeeling", "isNotNervousByEnemyTroopValue",
          "totalEnemyTroopValue", "totalTeamTroopValue", "totalEnemyRangedTroopValue", "relativeStrengthOfTeamComparedToEnemy", "currentPopulation", "totalFood", "totalAttackTroops", "totalRaidingTroopsUnk", "totalDefensiveTroopsUnk",
          "aivCurrentPauseIndex", "currentAttackWave", "currentAttackRaidParameter", "totalAttackingEngineerTroops", "totalDiggingUnitTroops", "totalAssassinTroops", "totalUnit2Troops", "totalLaddermenTroops", "totalTunnelerTroops",
          "totalUnitPatrolTroops", "totalUnitBackupTroops", "totalUnitEngageTroops", "totalUnitSiegeDefTroops", "totalMaxDefaultTroops", "moatsOwned", "campground.xEntry", "campground.yEntry", "barracks.id", "mercenaryPost.id", "engineersGuild.id",
          "canStartSpending", "idlePeasantsCount", "totalTroopsType6", "totalTroopsType7", "unknownCounter_01", "requestStateUnk"]
SP = {f: k.adresse("DAT_GameState", "playerDataArray[]." + f) for f in FELDER}
PAUSEN = k.adresse("DAT_GameState", "playerDataArray[].aivPauses[]")
GOLD = k.adresse("DAT_GameState", "playerDataArray[].currentResources[]")
RES = k.adresse("DAT_GameState", "playerDataArray[].resourcesToAcquireArray[]")
KAL = {f: k.adresse("DAT_GameState", "mapAndTime." + f) for f in ("dayTicks", "weekTicks", "monthTicks", "yearChanged")}
BAL = k.adresse("DAT_GameState", "gameTicksLoadBalancer")
IDX = k.adresse("DAT_GameState", "mapAndTime.playerBuildingInfoIndex[]")
EN = k.adresse("DAT_GameState", "mapAndTime.playerEnemyBuildingIDs[]")
TEAM = k.adresse("DAT_GameState", "mapAndTime.playerTeams[]")
NAH = k.adresse("DAT_TroopValueState", "attackInfo.playerTotalTroopValueOfTroopsNearKeep[]")
RQ = k.adresse("DAT_SkirmishDefinedData", "attackUnitRequired[].required")
AIC = {f: k.adresse("DAT_AICState", "aics[]." + f) for f in ("AttMaxEngineers", "AttDiggingUnitMax", "AttMaxAssassins", "AttUnit2Max", "AttMaxLaddermen", "AttMaxTunnelers", "AttUnitPatrolMax", "AttUnitBackupMax", "AttUnitEngageMax", "AttUnitSiegeDefMax", "AttMaxDefault", "TargetChoice", "RaidUnitsBase", "RaidUnitsRandom")}
U = {f: k.adresse("DAT_UnitsState", "units[]." + f) for f in ("uid", "logicalState", "unitType", "owner", "unknownDigMoatOrWallAttackFlag1015", "targetedBuildingTile", "x", "y")}
E = {f: k.adresse("DAT_EntityState", "entityArray[]." + f) for f in ("logicalState", "entityType", "owner", "someTracker")}
G = {f: k.adresse("DAT_BuildingsState", "buildings[]." + f) for f in ("logicalState", "buildingType", "owner", "uid", "attackWave", "x", "y")}
L = {f: k.adresse("DAT_TileMapState", f + "[]") for f in ("LogicLayer", "WallOwnerLayer", "HeightLayer", "DefaultHeightLayer", "BuildingLayer")}
AUS = np.array([10, 0x15, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x3b, 0x43, 0x47, 0x48, 0x49, 0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x68])
FLAGGEN = (10, 11, 12)
SOLDAT = (22, 23, 24, 25, 26, 27, 28, 29, 30, 37, 39, 40, 41, 58, 59, 60, 61, 70, 71, 72, 73, 74, 75, 76, 77)
BL = 0x177BC
# Zaehler je Angreifer, Adressen aus recomputeAttackInfo: (Name, Adresse fuer Spieler 0)
ZAEHLER = {"hack_c": 0x1793518, "hack_8": 0x179351C, "scale_10": 0x17973C0, "scale_c": 0x17973C4, "scale_8": 0x17973C8, "wide_c": 0x17A6E34, "wide_8": 0x17A6E38, "moat_c": 0x17A2F98, "moat_8": 0x17A2F9C}
LISTEN = {"hack": (0x1793524, "hack_8"), "scale": (0x17973D0, "scale_8"), "wide": (0x17A6E40, "wide_8"), "moat": (0x17A2FA4, "moat_8")}


def spalte(p, b, f, dt=None):
    a, gr, s, n = f
    return np.ndarray(shape=(n,), dtype=dt or TYP[gr], buffer=p, offset=a - b, strides=(s,))


def fenster(pfad):
    auf = aw.Aufzeichnung(pfad)
    bas = {b[0]: b[1] for b in auf.bereiche}
    letzter_bereich = auf.namen.index("befehle")  # der letzte Bereich, den die strengen Fenster in jedem Takt lesen; Karte alle 25 Takte, Datenblock alle 250
    daten_frisch = False
    st = {}
    aus = {"R": {}, "flagge": [], "flaggen_start": {}, "neu": [], "feind": [], "zaehler": {}, "mauer": [], "ziel": [], "neu_geb": []}
    uid_alt = flag_alt = None
    flagge_alt = {}
    zaehler_alt = {}
    geb_uid_alt = None
    for r, p, _ in auf.staende():
        st[auf.namen[r.bereich]] = p
        if auf.namen[r.bereich] == "datenblock":
            daten_frisch = True
        if r.bereich != letzter_bereich or "datenblock" not in st:
            continue
        t = r.takt
        gs, gb = st["DAT_GameState"], bas["DAT_GameState"]
        tv, tb = st["DAT_TroopValueState"], bas["DAT_TroopValueState"]
        rr = {f: struct.unpack_from("<i", gs, v[0] - gb)[0] for f, v in KAL.items()}
        rr["bal"] = struct.unpack_from("<i", gs, BAL[0] - gb)[0]
        team = [struct.unpack_from("<i", gs, TEAM[0] + i * 4 - gb)[0] for i in range(9)]
        for sp in range(1, 9):
            z = {f: struct.unpack_from(FMT[v[1]], gs, v[0] + sp * v[2] - gb)[0] for f, v in SP.items()}
            z["pause1"] = struct.unpack_from("<h", gs, PAUSEN[0] + sp * PAUSEN[2] + 2 - gb)[0]
            z["gold"] = struct.unpack_from("<i", gs, GOLD[0] + sp * GOLD[2] + 60 - gb)[0]
            z["roh71d"] = struct.unpack_from("<i", gs, GOLD[0] + sp * GOLD[2] + 60 + 0x71D * 4 - gb)[0]
            z["rohcf7"] = struct.unpack_from("<i", gs, GOLD[0] + sp * GOLD[2] + 60 + 0xCF7 * 4 - gb)[0]
            z["index"] = struct.unpack_from("<i", gs, IDX[0] + sp * 4 - gb)[0]
            z["nah"] = struct.unpack_from("<i", tv, NAH[0] + sp * 4 - tb)[0]
            z["bogen_fehlt"] = [struct.unpack_from("<i", gs, RES[0] + sp * RES[2] + i * 4 - gb)[0] for i in range(25)]
            rr[sp] = z
        d, db = st["datenblock"], bas["datenblock"]
        rr["req"] = tuple(struct.unpack_from("<i", d, RQ[0] + i * RQ[2] - db)[0] for i in range(11))
        rr["req_frisch"] = daten_frisch
        daten_frisch = False
        if "aic" not in aus:
            aus["aic"] = {f: [struct.unpack_from("<i", d, v[0] + i * v[2] - db)[0] for i in range(20)] for f, v in AIC.items()}
            aus["team"] = team
        # Einheiten
        ub, ud = bas["DAT_UnitsState"], st["DAT_UnitsState"]
        uid, uls, uty, uow = (spalte(ud, ub, U[f]) for f in ("uid", "logicalState", "unitType", "owner"))
        rr["lords"] = tuple(sorted(int(x) for x in uow[1:][(uls[1:] != 0) & (uty[1:] == 55)]))
        if uid_alt is not None:
            for i in np.flatnonzero((uid != uid_alt) & (uid != 0) & (uls != 0)):
                aus["neu"].append((t, int(i), int(uty[i]), int(uow[i])))
        uid_alt = uid.copy()
        fl = spalte(ud, ub, U["unknownDigMoatOrWallAttackFlag1015"])
        tile = spalte(ud, ub, U["targetedBuildingTile"])
        lg, wo, he, dh, bl = (spalte(st["DAT_TileMapState"], bas["DAT_TileMapState"], L[f]) for f in ("LogicLayer", "WallOwnerLayer", "HeightLayer", "DefaultHeightLayer", "BuildingLayer"))
        if flag_alt is not None:
            gbd, gbb = st["DAT_BuildingsState"], bas["DAT_BuildingsState"]
            gty, gow = spalte(gbd, gbb, G["buildingType"]), spalte(gbd, gbb, G["owner"])
            for i in np.flatnonzero((fl != flag_alt) & (fl != 0)):
                ti = int(tile[i])
                o = int(uow[i])
                wert = int(lg[ti]) if 0 <= ti < 80400 else 0
                geb = int(bl[ti]) if 0 <= ti < 80400 else 0
                in_liste = []
                for name, (a, zn) in LISTEN.items():
                    n = struct.unpack_from("<i", tv, ZAEHLER[zn] + o * BL - tb)[0]
                    if 0 < n <= 1000:
                        w = np.frombuffer(tv, dtype="<i4", offset=a + o * BL - tb, count=n * 4).reshape(-1, 4)
                        if ti in w[:, 0]:
                            in_liste.append(name)
                        elif ti in w[:, 1]:
                            in_liste.append(name + "2")
                aus["ziel"].append((t, int(i), int(uty[i]), o, int(fl[i]), ti, wert & 0xFFFFFFFF, geb, int(gty[geb]) if geb else 0, int(gow[geb]) if geb else 0, int(wo[ti]) if 0 <= ti < 80400 else 0, tuple(in_liste)))
        flag_alt = fl.copy()
        # Flaggen
        eb, ed = bas["DAT_EntityState"], st["DAT_EntityState"]
        el, ety, eow, etr = (spalte(ed, eb, E[f]) for f in ("logicalState", "entityType", "owner", "someTracker"))
        m = (el != 0) & np.isin(ety, FLAGGEN)
        for i in np.flatnonzero(m):
            w = int(etr[i])
            if i in flagge_alt and flagge_alt[i] != w:
                aus["flagge"].append((t, int(i), int(ety[i]), int(eow[i]), flagge_alt[i], w))
            flagge_alt[i] = w
        if not aus["flaggen_start"]:
            aus["flaggen_start"] = {(int(a), int(b)): int(c) for a, b, c in zip(*np.unique(np.vstack([ety[m], eow[m]]), axis=1), np.unique(np.vstack([ety[m], eow[m]]), axis=1, return_counts=True)[1])} if m.any() else {"keine": 0}
        # Feindliste: updateEnemyBuildings laeuft bei gameTicksLoadBalancer 0x47 bis 0x4E, der Zaehler steigt danach um 1
        gbd, gbb = st["DAT_BuildingsState"], bas["DAT_BuildingsState"]
        gty, gow, gls = spalte(gbd, gbb, G["buildingType"]), spalte(gbd, gbb, G["owner"]), spalte(gbd, gbb, G["logicalState"])
        if 0x47 <= rr["bal"] - 1 <= 0x4E:
            sp = rr["bal"] - 1 - 0x46
            ta = np.array(team)
            mm = (gls != 0) & (gls != 3) & (ta[np.clip(gow, 0, 8)] != team[sp])
            mm[0] = False
            ohne = mm & ~np.isin(gty, AUS)
            n = rr[sp]["index"]
            ids = np.frombuffer(gs, dtype="<i4", offset=EN[0] + sp * EN[1] - gb, count=max(n, 0))
            aus["feind"].append((t, sp, n, int(ohne.sum()), int(mm.sum()), int(np.isin(gty[ids], AUS).sum()) if n > 0 else 0, int((ta[np.clip(gow[ids], 0, 8)] == team[sp]).sum()) if n > 0 else 0))
        # Neue Gebaeude
        guid = spalte(gbd, gbb, G["uid"])
        if geb_uid_alt is not None:
            for i in np.flatnonzero((guid != geb_uid_alt) & (guid != 0) & (gls != 0)):
                aus["neu_geb"].append((t, int(i), int(gty[i]), int(gow[i]), struct.unpack_from("<i", gbd, G["attackWave"][0] + int(i) * G["attackWave"][2] - gbb)[0]))
        geb_uid_alt = guid.copy()
        # Zaehler recomputeAttackInfo
        for sp in range(1, 9):
            z = {n: struct.unpack_from("<i", tv, a + sp * BL - tb)[0] for n, a in ZAEHLER.items()}
            if zaehler_alt.get(sp) != z:
                ziel = rr[sp]["attackedPlayerID"]
                maske = None
                if 1 <= ziel <= 8:
                    kosten = np.frombuffer(st["DAT_TileMapState"], dtype=np.uint8, offset=0x1EE2998 + ziel * 0x13A10 - bas["DAT_TileMapState"], count=80400)
                    lw = lg.astype(np.int64) & 0xFFFFFFFF
                    maske = ((lw & 0x300) != 0) & ((lw & 2) == 0) & (kosten != 0) & (((wo.astype(np.int32) & 7) + 1) == ziel) & ((he.astype(np.int32) & 255) - (dh.astype(np.int32) & 255) > 0x14) & (bl == 0)
                aus["zaehler"].setdefault(sp, []).append((t, ziel, z, int(maske.sum()) if maske is not None else None))
                zaehler_alt[sp] = z
        aus["R"][t] = rr
    return aus


if __name__ == "__main__":
    basis = sys.argv[1]
    daten = {}
    for f in ("t1", "t6", "t8"):
        daten[f] = fenster(f"{basis}_{f}.auge")
        print(f, "Takte", len(daten[f]["R"]), "von", min(daten[f]["R"]), "bis", max(daten[f]["R"]), "neue Einheiten", len(daten[f]["neu"]), "Flaggen", len(daten[f]["flagge"]), "Ziele", len(daten[f]["ziel"]), "Feindliste", len(daten[f]["feind"]), "neue Gebaeude", len(daten[f]["neu_geb"]), flush=True)
    with open(os.path.join(HIER, "reihen6.pkl"), "wb") as d:
        pickle.dump(daten, d)
    print("geschrieben")
