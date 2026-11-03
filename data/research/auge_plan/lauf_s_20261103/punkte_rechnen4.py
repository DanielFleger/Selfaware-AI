# -*- coding: utf-8 -*-
"""B-142 Lauf S, Einzelpunkte 4: Tempo, Besatzung, Schild, Belagerungsturm, Werte um die Burg, Feuerstufen, Hoehe im Tunnel, Salven, Schaden je Art. Die Urteile stehen in Punkte_Lauf_S.md.

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/punkte_rechnen4.py > data/research/auge_plan/lauf_s_20261103/punkte_rechnung4.txt
"""
import collections
import json
import os

import numpy as np

import punkte_lesen as pl
from selfaware.tools.analysis import auge_regeln as ar

U = {"da": "units[].logicalState", "typ": "units[].unitType", "b": "units[].owner", "mx": "units[].microXPosition", "my": "units[].microYPosition", "z": ("units[].logicalState", ar.ZUSTAND_ABSTAND)}
MANN = "units[].digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300"


def p330():
    """Tempo im Laufen: Nur Rahmen, in denen sich der Ort aendert."""
    for s in ("laufen", "punkt"):
        p = pl.neueste(s)
        plan = pl.plan_von(p)
        wer = {e["nr"]: e for e in plan["einheiten"] if "nr" in e}
        z = collections.defaultdict(collections.Counter)
        alt = {}
        for t, u in pl.stand(p, "DAT_UnitsState", {**U, "c": "units[].calculatedMovementSpeed", "m": "units[].movementSpeed"}):
            for n, e in wer.items():
                o = (int(u["mx"][n]), int(u["my"][n]))
                if alt.get(n) not in (None, o) and u["typ"][n] == e["typ"]:
                    z[e["typ"]][(int(u["c"][n]), int(u["m"][n]))] += 1
                alt[n] = o
        print("P330", s, "je Art (berechnet, movementSpeed): Rahmen in Bewegung")
        for ty, c in sorted(z.items())[:22]:
            print("   ", ty, c.most_common(3))


def p333_p324():
    p = pl.neueste("sonder6_g")
    v = collections.defaultdict(list)
    lb = collections.Counter()
    for t, g in pl.stand(p, "DAT_GameState", {"a": "playerDataArray[].totalEnemyTroopValue", "r": "playerDataArray[].totalEnemyRangedTroopValue", "m": "playerDataArray[].totalTeamTroopValue", "lb": "gameTicksLoadBalancer"}):
        for sp in (1, 2):
            w = (int(g["a"][sp]), int(g["r"][sp]), int(g["m"][sp]))
            if not v[sp] or v[sp][-1][2:] != w:
                if v[sp]:
                    lb[g["lb"]] += 1
                v[sp].append((t, g["lb"], *w))
    print("P333 (Takt, Lastverteiler, Feind, Feind fern, Team):", {sp: w[:7] for sp, w in v.items()})
    print("   Lastverteiler bei Wechsel:", sorted(lb.items()))
    nah = []
    for t, x in pl.stand(p, "DAT_TroopValueState", {"n": "attackInfo.playerTotalTroopValueOfTroopsNearKeep[]"}):
        w = (int(x["n"][1]), int(x["n"][2]))
        if not nah or nah[-1][1:] != w:
            nah.append((t, *w))
    print("P324 (Takt, Spieler 1, Spieler 2):", nah[:10])


def p337_p334():
    p = pl.neueste("besatzung")
    plan = pl.plan_von(p)
    g = [e for e in plan["einheiten"] if e["rolle"] == "geraet" and "nr" in e]
    ing = [e for e in plan["einheiten"] if e["rolle"] == "ingenieur" and "nr" in e]
    print("P337 Felder eines Ingenieurs:", {k: ing[0].get(k) for k in ing[0] if k not in ("voll", "uid", "spieler")})
    verlauf = {e["nr"]: [] for e in g}
    start = None
    ende = {}
    for t, u in pl.stand(p, "DAT_UnitsState", {**U, "man": MANN}):
        start = t if start is None else start
        for e in g:
            w = int(u["man"][e["nr"]])
            if not verlauf[e["nr"]] or verlauf[e["nr"]][-1][1] != w:
                verlauf[e["nr"]].append((t - start, w))
        ende = {e["nr"]: (int(u["mx"][e["nr"]]) // 8, int(u["my"][e["nr"]]) // 8, int(u["z"][e["nr"]])) for e in ing}
        ende_g = {e["nr"]: (int(u["mx"][e["nr"]]) // 8, int(u["my"][e["nr"]]) // 8) for e in g}
    for e in g[:10]:
        leute = [i for i in ing if i.get("fall") == e.get("fall")]
        print("   Art", e["typ"], "soll", e.get("soll"), "mann", e.get("mann"), "Zaehler", verlauf[e["nr"]][:5], "Geraet bei", ende_g[e["nr"]], "Ingenieure (x, y, Zustand):", [ende[i["nr"]] for i in leute][:4])


def p341_p344():
    for s, posten in (("sonder2", "schild"), ("sonder3", "turmgeraet")):
        p = pl.neueste(s)
        plan = pl.plan_von(p)
        wer = [e for e in plan["einheiten"] if e.get("posten") == posten and e["typ"] in (30, 58, 60) and "nr" in e]
        v = {e["nr"]: [] for e in wer}
        start = None
        for t, u in pl.stand(p, "DAT_UnitsState", {**U, "man": MANN}):
            start = t if start is None else start
            for e in wer:
                n = e["nr"]
                w = (int(u["z"][n]), int(u["man"][n]) if e["typ"] != 30 else 0) if u["typ"][n] == e["typ"] else ("weg", 0)
                if not v[n] or v[n][-1][1:] != w:
                    v[n].append((t - start, *w))
        print("P341/P344", s, posten)
        for e in wer[:6]:
            print("   ", e["rolle"], "Art", e["typ"], "Nr", e["nr"], "(Takt, Zustand, Zaehler)", v[e["nr"]][:12])


def p298():
    """Feuer: Rahmen je Phase der Huette, und neue Feuer gegen die Nachbarn im Rahmen davor."""
    p = pl.neueste("sonder1")
    plan = pl.plan_von(p)
    huetten = [g for g in plan["gebaeude"] if g.get("posten") == "feuer" and "nr" in g]
    dauer = {}
    for t, b in pl.stand(p, "DAT_BuildingsState", {"d": "buildings[].fireDuration"}):
        dauer[t] = {g["nr"]: int(b["d"][g["nr"]]) for g in huetten}
    anfang = {g["nr"]: next((t for t, d in sorted(dauer.items()) if d[g["nr"]] > 0), None) for g in huetten}
    ende = {g["nr"]: max(t for t, d in dauer.items() if d[g["nr"]] > 0) for g in huetten}
    phase = collections.Counter()
    neu, alt = collections.Counter(), {}
    for t, e in pl.stand(p, "DAT_EntityState", {"art": "entityArray[].entityType", "da": "entityArray[].logicalState", "uid": "entityArray[].uid", "tr": "entityArray[].someTracker", "st": "entityArray[].fireParameter_0xb6", "z": "entityArray[].someCounter_OR_hitGround", "mx": "entityArray[].microX", "my": "entityArray[].microY"}):
        ist = {}
        for i in np.nonzero((e["art"] == 9) & (e["da"] != 0))[0]:
            x, y = int(e["mx"][i]) // 8, int(e["my"][i]) // 8
            k = (int(i), int(e["uid"][i]))
            ist[k] = (x, y, int(e["st"][i]))
            h = next((g for g in huetten if g["x"] <= x < g["x"] + g["groesse"] and g["y"] <= y < g["y"] + g["groesse"]), None)
            if h is not None and t in dauer:
                n = h["nr"]
                pz = "vorher" if t < anfang[n] else ("brennt" if t <= ende[n] else "danach")
                phase[(pz, int(e["tr"][i]) if e["tr"][i] >= 0 else -1, "Zaehler 0" if e["z"][i] == 0 else "Zaehler>0")] += 1
            if alt and k not in alt:
                nachbar = {v[2] for v in alt.values() if max(abs(v[0] - x), abs(v[1] - y)) <= 2}
                neu["Nachbar hat Stufe plus 1" if int(e["st"][i]) + 1 in nachbar else ("kein Nachbar" if not nachbar else "Nachbar anders")] += 1
        alt = ist
    print("P298 Huette brennt von bis:", anfang, ende)
    for k, n in sorted(phase.items(), key=str):
        print("   ", k, n)
    print("P298 neue Feuer:", dict(neu))


def p339_hunde():
    """huntedBy: Befehl (reichweite) gegen Hunde (tryAttackUnitID im Hundecode)."""
    p = pl.neueste("sonder3_g")
    plan = pl.plan_von(p)
    op = [e["nr"] for e in plan["einheiten"] if e.get("posten") == "hunde" and e["rolle"] == "opfer"]
    v = {n: [] for n in op}
    start = None
    for t, u in pl.stand(p, "DAT_UnitsState", {"j": "units[].huntedBy", "typ": "units[].unitType"}):
        start = t if start is None else start
        for n in op:
            w = int(u["j"][n]) if u["typ"][n] == 24 else None
            if not v[n] or v[n][-1][1] != w:
                v[n].append((t - start, w))
    print("P339 huntedBy der Opfer der Hunde:", {n: v[n][:5] for n in op[:3]})


def p349_hoehe():
    import json as _j
    basis = _j.load(open(os.path.join(pl.HIER, "feldnummern.json"), encoding="utf-8"))
    p = pl.neueste("sonder6_g")
    zeile, x0, x1 = 282, 195, 207
    v = []
    start = None
    for t, m in pl.stand(p, "DAT_TileMapState", {"h": "HeightLayer[]"}, rein=False):
        start = t if start is None else start
        w = [int(m["h"][basis[zeile] + x]) for x in range(x0, x1 + 1)]
        if not v or v[-1][1] != w:
            v.append((t - start, w))
    print("P349 Hoehe Zeile 282, x 195 bis 207, je Wechsel:", len(v))
    for a in v[::5]:
        print("   ", a)
    print("   ", v[-1])


def p351_je_spieler():
    p = pl.neueste("sonder6_g")
    um = collections.Counter()
    alt = {}
    probe = []
    for t, u in pl.stand(p, "DAT_UnitsState", {**U, "d": "units[].closestEnemyMicroDistance"}):
        m = (u["typ"] == 22) & (u["da"] != 0)
        m[0] = False
        for i in np.nonzero(m)[0]:
            i = int(i)
            z, d = int(u["z"][i]), int(u["d"][i])
            if alt.get(i) not in (11, None) and z == 11:
                um[(int(u["b"][i]), "ueber 400" if d > 400 else "bis 400", alt[i])] += 1
                if len(probe) < 4 and d <= 400:
                    probe.append((t, i, d, alt[i]))
            alt[i] = z
    print("P351 Wechsel zum Hinsetzen je (Spieler, Abstand, Zustand davor):", um.most_common(8), "Beispiele", probe)


def p361_p334():
    p = pl.neueste("besatzung")
    plan = pl.plan_von(p)
    g = ar.geschosse_lesen(p, pl.karte)
    wer = {e["nr"] for e in plan["einheiten"] if e["typ"] == 41 and "nr" in e}
    je = collections.defaultdict(collections.Counter)
    for x in g:
        if x["schuetze"] in wer:
            je[x["schuetze"]][x["von"]] += 1
    print("P361 Mangonel: Geschosse je Salve:", {n: collections.Counter(c.values()).most_common(4) for n, c in je.items()}, "Salven", {n: len(c) for n, c in je.items()})


def p353_bis_p368():
    z = json.load(open(os.path.join(pl.HIER, "gebaeude_nah.regeln.json"), encoding="utf-8"))["zeilen"]
    t = collections.defaultdict(dict)
    for x in z:
        if x["verluste"]:
            t[x["wer"]][x["ziel"].replace("BT_", "")] = (sorted(x["verluste"], key=lambda a: -x["verluste"][a])[0], sorted(x["takte_zwischen"])[0] if x["takte_zwischen"] else None)
    print("P353 bis P368 Verlust je Schlag und Takte zwischen den Schlaegen, je Art:")
    for w, d in sorted(t.items()):
        print("   ", w, d)


def p306_p370():
    for s in ("nahkampf_g", "schlacht_20"):
        p = pl.neueste(s)
        try:
            adr = pl.karte.adresse("DAT_GameState", "finalKillMatrix[]")
        except Exception:
            adr = None
        print("P306", s, "Adresse", adr)
        if adr:
            erste, letzte = None, None
            for t, g in pl.stand(p, "DAT_GameState", {"m": "finalKillMatrix[]"}):
                erste = g["m"].copy() if erste is None else erste
                letzte = g["m"].copy()
            print("   geaendert:", int((erste != letzte).sum()), "Werte", [(int(i), int(erste[i]), int(letzte[i])) for i in np.nonzero(erste != letzte)[0]][:8])
    p = pl.neueste("schlacht_20")
    plan = pl.plan_von(p)
    print("P370 Arten im Plan schlacht_20:", collections.Counter(e["typ"] for e in plan["einheiten"]).most_common(5))


if __name__ == "__main__":
    for f in (p330, p333_p324, p337_p334, p341_p344, p298, p339_hunde, p349_hoehe, p351_je_spieler, p361_p334, p353_bis_p368, p306_p370):
        try:
            f()
        except Exception as e:
            import traceback
            print("FEHLER", f.__name__, repr(e))
            traceback.print_exc(limit=2)
