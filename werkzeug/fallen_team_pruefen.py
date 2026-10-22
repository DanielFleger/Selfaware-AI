import unittest
from fallenwache import Fallenwache


class TeamFallenProbe(unittest.TestCase):
    def test_allied_assassin_passes_enemy_gets_trap(self):
        buildings = {1: {'besitzer': 1, 'typ': 19, 'x': 10, 'y': 10}}
        unit = {'besitzer': 2, 'typ': 73, 'leben': 12500, 'x': 20, 'y': 10, 'laufx': 11, 'laufy': 10}
        orders = []
        guard = Fallenwache(1, lambda x, y: orders.append((x,y)) or True, freunde={0,1,2})
        self.assertEqual(guard.schritt(100, {1: unit}, buildings, 100), [])
        self.assertEqual(orders, [])
        unit = dict(unit, besitzer=3)
        self.assertTrue(guard.schritt(101, {1: unit}, buildings, 100))
        self.assertEqual(orders, [(11,10)])


if __name__ == '__main__':
    unittest.main()
