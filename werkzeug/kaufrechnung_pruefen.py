# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer kaufrechnung.py (B-241). Vorher festgelegt (Spielwerte live 25.10. 09:21, spielwerte_20261025_092140):
  1. Preise aus den Spielwerten: Assassine 70 (Soeldner), Bogenschuetze 10 + Bogen 180/5 = 46, Ritter 120 + Schwert 350/5 +
     Eisenruestung 400/5 = 270 und braucht den Stall; Lord (55) ist nicht kaufbar
  2. Kalibrierung aus den Duellen: Nahkampf-Faktor Streitkolben 0,9-1,3 (Median der Paare), Assassine 0,9-1,1; Schussrate Bogen
     0,005-0,015 je Takt; eine Art ohne Duelle (Ritter 28 hat < 3 Paare? -> pruefen ueber "gemessen")
  3. Schadenstabelle: gemessenes Paar bleibt die Messung (26->55 = Duellwert), ungemessenes Paar = Tabelle x Faktor (26->28 steht
     nicht in den Duellen? dann 45 x Faktor), Lord-Leben 150000
  4. bewerte: Gold 0 -> leer; ohne Feinde -> alle Sieg; feuer=3 -> hoechstens 3 je Art; gegen 10 Bogen + 10 Speere mit 2000 Gold
     steht ein Sieg oben; Gegenprobe: 50 Gold gegen 40 Schwertkaempfer -> kein Sieg in der Liste
Aufruf: python werkzeug/kaufrechnung_pruefen.py (Rueckgabe 0 = gruen)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kaufrechnung as K
import gefecht

ok = []


def pruefe(nr, text, bed):
    ok.append(bool(bed))
    print("%s %d %s" % ("OK  " if bed else "ROT ", nr, text))


sw = K.spielwerte_laden(os.path.join(K.D, "spielwerte_20261025_092140.json"))
pr = K.preise(sw)
pruefe(1, "Preise: Assassine %s, Bogen %s, Ritter %s Stall %s, Lord kaufbar %s" % (
    pr[73]["gold"], pr[22]["gold"], pr[28]["gold"], pr[28]["stall"], 55 in pr),
       pr[73]["gold"] == 70 and abs(pr[22]["gold"] - 46) < 1e-9 and abs(pr[28]["gold"] - 270) < 1e-9 and pr[28]["stall"] and 55 not in pr)

nah, fern, gemessen = K.kalibrierung(sw)
pruefe(2, "Kalibrierung: Streitkolben %.2f, Assassine %.2f, Bogen-Rate %.4f, gemessene Arten %d" % (
    nah.get(26, 0), nah.get(73, 0), fern.get(22, 0), len(gemessen)),
       0.9 <= nah.get(26, 0) <= 1.3 and 0.9 <= nah.get(73, 0) <= 1.1 and 0.005 <= fern.get(22, 0) <= 0.015 and len(gemessen) >= 8)

S, F, LEB, kal = K.schadenstabelle(sw)
S0, _, _ = gefecht.tabelle()
md = K._w(sw, "einheit.melee_damage")
unge = next((z for z in range(80) if z not in S0.get(26, {}) and md[26][z] > 0 and K._w(sw, "einheit.base_hp")[z] > 0), None)
pruefe(3, "Schadenstabelle: 26->55 %.1f (Duell %.1f), ungemessen 26->%s = %.1f (Tabelle %s x %.2f), Lord-Leben %s" % (
    S[26][55], S0[26][55], unge, S[26].get(unge, -1), md[26][unge] if unge is not None else None, nah[26], LEB.get(55)),
       abs(S[26][55] - S0[26][55]) < 1e-9 and unge is not None and abs(S[26][unge] - md[26][unge] * nah[26]) < 1e-9 and LEB.get(55) == 150000)

feinde = [{"typ": 22, "n": 10}, {"typ": 24, "n": 10}]
leer = K.bewerte(sw, 0, feinde)
ohne = K.bewerte(sw, 1000, [])
feuer3 = K.bewerte(sw, 5000, feinde, feuer=3)
r2000 = K.bewerte(sw, 2000, feinde)
arm = K.bewerte(sw, 50, [{"typ": 27, "n": 40}])
pruefe(4, "bewerte: Gold 0 -> %d; ohne Feinde alle Sieg %s; feuer 3 -> max %d; 2000 Gold oben %s (%s); 50 Gold gegen 40 Schwerter Siege %d" % (
    len(leer), all(r["sieg"] for r in ohne) and len(ohne) > 0, max(r["n"] for r in feuer3), r2000[0]["sieg"], r2000[0]["name"][:20],
    sum(1 for r in arm if r["sieg"])),
       len(leer) == 0 and ohne and all(r["sieg"] for r in ohne) and max(r["n"] for r in feuer3) <= 3 and r2000[0]["sieg"]
       and sum(1 for r in arm if r["sieg"]) == 0)

print("%d von %d gruen" % (sum(ok), len(ok)))
raise SystemExit(0 if all(ok) else 1)
