# -*- coding: utf-8 -*-
"""B-142: P093, P096 Farmstufe gegen die Felder, P122 Stein am Stapel, P238 Ingenieur mit Oel, P140 wann das Feld 0 steht.

  PYTHONPATH="src;data/research/auge_plan/lauf_s_20261103" python data/research/auge_plan/lauf_s_20261103/punkte_rechnen21.py > data/research/auge_plan/lauf_s_20261103/punkte_rechnung21.txt
"""
import collections
import glob
import os

import numpy as np

import punkte_lesen as pl

K = pl.karte
F = os.path.join(pl.L, "lauf_f_20261102_214240.auge")
B, TM = "DAT_BuildingsState", "DAT_TileMapState"


def kacheln(x0, y0, b, kachel_von):
    return [kachel_von(x0 + i, y0 + j) for j in range(b) for i in range(b)]


def tile_von():
    """Feldnummer aus x und y: wie im Spiel ueber die Zeilentabelle. Hier aus dem Speicher der Laufzeit nicht noetig: Aus der Aufzeichnung: tile(x, y) = Summe der Zeilenlaengen, Rautenform."""
    from selfaware.tools.experiments.auge_lauf_f import Speicher  # nur wegen der Form, nichts wird gelesen
    return Speicher


def farm(p, nr, b, name, stufen, grenze, soll, bis=60000):
    """Stand der Farm (Wert) gegen die Zahl der Felder auf der Stufe, in den Rahmen der Karte. Die Felder der Farm: Gehoeren laut BuildingLayer zu ihr."""
    st = {}
    for t, w in pl.stand(p, B, {"s": "buildings[].wheatGrowStateRelated", "x": "buildings[].x", "y": "buildings[].y"}):
        st[t] = int(w["s"][nr])
        if t > bis:
            break
    zeiten = sorted(st)
    tab = collections.Counter()
    beispiel = {}
    n = 0
    for t, w in pl.stand(p, TM, {"bau": "BuildingLayer[]", "sch": "DamageLayer[]"}):
        if t > bis:
            break
        n += 1
        felder = (np.asarray(w["bau"]) == nr).nonzero()[0]
        s = np.asarray(w["sch"])[felder].astype(np.uint8)  # Stufe als Zahl ohne Vorzeichen, sonst wird 121 nie falsch, aber groessere Stufen schon
        z = int(((s >= stufen[0]) & (s <= stufen[1])).sum())
        i = np.searchsorted(zeiten, t, side="right") - 1
        if i >= 0:
            wert = st[zeiten[i]]
            tab[(wert, z >= grenze)] += 1
            beispiel.setdefault((wert, z >= grenze), (t, z, len(felder)))
    print(name, nr, "Kartenrahmen", n, f"(Stand, mindestens {grenze} Felder auf Stufe {stufen}): Rahmen", sorted(tab.items()))
    print("   Beispiele (Takt, Felder auf Stufe, Felder der Farm):", sorted(beispiel.items())[:8], "erwartet: Stand", soll)


def stapel(p, bruch):
    """P122: Stein am Stapel des Steinbruchs."""
    letzt = None
    for t, w in pl.stand(p, B, {"typ": "buildings[].buildingType"}):
        letzt = w["typ"].copy()
    from selfaware.game.ucp.bauen import NACH_TYP
    print("Arten mit QUARRY:", {t: v["laufzeitName"] for t, v in NACH_TYP.items() if "QUARRY" in str(v.get("laufzeitName"))})
    stap = [int(i) for i in (letzt == 21).nonzero()[0]]
    print("Stapel (Art 21)", stap)
    fo = {i: [] for i in stap}
    wechsel = []
    alt = None
    for t, w in pl.stand(p, B, {"st": "buildings[].resourceStone", "f": "buildings[].killingPitField", "s": "buildings[].state"}):
        for i in stap:
            v = int(w["st"][i])
            if not fo[i] or fo[i][-1][1] != v:
                fo[i].append((t, v))
        f = (int(w["f"][bruch]) >> 16) & 0xffff
        if alt == 1 and f == 0:
            wechsel.append(t)
        alt = f
    for i, l in fo.items():
        sp = collections.Counter(b[1] - a[1] for a, b in zip(l, l[1:]))
        print("  Stapel", i, "Wechsel", len(l), "Spruenge", sp.most_common(6), "hoechster Stand", max(x[1] for x in l), "erste", l[:10])
        # Fuer jeden Wechsel 1 auf 0: Aenderung am Stapel in den 5 Takten danach
        c = collections.Counter()
        for t0 in wechsel:
            vor = [v for t, v in l if t <= t0]
            nach = [v for t, v in l if t <= t0 + 5]
            if vor and nach:
                c[nach[-1] - vor[-1]] += 1
        print("    Bei Wechsel 1 auf 0: Aenderung am Stapel bis 5 Takte danach:", c.most_common(5))


def ingenieur(szene):
    """P238: Zustaende des Ingenieurs mit Oel und der Pechbestand."""
    p = pl.neueste(szene)
    if not p:
        print(szene, "fehlt")
        return
    plan = pl.plan_von(p)
    S = plan["von"]
    print(szene, os.path.basename(p), "Posten", [k["posten"] for k in plan["karte"]][:14])
    leute = [e for e in plan["einheiten"] if e.get("posten") == "oel" and e.get("typ") == 30]
    for e in leute[:3]:
        fo = []
        for t, u in pl.stand(p, "DAT_UnitsState", {"z": "units[].state", "w": "units[].resourceToDeposit", "ty": "units[].unitType"}):
            x = (int(u["z"][e["nr"]]), int(u["w"][e["nr"]]), int(u["ty"][e["nr"]]))
            if not fo or fo[-1][1] != x:
                fo.append((t - S, x))
        print("  Ingenieur", e["nr"], "(Takt, (Zustand, Traglast, Art))", fo[:22])
    pech = []
    for t, w in pl.stand(p, "DAT_GameState", {"p": ("playerDataArray[].currentResources[]", 8 * 4)}):
        v = int(w["p"][1])
        if not pech or pech[-1][1] != v:
            pech.append((t - S, v))
    print("  Pech im Lager, Spieler 1 (Takt, Bestand):", pech[:16])


def essen_zeiten(p):
    """P140: Bei welchen Takten steht das Feld auf 0, obwohl Essen da ist?"""
    felder = {"z": ("playerDataArray[].foodTypesInStock", 0)}
    for i, o in enumerate((-20, -16, -12, -8)):
        felder[f"e{i}"] = ("playerDataArray[].foodTypesInStock", o)
    fo = []
    for t, w in pl.stand(p, "DAT_GameState", felder):
        for n in (1,):
            g = sum(1 for i in range(4) if int(w[f"e{i}"][n]) > 0)
            z = int(w["z"][n])
            x = (z, g)
            if not fo or fo[-1][1] != x:
                fo.append((t, x))
    print("P140 Spieler 1, Wechsel (Takt, (Feld, Sorten)):", fo[:40])
    fehl = [(a[0], b[0] - a[0]) for a, b in zip(fo, fo[1:]) if a[1][0] == 0 and a[1][1] > 0]
    print("   Dauer der Faelle mit Feld 0 trotz Essen (Takt, Dauer):", fehl[:20], "haeufig:", collections.Counter(d for _, d in fehl).most_common(6))


if __name__ == "__main__":
    farm(F, 67, 9, "P093 Weizen", (121, 121), 4, 8)
    farm(F, 68, 9, "P096 Hopfen", (14, 27), 6, 5)
    stapel(F, 55)
    ingenieur("sonder_g")
    essen_zeiten(sorted(glob.glob(os.path.join(pl.L, "lauf_k_*_234952.auge")))[-1])
