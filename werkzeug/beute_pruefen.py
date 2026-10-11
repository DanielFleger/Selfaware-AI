# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer 3b "Beute" (Daniel 12.10. 00:44: "erkennen, wenn Fernkaempfer sich auf dem Boden bewegen und
damit im Nahkampf einfach zu snacken sind"). Vorher festgelegt, was gelten muss:
  1. Feindlicher Bogenschuetze (22) am Boden, 6 Felder neben einem freien Assassinen, kein Nahkaempfer dabei -> JAGD auf ihn,
     Angriffsbefehl auf die Einheit, das Gebaeudeziel wird aufgegeben
  2. derselbe Schuetze 2 Felder neben einem feindlichen Wachturm (Laufzeit-Typ 74) -> KEINE Jagd (er steht oben)
  3. Schuetze mit 2 feindlichen Nahkaempfern im Umkreis 5 -> KEINE Jagd (bewacht)
  4. Schuetze 3 Felder neben ihrem Lord -> KEINE Jagd
  5. Schuetze 30 Felder weg (> BEUTE_R) -> KEINE Jagd
Aufruf: python werkzeug/beute_pruefen.py [andere_assassinen.py]   (Rueckgabe 0 = gruen)
"""
import importlib.util, os, sys
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
if len(sys.argv) > 1:                                   # Gegenprobe gegen eine andere Fassung
    spec = importlib.util.spec_from_file_location("assassinen", sys.argv[1])
    A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
else:
    import assassinen as A
from ausweichen_pruefen import einheit, ORTE


def neu():
    return A.Einzeln(1, pruefe_begehbar=lambda pkt: set(pkt), wegtest=lambda n, p: [True] * len(p))


def lauf(L, G):
    t = neu()
    t.aufnehmen([100])
    bef = []
    for _ in range(2):                                  # zwei Runden; der Angriffsbefehl kommt in der Runde, in der er sie sieht
        bef += t.schritt(L, G, sichere_orte=ORTE)[1]
    jagd = t.jagd.get(100)
    befohlen = any(b.get("angriff", {}).get("ziel") == 600 and 100 in b["angriff"].get("einheiten", []) for b in bef)
    return jagd, befohlen, t


def main():
    ok = []
    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))
    G0 = {900: {"besitzer": 2, "typ": 32, "x": 230, "y": 270, "leben": 100, "uid": 1, "erreichbar": 1}}
    def szene(schuetze=(206, 270), extra=None, G=None):
        L = {100: einheit(73, 1, 200, 270), 600: einheit(22, 2, schuetze[0], schuetze[1], leben=5000)}
        L.update(extra or {})
        G1 = dict(G0); G1.update(G or {})
        return L, G1
    jagd, bef, t = lauf(*szene())
    pruefe(1, "Schuetze am Boden 6 Felder weg: Jagd %s, Angriffsbefehl %s, Gebaeudeziel %s" % (jagd, bef, t.ziel.get(100)),
           jagd == 600 and bef and 100 not in t.ziel)
    jagd, bef, _ = lauf(*szene(G={901: {"besitzer": 2, "typ": 74, "x": 207, "y": 271, "leben": 100, "uid": 2, "erreichbar": 1}}))
    pruefe(2, "Schuetze neben Wachturm (Typ 74): keine Jagd (%s)" % jagd, jagd != 600)
    jagd, bef, _ = lauf(*szene(extra={601: einheit(26, 2, 211, 270, leben=10000), 602: einheit(26, 2, 211, 271, leben=10000)}))
    pruefe(3, "Schuetze mit 2 Nahkaempfern: keine Jagd (%s)" % jagd, jagd != 600)
    jagd, bef, _ = lauf(*szene(extra={700: einheit(55, 2, 209, 270, leben=1500000)}))
    pruefe(4, "Schuetze 3 Felder neben ihrem Lord: keine Jagd (%s)" % jagd, jagd != 600)
    jagd, bef, _ = lauf(*szene(schuetze=(230, 270)))
    pruefe(5, "Schuetze 30 Felder weg: keine Jagd (%s)" % jagd, jagd != 600)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
