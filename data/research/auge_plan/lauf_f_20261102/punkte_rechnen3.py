# -*- coding: utf-8 -*-
"""B-142: Dritter Teil der Nachrechnung von Lauf F: Befehlsring, Anwerbekosten, KI-Tabellen, Einheitennamen, Bevoelkerungsstatistik. Ausgabe: punkte_rechnung3.txt."""
import collections
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
    print(s[:1900])


auf = aw.Aufzeichnung(B + ".auge")
db, be = auf.namen.index("datenblock"), auf.namen.index("befehle")
erst = None
ring0 = ring1 = None
for r, pp, _ in auf.staende():
    if r.bereich == db and erst is None:
        erst = bytes(pp)
    if r.bereich == be:
        if ring0 is None:
            ring0 = bytes(pp)
        ring1 = bytes(pp)
dbb = auf.bereiche[db][1]
GR = 1272
neu = [i for i in range(200) if ring0[i * GR:(i + 1) * GR] != ring1[i * GR:(i + 1) * GR]]
arten = collections.Counter(ring1[i * GR + 8] for i in neu)
p("A9 Ring: geaenderte Plaetze zwischen erstem und letztem Rahmen:", len(neu), sorted(arten.items()), "Plaetze", (neu[0], neu[-1]) if neu else None, "Zeiten", struct.unpack_from("<i", ring1, neu[0] * GR)[0], struct.unpack_from("<i", ring1, neu[-1] * GR)[0])
doppelt = collections.Counter(ring1[i * GR:i * GR + 40] for i in neu)
p("  doppelte Eintraege (gleiche Zeit, Art, Werte):", sum(1 for v in doppelt.values() if v > 1))
zeit_art = [(struct.unpack_from("<i", ring1, i * GR)[0], ring1[i * GR + 8]) for i in neu]
p("  erste", zeit_art[:6], "letzte", zeit_art[-4:])


def i32(adr):
    return struct.unpack_from("<i", erst, adr - dbb)[0]


def tabelle(name, n, gr=4):
    a = next((a_ for a_, n_ in karte.labels.items() if n_ == name), None)
    if a is None:
        return None
    return [struct.unpack_from({4: "<i", 2: "<h", 1: "<B"}[gr], erst, a + i * gr - dbb)[0] for i in range(n)]


for n, c, g in (("DAT_BarracksUnitCost", 12, 4), ("DAT_EuroUnitResourceCosts", 60, 4), ("DAT_MercenaryUnitCost", 12, 4), ("DAT_MarketResourceCycleArray", 30, 4), ("MarketResourceCycleArray", 30, 4)):
    p(n, tabelle(n, c, g))
kand = [(n, hex(a)) for a, n in karte.labels.items() if re.search(r"UnitCost|RecruitCost|UnitPrice|Merc.*Cost|Arab.*Cost|MarketResourceCycle", n)]
p("Kostentabellen:", kand[:14])
for (g, pf) in sorted(karte.bekannte):
    if re.search(r"UnitCost|MarketResourceCycle|recruitCost|euroUnit.*Cost|nonEuroUnit", pf):
        p("  bekannt", g, pf)
strukt = [(n, s, e, t) for s, e, n, t in karte.strukturen if re.search(r"UnitCost|Market|Recruit", n)]
p("Strukturen:", strukt[:10])

pk = json.load(open(B + ".punkte.json", encoding="utf-8"))["punkte"]
for x in pk:
    if x["nr"] in ("P018", "P016", "P017", "P076", "P027", "P034", "P035", "P036", "P037", "P038", "P039", "P040"):
        p(x["nr"], "MESSEN", x["messen"][:300], "| ERWARTET", x["erwartet"][:120])
        p("    ", [(b["feld"], b["werte"][:12]) for b in x["belege"]][:5])

# KI-Saetze je Figur
A0 = karte.adresse("DAT_AICState", "aics[].AttForceBase")
p("aics AttForceBase", hex(A0[0]), A0[1:])
FELDER = {"P027": (3, ["AttForceBase", "DefTotal", "recruitProbRaidDefault", "TargetChoice"], [10, 40, 0, 0]),
          "P028": (4, ["AttForceBase", "DefTotal", "CowThrowInterval", "TargetChoice"], [40, 100, 8, 2]),
          "P029": (5, ["AttMaxAssassins", "AttForceBase", "maxFood", "TargetChoice"], [5, 50, 50, 0]),
          "P030": (6, ["RaidUnitsBase", "RaidUnitsRandom", "AttMainGroupsCount", "TargetChoice"], [30, 30, 5, 1]),
          "P031": (7, ["SiegeEngine1", "AttMaxEngineers", "AttUnitBackupMax", "TargetChoice"], [0, 0, 120, 2]),
          "P032": (8, ["recruitProbAttackStrong", "AttMaxTunnelers", "recruitProbRaidDefault", "TargetChoice"], [90, 3, 0, 2]),
          "P033": (9, ["AttForceBase", "AttMaxEngineers", "fletcherSetting", "TargetChoice"], [30, 18, -999, 0])}
for nr, (n, fs, soll) in FELDER.items():
    ist = []
    for f in fs:
        a = karte.adresse("DAT_AICState", "aics[]." + f)
        ist.append(i32(a[0] + n * a[2]))
    p(nr, "aics[%d]" % n, dict(zip(fs, ist)), "Export-Grundwert", soll, "gleich" if ist == soll else "ANDERS")

# Einheitennamen
R = r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference"
tx = open(os.path.join(R, "types.json"), encoding="utf-8").read()
i = tx.find("UT_PEASANT")
p("UT_PEASANT an", i, tx[max(0, i - 60):i + 40] if i >= 0 else "")
namen = {}
if i >= 0:
    a = tx.rfind("definition", 0, i)
    b = tx.find('"}', i)
    for n_, w_ in re.findall(r"(UT_\w+)\s*=\s*(\d+)", tx[a:b]):
        namen[int(w_)] = n_
p("Typnamen", len(namen), {k: namen[k] for k in sorted(namen)[:90]})
ty = collections.defaultdict(collections.Counter)
for t, i_, typ, res in H["einh"] + J["einh"]:
    ty[typ][res] += 1
p("resourceToDeposit hoechstens:", {f"{k} {namen.get(k)}": max(v) for k, v in sorted(ty.items()) if max(v) > 0})
tage = collections.Counter(typ for t, i_, typ, res in H["einh"] + J["einh"])

# P149 Statistik
pi = karte.adresse("DAT_GameState", "mapAndTime.populationIndex")
ps = karte.adresse("DAT_GameState", "mapAndTime.playerPopulationStatistics[]")
p("Statistik", hex(pi[0]), pi[1:], hex(ps[0]), ps[1:])
gs = auf.namen.index("DAT_GameState")
gb = auf.bereiche[gs][1]
letzt = None
zeilen = []
pop_a = karte.adresse("DAT_GameState", "playerDataArray[].currentPopulation")
for r, pp, _ in auf.staende():
    if r.bereich == gs:
        i_ = struct.unpack_from("<i", pp, pi[0] - gb)[0]
        if i_ != letzt:
            letzt = i_
            pop = struct.unpack_from("<i", pp, pop_a[0] + pop_a[2] - gb)[0]
            # je Monat eine Zeile mit 9 Spielerspalten? Beide Lesarten zeigen
            z = [struct.unpack_from("<h" if ps[1] == 2 else "<i", pp, ps[0] + ((i_ - 1) * 9 + 1) * ps[1] - gb)[0]] if i_ else [None]
            zeilen.append((r.takt, i_, pop, z[0]))
p("Index, Leute, Statistik[Index-1][1]:", zeilen[:18])
open(os.path.join(HIER, "punkte_rechnung3.txt"), "w", encoding="utf-8").write("\n".join(aus))
