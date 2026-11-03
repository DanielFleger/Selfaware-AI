# -*- coding: utf-8 -*-
import collections, re, struct
import numpy as np
from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
k = Feldkarte.laden(feldliste=FELDLISTE)
basis = "data/research/auge_plan/laeufe/lauf_k_20261102_234952"
roh = open(r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference\types.json", encoding="utf-8").read().replace("\n", " ").replace("\t", " ")
WAND = {int(z) for n, z in re.findall(r"(M_MAPPER_[A-Z0-9_]+): (\d+)", roh) if n in ("M_MAPPER_WALL", "M_MAPPER_WOODWALL", "M_MAPPER_CRENAL", "M_MAPPER_CRENAL2", "M_MAPPER_MOAT", "M_MAPPER_PITCH_DITCH")}
print("Wandarten", WAND)
add, n = [], 0
kum = []
for y in range(400):
    w = 2 * (y + 1) if y < 200 else 2 * (400 - y)
    add.append(n - (199 - y if y < 200 else y - 200))
    n += w
    kum.append(n)
kum = np.array(kum)
def xy(o):
    y = int(np.searchsorted(kum, o, side="right"))
    return o - add[y], y
SP = k.adresse("DAT_GameState", "playerDataArray[].aivID")
AV = {f: k.adresse("DAT_AIVState", "aivs[]." + f) for f in ("totalSteps", "keepXOffset", "keepYOffset", "wallLocationsArrayIndex")}
L = k.adresse("DAT_AIVState", "aivs[].locationsArray[]")
S = k.adresse("DAT_AIVState", "aivs[].aivBuildingSteps[]"); F = {f: k.adresse("DAT_AIVState", "aivs[].aivBuildingSteps[]." + f) for f in ("buildStatus", "location", "buildingType", "quantity")}
a = aw.Aufzeichnung(basis + ".auge")
st, bas = {}, {b[0]: b[1] for b in a.bereiche}
for r, p, _ in a.staende():
    st[a.namen[r.bereich]] = p
    if len(st) == len(a.namen) and r.takt >= 110 and a.namen[r.bereich] == "DAT_UnitsState":
        ad, ab = st["DAT_AIVState"], bas["DAT_AIVState"]
        gs, gb = st["DAT_GameState"], bas["DAT_GameState"]
        ges = collections.Counter()
        for sp in range(1, 9):
            i = struct.unpack_from("<i", gs, SP[0] + sp * SP[2] - gb)[0]
            w = {f: struct.unpack_from("<i", ad, AV[f][0] + i * AV[f][2] - ab)[0] for f in AV}
            c = collections.Counter()
            for s in range(1, w["totalSteps"] + 1):
                wert = {f: struct.unpack_from({1: "<b", 2: "<h", 4: "<i"}[F[f][1]], ad, F[f][0] + i * F[f][2] + s * S[1] - ab)[0] for f in F}
                if wert["buildStatus"] != 1:
                    c["abgeschaltet"] += 1
                    continue
                if wert["buildingType"] in WAND:
                    c["Wand-Schritt"] += 1
                    continue
                x, y = xy(wert["location"])
                c["Bau im Feld" if w["keepXOffset"] <= x < w["keepXOffset"] + 100 and w["keepYOffset"] <= y < w["keepYOffset"] + 100 else "Bau ausserhalb"] += 1
            n_w = w["wallLocationsArrayIndex"]
            for j in range(min(n_w, L[3])):
                o = struct.unpack_from("<i", ad, L[0] + i * L[2] + j * L[1] - ab)[0]
                x, y = xy(o)
                c["Wandfeld im Feld" if w["keepXOffset"] <= x < w["keepXOffset"] + 100 and w["keepYOffset"] <= y < w["keepYOffset"] + 100 else "Wandfeld ausserhalb"] += 1
            print("Spieler", sp, dict(c))
            ges.update(c)
        print("Summe", dict(ges))
        break
