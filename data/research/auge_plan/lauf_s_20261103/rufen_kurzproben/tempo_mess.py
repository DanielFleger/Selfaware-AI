# -*- coding: utf-8 -*-
"""Daniels 830: Wie viele Takte je Sekunde laufen bei welchem Tempo? Im KI-Gefecht, Takt 3.500 aufwaerts. Nur Tempo setzen und zaehlen. Am Ende steht das Spiel wieder."""
import json
import time
from selfaware.tools.experiments import auge_lauf_f as lf
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.experiments.auge_lauf_s import SpeicherS
from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz

K = Feldkarte.laden(feldliste=FELDLISTE)
lf.sperre_holen("Kurzprobe Tempo (B-142)")
aus = {}
try:
    k = lf.EchterKanal()
    s = SpeicherS(ProzessQuelle(pid_der_instanz(2)), K)
    k.befehl({"pause": False}, lf.KANAL)
    for tempo in (100, 500, 830, 1000, 2000):
        k.befehl({"tempo": tempo}, lf.KANAL)
        time.sleep(0.3)
        a, u = s.takt(), time.perf_counter()
        time.sleep(4)
        b, v = s.takt(), time.perf_counter()
        aus[tempo] = round((b - a) / (v - u))
        print("Tempo", tempo, "Takte je Sekunde", aus[tempo], "Takt", b, flush=True)
    steht, t = lf.anhalten_und_pruefen(k, s)
    print("steht", steht, t)
finally:
    lf.sperre_freigeben()
with open("data/research/auge_plan/lauf_s_20261103/rufen_tempo_20261104.json", "w", encoding="utf-8") as d:
    json.dump(aus, d)
