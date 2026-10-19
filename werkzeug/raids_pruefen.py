# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer raids.py (19.10.). Vorher festgelegt (wir = Spieler 1, Sklave bei (100, 100)):
  1. Waffenlager 30 Felder weg, Holzfaeller 25 weg, Soeldnerposten 10 weg mit feindlichem Bogen 15 Felder daneben ->
     der Sklave nimmt das Waffenlager (Wert 10/30 > 5/25), nie den Posten am Bogen (der waere ohne Gefahr das beste Ziel)
  2. zwei Sklaven -> zwei verschiedene Ziele (Waffenlager und die sichere Huette)
  3. das Waffenlager brennt (Feuer 40), der Sklave steht davor -> Meldung "angezuendet", er bekommt das naechste Ziel, das
     Waffenlager kommt nie wieder dran
  4. feindliche Fallgrube 2 Felder neben dem Waffenlager -> es wird gemieden, Ziel ist die sichere Huette
  5. Reiter: feindlicher Holzfaeller 15 Felder weg, keine Gefahr -> Angriffsbefehl auf ihn; feindlicher Speer 6 Felder neben
     dem Reiter -> Laufbefehl, das Ziel liegt weiter vom Speer weg als der Reiter
  6. der gejagte Holzfaeller ist weg -> genau ein Abschuss gezaehlt, auch nach drei weiteren Runden
  8. (17:41) feindlicher Holzfaeller 60 Felder weg, nichts naeher -> der Reiter bekommt trotzdem den Angriffsbefehl (reitet hin)
  9. (17:41) Huette und Waffenlager gleich weit -> der Sklave nimmt die Huette (Pennerhof)
  7. Werbung: 100 Gold / 10 am Feuer -> 5 Sklaven, 1 Reiter; 20 Gold / 3 am Feuer -> 1 Sklave (2 bleiben am Feuer)
Gegenprobe: mit "alt" ist nichts gefaehrlich und kein Gebaeude brennt -> Faelle 1, 3 und 4 rot (Fall 2 bleibt gruen: zwei
Sklaven nehmen auch ohne Gefahrenpruefung verschiedene Ziele).
Aufruf: python werkzeug/raids_pruefen.py [alt]"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import raids as R

ALT = len(sys.argv) > 1 and sys.argv[1] == "alt"
if ALT:
    R.gefaehrlich = lambda ort, L, G, sp: None


def einheit(typ, sp, x, y, zustand=1):
    return {"typ": typ, "besitzer": sp, "x": x, "y": y, "leben": 6000, "zustand": zustand}


def geb(typ, sp, x, y):
    return {"typ": typ, "besitzer": sp, "x": x, "y": y}


class Befehle:
    def __init__(self):
        self.liste = []

    def __call__(self, b, warte=1.0, bis=None):
        self.liste.append(b)
        return []


# KORREKTUR 17:30: zuerst stand die dritte Huette bei (120, 100) und der Bogen bei (120, 110) - 10 Felder von ALLEN drei
# Gebaeuden, alle galten als gefaehrlich. Jetzt die Huette am Bogen abseits: 25 Felder vom Sklaven, der Bogen 15 davon,
# 40 Felder von den beiden anderen
# 17:31: das gefaehrdete Ziel ist ein Soeldnerposten 10 Felder weg (Wert 9/10 - ohne Gefahrenpruefung das beste Ziel), der
# Bogen 15 Felder davon, 25 und mehr von den beiden anderen
G0 = {1: geb(11, 2, 130, 100), 2: geb(3, 2, 125, 100), 3: geb(8, 2, 100, 110)}


def L0(*sklaven):
    L = {900: einheit(22, 2, 100, 125)}
    for i, o in enumerate(sklaven):
        L[10 + i] = einheit(71, 1, o[0], o[1])
    return L


def main():
    ok = []

    def pruefe(nr, text, bed):
        ok.append(bool(bed))
        print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text), flush=True)

    feuer = {}
    bt = R.Brandtrupp(1, lambda nr: 0 if ALT else feuer.get(nr, 0))
    b = Befehle()
    bt.schritt(L0((100, 100)), G0, b)
    pruefe(1, "Ziel des Sklaven: %s" % bt.ziel, bt.ziel.get(10) == 1)

    bt2 = R.Brandtrupp(1, lambda nr: 0)
    bt2.schritt(L0((100, 100), (100, 101)), G0, Befehle())
    pruefe(2, "zwei Sklaven: %s" % bt2.ziel, sorted(bt2.ziel.values()) == [1, 2] or (ALT and len(set(bt2.ziel.values())) == 2))

    feuer[1] = 40
    for _ in range(R.NEU_ALLE):
        aus3 = bt.schritt(L0((129, 100)), G0, Befehle())
        if any("angezuendet" in a for a in aus3):
            break
    pruefe(3, "Waffenlager brennt: Meldungen %s, neues Ziel %s, verbrannt %s" % ([a[:50] for a in aus3], bt.ziel, bt.brennt),
           any("angezuendet" in a for a in aus3) and bt.ziel.get(10) not in (1, None) and 1 in bt.brennt)

    G4 = dict(G0)
    G4[50] = geb(67, 2, 132, 100)
    bt4 = R.Brandtrupp(1, lambda nr: 0)
    bt4.schritt(L0((100, 100)), G4, Befehle())
    pruefe(4, "Grube am Waffenlager: Ziel %s" % bt4.ziel, bt4.ziel.get(10) == 2)

    rj = R.Reiterjagd(1)
    L5 = {20: einheit(74, 1, 100, 100), 700: einheit(3, 2, 115, 100)}
    b5 = Befehle()
    rj.schritt(L5, {}, b5)
    jagd = [x for x in b5.liste if x["angriff"].get("ziel") == 700]
    L5b = {20: einheit(74, 1, 100, 100), 700: einheit(3, 2, 115, 100), 701: einheit(24, 2, 106, 100)}
    b5b = Befehle()
    rj2 = R.Reiterjagd(1)
    rj2.schritt(L5b, {}, b5b)
    lauf = [x["angriff"]["lauf"] for x in b5b.liste if "lauf" in x["angriff"]]
    pruefe(5, "Jagd %s; mit Speer daneben Lauf %s" % (bool(jagd), lauf),
           jagd and lauf and R.schach(lauf[0], (106, 100)) > R.schach((100, 100), (106, 100)))

    L6 = {20: einheit(74, 1, 100, 100)}
    for _ in range(4):
        rj.schritt(L6, {}, Befehle())
    pruefe(6, "Abschuesse nach Verschwinden + 3 Runden: %d" % rj.getoetet, rj.getoetet == 1)

    rj8 = R.Reiterjagd(1)
    b8 = Befehle()
    rj8.schritt({20: einheit(74, 1, 100, 100), 800: einheit(3, 2, 160, 100)}, {}, b8)
    pruefe(8, "Holzfaeller 60 Felder weg: Befehle %s" % b8.liste, any(x["angriff"].get("ziel") == 800 for x in b8.liste))
    bt9 = R.Brandtrupp(1, lambda nr: 0)
    bt9.schritt({10: einheit(71, 1, 100, 100)}, {1: geb(11, 2, 120, 100), 2: geb(1, 2, 100, 120)}, Befehle())
    pruefe(9, "Huette und Waffenlager 20 Felder: Ziel %s" % bt9.ziel, bt9.ziel.get(10) == 2)
    w = (R.werbung(100, 10, 0, 0), R.werbung(20, 3, 0, 0))
    pruefe(7, "Werbung 100/10: %s, 20/3: %s" % w, w[0] == [(71, 5), (74, 1)] and w[1] == [(71, 1)])
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
