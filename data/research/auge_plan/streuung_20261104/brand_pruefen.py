# -*- coding: utf-8 -*-
"""Gebaeudebrand in der Szene streuung: Wann brennt die Huette, wie schnell faellt ihr Leben, springt es auf die Nachbarn ueber, wie lange brennt es?

Regeln aus dem Code: lightUpBuilding 0041c810 (Feuer auf jedem Feld des Gebaeudes, Start verzoegert um Zufall%120), updateBuildings 00422e20 (alle 20 Takte minus 1 Leben, Holzbauten minus 4; fireDuration zaehlt), UpdateFireEntity 00405680 (Feuer auf brennendem Gebaeude bleibt Stufe 3 und damit ausbreitungsfaehig).
Ausgabe: brand_pruefung.txt.
"""
import collections
import glob
import json
import os
import sys

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import feuer_pruefen as fe  # noqa: E402
from selfaware.tools.analysis.auge_auswertung import Aufzeichnung  # noqa: E402
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte  # noqa: E402

B_F = {"typ": ("buildingType", "<i2"), "da": ("logicalState", "<i2"), "x": ("x", "<i2"), "y": ("y", "<i2"), "leben": ("currentHealth", "<i2"), "brand": ("fireDuration", "<i2"), "abk": ("cooldownTimer", "<i2"), "wer": ("ifFireThenResponsiblePlayer", "<i2"), "bes": ("owner", "<i2")}


def main():
    pfad = sorted(glob.glob(os.path.join(HIER, "..", "laeufe", "lauf_s_*_streuung.auge")), key=os.path.getmtime)[-1]
    k = Feldkarte.laden(feldliste=FELDLISTE)
    plan = json.load(open(pfad + ".plan.json", encoding="utf-8"))
    huetten = [g for g in plan["gebaeude"] if g.get("posten") == "feuer" and "nr" in g]
    auf = Aufzeichnung(pfad)
    ib = auf.namen.index("DAT_BuildingsState")
    be = auf.bereiche[ib][1]
    ad = {n: k.adresse("DAT_BuildingsState", "buildings[]." + f) for n, (f, _) in B_F.items()}
    verlauf = collections.defaultdict(list)
    for r, p, _ in auf.staende():
        if r.bereich != ib or not r.rein:
            continue
        a = bytes(p)
        for g in huetten:
            i = g["nr"]
            verlauf[i].append((r.takt, {n: int(np.ndarray(shape=(1,), dtype=f[1], buffer=a, offset=ad[n][0] + i * ad[n][2] - be)[0]) for n, f in B_F.items()}))
    aus = ["Huetten der Szene: " + str([(g["nr"], g["x"], g["y"]) for g in huetten])]
    for i, v in verlauf.items():
        aus.append("Huette %d: Rahmen %d, Abstand der Rahmen %s" % (i, len(v), sorted(collections.Counter(b[0] - a[0] for a, b in zip(v, v[1:])).items())[:3]))
        letzt = None
        for t, z in v:
            w = (z["da"], z["brand"] > 0, z["abk"] > 0)
            if w != letzt:
                aus.append("   Takt %d: da %d, Leben %d, Brandzaehler %d, Abkuehlen %d, Verursacher %d" % (t, z["da"], z["leben"], z["brand"], z["abk"], z["wer"]))
            letzt = w
        aenderungen = [(a[0], b[0], b[1]["leben"] - a[1]["leben"], b[1]["brand"] - a[1]["brand"]) for a, b in zip(v, v[1:]) if b[1]["leben"] != a[1]["leben"] and b[1]["da"] == a[1]["da"]]
        aus.append("   Lebensverlust je Schritt: %s" % sorted(collections.Counter(x[2] for x in aenderungen).items()))
        schritte = [b[0] - a[0] for a, b in zip(aenderungen, aenderungen[1:])]
        aus.append("   Takte zwischen zwei Verlusten: %s" % sorted(collections.Counter(schritte).items())[:6])
    feuer = fe.feuer_lesen(pfad, k)
    stufen = collections.Counter()
    start_zaehler = collections.Counter()
    for s, f in feuer.items():
        stufen[(f[0][1]["stufe"], f[0][1]["stark"])] += 1
        if f[0][1]["phase"] < 0:
            start_zaehler["Start verzoegert"] += 1
    aus.append("Feuer der ganzen Szene je (Stufe, Staerke): " + str(sorted(stufen.items())) + " " + str(sorted(start_zaehler.items())))
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "brand_pruefung.txt"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
