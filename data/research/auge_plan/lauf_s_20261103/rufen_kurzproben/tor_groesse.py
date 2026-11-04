# -*- coding: utf-8 -*-
"""Das Spiel steht nach rufen4_g. Welche Groesse nimmt ein Holztor, welcher Mapper der Belagerungsturm? Nur Lesen und Pruefen, nichts wird gebaut."""
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.experiments.spielcode_rufen import Rufer
from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz

K = Feldkarte.laden(feldliste=FELDLISTE)
TM = K.struktur("DAT_TileMapState")[0]
F = K.adresse("DAT_TileMapState", "buildingPlacementFail")[0]
R_ = K.adresse("DAT_TileMapState", "buildingPlacementFailReason")[0]
X = (160, 245)
with Rufer(pid_der_instanz(2)) as r:
    for m in (103, 104, 140, 141, 142, 143, 144, 100, 101, 102, 94, 192, 90, 91, 92, 93, 95, 96):
        z = {}
        for g in (1, 3, 5, 7, 9):
            r.setze_i(R_, 0)
            r.rufe(0x005037b0, 1, X[0], X[1], m, g, this=TM)
            z[g] = (r.lies_i(F), r.lies_i(R_))
        print("Mapper", m, z)
    # welche Gebaeudeart gehoert zu welchem Mapper?
    for m in (103, 140, 141, 142, 143, 94, 192, 90, 91, 92, 93, 95, 96):
        print("Mapper", m, "wird Art", r.rufe(0x00420d20 if False else 0, this=0) if False else "?")
