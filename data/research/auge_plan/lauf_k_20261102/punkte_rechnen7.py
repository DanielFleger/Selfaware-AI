# -*- coding: utf-8 -*-
"""B-142 Lauf K: Einzelpunkte aus der Hauptaufzeichnung des Kampfs (reihen7.pkl) und den Zeitreihen.

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/punkte_rechnen7.py > data/research/auge_plan/lauf_k_20261102/punkte_rechnung7.txt
"""
import collections
import os
import pickle
import struct

HIER = os.path.dirname(os.path.abspath(__file__))
d7 = pickle.load(open(os.path.join(HIER, "reihen7.pkl"), "rb"))
d6 = pickle.load(open(os.path.join(HIER, "reihen6.pkl"), "rb"))
d1 = pickle.load(open(os.path.join(HIER, "reihen.pkl"), "rb"))
d2 = pickle.load(open(os.path.join(HIER, "reihen2.pkl"), "rb"))
KI = {1: 14, 2: 15, 3: 1, 4: 9, 5: 2, 6: 5, 7: 7, 8: 4}


def reihe(sp, f):
    return d1["t1"]["spieler"].get((sp, f), []) + d1["danach"]["spieler"].get((sp, f), [])


def stand(r, t):
    w = None
    for a, b in r:
        if a > t:
            break
        w = b
    return w


GOLD = {sp: d1["t1"]["gold"].get(sp, []) + d1["danach"]["gold"].get(sp, []) for sp in range(1, 9)}
LORDS = d1["t1"]["lords"] + d1["danach"]["lords"]

print("=== P267 Gruppe 0x11: Haltung gegen moat2 und Zustand")
h = collections.Counter()
for t, sp, i, st, gueltig, m2, zustand, wert in d7["stance"]:
    h[(gueltig, m2, st, zustand)] += 1
print("Eintraege (gueltige Gruppe, moat2>0, Haltung, Zustand)", sorted(h.items(), key=str))
print("mit moat2>0 und gueltiger Gruppe", [x for x in d7["stance"] if x[4] and x[5]][:20])

print("\n=== P268 Zielwechsel der Gruppen: (Ziel brennt, Ziel weg, neues Ziel, Zustand Besitzer)")
print(sorted(d7["ziel_wechsel"].items(), key=str))
print("Summe", sum(d7["ziel_wechsel"].values()), "ohne Grund", sum(v for k, v in d7["ziel_wechsel"].items() if not k[0] and not k[1]), "Beispiele ohne Grund", d7["ziel_bsp"][:10])

print("\n=== P250 Neue Belagerungsbauten: Takt, Platz, Art, Besitzer, Bau x,y, Welle, Auswahl-Einheit Gruppe 0x12 und 0xE, deren Ort, naechster Ingenieur, frei (Nachbarn frei, Hoehenunterschied, Einheit auf der Mitte)")
for x in d7["siege"]:
    print(x)

print("\n=== P252 Angriffsrichtungen je Spieler: (Eintraege mit x, mit Gruppe, erster, zweiter)")
for t, zeile in d7["vektor"][:60:6]:
    print(t, [(z[0], z[1], z[2][:2]) for z in zeile])
print("hoechste Zahl je Spieler", [max(z[1][i][0] for z in d7["vektor"]) for i in range(9)], "mit Gruppe", [max(z[1][i][1] for z in d7["vektor"]) for i in range(9)])

print("\n=== P272 Raubzug-Truppen gegen Wunschzahl (Parameter + RaidUnitsBase)")
aic = d6["t1"]["aic"]
for sp in range(1, 9):
    r = d7["raub"].get(sp, [])
    if not r:
        continue
    base = aic["RaidUnitsBase"][KI[sp]]
    ueber = collections.Counter()
    hoechst = collections.Counter()
    for t, tr, par in r:
        hoechst[par + base] = max(hoechst[par + base], tr)
        ueber[tr > par + base] += 1
    print("Spieler", sp, "Base", base, "je Wunschzahl hoechste Truppen", sorted(hoechst.items()), "ueber Wunsch", ueber[True], "von", len(r), "letzte", r[-1])

print("\n=== P275 Jahreswechsel: Ziele der Raubzug-Gruppen vor und nach dem Wechsel")
wird_null = bleibt = anders = 0
bsp = []
for t, jahr, vor, nach in d7["jahr"]:
    for kk, (gr, z) in nach.items():
        if kk in vor and vor[kk][0] == gr and vor[kk][1] != 0:
            if z == 0:
                wird_null += 1
                bsp.append((t, kk, vor[kk], z))
            elif z == vor[kk][1]:
                bleibt += 1
            else:
                anders += 1
print("Jahreswechsel", [(t, j) for t, j, _, _ in d7["jahr"]][:16], "Ziel bleibt", bleibt, "wird 0", wird_null, "anderes Ziel", anders, bsp[:6])
yc = d1["t1"]["kal"].get("yearChanged", []) + d1["danach"]["kal"].get("yearChanged", [])
print("yearChanged gesehen", [(t, w, t % 50) for t, w in yc if w][:20])
print("Tag-Takt beim Jahreswechsel: Takt modulo 50", [t % 50 for t, _, _, _ in d7["jahr"]])

print("\n=== P271 Nervositaet: bei Tracker 8: Takt, Spieler, relative Staerke, feindliche Fernkaempfer")
print(d7["nerv"])
hist = collections.Counter()
for sp in range(1, 9):
    for t, w in reihe(sp, "relativeStrengthOfTeamComparedToEnemy"):
        if t < 12000:
            hist[w < 250] += 1
print("Vor Takt 12000: relative Staerke unter 250", hist)

print("\n=== P253 Wegebene: je Ziel und Wert (Felder, Nachbar in 4 Richtungen mit Wert-1, in 8 Richtungen)")
print(d7["bfs"])

print("\n=== P278 UCP-Stueck: Zielwechsel im ganzen Lauf, solange Zustand >= 3 und der alte Gegner lebt")
for sp in range(1, 9):
    ziel = reihe(sp, "attackedPlayerID")
    zust = reihe(sp, "aiPlayerState")
    verletzt = []
    n = 0
    for (a, va), (b, vb) in zip(ziel, ziel[1:]):
        if va == vb or b <= 17040:
            continue
        n += 1
        z = stand(zust, b - 1)
        leb = stand(LORDS, b - 1) or ()
        if z is not None and z >= 3 and va in leb:
            verletzt.append((b, va, vb, z))
    print("Spieler", sp, "Zielwechsel", n, "im Angriff bei lebendem Gegner", verletzt[:6], "TargetChoice", aic["TargetChoice"][KI[sp]])
print("Burgeingaenge", {sp: (d6["t1"]["R"][15040][sp]["campground.xEntry"], d6["t1"]["R"][15040][sp]["campground.yEntry"]) for sp in range(1, 9)})
print("--- TargetChoice 2 im ganzen Lauf: Monatswechsel, Ziel gegen naechsten lebenden Gegner")
ort = {sp: (d6["t1"]["R"][15040][sp]["campground.xEntry"], d6["t1"]["R"][15040][sp]["campground.yEntry"]) for sp in range(1, 9)}
for sp in (4, 6, 8):
    ziel = reihe(sp, "attackedPlayerID")
    zust = reihe(sp, "aiPlayerState")
    ok = schlecht = 0
    bsp = []
    for b, vb in ziel:
        if b <= 17040:
            continue
        leb = [i for i in (stand(LORDS, b) or ()) if i != sp]
        if not leb:
            continue
        besser = None
        d = 10**6
        for i in sorted(leb):
            x = max(abs(ort[i][0] - ort[sp][0]), abs(ort[i][1] - ort[sp][1]))
            if x <= d:
                d, besser = x, i
        if vb == besser:
            ok += 1
        else:
            schlecht += 1
            bsp.append((b, "ist", vb, "soll", besser, leb))
    print("Spieler", sp, "passt", ok, "nicht", schlecht, bsp[:5])

print("\n=== P243 Jeder Belagerungsbau bis zu seinem Ende gegen das Ende seiner Welle")
ty_, ow_, ls_ = {}, {}, collections.defaultdict(list)
for a in (d1["t1"], d1["danach"]):
    for (i, f), r in a["geb"].items():
        if f == "logicalState":
            ls_[i].extend(r)
zaehl = collections.Counter()
zeilen = []
for t, i, art, o, bx, by, welle, sel, orte, nah, frei in d7["siege"]:
    folge = [x for x in ls_.get(i, []) if x[0] >= t]
    ende = next((x for x in folge if x[1] in (0, 3)), None)
    te = ende[0] if ende else None
    zustand = stand(reihe(o, "aiPlayerState"), te) if te else None
    wellen_ende = [x for x, v in reihe(o, "aiPlayerState") if v == 9 and x >= t]
    naechste = wellen_ende[0] if wellen_ende else None
    if te is None:
        klasse = "steht am Ende noch"
    elif naechste is not None and abs(te - naechste) <= 12:
        klasse = "am Wellenende"
    elif naechste is not None and te < naechste:
        klasse = "vorher zerstoert"
    else:
        klasse = "nach dem Wellenende"
    zaehl[(art, klasse)] += 1
    zeilen.append((t, i, art, o, "Welle", welle, "Ende", te, "Zustand", zustand, "Wellenende", naechste, klasse))
print(sorted(zaehl.items()))
for z in zeilen:
    print(z)
print("Eigentuemer Kathedrale", [(i, stand(d1["danach"]["geb"].get((i, "owner"), []), 10**9)) for (i, f), r in d1["danach"]["geb"].items() if f == "buildingType" and r and r[-1][1] == 38])
