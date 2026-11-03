# -*- coding: utf-8 -*-
"""Tunnel: Wo erlaubt das Spiel den Eingang (Mapper 66, Groesse 3), und steht er nach baue wirklich? Code: checkBuildingCanBePlacedHere sucht mit algTunnelerFindTarget ein feindliches Ziel binnen 76 Schritten. Probe auf Instanz 2 im laufenden Gefecht.

  SHC_INSTANZ=2 PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/probe_tunnel.py > data/research/auge_plan/lauf_s_20261103/probe_tunnel.txt
"""
import collections
import time

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
lords = {e["besitzer"]: e for e in s.einheiten_alle() if e["typ"] == 55}
print("Lords", {p: (e["x"], e["y"]) for p, e in lords.items()})
lf.sperre_holen("Probe Tunnel (B-142)")
try:
    k.befehl({"pause": True}, lf.KANAL)
    for wem, r in ((2, 45), (2, 95), (1, 45)):
        cx, cy = lords[wem]["x"], lords[wem]["y"]
        x0, y0, x1, y1 = max(1, cx - r), max(1, cy - r), min(398, cx + r), min(398, cy + r)
        z = k.platzkarte(66, 3, x0, y0, x1, y1, 1)
        arten = collections.Counter(c for reihe in z for c in reihe)
        ring = collections.defaultdict(collections.Counter)
        for j, reihe in enumerate(z):
            for i, c in enumerate(reihe):
                ring[max(abs(x0 + i - cx), abs(y0 + j - cy)) // 10 * 10][c] += 1
        print(f"Um den Lord von Spieler {wem}, Fenster {r}:", dict(arten))
        for d in sorted(ring):
            print("  Abstand", d, dict(ring[d]))
    cx, cy = lords[2]["x"], lords[2]["y"]
    z = k.platzkarte(66, 3, cx - 25, cy - 25, cx + 25, cy + 25, 1)
    plus = [(i - 25, j - 25) for j, reihe in enumerate(z) for i, c in enumerate(reihe) if c == "+" and max(abs(i - 25), abs(j - 25)) >= 18]
    print("Plus ab 18 Feldern:", len(plus), plus[:5])
    a, b = plus[len(plus) // 2]
    x, y = cx + a, cy + b
    vorher = {g["nr"] for g in s.gebaeude(None)}
    k.befehl({"tempo": 40}, lf.KANAL)
    k.befehl({"pause": False}, lf.KANAL)
    t = s.takt()
    k.liste([{"player": 1, "baue": {"mapper": 66, "x": x, "y": y, "groesse": 3, "richtung": 15}}], lf.KANAL)
    time.sleep(2.0)
    print("nach", s.takt() - t, "Takten bei", (x, y), "neu:", [g for g in s.gebaeude(None) if g["nr"] not in vorher])
finally:
    k.befehl({"pause": True}, lf.KANAL)
    lf.sperre_freigeben()
