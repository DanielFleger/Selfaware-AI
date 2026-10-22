"""Echte Karten: laufender Planer darf nicht erst beim Bauen Partnerland erkennen."""
import json
import pathlib
import unittest
from ertragsplaner import Ertragsplaner
from land import eigene_seite


class GebietsProbe(unittest.TestCase):
    def test_both_recorded_territories(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        for key in ('LigaBranchingFortunes_pl0-1-2-3_2v2', 'LigaBranchingFortunes_pl1-0-2-3_2v2'):
            with self.subTest(key=key):
                info = json.loads((root/'daten'/('start_'+key+'.json')).read_text(encoding='utf-8'))
                plan = json.loads((root/'daten'/('eroeffnung_plan_'+key+'.json')).read_text(encoding='utf-8'))
                planner = Ertragsplaner(plan, info['spieler'], None, None, None, kosten={}, groesse={})
                erlaubt = eigene_seite(info)
                self.assertTrue(planner.platz[32])
                for points in planner.platz.values():
                    self.assertTrue(all(erlaubt(p) for p in points))
                self.assertTrue(all(erlaubt(p) for p in planner.baeume_faellbar))
                # Im ersten echten Lauf wiederholt vorgeschlagen, gehoert aber dem Partner.
                if info['spieler'] == 1:
                    self.assertFalse(planner.eigene_seite((305, 260)))
                    self.assertTrue(planner.eigene_seite((193, 356)))


if __name__ == '__main__':
    unittest.main()
