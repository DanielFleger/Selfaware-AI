# -*- coding: utf-8 -*-
"""B-142 Plan Lauf S: Aus einem strengen Fenster von Lauf K (jeder Takt gelesen): Takte zwischen zwei Lebensverlusten derselben Einheit, und wann die Munition der Belagerungsgeraete faellt. Nur lesen.

Aufruf aus dem Arbeitsbaum:
  PYTHONPATH=src python data/research/auge_plan/lauf_s_plan/kampf_takt.py t9 > data/research/auge_plan/lauf_s_plan/kampf_takt_t9.txt
"""
import collections
import os
import struct
import sys

from selfaware.tools.analysis.auge_auswertung import Aufzeichnung
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

HIER = os.path.dirname(os.path.abspath(__file__))
fenster = sys.argv[1]
karte = Feldkarte.laden(feldliste=FELDLISTE)
SCHRITT = karte.adresse("DAT_UnitsState", "units[].logicalState")[2]
auf = Aufzeichnung(os.path.join(HIER, "..", "laeufe", "lauf_k_20261102_234952_%s.auge" % fenster))
i = auf.namen.index("DAT_UnitsState")
b0 = auf.bereiche[i][1]
O = {n: karte.adresse("DAT_UnitsState", "units[]." + n)[0] - b0 for n in ("logicalState", "unitType", "health", "stoneAmmunition")}
leben, letzter, mun = {}, {}, {}
abstand, verlust = collections.Counter(), collections.Counter()
schuss = collections.defaultdict(list)
n = 0
for r, p, _ in auf.staende():
    if r.bereich != i or not r.rein:
        continue
    n += 1
    a = bytes(p)
    for u in range(1, 2500):  # Platz 0 ist ein Merkplatz (Lauf K)
        lo = u * SCHRITT
        if a[O["logicalState"] + lo] == 0 and a[O["logicalState"] + lo + 1] == 0:
            leben.pop(u, None)
            mun.pop(u, None)
            letzter.pop(u, None)
            continue
        h = struct.unpack_from("<i", a, O["health"] + lo)[0]
        al = leben.get(u)
        if al is not None and 0 < h < al:
            verlust[al - h] += 1
            if u in letzter:
                abstand[r.takt - letzter[u]] += 1
            letzter[u] = r.takt
        leben[u] = h
        ty = struct.unpack_from("<h", a, O["unitType"] + lo)[0]
        if ty in (39, 40, 41, 61, 77):
            m = struct.unpack_from("<h", a, O["stoneAmmunition"] + lo)[0]
            if mun.get(u) is not None and m < mun[u]:
                schuss[(ty, u)].append(r.takt)
            mun[u] = m
print("Fenster", fenster, "reine Rahmen", n)
print("Abstaende insgesamt", sum(abstand.values()), "davon genau 1 Takt", abstand[1])
print("Takte zwischen zwei Lebensverlusten, haeufigste:", abstand.most_common(10))
print("Lebensverlust je Mal, haeufigste:", verlust.most_common(14))
for k, v in schuss.items():
    print("Munition faellt: Art %d Einheit %d, Abstaende in Takten %s" % (k[0], k[1], [b - a for a, b in zip(v, v[1:])]))
