"""B-254 Brotkette nach Bedarf (Daniel 26.10.2026 23:08 "warum nutzt sie nicht den Weizen fuer noch mehr Brot"; Partie 230627
Sp2: 1 Getreidefarm fuer 6 Baeckereien, Weizen/Mehl im Lager fast immer 0).

1 steht die Kette mit 1 Farm und 6 Baeckereien -> eine weitere Getreidefarm wird bestellt (Soll laut Nahrungsmodell)
2 mit so vielen Farmen wie das Soll -> nichts mehr
3 Weizen staut sich (>= WEIZEN_STAU) und weniger Muehlen als Farmen -> eine Muehle
4 bedarf() legt Holz fuer die fehlende Farm zurueck (damit der Holzkauf greift)
Gegenprobe: MEHR_FARMEN = 0 -> keine Farm (Fall 1 rot)."""
import sys
import unittest

import brotbau as BB

LAGER, KS, FARM = (100, 100), (108, 100), (70, 100)


def kette(farmen, muehlen=1, baeck=6):
    G, nr = {}, 1
    for typ, n, ort in ((30, farmen, FARM), (34, muehlen, LAGER), (17, baeck, LAGER), (19, 1, LAGER)):
        for i in range(n):
            G[nr] = {"typ": typ, "besitzer": 1, "x": ort[0] + i, "y": ort[1]}
            nr += 1
    return G


def lenker():
    gebaut = []
    b = BB.BrotBau({"getreide": [list(FARM)], "baeckereien": 6, "ab_tick": 0}, 1, LAGER, KS,
                   lambda typ, x, y, r: gebaut.append(typ) or (x, y), lambda typ: {"holz": 10, "gold": 0})
    b.fertig = True
    return b, gebaut


class BrotNachBedarf(unittest.TestCase):
    def test_1_mehr_farm(self):
        b, gebaut = lenker()
        soll = b.farmen_soll(b._steht(kette(1)))
        m = b.schritt(1000, {"holz": 100, "gold": 500, "weizen": 0}, kette(1))
        self.assertGreaterEqual(soll, 2, "Soll %d" % soll)
        self.assertEqual(gebaut, [30], m)

    def test_2_soll_erreicht(self):
        b, gebaut = lenker()
        soll = b.farmen_soll(b._steht(kette(1)))
        b.schritt(1000, {"holz": 100, "gold": 500, "weizen": 0}, kette(soll, muehlen=soll))
        self.assertEqual(gebaut, [])

    def test_3_muehle_bei_stau(self):
        b, gebaut = lenker()
        b.schritt(1000, {"holz": 100, "gold": 500, "weizen": BB.WEIZEN_STAU}, kette(2, muehlen=1))
        self.assertEqual(gebaut[:1], [34])

    def test_4_ruecklage(self):
        b, _ = lenker()
        self.assertEqual(b.bedarf(1000, kette(1)), {"holz": 10, "gold": 0})


if __name__ == "__main__":
    if "--gegenprobe" in sys.argv:
        sys.argv.remove("--gegenprobe")
        BB.MEHR_FARMEN = 0
    unittest.main()
