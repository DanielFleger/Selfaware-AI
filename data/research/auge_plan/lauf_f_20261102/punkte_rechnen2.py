# -*- coding: utf-8 -*-
"""B-142: Zweiter Teil der Nachrechnung von Lauf F: Zuzugsregel, Handelspreise, Einheitennamen, KI-Tabellen. Ausgabe: punkte_rechnung2.txt."""
import bisect
import collections
import glob
import json
import os
import pickle
import re
import struct

from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

HIER = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HIER, "..", "laeufe", "lauf_f_20261102_214240")
D = pickle.load(open(os.path.join(HIER, "reihen.pkl"), "rb"))
karte = Feldkarte.laden(feldliste=FELDLISTE)
H, J = D["haupt"], D["jahr"]
aus = []


def p(*x):
    s = " ".join(str(y) for y in x)
    aus.append(s)
    print(s[:1800])


def sp(f):
    return H["spieler"][f] + J["spieler"][f]


def wert(reihe, t):
    i = bisect.bisect_right([x[0] for x in reihe], t) - 1
    return reihe[i][1] if i >= 0 else None


TYP = {**H["typ_geb"], **J["typ_geb"]}


def geb(i, f):
    return H["geb"].get((i, f), []) + J["geb"].get((i, f), [])


# Zuzugsregel: vclock in aufeinanderfolgenden Lesungen, Spruenge beim Zuzug
vc = H["spieler"]["vclock"]
po = H["spieler"]["currentPopulation"]
be = H["spieler"]["popularity"]
p("vclock erste:", vc[:24])
p("Leute erste:", po[:16])
schritte = collections.Counter()
for k in range(1, len(vc)):
    dt = vc[k][0] - vc[k - 1][0]
    if 0 < dt <= 30:
        schritte[round((vc[k][1] - vc[k - 1][1]) / dt, 1)] += 1
p("vclock je Takt (kurze Abstaende):", schritte.most_common(12))
je = collections.defaultdict(list)
for k in range(1, len(vc)):
    dt = vc[k][0] - vc[k - 1][0]
    d = vc[k][1] - vc[k - 1][1]
    if 0 < dt <= 30 and d < 0:
        je[wert(be, vc[k][0]) // 500 * 5].append(-d / dt)
p("vclock-Abfall je Takt nach Beliebtheit (5er):", {k: (round(sum(v) / len(v), 2), len(v)) for k, v in sorted(je.items())})
vj = J["spieler"]["vclock"]
p("vclock im Jahr:", vj[:12], "Schritte", collections.Counter(vj[k][1] - vj[k - 1][1] for k in range(1, len(vj))).most_common(6), "Abstand", collections.Counter(vj[k][0] - vj[k - 1][0] for k in range(1, len(vj))).most_common(4))
zu = [po[k][0] for k in range(1, len(po)) if po[k][1] > po[k - 1][1]]
p("Zuzug-Takte bis 8000:", [t for t in zu if t < 8000])
for t in [t for t in zu if t < 5000][:6]:
    p("  um Zuzug", t, [x for x in vc if t - 40 <= x[0] <= t + 20][:8])

# Waffenbetrieb und Schlafen
p("Schlafen:", {(i, TYP[i]): [x for x in geb(i, "sleeping")] for i in TYP if any(x[1] for x in geb(i, "sleeping"))})
p("Waffe im Betrieb:", {(i, TYP[i]): sorted(set(x[1] for x in geb(i, "producedItemTypeNext"))) for i in TYP if any(x[1] for x in geb(i, "producedItemTypeNext"))})

# Handel: Kauf
W = H["waren"]
a = next(i for i, z in enumerate(W) if z[0] > 11790)
k = next(i for i in range(a, len(W)) if W[i][1][15] < W[i - 1][1][15])
p("Kauf: Takt", W[k - 1][0], "->", W[k][0], "Gold", W[k][1][15] - W[k - 1][1][15], {w: W[k][1][w] - W[k - 1][1][w] for w in range(25) if w != 15 and W[k][1][w] != W[k - 1][1][w]})

# Tabellen aus dem ersten Datenblock
auf = aw.Aufzeichnung(B + ".auge")
db = auf.namen.index("datenblock")
erst = None
for r, pp, _ in auf.staende():
    if r.bereich == db:
        erst = bytes(pp)
        t_erst = r.takt
        break
dbb = auf.bereiche[db][1]
p("Datenblock erster Rahmen bei Takt", t_erst)


def i32(adr):
    return struct.unpack_from("<i", erst, adr - dbb)[0]


def i16(adr):
    return struct.unpack_from("<h", erst, adr - dbb)[0]


def tab(g, f, n=None, fmt=None):
    ad = karte.adresse(g, f)
    n = n or ad[3] or 1
    gr = ad[1] if ad[1] in (1, 2, 4) else 4
    schritt = ad[2] or gr
    f_ = {1: "<B", 2: "<h", 4: "<i"}[gr]
    return [struct.unpack_from(f_, erst, ad[0] + i * schritt - dbb)[0] for i in range(n)]


for g, f, n in (("DAT_GameState", "mapAndTime.buyAndSalesPriceArray[].buyPrice", 25), ("DAT_GameState", "mapAndTime.buyAndSalesPriceArray[].salesPrice", 25), ("DAT_GameState", "mapAndTime.isResourceTradeable[]", 25)):
    try:
        p(f, tab(g, f, n))
    except Exception as e:  # noqa: BLE001
        p(f, "FEHLT", repr(e)[:120])
ind = {}
for (g, pf) in karte.bekannte:
    for s in ("MarketResourceCycleArray", "buyPrice", "salesPrice", "DAT_BarracksUnitCost", "AttForceBase", "populationIndex", "playerPopulationStatistics", "buildingCosts"):
        if pf.endswith(s) or pf.endswith(s + "[]"):
            ind.setdefault(s, []).append((g, pf))
p({k: v[:3] for k, v in ind.items()})

# Namen der Einheitentypen
R = r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference"
tx = open(os.path.join(R, "types.json"), encoding="utf-8").read()
m = re.search(r'"path":"[^"]*UnitType[^"]*","length":\d+,"definition":"(typedef enum[^"]{200,})"', tx)
namen = {}
if m:
    for n_, w_ in re.findall(r"(\w+)\s*=\s*(\d+)", m.group(1)):
        namen[int(w_)] = n_
p("Typnamen gefunden", len(namen))
ty = collections.defaultdict(collections.Counter)
for t, i, typ, res in H["einh"] + J["einh"]:
    ty[typ][res] += 1
p("Traeger:", {f"{k} {namen.get(k)}": max(v) for k, v in sorted(ty.items()) if max(v) > 0})

# Liga-Tabellen
L = json.load(open(glob.glob(r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme Instanz2\ucp\plugins\Mod-KI-Team-Liga-*\resources\balance\liga_ai.json")[0], encoding="utf-8"))
p("Liga beer", L.get("beer"), "population", {k: (v if not isinstance(v, list) else v) for k, v in L.get("population", {}).items()})
res = L.get("resources", {})
p("Liga Preise", {k: res[k] for k in list(res)[:6]})

# Code: Verkaufsmenge, Kaufmenge, Graben, Bestand
F = os.path.join(R, "functions")
gesucht = {"getSellResourceAmount", "countMoatsOwnedByEachPlayer", "getBatchBuyPrice", "getBatchSellPrice"}
gesehen = set()
for d in os.listdir(F):
    j = json.load(open(os.path.join(F, d), encoding="utf-8"))
    n = (j.get("name") or "").split("::")[-1]
    if n in gesucht:
        gesehen.add(n)
        p("=====", n, d)
        p("\n".join(s.rstrip()[:100] for s in (j.get("pseudocode") or "").splitlines()[4:42] if s.strip()))
    if "countMoatsOwnedByEachPlayer(" in (j.get("pseudocode") or "") and n != "countMoatsOwnedByEachPlayer":
        p("ruft countMoats:", n, d)
open(os.path.join(HIER, "punkte_rechnung2.txt"), "w", encoding="utf-8").write("\n".join(aus))
