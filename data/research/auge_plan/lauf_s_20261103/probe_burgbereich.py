# -*- coding: utf-8 -*-
"""Burgbauten gehen im Gefecht offenbar nur nahe der eigenen Burg: Wie gross ist der Bereich, und kommen Mauer, Graben und Pechgraben dort an? Probe auf Instanz 2 im laufenden Gefecht.

  SHC_INSTANZ=2 PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/probe_burgbereich.py > data/research/auge_plan/lauf_s_20261103/probe_burgbereich.txt
"""
import collections
import time

import numpy as np

from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.experiments import auge_lauf_f as lf
from selfaware.tools.experiments import auge_lauf_s as ls
from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz, spielart_lesen

q = ProzessQuelle(pid_der_instanz(2))
karte = Feldkarte.laden(feldliste=FELDLISTE)
s = ls.SpeicherS(q, karte)
if spielart_lesen(q, karte)["gameMode_2"] != 3:
    raise SystemExit("Kein Gefecht offen")
k = lf.EchterKanal()
lord = next((e for e in s.einheiten_alle() if e["typ"] == 55 and e["besitzer"] == 1), None)
print("Lord", lord)
lf.sperre_holen("Probe Burgbereich (B-142)")
try:
    k.befehl({"pause": True}, lf.KANAL)
    cx, cy = lord["x"], lord["y"]
    r = 45
    frei, hoehe, ge = s.raster()
    orte = {}
    for name, m, g in (("Wachturm", 110, 3), ("Kaefig", 312, 3), ("Mordgrube", 98, 1), ("Huette", 54, 4)):
        z = k.platzkarte(m, g, cx - r, cy - r, cx + r, cy + r, 1)
        arten = collections.Counter(c for reihe in z for c in reihe)
        plus = [(i - r, j - r) for j, reihe in enumerate(z) for i, c in enumerate(reihe) if c == "+"]
        print(name, dict(arten), "weitestes Plus", max((max(abs(a), abs(b)) for a, b in plus), default=None))
        orte[name] = plus
    # eine erlaubte Stelle fuer Mauer, Graben, Pech: frei und mit Abstand zur Burg
    plus = [(a, b) for a, b in orte["Wachturm"] if max(abs(a), abs(b)) >= 14]
    print("Plus ab 14 Felder:", len(plus), plus[:6])
    a, b = plus[len(plus) // 2]
    x, y = cx + a, cy + b
    print("Probe bei", (x, y), "frei im Umkreis:", int(frei[y - 3:y + 8, x - 3:x + 12].sum()))


    def bits():
        return {"mauer": len(s.felder_mit_bit(0x100)), "geplant": len(s.felder_mit_bit(0x4000)), "graben": len(s.felder_mit_bit(0x40000000)), "pech": len(s.pech_liste(1))}


    k.liste([{"player": 1, "ware": {"typ": 4, "menge": 2000}}, {"player": 1, "ware": {"typ": 7, "menge": 500}}], lf.KANAL)
    print("vorher", bits())
    k.befehl({"tempo": 40}, lf.KANAL)
    k.befehl({"pause": False}, lf.KANAL)
    t = s.takt()
    k.liste([{"player": 1, "spielbefehl": {"nr": 25, "werte": [x, y, x + 5, y, 25, 13]}}, {"player": 1, "spielbefehl": {"nr": 21, "werte": [x + 3, y + 4, 0, 0x40000000, 0]}}, {"player": 1, "baue": {"mapper": 99, "x": x + 8, "y": y + 1, "groesse": 1, "richtung": 15}}], lf.KANAL)
    time.sleep(2.0)
    print("nach", s.takt() - t, "Takten:", bits())
finally:
    k.befehl({"pause": True}, lf.KANAL)
    lf.sperre_freigeben()
