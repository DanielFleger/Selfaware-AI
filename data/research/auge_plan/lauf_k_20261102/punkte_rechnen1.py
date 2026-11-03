# -*- coding: utf-8 -*-
"""B-142 Lauf K: Rechnungen zu den Einzelpunkten aus reihen.pkl. Gibt Belege aus, die Urteile stehen in punkte_urteil.py.

Aufruf aus dem Arbeitsbaum: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/punkte_rechnen1.py > data/research/auge_plan/lauf_k_20261102/punkte_rechnung1.txt
"""
import collections
import os
import pickle

HIER = os.path.dirname(os.path.abspath(__file__))
d = pickle.load(open(os.path.join(HIER, "reihen.pkl"), "rb"))
H, T, D = d["haupt"], d["t1"], d["danach"]
ALLE = (H, T, D)


def reihe(tab, kk):
    aus = []
    for a in ALLE:
        aus += a[tab].get(kk, [])
    return aus


print("Abgelesen: Takte je Aufzeichnung", {k: (v["takte"][0], v["takte"][-1], len(v["takte"])) for k, v in d.items()})
print("Lords:", H["lords"], D["lords"])
print("\n--- Zustand je Spieler (P279, P263)")
for sp in range(1, 9):
    r = reihe("spieler", (sp, "aiPlayerState"))
    print(sp, "Zustaende", sorted(collections.Counter(w for _, w in r).items()))
    print("   Folge", [w for _, w in r][:40])
    print("   Wechsel", r[:14])
    print("   Takt % 200 beim Wechsel", collections.Counter(t % 200 for t, _ in r[1:]).most_common(8))
print("\n--- P264 Welle und Staerke")
for sp in range(1, 9):
    w = reihe("spieler", (sp, "currentAttackWave"))
    s = reihe("spieler", (sp, "currentWaveRandomAttackingStrength"))
    print(sp, "Welle", w[:12])
    print("   Staerke", s[:12])
print("\n--- P263 Truppen beim Verlassen von Zustand 0")
for sp in range(1, 9):
    r = reihe("spieler", (sp, "aiPlayerState"))
    tr = reihe("spieler", (sp, "totalAttackTroops"))
    ing = reihe("spieler", (sp, "totalAttackingEngineerTroops"))
    st = reihe("spieler", (sp, "currentWaveRandomAttackingStrength"))

    def stand(tab, t):
        w = None
        for a, b in tab:
            if a > t:
                break
            w = b
        return w
    z = []
    for (t0, a), (t1, b) in zip(r, r[1:]):
        if a == 0 and b != 0:
            z.append((t1, b, stand(tr, t1), stand(ing, t1), stand(st, t1)))
    print(sp, z[:10])
print("\n--- P270 Koordination")
for sp in range(1, 9):
    print(sp, reihe("spieler", (sp, "aiAttackCoordinationLevel"))[:14])
print("\n--- P271 relative Staerke (vor Takt 12000 und danach)")
for sp in range(1, 9):
    r = reihe("spieler", (sp, "relativeStrengthOfTeamComparedToEnemy"))
    n = reihe("spieler", (sp, "isNotNervousByEnemyTroopValue"))
    v = [w for t, w in r if t < 12000]
    print(sp, "vor 12000", (min(v), max(v)) if v else None, "gesamt", (min(w for _, w in r), max(w for _, w in r)) if r else None, "NichtNervoes-Wechsel", n[:6], "aiNervous", reihe("spieler", (sp, "aiNervousActionsTracker"))[:5])
print("\n--- P265 Raubzug-Parameter")
for sp in range(1, 9):
    print(sp, reihe("spieler", (sp, "currentAttackRaidParameter"))[:10])
print("\n--- P278 Ziel")
for sp in range(1, 9):
    r = reihe("spieler", (sp, "attackedPlayerID"))
    print(sp, r[:16], "Takt % 800:", collections.Counter(t % 800 for t, _ in r[1:]).most_common(4))
print("\n--- P276 Staerke-Zustand und Gefuehl")
for sp in range(1, 9):
    print(sp, "Zustand", reihe("spieler", (sp, "aiStrengthState"))[:8], "Gefuehl", reihe("spieler", (sp, "aiStrengthFeeling"))[:8])
print("\n--- P242 Rekrutier-Wahl und Nervositaet")
for sp in range(1, 9):
    print(sp, "Wahl", reihe("spieler", (sp, "aiRecruitUnitChoiceState"))[:10], "Nerv", reihe("spieler", (sp, "aiNervousActionsTracker"))[:6])
print("\n--- P260, P261 Ausfall")
for sp in range(1, 9):
    print(sp, "T6", reihe("spieler", (sp, "totalTroopsType6"))[:6], "U1", reihe("spieler", (sp, "unknownCounter_01"))[:6], "T7", reihe("spieler", (sp, "totalTroopsType7"))[:6])
print("\n--- P259 Belaestigung")
for sp in range(1, 9):
    print(sp, "Index", reihe("spieler", (sp, "harrassingSiegeEnginesIndex"))[:8], "spend", reihe("spieler", (sp, "canStartSpending"))[:4])
for f in ("aiUnitBehaviourType", "siegeTargetPlayerID", "unknownDigMoatOrWallAttackFlag1015"):
    z = collections.Counter()
    for a in ALLE:
        for t, i, ty, bes, w in a["einh_feld"].get(f, []):
            z[(ty, w)] += 1
    print(f, "je (Typ, Wert)", z.most_common(40))
print("\n--- P266 kuerzeste Entfernung")
for sp in range(1, 9):
    print(sp, reihe("spieler", (sp, "shortestDistanceX"))[:5], reihe("spieler", (sp, "shortestDistanceY"))[:5])
print("\n--- P284, P285, P286 Angriffsblock")
for f in ("attacker", "macemenTribeCount", "tentPoints", "moat2", "gate2", "wide3", "spearmenAndMacemen", "pikemenSwordsmenAndMore", "laddermen", "engineers", "ranged", "knights", "field86974_0x20f74", "field86627_0x20e04"):
    r = reihe("angriff", f)
    print(f, len(r), r[:10], "Werte", sorted(collections.Counter(w for _, w in r).items())[:14])
print("\n--- P282, P287, P288, P292, P293 value3Array01 und Ticker")
werte = collections.Counter()
for a in ALLE:
    for t, w in a["welle"]:
        for x in w:
            werte[x] += 1
print("value3 Werte ueber alle Rahmen", sorted(werte.items()))
tick = collections.Counter()
hoechst = 0
for a in ALLE:
    for t, w in a["ticker"]:
        hoechst = max(hoechst, max(w))
print("Ticker hoechstens", hoechst)
letzte_welle = None
folge = collections.defaultdict(list)
for a in ALLE:
    for t, w in a["welle"]:
        for i, x in enumerate(w):
            if not folge[i] or folge[i][-1][1] != x:
                folge[i].append((t, x))
for i in sorted(folge)[:8]:
    print("Platz", i, "Wechsel", len(folge[i]), "Folge", [x for _, x in folge[i]][:30], "erste", folge[i][:4])
t_folge = collections.defaultdict(list)
for t, w in T["ticker"]:
    for i, x in enumerate(w):
        t_folge[i].append((t, x))
for i in sorted(t_folge)[:4]:
    print("Ticker in t1 Platz", i, t_folge[i][:12])
print("\n--- P296 Verstaerkung")
c = reihe("kal", "countUpTo201")
print("countUpTo201 Wechsel", len(c), "in t1", T["kal"].get("countUpTo201", [])[:14])
print("hoechst", max(w for _, w in c), "Ruecksprung auf 0 bei Takten", [c[i][0] for i in range(1, len(c)) if c[i][1] == 0][:10])
print("\n--- P243 Belagerungsbauten, P246 Schutt: Gebaeude")
typen = {}
for a in ALLE:
    for (i, f), r in a["geb"].items():
        if f == "buildingType":
            for t, w in r:
                if w:
                    typen.setdefault(i, []).append((t, w))
je = collections.Counter(v[-1][1] for v in typen.values())
print("Gebaeudearten", sorted(je.items()))
ST = {}
for a in ALLE:
    for (i, f), r in a["geb"].items():
        if f == "logicalState":
            ST.setdefault(i, []).extend(r)
    for (i, f), r in a["geb"].items():
        if f == "noRubble":
            for t, w in r:
                pass
ls = collections.Counter()
for i, r in ST.items():
    for t, w in r:
        ls[(typen.get(i, [(0, 0)])[-1][1], w)] += 1
print("(Art, logicalState) Wechsel", sorted(ls.items())[:80])
nr = collections.Counter()
for a in ALLE:
    for (i, f), r in a["geb"].items():
        if f == "noRubble":
            for t, w in r:
                nr[(typen.get(i, [(0, 0)])[-1][1], w)] += 1
print("(Art, noRubble)", sorted(nr.items()))
print("\n--- P244 Aussenposten")
aussen = [i for i, v in typen.items() if v[-1][1] in (72, 73, 74, 75, 76)]
print("Plaetze", aussen[:10])
print("\n--- P273 Gruppen: counter, randomNumber")
beispiel = 0
for a in (T, D):
    for (i, f), r in sorted(a["gruppe"].items()):
        if f == "counter" and len(r) > 20 and beispiel < 4:
            rn = a["gruppe"].get((i, "randomNumber"), [])
            print("Gruppe", i, "Besitzer", a["gruppe"].get((i, "owner"), [])[:2], "Art", a["gruppe"].get((i, "tribeType"), [])[:2], "random", rn[:3], "counter", r[:30])
            beispiel += 1
print("\n--- Gruppen je Besitzer und Ziel")
ziel = collections.Counter()
for a in (T, D):
    for (i, f), r in a["gruppe"].items():
        if f == "targetPlayer_outpost":
            for t, w in r:
                ziel[w] += 1
print("targetPlayer_outpost Werte", sorted(ziel.items()))
print("targetBuildingID Wechsel", sum(len(r) for a in (T, D) for (i, f), r in a["gruppe"].items() if f == "targetBuildingID"))
print("Zaehlung Einheiten (Besitzer, Typ) Ende", sorted(D["zaehl"][-1][1].items())[:30])
print("Zaehlung (Besitzer, Typ) Takt ~50000", sorted(min(D["zaehl"], key=lambda x: abs(x[0] - 50000))[1].items())[:60])
print("Gold", {sp: D["gold"][sp][:2] + D["gold"][sp][-2:] for sp in range(1, 9) if sp in D["gold"]})
