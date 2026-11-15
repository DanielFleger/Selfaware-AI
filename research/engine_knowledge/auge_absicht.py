# -*- coding: utf-8 -*-
"""B-251 Punkt 6: KI-Absicht gegen Verhalten - Auswertung eines Langzeit-Protokolls (auge.protokollieren mit Trupps).

Liest je Schnappschuss den KI-Spieler (aiPlayerState, attackTicker, attackedPlayerID, totalAttackTroops ...), seine Trupps
(targetBuildingID, target, unitStance, rallyPoints) und seine Einheiten (Ort, Ziel) und misst:
  - wann aiPlayerState wechselt und was die Einheiten danach tun (Vorlauf bis zur ersten Bewegung Richtung Ziel)
  - wann ein Trupp ein Zielgebaeude bekommt und wann seine erste Einheit dort ankommt
Aufruf: python werkzeug/engine_knowledge/auge_absicht.py daten/auge_protokoll_<stempel>.npz [ki_spieler=2]
"""
import json
import os
import sys

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HIER))
import auge  # noqa: E402

MILITAER = list(range(22, 62)) + list(range(70, 80))   # Soldaten + Geraete, ohne Arbeiter (1-21) und Zivilisten (62-64 Huhn/Kuh?/Kind)

ZUSTAND = {0: "0 warten/sammeln", 1: "1 Angriff beschlossen", 2: "2 Sammeln am Treffpunkt", 3: "3 Ausruecken", 4: "4 Anmarsch/Sturm",
           5: "5 Mauern angreifen", 6: "6 Bresche, rein", 7: "7 Ziel tot, warten", 8: "8 Rueckzug", 9: "9 Aufraeumen"}


def auswerten(pfad, ki=2):
    L = auge.Protokoll.laden(pfad)
    aus = {"protokoll": os.path.basename(pfad), "takte": [L[0].takt, L[-1].takt], "schnappschuesse": len(L), "ki": ki,
           "zustandswechsel": [], "trupp_ziele": [], "attackTicker": []}
    letzter = None
    letzter_ticker = None
    for s in L:
        r = s.spieler[ki]
        z = int(r["aiPlayerState"])
        tk = int(r["attackTicker"])
        if letzter_ticker is not None and tk != letzter_ticker:
            aus["attackTicker"].append([s.takt, tk])
        letzter_ticker = tk
        if z != letzter:
            u = s.einheiten
            m = (u["owner"] == ki) & (u["logicalState"] == 2)
            aus["zustandswechsel"].append({
                "takt": s.takt, "aiPlayerState": z, "name": ZUSTAND.get(z, str(z)), "attackTicker": tk,
                "attackedPlayerID": int(r["attackedPlayerID"]), "totalAttackTroops": int(r["totalAttackTroops"]),
                "totalTroopValue": int(r["totalTroopValue"]), "totalEnemyTroopValue": int(r["totalEnemyTroopValue"]),
                "aiStrengthFeeling": int(r["aiStrengthFeeling"]), "einheiten": int(np.count_nonzero(m)),
                "soldaten_unterwegs": int(np.count_nonzero(m & (u["state"] == 101) & np.isin(u["unitType"], MILITAER))),
                "gold": int(r["currentResources"][15]), "armySize": int(r["armySize"]),
            })
            letzter = z
    # Trupp-Ziele: erstes Setzen von targetBuildingID je Trupp und erste Einheit des Trupps am Zielgebaeude
    gesehen = {}
    for s in L:
        t = s.trupps
        if not len(t):
            continue
        idx = s._trupps_idx
        for j in range(len(t)):
            r = t[j]
            if int(r["owner"]) != ki:
                continue
            tid = int(idx[j])
            ziel = int(r["targetBuildingID"])
            k = (tid, ziel, int(r["targetBuildingUID"]))
            if ziel and k not in gesehen:
                gesehen[k] = {"takt_gesetzt": s.takt, "trupp": tid, "tribeType": int(r["tribeType"]), "unitType": int(r["unitType"]),
                              "size": int(r["size"]), "targetBuildingID": ziel, "unitStance": int(r["unitStance"]),
                              "target": [int(r["targetX"]), int(r["targetY"])], "ankunft_takt": None, "abstand_start": None}
    # Ankunft: erste Einheit mit tribeID == trupp in <= 3 Feldern um das Zielgebaeude (Ort aus Gebaeude-Liste ist im Protokoll nicht
    # enthalten -> ueber targetedBuildingTile der Einheiten / das Zielfeld des Trupps naehern)
    for k, e in gesehen.items():
        tid = e["trupp"]
        zx, zy = e["target"]
        if zx == 0 and zy == 0:
            continue
        for s in L:
            if s.takt < e["takt_gesetzt"]:
                continue
            u = s.einheiten
            m = (u["owner"] == ki) & (u["logicalState"] == 2) & (u["tribeID"] == tid)
            if not m.any():
                continue
            d = np.maximum(np.abs(u["x"][m].astype(int) - zx), np.abs(u["y"][m].astype(int) - zy))
            if e["abstand_start"] is None:
                e["abstand_start"] = int(d.min())
            if d.min() <= 3:
                e["ankunft_takt"] = s.takt
                break
        if e["ankunft_takt"] is not None:
            e["vorlauf_takte"] = e["ankunft_takt"] - e["takt_gesetzt"]
    aus["trupp_ziele"] = list(gesehen.values())
    return aus


def main():
    pfad = sys.argv[1]
    ki = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    erg = auswerten(pfad, ki)
    out = pfad.replace(".npz", "_absicht.json")
    json.dump(erg, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Takte", erg["takte"], "Schnappschuesse", erg["schnappschuesse"])
    print("attackTicker-Aenderungen:", erg["attackTicker"][:12])
    for z in erg["zustandswechsel"]:
        print(" ", json.dumps(z, ensure_ascii=False))
    for t in erg["trupp_ziele"][:25]:
        print("  Trupp", json.dumps(t, ensure_ascii=False))
    print("->", out)


if __name__ == "__main__":
    main()
