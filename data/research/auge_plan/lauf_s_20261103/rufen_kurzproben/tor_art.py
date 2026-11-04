# -*- coding: utf-8 -*-
"""Kurzprobe im stehenden Spiel: Welche Gebaeudeart entsteht aus Mapper 103, 140 und 192? Setzt drei Gebaeude, liest nach."""
import time
from selfaware.tools.experiments import auge_lauf_f as lf
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.experiments.spielcode_rufen import Rufer
from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz

K = Feldkarte.laden(feldliste=FELDLISTE)
tp = K.adresse("DAT_BuildingsState", "buildings[].buildingType")
x_ = K.adresse("DAT_BuildingsState", "buildings[].x")
y_ = K.adresse("DAT_BuildingsState", "buildings[].y")
lf.sperre_holen("Kurzprobe Mapper und Art (B-142)")
try:
    k = lf.EchterKanal()
    with Rufer(pid_der_instanz(2)) as r:
        def alle():
            return {i: (r.lies_i(tp[0] + i * tp[2], tp[1]), r.lies_i(x_[0] + i * x_[2], x_[1]), r.lies_i(y_[0] + i * y_[2], y_[1])) for i in range(1, 120) if r.lies_i(tp[0] + i * tp[2], tp[1])}
        for m, x, y, g, dr in ((103, 160, 277, 3, 15), (103, 170, 277, 3, 2), (103, 180, 277, 3, 4), (100, 160, 285, 3, 15), (101, 170, 285, 3, 15), (102, 180, 285, 3, 15)):
            vor = alle()
            k.liste([{"setzeGebaeude": {"spieler": 1, "x": x, "y": y, "mapper": m, "groesse": g, "drehung": dr}}], lf.KANAL)
            time.sleep(1.0)
            neu = {i: v for i, v in alle().items() if vor.get(i) != v}
            print("Mapper", m, "Groesse", g, "Drehung", dr, "bei", (x, y), "neu (Nr: Art, x, y):", neu)
finally:
    lf.sperre_freigeben()
