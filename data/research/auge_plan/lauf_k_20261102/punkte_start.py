# -*- coding: utf-8 -*-
"""B-142 Lauf K: Punkte, die sich einmal am Start ablesen lassen (P247, P248, P249, P255, P262, P280). Quelle: Datenblock im ersten Rahmen, Takt 0.

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/punkte_start.py <basis>
"""
import struct
import sys

from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.experiments import auge_lauf_f as lf

basis = sys.argv[1]
k = Feldkarte.laden(feldliste=FELDLISTE)
a = aw.Aufzeichnung(basis + ".auge")
erste = {}
for r, p, _ in a.staende():
    n = a.namen[r.bereich]
    if n not in erste:
        erste[n] = (r.takt, bytes(p), a.bereiche[r.bereich][1])
    if len(erste) == len(a.namen):
        break
print("Takte", {n: v[0] for n, v in erste.items()})
D, BD = erste["datenblock"][1], erste["datenblock"][2]


def d_i(adr, n=1, f="i"):
    return struct.unpack_from(f"<{n}{f}", D, adr - BD)


def ad(g, f):
    return k.adresse(g, f)


# cr.tex wie loadCRTex 0x00473870: 0x410 Bytes Anfaenge je Gruppe (in Zeichen), dann die Texte, je Gruppe durch 0 getrennt
roh = open(lf.ordner(2) + "/cr.tex", "rb").read()
gruppen = struct.unpack_from("<260I", roh, 0)
texte = roh[0x410:].decode("utf-16-le", errors="ignore")


def text(gruppe, i):
    return texte[gruppen[gruppe]:gruppen[gruppe + 1]].split("\x00")[i]


print("Probe Text: Kartennamen Gruppe 219, Eintrag 39:", repr(text(219, 39)), "Nachbarn", [text(219, x) for x in (31, 131, 133, 17, 63, 143)])
print("--- P247 SetAIPlayerNickNames")
ai = d_i(ad("DAT_GameSynchronyState", "currentAIArray[]")[0], 9)
full = d_i(ad("DAT_GameSynchronyState", "currentPlayerFullIDArray[]")[0], 9)
try:
    var = d_i(ad("DAT_GameSynchronyState", "aiVariationArray[]")[0], 9)
except Exception:
    var = None
print("KI", ai, "Eintrag", full, "Variante", var)
nam = ad("DAT_GameSynchronyState", "DAT_PlayerNames[]")[0]
namen = [D[nam - BD + i * 250:nam - BD + (i + 1) * 250].split(b"\0")[0].decode("latin-1") for i in range(9)]
print("Namen", namen)
print("Erwartet", [text(79, 0x67 + 8 * ai[i] + (var[i] if var else 0)) if ai[i] else "" for i in range(9)])
print("Mit Typ-1", [text(79, 0x67 + 8 * (ai[i] - 1) + (var[i] if var else 0)) if ai[i] else "" for i in range(9)])
print("--- P248 LaunchSkirmishGame")
fair = d_i(0x01A24A4C)[0]
start = d_i(0x01A245A4)[0]
print("fairness 0x01A24A4C", fair, "startLevels 0x01A245A4", start, "Stufe NoRush", d_i(0x01A26A2C)[0])
sg = ad("DAT_RenderingDefinedData", "DAT_StartGoods[]")
print("Adresse Tabelle StartGoods", sg)
print("StartGoods", [list(d_i(sg[0] + i * sg[1], 25)) for i in range(3)])
st = ad("DAT_RenderingDefinedData", "DAT_StartingTroops[]")
print("StartingTroops Zeilen", st)
zeilen = [d_i(st[0] + i * st[1], st[1] // 4) for i in range(st[3])]
for i, z in enumerate(zeilen):
    print("  Zeile", i, [x for x in z])
nr = ad("DAT_RenderingDefinedData", "DAT_NoRushTicks[]")
print("NoRushTicks", d_i(nr[0], 8))
gs = erste["DAT_GameState"]
G, BG = gs[1], gs[2]
goods = ad("DAT_GameState", "mapAndTime.startGoods[]") if False else None
for name in ("mapAndTime.startGoods[]", "mapAndTime.startingTroops[]", "mapAndTime.totalNoRushTicks", "mapAndTime.noRushTicksLeftUnk"):
    try:
        x = ad("DAT_GameState", name)
        print(name, x, list(struct.unpack_from(f"<{min(x[1] // 4 or 1, 25)}i", G, x[0] - BG)))
    except Exception as e:
        print(name, "kein Feld", str(e)[:60])
tr = ad("DAT_GameState", "mapAndTime.startingTroops[]")
for p_ in range(8):
    print("  startingTroops", p_, list(struct.unpack_from("<20i", G, tr[0] + p_ * tr[1] - BG)))
print("--- P249 resetVarious")
sr = ad("DAT_GameState", "playerDataArray[].startResources[]")
cr = ad("DAT_GameState", "playerDataArray[].currentResources[]")
pop = ad("DAT_GameState", "playerDataArray[].popularity")
tb = ad("DAT_RenderingDefinedData", "field451_0x53bb4[]")
print("Tabelle field451", d_i(tb[0], tb[3]))
for sp in range(1, 9):
    print("  Spieler", sp, "startResources[15]", struct.unpack_from("<i", G, sr[0] + sp * sr[2] + 15 * 4 - BG)[0], "Gold", struct.unpack_from("<i", G, cr[0] + sp * cr[2] + 15 * 4 - BG)[0], "popularity", struct.unpack_from("<i", G, pop[0] + sp * pop[2] - BG)[0])
for name in ("startingPopularity",):
    for g in ("DAT_GameSynchronyState", "DAT_GameState", "DAT_GameCore"):
        try:
            x = ad(g, name)
            print(name, g, x)
        except Exception:
            pass
print("--- P255 processSingleplayerEvents")
print("currentGameMode", d_i(0x0191DD80)[0], "gameMode_2", d_i(0x01FE7D78)[0], "eventsCount", d_i(0x01653E04)[0])
print("--- P262 selectBuildingFromAListOfBuildingTypes")
for nm in ("BuildingTargetPrioritySet1[]", "BuildingTargetPrioritySet2[]", "BuildingTargetPrioritySet3[]"):
    x = ad("DAT_SkirmishDefinedData", nm)
    print(nm, d_i(x[0], x[3]))
print("--- P280 setKeepOffsetAndOrientation")
av = erste["DAT_AIVState"]
for f in ("aivs[].keepOrientation", "aivs[].keepX", "aivs[].keepY", "aivs[].playerID", "aivs[].keepXOffset", "aivs[].keepYOffset"):
    try:
        x = ad("DAT_AIVState", f)
        print(f, x[2], x[3], [struct.unpack_from("<i", av[1], x[0] + i * x[2] - av[2])[0] for i in range(x[3])])
    except Exception as e:
        print(f, "kein Feld", str(e)[:70])
kp = ad("DAT_GameState", "playerDataArray[].keep") if False else None
