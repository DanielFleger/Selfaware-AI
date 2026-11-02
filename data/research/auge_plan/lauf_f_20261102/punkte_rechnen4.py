# -*- coding: utf-8 -*-
"""B-142: Vierter Teil der Nachrechnung von Lauf F: restliche Tabellen, Baukosten, Pech und Stein beim Bauen, Anwerbekosten, Traeger je Beruf. Ausgabe: punkte_rechnung4.txt."""
import bisect
import collections
import json
import os
import pickle
import re
import struct

from selfaware.game.ucp import bauen
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
    print(s[:1700])


auf = aw.Aufzeichnung(B + ".auge")
db, gs = auf.namen.index("datenblock"), auf.namen.index("DAT_GameState")
erst = None
letzt_g = None
for r, pp, _ in auf.staende():
    if r.bereich == db and erst is None:
        erst = bytes(pp)
    if r.bereich == gs:
        letzt_g = bytes(pp)
dbb = auf.bereiche[db][1]
gb = auf.bereiche[gs][1]


def lies(adr, n=1, gr=4):
    f = {4: "<i", 2: "<h", 1: "<B"}[gr]
    return [struct.unpack_from(f, erst, adr + i * gr - dbb)[0] for i in range(n)]


def marke(name, n, gr=4):
    a = next((a_ for a_, n_ in karte.labels.items() if n_ == name), None)
    return lies(a, n, gr) if a else None


for name, n, gr in (("DAT_RangedAndArmoredUnits", 7, 4), ("RangedAndArmoredUnits", 7, 4), ("DAT_DefenseTribesUnitTypeArray", 20, 4), ("DefenseTribesUnitTypeArray", 20, 4), ("DAT_SiegeEngineTypeRequiredEngineers", 6, 4), ("SiegeEngineTypeRequiredEngineers", 6, 4),
                    ("DAT_SiegeEngineUnitType", 6, 4), ("SiegeEngineUnitType", 6, 4), ("DAT_BuildingSizeIndexMapping", 24, 4), ("DAT_NonEuroUnitCost", 24, 4), ("DAT_XYOffsetsInAllDirections", 16, 4)):
    w = marke(name, n, gr)
    if w is not None:
        p(name, w)
kand = [(n, hex(a)) for a, n in karte.labels.items() if re.search(r"RangedAndArmored|DefenseTribes|SiegeEngineType|SiegeEngineUnit|BuildingSizeIndex|NonEuro", n)]
p("Marken:", kand[:12])
bek = [(g, f) for g, f in karte.bekannte if re.search(r"RangedAndArmored|DefenseTribes|SiegeEngineType|SiegeEngineUnit|BuildingSizeIndex|euroRecruitable|mercRecruitable|copyOfBuyAndSales|someCount44|storedPopularityPercent", f)]
p("In der Liste:", bek[:14])
for g, f in bek:
    try:
        a = karte.adresse(g, f)
        p(" ", f, hex(a[0]), a[1:], lies(a[0], min(a[3] or 1, 14), a[1] if a[1] in (1, 2, 4) else 4) if a[2] in (0, a[1]) else [lies(a[0] + i * a[2], 1, a[1] if a[1] in (1, 2, 4) else 4)[0] for i in range(min(a[3] or 1, 14))])
    except Exception as e:  # noqa: BLE001
        p(" ", f, "Fehler", repr(e)[:100])

# P023: Kopie der Preise gleich den Preisen?
ba = karte.adresse("DAT_GameState", "mapAndTime.buyAndSalesPriceArray[].buyPrice")
sa = karte.adresse("DAT_GameState", "mapAndTime.buyAndSalesPriceArray[].salesPrice")
cb = karte.adresse("DAT_GameState", "mapAndTime.copyOfBuyAndSalesPrice[].buyPrice")
cs = karte.adresse("DAT_GameState", "mapAndTime.copyOfBuyAndSalesPrice[].salesPrice")
pk = [lies(ba[0] + i * ba[2])[0] for i in range(25)], [lies(sa[0] + i * sa[2])[0] for i in range(25)]
ck = [lies(cb[0] + i * cb[2])[0] for i in range(25)], [lies(cs[0] + i * cs[2])[0] for i in range(25)]
p("P023 Kopie gleich:", pk == ck, ck[0][:8])

# KI-Saetze P034-P040
FELDER = {"P034": (10, ["AttForceBase", "DefTotal", "SiegeEngine1"], [10, 20, 0]), "P035": (11, ["AttForceBase", "AttCoordinationPreference", "HarassingSiegeEngine1"], [40, 90, 358]), "P036": (12, ["maxFarms", "RecruitInterval", "TargetChoice"], [16, 0, 0]),
          "P037": (13, ["AttMaxAssassins", "HarassingSiegeEnginesMax", "TargetChoice"], [40, 0, 2]), "P038": (14, ["AttForceBase", "CowThrowInterval", "AttMaxAssassins"], [50, 6, 10]), "P039": (15, ["AttForceBase", "criticalPopularity", "TargetChoice"], [10, 4000, 1]),
          "P040": (16, ["AttForceBase", "taxesMax", "AttUnitMain1"], [50, 12, 37])}
for nr, (n, fs, soll) in FELDER.items():
    ist = []
    for f in fs:
        a = karte.adresse("DAT_AICState", "aics[]." + f)
        ist.append(lies(a[0] + n * a[2])[0])
    p(nr, "aics[%d]" % n, dict(zip(fs, ist)), "Export", soll, "gleich" if ist == soll else "ANDERS")

# Baukosten
for f in [x for g, x in karte.bekannte if x.startswith("buildingCosts") or "buildingCosts" in x][:10]:
    p("Kostenfeld", f)
for g, f in karte.bekannte:
    if f.endswith("buildingCosts[]"):
        a = karte.adresse(g, f)
        p("buildingCosts", g, hex(a[0]), a[1:])
        for t in (12, 62):
            p("  Art", t, bauen.NACH_TYP[t]["name"], lies(a[0] + t * a[1], a[1] // 4))
# Anwerben: Kosten
bc = marke("DAT_BarracksUnitCost", 12)
ne = marke("DAT_NonEuroUnitCost", 80)
p("Kaserne je Typ 22..33:", bc)
p("NonEuro:", ne)

# Einheitennamen
R = r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference"
tx = open(os.path.join(R, "types.json"), encoding="utf-8").read()
namen = {int(w): n for n, w in re.findall(r"\b(UT_\w+): (\d+)", tx)}
p("Typnamen", len(namen), {k: namen[k] for k in (1, 3, 4, 5, 6, 8, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 24, 32, 33, 34, 35, 36, 52, 55, 63, 64, 62, 44, 47) if k in namen})
ty = collections.defaultdict(collections.Counter)
for t, i_, typ, res in H["einh"] + J["einh"]:
    ty[typ][res] += 1
p("Hoechstladung je Beruf:", {f"{k} {namen.get(k)}": max(v) for k, v in sorted(ty.items()) if max(v) > 0})

# Pech und Stein beim Bauen
W = H["waren"]
LOG = r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme Instanz2\ucp3.log"
ereignis = []
with open(LOG, encoding="utf-8", errors="replace") as f:
    for z in f:
        if not ("2026-11-02 21:42:40" <= z[:19] <= "2026-11-02 21:43:40"):
            continue
        m = re.search(r"BAUE Tick (\d+): Mapper (\d+)", z)
        if m:
            ereignis.append((int(m.group(1)), "Mapper" + m.group(2)))
        m = re.search(r"SPIELBEFEHL Tick (\d+): Nr (\d+) Werte \[([^\]]*)\]", z)
        if m and int(m.group(2)) in (25, 21):
            ereignis.append((int(m.group(1)), "Nr" + m.group(2) + " " + m.group(3)))
        m = re.search(r"ABREISSEN Tick (\d+): Nr (\d+)", z)
        if m:
            ereignis.append((int(m.group(1)), "Abriss" + m.group(2)))
p("Pechgraben-Befehle:", [e for e in ereignis if e[1] == "Mapper" + str(bauen.NACH_TYP[68]["mapper"])], "Mauer:", [e for e in ereignis if e[1].startswith("Nr")], "Abriss:", [e for e in ereignis if e[1].startswith("Abriss")])
for name, w, a_, b_ in (("Pech", 7, 6300, 6700), ("Stein", 4, 16130, 16175), ("Holz", 2, 16380, 16420), ("Holz", 2, 16420, 16470)):
    p(name, [(t, x[w], x[15]) for t, x in W if a_ <= t <= b_][:14])

# P149
pi = karte.adresse("DAT_GameState", "mapAndTime.populationIndex")[0]
ps = karte.adresse("DAT_GameState", "mapAndTime.playerPopulationStatistics[]")
idx = struct.unpack_from("<i", letzt_g, pi - gb)[0]
reihe = [struct.unpack_from("<i", letzt_g, ps[0] + 1 * 600 + i * 4 - gb)[0] for i in range(max(0, idx - 12), idx)] if False else None
for sc, gr in ((600, 4), (600, 2), (240, 4), (2, 2)):
    try:
        z = [struct.unpack_from({4: "<i", 2: "<h"}[gr], letzt_g, ps[0] + 1 * sc + i * gr - gb)[0] for i in range(0, min(idx, 40))]
        p("Statistik Schritt", sc, "gr", gr, "Index", idx, z[:40])
    except Exception as e:  # noqa: BLE001
        p("Statistik", repr(e)[:80])
p("Felder +0x2c8 im Bereich:", [(f, a) for f, a in [(x, 0) for g, x in karte.bekannte if "field201_0x2c8" in x]][:3])
open(os.path.join(HIER, "punkte_rechnung4.txt"), "w", encoding="utf-8").write("\n".join(aus))
