# -*- coding: utf-8 -*-
"""B-142: Zeitreihen aus den Aufzeichnungen von Lauf F (02.11.2026 21:42) fuer die Einzelpunkte. Speichert nach reihen.pkl (bleibt lokal, siehe .gitignore).

Aufruf aus dem Arbeitsbaum: PYTHONPATH=src python data/research/auge_plan/lauf_f_20261102/reihen_sammeln.py
Je Feld stehen nur die Wechsel drin: (Takt, Wert). Spieler 1, Gebaeude je Platz, Einheiten je Platz.
"""
import os
import pickle
import struct

from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

HIER = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HIER, "..", "laeufe", "lauf_f_20261102_214240")
karte = Feldkarte.laden(feldliste=FELDLISTE)
SP0 = aw.SPIELERDATEN
SP = SP0 + aw.SPIELER_SCHRITT
G0, GS = 0xF98520, 0x32C
U0, US = 0x0138854C, 1168
FMT = {1: "<B", 2: "<h", 4: "<i"}

SPIELER = ["fearFactorLevel", "goodStuffCount", "badStuffCount", "currentPopulation", "populationCap", "lastMonthsIncomeTax", "lastMonthsBribeTax", "taxesSetting", "rationsSetting", "foodClockSpeed", "availableHorses",
           "aleRate", "vclock", "popularity", "populationIndex", "moatsOwned", "armySize", "count", "count_2", "totalFood", "breadCount", "cheeseCount", "meatCount", "appleCount", "religionVar1", "storageMarketFailState",
           "taxIncomeMonthlyAccumulator", "taxBribeMonthlyAccumulator", "availablePeasantsAtFire", "countSlingers2", "foodTypesInStock", "foodTypesCurrentlyEaten", "fearFactorProductivityUnk", "dairyFarmVariationMod4", "healerCount",
           "beerPercentage", "popularityChangeAleBased", "popularityChangeBasedOnReligion", "popularityChangeBasedOnFood", "popularityChangeBasedOnTax", "popularityChangeFearFactorBased"]
GEBAEUDE = ["growCounter", "farmGrowState", "outpostRelatedUnk4", "numberOfAnimals", "flagonsOfAleOrCheeseOrReleaseDogs", "state", "sleeping", "gateState", "gateCloseOpenTimer", "hovelVisualStyle", "producedItemTypeNext",
            "quarryStockpileID", "cooldownTimer", "resourceStone", "currentlyNeededEmployeeCount", "logicalState", "uid"]


def ort(global_name, pfad):
    try:
        a = karte.adresse(global_name, pfad)
        return a[0], a[1]
    except Exception as e:  # noqa: BLE001  ein unbekanntes Feld steht dann in der Ausgabe
        print("kein Feld", pfad, e)
        return None


O_SP = {f: (SP + ort("DAT_GameState", "playerDataArray[]." + f)[0] - SP0, ort("DAT_GameState", "playerDataArray[]." + f)[1]) for f in SPIELER if ort("DAT_GameState", "playerDataArray[]." + f)}
O_G = {f: (ort("DAT_BuildingsState", "buildings[]." + f)[0] - G0, ort("DAT_BuildingsState", "buildings[]." + f)[1]) for f in GEBAEUDE if ort("DAT_BuildingsState", "buildings[]." + f)}
O_RES = ort("DAT_UnitsState", "units[].resourceToDeposit")
K = {n: ort("DAT_GameState", "mapAndTime." + n) for n in ("year", "month", "week", "dayTicks", "weekTicks", "monthTicks", "weekChanged", "monthChanged")}


def sammeln(pfad):
    auf = aw.Aufzeichnung(pfad)
    g, b, u = (auf.namen.index(n) for n in ("DAT_GameState", "DAT_BuildingsState", "DAT_UnitsState"))
    gb, bb, ub = auf.bereiche[g][1], auf.bereiche[b][1], auf.bereiche[u][1]
    aus = {"spieler": {f: [] for f in O_SP}, "waren": [], "start": [], "kal": {n: [] for n in K}, "geb": {}, "typ_geb": {}, "last": {}, "einh": [], "takte": []}
    letzt_sp, letzt_k, letzt_g, letzt_u = {}, {}, {}, {}
    letzt_w = letzt_s = None
    best = aw.SPIELERDATEN + aw.SPIELER_SCHRITT + aw.FELD_BESTAND - gb
    start = aw.SPIELERDATEN + aw.SPIELER_SCHRITT + aw.FELD_START - gb
    for r, p, teile in auf.staende():
        if r.bereich == g:
            aus["takte"].append(r.takt)
            for f, (a, gr) in O_SP.items():
                w = struct.unpack_from(FMT.get(gr, "<i"), p, a - gb)[0]
                if letzt_sp.get(f) != w:
                    aus["spieler"][f].append((r.takt, w))
                    letzt_sp[f] = w
            for n, o in K.items():
                w = struct.unpack_from(FMT.get(o[1], "<i"), p, o[0] - gb)[0]
                if letzt_k.get(n) != w:
                    aus["kal"][n].append((r.takt, w))
                    letzt_k[n] = w
            w = struct.unpack_from("<25i", p, best)
            if w != letzt_w:
                aus["waren"].append((r.takt, w))
                letzt_w = w
            w = struct.unpack_from("<25i", p, start)
            if w != letzt_s:
                aus["start"].append((r.takt, w))
                letzt_s = w
        elif r.bereich == b:
            for i in range(1, 140):
                ba = G0 + i * GS - bb
                typ = struct.unpack_from("<h", p, ba + aw.GEBAEUDE_TYP)[0]
                if not typ:
                    continue
                aus["typ_geb"][i] = typ
                for f, (a, gr) in O_G.items():
                    w = struct.unpack_from(FMT.get(gr, "<i"), p, ba + a)[0]
                    k = (i, f)
                    if letzt_g.get(k) != w:
                        aus["geb"].setdefault(k, []).append((r.takt, w))
                        letzt_g[k] = w
        elif r.bereich == u:
            n = 160
            for i in range(1, n):
                ba = U0 + i * US - ub
                if not struct.unpack_from("<h", p, ba + 0x8C)[0]:
                    continue
                typ = struct.unpack_from("<h", p, ba + 0x8E)[0]
                res = struct.unpack_from(FMT.get(O_RES[1], "<i"), p, O_RES[0] + i * US - ub)[0]
                k = i
                if letzt_u.get(k) != (typ, res):
                    aus["einh"].append((r.takt, i, typ, res))
                    letzt_u[k] = (typ, res)
    return aus


if __name__ == "__main__":
    daten = {"haupt": sammeln(B + ".auge"), "jahr": sammeln(B + "_jahr40.auge")}
    with open(os.path.join(HIER, "reihen.pkl"), "wb") as f:
        pickle.dump(daten, f)
    print({k: (len(v["takte"]), len(v["waren"]), len(v["geb"]), len(v["einh"])) for k, v in daten.items()})
