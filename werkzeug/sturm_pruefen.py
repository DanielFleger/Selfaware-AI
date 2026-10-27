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


def lage(positionen, schuetzen=True, lord=150000):
    L = {500: einheit(55, 2, LP[0], LP[1], lord, 0)}
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
    # 2 Partie 221355: die Haelfte (5 Streitkolben) ist da, aber der Wettlauf verliert (gestapelt 5 gegen 150.000 - Eichung L200:
    #   Lord ueberlebt) -> NICHT los, Meldung nennt den Grund
    erg2, _b, aus2 = schritt(f, lage([pkt] * 5 + [HEER] * 5), 10100)
    faelle.append(("5 von 10 da, Wettlauf verliert: kein Sturm, Meldung 'los erst, wenn'", erg2 is False
                   and any("los erst, wenn der Wettlauf" in m for m in aus2)))
    # 3 alle 10 da, Lord geschwaecht (40.000) -> Wettlauf gewinnt -> STURM LOS; danach Abbruch nach der Frist
    L3 = lage([pkt] * 10, lord=40000)
    erg3, _b, aus3 = schritt(f, L3, 10200)
    faelle.append(("10 da, Lord 40.000: STURM LOS", erg3 is True and any("STURM LOS" in m for m in aus3)
                   and F.STURM_LAEUFT == set(range(10, 20))))
    erg3b, _b, aus3b = schritt(f, L3, 10200 + f.sturm["frist"] + 1)
    faelle.append(("Lord lebt nach der Frist (%d Takte): STURM ABGEBROCHEN, Sturmliste leer" % f.sturm["frist"],
                   erg3b is False and any("STURM ABGEBROCHEN" in m for m in aus3b) and not F.STURM_LAEUFT))
    # 4 Partie 221355: einer da, Frist weit um, Wettlauf verliert -> trotzdem KEIN Sturm (vorher: "Sammelfrist um (1 von 13)")
    f4 = neu()
    schritt(f4, lage([HEER] * 10), 20000)
    p4 = f4.sturm["punkt"]
    schritt(f4, lage([p4] + [HEER] * 9), 20100)
    erg4, _b, aus4 = schritt(f4, lage([p4] + [HEER] * 9), 20100 + F.Feldzug.STURM_FRIST + 50)
    faelle.append(("1 von 10 da, Frist um, Wettlauf verliert: kein Sturm", erg4 is False and not any("STURM LOS" in m for m in aus4)))
    # 5 wer am Lord steht, zaehlt als da und wird nicht zurueckgeschickt
    f5 = neu()
    erg5, bef5, _a = schritt(f5, lage([(301, 100)] * 6 + [HEER] * 4), 30000)
    zurueck = [n for b in bef5 for n in b["angriff"]["einheiten"] if n in range(10, 16)]
    faelle.append(("6 am Lord + 4 weit weg: keiner der 6 wird zurueckgeschickt (sie kaempfen weiter)", not zurueck))
    for name, ok in faelle:
        print("%s %s" % ("OK  " if ok else "ROT ", name))
    print("%d von %d gruen" % (sum(ok for _, ok in faelle), len(faelle)))
    sys.exit(0 if all(ok for _, ok in faelle) else 1)
