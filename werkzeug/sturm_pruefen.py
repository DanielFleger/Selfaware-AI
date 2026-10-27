# -*- coding: utf-8 -*-
"""B-263 gebuendelter Sturm + B-216 Abbruch ohne Spiel pruefen (Feldzug._sturm). Soll je Fall vorher festgelegt.
Lage: Lord (Spieler 2) bei (300, 100), unser Heer (10 Streitkolben) bei (250, 100), 6 feindliche Bogenschuetzen bei
(310, 98-103), Reichweite 44 -> sie decken die Kandidaten 20/25/30 Felder vor dem Lord ab; 35 Felder ist der naechste sichere.
Aufruf: python sturm_pruefen.py"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import feldzug as F
import parteien

parteien.freunde_von = F.freunde_von = lambda sp: {sp}
LP, HEER = (300, 100), (250, 100)


class Befehle:
    def __init__(self):
        self.liste = []

    def __call__(self, b, *a, **k):
        self.liste.append(b)
        return []


def einheit(typ, sp, x, y, leben=25000, zustand=101):
    return {"typ": typ, "besitzer": sp, "x": x, "y": y, "leben": leben, "zustand": zustand}


def lage(positionen, schuetzen=True):
    L = {500: einheit(55, 2, LP[0], LP[1], 150000, 0)}
    if schuetzen:
        for i in range(6):
            L[600 + i] = einheit(22, 2, 310, 98 + i, 3500, 0)
    for i, p in enumerate(positionen):
        L[10 + i] = einheit(26, 1, p[0], p[1])
    return L


def neu():
    f = F.Feldzug(1, HEER, n=10)
    f.ziel, f.wegtest, f.runde = 500, None, 0
    return f


def schritt(f, L, t):
    b, aus = Befehle(), []
    erg = f._sturm(L, [n for n in L if L[n]["besitzer"] == 1], LP, HEER, t, b, {}, aus)
    return erg, b.liste, aus


if __name__ == "__main__":
    faelle = []
    # 1 alle weit weg: sammeln, nicht los; Sammelpunkt = naechster ausser Reichweite der Bogen (35 Felder), auf unserer Seite
    f = neu()
    L = lage([HEER] * 10)
    erg, bef, aus = schritt(f, L, 10000)
    pkt = f.sturm["punkt"] if f.sturm else None
    faelle.append(("weit weg: sammeln (kein Sturm), Laufbefehl fuer alle 10 zum Sammelpunkt %s" % (pkt,),
                   erg is False and any(len(b["angriff"]["einheiten"]) == 10 and b["angriff"].get("lauf") == list(pkt) for b in bef)))
    faelle.append(("Sammelpunkt = naechster sicherer Punkt (265, 100): 35 Felder vor dem Lord, 0 Schuetzen in Reichweite",
                   pkt == (265, 100) and f.sturm["schuetzen"] == 0))
    # 2 die Haelfte ist da: Sturm los
    L2 = lage([pkt] * 5 + [HEER] * 5)
    erg2, _b, aus2 = schritt(f, L2, 10100)
    faelle.append(("5 von 10 am Sammelpunkt: STURM LOS", erg2 is True and any("STURM LOS" in m for m in aus2)))
    # 3 Abbruch: Lord lebt nach der Frist noch -> zurueck zum Sammeln
    erg3, _b, aus3 = schritt(f, L2, 10100 + f.sturm["frist"] + 1)
    faelle.append(("Lord lebt nach der Frist (%d Takte): STURM ABGEBROCHEN, zurueck" % f.sturm["frist"],
                   erg3 is False and any("STURM ABGEBROCHEN" in m for m in aus3)))
    # 4 nur einer da, Sammelfrist um: los
    f4 = neu()
    schritt(f4, lage([HEER] * 10), 20000)
    p4 = f4.sturm["punkt"]
    erg4a, _b, _a = schritt(f4, lage([p4] + [HEER] * 9), 20000 + F.Feldzug.STURM_FRIST - 10)
    erg4, _b, aus4 = schritt(f4, lage([p4] + [HEER] * 9), 20000 + F.Feldzug.STURM_FRIST)
    faelle.append(("1 von 10 da: vor der Frist sammeln, nach %d Takten los" % F.Feldzug.STURM_FRIST,
                   erg4a is False and erg4 is True and any("Sammelfrist" in m for m in aus4)))
    # 5 wer am Lord steht, zaehlt als da und wird nicht zurueckgeschickt
    f5 = neu()
    erg5, bef5, _a = schritt(f5, lage([(301, 100)] * 6 + [HEER] * 4), 30000)
    zurueck = [n for b in bef5 for n in b["angriff"]["einheiten"] if n in range(10, 16)]
    faelle.append(("6 am Lord + 4 weit weg: Sturm, keiner der 6 wird zurueckgeschickt", erg5 is True and not zurueck))
    for name, ok in faelle:
        print("%s %s" % ("OK  " if ok else "ROT ", name))
    print("%d von %d gruen" % (sum(ok for _, ok in faelle), len(faelle)))
    sys.exit(0 if all(ok for _, ok in faelle) else 1)
