"""B-255 (Daniel 26.10.2026 23:10 "warum wird nicht die naehere Eisen oder Stein genutzt, sondern das weiter weg?").

Echte Karte der Partie 222338 (Lobby, Spieler 1, Bergfried 131/268, Lager um 177/232): die Eisenmine (143,310) scheiterte
zweimal mit "kein Platz im Umkreis 1". Bis B-255 sperrte das 8 Felder rundum - das naechste Erzfeld (Mitte 140/313, 122
Ankerplaetze) war bis auf 5 Plaetze in einer Ecke weg; die weiteren Minen kamen auf Felder 95-97 Felder vom Lager.

Gegenprobe: mit der alten Sperre (8 Felder) bleiben 5 Plaetze - der Vergleich neu > 2 x alt wird rot."""
import json
import pathlib
import unittest

from ertragsplaner import Ertragsplaner, schach

KURZ = "Lobby_sp1_bf_131_268"
ERZ_MITTE = (140, 313)         # naechstes Erzfeld zum Bergfried (Platzkarte, gemessen 26.10.)
FEHL = (143, 310)              # zweimal "kein Platz im Umkreis 1" (Partie 222338)


class _Wirt:
    alt, B_offen = set(), []


def planer():
    root = pathlib.Path(__file__).resolve().parents[1]
    plan = json.loads((root / "daten" / ("eroeffnung_plan_%s.json" % KURZ)).read_text(encoding="utf-8"))
    plan.setdefault("start", KURZ)
    p = Ertragsplaner(plan, 1, None, _Wirt(), None, kosten={}, groesse={5: 4, 20: 6, 3: 3, 31: 9, 32: 10})
    p.fehlschlag = {(5, FEHL): 1}
    return p


def im_naechsten_feld(p):
    # Lager (Typ 10) und Kornspeicher (Typ 19) wie in der Partie (Lage Tick 45.020), die erste Mine (139,317) stand schon
    G = {1: {"typ": 10, "besitzer": 1, "x": 175, "y": 230}, 2: {"typ": 19, "besitzer": 1, "x": 146, "y": 246},
         3: {"typ": 5, "besitzer": 1, "x": 139, "y": 317}}
    return [q for q in p._orte(5, {}, G) if schach(q, ERZ_MITTE) <= 8], G


class RohstoffPlatz(unittest.TestCase):
    def test_naechstes_erzfeld_bleibt(self):
        # gemessen 26.10.: mit der 8-Felder-Sperre blieben 5 Plaetze in einer Ecke des Feldes, mit 3 Feldern 25
        neu, G = im_naechsten_feld(planer())
        alt_p = planer()
        alt_p.SPERR_R_ROHSTOFF = 8
        alt, _ = im_naechsten_feld(alt_p)
        self.assertGreater(len(neu), 2 * len(alt), "neu %d, alt %d Plaetze im naechsten Erzfeld" % (len(neu), len(alt)))
        ort, weg = planer()._bester_ort(5, {}, G)
        self.assertLessEqual(schach(ort, ERZ_MITTE), 8, "beste Mine %s liegt nicht im naechsten Erzfeld" % (ort,))

    def test_gegenprobe_alte_sperre(self):
        p = planer()
        p.SPERR_R_ROHSTOFF = 8
        alt, _ = im_naechsten_feld(p)
        self.assertLessEqual(len(alt), 5, "alte Sperre: %d Plaetze (gemessen waren 5)" % len(alt))


if __name__ == "__main__":
    unittest.main()
