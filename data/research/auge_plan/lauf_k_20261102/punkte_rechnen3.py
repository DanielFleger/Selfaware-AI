# -*- coding: utf-8 -*-
"""B-142 Lauf K: Rechnungen zu den Einzelpunkten: KI-Werte am richtigen Platz, Angriffsblock je Spieler (reihen3.pkl), Truppen je Spieler. Die Urteile stehen in punkte_urteil.py.

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/punkte_rechnen3.py > data/research/auge_plan/lauf_k_20261102/punkte_rechnung3.txt
"""
import collections
import os
import pickle

HIER = os.path.dirname(os.path.abspath(__file__))
d1 = pickle.load(open(os.path.join(HIER, "reihen.pkl"), "rb"))
d2 = pickle.load(open(os.path.join(HIER, "reihen2.pkl"), "rb"))
d3 = pickle.load(open(os.path.join(HIER, "reihen3.pkl"), "rb"))
KI = {1: 14, 2: 15, 3: 1, 4: 9, 5: 2, 6: 5, 7: 7, 8: 4}
H = d2["haupt"]
aic, roh = H["aic"], H["aic_roh"]
print("aiType je Spieler:", {sp: d1["haupt"]["spieler"].get((sp, "aiType"), [])[:2] for sp in KI})
print("aics[KI] je Spieler:")
for sp, ki in KI.items():
    print(sp, "KI", ki, {n: aic[n][ki] for n in aic}, roh[ki])
print("\nTruppen je Spieler im Verlauf: Soldaten ohne Lord und Arbeiter sind hier alle Typen ausser Bauer 1, Lord 55; (Besitzer: Summe Typen 22..39, 60..78)")
for t, z in d1["danach"]["zaehl"][::24]:
    je = collections.Counter()
    for (b, ty), n in z.items():
        if ty in range(22, 41) or ty in range(60, 80):
            je[b] += n
    print(t, sorted(je.items()))
print("\nSpieler 5 bis 8: Einheiten je Typ bei rund Takt 30.000")
z = min(d1["danach"]["zaehl"], key=lambda x: abs(x[0] - 30000))
for sp in (5, 6, 7, 8):
    print(sp, z[0], sorted((ty, n) for (b, ty), n in z[1].items() if b == sp))
A = {k: d3[k] for k in d3}
print("\nAngriffsblock je Spieler (t1 und danach): Wechsel, Werte")
for sp in range(1, 9):
    for f in ("attacker", "macemenTribeCount", "tentPoints", "moat2", "gate2", "wide3", "spearmenAndMacemen", "pikemenSwordsmenAndMore", "laddermen", "engineers", "ranged", "knights", "field86974_0x20f74", "field86627_0x20e04"):
        r = A["t1"]["felder"].get((sp, f), []) + A["danach"]["felder"].get((sp, f), [])
        if len(r) > 2:
            print(sp, f, len(r), r[:7])
print("\nP281, P282, P287, P288, P292, P293: value3Array01 und attackWaveTicker je Spieler")
for sp in range(1, 9):
    r = A["danach"]["welle"].get(sp, [])
    werte = collections.Counter()
    folge = collections.defaultdict(list)
    for t, w in r:
        for i, x in enumerate(w):
            werte[x] += 1
            if not folge[i] or folge[i][-1][1] != x:
                folge[i].append((t, x))
    print(sp, "Wechsel", len(r), "Werte", sorted(werte.items()))
    belegte = [i for i in sorted(folge) if len(folge[i]) > 1]
    for i in belegte[:3]:
        print("   Platz", i, [x for _, x in folge[i]][:24], folge[i][:5])
    tk = A["danach"]["ticker"].get(sp, [])
    hoch = max((max(w) for _, w in tk), default=0)
    print("   Ticker hoechstens", hoch, "Wechsel", len(tk), "Werte Beispiel", collections.Counter(x for _, w in tk[:400] for x in w if x).most_common(6))
print("\nP290 Zelte, P291 Groessen, P284 die 9 Werte")
for sp in (1, 2, 3, 4):
    print(sp, "Zelt", [x for x in A["danach"]["zelt"].get(sp, [])][:3])
    print(sp, "Groessen", [x for x in A["danach"]["groessen"].get(sp, [])][:3])
    print(sp, "Neun", [x for x in A["danach"]["neun"].get(sp, [])][:6])
print("\nNeue Einheiten je (Besitzer, Typ) in danach")
z = collections.Counter((o, ty) for t, i, ty, o in d2["danach"]["neu"])
print(sorted(z.items()))
print("\nP296 startingTroops")
for sp in range(0, 8):
    r = H["start"].get(sp, [])
    print(sp, len(r), [x[0] for x in r], r[0][1], r[1][1] if len(r) > 1 else "")
print("countUpTo201", d1["haupt"]["kal"].get("countUpTo201", [])[:6], "Hoechster", max(w for _, w in d1["haupt"]["kal"].get("countUpTo201", [(0, 0)])))
print("\nGebaeude: Art je Besitzer am Ende der Friedenszeit, Takt 15.039")
print("Flaggen", d2["danach"]["flagge_zahl"].most_common(14))
print("\nP286 Keulen je Spieler, P285", {sp: A["danach"]["felder"].get((sp, "macemenTribeCount"), [])[:6] for sp in (1, 2, 3, 4)})
