# -*- coding: utf-8 -*-
"""Szene streuung3: Schuetzen auf Mauer und Turm, Feuerkorb und Brandpfeile, Schuss nach oben.

Widerlegt die Regeln: Ein Brandpfeil macht mehr Schaden als ein normaler oder zuendet Huette oder Einheit an. Streuung nach oben weicht deutlich von Stufe / 300 ab. Die Zahl, gegen die verglichen wird, ist die Chance aus dem Modell.
Ausgabe: oben_pruefung.txt.
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
import streuung_modell as sm  # noqa: E402
from selfaware.tools.analysis.auge_auswertung import Aufzeichnung  # noqa: E402
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte  # noqa: E402

fp.U_F.update({"blick": "facingDirection", "schiesst": "shootTargetedUnit", "tgt": "targetingType", "sx": "shootTargetMicroX", "sy": "shootTargetMicroY", "sz": "shootTargetZ"})


def main():
    pfad = sorted(glob.glob(os.path.join(HIER, "..", "laeufe", "lauf_s_*_streuung3.auge")), key=os.path.getmtime)[-1]
    k = Feldkarte.laden(feldliste=FELDLISTE)
    plan = json.load(open(pfad + ".plan.json", encoding="utf-8"))
    lauf = fp.Lauf(pfad, k)
    u = lauf.u
    tk = sorted(u)
    aus = ["Datei %s, Takte %d, Fluege %d, nicht gesetzt %s, Mauer fehlt %s" % (os.path.basename(pfad), len(u), len(lauf.fluege), plan.get("nicht_gesetzt"), plan.get("mauer_fehlt"))]
    karte = {c["posten"]: c for c in plan["karte"]}
    aus.append("Orte: " + str({n: (c["x"], c["y"]) for n, c in karte.items()}))
    # Wer steht wo, wie hoch? Der letzte Rahmen vor dem Ende, alle Schuetzen
    st = u[tk[len(tk) // 2]]
    leute = collections.Counter()
    for i in np.nonzero((st["da"] != 0) & (st["bes"] == 1) & np.isin(st["typ"], [22, 23, 70, 72]))[0]:
        leute[(int(st["typ"][i]), "buildingHeight %d" % st["hb"][i], "terrainOrClimbHeight %d" % st["ht"][i])] += 1
    aus.append("Schuetzen von Spieler 1 in der Mitte des Laufs (Art, Hoehen): " + str(sorted(leute.items())))
    # Schuesse je Hoehe des Schuetzen und Marke
    je = collections.Counter()
    verlust = collections.Counter()
    gruppe = {}
    for s, f in lauf.fluege.items():
        z = f[0][1]
        t0 = f[0][0]
        if t0 - 1 not in u or z["art"] not in (1, 7, 33):
            continue
        q = u[t0 - 1]
        hb, ht = int(q["hb"][z["sch"]]), int(q["ht"][z["sch"]])
        oben = hb + ht > 8
        gruppe[s] = oben
        je[("oben" if oben else "unten", "Art %d" % z["art"], "Marke %d" % z["rng2"], "Start h %d" % z["h0"], "hb %d ht %d" % (hb, ht), "Ziel-Nr %s" % ("Einheit" if z["ziel"] > 0 else z["ziel"]))] += 1
        ende = next(((t, x) for t, x in f[1:] if x["da"] != 2 or x["boden"] != 0), None)
        if ende and z["ziel"] > 0 and ende[0] in u and ende[0] - 1 in u and ((ende[1]["da"] == 3 and ende[1]["boden"] == 9) or (z["rng2"] != 0 and ende[1]["da"] == 7)):
            d = int(u[ende[0] - 1]["leben"][z["ziel"]] - u[ende[0]]["leben"][z["ziel"]])
            verlust[("oben" if oben else "unten", "Geschoss %d" % z["art"], "Marke %d" % z["rng2"], "Ziel-Art %d" % int(u[ende[0]]["typ"][z["ziel"]]), "Ziel-Boden %d" % (int(u[ende[0]]["hb"][z["ziel"]]) + int(u[ende[0]]["ht"][z["ziel"]])), "Verlust %d" % d)] += 1
    aus.append("Schuesse (Ort des Schuetzen, Art, Marke, Starthoehe, Hoehen, Ziel): ")
    aus += ["   %s: %d" % (a, n) for a, n in sorted(je.items(), key=str)]
    aus.append("Verlust je Treffer: " + str(sorted(verlust.items(), key=str)))
    # Huette unter Brandpfeilen
    m = karte.get("mauer_korb")
    huette = next((g for g in plan["gebaeude"] if g.get("posten") == "mauer_korb" and "nr" in g), None)
    if huette:
        auf = Aufzeichnung(pfad)
        ib = auf.namen.index("DAT_BuildingsState")
        be = auf.bereiche[ib][1]
        ab, al = k.adresse("DAT_BuildingsState", "buildings[].fireDuration"), k.adresse("DAT_BuildingsState", "buildings[].currentHealth")
        erst, letzt = None, None
        for r, p, _ in auf.staende():
            if r.bereich == ib and r.rein:
                a = bytes(p)
                w = (int(np.ndarray(shape=(1,), dtype="<i2", buffer=a, offset=ab[0] + huette["nr"] * ab[2] - be)[0]), int(np.ndarray(shape=(1,), dtype="<i2", buffer=a, offset=al[0] + huette["nr"] * al[2] - be)[0]))
                erst = erst or (r.takt, w)
                letzt = (r.takt, w)
        aus.append("Huette (Brandzaehler, Leben): Anfang %s, Ende %s" % (erst, letzt))
    feuer = fe.feuer_lesen(pfad, k)
    if m:
        nah = sorted((f[0][0], f[0][1]["mx"] >> 3, f[0][1]["my"] >> 3, f[0][1]["stufe"], f[0][1]["stark"]) for s, f in feuer.items() if m["x"] - 3 <= f[0][1]["mx"] >> 3 <= m["x"] + m["breite"] + 3 and m["y"] - 3 <= f[0][1]["my"] >> 3 <= m["y"] + m["hoehe"] + 3)
        aus.append("Feuer im Bereich Mauer-Korb (Takt, x, y, Stufe, Staerke), erste 14 von %d: %s" % (len(nah), nah[:14]))
    # Pech
    a = k.adresse("DAT_TileMapState", "pitchDitches[].state")
    aus.append("Feld pitchDitches.state: " + str(a[:3]))
    # Schuss nach oben: Anteil gestreut gegen Modell
    no = karte.get("nach_oben")
    if no:
        g = collections.Counter()
        for s, f in lauf.fluege.items():
            z = f[0][1]
            t0 = f[0][0]
            if t0 - 1 not in u or z["ziel"] <= 0 or z["art"] not in (1, 7, 33):
                continue
            q = u[t0]
            ziel = z["ziel"]
            zb = int(q["hb"][ziel]) + int(q["ht"][ziel])
            e = int(u[t0 - 1]["ht"][z["sch"]])
            if zb - e <= 0:
                continue
            mitte = (int(q["x"][ziel]) * 8 + 4, int(q["y"][ziel]) * 8 + 4)
            genau = (z["zx"], z["zy"]) == mitte and z["zz"] == zb + 30
            stufe = sm.fehler_stufe(int(u[t0 - 1]["typ"][z["sch"]]), zb, e)
            g[(zb - e, stufe, "genau" if genau else "gestreut")] += 1
        aus.append("Schuss nach oben (Hoehenunterschied, Stufe, Ergebnis): " + str(sorted(g.items())))
        for hu, stufe in sorted({(a_[0], a_[1]) for a_ in g}):
            n = g[(hu, stufe, "genau")] + g[(hu, stufe, "gestreut")]
            aus.append("   Hoehe %d: Modell-Chance %.0f %%, gemessen %.0f %% von %d Schuessen" % (hu, 100 * stufe / 300, 100 * g[(hu, stufe, "gestreut")] / n, n))
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "oben_pruefung.txt"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
