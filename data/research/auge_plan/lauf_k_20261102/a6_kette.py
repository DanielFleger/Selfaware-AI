# -*- coding: utf-8 -*-
"""B-142 A6: Zwei Fenster aus demselben Stand. Je Feld der erste abweichende Takt, damit die Kette sichtbar wird: Was weicht zuerst ab, was folgt daraus.
Geschossplaetze zaehlen nur, wenn sie in einem der Fenster belegt sind: Freie Plaetze behalten Reste aus der Partie davor.

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/a6_kette.py <basis> <T> [Fenster1 Fenster2]
"""
import collections
import struct
import sys

import numpy as np

from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

b, t = sys.argv[1], int(sys.argv[2])
N1, N2 = (sys.argv[3], sys.argv[4]) if len(sys.argv) > 4 else ("t2", "t3")
karte = Feldkarte.laden(feldliste=FELDLISTE)
a2, a3 = aw.Aufzeichnung(f"{b}_{N1}.auge"), aw.Aufzeichnung(f"{b}_{N2}.auge")
masken = aw.spielmasken(karte, a2)
erst = {}
wie_oft = collections.Counter()
plaetze = collections.defaultdict(list)
rng_erst = None
rng_werte = []
U0, US = karte.adresse("DAT_UnitsState", "units[].animationTicker")[0] - 64, 1168
E_LS = karte.adresse("DAT_EntityState", "entityArray[].logicalState")
E_B = a2.bereiche[a2.namen.index("DAT_EntityState")][1]
for (r1, p1), (r2, p2) in zip(aw._je_takt(a2, t, t + 2001), aw._je_takt(a3, t, t + 2001)):
    name = a2.namen[r1.bereich]
    if name != "SEC_RNG" and name not in masken:
        continue
    d = np.frombuffer(p1, dtype=np.uint8) != np.frombuffer(p2, dtype=np.uint8)
    if name in masken:
        d &= masken[name]
    if name == "DAT_EntityState":
        # nur belegte Plaetze
        d = d.copy()
        s, n = E_LS[2], E_LS[3]
        a1 = np.ndarray(shape=(n,), dtype="<i2", buffer=p1, offset=E_LS[0] - E_B, strides=(s,))
        a4 = np.ndarray(shape=(n,), dtype="<i2", buffer=p2, offset=E_LS[0] - E_B, strides=(s,))
        anfang = E_LS[0] - E_B - (E_LS[0] - karte.adresse("DAT_EntityState", "entityArray[].x1")[0]) - 0xC
        for i in np.flatnonzero((a1 == 0) & (a4 == 0)):
            d[anfang + i * s:anfang + (i + 1) * s] = False
    if not d.any():
        continue
    k = r1.takt - t
    if name == "SEC_RNG" and rng_erst is None:
        rng_erst = k
        rng_werte = (struct.unpack_from("<hh", p1, 0), struct.unpack_from("<ii", p1, 40008), struct.unpack_from("<hh", p2, 0), struct.unpack_from("<ii", p2, 40008))
    basis = a2.bereiche[r1.bereich][1]
    for o, l in aw._luecken(d):
        for g, f in karte.felder_einer_aenderung(basis + o, l):
            key = f"{g} {f}"
            erst.setdefault(key, k)
            wie_oft[key] += 1
            if len(plaetze[key]) < 12 and "units[]" in f:
                i = (basis + o - U0) // US
                w1 = struct.unpack_from("<h", p1, U0 + i * US - basis + 0x8E)[0] if name == "DAT_UnitsState" else None
                plaetze[key].append((k, i, w1))
print("Zufall weicht zuerst ab bei Takt", rng_erst, rng_werte)
for key, k in sorted(erst.items(), key=lambda x: x[1])[:45]:
    print(f"ab {k:5d}  {wie_oft[key]:7d} mal  {key}  {plaetze[key][:4] if plaetze[key] else ''}")
print("Felder gesamt", len(erst))
