# -*- coding: utf-8 -*-
"""B-142 Lauf S, Nachlauf im Editor (Szene sonder8). Die Urteile stehen in Punkte_Lauf_S.md.

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/punkte_rechnen6.py > data/research/auge_plan/lauf_s_20261103/punkte_rechnung6.txt
"""
import collections
import json
import os

import numpy as np

import punkte_lesen as pl
from selfaware.tools.analysis import auge_regeln as ar

U = {"da": "units[].logicalState", "typ": "units[].unitType", "b": "units[].owner", "mx": "units[].microXPosition", "my": "units[].microYPosition", "z": ("units[].logicalState", ar.ZUSTAND_ABSTAND)}
MANN = "units[].digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300"
p = pl.neueste("sonder8")
plan = pl.plan_von(p)
ort = {k["posten"]: k for k in plan["karte"]}
wer = collections.defaultdict(list)
for e in plan["einheiten"]:
    if "nr" in e:
        wer[e.get("posten")].append(e)
gb = collections.defaultdict(list)
for g in plan["gebaeude"]:
    if "nr" in g:
        gb[g.get("posten")].append(g)
START = plan["von"]


def einheiten(liste, felder=None):
    """Je Einheit die Wechsel von Zustand plus Zusatzfeldern und der letzte Ort."""
    f = {**U, **(felder or {})}
    v = {e["nr"]: [] for e in liste}
    ende = {}
    for t, u in pl.stand(p, "DAT_UnitsState", f):
        for e in liste:
            n = e["nr"]
            if u["typ"][n] != e["typ"] or not u["da"][n]:
                if not v[n] or v[n][-1][1] != "weg":
                    v[n].append((t - START, "weg"))
                continue
            w = (int(u["z"][n]),) + tuple(int(u[k][n]) for k in (felder or {}))
            if not v[n] or v[n][-1][1:] != w:
                v[n].append((t - START, *w))
            ende[n] = (int(u["mx"][n]) // 8, int(u["my"][n]) // 8)
    return v, ende


def kopf():
    print("sonder8 Takte", plan["bis"] - plan["von"], "kein Platz", plan["kein_platz"], "nicht gesetzt", plan["nicht_gesetzt"], "Posten", {k: (o["x"], o["y"]) for k, o in ort.items()})
    z = json.load(open(p + ".regeln.json", encoding="utf-8"))["zeilen"]
    print("fremd:", {r["posten"]: r["fremd"] for r in z if r["fremd"]["schlaeger"] or r["fremd"]["geschosse"]})


def mauer_art():
    """P353 bis P357, P366 bis P368, P322: Hoehe und Schaden am Zielfeld."""
    ziele = ort["mauer_art"]["felder"]
    leute = wer["mauer_art"]
    v = {z[2]: [] for z in ziele}
    for t, m in pl.stand(p, "DAT_TileMapState", {"h": "HeightLayer[]", "d": "DamageLayer[]"}, rein=False):
        for z in ziele:
            w = (int(m["h"][z[2]]), int(m["d"][z[2]]))
            if not v[z[2]] or v[z[2]][-1][1:] != w:
                v[z[2]].append((t - START, *w))
    print("Mauer je Art (Takt, Hoehe, Schaden), Raster 25:")
    for e, z in zip(leute, ziele):
        s = v[z[2]]
        schritte = collections.Counter(b[2] - a[2] for a, b in zip(s, s[1:]) if b[2] > a[2])
        print("  ", e["rolle"], "Art", e["typ"], "Feld", z[:2], "Wechsel", len(s), "Schaden je Wechsel", schritte.most_common(3), "Folge", s[:6], "...", s[-2:])


def turmgeraet():
    """P344: Zustand, Bemannung, neues Gebaeude."""
    liste = [e for e in wer["turmgeraet"] if e["typ"] == 58]
    v, ende = einheiten(liste, {"man": MANN, "ziel": "units[].targetingType"})
    print("Belagerungsturm (Takt, Zustand, Mann, Anweisung):", v[liste[0]["nr"]][:14], "Ende", ende)
    neu = {}
    for t, b in pl.stand(p, "DAT_BuildingsState", {"typ": "buildings[].buildingType", "da": "buildings[].logicalState", "x": "buildings[].x", "y": "buildings[].y", "o": "buildings[].owner"}):
        o = ort["turmgeraet"]
        m = (b["da"] != 0) & (b["x"] >= o["x"]) & (b["x"] < o["x"] + o["breite"]) & (b["y"] >= o["y"]) & (b["y"] < o["y"] + o["hoehe"])
        for i in np.nonzero(m)[0]:
            neu.setdefault((int(i), int(b["typ"][i])), (t - START, int(b["x"][i]), int(b["y"][i]), int(b["o"][i])))
    print("   Gebaeude im Posten (Platz, Art): (Takt, x, y, Besitzer):", neu)


def ramme():
    """P328, P345."""
    r = [e for e in wer["ramme"] if e["typ"] == 59]
    v, ende = einheiten(r, {"man": MANN, "ziel": "units[].targetedBuildingTile"})
    for e in r:
        print("Ramme mann", e["mann"], "Nr", e["nr"], "von", (e["x"], e["y"]), "Ende", ende.get(e["nr"]), "Wechsel", v[e["nr"]][:7])
    if gb["ramme"]:
        n = gb["ramme"][0]["nr"]
        s = []
        for t, b in pl.stand(p, "DAT_BuildingsState", {"le": "buildings[].currentHealth"}):
            w = int(b["le"][n])
            if not s or s[-1][1] != w:
                s.append((t - START, w))
        print("   Tor Leben:", s[:10], "...", s[-2:], "Verlust je Wechsel:", collections.Counter(a[1] - c[1] for a, c in zip(s, s[1:])).most_common(4))


def tore():
    """P303, P304."""
    for name in ("tor_24", "tor_26", "tor_feld"):
        if not gb[name]:
            print(name, "kein Tor")
            continue
        n = gb[name][0]["nr"]
        v = collections.defaultdict(list)
        for t, b in pl.stand(p, "DAT_BuildingsState", {"z": "buildings[].gateState", "z2": "buildings[].gateState2", "ti": "buildings[].gateCloseOpenTimer", "pl": "buildings[].pathLinkageRelated2", "f": "buildings[].field268_0x2c6"}):
            for k in ("z", "ti", "pl", "f"):
                w = int(b[k][n])
                if not v[k] or v[k][-1][1] != w:
                    v[k].append((t - START, w))
            w = int(b["z2"][n])
            if not v["z2"] or (w > v["z2"][-1][1]) or (w == 0 and v["z2"][-1][1] != 0):
                v["z2"].append((t - START, w))
        print(name, "gateState", v["z"][:7], "pathLinkage", v["pl"][:7], "gateState2 (Spruenge)", v["z2"][:6], "Timer", v["ti"][:3], "field268", v["f"][:4])
        vf, ende = einheiten(wer[name])
        print("    Feind:", {k: w[:5] for k, w in vf.items()}, "Ende", ende)
    z = collections.Counter()
    o = ort["tor_feld"]
    for t, e in pl.stand(p, "DAT_EntityState", {"art": "entityArray[].entityType", "da": "entityArray[].logicalState", "mx": "entityArray[].microX", "my": "entityArray[].microY"}):
        m = (e["da"] != 0) & np.isin(e["art"], [10, 11, 12]) & (e["mx"] // 8 >= o["x"]) & (e["mx"] // 8 < o["x"] + 14) & (e["my"] // 8 >= o["y"]) & (e["my"] // 8 < o["y"] + 8)
        for a in e["art"][m]:
            z[int(a)] += 1
    print("   Flaggen im Posten tor_feld, Rahmen je Art:", dict(z))


def tuerme():
    """P338, P302."""
    if gb["turm_oben"]:
        t0 = gb["turm_oben"][0]
        fl = [(t0["x"] + i, t0["y"] + j) for i in range(3) for j in range(3)]
        hoch = 0
        verlauf = []
        for t, u in pl.stand(p, "DAT_UnitsState", {**U, "h": "units[].terrainOrClimbHeight"}):
            n = sum(1 for e in wer["turm_oben"] if (int(u["mx"][e["nr"]]) // 8, int(u["my"][e["nr"]]) // 8) in fl)
            hoehe = [int(u["h"][e["nr"]]) for e in wer["turm_oben"]]
            hoch = max(hoch, n)
            if not verlauf or verlauf[-1][1:] != (n, max(hoehe)):
                verlauf.append((t - START, n, max(hoehe)))
        print("P338 Wachturm (Takt, auf dem Grundriss, hoechste Hoehe):", verlauf[:8], "hoechstens", hoch)
    if gb["turm4"]:
        n = gb["turm4"][0]["nr"]
        v = []
        for t, b in pl.stand(p, "DAT_BuildingsState", {"top": "buildings[].hasUnitsOntop", "z": "buildings[].field288_0x2fa"}):
            w = int(b["top"][n])
            z = int(b["z"][n])
            if not v or v[-1][1] != w:
                v.append((t - START, w, z))
        vu, ende = einheiten(wer["turm4"], {"h": "units[].terrainOrClimbHeight"})
        print("P302 Turm 4 (Takt, hasUnitsOntop, Zaehler):", v[:6], "Einheit:", list(vu.values())[0][:6], "Ende", ende)


def trupps():
    """P326, P325."""
    for name in ("trupp_frei", "trupp_kampf"):
        liste = wer[name]
        tr = [e for e in liste if e["rolle"] == "trupp"]
        erste = {}
        for t, u in pl.stand(p, "DAT_UnitsState", {**U, "px": "units[].plannedDestinationX", "py": "units[].plannedDestinationY", "tri": "units[].tribeID", "sch": "units[].attackedUnitID"}):
            ist = tuple((int(u["px"][e["nr"]]), int(u["py"][e["nr"]])) for e in tr)
            if ist not in erste:
                erste[ist] = (t - START, tuple(int(u["tri"][e["nr"]]) for e in tr), tuple(int(u["sch"][e["nr"]]) for e in tr))
        print(name, "Stufen der Zielfelder:", len(erste))
        for ist, (t, tri, sch) in list(erste.items())[:5]:
            ds = [max(abs(a[0] - b[0]), abs(a[1] - b[1])) for i, a in enumerate(ist) for b in ist[i + 1:]]
            print("    Takt", t, "Trupps", sorted(set(tri)), "schlaegt", [1 if s else 0 for s in sch], "Ziele", ist, "kleinster Abstand", min(ds), "groesster", max(ds))


def rest():
    """P343, P352, P371, P330."""
    v, ende = einheiten(wer["unerreichbar"], {"ziel": "units[].targetingType"})
    print("P343 unerreichbar:", {k: w[:8] for k, w in v.items()}, "Ende", ende, "Start", [(e["x"], e["y"]) for e in wer["unerreichbar"]])
    v, ende = einheiten(wer["vorbei"], {"ziel": "units[].targetingType"})
    g = ar.geschosse_lesen(p, pl.karte)
    for e in wer["vorbei"]:
        sch = sorted(x["von"] - START for x in g if x["schuetze"] == e["nr"])
        print("P352/P371", e["rolle"], "Art", e["typ"], "Ende", ende.get(e["nr"]), "Schuesse", len(sch), sch[:6], "Wechsel", v[e["nr"]][:8], "Abstaende", [b - a for a, b in zip(sch, sch[1:])][:6])
    if wer["bergauf"]:
        v, ende = einheiten(wer["bergauf"], {"c": "units[].calculatedMovementSpeed", "m": "units[].movementSpeed", "h": "units[].terrainOrClimbHeight"})
        print("P330 bergauf (Takt, Zustand, berechnet, movementSpeed, Hoehe):", list(v.values())[0][:30], "Ende", ende)
    else:
        print("P330 kein Hang gefunden")


if __name__ == "__main__":
    for f in (kopf, mauer_art, turmgeraet, ramme, tore, tuerme, trupps, rest):
        try:
            f()
        except Exception as e:
            import traceback
            print("FEHLER", f.__name__, repr(e))
            traceback.print_exc(limit=2)
