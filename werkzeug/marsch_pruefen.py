# -*- coding: utf-8 -*-
"""B-284 Marsch in Gruppen + Spaeher-Sperre (Daniel 28.10. 00:57/01:02). Soll vorher festgelegt:
  1. Umweg (240,60) -> (290,80) -> Lord; 12 Mann am ersten Wegpunkt, 18 Mann 40 Felder dahinter (in der Kolonne) -> der
     Wegpunkt bleibt (weg_i 0), Meldung MARSCH SAMMELN, die Laufbefehle gehen weiter an (240,60)
  2. alle 30 am ersten Wegpunkt -> naechster Wegpunkt (weg_i 1)
  3. wie 1, aber MARSCH_FRIST ist um -> weiter, auch ohne die Nachzuegler
  4. wer daheim steht (ueber MARSCH_R vom Wegpunkt), haelt nicht auf (1019i)
  6. (B-285) Reiter ohne Ziel mit vertretbarem Risiko, Arbeiter 60 Felder weg -> REITER LAUERT, Laufbefehl
  7. (B-285) dasselbe 2 Felder vor dem Arbeiter -> REITER STEHT mit Grund
  5. Spaeher: kein Reiter da, der letzte starb vor 500 Takten -> kein Kauf, Grund "KEIN Spaeher"; vor 5.000 Takten -> Spaeher
Aufruf: python marsch_pruefen.py"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import feldzug as F
import raids as R
from feldzug_pruefen import lage, Befehle
heim_ort = (80, 260)                  # wie feldzug_pruefen (heim)


def marsch(hinten, t2, hinten_ort=(200, 40)):
    f = F.Feldzug(1, heim_ort, lord_schutz_bis=9600, n=30)
    f.wegplaner = lambda L_, G_, s, z: [(240, 60), (290, 80), z]
    f.schritt({"t": 12000}, *lage(10, heim_ort), Befehle())
    L, G = lage(30, f.punkt)
    f.schritt({"t": 12050}, L, G, Befehle())
    L, G = lage(30, (240, 60))
    for i, n in enumerate(sorted(n for n, e in L.items() if e["besitzer"] == 1 and e["typ"] != 55)[:hinten]):
        L[n].update(x=hinten_ort[0] + i % 3, y=hinten_ort[1] + i // 6)
    b = Befehle()
    aus = f.schritt({"t": t2}, L, G, b)
    lauf = [tuple(x["angriff"]["lauf"]) for x in b.liste if "lauf" in x.get("angriff", {})]
    return f, aus or [], lauf


def main():
    ok = []

    def pruefe(nr, text, bed):
        ok.append(bool(bed))
        print("%s %d %s" % ("OK  " if bed else "ROT ", nr, text))
    f1, a1, l1 = marsch(18, 12100)
    pruefe(1, "12 vorn, 18 in der Kolonne dahinter: weg_i %d, Meldung %s, Lauf %s" % (
        f1.weg_i, [z[:50] for z in a1 if "MARSCH" in z][:1], l1[:2]),
        f1.weg_i == 0 and any("MARSCH SAMMELN" in z for z in a1))
    f2, a2, l2 = marsch(0, 12100)
    pruefe(2, "alle 30 am Wegpunkt: weg_i %d" % f2.weg_i, f2.weg_i >= 1)
    f3 = F.Feldzug(1, heim_ort, lord_schutz_bis=9600, n=30)
    f3, a3, _ = marsch(18, 12100)
    L3, G3 = lage(30, (240, 60))
    for i, n in enumerate(sorted(n for n, e in L3.items() if e["besitzer"] == 1 and e["typ"] != 55)[:18]):
        L3[n].update(x=200 + i % 3, y=40 + i // 6)
    f3.schritt({"t": 12100 + F.Feldzug.MARSCH_FRIST + 10}, L3, G3, Befehle())
    pruefe(3, "Frist um: weg_i %d" % f3.weg_i, f3.weg_i >= 1)
    f4, a4, _ = marsch(18, 12100, hinten_ort=heim_ort)
    pruefe(4, "18 daheim (%s, ueber MARSCH_R): weg_i %d" % (heim_ort, f4.weg_i), f4.weg_i >= 1)
    g5, g6 = [], []
    w5 = R.werbung(400, 10, 5, 0, reiter_ziele=None, gruende=g5, reiter_tot_vor=500)
    w6 = R.werbung(400, 10, 5, 0, reiter_ziele=None, gruende=g6, reiter_tot_vor=5000)
    pruefe(5, "Spaeher-Sperre: vor 500 Takten %s %s, vor 5.000 %s" % (w5, g5[:1], w6),
           w5 == [] and any("KEIN Spaeher" in g for g in g5) and w6 == [(R.PFERDEBOGEN, 1)])
    # 6/7 (B-285) Reiter ohne vertretbares Ziel: lauern statt stehen, mit Grund
    import gefahrenschutz as GS
    from raids_pruefen import RATEN, einheit as einh
    alt_bewerte = GS.bewerte
    GS.bewerte = lambda *a, **k: []
    try:
        rj = R.Reiterjagd(1, raten=RATEN)
        b6 = Befehle()
        a6 = rj.schritt({20: einh(74, 1, 100, 100), 700: einh(3, 2, 160, 100)}, {}, b6)
        rj7 = R.Reiterjagd(1, raten=RATEN)
        a7 = rj7.schritt({20: einh(74, 1, 158, 100), 700: einh(3, 2, 160, 100)}, {}, Befehle())
    finally:
        GS.bewerte = alt_bewerte
    pruefe(6, "kein Ziel, Arbeiter 60 Felder weg: %s" % [z[:60] for z in a6 if "LAUERT" in z][:1],
           any("REITER LAUERT 20" in z for z in a6) and any("lauf" in x.get("angriff", {}) for x in b6.liste))
    pruefe(7, "kein Ziel, schon 2 Felder davor: %s" % [z[:60] for z in a7 if "REITER" in z][:1], any("REITER STEHT 20" in z for z in a7))
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return all(ok)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
