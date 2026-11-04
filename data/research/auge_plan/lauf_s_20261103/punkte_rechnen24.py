# -*- coding: utf-8 -*-
"""B-142: Auswertung sonder24_g: P126 Belagerungszelt, P238 Oelwurf, P111 Schmelze und Lager, P119 Mauerkosten, Stapel halten, Holztor.

  PYTHONPATH="src;data/research/auge_plan/lauf_s_20261103" python data/research/auge_plan/lauf_s_20261103/punkte_rechnen24.py > data/research/auge_plan/lauf_s_20261103/punkte_rechnung24.txt
"""
import collections

import punkte_lesen as pl

import sys
P = pl.neueste(sys.argv[1] if len(sys.argv) > 1 else "sonder24_g")
plan = pl.plan_von(P)
S = plan["von"]
B, U, G = "DAT_BuildingsState", "DAT_UnitsState", "DAT_GameState"
print("Plan", {k: plan.get(k) for k in ("von", "bis", "nicht_gesetzt", "kein_platz", "mauer_fehlt", "mauer_wiederholt")})
ort = {k["posten"]: k for k in plan["karte"]}
print("Orte", {k: (v["x"], v["y"]) for k, v in ort.items()})


def gebaeude_am_ort(n, b, h):
    k = ort[n]
    letzt = None
    for t, w in pl.stand(P, B, {"typ": "buildings[].buildingType", "x": "buildings[].x", "y": "buildings[].y"}):
        letzt = w
    return [(i, int(letzt["typ"][i]), int(letzt["x"][i]), int(letzt["y"][i])) for i in range(1, 400) if letzt["typ"][i] and k["x"] - 4 <= letzt["x"][i] < k["x"] + b + 4 and k["y"] - 4 <= letzt["y"][i] < k["y"] + h + 4]


def zelt(n):
    k = ort[n]
    ge = set()
    fo = {}
    letzt = {}
    for t, w in pl.stand(P, B, {"typ": "buildings[].buildingType", "pr": "buildings[].buildingProgress", "ma": "buildings[].currentEmployeeCount", "st": "buildings[].state", "x": "buildings[].x", "y": "buildings[].y"}):
        for i in (w["typ"] == 82).nonzero()[0]:
            i = int(i)
            if k["x"] - 4 <= w["x"][i] < k["x"] + 24 and k["y"] - 4 <= w["y"][i] < k["y"] + 14:
                ge.add(i)
        for i in ge:
            z = (int(w["typ"][i]), int(w["pr"][i]), int(w["ma"][i]), int(w["st"][i]))
            if letzt.get(i) != z:
                fo.setdefault(i, []).append((t - S,) + z)
                letzt[i] = z
    for i, l in fo.items():
        schritte = collections.Counter()
        for a, b in zip(l, l[1:]):
            if b[0] > a[0] and b[2] > a[2]:
                schritte[round((b[2] - a[2]) / (b[0] - a[0]), 2)] += 1
        print("  Gebaeude", i, "Wechsel", len(l), "Anfang (Takt, Art, Fortschritt, Mann, Zustand)", l[:6], "Ende", l[-4:], "Anstieg je Takt", schritte.most_common(4), "hoechster Fortschritt", max(x[2] for x in l))
    tuerme = {}
    for t, u in pl.stand(P, U, {"ty": "units[].unitType", "b": "units[].owner", "m": "units[].digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300", "x": "units[].x", "y": "units[].y"}):
        for i in (u["ty"] == 58).nonzero()[0]:
            i = int(i)
            k = ort[n]
            if k["x"] - 6 <= u["x"][i] < k["x"] + 26 and k["y"] - 6 <= u["y"][i] < k["y"] + 16:
                z = (int(u["m"][i]), int(u["x"][i]), int(u["y"][i]))
                if i not in tuerme:
                    tuerme[i] = [(t - S,) + z]
                elif tuerme[i][-1][1] != z[0]:
                    tuerme[i].append((t - S,) + z)
    print("  Belagerungstuerme (Einheit: Takt, Zaehlfeld, x, y):", {k: v[:4] for k, v in tuerme.items()})
    ing = [e for e in plan["einheiten"] if e.get("posten") == n]
    print("  Ingenieure am Ende:", [(e["nr"]) for e in ing])


def oel(n):
    leute = [e for e in plan["einheiten"] if e.get("posten") == n and e.get("typ") == 30]
    feind = [e for e in plan["einheiten"] if e.get("posten") == n and e.get("rolle") == "feind"]
    for e in leute:
        fo = []
        for t, u in pl.stand(P, U, {"z": "units[].state", "w": "units[].resourceToDeposit"}):
            x = (int(u["z"][e["nr"]]), int(u["w"][e["nr"]]))
            if not fo or fo[-1][1] != x:
                fo.append((t - S, x))
        print(n, "Ingenieur", e["nr"], "(Takt, (Zustand, Traglast))", fo[:24])
    for e in feind:
        fo = []
        for t, u in pl.stand(P, U, {"l": "units[].health", "z": "units[].state"}):
            x = (int(u["l"][e["nr"]]), int(u["z"][e["nr"]]))
            if not fo or fo[-1][1] != x:
                fo.append((t - S, x))
        print(n, "Feind", e["nr"], "(Takt, (Leben, Zustand))", fo[:12])
    ge = [g for g in plan["gebaeude"] if g.get("posten") == n and "nr" in g]
    for g in ge:
        fo = []
        for t, w in pl.stand(P, B, {"st": "buildings[].state", "p": "buildings[].resourcePitch"}):
            x = (int(w["st"][g["nr"]]), int(w["p"][g["nr"]]))
            if not fo or fo[-1][1] != x:
                fo.append((t - S, x))
        print(n, "Schmelze", g["nr"], "(Takt, (Zustand, Pech))", fo[:26])


def pech():
    fo = []
    for t, w in pl.stand(P, G, {"p": ("playerDataArray[].currentResources[]", 7 * 4)}):
        v = int(w["p"][1])
        if not fo or fo[-1][1] != v:
            fo.append((t - S, v))
    print("Pechbestand Spieler 1 (Takt, Wert):", fo[:24])


def mauer():
    fo = []
    for t, w in pl.stand(P, G, {"st": ("playerDataArray[].currentResources[]", 4 * 4), "te": ("playerDataArray[].partialStoneCounter", 0)}):
        x = (int(w["st"][1]), int(w["te"][1]))
        if not fo or fo[-1][1] != x:
            fo.append((t - S, x))
    print("Mauer: Stein und Rest Spieler 1 um die Befehle (Takt, (Stein, Rest))", [q for q in fo if 180 <= q[0] <= 560][:30])
    c = []
    for t, w in pl.stand(P, "DAT_TileMapState", {"k": "wallPlacementCost"}):
        v = int(w["k"])
        if not c or c[-1][1] != v:
            c.append((t - S, v))
    print("wallPlacementCost (Takt, Wert)", c[:16])


def stapel():
    wer = [e for e in plan["einheiten"] if e.get("posten") == "punkt_halten"]
    z = []
    for t, u in pl.stand(P, U, {"mx": "units[].microXPosition", "my": "units[].microYPosition"}):
        c = collections.Counter((int(u["mx"][e["nr"]]) // 8, int(u["my"][e["nr"]]) // 8) for e in wer)
        m = c.most_common(1)[0][1]
        if not z or z[-1][1] != m:
            z.append((t - S, m))
    print("Stapel halten (Takt, meiste auf einem Feld):", z[:30])


def tor():
    ge = [g for g in plan["gebaeude"] if g.get("posten") == "holztor"]
    print("Holztor geplant", ge)
    for g in ge:
        if "nr" not in g:
            continue
        fo = []
        for t, w in pl.stand(P, B, {"h": "buildings[].currentHealth", "m": "buildings[].maxHealth", "ty": "buildings[].buildingType"}):
            x = (int(w["h"][g["nr"]]), int(w["m"][g["nr"]]), int(w["ty"][g["nr"]]))
            if not fo or fo[-1][1] != x:
                fo.append((t - S, x))
        sp = collections.Counter(a[1][0] - b[1][0] for a, b in zip(fo, fo[1:]))
        print("  Holztor", g["nr"], "(Takt, (Leben, max, Art))", fo[:12], "Ende", fo[-2:], "Schaden je Wechsel", sp.most_common(5))


for f in ((lambda: zelt("zelt4"), lambda: zelt("zelt2")) if "sonder25" in P else (lambda: oel("oel_wurf"), lambda: oel("oel_lager"), pech, mauer, stapel, tor)):
    try:
        f()
    except Exception as e:
        print("FEHLER", repr(e)[:300])
