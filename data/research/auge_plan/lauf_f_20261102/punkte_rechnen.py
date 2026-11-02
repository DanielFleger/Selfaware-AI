# -*- coding: utf-8 -*-
"""B-142: Rechnet Einzelpunkte von Lauf F aus den Zeitreihen (reihen.pkl) und den Tabellen im Datenblock nach. Ausgabe: punkte_rechnung.txt.

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_f_20261102/punkte_rechnen.py
"""
import bisect
import collections
import json
import os
import pickle
import re
import struct
import sys

from selfaware.game.ucp import bauen
from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

HIER = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HIER, "..", "laeufe", "lauf_f_20261102_214240")
D = pickle.load(open(os.path.join(HIER, "reihen.pkl"), "rb"))
karte = Feldkarte.laden(feldliste=FELDLISTE)
H, J = D["haupt"], D["jahr"]
NAME = {t: g.get("name") for t, g in bauen.NACH_TYP.items()}
aus = []


def p(*x):
    s = " ".join(str(y) for y in x)
    aus.append(s)
    print(s[:1500])


def sp(f):
    return H["spieler"][f] + J["spieler"][f]


def wert(reihe, t):
    i = bisect.bisect_right([x[0] for x in reihe], t) - 1
    return reihe[i][1] if i >= 0 else None


TYP = {**H["typ_geb"], **J["typ_geb"]}


def geb(i, f):
    return H["geb"].get((i, f), []) + J["geb"].get((i, f), [])


def nach_typ(typ):
    return [i for i, t in TYP.items() if t == typ]


p("Gebaeude:", {i: f"{t} {NAME.get(t)}" for i, t in sorted(TYP.items()) if t not in (1, 10, 19, 11)})

# P090 Furchtstufe
fl, gu, sc, po = sp("fearFactorLevel"), sp("goodStuffCount"), sp("badStuffCount"), sp("currentPopulation")
falsch = gut = 0
beispiele = []
for t, w in fl:
    g_, s_, n_ = wert(gu, t), wert(sc, t), wert(po, t)
    soll = int((g_ - s_) / (n_ // 16 + 1))
    if soll == w:
        gut += 1
    else:
        falsch += 1
        beispiele.append((t, w, g_, s_, n_, soll))
p("P090 Furchtstufe = (gut-schlecht)/(Leute/16+1):", "passt", gut, "weicht ab", falsch, beispiele[:8], "Stufen", sorted(set(x[1] for x in fl)))

# P112, P113 Felder
for typ, soll in ((33, "?"), (34, "?")):
    pass
for i, t in sorted(TYP.items()):
    r = geb(i, "growCounter")
    if len(r) > 5:
        w = [x[1] for x in r]
        spruenge = [(r[k - 1][1], r[k][1], r[k][0]) for k in range(1, len(r)) if r[k][1] < r[k - 1][1]]
        j = J["geb"].get((i, "growCounter"), [])
        p("growCounter", i, t, NAME.get(t), "Wechsel", len(r), "max", max(w), "Ruecksprung", spruenge[:4], "je Takt im Jahr", collections.Counter(j[k][1] - j[k - 1][1] for k in range(1, len(j))).most_common(4))

# P114, P115 Vieh
for i, t in sorted(TYP.items()):
    r = J["geb"].get((i, "numberOfAnimals"), []) + []
    q = J["geb"].get((i, "outpostRelatedUnk4"), [])
    if len(H["geb"].get((i, "numberOfAnimals"), [])) > 1 or len(r) > 1:
        sp_ = [(q[k - 1][1], q[k][1], q[k][0]) for k in range(1, len(q)) if q[k][1] < q[k - 1][1]]
        p("Vieh", i, t, NAME.get(t), "Tiere Haupt", H["geb"].get((i, "numberOfAnimals"), [])[:12], "Jahr", r[:8], "Zaehler max", max([x[1] for x in q] or [0]), "Ruecksprung", sp_[:4], "Schritte", collections.Counter(q[k][1] - q[k - 1][1] for k in range(1, len(q))).most_common(3))

# P089, P110, P220 Schenke
for i, t in sorted(TYP.items()):
    r = J["geb"].get((i, "flagonsOfAleOrCheeseOrReleaseDogs"), [])
    rr = H["geb"].get((i, "flagonsOfAleOrCheeseOrReleaseDogs"), [])
    if len(r) > 3 or len(rr) > 3:
        d = collections.Counter(r[k][1] - r[k - 1][1] for k in range(1, len(r)))
        ab = [r[k][0] - r[k - 1][0] for k in range(1, len(r)) if r[k][1] - r[k - 1][1] == -1]
        p("Humpen", i, t, NAME.get(t), "Jahr Schritte", d.most_common(6), "Takte je -1:", collections.Counter(ab).most_common(4), "max", max([x[1] for x in r + rr]), "Haupt erste", rr[:5])
p("aleRate", sp("aleRate"), "Bier-Posten", sp("popularityChangeAleBased")[:12], "beerPercentage", sp("beerPercentage")[:10])

# P117 vclock gegen Beliebtheit
vc, be = sp("vclock"), sp("popularity")
pa = [(t, w, wert(be, t)) for t, w in vc[:: max(1, len(vc) // 14)]]
p("P117 vclock, Beliebtheit:", pa)

# P141 foodClockSpeed
fc, ra = sp("foodClockSpeed"), sp("rationsSetting")
je = collections.defaultdict(set)
for t, w in fc:
    r_, n_ = wert(ra, t), wert(po, t)
    if n_:
        je[r_].add(round(w / n_, 2))
p("P141 foodClockSpeed je Kopf nach Ration:", {k: sorted(v)[:8] for k, v in sorted(je.items())})

# P145, P146, P151 Steuer am Monatswechsel
go = [(t, w[15]) for t, w in H["waren"] + J["waren"]]
li, lb = sp("lastMonthsIncomeTax"), sp("lastMonthsBribeTax")
for t, w in sorted(set(li + lb)):
    if t > 100:
        p("Steuer: Takt", t, "Stufe", wert(sp("taxesSetting"), t), "Leute", wert(po, t), "Einnahme", wert(li, t), "Bestechung", wert(lb, t), "Gold davor", wert(go, t - 1), "danach", wert(go, t))
p("Sammelfelder", sp("taxIncomeMonthlyAccumulator")[:12], sp("taxBribeMonthlyAccumulator")[:12])
p("Steuerstufen", sp("taxesSetting")[:16], "Posten", sp("popularityChangeBasedOnTax")[:16], "Rationen", sp("rationsSetting")[:8], "Beliebtheit min im Lauf", min(x[1] for x in be), "max", max(x[1] for x in be))

# Handel und Anwerben: Warenstand um die Befehle
pr = [json.loads(z) for z in open(B + ".protokoll.jsonl", encoding="utf-8")]
W = H["waren"]
for t0, t1, name in ((11800, 11815, "Verkauf"), (11815, 11835, "Kauf"), (16480, 16580, "Anwerben")):
    a, b = wert(W, t0), wert(W, t1)
    if a and b:
        p(name, t0, t1, "Gold", b[15] - a[15], {k: b[k] - a[k] for k in range(25) if b[k] != a[k] and k != 15})
for z in [x for x in W if 11790 <= x[0] <= 11900][:12]:
    p("  Waren", z[0], "Gold", z[1][15], "Stein", z[1][4], "Holz", z[1][2], "Speer", z[1][19], "Bogen", z[1][17])
for z in [x for x in W if 16490 <= x[0] <= 16600][:10]:
    p("  Anwerben", z[0], "Gold", z[1][15], "Waffen", z[1][17:25])
p("Pferde", H["spieler"]["availableHorses"][:16], "Heer", H["spieler"]["armySize"][-8:], "count_2", H["spieler"]["count_2"][:6])

# Einheiten: resourceToDeposit je Typ
ty = collections.defaultdict(collections.Counter)
for t, i, typ, res in H["einh"] + J["einh"]:
    ty[typ][res] += 1
p("resourceToDeposit je Einheitentyp:", {k: sorted(v)[:12] for k, v in sorted(ty.items())})

# Kalender
for n in ("dayTicks", "weekTicks", "monthTicks"):
    r = J["kal"][n]
    w = [x[1] for x in r]
    sp_ = [r[k][0] for k in range(1, len(r)) if r[k][1] < r[k - 1][1]]
    p(n, "max im Jahr", max(w), "Ruecksprung alle", collections.Counter(sp_[k] - sp_[k - 1] for k in range(1, len(sp_))).most_common(3))
p("Monate", H["kal"]["month"][:6], "Jahr", H["kal"]["year"], J["kal"]["year"])
p("weekChanged", collections.Counter(J["kal"]["weekChanged"][k][0] - J["kal"]["weekChanged"][k - 2][0] for k in range(2, len(J["kal"]["weekChanged"]), 2)).most_common(3))

# Gebaeude-Felder
p("Tor", {i: (geb(i, "gateState")[:4], geb(i, "gateCloseOpenTimer")[:3], geb(i, "gateCloseOpenTimer")[-2:]) for i, t in TYP.items() if t in (45, 46)})
p("Hovel", [(i, geb(i, "hovelVisualStyle")[:2]) for i, t in sorted(TYP.items()) if t == 1])
p("cooldown max", max(x[1] for i in TYP for x in geb(i, "cooldownTimer")))
for i, t in sorted(TYP.items()):
    q = geb(i, "quarryStockpileID")
    if q and any(x[1] for x in q):
        p("Steinbruch", i, t, NAME.get(t), q[:3], "Halde", {x[1]: TYP.get(x[1]) for x in q if x[1]})
p("sleeping", {(i, TYP[i]): geb(i, "sleeping") for i in TYP if geb(i, "sleeping") and len(geb(i, "sleeping")) > 1})
p("zweiter Waffenbetrieb", {(i, TYP[i]): geb(i, "producedItemTypeNext")[:6] for i in TYP if len(geb(i, "producedItemTypeNext")) > 1})
p("countSlingers2", sp("countSlingers2")[:6], sp("countSlingers2")[-4:], "moatsOwned", sp("moatsOwned")[:4], "fail", sp("storageMarketFailState")[:4])
p("Religion", sp("religionVar1"), sp("popularityChangeBasedOnReligion")[:8], "Produktivitaet", sp("fearFactorProductivityUnk"), "Stufe", sorted(set(x[1] for x in fl)))
p("Essen Sorten", sp("foodTypesCurrentlyEaten")[:12], "Lager", collections.Counter(x[1] for x in sp("foodTypesInStock")).most_common(6), "Heiler", sp("healerCount")[:4])

# Tabellen und Bits aus dem Datenblock
auf = aw.Aufzeichnung(B + ".auge")
db = auf.namen.index("datenblock")
tm = auf.namen.index("DAT_TileMapState")
erst = None
letzt_tm = None
for r, pp, _ in auf.staende():
    if r.bereich == db and erst is None:
        erst = bytes(pp)
    if r.bereich == tm:
        letzt_tm = (r.takt, bytes(pp))
dbb = auf.bereiche[db][1]


def lies(adr, n=4, fmt="<i"):
    return struct.unpack_from(fmt, erst, adr - dbb)[0]


def a(g, f):
    return karte.adresse(g, f)


# P206, P207 Felder im LogicLayer
ll = a("DAT_TileMapState", "LogicLayer[]")
tb = auf.bereiche[tm][1]
werte = struct.unpack_from("<%di" % ll[3], letzt_tm[1], ll[0] - tb)
p("LogicLayer", hex(ll[0]), ll[1:], "bei Takt", letzt_tm[0], "Bit 0x1000000:", sum(1 for w in werte if w & 0x1000000), "Bit 0x2000000:", sum(1 for w in werte if w & 0x2000000), "Weizenfarmen", len(nach_typ(35)), [(t, NAME.get(t)) for t in sorted(set(TYP.values())) if t in (32, 33, 34, 35, 36, 37)])

# P018 Markt, P016 handelbar, Preise
mc = a("DAT_GameState", "mapAndTime.MarketResourceCycleArray[]") if False else None
for name, g_, f_ in (("Markt", None, "MarketResourceCycleArray[]"), ("Handelbar", "DAT_GameState", "mapAndTime.isResourceTradeable[]"), ("Kauf", "DAT_GameState", "mapAndTime.buyAndSalesPriceArray[]")):
    try:
        treffer = [(g, pf) for (g, pf) in karte.bekannte if pf.endswith(f_)] if hasattr(karte, "bekannte") else []
        p(name, treffer[:3])
    except Exception as e:  # noqa: BLE001
        p(name, "Fehler", e)

open(os.path.join(HIER, "punkte_rechnung.txt"), "w", encoding="utf-8").write("\n".join(aus))
