import copy
import unittest
from benchmark_auswerten import auswerten


class ErgebnisProbe(unittest.TestCase):
    def setUp(self):
        self.profil = {'our_players': [1, 2], 'enemy_players': [3, 4], 'enemy_ai_ids': [7, 8],
                       'evaluation': {'minimum_own_lord_health_fraction': .9, 'median_win_tick_max': 28800}}
        self.start = {'tick': 500, 'over': 0, 'view': 14, 'alive': [0]*8,
                      'ai': [0, 0, 7, 8, 0, 0, 0, 0], 'coherent': True,
                      'lords': {str(sp): {'uid': 10+sp, 'health': 150000} for sp in range(1, 5)}}
        self.end = copy.deepcopy(self.start)
        self.end.update(tick=32347, over=1, alive=[1, 1, 0, 0, 0, 0, 0, 0])
        self.end['lords'] = {sp: self.end['lords'][sp] for sp in ('1', '2')}

    def test_win_is_not_speed_pass_or_qualification(self):
        r = auswerten([self.start, self.end], self.profil)
        self.assertEqual(r['observed_result'], 'win')
        self.assertTrue(r['observed_dominant_win'])
        self.assertFalse(r['within_median_target_tick'])
        self.assertFalse(r['evaluation_eligible'])

    def test_dead_enemies_without_gameover_is_not_win(self):
        self.end['over'] = 0
        self.assertEqual(auswerten([self.start, self.end], self.profil)['observed_result'], 'incomplete')

    def test_all_zero_alive_in_running_game_is_not_win(self):
        self.end['alive'] = [0]*8
        self.assertNotEqual(auswerten([self.start, self.end], self.profil)['observed_result'], 'win')

    def test_living_enemy_blocks_win(self):
        self.end['lords']['3'] = {'uid': 13, 'health': 1}
        self.assertNotEqual(auswerten([self.start, self.end], self.profil)['observed_result'], 'win')

    def test_bad_sources_rejected(self):
        for field, value in [('coherent', False), ('tick', 400), ('ai', [0]*8)]:
            end = copy.deepcopy(self.end)
            end[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                auswerten([self.start, end], self.profil)


if __name__ == '__main__':
    unittest.main()
