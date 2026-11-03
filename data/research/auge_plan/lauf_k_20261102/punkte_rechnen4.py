# -*- coding: utf-8 -*-
"""B-142 Lauf K: Letzte Rechnungen: Namen der Arten, Ingenieure und Gold (P258), Belagerungsbauten (P243), Flaggen in t1 (P242), Feindliste (P245), Zone gegen Wegebene (P251, P253), Stichprobe Lords und Ausfall.

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/punkte_rechnen4.py <basis> > data/research/auge_plan/lauf_k_20261102/punkte_rechnung4.txt
"""
import collections
import json
import os
import pickle
import re
import struct
import sys

import numpy as np

from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

HIER = os.path.dirname(os.path.abspath(__file__))
basis = sys.argv[1]
k = Feldkarte.laden(feldliste=FELDLISTE)
d1 = pickle.load(open(os.path.join(HIER, "reihen.pkl"), "rb"))
d2 = pickle.load(open(os.path.join(HIER, "reihen2.pkl"), "rb"))
roh = open(r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference\types.json", encoding="utf-8").read()
UT = {int(z): n for n, z in re.findall(r"\b(UT_[A-Z0-9_]+): (\d+)", roh.replace("\\n", " "))}
BT = {int(z): n for n, z in re.findall(r"\b(BT_[A-Z0-9_]+): (\d+)", roh.replace("\\n", " "))}
ET = {int(z): n for n, z in re.findall(r"\b(ET_[A-Z0-9_]+): (\d+)", roh.replace("\\n", " "))}
print("Einheitenarten", {t: UT.get(t) for t in (1, 3, 22, 23, 24, 25, 27, 28, 29, 30, 33, 35, 37, 39, 40, 41, 51, 52, 53, 55, 57, 60, 61, 62, 63, 64, 70, 71, 72, 75, 76)})
print("Gebaeudearten", {t: BT.get(t) for t in (1, 3, 27, 32, 33, 45, 46, 53, 55, 62, 66, 76, 92, 94, 99, 100, 101, 103)})
print("Geschossarten", {t: ET.get(t) for t in (1, 4, 5, 6, 9, 10, 11, 13, 14, 21, 27, 30, 33, 40, 41, 43)})
ENG = next((z for z, n in UT.items() if "ENGINEER" in n), None)
LAD = next((z for z, n in UT.items() if "LADDER" in n), None)
print("Ingenieur", ENG, "Leitermann", LAD)

print("\n--- P258 Gold beim neuen Ingenieur: Aenderung im selben Rahmen")
g = collections.defaultdict(dict)
for a in (d1["t1"], d1["danach"]):
    for sp, r in a["gold"].items():
        for (t0, w0), (t1, w1) in zip(r, r[1:]):
            g[sp][t1] = w1 - w0
hist = collections.Counter()
for a in (d2["t1"], d2["danach"]):
    for t, i, ty, o in a["neu"]:
        if ty == ENG and o in g and t in g[o]:
            hist[g[o][t]] += 1
print("Goldaenderung bei neuem Ingenieur", hist.most_common(10), "Ingenieure gesamt", sum(1 for a in (d2["t1"], d2["danach"]) for x in a["neu"] if x[2] == ENG))

print("\n--- P243 Belagerungsbauten: Art, Besitzer, Folge logicalState, Zustand des Besitzers beim letzten Wechsel")
typ = {}
own = {}
ls = collections.defaultdict(list)
for a in (d1["t1"], d1["danach"]):
    for (i, f), r in a["geb"].items():
        if f == "buildingType" and r:
            typ[i] = r[-1][1] or typ.get(i)
        if f == "owner" and r:
            own[i] = r[-1][1] or own.get(i)
        if f == "logicalState":
            ls[i] += r
Z = {sp: d1["t1"]["spieler"].get((sp, "aiPlayerState"), []) + d1["danach"]["spieler"].get((sp, "aiPlayerState"), []) for sp in range(1, 9)}


def stand(r, t):
    w = None
    for a, b in r:
        if a > t:
            break
        w = b
    return w


zaehl = collections.Counter()
for i, r in ls.items():
    if typ.get(i) in (92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 103):
        o = own.get(i)
        fo = [w for _, w in r]
        ende = r[-1][0]
        zaehl[(typ.get(i), tuple(fo[-3:]), stand(Z.get(o, []), ende))] += 1
print(zaehl.most_common(24))

print("\n--- P245 Feindliste: Eintraege gehoeren einem Gegner?")
for x in d2["danach"]["geb_stichprobe"][:2]:
    t, je, idx, ln, liste = x
    print(t, "Summe", sum(je.values()), "je", je, "Index", idx, "eigener Eintrag?", {sp: sum(1 for ty, o in v if o == sp) for sp, v in liste.items()})

print("\n--- P242 Flaggen in t1: Besitzer, someTracker, Wahl")
a = aw.Aufzeichnung(basis + "_t1.auge")
E = a.namen.index("DAT_EntityState")
Eb = a.bereiche[E][1]
ER = {f: k.adresse("DAT_EntityState", "entityArray[]." + f) for f in ("logicalState", "entityType", "owner", "someTracker")}
TYP = {2: "<i2", 4: "<i4"}


def sp(p, f):
    return np.ndarray(shape=(f[3],), dtype=TYP[f[1]], buffer=p, offset=f[0] - Eb, strides=(f[2],))


reihe = collections.defaultdict(list)
for r, p, _ in a.staende():
    if r.bereich != E:
        continue
    l, ty, ow, tr = (sp(p, ER[x]) for x in ("logicalState", "entityType", "owner", "someTracker"))
    m = (l != 0) & (ty == 14)
    z = collections.Counter(zip(ow[m].tolist(), tr[m].tolist()))
    for o in range(1, 9):
        w = tuple(sorted((v, c) for (b, v), c in z.items() if b == o))
        if not reihe[o] or reihe[o][-1][1] != w:
            reihe[o].append((r.takt, w))
for o in range(1, 9):
    print(o, "Flaggen", reihe[o][:6], "Wahl", [x for x in d1["t1"]["spieler"].get((o, "aiRecruitUnitChoiceState"), [])][:6])

print("\n--- P251, P253 Zone gegen Wegebene in einer Stichprobe")
T = aw.Aufzeichnung(basis + "_danach.auge")
i = T.namen.index("DAT_TileMapState")
b = T.bereiche[i][1]
Z_A = k.adresse("DAT_TileMapState", "AIZoneLayer[]")
n = 0
for r, p, _ in T.staende():
    if r.bereich == i and r.takt > 60000:
        z = np.frombuffer(p, dtype=np.uint8, offset=Z_A[0] - b, count=80400)
        print("Takt", r.takt, "Zone Werte", dict(zip(*[x.tolist() for x in np.unique(z, return_counts=True)])))
        for spieler in (1, 2, 3, 4):
            w = np.frombuffer(p, dtype=np.uint8, offset=0x01EE2998 + spieler * 0x13A10 - b, count=80400)
            print(" Spieler", spieler, "Wegebene: Felder Zone 1 mit Wert 1:", int(((z == 1) & (w == 1)).sum()), "von", int((z == 1).sum()), "Werte", dict(list(zip(*[x.tolist() for x in np.unique(w, return_counts=True)]))[:5]))
        n += 1
        if n >= 1:
            break
print("\n--- P259, P274 Ingenieure mit 0x16, Ziel der Geraete")
ai = collections.Counter()
for a2 in (d1["t1"], d1["danach"]):
    for t, i2, ty, o, w in a2["einh_feld"].get("aiUnitBehaviourType", []):
        if w in (0x15, 0x16):
            ai[(UT.get(ty, ty), w)] += 1
print(ai.most_common(10))
print("\n--- P294 Werte unknownDigMoatOrWallAttackFlag1015")
wf = collections.Counter(w for a2 in (d1["t1"], d1["danach"]) for t, i2, ty, o, w in a2["einh_feld"].get("unknownDigMoatOrWallAttackFlag1015", []))
print(sorted(wf.items()))
print("\n--- P256 Gruppen: targetPlayer_outpost Felder gesamt", sum(1 for a2 in (d1["t1"], d1["danach"]) for (i2, f) in a2["gruppe"] if f == "targetPlayer_outpost"))
print("--- P276: Einzelfall Spieler 1 Strength-Wechsel mit Monatstakt", d1["danach"]["spieler"].get((1, "aiStrengthState"), [])[:6], "Takt % 800", [t % 800 for t, _ in d1["danach"]["spieler"].get((1, "aiStrengthState"), [])][:10])
print("--- P278: TargetChoice je KI aus reihen2: siehe punkte_rechnung3")
print("--- P260/P261 Typen der Ausfalltruppen je Spieler", {(sp2, UT.get(ty, ty)): c for (sp2, ty), c in collections.Counter((o, ty) for t, i2, ty, o in d2["danach"]["neu"] if ty in (22, 23, 24, 25, 27, 28, 29, 30, 37, 70, 75)).items() if sp2 in (1, 2, 3, 4)})
