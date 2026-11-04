# -*- coding: utf-8 -*-
"""B-142: Lauf-F-Punkte, die nur gesehen waren, jetzt nachrechnen: P093, P096 (Farmen), P121 (Eisen), P122 (Steinbruch), P223, P234 (Holz je Waffe). Dazu P111, P238 aus sonder8_g.

  PYTHONPATH="src;data/research/auge_plan/lauf_s_20261103" python data/research/auge_plan/lauf_s_20261103/punkte_rechnen20.py > data/research/auge_plan/lauf_s_20261103/punkte_rechnung20.txt
"""
import collections
import os

import numpy as np

import punkte_lesen as pl

K = pl.karte
F = os.path.join(pl.L, "lauf_f_20261102_214240.auge")
B = "DAT_BuildingsState"


def typen(p, namen):
    """Welche Gebaeude dieser Arten gab es, je Art die Nummern (aus dem letzten Rahmen)."""
    letzt = None
    for t, w in pl.stand(p, B, {"typ": "buildings[].buildingType"}):
        letzt = w["typ"].copy()
    return {n: [int(i) for i in (letzt == a).nonzero()[0]] for n, a in namen.items()}


def verlauf(p, nr, felder, n=4000):
    """Folge der Wechsel (Takt, Werte) eines Gebaeudes."""
    aus = []
    ad = {k: f"buildings[].{v}" for k, v in felder.items()}
    for t, w in pl.stand(p, B, ad):
        z = tuple(int(w[k][nr]) for k in felder)
        if not aus or aus[-1][1] != z:
            aus.append((t, z))
        if len(aus) > n:
            break
    return aus


def felder_von_gebaeude():
    s = K.struktur(B)
    m = None
    for o, tt, gr, nm in K.typen[s[3]]["felder"]:
        if nm == "buildings":
            m = tt
    el = m.split("[")[0].strip() if m else None
    return el, [(o, nm) for o, tt, gr, nm in K.typen[el]["felder"]]


def farm(p, namen):
    el, f = felder_von_gebaeude()
    print("Gebaeudefelder mit farm/grow/resource:", [(hex(o), n) for o, n in f if any(w in n.lower() for w in ("farm", "grow", "resource", "field119", "field_0x2a0", "0x2a0"))])
    for name, nr_liste in namen.items():
        for nr in nr_liste[:1]:
            v = verlauf(p, nr, {"st": "wheatGrowStateRelated"})
            print(name, nr, "wheatGrowStateRelated Wechsel", len(v), v[:16], "Werte", collections.Counter(x[1][0] for x in v).most_common())


def eisen(p, nr):
    v = verlauf(p, nr, {"state": "state", "eisen": "resourceIron"})
    print("P121 Mine", nr, "Wechsel", len(v), v[:40])
    ue = collections.Counter()
    for (t0, a), (t1, b) in zip(v, v[1:]):
        if a[1] != b[1]:
            ue[(a[0], b[1] - a[1], b[0])] += 1
    print("   (Zustand, Aenderung Eisen, Zustand danach)", ue.most_common(10))
    ende = collections.Counter()
    for (t0, a), (t1, b) in zip(v, v[1:]):
        if a[0] in (5, 6) and b[0] != a[0]:
            ende[(a[0], b[0], "Menge<7" if a[1] < 7 else "Menge>=7")] += 1
    print("   Ende von Zustand 5 oder 6 (von, nach, Menge):", ende.most_common(), "hoechste Menge:", max(x[1][1] for x in v))


def steinbruch(p, nr):
    v = verlauf(p, nr, {"state": "state", "f": "killingPitField", "stein": "resourceStone"})
    print("P122 Steinbruch", nr, "Wechsel", len(v), v[:30])
    c = collections.Counter()
    letzte = None
    abst = []
    for (t0, a), (t1, b) in zip(v, v[1:]):
        fa, fb = (a[1] >> 16) & 0xffff, (b[1] >> 16) & 0xffff  # field119_0x11e: die obere Haelfte von killingPitField
        if fa == 1 and fb == 0:
            c[("1 auf 0", b[2] - a[2])] += 1
            if letzte is not None:
                abst.append(t1 - letzte)
            letzte = t1
        if a[2] != b[2]:
            c[("Stein aendert sich", fa, fb, b[2] - a[2])] += 1
    print("   Wechsel und Stein:", c.most_common(10), "Abstand Takte:", collections.Counter(abst).most_common(6))


def waffe(p, nr, name):
    v = verlauf(p, nr, {"state": "state", "holz": "resourceWood"})
    ue = collections.Counter()
    for (t0, a), (t1, b) in zip(v, v[1:]):
        if a[1] != b[1]:
            ue[(a[1], b[1])] += 1
    print(name, nr, "Holz der Werkstatt, Wechsel (vorher, nachher):", ue.most_common(8), "Rahmen", len(v))


def oel(p, ofen_art):
    plan = pl.plan_von(p)
    S = plan["von"]
    letzt = None
    for t, w in pl.stand(p, B, {"typ": "buildings[].buildingType"}):
        letzt = w["typ"].copy()
    ofen = [int(i) for i in (letzt == ofen_art).nonzero()[0]]
    print("sonder8_g Oefen", ofen, "Plan", S, plan["bis"])
    for nr in ofen[:2]:
        v = verlauf(p, nr, {"state": "state", "pech": "resourcePitch", "anim": "animationIndex"})
        ue = collections.Counter()
        for (t0, a), (t1, b) in zip(v, v[1:]):
            if a[1] != b[1]:
                ue[(a[0], a[2], b[1] - a[1], b[0])] += 1
        print("  Ofen", nr, "Zustand-Folge", [x for x in pl.wechsel([(t, z[0]) for t, z in v])][:24])
        print("    Pech aendert sich (Zustand, Bild, um, Zustand danach):", ue.most_common(12))
    trage = [e for e in plan["einheiten"] if e.get("rolle") == "oel"]
    for e in trage[:4]:
        fo = []
        for t, u in pl.stand(p, "DAT_UnitsState", {"z": "units[].state", "w": "units[].resourceToDeposit"}):
            x = (int(u["z"][e["nr"]]), int(u["w"][e["nr"]]))
            if not fo or fo[-1][1] != x:
                fo.append((t - S, x))
        print("  Ingenieur", e["nr"], e.get("posten"), "(Takt, (Zustand, Traglast))", fo[:18])


if __name__ == "__main__":
    print("Lauf F Rahmen Gebaeude: siehe Takte der Wechsel")
    from selfaware.game.ucp.bauen import NACH_TYP
    arten = {v.get("laufzeitName"): t for t, v in NACH_TYP.items()}
    print({n: a for n, a in arten.items() if any(w in str(n) for w in ("MINE", "QUARRY", "FLETCH", "POLE", "OIL", "SMELT"))})
    wahl = {n: a for n, a in arten.items() if n in ("BT_IRONMINE", "BT_QUARRY", "BT_FLETCHER", "BT_POLETURNER", "BT_WHEATFARM", "BT_HOPFARM", "BT_OILSMELTER", "BT_MINE")}
    gebaeude = typen(F, wahl)
    print(gebaeude)
    farm(F, {n: gebaeude.get(n, []) for n in ("BT_WHEATFARM", "BT_HOPFARM")})
    for n, f_ in (("BT_IRONMINE", eisen), ("BT_MINE", eisen), ("BT_QUARRY", steinbruch)):
        for nr in gebaeude.get(n, [])[:1]:
            try:
                f_(F, nr)
            except KeyError as e:
                print(n, "Feld fehlt", e)
    for n in ("BT_FLETCHER", "BT_POLETURNER"):
        for nr in gebaeude.get(n, [])[:2]:
            waffe(F, nr, n)
    p8 = pl.neueste("sonder8_g")
    if p8:
        try:
            oel(p8, arten["BT_OILSMELTER"])
        except KeyError as e:
            print("oel Feld fehlt", e)
