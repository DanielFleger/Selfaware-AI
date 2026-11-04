# -*- coding: utf-8 -*-
"""Daniels Angaben: (1) Feuerkorb nur auf Bergfried, Tuerme, Torhaeuser, Mauern, keine Zinnen. Die Oberflaeche fragt getHeightAtTileIncludingOwnersBuildings: 0 heisst nein.
(2) Koennen sich KI etwas schicken? Befehl 113 Unterart 2 (ProcessAllyGoodsRequest). Stehendes KI-Gefecht, Instanz 2, Messlauf."""
import collections
import glob
import json
import os
import re
import time

from selfaware.tools.experiments import auge_lauf_f as lf
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.experiments.auge_lauf_s import SpeicherS
from selfaware.tools.experiments.spielcode_rufen import Rufer
from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz

D = r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference\functions"
F_HOEHE = None
for f in os.listdir(D):
    with open(os.path.join(D, f), encoding="utf-8") as d:
        if "getHeightAtTileIncludingOwnersBuildings" in d.read(300):
            F_HOEHE = int(f[:-5], 16)
            break
print("Hoehenfunktion", hex(F_HOEHE))
K = Feldkarte.laden(feldliste=FELDLISTE)
TM = K.struktur("DAT_TileMapState")[0]
lo, ba, en = K.adresse("DAT_TileMapState", "LogicLayer[]"), K.adresse("DAT_TileMapState", "BuildingLayer[]"), K.adresse("DAT_TileMapState", "EntityLayer[]")
wa = K.adresse("DAT_TileMapState", "WallOwnerLayer[]")
tr = K.adresse("DAT_ViewportRenderState", "translationMatrix[]")
ty_b = K.adresse("DAT_BuildingsState", "buildings[].buildingType")
own_b = K.adresse("DAT_BuildingsState", "buildings[].owner")
ty_e = K.adresse("DAT_EntityState", "entityArray[].entityType")
cu = K.adresse("DAT_GameState", "playerDataArray[].currentResources[]")
aus = {}
lf.sperre_holen("Kurzprobe Feuerkorb und Waren (B-142)")
try:
    k = lf.EchterKanal()
    s = SpeicherS(ProzessQuelle(pid_der_instanz(2)), K)
    with Rufer(pid_der_instanz(2)) as r:
        def kachel(x, y):
            return r.lies_i(tr[0] + y * tr[2]) + x

        def schritt(*bef):
            k.liste(list(bef), lf.KANAL)
            k.befehl({"tempo": lf.TEMPO_JEDER_TAKT}, lf.KANAL)
            k.befehl({"pause": False}, lf.KANAL)
            time.sleep(0.5)
            lf.anhalten_und_pruefen(k, s)

        # Alle Felder der Karte durchgehen, die Besitzer 1 gehoeren koennen: Klasse des Feldes gegen die Antwort der Funktion
        klassen = collections.Counter()
        bsp = {}
        lord = next(e for e in s.einheiten_alle() if e["typ"] == 55 and e["besitzer"] == 1)
        for y in range(max(0, lord["y"] - 70), min(400, lord["y"] + 70)):
            for x in range(max(0, lord["x"] - 70), min(400, lord["x"] + 70)):
                t = kachel(x, y)
                if not 0 <= t < 80400:
                    continue
                l = r.lies_i(lo[0] + t * lo[2]) & 0xffffffff
                b = r.lies_i(ba[0] + t * (ba[2] or ba[1]), ba[1])
                if not (l & 0x700 or b):
                    continue
                art = r.lies_i(ty_b[0] + b * ty_b[2], ty_b[1]) if b else 0
                ei = r.lies_i(own_b[0] + b * own_b[2], own_b[1]) if b else (r.lies_i(wa[0] + t * (wa[2] or wa[1]), wa[1]) & 7) + 1
                if ei != 1:
                    continue
                name = (f"Gebaeude Art {art}" if b else "") + (" Mauer" if l & 0x100 else "") + (" Zinne" if l & 0x200 else "") + (" Treppe" if l & 0x800 else "")
                h = r.rufe(F_HOEHE, t, 1, this=TM)
                klassen[(name, h > 0)] += 1
                bsp.setdefault((name, h > 0), (x, y, h))
        aus["Klasse, Hoehe ueber 0: Felder"] = sorted((str(a), n) for a, n in klassen.items())
        print(aus["Klasse, Hoehe ueber 0: Felder"][:60])

        # Echte Befehle: auf eine Mauer oder einen Turm, auf den Bergfried, auf Boden
        def korb_auf(ziel, name):
            x, y, h = ziel
            t = kachel(x, y)
            schritt({"player": 1, "spielbefehl": {"nr": 69, "werte": [1, x * 8, y * 8, h, 14, 1]}})
            e = r.lies_i(en[0] + t * (en[2] or en[1]), en[1])
            aus["Befehl 69 " + name] = {"Feld": (x, y, h), "EntityLayer": e, "Art": r.lies_i(ty_e[0] + e * ty_e[2], ty_e[1]) if e else None}
        gewaehlt = 0
        for (name, ok), z in sorted(bsp.items(), key=lambda q: str(q[0])):
            if ok and gewaehlt < 5 and z[2] > 0:
                korb_auf(z, name)
                gewaehlt += 1
        korb_auf((lord["x"] + 30, lord["y"] + 30, 8), "freier Boden, Hoehe 8")

        # Waren schicken: Befehl 113, Unterart 2: Empfaenger, Ware, Menge, Absender
        def konto(n, w):
            return r.lies_i(cu[0] + n * cu[2] + w * 4)
        vor = {n: (konto(n, 15), konto(n, 2)) for n in (1, 2)}
        schritt({"player": 2, "spielbefehl": {"nr": 113, "werte": [2, 1, 15, 100, 2]}})
        nach = {n: (konto(n, 15), konto(n, 2)) for n in (1, 2)}
        aus["Befehl 113: Spieler 2 schickt 100 Gold an 1 (Gold, Holz) vorher, nachher"] = (vor, nach)
        vor = nach
        schritt({"player": 2, "spielbefehl": {"nr": 113, "werte": [2, 1, 2, 5, 2]}})
        nach = {n: (konto(n, 15), konto(n, 2)) for n in (1, 2)}
        aus["Befehl 113: Spieler 2 schickt 5 Holz an 1 (Gold, Holz) vorher, nachher"] = (vor, nach)
finally:
    lf.sperre_freigeben()
print(json.dumps(aus, ensure_ascii=False)[:2600])
with open("data/research/auge_plan/lauf_s_20261103/rufen_korb_waren_20261104.json", "w", encoding="utf-8") as d:
    json.dump(aus, d, ensure_ascii=False, default=str)
