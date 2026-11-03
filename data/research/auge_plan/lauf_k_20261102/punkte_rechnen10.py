# -*- coding: utf-8 -*-
"""B-142 Lauf K: Die Zaehlungen aus den Einheitenfeldern noch einmal ohne Platz 0. Dort kopiert das Spiel Einheiten vor der Wegsuche hin (setDestinationForUnit), das sind keine eigenen Ereignisse.

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/punkte_rechnen10.py > data/research/auge_plan/lauf_k_20261102/punkte_rechnung10.txt
"""
import collections
import os
import pickle

HIER = os.path.dirname(os.path.abspath(__file__))
d1 = pickle.load(open(os.path.join(HIER, "reihen.pkl"), "rb"))
d2 = pickle.load(open(os.path.join(HIER, "reihen2.pkl"), "rb"))


def reihe(sp, f):
    return d1["t1"]["spieler"].get((sp, f), []) + d1["danach"]["spieler"].get((sp, f), [])


def stand(r, t):
    w = None
    for a, b in r:
        if a > t:
            break
        w = b
    return w


felder = collections.defaultdict(list)
for a in (d1["t1"], d1["danach"]):
    for k, v in a["einh_feld"].items():
        felder[k].extend(x for x in v if x[1] != 0)

print("=== P294 Werte von unknownDigMoatOrWallAttackFlag1015 ohne Platz 0")
print(sorted(collections.Counter(x[4] for x in felder["unknownDigMoatOrWallAttackFlag1015"]).items()))

print("\n=== P269, P267 Flagge gegen gate2, wide3, moat2 ohne Platz 0")
pi = {}
for a in (d2["t1"], d2["danach"]):
    for kk, r in a["pi"].items():
        pi.setdefault(kk, []).extend(r)
h = collections.Counter()
for t, i, ty, o, v in felder["unknownDigMoatOrWallAttackFlag1015"]:
    if v in (1014, 1043, 1044, 1015) and 1 <= o <= 8:
        h[(v, ty, (stand(pi[(o - 1, "gate2")], t) or 0) != 0, (stand(pi[(o - 1, "wide3")], t) or 0) != 0, (stand(pi[(o - 1, "moat2")], t) or 0) != 0)] += 1
print("(Flagge, Typ, gate2, wide3, moat2)", sorted(h.items()))

print("\n=== P259 Verhalten 0x15, 0x16 und Ziel der Geraete ohne Platz 0")
print("Verhalten", sorted(collections.Counter((x[2], x[4]) for x in felder["aiUnitBehaviourType"] if x[4] in (0x15, 0x16)).items()))
h = collections.Counter()
for t, i, ty, o, v in felder["siegeTargetPlayerID"]:
    if ty in (39, 40, 41, 61, 77) and 1 <= o <= 8 and v:
        ziel = reihe(o, "attackedPlayerID")
        h[(ty, o, v == stand(ziel, t), v == stand(ziel, t + 800))] += 1
print("(Typ, Besitzer, gleich Ziel jetzt, gleich Ziel 800 Takte spaeter)", sorted(h.items()))

print("\n=== P260, P261 Verhalten 6 und 7 ohne Platz 0, ohne Bauern")
for w in (6, 7):
    print("Verhalten", w, sorted(collections.Counter((x[3], x[2]) for x in felder["aiUnitBehaviourType"] if x[4] == w and x[2] != 1).items()))
