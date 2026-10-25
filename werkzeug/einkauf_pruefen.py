# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer einkauf.py (B-241 Schritt 3). Spielwerte live 25.10. 09:54 (spielwerte_20261025_095417).
Vorher festgelegt:
  1. Feldzug: 2 arab. Schwertkaempfer (A_SWORDSMAN 75) gegen Lord 150.000 + 20 Armbrueste: Fortschritt klein; der Bedarf nennt
     Arten mit Fortschritt > 0 je Gold, Schwertkaempfer (E_SWORD 27) ueber Bogenschuetze (E_ARCHER 22); Gegenprobe: ein Heer, das
     den Lord schon schafft (f0 = 1) -> kein Feldzug-Bedarf
  2. Raid: 6 Holzfaellerhuetten ohne Schuetzen -> Bedarf fuer Sklave (71) und Meuchelmoerder (73) mit 6 Zielen, Wert > 0;
     Gegenprobe: alle 6 brennen -> leer; Reiter nur, wenn Reiterjagd-Ziele > Reiter da (4 > 1 ja, 1 > 1 nein)
  3. Heimwache: 3 feindliche Sklaven an unserer Huette, KEINE eigene Wache -> Bedarf (Arten, die gewinnen); Gegenprobe: 2 eigene
     arab. Schwertkaempfer daheim -> leer (die Wache schafft es)
  4. einkaufen: Gold 1.500, Feuer 8 -> Werbungen am Soeldnerposten, Gold und Bauern werden nicht ueberschritten; Kasernen-Arten
     ohne Kaserne -> Wunsch 'kaserne' (kein Werbe-Befehl); Gegenproben: Feuer 2 -> nichts; Gold 150 (= Rand) -> nichts
  5. Waffen: Kaserne + Waffenlager da, keine Keulen im Lager, Streitkolben lohnt -> Marktkauf RT 21 (und 23), keine Werbung
     in dieser Runde; mit 5 Keulen + 5 Leder im Lager -> Werbung an der Kaserne
Aufruf: python werkzeug/einkauf_pruefen.py (Rueckgabe 0 = gruen)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import einkauf as E
import kaufrechnung as K
import gefahrenschutz as GS
import gefecht

ok = []


def pruefe(nr, text, bed):
    ok.append(bool(bed))
    print("%s %d %s" % ("OK  " if bed else "ROT ", nr, text))


sw = K.spielwerte_laden(os.path.join(K.D, "spielwerte_20261025_095417.json"))
ek = E.Einkaeufer(1, sw, freunde=lambda s: {0, s})


def e(t, b, x, y, l=None):
    return {"typ": t, "besitzer": b, "x": x, "y": y, "leben": l or ek.leben.get(t, 1), "zustand": 1}


def lage_fuer(L, G):
    return GS.Lage(L, G, lambda b_: b_ not in (0, 1), gefecht.FERN_REICH, raten={})


# 1 Feldzug
L = {500: e(55, 3, 300, 100, 150000)}
L.update({600 + i: e(23, 3, 296 + i % 5, 96 + i // 5) for i in range(20)})
L.update({10: e(75, 1, 100, 100), 11: e(75, 1, 100, 101)})
G = {1: {"besitzer": 1, "typ": 8, "x": 100, "y": 100}, 2: {"besitzer": 1, "typ": 41, "x": 90, "y": 100}}
G.update({50 + i: {"besitzer": 3, "typ": 3, "x": 250 + i * 4, "y": 100, "feuer": 0} for i in range(6)})
b1 = {t: (v, n) for t, v, n, _ in ek.bedarf_feldzug(L, G, [10, 11], 3000, 20)}
Lv = dict(L)
Lv.update({20 + i: e(27, 1, 100, 100) for i in range(30)})
b1v = ek.bedarf_feldzug(Lv, G, [20 + i for i in range(30)], 3000, 20)
pruefe(1, "Feldzug: %d Arten, Schwert %s > Bogen %s | 30 Schwerter daheim (schafft es schon): %d" % (
    len(b1), b1.get(27, (0,))[0] and round(b1[27][0]), b1.get(22, (0,))[0] and round(b1[22][0]), len(b1v)),
       len(b1) >= 6 and 27 in b1 and 22 in b1 and b1[27][0] > b1[22][0] and len(b1v) == 0)

# 2 Raid
r2 = {t: (v, n) for t, v, n, _ in ek.bedarf_raid(L, G, lage_fuer(L, G), (100, 100), reiter_ziele=4, reiter_da=1)}
Gb = {n: dict(g, feuer=50) if g.get("besitzer") == 3 else g for n, g in G.items()}
r2b = ek.bedarf_raid(L, Gb, lage_fuer(L, Gb), (100, 100), reiter_ziele=1, reiter_da=1)
pruefe(2, "Raid: Sklave %s, Meuchelmoerder %s, Reiter %s | alles brennt + 1 Reiterziel: %d" % (r2.get(71), r2.get(73), r2.get(74), len(r2b)),
       r2.get(71, (0, 0))[1] == 6 and r2[71][0] > 0 and r2.get(73, (0, 0))[1] == 6 and r2.get(74, (0, 0))[1] == 3 and len(r2b) == 0)

# 3 Heimwache
L3 = {500: e(55, 3, 300, 100, 150000)}
L3.update({700 + i: e(71, 3, 92 + i, 101) for i in range(3)})
G3 = dict(G)
G3[3] = {"besitzer": 1, "typ": 1, "x": 92, "y": 102}
h3 = ek.bedarf_heim(L3, G3, (90, 100))
L3w = dict(L3)
L3w.update({10: e(75, 1, 95, 100), 11: e(75, 1, 95, 101)})
h3w = ek.bedarf_heim(L3w, G3, (90, 100))
pruefe(3, "Heimwache ohne Wache: %d Arten (z. B. %s) | mit 2 arab. Schwertern: %d" % (len(h3), [(t, n) for t, _, n, _ in h3][:3], len(h3w)),
       len(h3) >= 3 and all(v > 0 for _, v, _, _ in h3) and len(h3w) == 0)

# 4 einkaufen
st = {"gold": 1500, "feuer": 8}
w4, m4, er4 = ek.einkaufen(st, L, G, {"keule": 0}, 0, lage=lage_fuer(L, G), heer=[10, 11], reiter_ziele=4, reiter_da=1, heim_ort=(90, 100))
gold4 = sum(n * ek.preise[t]["gold"] for t, n, _ in w4)
bauern4 = sum(n for _, n, _ in w4)
w4f, _, _ = ek.einkaufen({"gold": 1500, "feuer": 2}, L, G, {}, 0, lage=lage_fuer(L, G), heer=[10, 11])
w4g, _, _ = ek.einkaufen({"gold": 150, "feuer": 8}, L, G, {}, 0, lage=lage_fuer(L, G), heer=[10, 11])
pruefe(4, "einkaufen: %s, Gold %d <= 1350, Bauern %d <= 6, alle am Posten %s, Wunsch %s | Feuer 2: %d, Gold 150: %d" % (
    w4, gold4, bauern4, all(g == 1 for _, _, g in w4), sorted(ek.wunsch), len(w4f), len(w4g)),
       w4 and gold4 <= 1350 and bauern4 <= 6 and all(g == 1 for _, _, g in w4) and "kaserne" in ek.wunsch and not w4f and not w4g)

# 5 Waffen
G5 = dict(G)
G5[4] = {"besitzer": 1, "typ": 9, "x": 95, "y": 95}
G5[5] = {"besitzer": 1, "typ": 11, "x": 94, "y": 95}
ek5 = E.Einkaeufer(1, sw, freunde=lambda s: {0, s})
ek5._feldzug = (-99, [(26, 600.0, 4, "Pruefung: Streitkolben lohnt")])      # Feldzug-Bedarf fest vorgegeben
ek5.runde = 0
ek5.FELDZUG_ALLE = 10 ** 9
E.FELDZUG_ALLE, alt = 10 ** 9, E.FELDZUG_ALLE
w5, m5, er5 = ek5.einkaufen({"gold": 1500, "feuer": 8}, L, G5, {"keule": 0, "leder": 0}, 0, lage=None, heer=[10, 11])
w5b, m5b, _ = ek5.einkaufen({"gold": 1500, "feuer": 8}, L, G5, {"keule": 5, "leder": 5}, 0, lage=None, heer=[10, 11])
E.FELDZUG_ALLE = alt
pruefe(5, "ohne Keulen: Markt %s, Werbungen %s | mit 5 Keulen + 5 Leder: Werbungen %s" % (m5, w5, w5b),
       21 in m5 and 23 in m5 and not any(t == 26 for t, _, _ in w5) and any(t == 26 and g == 4 for t, _, g in w5b) and not m5b)

# 6 (Lauf 142712, Daniel 14:33 "Schleuderer stehen nur rum"): Feldzug-Bedarf fuer Schleuderer (72) wird ohne Deckung nicht
#    gekauft, mit deckung_an=True schon; ein Bedarf mit Wert unter dem Preis wird nie gekauft
ek6 = E.Einkaeufer(1, sw, freunde=lambda s: {0, s})
ek6._feldzug = (-99, [(72, 100.0, 4, "Pruefung: Schleuderer"), (75, 50.0, 2, "Pruefung: unter Preis (100)")])
E.FELDZUG_ALLE, alt6 = 10 ** 9, E.FELDZUG_ALLE
w6, _, _ = ek6.einkaufen({"gold": 1500, "feuer": 8}, L, G, {}, 0, lage=None, heer=[10, 11])
w6d, _, _ = ek6.einkaufen({"gold": 1500, "feuer": 8}, L, G, {}, 0, lage=None, heer=[10, 11], deckung_an=True)
E.FELDZUG_ALLE = alt6
pruefe(6, "Schleuderer ohne Deckung: %s | mit Deckung: %s | arab. Schwert unter Preis gekauft: %s" % (
    w6, w6d, any(t == 75 for t, _, _ in w6d)),
       not any(t == 72 for t, _, _ in w6) and any(t == 72 for t, _, _ in w6d) and not any(t == 75 for t, _, _ in w6d))

print("%d von %d gruen" % (sum(ok), len(ok)))
raise SystemExit(0 if all(ok) else 1)
