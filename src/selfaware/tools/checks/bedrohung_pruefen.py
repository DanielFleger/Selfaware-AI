# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer bedrohung.py (Lord-Bedarf aus gemessenen Lagen statt Formel). Vorher festgelegt:
  1. dieselbe Lage -> belegt, belegte Zahl, Gruppenleben
  2. ein Verteidiger weniger -> belegt (weniger ist nie gefaehrlicher - offene Annahme, siehe bedrohung.py)
  3. ein Bogenschuetze mehr bis 15 Felder -> VORLAEUFIG, Grund nennt den Ring und Typ
  4. ein Arbeiter mehr bis 45 Felder -> VORLAEUFIG (nichts wird vorher aussortiert)
  5. eine Einheit mehr weiter als 45 Felder -> belegt (nur mitgeschrieben, in keiner Messung beteiligt)
  6. ein Gebaeude mehr bis 15 Felder -> VORLAEUFIG
  7. Lord staerker -> VORLAEUFIG; Lord 4 Felder woanders -> VORLAEUFIG
  8. zwei deckende Lagen -> die kleinere belegte Zahl
  9. keine Lage gemessen -> VORLAEUFIG mit Ersatzwert, als solcher benannt
 10. kein feindlicher Lord -> kein Bedarf
Aufruf: uv run python -m selfaware.tools.checks.bedrohung_pruefen   (Rueckgabe 0 = gruen)
"""
import copy, os, sys
HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.services.bedrohung as B

LORD = (230, 287)


def e(typ, besitzer, x, y, leben=1000):
    return {"typ": typ, "besitzer": besitzer, "x": x, "y": y, "leben": leben}


def lage_grund():
    L = {1: e(55, 2, *LORD, leben=150000), 2: e(22, 2, 235, 287), 3: e(22, 2, 240, 290), 4: e(24, 2, 232, 289),
         5: e(3, 2, 250, 300), 6: e(73, 1, 180, 280), 7: e(9, 2, 380, 380)}
    G = {50: {"besitzer": 2, "typ": 19, "x": 228, "y": 285}, 51: {"besitzer": 2, "typ": 32, "x": 300, "y": 300}}
    return L, G


def main():
    ok = []
    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %2d %s" % ("OK" if bed else "ROT", nr, text))
    L, G = lage_grund()
    gem = {"name": "Messlage", "mindest": 19, "gruppe_leben": 237500, "beleg": "test", "fingerabdruck": B.fingerabdruck(L, G)}
    def bed(L2, G2, lagen=(gem,)):
        return B.bedarf(B.fingerabdruck(L2, G2), list(lagen))
    n, art, grund, gl = bed(L, G)
    pruefe(1, "dieselbe Lage -> belegt 19, Gruppenleben 237500 (%s %s %s)" % (n, art, gl), (n, art, gl) == (19, "belegt", 237500))
    L2 = copy.deepcopy(L); del L2[4]
    pruefe(2, "ein Speertraeger weniger -> belegt", bed(L2, G)[1] == "belegt")
    L3 = copy.deepcopy(L); L3[8] = e(22, 2, 225, 280)
    r = bed(L3, G)
    pruefe(3, "ein Bogenschuetze mehr bis 15 -> VORLAEUFIG (%s)" % r[2][:70], r[1] == "vorlaeufig" and "15:22" in r[2])
    L4 = copy.deepcopy(L); L4[9] = e(3, 2, 260, 310)
    pruefe(4, "ein Arbeiter mehr bis 45 -> VORLAEUFIG", bed(L4, G)[1] == "vorlaeufig")
    L5 = copy.deepcopy(L); L5[10] = e(24, 2, 390, 100)
    pruefe(5, "eine Einheit mehr weiter als 45 -> belegt (nur mitgeschrieben)", bed(L5, G)[1] == "belegt")
    G6 = copy.deepcopy(G); G6[52] = {"besitzer": 2, "typ": 10, "x": 236, "y": 290}
    pruefe(6, "ein Gebaeude mehr bis 15 -> VORLAEUFIG", bed(L, G6)[1] == "vorlaeufig")
    L7 = copy.deepcopy(L); L7[1]["leben"] = 160000
    L7b = copy.deepcopy(L); L7b[1]["x"] += 4
    pruefe(7, "Lord staerker / 4 Felder woanders -> VORLAEUFIG", bed(L7, G)[1] == "vorlaeufig" and bed(L7b, G)[1] == "vorlaeufig")
    gem2 = dict(gem, name="Messlage 2", mindest=15)
    pruefe(8, "zwei deckende Lagen -> die kleinere Zahl", bed(L, G, (gem, gem2))[0] == 15)
    n, art, grund, gl = bed(L, G, ())
    pruefe(9, "keine Lage gemessen -> VORLAEUFIG %s (%s)" % (n, grund), (n, art, gl) == (B.VORLAEUFIG, "vorlaeufig", None)
           and "noch keine Lage" in grund)
    L10 = copy.deepcopy(L); del L10[1]
    pruefe(10, "kein feindlicher Lord -> kein Bedarf", bed(L10, G)[0] is None)
    L11 = copy.deepcopy(L)
    for i in range(30):
        L11[700 + i] = e(1, 2, LORD[0] + 2, LORD[1] + 2)
    pruefe(11, "30 Bauern mehr am Lord -> belegt (Bauern werden nicht verglichen, Daniel 06.10. 19:33)", bed(L11, G)[1] == "belegt")
    print("\n%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
