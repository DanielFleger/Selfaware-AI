# -*- coding: utf-8 -*-
"""B-142 Lauf K: Nachtrag zu punkte_start.py: Tabellen, die die Feldkarte zu kurz kennt, und die Namen aus dem Textspeicher des Spiels (die Liga ersetzt Texte, cr.tex allein genuegt nicht)."""
import struct
import sys

from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

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
D, BD = erste["datenblock"][1], erste["datenblock"][2]
G, BG = erste["DAT_GameState"][1], erste["DAT_GameState"][2]


def d_i(adr, n=1, f="i"):
    return struct.unpack_from(f"<{n}{f}", D, adr - BD)


intens = k.adresse("DAT_GameSynchronyState", "skirmishGameIntensityType")[0]
vort = k.adresse("DAT_GameSynchronyState", "skirmishCurrentAdvantageBalance")[0]
I, V = d_i(intens)[0], d_i(vort)[0]
print("Intensitaet", I, "Vorteil-Stufe", V)
tb = k.adresse("DAT_RenderingDefinedData", "field451_0x53bb4[]")[0]
print("field451 ab 0..60", d_i(tb, 60))
print("Erwartet KI: Tabelle[(V+I*5)*2+0xD] =", d_i(tb + ((V + I * 5) * 2 + 0xD) * 4)[0], " Mensch +0xC =", d_i(tb + ((V + I * 5) * 2 + 0xC) * 4)[0])
print("Startgold 0x005C2A68", d_i(0x005C2A68, 6))
sg = k.adresse("DAT_GameState", "mapAndTime.startGoods[]")[0]
print("mapAndTime.startGoods", struct.unpack_from("<25i", G, sg - BG))
st = k.adresse("DAT_RenderingDefinedData", "DAT_StartingTroops[]")[0]
print("Faktor KI: StartingTroops - 4 + (V + 0x35) * 4 =", d_i(st - 4 + (V + 0x35) * 4)[0], " Tabelle dort", d_i(st - 4 + 0x35 * 4, 8), " Mensch +0x2F", d_i(st - 4 + (V + 0x2F) * 4)[0])
try:
    sp = k.adresse("DAT_GameState", "mapAndTime.startingPopularity")[0]
    print("startingPopularity", struct.unpack_from("<i", G, sp - BG)[0])
except Exception as e:
    print("startingPopularity", e)
for g, f in (("DAT_GameSynchronyState", "aiVariationArray[]"), ("DAT_GameSynchronyState", "DAT_AIVariationArray[]"), ("DAT_GameSynchronyState", "currentAIVariationArray[]")):
    try:
        x = k.adresse(g, f)
        print(f, x, d_i(x[0], 9))
    except Exception:
        pass
print("logik.lua aiVar? Felder mit ariation:", [n for (g, n) in k.bekannte if "ariation" in n and "Synchrony" in g][:8])
for f in ("textOffsets", "textOffsets[]", "textStart", "textStart[]"):
    try:
        print(f, k.adresse("DAT_TextManagerObject", f))
    except Exception as e:
        print(f, "nein", str(e)[:50])
