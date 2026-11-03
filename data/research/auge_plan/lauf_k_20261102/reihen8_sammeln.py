# -*- coding: utf-8 -*-
"""B-142 Lauf K: Letzter Durchgang durch die Hauptaufzeichnung: Ziele der Einheiten (P295), Mauerzaehler (P289), Gold beim Ingenieur (P258), Feuer (P268), Schutt-Tabelle (P246). Speichert nach reihen8.pkl (bleibt lokal).

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/reihen8_sammeln.py <basis>
Die Karte wird seltener gelesen als die Einheiten: Das Alter der gelesenen Karte steht mit in den Daten.
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
TYP = {1: "<i1", 2: "<i2", 4: "<i4"}
U = {f: k.adresse("DAT_UnitsState", "units[]." + f) for f in ("unitType", "owner", "unknownDigMoatOrWallAttackFlag1015", "targetedBuildingTile")}
G = {f: k.adresse("DAT_BuildingsState", "buildings[]." + f) for f in ("buildingType", "owner", "fireDuration", "logicalState")}
L = {f: k.adresse("DAT_TileMapState", f + "[]") for f in ("LogicLayer", "WallOwnerLayer", "HeightLayer", "DefaultHeightLayer", "BuildingLayer")}
ZIEL = k.adresse("DAT_GameState", "playerDataArray[].attackedPlayerID")
ING = k.adresse("DAT_GameState", "playerDataArray[].isEngineerRequired")
GOLD = k.adresse("DAT_GameState", "playerDataArray[].currentResources[]")
TAG = k.adresse("DAT_GameState", "mapAndTime.dayTicks")
RUBBLE = k.adresse("DAT_BuildingDefinedData", "DAT_BuildingShowRubbleWhenDestroyed[]")
BL = 0x177BC
ZAEHLER = {"hack_c": 0x1793518, "hack_8": 0x179351C, "scale_10": 0x17973C0, "scale_c": 0x17973C4, "scale_8": 0x17973C8, "wide_c": 0x17A6E34, "wide_8": 0x17A6E38, "moat_c": 0x17A2F98, "moat_8": 0x17A2F9C, "gate_8": 0x179F100, "town_8": 0x179B264}
LISTEN = {"hack": (0x1793524, "hack_8"), "scale": (0x17973D0, "scale_8"), "wide": (0x17A6E40, "wide_8"), "moat": (0x17A2FA4, "moat_8"), "gate": (0x179F108, "gate_8"), "town": (0x179B26C, "town_8")}
E = {f: k.adresse("DAT_EntityState", "entityArray[]." + f) for f in ("logicalState", "entityType", "owner", "someTracker")}
NERV = {f: k.adresse("DAT_GameState", "playerDataArray[]." + f) for f in ("aiNervousActionsTracker", "aiBuildingDestroyChoiceTracker")}
FLAGGEN = (10, 11, 12)


def spalte(p, b, f):
    a, gr, s, n = f
    return np.ndarray(shape=(n,), dtype=TYP[gr], buffer=p, offset=a - b, strides=(s,))


def sammeln(pfad):
    auf = aw.Aufzeichnung(pfad)
    bas = {b[0]: b[1] for b in auf.bereiche}
    st = {}
    aus = {"ziel": [], "zaehler": {}, "ing": [], "feuer": collections.Counter(), "feuer_runden": 0, "rubble": None, "runden": 0, "flagge": [], "nerv": {}}
    flag_alt = None
    flagge_alt = {}
    nerv_alt = {}
    zaehler_alt = {}
    ing_alt = {}
    gold_alt = {}
    karte_takt = 0
    for r, p, _ in auf.staende():
        name = auf.namen[r.bereich]
        st[name] = p
        if name == "DAT_TileMapState":
            karte_takt = r.takt
        if name == "datenblock" and aus["rubble"] is None:
            aus["rubble"] = list(struct.unpack_from("<110i", p, RUBBLE[0] - bas[name]))
        if name != "DAT_TroopValueState" or "DAT_TileMapState" not in st:
            continue
        t = r.takt
        aus["runden"] += 1
        gs, gb = st["DAT_GameState"], bas["DAT_GameState"]
        tv, tb = p, bas[name]
        ud, ub = st["DAT_UnitsState"], bas["DAT_UnitsState"]
        gd, gbb = st["DAT_BuildingsState"], bas["DAT_BuildingsState"]
        tm, tmb = st["DAT_TileMapState"], bas["DAT_TileMapState"]
        lg, wo, he, dh, bl = (spalte(tm, tmb, L[f]) for f in ("LogicLayer", "WallOwnerLayer", "HeightLayer", "DefaultHeightLayer", "BuildingLayer"))
        uty, uow, fl, tile = (spalte(ud, ub, U[f]) for f in ("unitType", "owner", "unknownDigMoatOrWallAttackFlag1015", "targetedBuildingTile"))
        gty, gow, gfi, gls = (spalte(gd, gbb, G[f]) for f in ("buildingType", "owner", "fireDuration", "logicalState"))
        if flag_alt is not None:
            for i in np.flatnonzero((fl != flag_alt) & (fl != 0)):
                ti = int(tile[i])
                o = int(uow[i])
                gueltig = 0 <= ti < 80400
                in_liste = []
                if 1 <= o <= 8:
                    for ln, (a, zn) in LISTEN.items():
                        n = struct.unpack_from("<i", tv, ZAEHLER[zn] + o * BL - tb)[0]
                        if 0 < n <= 1000:
                            w = np.frombuffer(tv, dtype="<i4", offset=a + o * BL - tb, count=n * 4).reshape(-1, 4)
                            if ti in w[:, 0]:
                                in_liste.append(ln)
                            elif ti in w[:, 1]:
                                in_liste.append(ln + "2")
                geb = int(bl[ti]) if gueltig else 0
                aus["ziel"].append((t, int(i), int(uty[i]), o, int(fl[i]), ti, int(lg[ti]) & 0xFFFFFFFF if gueltig else 0, geb, int(gty[geb]) if geb else 0, int(gow[geb]) if geb else 0, int(wo[ti]) if gueltig else 0, tuple(in_liste), t - karte_takt))
        flag_alt = fl.copy()
        for sp in range(1, 9):
            z = {n: struct.unpack_from("<i", tv, a + sp * BL - tb)[0] for n, a in ZAEHLER.items()}
            if zaehler_alt.get(sp) != z:
                ziel = struct.unpack_from("<i", gs, ZIEL[0] + sp * ZIEL[2] - gb)[0]
                mauer = None
                if 1 <= ziel <= 8:
                    kosten = np.frombuffer(tm, dtype=np.uint8, offset=0x1EE2998 + ziel * 0x13A10 - tmb, count=80400)
                    lw = lg.astype(np.int64) & 0xFFFFFFFF
                    maske = ((lw & 0x300) != 0) & ((lw & 2) == 0) & (kosten != 0) & (((wo.astype(np.int32) & 7) + 1) == ziel) & ((he.astype(np.int32) & 255) - (dh.astype(np.int32) & 255) > 0x14) & (bl == 0)
                    mauer = int(maske.sum())
                aus["zaehler"].setdefault(sp, []).append((t, ziel, z, mauer, t - karte_takt))
                zaehler_alt[sp] = z
            w = struct.unpack_from({1: "<b", 2: "<h", 4: "<i"}[ING[1]], gs, ING[0] + sp * ING[2] - gb)[0]
            g = struct.unpack_from("<i", gs, GOLD[0] + sp * GOLD[2] + 60 - gb)[0]
            if ing_alt.get(sp, 0) and not w:
                aus["ing"].append((t, sp, gold_alt.get(sp), g, struct.unpack_from("<i", gs, TAG[0] - gb)[0]))
            ing_alt[sp] = w
            gold_alt[sp] = g
        # P242 Flaggen und der Nervositaets-Merker, damit auch der Wert 3 gegen die Regel steht
        ed, eb = st["DAT_EntityState"], bas["DAT_EntityState"]
        el, ety, eow, etr = (spalte(ed, eb, E[f]) for f in ("logicalState", "entityType", "owner", "someTracker"))
        for i in np.flatnonzero((el != 0) & np.isin(ety, FLAGGEN)):
            w = int(etr[i])
            if i in flagge_alt and flagge_alt[i] != w:
                aus["flagge"].append((t, int(i), int(ety[i]), int(eow[i]), flagge_alt[i], w))
            flagge_alt[i] = w
        for sp in range(1, 9):
            w = tuple(struct.unpack_from("<i", gs, v[0] + sp * v[2] - gb)[0] for v in NERV.values())
            if nerv_alt.get(sp) != w:
                aus["nerv"].setdefault(sp, []).append((t,) + w)
                nerv_alt[sp] = w
        brennt = (gfi != 0) & (gls != 0)
        if brennt.any():
            aus["feuer_runden"] += 1
            for a, c in zip(*np.unique(gty[brennt], return_counts=True)):
                aus["feuer"][int(a)] = max(aus["feuer"][int(a)], int(c))
    return aus


if __name__ == "__main__":
    basis = sys.argv[1]
    d = sammeln(basis + "_danach.auge")
    print("Runden", d["runden"], "Ziele", len(d["ziel"]), "Ingenieure", len(d["ing"]), "Runden mit Feuer", d["feuer_runden"], flush=True)
    with open(os.path.join(HIER, "reihen8.pkl"), "wb") as f:
        pickle.dump(d, f)
    print("geschrieben")
