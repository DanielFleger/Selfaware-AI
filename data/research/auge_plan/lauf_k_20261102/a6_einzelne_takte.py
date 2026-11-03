# -*- coding: utf-8 -*-
"""B-142 A6: Warum weichen t8 und t9 in genau zwei Takten ab und danach nicht mehr? Vermutung: Eine Lesung hat einen Takt erwischt, der noch nicht fertig gerechnet war.
Probe: An den abweichenden Bytes steht in einer der beiden Aufzeichnungen noch der Wert des Takts davor. Weichen sie anders ab, ist die Vermutung falsch.

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/a6_einzelne_takte.py <basis> > data/research/auge_plan/lauf_k_20261102/a6_einzelne_takte.txt
"""
import sys

import numpy as np

from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

basis = sys.argv[1]
karte = Feldkarte.laden(feldliste=FELDLISTE)
A, B = aw.Aufzeichnung(basis + "_t8.auge"), aw.Aufzeichnung(basis + "_t9.auge")
masken = aw.spielmasken(karte, A)
start = next(A.rahmen()).takt
print("Start", start)


def fenster(auf, name, ks):
    i = auf.namen.index(name)
    aus = {}
    for r, p, _ in auf.staende():
        if r.bereich == i and r.takt - start in ks:
            aus[r.takt - start] = (bytes(p), r)
    return aus


for k, name in ((203, "DAT_GameState"), (203, "DAT_UnitsState"), (605, "DAT_GameState"), (605, "DAT_UnitsState")):
    ks = {k - 1, k, k + 1}
    fa, fb = fenster(A, name, ks), fenster(B, name, ks)
    a, b = np.frombuffer(fa[k][0], dtype=np.uint8), np.frombuffer(fb[k][0], dtype=np.uint8)
    d = (a != b) & masken[name]
    n = int(d.sum())
    print(f"Takt {k} {name}: {n} Bytes anders; davor gleich {int((np.frombuffer(fa[k - 1][0], dtype=np.uint8)[masken[name]] != np.frombuffer(fb[k - 1][0], dtype=np.uint8)[masken[name]]).sum()) == 0}; danach gleich {int((np.frombuffer(fa[k + 1][0], dtype=np.uint8)[masken[name]] != np.frombuffer(fb[k + 1][0], dtype=np.uint8)[masken[name]]).sum()) == 0}")
    if n:
        a0, b0 = np.frombuffer(fa[k - 1][0], dtype=np.uint8), np.frombuffer(fb[k - 1][0], dtype=np.uint8)
        a1, b1 = np.frombuffer(fa[k + 1][0], dtype=np.uint8), np.frombuffer(fb[k + 1][0], dtype=np.uint8)
        print("   t8 hat noch den alten Wert:", int((a[d] == a0[d]).sum()), " t9 hat noch den alten Wert:", int((b[d] == b0[d]).sum()), " t8 hat schon den Wert des Folgetakts:", int((a[d] == a1[d]).sum()), " t9 hat schon den Wert des Folgetakts:", int((b[d] == b1[d]).sum()))
        basis_adr = A.bereiche[A.namen.index(name)][1]
        print("   Felder:", sorted({f"{g} {f}" for o, l in aw._luecken(d) for g, f in karte.felder_einer_aenderung(basis_adr + o, l)})[:14])
    for nm, f in (("t8", fa), ("t9", fb)):
        r = f[k][1]
        print("  ", nm, "Lesung", {x: getattr(r, x) for x in ("takt", "vor", "nach", "rein", "dauer") if hasattr(r, x)}, "Zeit seit dem Rahmen davor", round(r.zeit - f[k - 1][1].zeit, 4) if hasattr(r, "zeit") else None, "bis zum nächsten", round(f[k + 1][1].zeit - r.zeit, 4) if hasattr(r, "zeit") else None)
