# -*- coding: utf-8 -*-
"""P312, Befehl 69 und 97 im stehenden KI-Gefecht: Entsteht ein Feuerkorb (Art 14)? Erwartung Befehl 69: Korb entsteht, in Siege That sinkt das Gold um den Preis."""
import json
import time
from selfaware.tools.experiments import auge_lauf_f as lf
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.experiments.spielcode_rufen import Rufer
from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz

K = Feldkarte.laden(feldliste=FELDLISTE)
st = K.struktur("DAT_EntityState")
el = next(tt for o, tt, gr, n in K.typen[st[3]]["felder"] if n == "entityArray").split("[")[0].strip()
print([n for o, tt, gr, n in K.typen[el]["felder"]][:14])
ty = K.adresse("DAT_EntityState", "entityArray[].entityType")
lo = K.adresse("DAT_EntityState", "entityArray[].logicalState")
xx = K.adresse("DAT_EntityState", "entityArray[].x") if any(n == "x" for o, tt, gr, n in K.typen[el]["felder"]) else None
gm = K.adresse("DAT_GameCore", "gameMode_2")
go = K.adresse("DAT_GameState", "playerDataArray[].currentResources[]")
aus = {}
lf.sperre_holen("Kurzprobe Feuerkorb (B-142)")
try:
    k = lf.EchterKanal()
    with Rufer(pid_der_instanz(2)) as r:
        def koerbe():
            n = min(ty[3], 8000)
            return [i for i in range(1, n) if r.lies_i(ty[0] + i * ty[2], ty[1]) == 14 and r.lies_i(lo[0] + i * lo[2], lo[1]) != 0]

        def gold():
            return r.lies_i(go[0] + go[2] + 15 * 4)

        def lauf(*befehle):
            k.liste(list(befehle), lf.KANAL)
            k.befehl({"tempo": lf.TEMPO_JEDER_TAKT}, lf.KANAL)
            k.befehl({"pause": False}, lf.KANAL)
            time.sleep(0.7)
            k.befehl({"pause": True}, lf.KANAL)
            time.sleep(0.5)
        aus["vorher"] = (koerbe()[:6], gold())
        lauf({"player": 1, "spielbefehl": {"nr": 69, "werte": [1, 160 * 8 + 4, 245 * 8 + 4, 8, 14, 1]}})
        aus["Befehl 69, Gefecht"] = (koerbe()[:6], gold())
        alt = r.lies_i(gm[0], gm[1])
        r.setze_i(gm[0], 6, gm[1])
        lauf({"player": 1, "spielbefehl": {"nr": 69, "werte": [1, 165 * 8 + 4, 245 * 8 + 4, 8, 14, 1]}})
        aus["Befehl 69, Spielart 6"] = (koerbe()[:6], gold())
        r.setze_i(gm[0], alt, gm[1])
        lauf({"player": 1, "spielbefehl": {"nr": 97, "werte": [170, 245]}})
        aus["Befehl 97"] = (koerbe()[:6], gold())
finally:
    lf.sperre_freigeben()
print(json.dumps(aus, ensure_ascii=False))
with open("data/research/auge_plan/lauf_s_20261103/rufen_korb_20261104.json", "w", encoding="utf-8") as d:
    json.dump(aus, d, ensure_ascii=False)
