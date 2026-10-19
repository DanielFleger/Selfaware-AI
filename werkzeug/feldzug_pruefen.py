# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer feldzug.py (Daniel 18.10.2026: 30 Streitkolben je Nomade, gestackt, eins nach dem anderen).
Vorher festgelegt, was gelten muss:
  1. 10 Streitkolben am Bergfried, Lord weit weg, Schuetzen um den Lord -> Phase sammeln, Laufbefehl an den Sammelpunkt;
     der Sammelpunkt liegt mehr als 50 Felder von jedem Schuetzen und mehr als 30 von jedem feindlichen Gebaeude
  2. 30 Streitkolben am Sammelpunkt, Tick nach dem Lord-Schutz -> ANGRIFF: ein LAUF-Befehl mit allen 30 (19.10.: laufen
     an Feinden vorbei, klettern), noch kein Angriffsbefehl - der Lord ist weit weg
  3. dieselben 30 vor dem Lord-Schutz -> KEIN Angriff
  4. der Ziel-Lord ist tot -> naechstes Ziel ist der andere Lord, Phase sammeln (Ueberlebende sammeln neu)
  5. feindlicher Speer 12 Felder vor dem Sammelpunkt -> die dort stehenden Streitkolben greifen ihn an
  6. (19.10., Gefechtsrechnung statt fester 30) 8 Streitkolben am Sammelpunkt, am Lord 20 arab. Schwertkaempfer -> kein
     Angriff (die Rechnung verliert)
  7. (19.10.) im Angriff: 10 Streitkolben 3 Felder neben dem Lord -> Angriffsbefehl auf den Lord fuer genau diese 10
  8. (19.10., Daniel: "obenrum haetten die Bogenschuetzen sie erst am Ende erkannt") Wegplaner liefert einen Umweg ->
     der erste Laufbefehl geht an den ersten Wegpunkt, nicht an den Lord
  9. (Daniel 19.10.: "danach besser verteilen um auch zu raiden"; 1019f: 26 arab. Schwertkaempfer standen am Bergfried) 12
     arab. Schwertkaempfer am Sammelpunkt, der Lord mit 2 Schuetzen -> ANGRIFF (das Heer sind alle Truppen, nicht nur
     Streitkolben; die Rechnung gewinnt)
 10. dieselben 12, davon 4 in der Heimwache -> das Heer hat 8, die 4 bekommen keinen Befehl
 11. (1019h: 79 Mann 6-22 Felder vor dem Lord, Wegpunkt 14/15, am Lord 0 - beschossen, ohne anzugreifen) Angriff laeuft, die
     Spitze 20 Felder vor dem Lord, die Mitte nicht am Wegpunkt -> alle Nahkaempfer bekommen den Angriffsbefehl auf den Lord
 12. (Daniel: "arabische Bogenschuetzen sollten eher schiessen, wenn sie koennen") Schuetzen im Heer, ein feindlicher Bogen
     30 Felder vor ihnen -> sie greifen ihn an statt zu laufen
 13. (1019h: Laufbefehle jede Runde neu) zwei Runden hintereinander, niemand ist angekommen -> in der zweiten kein neuer
     Laufbefehl
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
    lauf2 = [x for x in b.liste if "lauf" in x.get("angriff", {})]
    pruefe(2, "30 am Punkt nach dem Lord-Schutz: Phase %s, Laufbefehl mit %s Einheiten, Angriffsbefehle %d" % (
        f.phase, len(lauf2[-1]["angriff"]["einheiten"]) if lauf2 else 0, len(angr)),
        f.phase == "angriff" and lauf2 and len(lauf2[-1]["angriff"]["einheiten"]) == 30 and not angr)
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
    L, G = lage(8, f6.punkt)
    for i in range(20):
        L[900 + i] = einheit(75, 2, 300 + i % 5, 102 + i // 5, 28000)
    b = Befehle()
    f6.schritt({"t": 12050}, L, G, b)
    pruefe(6, "8 am Punkt, 20 arab. Schwertkaempfer am Lord: Phase %s" % f6.phase, f6.phase == "sammeln")
    # 7
    f7 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    f7.schritt({"t": 12000}, *lage(10, heim), Befehle())
    f7.schritt({"t": 12050}, *lage(30, f7.punkt), Befehle())
    L, G = lage(10, (298, 98))
    b = Befehle()
    f7.schritt({"t": 12100}, L, G, b)
    angr7 = [x for x in b.liste if x.get("angriff", {}).get("ziel") == 500]
    pruefe(7, "10 Streitkolben 3 Felder neben dem Lord: Angriffsbefehl %s" % (angr7[:1],),
           angr7 and sorted(angr7[0]["angriff"]["einheiten"]) == list(range(10, 20)))
    # 8
    f8 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    f8.wegplaner = lambda L_, G_, s, z: [(240, 60), (290, 80), z]
    f8.schritt({"t": 12000}, *lage(10, heim), Befehle())
    L, G = lage(30, f8.punkt)
    b = Befehle()
    f8.schritt({"t": 12050}, L, G, b)
    lauf8 = [x["angriff"]["lauf"] for x in b.liste if "lauf" in x.get("angriff", {})]
    pruefe(8, "Umweg (240,60) -> (290,80) -> Lord: Laufbefehle %s" % lauf8, lauf8 and lauf8[-1] == [240, 60])
    # 9 / 10
    def heer(heimwache):
        f9 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
        f9.heimwache = set(heimwache)
        f9.schritt({"t": 12000}, *lage(10, heim), Befehle())
        L, G = lage(0, f9.punkt)
        for i in range(12):
            L[10 + i] = einheit(75, 1, f9.punkt[0] + i % 3, f9.punkt[1] + i // 3, 28000)
        b = Befehle()
        aus = f9.schritt({"t": 12050}, L, G, b)
        befohlen = {n for x in b.liste for n in x.get("angriff", {}).get("einheiten", [])}
        return f9.phase, befohlen, [a[:110] for a in aus if "ANGRIFF" in a][:1]
    ph9, bef9, m9 = heer(())
    pruefe(9, "12 arab. Schwertkaempfer am Punkt, Lord mit 2 Schuetzen: Phase %s %s" % (ph9, m9), ph9 == "angriff")
    ph10, bef10, _ = heer((10, 11, 12, 13))
    pruefe(10, "4 davon Heimwache: Befehle an %s" % sorted(bef10), not bef10 & {10, 11, 12, 13} and bef10)
    # 11
    f11 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    f11.wegplaner = lambda L_, G_, s, z: [(240, 60), (290, 80), z]
    f11.schritt({"t": 12000}, *lage(10, heim), Befehle())
    f11.schritt({"t": 12050}, *lage(30, f11.punkt), Befehle())
    L, G = lage(0, heim)
    for i in range(20):
        L[10 + i] = einheit(75, 1, 300 - 20 + i % 5, 100 + i // 5, 28000)
    b = Befehle()
    f11.schritt({"t": 12100}, L, G, b)
    angr11 = [x for x in b.liste if x.get("angriff", {}).get("ziel") == 500]
    n11 = len(angr11[0]["angriff"]["einheiten"]) if angr11 else 0
    pruefe(11, "Spitze 20 Felder vor dem Lord: Angriffsbefehl auf den Lord fuer %d von 20" % n11, n11 == 20)
    # 12
    f12 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    f12.schritt({"t": 12000}, *lage(10, heim), Befehle())
    f12.schritt({"t": 12050}, *lage(30, f12.punkt), Befehle())
    L, G = lage(0, heim)
    for i in range(6):
        L[40 + i] = einheit(70, 1, 200 + i, 150, 15000)
    L[777] = einheit(22, 2, 200, 180)
    b = Befehle()
    f12.schritt({"t": 12100}, L, G, b)
    schuss = [x for x in b.liste if x.get("angriff", {}).get("ziel") == 777]
    pruefe(12, "6 arab. Bogen, feindlicher Bogen 30 Felder: Angriff auf ihn %s" % (schuss[:1],),
           schuss and set(schuss[0]["angriff"]["einheiten"]) == set(range(40, 46)))
    # 13
    f13 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    L, G = lage(10, heim)
    for n in L:
        if L[n]["besitzer"] == 1:
            L[n]["zustand"] = 101
    b1 = Befehle()
    f13.schritt({"t": 12000}, L, G, b1)
    b2 = Befehle()
    f13.schritt({"t": 12050}, L, G, b2)
    lauf1 = [x for x in b1.liste if "lauf" in x.get("angriff", {})]
    lauf2 = [x for x in b2.liste if "lauf" in x.get("angriff", {})]
    pruefe(13, "Laufbefehle Runde 1: %d, Runde 2: %d" % (len(lauf1), len(lauf2)), lauf1 and not lauf2)
    # 14 (19.10., 1018l: Endspurt-Angriff 10.000 Ticks bei "Wegpunkt 2/20", Spitze immer 157 Felder vor dem Lord): im Angriff
    # bewegt sich niemand -> nach 1.500 Ticks Wegpunkt uebersprungen, nach weiteren 1.500 alle mit Angriffsbefehl auf den Lord
    f14 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    f14.wegplaner = lambda L_, G_, s, z: [(150, 200), (200, 150), (250, 120), z]
    f14.schritt({"t": 12000}, *lage(10, heim), Befehle())
    f14.schritt({"t": 12050}, *lage(30, f14.punkt), Befehle())
    L14, G14 = lage(0, heim)
    for i in range(20):
        L14[10 + i] = einheit(75, 1, 100 + i % 5, 240 + i // 5, 28000)
    meld, lord14 = [], []
    for t in range(12100, 15400, 100):
        b14 = Befehle()
        meld += [m for m in f14.schritt({"t": t}, L14, G14, b14) if "STAU" in m]
        if len(meld) == 2:            # ab dem zweiten Stau: Angriffsbefehle auf den Lord (alle 5 Runden neu)
            lord14 += [x for x in b14.liste if x.get("angriff", {}).get("ziel") == 500]
    pruefe(14, "Stau: Meldungen %s; am Ende Angriff auf den Lord fuer %d" % (
        [m[:60] for m in meld], len(lord14[0]["angriff"]["einheiten"]) if lord14 else 0),
           len(meld) == 2 and "uebersprungen" in meld[0] and "direkt" in meld[1] and lord14
           and len(lord14[0]["angriff"]["einheiten"]) == 20)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
