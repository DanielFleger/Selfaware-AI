# -*- coding: utf-8 -*-
"""Warum kommen Mauer, Graben und Pechgraben im Gefecht nicht an? Vermutung: Spielbefehle im angehaltenen Spiel verfallen. Probe auf Instanz 2 im laufenden Gefecht: dieselben Befehle einmal im Stand, einmal im Lauf, je an freier Stelle. Dazu: Erlaubt das Spiel Kaefig und Wachturm dort?

  SHC_INSTANZ=2 PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/probe_befehle_gefecht.py > data/research/auge_plan/lauf_s_20261103/probe_befehle_gefecht.txt
"""
import time

from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.experiments import auge_lauf_f as lf
from selfaware.tools.experiments import auge_lauf_s as ls
from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz, spielart_lesen

q = ProzessQuelle(pid_der_instanz(2))
karte = Feldkarte.laden(feldliste=FELDLISTE)
s = ls.SpeicherS(q, karte)
art = spielart_lesen(q, karte)
print("Spielart", art, "Takt", s.takt(), "Ansicht", lf.EchterKanal().peek(lf.ANSICHT)[0])
if art["gameMode_2"] != 3:
    raise SystemExit("Kein Gefecht offen")
k = lf.EchterKanal()
lf.sperre_holen("Probe Befehle im Gefecht (B-142)")
try:
    frei, hoehe, _ = s.raster()
    orte = ls.packen(frei, [(14, 8)] * 4, rand=10)
    print("Orte", orte)


    def bits():
        return {"mauer": len(s.felder_mit_bit(0x100)), "geplant": len(s.felder_mit_bit(0x4000)), "graben": len(s.felder_mit_bit(0x40000000)), "pech": len(s.pech_liste(1))}


    k.liste([{"player": 1, "ware": {"typ": 4, "menge": 2000}}, {"player": 1, "ware": {"typ": 7, "menge": 500}}], lf.KANAL)
    print("vorher", bits())
    (x, y), (x2, y2) = orte[0], orte[1]
    befehle = lambda x, y: [{"player": 1, "spielbefehl": {"nr": 25, "werte": [x, y, x + 5, y, 25, 13]}}, {"player": 1, "spielbefehl": {"nr": 21, "werte": [x + 3, y + 4, 0, 0x40000000, 0]}}, {"player": 1, "baue": {"mapper": 99, "x": x + 8, "y": y + 1, "groesse": 1, "richtung": 15}}]  # noqa: E731
    k.befehl({"pause": True}, lf.KANAL)
    t = s.takt()
    k.liste(befehle(x, y), lf.KANAL)
    k.befehl({"tempo": 40}, lf.KANAL)
    k.befehl({"pause": False}, lf.KANAL)
    time.sleep(2.0)
    print("im Stand abgeschickt, nach", s.takt() - t, "Takten:", bits())
    t = s.takt()
    k.liste(befehle(x2, y2), lf.KANAL)
    time.sleep(2.0)
    print("im Lauf abgeschickt, nach", s.takt() - t, "Takten:", bits())
    k.befehl({"pause": True}, lf.KANAL)
    for name, m, g in (("Kaefig", 312, 3), ("Wachturm", 110, 3), ("Oelschmelze", 180, 4), ("Huette", 54, 4)):
        for sp in (1, 2):
            (x3, y3) = orte[2]
            z = k.platzkarte(m, g, x3, y3, x3 + 10, y3 + 5, sp)
            print(name, "Spieler", sp, "erlaubt", sum(r.count("+") for r in z), "von", sum(len(r) for r in z), repr(z[0][:14]))
finally:
    k.befehl({"pause": True}, lf.KANAL)
    lf.sperre_freigeben()
