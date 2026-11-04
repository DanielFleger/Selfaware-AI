# -*- coding: utf-8 -*-
"""Szene streuung4: Zuendet der Brandpfeil das Pech an, und nur mit Feuerkorb?

Widerlegt die Regel (Code: UpdateCrusaderArcher, Art 0x5d, processEntityHitBuildingOrUnit): Der Schuetze am Korb schiesst normale Pfeile, oder der Graben brennt nicht. Der Schuetze ohne Korb zuendet ihn trotzdem an. Ausgabe: pech_pruefung.txt.
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
import flug_pruefen as fp  # noqa: E402
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte  # noqa: E402

fp.U_F.update({"tgt": "targetingType", "schiesst": "shootTargetedUnit"})


def main():
    pfad = sorted(glob.glob(os.path.join(HIER, "..", "laeufe", "lauf_s_*_streuung4_g.auge")), key=os.path.getmtime)[-1]
    k = Feldkarte.laden(feldliste=FELDLISTE)
    plan = json.load(open(pfad + ".plan.json", encoding="utf-8"))
    lauf = fp.Lauf(pfad, k)
    u = lauf.u
    tk = sorted(u)
    aus = ["Datei %s, Takte %d, Fluege %d" % (os.path.basename(pfad), len(u), len(lauf.fluege))]
    m = plan["karte"][0]
    x0, y0 = m["x"], m["y"]
    aus.append("Ort (%d, %d), Mauer fehlt %s" % (x0, y0, plan.get("mauer_fehlt")))
    st = u[tk[len(tk) // 2]]
    leute = [(int(i), "Feld", int(st["x"][i]), int(st["y"][i]), "hb", int(st["hb"][i]), "ht", int(st["ht"][i]), "Zielart", int(st["tgt"][i]), "schiesst", int(st["schiesst"][i])) for i in np.nonzero((st["da"] != 0) & (st["bes"] == 1) & (st["typ"] == 22))[0]]
    aus.append("Schuetzen in der Mitte des Laufs: " + str(leute))
    schuesse = collections.Counter()
    punkte = []
    for s, f in sorted(lauf.fluege.items(), key=lambda x: x[1][0][0]):
        z = f[0][1]
        q = u.get(f[0][0] - 1)
        hoch = q is not None and int(q["hb"][z["sch"]]) + int(q["ht"][z["sch"]]) > 8
        schuesse[("auf der Mauer" if hoch else "am Boden", "Art %d" % z["art"], "Marke %d" % z["rng2"], "Zielart %d" % (int(q["tgt"][z["sch"]]) if q is not None else -1))] += 1
        if z["rng2"] == 2 or (q is not None and int(q["tgt"][z["sch"]]) == 34):
            ende = next(((t, x) for t, x in f[1:] if x["da"] != 2 or x["boden"] != 0), None)
            punkte.append((f[0][0] - tk[0], "Schuetze", z["sch"], "Marke", z["rng2"], "Ziel", z["zx"], z["zy"], z["zz"], "Feld", z["zx"] >> 3, z["zy"] >> 3, "Ende", (ende[0] - tk[0], ende[1]["mx"], ende[1]["my"], ende[1]["h"], ende[1]["da"], ende[1]["boden"]) if ende else None))
    aus.append("Schuesse: " + str(sorted(schuesse.items(), key=str)))
    aus.append("Schuesse auf den Graben (erste 10): " + str(punkte[:10]))
    feuer = fe.feuer_lesen(pfad, k)
    je = collections.Counter()
    erste = []
    for s, f in feuer.items():
        a = f[0][1]
        fx, fy = a["mx"] >> 3, a["my"] >> 3
        seite = "links (Korb)" if fx < x0 + 20 else "rechts (ohne Korb)"
        je[(seite, a["stufe"], a["stark"])] += 1
        erste.append((f[0][0] - tk[0], fx, fy, a["stufe"], a["stark"], f[-1][0] - f[0][0]))
    aus.append("Feuer je (Seite, Stufe, Staerke): " + str(sorted(je.items(), key=str)))
    aus.append("Feuer der Reihe nach (Takt, x, y, Stufe, Staerke, Takte im Bild), erste 14 von %d: %s" % (len(erste), sorted(erste)[:14]))
    opfer = [e for e in plan["einheiten"] if e["rolle"] == "opfer"]
    for e in opfer:
        i = e["nr"]
        l0 = [(t, int(u[t]["leben"][i])) for t in tk]
        ver = collections.Counter(a[1] - b[1] for a, b in zip(l0, l0[1:]) if a[1] != b[1])
        aus.append("Opfer %d auf Feld (%d, %d): Leben Anfang %d, Ende %d, Verlust je Takt: %s" % (i, e["x"], e["y"], l0[0][1], l0[-1][1], ver.most_common(5)))
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "pech_pruefung.txt"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
