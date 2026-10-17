# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer sicht.py (Plan_Entdeckung.md, 17.10.). Vorher festgelegt:
  1. Holzfaeller direkt neben der Assassine -> NICHT sichtbar (Arbeiter verraten nicht, L75)
  2. Speertraeger 19 Felder weg -> sichtbar; 21 Felder weg -> nicht sichtbar
  3. Bogenschuetze 30 Felder weg, Speertraeger 5 Felder neben der Assassine, freie Linie -> Beschuss 1,352 je Takt
  4. dasselbe, Kaserne (5x5) genau zwischen Schuetze und Assassine -> 0,070; Apfelplantage (flach) dazwischen -> 1,352
  5. Schuetze auf einem Turm (Laufzeit 76) hinter derselben Kaserne -> 1,352 (von oben frei)
  6. Bogenschuetze 45 Felder weg (ausser Reichweite 40) -> 0
  7. Speertraeger 20 Felder weg in einem Trupp mit Haltung Angriff -> verfolgt; Haltung Stehen -> nicht; ohne Trupp -> nicht
  8. sicher: sichtbar, aber kein Schuetze -> sicher; sichtbar mit Schuetze -> nicht sicher
Gegenprobe: mit "arbeiter" zaehlen Arbeiter als waehlbar -> Fall 1 rot.
Aufruf: python werkzeug/sicht_pruefen.py [arbeiter]"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import sicht as S

if len(sys.argv) > 1 and sys.argv[1] == "arbeiter":
    S.WAEHLBAR = S.WAEHLBAR | {1, 3, 7, 8, 19}

A = (200, 200)


def e(typ, x, y, besitzer=2, gruppe=0):
    return {"typ": typ, "x": x, "y": y, "besitzer": besitzer, "gruppe": gruppe, "leben": 10000}


def lage(einheiten, gebaeude=None, haltung=None):
    L = {i + 1: x for i, x in enumerate([e(73, A[0], A[1], besitzer=1)] + einheiten)}
    G = {900 + i: g for i, g in enumerate(gebaeude or [])}
    return S.Lage(L, G, 1, haltung)


def main():
    ok = []
    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))
    l1 = lage([e(3, 201, 200)])
    pruefe(1, "Holzfaeller daneben: sichtbar %s" % l1.sichtbar(A), not l1.sichtbar(A))
    l2a, l2b = lage([e(24, 219, 200)]), lage([e(24, 221, 200)])
    pruefe(2, "Speer 19 Felder: sichtbar %s, 21 Felder: sichtbar %s" % (l2a.sichtbar(A), l2b.sichtbar(A)),
           l2a.sichtbar(A) and not l2b.sichtbar(A))
    grund = [e(22, 230, 200), e(24, 205, 200)]
    l3 = lage(grund)
    pruefe(3, "Bogen 30 Felder, Speer 5 daneben, frei: %.3f" % l3.beschuss(A), abs(l3.beschuss(A) - S.RATE_FREI) < 1e-9)
    kaserne = {"typ": 9, "x": 213, "y": 198, "besitzer": 2, "leben": 500, "uid": 1}
    apfel = {"typ": 32, "x": 211, "y": 195, "besitzer": 2, "leben": 60, "uid": 2}
    l4, l4b = lage(grund, [kaserne]), lage(grund, [apfel])
    pruefe(4, "Kaserne dazwischen: %.3f, Apfelplantage dazwischen: %.3f" % (l4.beschuss(A), l4b.beschuss(A)),
           abs(l4.beschuss(A) - S.RATE_ZU) < 1e-9 and abs(l4b.beschuss(A) - S.RATE_FREI) < 1e-9)
    turm = {"typ": 76, "x": 229, "y": 199, "besitzer": 2, "leben": 1000, "uid": 3}
    l5 = lage(grund, [kaserne, turm])
    pruefe(5, "Schuetze auf Turm hinter der Kaserne: %.3f" % l5.beschuss(A), abs(l5.beschuss(A) - S.RATE_FREI) < 1e-9)
    l6 = lage([e(22, 245, 200), e(24, 205, 200)])
    pruefe(6, "Bogen 45 Felder: %.3f" % l6.beschuss(A), l6.beschuss(A) == 0)
    l7a = lage([e(24, 220, 200, gruppe=7)], haltung={7: 2})
    l7b = lage([e(24, 220, 200, gruppe=7)], haltung={7: 0})
    l7c = lage([e(24, 220, 200, gruppe=0)], haltung={7: 2})
    pruefe(7, "Speer 20 Felder, Angriff: %s, Stehen: %s, ohne Trupp: %s" % (bool(l7a.verfolgt(A)), bool(l7b.verfolgt(A)),
                                                                          bool(l7c.verfolgt(A))),
           l7a.verfolgt(A) and not l7b.verfolgt(A) and not l7c.verfolgt(A))
    l8a = lage([e(24, 210, 200)])
    pruefe(8, "sichtbar ohne Schuetze sicher: %s, mit Schuetze (Fall 3) sicher: %s" % (l8a.sicher(A), l3.sicher(A)),
           l8a.sicher(A) and not l3.sicher(A))
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
