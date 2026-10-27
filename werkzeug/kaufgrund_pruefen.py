# -*- coding: utf-8 -*-
"""B-276 Kaufgrund pruefen (Daniel 27.10. 23:00 "ohne Grund werden Berittene gebaut, es muss auch ein Kaufgrund geloggt werden").
Soll vorher festgelegt: (1) raids.werbung liefert je Eintrag genau einen Grund mit Soll, Bestand und der Grenze, die die Zahl
bestimmt hat; (2) der Spaeher-Kauf sagt, dass er ein Spaeher ist; (3) jede Werbe-Meldung in erstes_spiel.py traegt "Grund:".
Aufruf: python kaufgrund_pruefen.py"""
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import raids as R


def fall(gold, feuer, sklaven, reiter, ziele):
    g = []
    w = R.werbung(gold, feuer, sklaven, reiter, reiter_ziele=ziele, gruende=g)
    return w, g


if __name__ == "__main__":
    w1, g1 = fall(100, 10, 0, 0, None)            # Partie 225742 Anfang: Sklaven + ein Spaeher
    w2, g2 = fall(400, 10, 5, 1, 3)               # Reiterjagd sah 3 Ziele, 1 Reiter da -> 2 neue, Grenze Soll
    w3, g3 = fall(80, 10, 5, 1, 3)                # nur Gold fuer einen -> Grenze Gold
    w4, g4 = fall(400, 10, 5, 1, 1)               # 1 Ziel, 1 Reiter -> kein Kauf, kein Grund
    quelle = open(os.path.join(HIER, "erstes_spiel.py"), encoding="utf-8").read()
    meldungen = re.findall(r'ereignis\.append\("[A-Z-]*WERBUNG:[^\n]*(?:\n[^\n]*){0,2}', quelle)
    ohne = [m.split("\n")[0].strip()[:70] for m in meldungen if "Grund" not in m]
    faelle = [
        ("je Werbung genau ein Grund", len(g1) == len(w1) == 2 and len(g2) == len(w2) == 1 and len(g3) == len(w3) == 1),
        ("Sklaven-Grund nennt Soll und Bestand", "Soll 5 Sklaven, da 0" in g1[0]),
        ("Spaeher-Kauf sagt Spaeher", g1[1].startswith("Spaeher")),
        ("Reiterkauf nennt gesehene Ziele und Reiter", "sah zuletzt 3" in g2[0] and "1 Reiter da" in g2[0]),
        ("Grenze Soll erkannt", g2[0].endswith("Grenze: Soll")),
        ("Grenze Gold erkannt", g3[0].endswith("Grenze: Gold")),
        ("kein Kauf -> kein Grund", w4 == [] and g4 == []),
        ("ohne gruende-Liste unveraendert", R.werbung(400, 10, 5, 1, reiter_ziele=3) == w2),
        ("alle %d Werbe-Meldungen in erstes_spiel tragen 'Grund'%s" % (len(meldungen), (" - ohne: %s" % ohne) if ohne else ""),
         len(meldungen) >= 3 and not ohne),
    ]
    for name, ok in faelle:
        print("%s %s" % ("OK  " if ok else "ROT ", name))
    print("%d von %d gruen" % (sum(ok for _, ok in faelle), len(faelle)))
    sys.exit(0 if all(ok for _, ok in faelle) else 1)
