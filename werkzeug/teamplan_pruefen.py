"""B-210: recorded north-side failure, both players, tie and impossible placement."""
import json
import pathlib
import sys
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import land
import nahrungswahl as food

class TeamplanTest(unittest.TestCase):
    def test_tie_has_exactly_one_owner(self):
        keeps = {1: (0, 0), 2: (10, 0)}
        self.assertEqual(land.besitzer((5, 0), keeps), 1)
        self.assertEqual(land.besitzer((5, 0), dict(reversed(list(keeps.items())))), 1)

    def test_no_coordinate_invented_when_no_storage_fits(self):
        fake = types.ModuleType('farmen_mischen')
        fake.lies_karte = lambda path: {(10, 10)}
        with patch.dict(sys.modules, farmen_mischen=fake):
            with self.assertRaisesRegex(ValueError, 'KEIN GUELTIGER'):
                food.speicherplatz('blocked', (99, 99), [(10, 10, 10)])
            with self.assertRaisesRegex(ValueError, 'KEIN GUELTIGER'):
                food.speicherplatz('foreign', (99, 99), [], lambda p: False)

    def test_recorded_north_side_planning_before_allocation(self):
        import eroeffnung
        import numpy  # Native modules must outlive patch.dict(sys.modules).
        root = pathlib.Path(__file__).resolve().parent.parent
        cat = json.loads((root.parent / 'VillageStudio/lib/gebaeude.json').read_text(encoding='utf-8'))['gebaeude']
        fake = types.ModuleType('bauen')
        fake.NACH_TYP = {g['laufzeit']: g for g in cat.values() if 'laufzeit' in g and 'mapper' in g}
        for key in ('M19_pl2-3-0-1_2v2', 'M19_pl3-2-0-1_2v2'):
            with self.subTest(player=key), patch.dict(sys.modules, bauen=fake):
                info = json.loads((root / 'daten' / ('start_' + key + '.json')).read_text(encoding='utf-8'))
                allowed = land.eigene_seite(info)
                plan = eroeffnung.plane(K=14, A=0, start=key)
                self.assertNotIn('fehler', plan)
                result = food.waehle(key, plan, horizont=900000)
                self.assertTrue(result['aepfel'] or result['jaeger'] or result['brot'])
                self.assertTrue(all(allowed(p) for p in result['aepfel'] + [result['kornspeicher']] + plan['holzfaeller']))
                from farmen_mischen import lies_karte
                valid = lies_karte(root / 'daten' / ('start_' + key + '_platz_speicher.txt'))
                self.assertIn(tuple(result['kornspeicher']), valid)

if __name__ == '__main__':
    unittest.main()
