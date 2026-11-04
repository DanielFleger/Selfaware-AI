# -*- coding: utf-8 -*-
"""B-142 Lauf S, zweiter Nachlauf im Editor (Szene sonder10): Weg auf den Turm, Tor mit Entwarnung und Durchgang, Trupp mit einem Kaempfenden, Hang. Die Urteile stehen in Punkte_Lauf_S.md.

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/punkte_rechnen8.py > data/research/auge_plan/lauf_s_20261103/punkte_rechnung8.txt
"""
import collections
import json
import os

import punkte_lesen as pl
from selfaware.tools.analysis import auge_regeln as ar

U = {"da": "units[].logicalState", "typ": "units[].unitType", "b": "units[].owner", "mx": "units[].microXPosition", "my": "units[].microYPosition", "z": ("units[].logicalState", ar.ZUSTAND_ABSTAND)}
p = pl.neueste("sonder10")
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


def wege(liste, jeder=1):
    """Je Einheit die Wechsel des Feldes samt Kletterhoehe."""
    v = {e["nr"]: [] for e in liste}
    for t, u in pl.stand(p, "DAT_UnitsState", {**U, "h": "units[].terrainOrClimbHeight"}, jeder=jeder):
        for e in liste:
            n = e["nr"]
            w = (int(u["mx"][n]) // 8, int(u["my"][n]) // 8, int(u["h"][n]))
            if not v[n] or v[n][-1][1:] != w:
                v[n].append((t - START, *w))
    return v


def kopf():
    print("sonder10 Takte", plan["bis"] - plan["von"], "kein Platz", plan["kein_platz"], "nicht gesetzt", plan["nicht_gesetzt"], "Posten", {k: (o["x"], o["y"]) for k, o in ort.items()})
    if os.path.exists(p + ".regeln.json"):
        z = json.load(open(p + ".regeln.json", encoding="utf-8"))["zeilen"]
        print("fremd:", {r["posten"]: r["fremd"] for r in z if r["fremd"]["schlaeger"] or r["fremd"]["geschosse"]})


def mauer(name):
    """Stehen Mauer und Treppe? Hoehe auf der Linie (Raster 25)."""
    o = ort[name]
    y = o["y"] + 3
    b = json.load(open(os.path.join(os.path.dirname(p), "..", "lauf_s_20261103", "feldnummern.json"), encoding="utf-8"))
    basis = b["basis"] if isinstance(b, dict) and "basis" in b else b
    felder = [(o["x"] + i, y, basis[y] + o["x"] + i) for i in range(1, 14)]
    letzte = None
    for t, m in pl.stand(p, "DAT_TileMapState", {"h": "HeightLayer[]"}, rein=False):
        w = tuple(int(m["h"][f[2]]) for f in felder)
        if w != letzte:
            if letzte is None or t - START < 300:
                print("  ", name, "Hoehe x+1 bis x+13, Takt", t - START, w)
            letzte = w
    print("  ", name, "Hoehe am Ende", letzte)


def tuerme():
    """P338, P302."""
    for name in ("turm_oben", "turm4"):
        print(name, "Gebaeude", [(g["typ"], g["x"], g["y"], g["spieler"]) for g in gb[name]], "Einheiten", [(e["typ"], e["x"], e["y"]) for e in wer[name]])
        mauer(name)
        if not gb[name]:
            continue
        n = gb[name][0]["nr"]
        v = []
        for t, b in pl.stand(p, "DAT_BuildingsState", {"top": "buildings[].hasUnitsOntop", "z": "buildings[].field288_0x2fa"}):
            w = (int(b["top"][n]), int(b["z"][n]))
            if not v or v[-1][1:] != w:
                v.append((t - START, *w))
        print("   (Takt, hasUnitsOntop, Zaehler):", v[:12], "Wechsel", len(v))
        w = wege(wer[name])
        for e in wer[name]:
            s = w[e["nr"]]
            print("   Nr", e["nr"], "Wechsel", len(s), "hoechste Hoehe", max(x[3] for x in s), "Anfang", s[:2], "Ende", s[-3:])
        vu, ende = einheiten(wer[name], {"ziel": "units[].targetingType"})
        for e in wer[name][:2]:
            print("   Zustand Nr", e["nr"], vu[e["nr"]][:8], "Ende", ende.get(e["nr"]))


def tore():
    """P304."""
    for name in ("tor_weg", "tor_offen", "tor_zu"):
        if not gb[name]:
            print(name, "kein Tor", plan["nicht_gesetzt"])
            continue
        n = gb[name][0]["nr"]
        v = collections.defaultdict(list)
        for t, b in pl.stand(p, "DAT_BuildingsState", {"z": "buildings[].gateState", "z2": "buildings[].gateState2", "ti": "buildings[].gateCloseOpenTimer", "pl": "buildings[].pathLinkageRelated2"}):
            for k in ("z", "ti", "pl"):
                w = int(b[k][n])
                if not v[k] or v[k][-1][1] != w:
                    v[k].append((t - START, w))
            w = int(b["z2"][n])
            if not v["z2"] or (w > v["z2"][-1][1]) or (w == 0 and v["z2"][-1][1] != 0):
                v["z2"].append((t - START, w))
        g = gb[name][0]
        print(name, "Tor bei", (g["x"], g["y"]), "gateState", v["z"][:9], "pathLinkage", v["pl"][:9], "gateState2 (Spruenge)", v["z2"][:8], "Timer", v["ti"][:3])
        w = wege(wer[name])
        for e in wer[name]:
            s = w[e["nr"]]
            print("   ", e["rolle"], "Art", e["typ"], "Spieler", e.get("spieler"), "von", (e["x"], e["y"]), "Wechsel", len(s), "Ende", s[-2:], "Abstand zum Tor am Anfang", max(abs(e["x"] - g["x"]), abs(e["y"] - g["y"])))
        # Der Geher: wann ist er durch die Mauerlinie?
        for e in wer[name]:
            if e["rolle"] == "geher":
                durch = next((x for x in w[e["nr"]] if x[2] > ort[name]["y"] + 5), None)
                print("    Geher ueber die Mauerlinie (Takt, x, y, Hoehe):", durch, "Linie y", ort[name]["y"] + 5, "Tor x", g["x"], "bis", g["x"] + 4)


def trupp():
    """P325."""
    liste = wer["trupp_nah"]
    tr = [e for e in liste if e["rolle"] == "trupp"]
    k = next(e for e in liste if e["rolle"] == "feind")
    stufen = {}
    sch = collections.Counter()
    for t, u in pl.stand(p, "DAT_UnitsState", {**U, "px": "units[].plannedDestinationX", "py": "units[].plannedDestinationY", "tri": "units[].tribeID", "s": "units[].attackedUnitID", "l": "units[].health", "tm": "units[].targetingType"}):
        ist = tuple((int(u["px"][e["nr"]]), int(u["py"][e["nr"]])) for e in tr)
        if ist not in stufen:
            stufen[ist] = (t - START, tuple(int(u["tri"][e["nr"]]) for e in tr), tuple(int(u["s"][e["nr"]]) for e in tr), tuple(int(u["z"][e["nr"]]) for e in tr), tuple(int(u["tm"][e["nr"]]) for e in tr), tuple((int(u["mx"][e["nr"]]) // 8, int(u["my"][e["nr"]]) // 8) for e in tr), int(u["l"][k["nr"]]))
    print("trupp_nah Einheiten", [(e["nr"], e["x"], e["y"]) for e in tr], "Feind", (k["nr"], k["x"], k["y"]))
    for ist, (t, tri, s, z, tm, wo, l) in list(stufen.items())[:9]:
        print("   Takt", t, "Trupps", tri, "schlaegt", s, "Zustand", z, "Anweisung", tm, "Ziele", ist, "Orte", wo, "Leben Feind", l)
    print("   Stufen", len(stufen))


def hang():
    """P330."""
    if not wer["bergauf"]:
        print("P330 kein Hang gefunden")
        return
    v, ende = einheiten(wer["bergauf"], {"c": "units[].calculatedMovementSpeed", "m": "units[].movementSpeed", "h": "units[].terrainOrClimbHeight"})
    print("P330 bergauf von", [(e["x"], e["y"]) for e in wer["bergauf"]], "(Takt, Zustand, berechnet, movementSpeed, Hoehe):", list(v.values())[0][:40], "Ende", ende)


if __name__ == "__main__":
    for f in (kopf, tuerme, tore, trupp, hang):
        try:
            f()
        except Exception as e:
            import traceback
            print("FEHLER", f.__name__, repr(e))
            traceback.print_exc(limit=2)
