"""B-268 (Partie 175718 'Riverside Rampage', Daniel 27.10.2026: Zugang (174,341) dreimal in einer Runde verworfen und dreimal
wieder geplant): eine verworfene Kachel im Rand eines Turms muss auch fuer den Torhaus/Turm-Kandidaten gesperrt bleiben.
Prueft die Verdrahtung: der Torhaus-Kandidat bekommt die verworfene Kachel als gesperrt und nicht als 'frei'.
Gegenprobe (Negativlauf 27.10.): mit der alten Zeile (sperre & ~rand) ist sie frei -> rot."""
import sys
import unittest

import numpy as np

import durchbruch as D

N = 40


class Verworfen(unittest.TestCase):
    def test_bleibt_gesperrt(self):
        bau = np.zeros((N, N), np.int64)
        bau[20:24, 20:24] = 7                                   # Turm Typ 75, 4x4
        e = {"link": np.full((N, N), 0xFF, np.int64), "logik": np.zeros((N, N), np.int64), "bau": bau,
             "besitz": np.ones((N, N), np.int64), "hoehe": np.zeros((N, N), np.int64), "boden": np.zeros((N, N), np.int64)}
        G = {7: {"typ": 75, "besitzer": 2, "x": 20, "y": 20, "leben": 1500}}
        kachel = (24, 21)                                       # im Rand (2 Felder) des Turms
        aufrufe = []
        alt = D.mechanik.durchbruch_schritte
        D.mechanik.durchbruch_schritte = lambda *a, **k: aufrufe.append(k) or {"weg": None, "mauern": [], "takte": None}
        try:
            D.plane(1, (2, 2), 10, (35, 35), mk={"mauer": 30, "takte_je_treffer": 40, "tor_turm": 20, "gebaeude": 40},
                    L={}, G=G, gf=np.zeros((N, N)), verworfen={kachel}, e=e)
        finally:
            D.mechanik.durchbruch_schritte = alt
        tor = [k for k in aufrufe if k.get("frei") is not None]
        self.assertTrue(tor, "kein Torhaus/Turm-Kandidat gerechnet")
        self.assertTrue(tor[0]["sperre"][kachel], "verworfene Kachel im Turmrand ist fuer den Turm-Kandidaten frei")
        self.assertFalse(tor[0]["frei"][kachel], "verworfene Kachel steht im 'frei'-Bereich")


if __name__ == "__main__":
    unittest.main()
