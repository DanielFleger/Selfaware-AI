# -*- coding: utf-8 -*-
"""B-142 Lauf K: Aus der Hauptaufzeichnung des Kampfs: Graben-Gruppe, Ziele der Gruppen, neue Belagerungsbauten, Angriffsrichtungen, Raubzug-Truppen, Jahreswechsel, Nervositaet, Wegebene. Speichert nach reihen7.pkl (bleibt lokal).

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/reihen7_sammeln.py <basis> <Instanz>
Gerechnet wird beim Rahmen von DAT_TroopValueState: Einheiten, Gebaeude, Gruppen und Spieler sind dann schon von dieser Runde, die Karte noch von der Runde davor.
Die Umrechnung Feld zu Kartenplatz steht im Spielspeicher und aendert sich nie, darum liest das Programm sie einmal aus der Instanz (nur lesen).
"""
import collections
import os
import pickle
import struct
import sys

import numpy as np

from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz

HIER = os.path.dirname(os.path.abspath(__file__))
k = Feldkarte.laden(feldliste=FELDLISTE)
TYP = {1: "<i1", 2: "<i2", 4: "<i4"}
FMT = {1: "<b", 2: "<h", 4: "<i"}
SP = {f: k.adresse("DAT_GameState", "playerDataArray[]." + f) for f in ("aiPlayerState", "attackedPlayerID", "aiNervousActionsTracker", "relativeStrengthOfTeamComparedToEnemy", "totalEnemyRangedTroopValue", "totalRaidingTroopsUnk", "currentAttackRaidParameter", "totalAttackTroops", "totalDefensiveTroopsUnk", "aiRecruitUnitChoiceState")}
IDS = k.adresse("DAT_GameState", "playerDataArray[].aiTribeIDs[]")
UIDS = k.adresse("DAT_GameState", "playerDataArray[].aiTribeUIDs[]")
AV = k.adresse("DAT_GameState", "mapAndTime.attackVectors[]")
JAHR = k.adresse("DAT_GameState", "mapAndTime.year")
T = {f: k.adresse("DAT_TribesState", "tribes[]." + f) for f in ("uid", "owner", "selectionTargetUnitID", "unitStance", "targetBuildingID", "targetBuildingUID", "size")}
B = {f: k.adresse("DAT_BuildingsState", "buildings[]." + f) for f in ("uid", "fireDuration", "x", "y", "buildingType", "owner", "logicalState", "attackWave")}
U = {f: k.adresse("DAT_UnitsState", "units[]." + f) for f in ("x", "y", "unitType", "owner", "logicalState")}
L = {f: k.adresse("DAT_TileMapState", f + "[]") for f in ("LogicLayer", "BuildingLayer", "UnitLayer", "directionTranslationMatrix")}
HOEHE = k.adresse("DAT_TileMapState", "HeightLayer[]")
MOAT2 = k.adresse("DAT_TroopValueState", "attackInfo.playerInfo[].moat2")
SIEGE = (29, 50, 54, 69, 80, 81, 82, 83, 84, 86, 87)
MASKE_FREI = 0x4A7014B1 | 4


def spalte(p, b, f):
    a, gr, s, n = f
    return np.ndarray(shape=(n,), dtype=TYP[gr], buffer=p, offset=a - b, strides=(s,))


def sammeln(pfad, add, y_von):
    auf = aw.Aufzeichnung(pfad)
    bas = {b[0]: b[1] for b in auf.bereiche}
    st = {}
    aus = {"stance": [], "ziel_wechsel": collections.Counter(), "ziel_bsp": [], "siege": [], "vektor": [], "raub": collections.defaultdict(list), "jahr": [], "nerv": [], "bfs": None, "runden": 0}
    letzt = {}
    guid_alt = ziel_alt = zuid_alt = fire_alt = buid_alt = None
    jahr_alt = None
    raid_alt = {}
    naechster_vektor = 0
    for r, p, _ in auf.staende():
        name = auf.namen[r.bereich]
        st[name] = p
        if name != "DAT_TroopValueState" or "DAT_TileMapState" not in st:
            continue
        t = r.takt
        aus["runden"] += 1
        gs, gb = st["DAT_GameState"], bas["DAT_GameState"]
        tv, tb = p, bas[name]
        trd, trb = st["DAT_TribesState"], bas["DAT_TribesState"]
        gd, gbb = st["DAT_BuildingsState"], bas["DAT_BuildingsState"]
        ud, ub = st["DAT_UnitsState"], bas["DAT_UnitsState"]
        tm, tmb = st["DAT_TileMapState"], bas["DAT_TileMapState"]
        wert = lambda f, sp: struct.unpack_from(FMT[SP[f][1]], gs, SP[f][0] + sp * SP[f][2] - gb)[0]  # noqa: E731
        tid = lambda sp, i: struct.unpack_from("<h", gs, IDS[0] + sp * IDS[2] + i * 2 - gb)[0]  # noqa: E731
        tuid = lambda sp, i: struct.unpack_from("<i", gs, UIDS[0] + sp * UIDS[2] + i * 4 - gb)[0]  # noqa: E731
        stance, tr_uid, tr_sel, tr_ziel, tr_zuid, tr_own = (spalte(trd, trb, T[f]) for f in ("unitStance", "uid", "selectionTargetUnitID", "targetBuildingID", "targetBuildingUID", "owner"))
        # P267 Graben-Gruppe
        for sp in range(1, 9):
            i = tid(sp, 0x11)
            m2 = struct.unpack_from("<i", tv, MOAT2[0] + (sp - 1) * MOAT2[2] - tb)[0]
            gueltig = i != 0 and tr_uid[i] == tuid(sp, 0x11) and tr_sel[i] != 0
            w = (i, int(stance[i]) if i else -1, gueltig, m2 > 0, wert("aiPlayerState", sp))
            if letzt.get(("st", sp)) != w:
                aus["stance"].append((t, sp) + w + (m2,))
                letzt[("st", sp)] = w
        # P268 Ziele der Gruppen
        gu, gf = spalte(gd, gbb, B["uid"]), spalte(gd, gbb, B["fireDuration"])
        if ziel_alt is not None:
            for i in np.flatnonzero((tr_ziel != ziel_alt) & (ziel_alt != 0)):
                alt = int(ziel_alt[i])
                brennt = bool(fire_alt[alt] != 0 or gf[alt] != 0)
                weg = bool(buid_alt[alt] != zuid_alt[i] or gu[alt] != zuid_alt[i])
                z = wert("aiPlayerState", int(tr_own[i])) if 1 <= tr_own[i] <= 8 else -1
                aus["ziel_wechsel"][(brennt, weg, int(tr_ziel[i]) != 0, z)] += 1
                if len(aus["ziel_bsp"]) < 40 and not brennt and not weg:
                    aus["ziel_bsp"].append((t, int(i), int(tr_own[i]), alt, int(tr_ziel[i]), z))
        ziel_alt, zuid_alt, fire_alt, buid_alt = tr_ziel.copy(), tr_zuid.copy(), gf.copy(), gu.copy()
        # P250 Neue Belagerungsbauten
        gt, go, gx, gy, gw, gl = (spalte(gd, gbb, B[f]) for f in ("buildingType", "owner", "x", "y", "attackWave", "logicalState"))
        if guid_alt is not None:
            for i in np.flatnonzero((gu != guid_alt) & (gu != 0) & (gl != 0) & np.isin(gt, SIEGE)):
                o, bx, by = int(go[i]), int(gx[i]), int(gy[i])
                ux, uy, uty, uow, uls = (spalte(ud, ub, U[f]) for f in ("x", "y", "unitType", "owner", "logicalState"))
                gr12, gr0e = tid(o, 0x12) if 1 <= o <= 8 else 0, tid(o, 0xE) if 1 <= o <= 8 else 0
                sel = [int(tr_sel[g]) for g in (gr12, gr0e)]
                ms = (uty == 30) & (uow == o) & (uls != 0)
                naechster = None
                if ms.any():
                    naechster = int(np.max(np.abs(np.vstack([ux[ms].astype(int) - bx - 1, uy[ms].astype(int) - by - 1])), axis=0).min())
                frei = None
                if 1 <= bx + 1 < 399 and 1 <= by + 1 < 399:
                    mitte = int(add[by + 1]) + bx + 1
                    lg, bl, ul = (spalte(tm, tmb, L[f]) for f in ("LogicLayer", "BuildingLayer", "UnitLayer"))
                    dirm = np.frombuffer(tm, dtype="<i4", offset=L["directionTranslationMatrix"][0] - tmb, count=400 * 8).reshape(400, 8)
                    nb = [mitte + int(dirm[by + 1][d]) for d in range(8)]
                    hh = np.frombuffer(tm, dtype=np.uint8, offset=HOEHE[0] - tmb, count=80400)
                    frei = (sum(1 for n in nb if (int(lg[n]) & MASKE_FREI) == 0 and ul[n] == 0 and bl[n] == 0), int(hh[nb + [mitte]].max()) - int(hh[nb + [mitte]].min()), int(ul[mitte]))
                aus["siege"].append((t, int(i), int(gt[i]), o, bx, by, int(gw[i]), sel, [(int(ux[s]), int(uy[s])) if s else None for s in sel], naechster, frei))
        guid_alt = gu.copy()
        # P252 Angriffsrichtungen
        if t >= naechster_vektor:
            block = np.frombuffer(gs, dtype="<i4", offset=AV[0] - gb, count=4 * 50 * 9).reshape(9, 50, 4)
            aus["vektor"].append((t, [(int((block[z, :, 0] != 0).sum()), int((block[z, :, 3] != 0).sum()), block[z, 0].tolist(), block[z, 1].tolist()) for z in range(9)]))
            naechster_vektor = t + 2500
        # P272 Raubzug-Truppen
        for sp in range(1, 9):
            w = (wert("totalRaidingTroopsUnk", sp), wert("currentAttackRaidParameter", sp))
            if raid_alt.get(sp) != w:
                aus["raub"][sp].append((t,) + w)
                raid_alt[sp] = w
        # P275 Jahreswechsel
        jahr = struct.unpack_from("<i", gs, JAHR[0] - gb)[0]
        raub_jetzt = {(sp, i): (tid(sp, 0xB4 + i), int(tr_ziel[tid(sp, 0xB4 + i)])) for sp in range(1, 9) for i in range(6) if tid(sp, 0xB4 + i) != 0}
        if jahr_alt is not None and jahr != jahr_alt:
            aus["jahr"].append((t, jahr, raub_vorher, raub_jetzt))
        jahr_alt = jahr
        raub_vorher = raub_jetzt
        # P271 Nervositaet
        for sp in range(1, 9):
            w = wert("aiNervousActionsTracker", sp)
            if letzt.get(("n", sp)) != w:
                if w == 8:
                    aus["nerv"].append((t, sp, wert("relativeStrengthOfTeamComparedToEnemy", sp), wert("totalEnemyRangedTroopValue", sp)))
                letzt[("n", sp)] = w
        # P253 einmal die Wegebene gegen ihre Nachbarn
        if aus["bfs"] is None and t > 60000:
            dirm = np.frombuffer(tm, dtype="<i4", offset=L["directionTranslationMatrix"][0] - tmb, count=400 * 8).reshape(400, 8)
            jeder = {}
            felder = np.arange(80400)
            yy = y_von[felder]
            for ziel in range(1, 5):
                wl = np.frombuffer(tm, dtype=np.uint8, offset=0x1EE2998 + ziel * 0x13A10 - tmb, count=80400)
                zeile = {}
                for v in range(2, 7):
                    wo = np.flatnonzero(wl == v)
                    if not len(wo):
                        continue
                    nb4 = np.stack([np.clip(wo + dirm[yy[wo], d], 0, 80399) for d in (0, 2, 4, 6)])
                    nb8 = np.stack([np.clip(wo + dirm[yy[wo], d], 0, 80399) for d in range(8)])
                    zeile[v] = (len(wo), int((wl[nb4] == v - 1).any(axis=0).sum()), int((wl[nb8] == v - 1).any(axis=0).sum()))
                jeder[ziel] = zeile
            aus["bfs"] = (t, jeder)
    aus["raub"] = dict(aus["raub"])
    return aus


if __name__ == "__main__":
    basis, n = sys.argv[1], int(sys.argv[2])
    q = ProzessQuelle(pid_der_instanz(n))
    ad = k.adresse("DAT_ViewportRenderState", "translationMatrix[].addXgetTile")
    add = [struct.unpack("<i", q.lies(ad[0] + y * ad[2], 4))[0] for y in range(400)]
    yv = k.adresse("DAT_ViewportRenderState", "tileTranslationMatrix_YComponent[]")
    y_von = np.frombuffer(q.lies(yv[0], 80400 * 2), dtype="<i2").copy()
    daten = sammeln(basis + "_danach.auge", add, y_von)
    print("Runden", daten["runden"], "neue Belagerungsbauten", len(daten["siege"]), "Graben-Eintraege", len(daten["stance"]), "Jahreswechsel", len(daten["jahr"]), flush=True)
    with open(os.path.join(HIER, "reihen7.pkl"), "wb") as d:
        pickle.dump(daten, d)
    print("geschrieben")
