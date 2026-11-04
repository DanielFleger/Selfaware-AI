# -*- coding: utf-8 -*-
"""Letzte Kurzprobe, stehendes KI-Gefecht. (1) Je Gebaeudeart alle Felder: Wo sagt die Oberflaeche ja? (2) P312: Korb im Modus Siege That kostet Gold? (3) P372 Team-Bits."""
import collections
import json
import time

from selfaware.tools.experiments import auge_lauf_f as lf
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.experiments.auge_lauf_s import SpeicherS
from selfaware.tools.experiments.spielcode_rufen import Rufer
from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz

F_HOEHE, F_TEAM = 0x4fff10, 0x00459740
K = Feldkarte.laden(feldliste=FELDLISTE)
TM, G = K.struktur("DAT_TileMapState")[0], K.struktur("DAT_GameState")[0]
ba, en = K.adresse("DAT_TileMapState", "BuildingLayer[]"), K.adresse("DAT_TileMapState", "EntityLayer[]")
ty_b, own_b = K.adresse("DAT_BuildingsState", "buildings[].buildingType"), K.adresse("DAT_BuildingsState", "buildings[].owner")
ty_e = K.adresse("DAT_EntityState", "entityArray[].entityType")
gm, cu = K.adresse("DAT_GameCore", "gameMode_2"), K.adresse("DAT_GameState", "playerDataArray[].currentResources[]")
aus = {}
lf.sperre_holen("Kurzprobe Feuerkorb Gebaeude (B-142)")
try:
    k = lf.EchterKanal()
    s = SpeicherS(ProzessQuelle(pid_der_instanz(2)), K)
    with Rufer(pid_der_instanz(2)) as r:
        def schritt(*bef):
            k.liste(list(bef), lf.KANAL)
            k.befehl({"tempo": lf.TEMPO_JEDER_TAKT}, lf.KANAL)
            k.befehl({"pause": False}, lf.KANAL)
            time.sleep(0.5)
            lf.anhalten_und_pruefen(k, s)
        c = collections.Counter()
        ort = {}
        roh = r.lies(ba[0], 80400 * ba[1])
        namen_y = s.raster()[1].shape
        for y in range(namen_y[0]):
            for x in range(namen_y[1]):
                t = s.kachel(x, y)
                if not 0 <= t < 80400:
                    continue
                b = int.from_bytes(roh[t * ba[1]:(t + 1) * ba[1]], "little", signed=True)
                if b <= 0:
                    continue
                art = r.lies_i(ty_b[0] + b * ty_b[2], ty_b[1])
                ei = r.lies_i(own_b[0] + b * own_b[2], own_b[1])
                h = r.rufe(F_HOEHE, t, ei, this=TM)
                c[(art, h > 0)] += 1
                if h > 0:
                    ort.setdefault(art, (ei, x, y, h))
        z = collections.defaultdict(dict)
        for (art, ja), n in c.items():
            z[art]["ja" if ja else "nein"] = n
        aus["Gebaeudeart: Felder ja oder nein"] = {a: v for a, v in sorted(z.items()) if v.get("ja")}
        aus["Arten ganz ohne ja"] = sorted(a for a, v in z.items() if not v.get("ja"))
        aus["Beispiele"] = ort
        print(json.dumps(aus, ensure_ascii=False)[:1000], flush=True)
        # P312: Turm oder Bergfried, im Modus Siege That
        ziel = next((v for a, v in ort.items() if a not in (46,)), None) or next(iter(ort.values()))
        sp, x, y, h = ziel
        alt = r.lies_i(gm[0], gm[1])
        vor = r.lies_i(cu[0] + sp * cu[2] + 15 * 4)
        schritt({"player": sp, "spielbefehl": {"nr": 69, "werte": [sp, x * 8, y * 8, h, 14, sp]}})
        nach1 = r.lies_i(cu[0] + sp * cu[2] + 15 * 4)
        e = r.lies_i(en[0] + s.kachel(x, y) * (en[2] or en[1]), en[1])
        aus["Gefecht: Korb, Gold vorher, nachher"] = (r.lies_i(ty_e[0] + e * ty_e[2], ty_e[1]) if e else None, vor, nach1)
        ziele = list(ort.values())
        if len(ziele) > 1:
            sp2, x2, y2, h2 = ziele[-1]
            r.setze_i(gm[0], 6, gm[1])
            vor2 = r.lies_i(cu[0] + sp2 * cu[2] + 15 * 4)
            k.liste([{"player": sp2, "spielbefehl": {"nr": 69, "werte": [sp2, x2 * 8, y2 * 8, h2, 14, sp2]}}], lf.KANAL)
            k.befehl({"pause": False}, lf.KANAL)
            time.sleep(0.25)
            nach2 = r.lies_i(cu[0] + sp2 * cu[2] + 15 * 4)
            r.setze_i(gm[0], alt, gm[1])
            lf.anhalten_und_pruefen(k, s)
            e2 = r.lies_i(en[0] + s.kachel(x2, y2) * (en[2] or en[1]), en[1])
            aus["Siege That: Spieler, Feld, Korb, Gold vorher, nachher"] = (sp2, (x2, y2), r.lies_i(ty_e[0] + e2 * ty_e[2], ty_e[1]) if e2 else None, vor2, nach2)
        # P372: fuer eine Einheit von Spieler 3
        a, g_, sch, _ = K.adresse("DAT_GameState", "mapAndTime.playerTeams[]")
        el = sch or g_
        team = [r.lies_i(a + i * el, g_) for i in range(9)]
        einheit = next((e for e in s.einheiten_alle() if e["besitzer"] == 3), None)
        if einheit:
            aus["Team-Bits, jeder allein"] = bin(r.rufe(F_TEAM, einheit["nr"], this=G) & 0xff)
            r.setze_i(a + 4 * el, team[3], g_)
            aus["Team-Bits, Spieler 3 und 4 zusammen"] = bin(r.rufe(F_TEAM, einheit["nr"], this=G) & 0xff)
            r.setze_i(a + 4 * el, team[4], g_)
finally:
    lf.sperre_freigeben()
print(json.dumps({a: v for a, v in aus.items() if not a.startswith("Gebaeudeart") and a != "Beispiele"}, ensure_ascii=False)[:900])
with open("data/research/auge_plan/lauf_s_20261103/rufen_korb_gebaeude_20261104.json", "w", encoding="utf-8") as d:
    json.dump(aus, d, ensure_ascii=False, default=str)
