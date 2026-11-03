# -*- coding: utf-8 -*-
"""B-142 Lauf K: Rechnungen zu den Einzelpunkten aus reihen.pkl und reihen2.pkl. Die Urteile stehen in punkte_urteil.py.

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/punkte_rechnen2.py > data/research/auge_plan/lauf_k_20261102/punkte_rechnung2.txt
"""
import collections
import os
import pickle

HIER = os.path.dirname(os.path.abspath(__file__))
d1 = pickle.load(open(os.path.join(HIER, "reihen.pkl"), "rb"))
d = pickle.load(open(os.path.join(HIER, "reihen2.pkl"), "rb"))
H, T, D = d["haupt"], d["t1"], d["danach"]
KI = {1: 14, 2: 15, 3: 1, 4: 9, 5: 2, 6: 5, 7: 7, 8: 4}
print("KI-Werte je Spieler (aics[KI-1]):")
aic = H["aic"]
for sp, ki in KI.items():
    print(sp, "KI", ki, {n: aic[n][ki - 1] for n in aic}, H["aic_roh"][ki - 1])
print("\nP263/Warum 5 bis 8 nie angreifen: hoechste Truppen gegen AttForceBase")
for sp, ki in KI.items():
    r = []
    for a in (d1["haupt"], d1["t1"], d1["danach"]):
        r += a["spieler"].get((sp, "totalAttackTroops"), [])
    e = []
    for a in (d1["haupt"], d1["t1"], d1["danach"]):
        e += a["spieler"].get((sp, "totalAttackingEngineerTroops"), [])
    print(sp, "AttForceBase", aic["AttForceBase"][ki - 1], "hoechste Truppen", max((w for _, w in r), default=None), "Ingenieure hoechstens", max((w for _, w in e), default=None), "letzte", r[-1:], "erste Werte", r[:4])
print("\nP264 Rechnung je Welle: (Staerke - Welle*5) / AttForceRandom")
for sp in (1, 2, 3, 4):
    w = []
    s = []
    for a in (d1["haupt"], d1["t1"], d1["danach"]):
        w += a["spieler"].get((sp, "currentAttackWave"), [])
        s += a["spieler"].get((sp, "currentWaveRandomAttackingStrength"), [])
    print(sp, "AttForceRandom", aic["AttForceRandom"][KI[sp] - 1], "Welle", [x for x in w if x[0] > 17040], "Staerke", [x for x in s if x[0] > 17040])
print("\nP252 attackVectors")
for sp in (1, 2, 3, 4):
    print(sp, [x for x in D["av"].get(sp, [])][:6])
print("P266 signpostEntryData: Platz sp-1")
for sp in (1, 2, 3, 4):
    print(sp, D["signpost"].get(sp - 1, [])[:5])
print("\nP274 aiSiegeCreationInformation[0..2]: je Eintrag delay, unitID, buildingID ...")
for sp in range(1, 9):
    r = D["siege"].get(sp, [])
    print(sp, len(r), r[:6])
print("\nP245 Stichproben: (Takt, Gebaeude je Besitzer, Index je Spieler, Laenge Liste, erste Eintraege)")
for x in D["geb_stichprobe"][:4]:
    print(x[0], x[1], x[2], x[3], {k: v[:8] for k, v in x[4].items() if k in (1, 2)})
print("\nP251 AIZoneLayer: Werte und Anzahl")
for x in D["zone"][:6]:
    print(x)
print("P253 Wegebene je Spieler, Stichprobe")
if D["weg"]:
    print(D["weg"][10][0], [sorted(v.items())[:6] for v in D["weg"][10][1][:2]])
print("\nP290 Zeltpunkte", D["tent"][:6], D["tent_werte"][:2])
print("P291 Groessen", D["groessen"][:2])
print("P267/P269 je Spieler moat2, gate2, wide3")
for kk, r in sorted(D["pi"].items()):
    print(kk, len(r), r[:5])
print("\nP257 attackUnitRequired.required", D["required"][:4])
print("\nP296 startingTroops je Spieler (Wechsel, erste)")
for sp in range(0, 8):
    r = H["start"].get(sp, [])
    print(sp, len(r), r[:3], "letzte", r[-1:])
print("\nNeue Einheiten je (Besitzer, Typ) in danach, Typen 30/70/72/75 usw.")
z = collections.Counter((o, ty) for t, i, ty, o in D["neu"])
print(sorted(z.items())[:80])
print("Flaggen: Entity-Arten Anzahl", D["flagge_zahl"].most_common(20))
