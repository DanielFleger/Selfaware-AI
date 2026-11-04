# -*- coding: utf-8 -*-
"""Feuerkorb: Welche Felder nennt die Oberflaeche erlaubt (Hoehe ueber 0)? Je Spieler alle Gebaeude und die Mauerfelder. Dann der Befehl auf Turm, Mauer, Hof. Stehendes KI-Gefecht."""
import collections
import json
import os
import time

from selfaware.tools.experiments import auge_lauf_f as lf
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.experiments.auge_lauf_s import SpeicherS
from selfaware.tools.experiments.spielcode_rufen import Rufer
from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz

F_HOEHE = 0x4fff10
F_TEAM = 0x00459740
K = Feldkarte.laden(feldliste=FELDLISTE)
TM = K.struktur("DAT_TileMapState")[0]
lo, ba, en = K.adresse("DAT_TileMapState", "LogicLayer[]"), K.adresse("DAT_TileMapState", "BuildingLayer[]"), K.adresse("DAT_TileMapState", "EntityLayer[]")
wa = K.adresse("DAT_TileMapState", "WallOwnerLayer[]")
tr = K.adresse("DAT_ViewportRenderState", "translationMatrix[]")
ty_e = K.adresse("DAT_EntityState", "entityArray[].entityType")
aus = {}
lf.sperre_holen("Kurzprobe Feuerkorb Felder (B-142)")
try:
    k = lf.EchterKanal()
    s = SpeicherS(ProzessQuelle(pid_der_instanz(2)), K)
    with Rufer(pid_der_instanz(2)) as r:
        def kachel(x, y):
            return s.kachel(x, y)  # die Zeilentabelle hat ihren Wert nicht vorn im Eintrag: Eigenes Rechnen traf falsche Felder

        def schritt(*bef):
            k.liste(list(bef), lf.KANAL)
            k.befehl({"tempo": lf.TEMPO_JEDER_TAKT}, lf.KANAL)
            k.befehl({"pause": False}, lf.KANAL)
            time.sleep(0.5)
            lf.anhalten_und_pruefen(k, s)
        lage = {}
        ziele = {}
        for sp in range(1, 9):
            for g in s.gebaeude(sp):
                t = kachel(g["x"], g["y"])
                h = r.rufe(F_HOEHE, t, sp, this=TM)
                c = lage.setdefault(g["typ"], collections.Counter())
                c[h > 0] += 1
                if h > 0 and g["typ"] not in ziele:
                    ziele[g["typ"]] = (sp, g["x"], g["y"], h)
        aus["Gebaeudeart: (erlaubt, Zahl)"] = {a: c.most_common() for a, c in sorted(lage.items())}
        # Mauer, Zinne, Treppe: alle Felder der Karte
        frei_karte = s.raster()[1] > -10**6  # jedes Feld im Raster
        mauer = collections.Counter()
        bsp = {}
        for y in range(0, 400, 1):
            for x in range(0, 400, 1):
                if not frei_karte[y, x]:
                    continue
                t = kachel(x, y)
                if not 0 <= t < 80400:
                    continue
                l = r.lies_i(lo[0] + t * lo[2]) & 0xffffffff
                if not l & 0xB00:
                    continue
                sp = (r.lies_i(wa[0] + t * (wa[2] or wa[1]), wa[1]) & 7) + 1
                name = "+".join(n for b, n in ((0x100, "Mauer"), (0x200, "Zinne"), (0x800, "Treppe")) if l & b)
                h = r.rufe(F_HOEHE, t, sp, this=TM)
                h_fremd = r.rufe(F_HOEHE, t, sp % 8 + 1, this=TM)
                mauer[(name, h > 0, h_fremd > 0)] += 1
                bsp.setdefault((name, h > 0), (sp, x, y, h))
        aus["Mauerfelder (Art, erlaubt fuer den Besitzer, erlaubt fuer einen anderen): Zahl"] = [(str(a), n) for a, n in mauer.most_common()]
        print(json.dumps(aus, ensure_ascii=False)[:1800], flush=True)
        def korb(ziel, name):
            sp, x, y, h = ziel
            t = kachel(x, y)
            schritt({"player": sp, "spielbefehl": {"nr": 69, "werte": [sp, x * 8, y * 8, h, 14, sp]}})
            e = r.lies_i(en[0] + t * (en[2] or en[1]), en[1])
            aus["Befehl 69 auf " + name] = {"Ziel": ziel, "Eintrag": e, "Art": r.lies_i(ty_e[0] + e * ty_e[2], ty_e[1]) if e else None}
        for (name, ok), z in list(bsp.items()):
            if ok:
                korb(z, name)
        for a, z in list(ziele.items())[:4]:
            korb(z, f"Gebaeude Art {a}")
        # P372: Teams als Bits
        a, g, sch, _ = K.adresse("DAT_GameState", "mapAndTime.playerTeams[]")
        el = sch or g
        team = [r.lies_i(a + i * el, g) for i in range(9)]
        aus["Teams"] = team
finally:
    lf.sperre_freigeben()
print(json.dumps({k_: v for k_, v in aus.items() if k_.startswith("Befehl") or k_ == "Teams"}, ensure_ascii=False)[:1400])
with open("data/research/auge_plan/lauf_s_20261103/rufen_korb_felder_20261104.json", "w", encoding="utf-8") as d:
    json.dump(aus, d, ensure_ascii=False, default=str)
