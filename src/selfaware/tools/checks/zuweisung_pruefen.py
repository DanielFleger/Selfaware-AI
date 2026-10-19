# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer uebersicht.py (Makro), zuweisung.py (Mikro) und die Jagd-Sperre im Waechter (19.10. 18:30).
Vorher festgelegt:
  1. einholbar: arab. Schwert gegen laufende Assassine NEIN; Bogen JA; Speer (13,5) JA; arab. Schwert gegen stehende
     Assassine JA; Streitkolben (Tempo ungemessen) gegen laufende Assassine NEIN
  2. kleinste_gruppe: 40 arab. Schwert + 3 Bogen gegen 1 laufende Assassine -> nur Bogen, hoechstens 3
  3. kleinste_gruppe: 40 arab. Schwert gegen 1 stehende Assassine -> 1 oder 2, nicht 40
  4. Uebersicht: Einheit 5 Felder gelaufen -> laeuft; stehende -> steht; 10 dicht + 1 weit = 2 Verbaende des Gegners;
     die LAGE-Zeile nennt beide Spieler
  5. Waechter (der Fall aus Daniels Bild 18:07): 40 eigene arab. Schwert, 1 feindliche Assassine LAEUFT durch unsere
     Wirtschaft -> KEIN Angriffsbefehl, Meldung KEINE JAGD
  6. Waechter: dieselbe Assassine STEHT (reisst ab) -> Angriff mit hoechstens 4, nicht 40
  NEU 18:35 (Zielwahl, Plan Schritt 2):
  7. abwehr_rang: Bogen 5 Felder, arab. Schwert 10, stehende Assassine 15 - eigene arab. Schwert -> Assassine zuerst,
     dann Schwert, Bogen zuletzt (meister Schaden je Leben)
  8. dieselbe Assassine LAEUFT -> sie faellt heraus (keiner holt sie ein), Schwert zuerst
  9. Waechter mit ZIELWAHL "schaden": Bogen naeher an unseren Gebaeuden als die stehende Assassine -> Ziel ist die Assassine
  10. Uebersicht mit Gebaeuden: Spieler 2 hat Kornspeicher (19) bei (40, 40) und Markt (26) -> schluessel(2) nennt beide,
      die LAGE-Zeile nennt "Kornspeicher (40, 40)"; Spieler 1 ohne Schluesselgebaeude -> leer
Gegenprobe: uv run python -m selfaware.tools.checks.zuweisung_pruefen alt  (einholbar immer ja = alter Stand) -> 1, 2, 5 und 8 rot;
uv run python -m selfaware.tools.checks.zuweisung_pruefen abstand  (Zielwahl wie bis 18:35) -> 9 rot."""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.micro.zuweisung as ZW
import selfaware.services.uebersicht as UB
import selfaware.micro.tasks.waechter as W

if len(sys.argv) > 1 and sys.argv[1] == "alt":
    ZW.einholbar = lambda a, b, c: True
if len(sys.argv) > 1 and sys.argv[1] == "abstand":
    W.Waechter.ZIELWAHL = "abstand"


def e(typ, sp, x, y, leben, nr=0, lauf=(0, 0), nahziel=-1):
    return {"nr": nr, "typ": typ, "besitzer": sp, "x": x, "y": y, "leben": leben, "zustand": 1, "zielart": 0,
            "zieleinheit": 0, "laufx": lauf[0], "laufy": lauf[1], "nahziel": nahziel, "nahangreifer": 0, "gruppe": 0}


def main():
    ok = []

    def pruefe(nr, text, bed):
        ok.append(bool(bed))
        print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text), flush=True)

    r1 = (ZW.einholbar(75, 73, False), ZW.einholbar(22, 73, False), ZW.einholbar(24, 73, False), ZW.einholbar(75, 73, True),
          ZW.einholbar(26, 73, False))
    pruefe(1, "einholbar (Schwert, Bogen, Speer, Schwert/steht, Streitkolben): %s" % (r1,), r1 == (False, True, True, True, False))

    eig = [dict(nr=100 + i, typ=75, leben=28000, x=100 + i % 5, y=100 + i // 5) for i in range(40)]
    eig += [dict(nr=200 + i, typ=22, leben=10000, x=110, y=100 + i) for i in range(3)]
    ass = [dict(typ=73, leben=12500, x=120, y=105)]
    g2 = ZW.kleinste_gruppe(eig, ass, ziel_steht=False)
    pruefe(2, "1 laufende Assassine: %s - %s" % (g2[0], g2[2]), g2[0] and len(g2[0]) <= 3 and all(n >= 200 for n in g2[0]))
    g3 = ZW.kleinste_gruppe(eig[:40], ass, ziel_steht=True)
    pruefe(3, "1 stehende Assassine: %s - %s" % (g3[0], g3[2]), g3[1] and 1 <= len(g3[0]) <= 2)

    u = UB.Uebersicht(1)
    L1 = {1: e(75, 1, 50, 50, 28000, 1), 2: e(73, 2, 80, 80, 12500, 2)}
    for i in range(10):
        L1[10 + i] = e(75, 2, 150 + i, 150, 28000, 10 + i)
    L1[30] = e(22, 2, 200, 200, 10000, 30)
    u.runde(1000, L1)
    L2 = dict(L1)
    L2[2] = e(73, 2, 85, 80, 12500, 2)
    u.runde(1060, L2)
    z = u.zeile([(50, 50)])
    vb2 = [v for v in u.verbaende if v["besitzer"] == 2]
    pruefe(4, "laeuft/steht %s/%s, Verbaende SP2 %d (erwartet 3: 10er, Bogen, Assassine) | %s" % (
        u.steht(2), u.steht(1), len(vb2), z[:160]), u.steht(2) is False and u.steht(1) is True and len(vb2) == 3
        and "SP1" in z and "SP2" in z)

    befehle = []
    W.befehl = lambda b, *a, **k: befehle.append(b)

    def waechter_fall(laeuft):
        befehle.clear()
        w = W.Waechter(1, posten=(100, 100))
        w.besetzt = True
        u = UB.Uebersicht(1)
        w.uebersicht = u
        L = {}
        for i in range(40):
            L[100 + i] = e(75, 1, 100 + i % 5, 100 + i // 5, 28000, 100 + i)
        L[500] = e(73, 2, 120, 120, 12500, 500, lauf=(125, 120))
        u.runde(1000, L)
        L = dict(L)
        L[500] = e(73, 2, 124 if laeuft else 120, 120, 12500, 500, lauf=(130, 120))
        u.runde(1060, L)
        ev = w.schritt(L, [(118, 118), (125, 125)])
        angriffe = [b for b in befehle if "angriff" in b and b["angriff"].get("ziel") == 500]
        return ev, angriffe

    ev5, an5 = waechter_fall(True)
    pruefe(5, "laufende Assassine: Angriffe %d, Meldung %s" % (len(an5), [x[:90] for x in ev5]),
           not an5 and any("KEINE JAGD" in x for x in ev5))
    ev6, an6 = waechter_fall(False)
    n6 = len(an6[0]["angriff"]["einheiten"]) if an6 else 0
    pruefe(6, "stehende Assassine: %d greifen an - %s" % (n6, [x[:110] for x in ev6]), 1 <= n6 <= 4)
    fe = {1: e(22, 2, 105, 100, 10000, 1), 2: e(75, 2, 110, 100, 28000, 2), 3: e(73, 2, 115, 100, 12500, 3)}
    eig7 = [dict(typ=75)]
    r7 = [n for n, _ in ZW.abwehr_rang(fe, eig7, steht=lambda n: True)]
    pruefe(7, "Rang (stehende Assassine): %s" % r7, r7 == [3, 2, 1])
    r8 = [n for n, _ in ZW.abwehr_rang(fe, eig7, steht=lambda n: n != 3)]
    pruefe(8, "Rang (Assassine laeuft): %s" % r8, r8 == [2, 1])
    befehle.clear()
    w9 = W.Waechter(1, posten=(100, 100))
    w9.besetzt = True
    u9 = UB.Uebersicht(1)
    w9.uebersicht = u9
    L9 = {}
    for i in range(20):
        L9[100 + i] = e(75, 1, 100 + i % 5, 100 + i // 5, 28000, 100 + i)
    L9[600] = e(22, 2, 112, 112, 10000, 600)          # Bogen, 2 Felder vor unserem Gebaeude
    L9[601] = e(73, 2, 116, 116, 12500, 601)          # Assassine, 6 Felder vor unserem Gebaeude
    u9.runde(1000, L9)
    u9.runde(1060, dict(L9))
    w9.schritt(L9, [(110, 110)])
    pruefe(9, "Waechter Zielwahl %s: Ziel %s" % (W.Waechter.ZIELWAHL, w9.ziel), w9.ziel == 601)
    u10 = UB.Uebersicht(1)
    G10 = {1: {"besitzer": 2, "typ": 19, "x": 40, "y": 40, "leben": 1000}, 2: {"besitzer": 2, "typ": 26, "x": 50, "y": 40, "leben": 900},
           3: {"besitzer": 1, "typ": 3, "x": 10, "y": 10, "leben": 300}, 4: {"besitzer": 0, "typ": 19, "x": 1, "y": 1, "leben": 1}}
    u10.runde(1000, {1: e(55, 1, 10, 10, 150000, 1)}, G10)
    z10 = u10.zeile()
    pruefe(10, "Schluessel SP2 %s, SP1 %s | %s" % (sorted(k[0] for k in u10.schluessel(2)), u10.schluessel(1), z10[:140]),
           sorted(k[0] for k in u10.schluessel(2)) == [19, 26] and u10.schluessel(1) == [] and "Kornspeicher (40, 40)" in z10)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
