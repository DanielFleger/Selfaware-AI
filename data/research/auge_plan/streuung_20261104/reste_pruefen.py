# -*- coding: utf-8 -*-
"""Die Reste der Streuung in der Szene streuung2: Schuetze auf der Mauer, Brandpfeile, Pech, Feuer an Baeumen.

Widerlegt die Regel: Ein Brandpfeil, der mehr Schaden macht als ein normaler oder etwas anzuendet. Ein Baum, der ohne Feuer brennt, oder ein Feuer auf einem Baumfeld, das den Baum nicht anzuendet (Eiche und Co. bis Art 4, Stufe 3 und mehr).
Ausgabe: reste_pruefung.txt.
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
from selfaware.tools.analysis.auge_auswertung import Aufzeichnung  # noqa: E402
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte  # noqa: E402

fp.U_F.update({"blick": "facingDirection", "schiesst": "shootTargetedUnit", "tgt": "targetingType"})
T_F = {"art": "treeType", "stufe": "stage", "zustand": "state", "feuer": "field92_0x98", "x": "xPosition", "y": "yPosition", "tile": "tile"}


def baeume_lesen(pfad, k):
    """Baumdaten je Rahmen, nur was sich aendert."""
    auf = Aufzeichnung(pfad)
    il = auf.namen.index("DAT_LandscapeState")
    bl = auf.bereiche[il][1]
    ad = {}
    for n, f in T_F.items():
        try:
            ad[n] = k.adresse("DAT_LandscapeState", "trees[]." + f)
        except KeyError:
            pass
    aus = []
    for r, p, _ in auf.staende():
        if r.bereich != il or not r.rein:
            continue
        a = bytes(p)
        aus.append((r.takt, {n: np.array(np.ndarray(shape=(v[3],), dtype={1: "<u1", 2: "<i2", 4: "<i4"}[v[1]], buffer=a, offset=v[0] - bl, strides=(v[2],))) for n, v in ad.items()}))
    return aus


def main():
    pfad = sorted(glob.glob(os.path.join(HIER, "..", "laeufe", "lauf_s_*_streuung2.auge")), key=os.path.getmtime)[-1]
    k = Feldkarte.laden(feldliste=FELDLISTE)
    plan = json.load(open(pfad + ".plan.json", encoding="utf-8"))
    lauf = fp.Lauf(pfad, k)
    u = lauf.u
    zeilen = fp.zeilen_lesen()
    aus = ["Datei %s, Takte %d, Fluege %d" % (os.path.basename(pfad), len(u), len(lauf.fluege))]
    aus.append("Plan: nicht gesetzt %s, kein Platz %s" % (plan.get("nicht_gesetzt"), plan.get("kein_platz")))
    # 1. Schuetzen auf der Mauer
    mauer = [e for e in plan["einheiten"] if e.get("posten") == "mauer_korb" and e["rolle"] == "schuetze"]
    tk = sorted(u)
    for e in mauer:
        i = e["nr"]
        for t in (tk[0], tk[len(tk) // 4], tk[len(tk) // 2], tk[-1]):
            st = u[t]
            aus.append("Mauer-Schuetze %d Takt +%d: Feld %d %d, buildingHeight %d, terrainOrClimbHeight %d, Art %d, Leben %d" % (i, t - tk[0], st["x"][i], st["y"][i], st["hb"][i], st["ht"][i], st["typ"][i], st["leben"][i]))
    # 2. Brandpfeile
    nr = {e["nr"] for e in mauer}
    brand = collections.Counter()
    rows = []
    for s, f in lauf.fluege.items():
        z = f[0][1]
        if z["sch"] in nr:
            brand[(z["art"], "rng2=%d" % z["rng2"], "v=%d" % z["v"], "Start h %d" % z["h0"], "Ziel z %d" % z["zz"])] += 1
            rows.append((s, z, f))
    aus.append("Schuesse der Mauer-Schuetzen (Art, Marke, Tempo, Hoehe): " + str(sorted(brand.items())))
    # Schaden je Marke an derselben Zielart
    verlust = collections.Counter()
    for s, z, f in rows:
        ende = next(((t, x) for t, x in f[1:] if x["da"] != 2 or x["boden"] != 0), None)
        if ende is None or z["ziel"] <= 0 or ende[0] not in u or ende[0] - 1 not in u:
            continue
        if ende[1]["da"] == 3 and ende[1]["boden"] == 9:
            d = int(u[ende[0] - 1]["leben"][z["ziel"]] - u[ende[0]]["leben"][z["ziel"]])
            verlust[("rng2=%d" % z["rng2"], "Ziel-Art %d" % int(u[ende[0]]["typ"][z["ziel"]]), d)] += 1
    aus.append("Verlust je Treffer (Marke, Ziel, Verlust): " + str(sorted(verlust.items())))
    verlust_normal = collections.Counter()
    for s, f in lauf.fluege.items():
        z = f[0][1]
        if z["sch"] in nr or z["art"] != 1 or z["rng2"] != 0 or z["ziel"] <= 0:
            continue
        ende = next(((t, x) for t, x in f[1:] if x["da"] != 2 or x["boden"] != 0), None)
        if ende and ende[1]["da"] == 3 and ende[1]["boden"] == 9 and ende[0] in u and ende[0] - 1 in u:
            d = int(u[ende[0] - 1]["leben"][z["ziel"]] - u[ende[0]]["leben"][z["ziel"]])
            verlust_normal[("Ziel-Art %d" % int(u[ende[0]]["typ"][z["ziel"]]), d)] += 1
    aus.append("Zum Vergleich, normale Pfeile vom Boden: " + str(sorted(verlust_normal.items())))
    # 3. Huette unter Brandpfeilen, Pech, Feuer rundherum
    feuer = fe.feuer_lesen(pfad, k)
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
        aus.append("Huette unter Pfeilen vom Mauer-Korb: Anfang (Brand, Leben) %s, Ende %s" % (erst, letzt))
    orte = {e["posten"]: e for e in plan["einheiten"] if e.get("posten") == "mauer_korb"}
    karte = {c["posten"]: c for c in plan["karte"]}
    m = karte.get("mauer_korb")
    if m:
        nah = [(f[0][0], f[0][1]["mx"] >> 3, f[0][1]["my"] >> 3, f[0][1]["stufe"], f[0][1]["stark"]) for s, f in feuer.items() if m["x"] - 2 <= f[0][1]["mx"] >> 3 <= m["x"] + m["breite"] + 2 and m["y"] - 2 <= f[0][1]["my"] >> 3 <= m["y"] + m["hoehe"] + 2]
        aus.append("Feuer im Bereich des Mauer-Korbs (Takt, x, y, Stufe, Staerke), erste 12 von %d: %s" % (len(nah), sorted(nah)[:12]))
    # 4. Baeume
    ft = [e for e in plan["einheiten"] if e.get("posten") == "baeume"]
    aus.append("Feuerwerfer an den Baeumen: " + str([(e["nr"], e["x"], e["y"]) for e in ft]))
    if ft:
        ziel = next(((f[0][1]["zx"] >> 3, f[0][1]["zy"] >> 3) for s, f in lauf.fluege.items() if f[0][1]["sch"] == ft[0]["nr"]), None)
        aus.append("Erster Zielpunkt der Flammen (Feld): " + str(ziel))
        bm = baeume_lesen(pfad, k)
        gel = lauf.gel[0][1]
        if ziel and bm:
            nahe_feuer = [(f[0][0], f[0][1]["mx"] >> 3, f[0][1]["my"] >> 3, f[0][1]["stufe"], f[0][1]["stark"], int(gel["logik"][f[0][1]["feld"]]) & 0x1000 != 0, f[-1][0] - f[0][0]) for s, f in feuer.items() if abs((f[0][1]["mx"] >> 3) - ziel[0]) <= 25 and abs((f[0][1]["my"] >> 3) - ziel[1]) <= 25]
            aus.append("Feuer rund um die Baeume: %d. Erste 20 (Takt, x, y, Stufe, Staerke, Baumfeld, Takte im Bild): %s" % (len(nahe_feuer), sorted(nahe_feuer)[:20]))
            auf_baum = [x for x in nahe_feuer if x[5]]
            aus.append("davon auf Baumfeldern: %d, nach Stufe %s" % (len(auf_baum), sorted(collections.Counter(x[3] for x in auf_baum).items())))
            a0 = bm[0][1]
            en = bm[-1][1]
            n = len(next(iter(a0.values())))
            ge = []
            for i in range(n):
                if any(int(a0[f_][i]) != int(en[f_][i]) for f_ in a0 if f_ in ("stufe", "zustand", "feuer")):
                    ge.append({f_: (int(a0[f_][i]), int(en[f_][i])) for f_ in a0})
            aus.append("Baeume, die sich von Anfang bis Ende geaendert haben: %d, Beispiele: %s" % (len(ge), ge[:6]))
            je_art = collections.Counter((g["art"][0], g["stufe"][0] >= 3, g["feuer"][1] != 0 if "feuer" in g else None, g["zustand"][1] if "zustand" in g else None) for g in ge)
            aus.append("Geaendert je (Art, Stufe ab 3, Feuer-Zaehler, Zustand am Ende): " + str(sorted(je_art.items(), key=str)[:20]))
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "reste_pruefung.txt"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
