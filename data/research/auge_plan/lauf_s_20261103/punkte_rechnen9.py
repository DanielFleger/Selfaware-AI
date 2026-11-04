# -*- coding: utf-8 -*-
"""B-142 Lauf S, dritter Nachlauf im Editor (Szene sonder12): Weg auf den Turm, Tor-Grenze, Tor mit Mauer, Trupp mit Ziel im Ring, Hang. Die Urteile stehen in Punkte_Lauf_S.md.

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/punkte_rechnen9.py > data/research/auge_plan/lauf_s_20261103/punkte_rechnung9.txt
"""
import collections
import json
import os
import sys

import numpy as np

import punkte_lesen as pl
from selfaware.tools.analysis import auge_regeln as ar

U = {"da": "units[].logicalState", "typ": "units[].unitType", "b": "units[].owner", "mx": "units[].microXPosition", "my": "units[].microYPosition", "z": ("units[].logicalState", ar.ZUSTAND_ABSTAND)}
HIER = os.path.dirname(os.path.abspath(__file__))
FN = json.load(open(os.path.join(HIER, "feldnummern.json"), encoding="utf-8"))
SZENE = sys.argv[1] if len(sys.argv) > 1 else "sonder12"
p = pl.neueste(SZENE)
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


def reihe(liste, felder):
    """Je Einheit die Wechsel der Felder, der Ort geht mit."""
    f = {**U, **felder}
    v = {e["nr"]: [] for e in liste}
    for t, u in pl.stand(p, "DAT_UnitsState", f):
        for e in liste:
            n = e["nr"]
            if u["typ"][n] != e["typ"] or not u["da"][n]:
                if not v[n] or v[n][-1][1] != "weg":
                    v[n].append((t - START, "weg"))
                continue
            w = (int(u["mx"][n]) // 8, int(u["my"][n]) // 8, int(u["z"][n])) + tuple(int(u[k][n]) for k in felder)
            if not v[n] or v[n][-1][1:] != w:
                v[n].append((t - START, *w))
    return v


def karte_ende():
    h = b = None
    for t, m in pl.stand(p, "DAT_TileMapState", {"h": "HeightLayer[]", "b": "BuildingLayer[]"}, rein=False):
        h, b = np.array(m["h"]), np.array(m["b"])
    return h, b


def kopf():
    print(SZENE, "Takte", plan["bis"] - plan["von"], "Mauer fehlt", plan.get("mauer_fehlt"), "wiederholt", plan.get("mauer_wiederholt"), "kein Platz", plan["kein_platz"], "nicht gesetzt", plan["nicht_gesetzt"], "Posten", {k: (o["x"], o["y"]) for k, o in ort.items()})
    if os.path.exists(p + ".regeln.json"):
        z = json.load(open(p + ".regeln.json", encoding="utf-8"))["zeilen"]
        print("fremd:", {r["posten"]: r["fremd"] for r in z if r["fremd"]["schlaeger"] or r["fremd"]["geschosse"]})


def tuerme():
    """P338, P302, P330 an der Treppe."""
    h, _ = karte_ende()
    for name in ("nur_mauer", "turm_eck", "turm_mitte", "turm_treppe", "turm_direkt", "turm4_weg", "turm_voll", "turm4_gang"):
        if name not in ort:
            continue
        if not gb[name]:
            v = reihe(wer[name], {"h": "units[].terrainOrClimbHeight", "c": "units[].calculatedMovementSpeed", "m": "units[].movementSpeed"})
            for s in v.values():
                print(name, "ohne Turm (Takt, x, y, Zustand, Hoehe, berechnet, Grund): Wechsel", len(s), s[:40], "Ende", s[-2:])
            continue
        t0 = gb[name][0]
        o = ort[name]
        print(name, "Turm", (t0["typ"], t0["x"], t0["y"]), "Einheiten", [(e["x"], e["y"]) for e in wer[name]][:2], "Anzahl", len(wer[name]))
        for j in range(o["hoehe"]):
            print("    y", o["y"] + j, " ".join(f"{int(h[FN[o['y'] + j] + o['x'] + i]):3d}" for i in range(o["breite"])))
        w = 3 if t0["typ"] == 74 else 6
        fl = {(t0["x"] + i, t0["y"] + j) for i in range(w) for j in range(w)}
        n = t0["nr"]
        vb = []
        for t, b in pl.stand(p, "DAT_BuildingsState", {"top": "buildings[].hasUnitsOntop", "c": "buildings[].field288_0x2fa"}):
            a = (int(b["top"][n]), int(b["c"][n]))
            if not vb or vb[-1][1:] != a:
                vb.append((t - START, *a))
        print("    Gebaeude (Takt, hasUnitsOntop, Zaehler): Wechsel", len(vb), vb[:10], "...", vb[-3:])
        ober, hoch, verlauf = 0, 0, []
        schnell = collections.Counter()
        for t, u in pl.stand(p, "DAT_UnitsState", {**U, "h": "units[].terrainOrClimbHeight", "c": "units[].calculatedMovementSpeed", "m": "units[].movementSpeed"}):
            k = sum(1 for e in wer[name] if (int(u["mx"][e["nr"]]) // 8, int(u["my"][e["nr"]]) // 8) in fl)
            hh = max(int(u["h"][e["nr"]]) for e in wer[name])
            ober, hoch = max(ober, k), max(hoch, hh)
            if not verlauf or verlauf[-1][1:] != (k, hh):
                verlauf.append((t - START, k, hh))
            for e in wer[name]:
                schnell[int(u["c"][e["nr"]]) - int(u["m"][e["nr"]])] += 1
        print("    auf dem Grundriss hoechstens", ober, "hoechste Hoehe", hoch, "(Takt, Zahl, Hoehe):", verlauf[:14], "...", verlauf[-2:])
        print("    berechnet minus Grundtempo (Wert: Rahmen je Einheit):", sorted(schnell.items()))
        v = reihe(wer[name][:1], {"h": "units[].terrainOrClimbHeight", "ziel": "units[].targetingType"})
        s = list(v.values())[0]
        print("    erste Einheit (Takt, x, y, Zustand, Hoehe, Anweisung):", s[:6], "...", s[-3:], "Wechsel", len(s))


def tore():
    """P303, P304."""
    for name in ("tor_17", "tor_18", "tor_offen_w", "tor_zu_w"):
        if name not in ort:
            continue
        if not gb[name]:
            print(name, "kein Tor, nicht gesetzt", plan["nicht_gesetzt"])
            continue
        n = gb[name][0]["nr"]
        g = gb[name][0]
        v = collections.defaultdict(list)
        for t, b in pl.stand(p, "DAT_BuildingsState", {"z": "buildings[].gateState", "z2": "buildings[].gateState2", "pl": "buildings[].pathLinkageRelated2"}):
            for k in ("z", "pl"):
                w = int(b[k][n])
                if not v[k] or v[k][-1][1] != w:
                    v[k].append((t - START, w))
            w = int(b["z2"][n])
            if not v["z2"] or (w > v["z2"][-1][1]) or (w == 0 and v["z2"][-1][1] != 0):
                v["z2"].append((t - START, w))
        print(name, "Tor", (g["x"], g["y"]), "gateState", v["z"][:6], "pathLinkage", v["pl"][:9], "gateState2 (Spruenge)", v["z2"][:6])
        f = reihe(wer[name], {"h": "units[].terrainOrClimbHeight"})
        for e in wer[name]:
            s = f[e["nr"]]
            print("   ", e["rolle"], "Spieler", e["spieler"], "von", (e["x"], e["y"]), "Mikro-Abstand zur Torecke am Anfang", (abs(e["x"] - g["x"]) * 8, abs(e["y"] - g["y"]) * 8), "Wechsel", len(s), "letzte", s[-2:], "hoechste Hoehe", max(x[4] for x in s if len(x) > 4))
            if e["rolle"] == "geher":
                linie = ort[name]["y"] + 5
                durch = next((x for x in s if x[2] > linie), None)
                print("        ueber die Mauerlinie y", linie, "(Takt, x, y, Zustand, Hoehe):", durch, "Tor x", g["x"], "bis", g["x"] + 4, "Mauer x", ort[name]["x"], "bis", ort[name]["x"] + 26, "kleinstes x", min(x[1] for x in s if len(x) > 2), "groesstes x", max(x[1] for x in s if len(x) > 2))


def trupp():
    """P325."""
    if "trupp_ring" not in ort:
        return
    liste = wer["trupp_ring"]
    tr = [e for e in liste if e["rolle"] == "trupp"]
    k = next(e for e in liste if e["rolle"] == "feind")
    stufen = {}
    letzter = None
    for t, u in pl.stand(p, "DAT_UnitsState", {**U, "px": "units[].plannedDestinationX", "py": "units[].plannedDestinationY", "l": "units[].health", "tm": "units[].targetingType"}):
        ist = tuple((int(u["px"][e["nr"]]), int(u["py"][e["nr"]])) for e in tr)
        if ist not in stufen:
            stufen[ist] = (t - START, tuple(int(u["z"][e["nr"]]) for e in tr), tuple(int(u["tm"][e["nr"]]) for e in tr), tuple((int(u["mx"][e["nr"]]) // 8, int(u["my"][e["nr"]]) // 8) for e in tr), int(u["l"][k["nr"]]), letzter)
        letzter = (t - START, tuple(int(u["z"][e["nr"]]) for e in tr))
    print("trupp_ring Einheiten", [(e["nr"], e["x"], e["y"]) for e in tr], "Feind", (k["nr"], k["x"], k["y"]), "Ziel im Ring", (ort["trupp_ring"]["x"] + 34, ort["trupp_ring"]["y"] + 4))
    for ist, (t, z, tm, wo, l, vor) in list(stufen.items())[:8]:
        print("   Takt", t, "Zielfelder", ist, "Zustand", z, "Anweisung", tm, "Orte", wo, "Leben Feind", l, "davor", vor)
    print("   Stufen", len(stufen))
    h, _ = karte_ende()
    o = ort["trupp_ring"]
    for j in range(o["hoehe"]):
        print("    y", o["y"] + j, " ".join(f"{int(h[FN[o['y'] + j] + o['x'] + i]):3d}" for i in range(28, o["breite"])))


def trupp_flaeche():
    """P325 mit erster Einheit ohne Flaeche."""
    name = next((n for n in ("trupp_ohne_flaeche", "trupp_eck") if n in ort), None)
    if name is None:
        return
    liste = wer[name]
    tr = [e for e in liste if e["rolle"] == "trupp"]
    k = next(e for e in liste if e["rolle"] == "feind")
    stufen = {}
    letzter = None
    for t, u in pl.stand(p, "DAT_UnitsState", {**U, "px": "units[].plannedDestinationX", "py": "units[].plannedDestinationY", "l": "units[].health", "tri": "units[].tribeID"}):
        ist = tuple((int(u["px"][e["nr"]]), int(u["py"][e["nr"]])) for e in tr)
        if ist not in stufen:
            stufen[ist] = (t - START, tuple(int(u["z"][e["nr"]]) for e in tr), tuple(int(u["tri"][e["nr"]]) for e in tr), tuple((int(u["mx"][e["nr"]]) // 8, int(u["my"][e["nr"]]) // 8) for e in tr), int(u["l"][k["nr"]]), letzter)
        letzter = (t - START, tuple(int(u["z"][e["nr"]]) for e in tr))
    print(name, "Einheiten", [(e["nr"], e["x"], e["y"]) for e in tr], "Feind", (k["nr"], k["x"], k["y"]), "Ziel", (ort[name]["x"] + 30, ort[name]["y"] + 3))
    for ist, (t, z, tri, wo, l, vor) in list(stufen.items())[:8]:
        print("   Takt", t, "Zielfelder", ist, "Zustand", z, "Trupps", tri, "Orte", wo, "Leben Feind", l, "davor", vor)


def hang():
    """P330."""
    if "bergab_auf" not in ort:
        return
    if not wer["bergab_auf"]:
        print("P330 kein Hang gefunden")
        return
    v = reihe(wer["bergab_auf"], {"c": "units[].calculatedMovementSpeed", "m": "units[].movementSpeed", "h": "units[].terrainOrClimbHeight"})
    s = list(v.values())[0]
    print("P330 bergab und bergauf (Takt, x, y, Zustand, berechnet, Grund, Hoehe), Wechsel", len(s))
    print("   ", s[:60])


if __name__ == "__main__":
    for f in (kopf, tuerme, tore, trupp, trupp_flaeche, hang):
        try:
            f()
        except Exception as e:
            import traceback
            print("FEHLER", f.__name__, repr(e))
            traceback.print_exc(limit=2)
