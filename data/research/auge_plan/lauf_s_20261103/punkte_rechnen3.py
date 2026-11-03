# -*- coding: utf-8 -*-
"""B-142 Lauf S, Einzelpunkte 3: Trupps, Haltung, Tempo, Schuetzen, Werte um die Burg, Todeskarte, Tore im Einzelnen. Die Urteile stehen in Punkte_Lauf_S.md.

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/punkte_rechnen3.py > data/research/auge_plan/lauf_s_20261103/punkte_rechnung3.txt
"""
import collections
import json
import os

import numpy as np

import punkte_lesen as pl
from selfaware.tools.analysis import auge_regeln as ar

U = {"da": "units[].logicalState", "typ": "units[].unitType", "b": "units[].owner", "mx": "units[].microXPosition", "my": "units[].microYPosition", "z": ("units[].logicalState", ar.ZUSTAND_ABSTAND)}


def rollen(plan):
    return collections.Counter(e["rolle"] for e in plan["einheiten"])


def p318_p327():
    """Anteil im Kampf je Trupp gegen die Einheiten, die wirklich schlagen."""
    for s in ("punkt", "schlacht_20"):
        p = pl.neueste(s)
        hoch = 0
        stufen = collections.Counter()
        tr = {}
        for t, x in pl.stand(p, "DAT_TribesState", {"pr": "tribes[].percentageAttackingUnk"}):
            tr[t] = x["pr"].copy()
            hoch = max(hoch, int(x["pr"].max()))
        passt = collections.Counter()
        for t, u in pl.stand(p, "DAT_UnitsState", {**U, "tri": "units[].tribeID", "sch": "units[].attackedUnitID"}):
            if t not in tr:
                continue
            da = (u["da"] != 0) & (u["tri"] > 0)
            da[0] = False
            for tid in np.unique(u["tri"][da]):
                m = da & (u["tri"] == tid)
                n, k = int(m.sum()), int((m & (u["sch"] != 0)).sum())
                if k:
                    pr = int(tr[t][tid])
                    passt["ueber 10" if pr > 10 else ("1 bis 10" if pr > 0 else "0")] += 1
                    stufen[min(100, round(pr / 10) * 10)] += 1
        print("P318/P327", s, "hoechster Anteil", hoch, "Trupps mit Schlaeger je Rahmen:", dict(passt), "Anteil gerundet:", sorted(stufen.items()))


def p339_p346():
    p = pl.neueste("reichweite")
    plan = pl.plan_von(p)
    print("P339/P346 reichweite Rollen", rollen(plan), "Beispiel", {k: v for k, v in plan["einheiten"][0].items() if k in ("rolle", "typ", "paar", "abstand", "fall", "ziel")})
    im_plan = {e["nr"]: e for e in plan["einheiten"] if "nr" in e}
    erster = {}
    gejagt = collections.Counter()
    start = None
    for t, u in pl.stand(p, "DAT_UnitsState", {**U, "sch": "units[].attackedUnitID", "jagd": "units[].huntedBy"}):
        start = t if start is None else start
        for n, e in im_plan.items():
            ziel = int(u["sch"][n])
            if ziel and n not in erster and ziel in im_plan:
                d = max(abs(int(u["mx"][n]) - int(u["mx"][ziel])), abs(int(u["my"][n]) - int(u["my"][ziel]))) / 8
                erster[n] = (e["typ"], t - start, round(d, 1))
            gejagt[int(u["jagd"][n])] += 1 if e["rolle"] != "laeufer" else 0
    print("   erster Schlag (Art, Takt, Abstand in Feldern):", sorted(erster.values())[:24])
    print("   Abstaende:", collections.Counter(round(v[2]) for v in erster.values()))
    print("   huntedBy der Ziele, Rahmen je Wert:", sorted(gejagt.items()))
    werte = {}
    for t, u in pl.stand(p, "DAT_UnitsState", {"jagd": "units[].huntedBy"}):
        for n, e in im_plan.items():
            if e["rolle"] != "laeufer":
                w = int(u["jagd"][n])
                if n not in werte or werte[n][-1][1] != w:
                    werte.setdefault(n, []).append((t - start, w))
    print("   huntedBy-Verlauf von 4 Zielen:", list(werte.values())[:4])


def p329_p347():
    p = pl.neueste("haltung")
    plan = pl.plan_von(p)
    wachen = [e for e in plan["einheiten"] if e["rolle"] == "wache" and "nr" in e]
    start = None
    v = {e["nr"]: None for e in wachen}
    tribut = {}
    for t, u in pl.stand(p, "DAT_UnitsState", {**U, "ziel": "units[].movementType_OR_targetUnitID", "look": "units[].lookForEnemy", "tri": "units[].tribeID"}):
        start = t if start is None else start
        for e in wachen:
            n = e["nr"]
            tribut[n] = int(u["tri"][n])
            if v[n] is None and u["ziel"][n] != 0:
                v[n] = (t - start, int(u["ziel"][n]), int(u["look"][n]))
    print("P347 je Wache (Art, Haltung, Abstand, Takt, Ziel, lookForEnemy):")
    for e in wachen[:21]:
        print("   ", e["typ"], e["haltung"], e["abstand"], v[e["nr"]])
    agg = [e for e in wachen if e["wert"] == 2]
    tr = tribut[agg[0]["nr"]]
    folge = []
    for t, x in pl.stand(p, "DAT_TribesState", {"c": "tribes[].unknownAttackRelatedUpdateCounter", "f": "tribes[].field93_0x22a"}):
        folge.append((t - start, int(x["c"][tr]), int(x["f"][tr])))
    sprung = [(a, b) for a, b in zip(folge, folge[1:]) if b[2] == 0 and a[2] > 0]
    steig = [(b[1] - a[1]) / (b[0] - a[0]) for a, b in zip(folge, folge[1:]) if b[0] > a[0] and b[1] > a[1]]
    print("P329 Trupp", tr, "Rahmen", len(folge), "Zaehler +je Takt (Median)", round(float(np.median(steig)), 2) if steig else None, "hoechster Zaehler", max(x[1] for x in folge), "field93 hoechstens", max(x[2] for x in folge), "Spruenge auf 0:", len(sprung), sprung[:2], "Anfang", folge[:3], "ab 51:", [x for x in folge if x[1] >= 51][:3])


def p330():
    for s in ("laufen", "laufen_trupp"):
        p = pl.neueste(s)
        plan = pl.plan_von(p)
        wer = {e["nr"]: e for e in plan["einheiten"] if "nr" in e}
        z = collections.defaultdict(collections.Counter)
        for t, u in pl.stand(p, "DAT_UnitsState", {**U, "c": "units[].calculatedMovementSpeed", "m": "units[].movementSpeed"}):
            for n, e in wer.items():
                if u["z"][n] == 101:
                    z[e["typ"]][(int(u["c"][n]), int(u["m"][n]))] += 1
        print("P330", s, "je Art (berechnet, movementSpeed): Rahmen im Laufen")
        for ty, c in sorted(z.items())[:24]:
            print("   ", ty, c.most_common(4))


def p333_p324():
    p = pl.neueste("sonder6_g")
    v = collections.defaultdict(list)
    lb = collections.Counter()
    kopf = None
    for t, g in pl.stand(p, "DAT_GameState", {"a": "playerDataArray[].totalEnemyTroopValue", "r": "playerDataArray[].totalEnemyRangedTroopValue", "m": "playerDataArray[].totalTeamTroopValue", "lb": "mapAndTime.gameTicksLoadBalancer"}):
        for sp in (1, 2):
            w = (int(g["a"][sp]), int(g["r"][sp]), int(g["m"][sp]))
            if not v[sp] or v[sp][-1][2:] != w:
                v[sp].append((t, g["lb"], *w))
                if len(v[sp]) > 1:
                    lb[g["lb"]] += 1
    print("P333 Wechsel je Spieler (Takt, LoadBalancer, Feind, Feind fern, Team):", {sp: w[:8] for sp, w in v.items()})
    print("   LoadBalancer bei Wechsel:", sorted(lb.items()))
    try:
        nah = []
        for t, x in pl.stand(p, "DAT_TroopValueState", {"n": "attackInfo.playerTotalTroopValueOfTroopsNearKeep[]"}):
            w = (int(x["n"][1]), int(x["n"][2]))
            if not nah or nah[-1][1:] != w:
                nah.append((t, *w))
        print("P324 Wert nahe der Burg Spieler 1 und 2 (Takt, P1, P2):", nah[:12])
    except Exception as e:
        print("P324 FEHLT", repr(e)[:100])


def p351():
    for s in ("sonder6_g", "haltung"):
        p = pl.neueste(s)
        um = collections.Counter()
        alt = {}
        sitz = collections.Counter()
        for t, u in pl.stand(p, "DAT_UnitsState", {**U, "d": "units[].closestEnemyMicroDistance"}):
            m = (u["typ"] == 22) & (u["da"] != 0)
            m[0] = False
            for i in np.nonzero(m)[0]:
                i = int(i)
                z = int(u["z"][i])
                d = int(u["d"][i])
                if z == 11:
                    sitz["sitzt, Abstand ueber 400" if d > 400 else "sitzt, Abstand bis 400"] += 1
                elif z in (0, 1, 2, 8):
                    sitz["steht, Abstand ueber 400" if d > 400 else "steht, Abstand bis 400"] += 1
                if alt.get(i) not in (11, None) and z == 11:
                    um["ueber 400" if d > 400 else "bis 400"] += 1
                alt[i] = z
        print("P351", s, "Bogenschuetzen je Rahmen:", dict(sitz), "Wechsel zum Hinsetzen:", dict(um))


def p365():
    p = pl.neueste("schlacht_araber")
    v = []
    leben = {}
    for t, u in pl.stand(p, "DAT_UnitsState", {**U}):
        m = (u["da"] != 0) & (u["typ"] == 70)
        m[0] = False
        leben[t] = (int((m & (u["b"] == 1)).sum()), int((m & (u["b"] == 2)).sum()))
    for t, g in pl.stand(p, "DAT_GameState", {"n": "playerDataArray[].countArabianArcher"}):
        if t in leben:
            v.append((t, int(g["n"][1]), int(g["n"][2]), *leben[t]))
    plan = pl.plan_von(p)
    print("P365 Arten im Plan:", collections.Counter(e["typ"] for e in plan["einheiten"]).most_common(8))
    print("   (Takt, Feld P1, Feld P2, lebend P1, lebend P2):", v[:3], v[len(v) // 2:len(v) // 2 + 2], v[-2:], "gleich:", sum(1 for x in v if x[1] == x[3] and x[2] == x[4]), "von", len(v))


def p371():
    for s in ("schlacht_schuetzen", "punkt", "laufziel", "reichweite"):
        p = pl.neueste(s)
        plan = pl.plan_von(p)
        wer = [e for e in plan["einheiten"] if e["typ"] == 74 and "nr" in e]
        if not wer:
            continue
        n = wer[0]["nr"]
        v = []
        start = None
        for t, u in pl.stand(p, "DAT_UnitsState", {**U}):
            start = t if start is None else start
            z = int(u["z"][n])
            if not v or v[-1][1] != z:
                v.append((t - start, z))
        print("P371", s, "A_HARCHER", len(wer), "Rolle", wer[0]["rolle"], "Zustaende", v[:9])


def p314_p301():
    for s, posten in (("sonder5_g", "pech"), ("sonder1", "pech"), ("sonder1", "feuer")):
        p = pl.neueste(s)
        plan = pl.plan_von(p)
        wer = [e for e in plan["einheiten"] if e.get("posten") == posten and "nr" in e]
        v = {e["nr"]: [] for e in wer}
        start = None
        for t, u in pl.stand(p, "DAT_UnitsState", {"c": "units[].counter", "typ": "units[].unitType", "le": "units[].health"}):
            start = t if start is None else start
            for e in wer:
                w = int(u["c"][e["nr"]])
                if u["typ"][e["nr"]] == e["typ"] and (not v[e["nr"]] or v[e["nr"]][-1][1] != w):
                    v[e["nr"]].append((t - start, w))
        print("P314", s, posten, {e["rolle"]: v[e["nr"]][:5] for e in wer})
    p = pl.neueste("sonder1")
    g = ar.geschosse_lesen(p, pl.karte)
    plan = pl.plan_von(p)
    k = next(z for z in plan["karte"] if z["posten"] == "feuer")
    feu = sorted(x["von"] - plan["von"] for x in g if x["art"] in ("feuer", "feuer_frei") and k["x"] - 10 <= x["start"][0] // 8 < k["x"] + k["breite"] + 10 and k["y"] - 10 <= x["start"][1] // 8 < k["y"] + k["hoehe"] + 10)
    print("P301 erster Feuerstrahl im Posten feuer bei Takt:", feu[:3], "Anzahl", len(feu), "vor Takt 360:", sum(1 for x in feu if x < 360))


def p316():
    """Todeskarte: Mensch gegen Editor."""
    for s in ("nahkampf_g", "nahkampf", "beschuss_g", "beschuss"):
        p = pl.neueste(s)
        erste, letzte = None, None
        for t, m in pl.stand(p, "DAT_TileMapState", {"h": "unitDeathHeatMap[]"}, rein=False):
            if erste is None:
                erste = m["h"].copy()
            letzte = (t, m["h"].copy())
        d = letzte[1].astype(int) - erste.astype(int)
        print("P316", s, "Felder geaendert", int((d != 0).sum()), "hoch", int((d > 0).sum()), "runter", int((d < 0).sum()), "groesste Aenderung", int(d.max()), "Werte", collections.Counter(d[d != 0].tolist()).most_common(5))


def p326_p325():
    """Abstand der Zielfelder innerhalb eines Trupps gleich nach dem Befehl."""
    for s in ("sonder7_g", "besatzung", "punkt"):
        p = pl.neueste(s)
        plan = pl.plan_von(p)
        nr = {e["nr"]: e for e in plan["einheiten"] if "nr" in e}
        gesehen = {}
        for t, u in pl.stand(p, "DAT_UnitsState", {**U, "px": "units[].plannedDestinationX", "py": "units[].plannedDestinationY", "tri": "units[].tribeID"}):
            je = collections.defaultdict(list)
            for n, e in nr.items():
                if u["typ"][n] == e["typ"] and u["tri"][n] > 0 and u["px"][n] > 0:
                    je[int(u["tri"][n])].append((e["typ"], int(u["px"][n]), int(u["py"][n])))
            for tr, w in je.items():
                if len(w) >= 2 and tr not in gesehen:
                    ds = [max(abs(a[1] - b[1]), abs(a[2] - b[2])) for i, a in enumerate(w) for b in w[i + 1:]]
                    gesehen[tr] = (w[0][0], len(w), min(ds), max(ds))
        print("P326", s, "Trupps mit mindestens 2 (Art, Zahl, kleinster und groesster Abstand):", list(gesehen.values())[:10])


def p304_nah():
    """Tor: Abstand des naechsten Feindes beim Wechsel, Timer im Wortlaut."""
    from selfaware.game.ucp.bauen import NACH_TYP
    tore = {t for t, v in NACH_TYP.items() if "GATE" in v["laufzeitName"]}
    for s in ("gebaeude_nah", "belagerung"):
        p = pl.neueste(s)
        fuer = {}
        for t, b in pl.stand(p, "DAT_BuildingsState", {"typ": "buildings[].buildingType", "da": "buildings[].logicalState", "pl": "buildings[].pathLinkageRelated2", "z": "buildings[].gateState", "z2": "buildings[].gateState2", "ti": "buildings[].gateCloseOpenTimer", "x": "buildings[].x", "y": "buildings[].y", "o": "buildings[].owner"}):
            for i in np.nonzero(np.isin(b["typ"], list(tore)) & (b["da"] != 0))[0]:
                k = int(i)
                w = fuer.setdefault(k, {"o": int(b["o"][i]), "x": int(b["x"][i]), "y": int(b["y"][i]), "um": None, "z2": collections.Counter(), "ti": collections.Counter(), "z": collections.Counter(), "alt": int(b["pl"][i])})
                w["z2"][int(b["z2"][i])] += 1
                w["ti"][int(b["ti"][i])] += 1
                w["z"][int(b["z"][i])] += 1
                if int(b["pl"][i]) == 1 and w["alt"] == 0 and w["um"] is None:
                    w["um"] = t
                w["alt"] = int(b["pl"][i])
        ab = []
        for t, u in pl.stand(p, "DAT_UnitsState", {**U}):
            for k, w in fuer.items():
                if w["um"] == t:
                    m = (u["da"] != 0) & (u["b"] > 0) & (u["b"] != w["o"]) & (u["typ"] > 1)
                    m[0] = False
                    if m.any():
                        d = np.maximum(np.abs(u["mx"][m] // 8 - w["x"]), np.abs(u["my"][m] // 8 - w["y"]))
                        ab.append(int(d.min()))
        w0 = next(iter(fuer.values()))
        print("P303/P304", s, "Tore", len(fuer), "Abstand des naechsten Feindes beim Wechsel 0 auf 1:", sorted(ab), "Beispiel gateState", w0["z"].most_common(4), "gateState2", w0["z2"].most_common(3), "Timer", w0["ti"].most_common(3))


def p302_p317():
    for s in ("gebaeude_nah", "belagerung", "sonder3", "sonder5"):
        p = pl.neueste(s)
        n = collections.Counter()
        for t, b in pl.stand(p, "DAT_BuildingsState", {"typ": "buildings[].buildingType", "top": "buildings[].hasUnitsOntop"}):
            for i in np.nonzero(b["top"] != 0)[0]:
                n[int(b["typ"][i])] += 1
        print("P302", s, "Gebaeudeart mit hasUnitsOntop: Rahmen", n.most_common(5))
    p = pl.neueste("sonder3")
    v = []
    start = None
    for t, x in pl.stand(p, "DAT_PathFindingState", {"art": "climbData[].type", "richtung": "climbData[].ladderDirection"}):
        start = t if start is None else start
        w = [(int(i), int(x["art"][i]), int(x["richtung"][i])) for i in np.nonzero(x["art"] != 0)[0]]
        if not v or v[-1][1] != w:
            v.append((t - start, w))
    plan = pl.plan_von(p)
    trag = [e for e in plan["einheiten"] if e["rolle"] == "leiter" and "nr" in e]
    f = {}
    for t, u in pl.stand(p, "DAT_UnitsState", {"f": "units[].facingDirection"}):
        for e in trag:
            w = int(u["f"][e["nr"]])
            if e["nr"] not in f or f[e["nr"]][-1][1] != w:
                f.setdefault(e["nr"], []).append((t - start, w))
    print("P317 climbData (Takt, [(Platz, Art, Richtung)]):", v[:6], "Leitertraeger Blick:", {k: w[-3:] for k, w in f.items()})


def p328_p345_p337():
    z = json.load(open(os.path.join(pl.HIER, "besatzung.regeln.json"), encoding="utf-8"))["zeilen"]
    print("P328 besatzung Ramme, Turm, Schild:", [(x["typ"], x["art"], x["mann"], x["besetzt"], x["felder"], x["handelt"]) for x in z if x["typ"] in (58, 59, 60)])
    z = json.load(open(os.path.join(pl.HIER, "belagerung.regeln.json"), encoding="utf-8"))["zeilen"]
    print("P345 belagerung Ramme:", [(x["ziel"], x["leben"], x["verluste"], x["urteil"]) for x in z if x["geraet"] == 59])
    p = pl.neueste("besatzung")
    plan = pl.plan_von(p)
    g = [e for e in plan["einheiten"] if e.get("rolle") in ("geraet", "ingenieur") and "nr" in e][:6]
    print("P337 Beispiel Rollen", rollen(plan), [{k: e.get(k) for k in ("rolle", "typ", "mann", "soll", "fall", "nr")} for e in g])
    gt = [e for e in plan["einheiten"] if e.get("typ") == 39 and "nr" in e and e.get("mann") == 1]
    if gt:
        n = gt[0]["nr"]
        v, zu = [], []
        start = None
        for t, u in pl.stand(p, "DAT_UnitsState", {"man": "units[].digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300", "w": "units[].targetingType"}):
            start = t if start is None else start
            w = int(u["man"][n])
            if not v or v[-1][1] != w:
                v.append((t - start, w))
        print("   Katapult mit 1 Mann, Nr", n, "Zaehler:", v[:5])
        ing = [e for e in plan["einheiten"] if e["typ"] == 30 and e.get("geraet") == n]
        print("   sein Ingenieur:", ing[:1])


if __name__ == "__main__":
    for f in (p318_p327, p339_p346, p329_p347, p330, p333_p324, p351, p365, p371, p314_p301, p316, p326_p325, p304_nah, p302_p317, p328_p345_p337):
        try:
            f()
        except Exception as e:
            import traceback
            print("FEHLER", f.__name__, repr(e))
            traceback.print_exc(limit=2)
