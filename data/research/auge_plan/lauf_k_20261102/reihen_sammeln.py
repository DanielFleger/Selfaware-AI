# -*- coding: utf-8 -*-
"""B-142: Zeitreihen aus den Aufzeichnungen von Lauf K fuer die Einzelpunkte. Speichert nach reihen.pkl (bleibt lokal, siehe .gitignore).

Aufruf aus dem Arbeitsbaum: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/reihen_sammeln.py <basis>
Je Feld stehen nur die Wechsel drin: (Takt, Wert). Spieler 1 bis 8, Gruppen und Gebaeude je Platz, Einheiten als Zaehlung je Spieler und Typ.
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
karte = Feldkarte.laden(feldliste=FELDLISTE)
FMT = {1: "<B", 2: "<h", 4: "<i"}
LORD = 55

SPIELER = ["aiType", "aiPlayerState", "attackedPlayerID", "aiRecruitUnitChoiceState", "requestStateUnk", "canStartSpending", "harrassingSiegeEnginesIndex", "totalTroopsType6", "unknownCounter_01", "totalTroopsType7",
           "totalAttackTroops", "totalAttackingEngineerTroops", "currentWaveRandomAttackingStrength", "currentAttackWave", "currentAttackRaidParameter", "shortestDistanceX", "shortestDistanceY", "aiAttackCoordinationLevel",
           "relativeStrengthOfTeamComparedToEnemy", "aiStrengthState", "aiStrengthFeeling", "isNotNervousByEnemyTroopValue", "aiNervousActionsTracker", "attackTicker", "popularity", "currentPopulation", "lordID", "lordUID",
           "lordKilledByPlayerID", "armySize", "fearFactorLevel", "taxesSetting", "rationsSetting"]
KAL = ["year", "month", "week", "dayTicks", "weekTicks", "monthTicks", "yearChanged", "monthChanged", "weekChanged", "totalNoRushTicks", "noRushTicksLeftUnk", "countUpTo201", "playerBuildingInfoIndex[]", "armySizeLimit"]
ANGRIFF = ["attacker", "macemenTribeCount", "tentPoints", "moat2", "gate2", "wide3", "spearmenAndMacemen", "pikemenSwordsmenAndMore", "laddermen", "engineers", "ranged", "knights", "field86974_0x20f74", "field86627_0x20e04"]
GRUPPE = ["owner", "tribeState", "tribeType", "size", "targetPlayer_outpost", "targetBuildingID", "randomNumber", "counter", "targetX", "targetY"]
GEBAEUDE = ["buildingType", "owner", "logicalState", "noRubble", "tribeID", "outpostRelatedUnk05", "outpostRelatedUnk06", "incByFourUnk", "field268_0x308", "health"]
EINHEIT = ["unknownDigMoatOrWallAttackFlag1015", "aiUnitBehaviourType", "siegeTargetPlayerID"]


def ort(g, p):
    try:
        return karte.adresse(g, p)
    except Exception as e:  # noqa: BLE001  ein unbekanntes Feld steht dann in der Ausgabe
        print("kein Feld", g, p, str(e)[:60])
        return None


O_SP = {f: ort("DAT_GameState", "playerDataArray[]." + f) for f in SPIELER}
O_SP = {f: v for f, v in O_SP.items() if v}
GOLD = ort("DAT_GameState", "playerDataArray[].currentResources[]")
O_KAL = {f: ort("DAT_GameState", "mapAndTime." + f) for f in KAL}
O_KAL = {f: v for f, v in O_KAL.items() if v}
O_ANG = {f: ort("DAT_TroopValueState", "attackInfo." + f) for f in ANGRIFF}
O_ANG = {f: v for f, v in O_ANG.items() if v}
WELLE = ort("DAT_TroopValueState", "attackInfo.value3Array01[]")
TICKER = ort("DAT_TroopValueState", "attackInfo.attackWaveTicker[]")
O_GR = {f: ort("DAT_TribesState", "tribes[]." + f) for f in GRUPPE}
O_GR = {f: v for f, v in O_GR.items() if v}
O_GEB = {f: ort("DAT_BuildingsState", "buildings[]." + f) for f in GEBAEUDE}
O_GEB = {f: v for f, v in O_GEB.items() if v}
O_EIN = {f: ort("DAT_UnitsState", "units[]." + f) for f in EINHEIT}
O_EIN = {f: v for f, v in O_EIN.items() if v}
U_TYP = ort("DAT_UnitsState", "units[].unitType")
U_DA = ort("DAT_UnitsState", "units[].logicalState")
U_BES = ort("DAT_UnitsState", "units[].owner")
TYP = {1: "<i1", 2: "<i2", 4: "<i4"}


def spalte(p, basis, adr, gr, schritt, anzahl):
    return np.ndarray(shape=(anzahl,), dtype=TYP.get(gr, "<i4"), buffer=p, offset=adr - basis, strides=(schritt,))


def sammeln(pfad):
    auf = aw.Aufzeichnung(pfad)
    idx = {n: i for i, n in enumerate(auf.namen)}
    bas = {n: auf.bereiche[i][1] for n, i in idx.items()}
    aus = {"spieler": collections.defaultdict(list), "gold": collections.defaultdict(list), "kal": collections.defaultdict(list), "angriff": collections.defaultdict(list), "welle": [], "ticker": [],
           "gruppe": collections.defaultdict(list), "geb": collections.defaultdict(list), "einh_feld": collections.defaultdict(list), "zaehl": [], "lords": [], "takte": []}
    letzt = {}
    alt_sp = {}
    naechste_zaehlung = 0

    def merke(tab, k, t, w):
        if letzt.get((id(tab), k)) != w:
            tab[k].append((t, w))
            letzt[(id(tab), k)] = w

    for r, p, _ in auf.staende():
        name = auf.namen[r.bereich]
        t = r.takt
        if name == "DAT_GameState":
            aus["takte"].append(t)
            b = bas[name]
            for f, (a, gr, s, n) in O_SP.items():
                werte = struct.unpack_from(f"<{FMT[gr][1]}", p, a - b) if False else None
                for sp in range(1, 9):
                    w = struct.unpack_from(FMT.get(gr, "<i"), p, a + sp * s - b)[0]
                    merke(aus["spieler"], (sp, f), t, w)
            for sp in range(1, 9):
                w = struct.unpack_from("<i", p, GOLD[0] + sp * GOLD[2] + 15 * 4 - b)[0]
                merke(aus["gold"], sp, t, w)
            for f, (a, gr, s, n) in O_KAL.items():
                w = struct.unpack_from(FMT.get(gr, "<i"), p, a - b)[0]
                merke(aus["kal"], f, t, w)
        elif name == "DAT_TroopValueState":
            b = bas[name]
            for f, (a, gr, s, n) in O_ANG.items():
                merke(aus["angriff"], f, t, struct.unpack_from(FMT.get(gr, "<i"), p, a - b)[0])
            w = struct.unpack_from("<50i", p, WELLE[0] - b)
            if letzt.get("welle") != w:
                aus["welle"].append((t, w))
                letzt["welle"] = w
            w = struct.unpack_from("<50i", p, TICKER[0] - b)
            if letzt.get("ticker") != w:
                aus["ticker"].append((t, w))
                letzt["ticker"] = w
        elif name == "DAT_TribesState":
            b = bas[name]
            for f, (a, gr, s, n) in O_GR.items():
                v = spalte(p, b, a, gr, s, n).copy()
                alt = alt_sp.get(("g", f))
                if alt is None:
                    for i in np.flatnonzero(v):
                        aus["gruppe"][(int(i), f)].append((t, int(v[i])))
                else:
                    for i in np.flatnonzero(v != alt):
                        aus["gruppe"][(int(i), f)].append((t, int(v[i])))
                alt_sp[("g", f)] = v
        elif name == "DAT_BuildingsState":
            b = bas[name]
            for f, (a, gr, s, n) in O_GEB.items():
                v = spalte(p, b, a, gr, s, n).copy()
                alt = alt_sp.get(("b", f))
                if alt is None:
                    for i in np.flatnonzero(v):
                        aus["geb"][(int(i), f)].append((t, int(v[i])))
                else:
                    for i in np.flatnonzero(v != alt):
                        aus["geb"][(int(i), f)].append((t, int(v[i])))
                alt_sp[("b", f)] = v
        elif name == "DAT_UnitsState":
            b = bas[name]
            typ = spalte(p, b, U_TYP[0], 2, U_TYP[2], U_TYP[3])
            da = spalte(p, b, U_DA[0], 2, U_DA[2], U_DA[3])
            bes = spalte(p, b, U_BES[0], 2, U_BES[2], U_BES[3])
            lebend = da[1:] != 0
            lords = tuple(sorted(int(x) for x in bes[1:][lebend & (typ[1:] == LORD)]))
            if letzt.get("lords") != lords:
                aus["lords"].append((t, lords))
                letzt["lords"] = lords
            for f, (a, gr, s, n) in O_EIN.items():
                v = spalte(p, b, a, gr, s, n).copy()
                alt = alt_sp.get(("u", f))
                if alt is not None:
                    for i in np.flatnonzero(v != alt)[:200]:
                        aus["einh_feld"][f].append((t, int(i), int(typ[i]), int(bes[i]), int(v[i])))
                alt_sp[("u", f)] = v
            if t >= naechste_zaehlung:
                z = collections.Counter(zip(bes[1:][lebend].tolist(), typ[1:][lebend].tolist()))
                aus["zaehl"].append((t, dict(z)))
                naechste_zaehlung = t + 500
    for k in ("spieler", "gold", "kal", "angriff", "gruppe", "geb", "einh_feld"):
        aus[k] = dict(aus[k])
    return aus


if __name__ == "__main__":
    basis = sys.argv[1]
    daten = {}
    for k, e in (("haupt", ".auge"), ("t1", "_t1.auge"), ("danach", "_danach.auge")):
        if os.path.exists(basis + e):
            daten[k] = sammeln(basis + e)
            print(k, len(daten[k]["takte"]), "Lord-Wechsel", len(daten[k]["lords"]), flush=True)
    with open(os.path.join(HIER, "reihen.pkl"), "wb") as f:
        pickle.dump(daten, f)
    print("geschrieben", {k: (len(v["takte"]), len(v["spieler"]), len(v["gruppe"]), len(v["geb"])) for k, v in daten.items()})
