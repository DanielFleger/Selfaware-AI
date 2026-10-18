# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer feldzug.py (Daniel 18.10.2026: 30 Streitkolben je Nomade, gestackt, eins nach dem anderen).
Vorher festgelegt, was gelten muss:
  1. 10 Streitkolben am Bergfried, Lord weit weg, Schuetzen um den Lord -> Phase sammeln, Laufbefehl an den Sammelpunkt;
     der Sammelpunkt liegt mehr als 50 Felder von jedem Schuetzen und mehr als 30 von jedem feindlichen Gebaeude
  2. 30 Streitkolben am Sammelpunkt, Tick nach dem Lord-Schutz -> ANGRIFF: ein Befehl mit allen 30 auf den Lord
  3. dieselben 30 vor dem Lord-Schutz -> KEIN Angriff
  4. der Ziel-Lord ist tot -> naechstes Ziel ist der andere Lord, Phase sammeln (Ueberlebende sammeln neu)
  5. feindlicher Speer 12 Felder vor dem Sammelpunkt -> die dort stehenden Streitkolben greifen ihn an
  6. 29 Streitkolben am Sammelpunkt -> kein Angriff (erst ab 30, Ueberlebende zaehlen mit)
Aufruf: python werkzeug/feldzug_pruefen.py   (Rueckgabe 0 = gruen)
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import feldzug as F

ok = []


def pruefe(nr, text, bed):
    ok.append(bool(bed))
    print("%s %3d %s" % ("OK  " if bed else "ROT ", nr, text))


def einheit(typ, sp, x, y, leben=10000):
    return {"typ": typ, "besitzer": sp, "x": x, "y": y, "leben": leben, "laufx": x, "laufy": y, "zustand": 1}


def lage(n_kolben, bei, lord2=True):
    L = {500: einheit(55, 2, 300, 100, 30000), 600: einheit(23, 2, 295, 105), 601: einheit(22, 2, 305, 95)}
    if lord2:
        L[700] = einheit(55, 3, 330, 330, 30000)
    for i in range(n_kolben):
        L[10 + i] = einheit(26, 1, bei[0] + i % 3, bei[1] + i // 10)
    G = {900: {"besitzer": 2, "typ": 3, "x": 290, "y": 110, "leben": 100}}
    return L, G


class Befehle:
    def __init__(self):
        self.liste = []

    def __call__(self, b, warte=1.0, bis=None):
        self.liste.append(b)
        return []


def main():
    heim = (80, 260)
    # 1
    f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    L, G = lage(10, heim)
    b = Befehle()
    aus = f.schritt({"t": 12000}, L, G, b)
    p = f.punkt
    abst = min(F.schach(p, (e["x"], e["y"])) for e in L.values() if e["besitzer"] == 2 and e["typ"] in F.FERN) if p else -1
    lauf = [x for x in b.liste if "lauf" in x.get("angriff", {})]
    pruefe(1, "Phase %s, Sammelpunkt %s, %d Felder zum naechsten Schuetzen, Laufbefehl %s" % (f.phase, p, abst, bool(lauf)),
           f.phase == "sammeln" and p is not None and abst > 50 and F.schach(p, (290, 110)) > 30 and lauf)
    # 2
    L, G = lage(30, p)
    b = Befehle()
    f.schritt({"t": 12100}, L, G, b)
    angr = [x for x in b.liste if x.get("angriff", {}).get("ziel") == 500]
    pruefe(2, "30 am Punkt nach dem Lord-Schutz: Phase %s, Angriffsbefehl mit %s Einheiten" % (
        f.phase, len(angr[0]["angriff"]["einheiten"]) if angr else 0), f.phase == "angriff" and angr and len(angr[0]["angriff"]["einheiten"]) == 30)
    # 3
    f3 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    f3.schritt({"t": 5000}, *lage(10, heim), Befehle())
    L, G = lage(30, f3.punkt)
    b = Befehle()
    f3.schritt({"t": 5100}, L, G, b)
    pruefe(3, "30 am Punkt vor dem Lord-Schutz: Phase %s" % f3.phase, f3.phase == "sammeln" and not [x for x in b.liste if x.get("angriff", {}).get("ziel") == 500])
    # 4
    L, G = lage(18, p)
    del L[500]
    aus = f.schritt({"t": 13000}, L, G, Befehle())
    pruefe(4, "Lord 500 tot: Ziel jetzt %s, Phase %s, Meldungen %s" % (f.ziel, f.phase, [a[:40] for a in aus][:2]), f.ziel == 700 and f.phase == "sammeln")
    # 5
    f5 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    f5.schritt({"t": 12000}, *lage(10, heim), Befehle())
    q = f5.punkt
    L, G = lage(10, q)
    L[800] = einheit(24, 2, q[0] + 12, q[1])
    b = Befehle()
    f5.schritt({"t": 12050}, L, G, b)
    pruefe(5, "Speer 12 Felder vor dem Sammelpunkt: Angriff auf ihn %s" % [x for x in b.liste if x.get("angriff", {}).get("ziel") == 800][:1],
           any(x.get("angriff", {}).get("ziel") == 800 for x in b.liste))
    # 6
    f6 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    f6.schritt({"t": 12000}, *lage(10, heim), Befehle())
    L, G = lage(29, f6.punkt)
    b = Befehle()
    f6.schritt({"t": 12050}, L, G, b)
    pruefe(6, "29 am Punkt: Phase %s" % f6.phase, f6.phase == "sammeln")
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
