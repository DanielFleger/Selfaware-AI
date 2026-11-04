# -*- coding: utf-8 -*-
"""P187 im stehenden KI-Gefecht: requestGoods braucht einen Partner mit currentPlayerFullIDArray ungleich -1 (ein Mensch). Einmal wie es ist, einmal mit gesetzter Kennung. Danach alles zurueck."""
import json
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.experiments.spielcode_rufen import Rufer
from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz

K = Feldkarte.laden(feldliste=FELDLISTE)
AIC = K.struktur("DAT_AICState")[0]
F_BITTE = 0x004d1f00
t = K.adresse("DAT_GameState", "mapAndTime.playerTeams[]")
i_ = K.adresse("DAT_GameSynchronyState", "currentPlayerFullIDArray[]")
r1 = K.adresse("DAT_GameState", "playerDataArray[].requestedGoodsArray1Unk[]")
r2 = K.adresse("DAT_GameState", "playerDataArray[].requestedGoodsArray2Unk[]")
de = K.adresse("DAT_GameState", "playerDataArray[].aiRequestDelay")
slot = K.adresse("DAT_GameSynchronyState", "currentPlayerSlotID")
aus = {}
with Rufer(pid_der_instanz(2)) as r:
    te = [r.lies_i(t[0] + n * (t[2] or t[1]), t[1]) for n in range(9)]
    ids = [r.lies_i(i_[0] + n * (i_[2] or i_[1]), i_[1]) for n in range(9)]
    aus["teams"], aus["kennungen"], aus["angezeigt"] = te, ids, r.lies_i(slot[0], slot[1])
    KI, PARTNER = 3, 2

    def bitte(ware, menge):
        r.setze_i(r1[0] + PARTNER * r1[2] + 2 * KI, 0, 2)
        r.setze_i(r2[0] + PARTNER * r2[2] + 2 * KI, 0, 2)
        r.setze_i(de[0] + KI * de[2], 0, de[1])
        r.rufe(F_BITTE, KI, ware, menge, this=AIC)
        return (r.lies_i(r1[0] + PARTNER * r1[2] + 2 * KI, 2), r.lies_i(r2[0] + PARTNER * r2[2] + 2 * KI, 2))
    r.setze_i(t[0] + KI * (t[2] or t[1]), te[PARTNER], t[1])
    aus["Team gleich, Partner ohne Kennung: Holz 7"] = bitte(2, 7)
    r.setze_i(i_[0] + PARTNER * (i_[2] or i_[1]), 1, i_[1])
    aus["Team gleich, Partner mit Kennung: Holz 7"] = bitte(2, 7)
    aus["Hopfen 7"] = bitte(3, 7)
    aus["Bier 7"] = bitte(14, 7)
    aus["Stein 9"] = bitte(4, 9)
    r.setze_i(t[0] + KI * (t[2] or t[1]), te[KI], t[1])
    aus["kein Team: Holz 7"] = bitte(2, 7)
    r.setze_i(i_[0] + PARTNER * (i_[2] or i_[1]), ids[PARTNER], i_[1])
    r.setze_i(r1[0] + PARTNER * r1[2] + 2 * KI, 0, 2)
    r.setze_i(r2[0] + PARTNER * r2[2] + 2 * KI, 0, 2)
print(json.dumps(aus, ensure_ascii=False))
with open("data/research/auge_plan/lauf_s_20261103/rufen_bitte_20261104.json", "w", encoding="utf-8") as d:
    json.dump(aus, d, ensure_ascii=False)
