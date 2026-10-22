import unittest
import raids,assassinen,parteien
from gebaeudeziele import angreifbar
parteien.setzen(1,{1})
class Gebaeudeziele(unittest.TestCase):
 def test_native_stockpile_immune(self):self.assertFalse(angreifbar({'typ':10}))
 def test_quarry_and_its_pile_differ(self):
  self.assertTrue(angreifbar({'typ':20}));self.assertFalse(angreifbar({'typ':21}))
 def test_keep_immune_but_granary_and_armory_damageable(self):
  self.assertFalse(angreifbar({'typ':41}));self.assertTrue(angreifbar({'typ':19}));self.assertTrue(angreifbar({'typ':11}))
 def test_closest_stockpile_cannot_displace_real_target(self):
  b=raids.Brandtrupp(1,lambda _:0)
  g={100:{'typ':10,'besitzer':2,'x':101,'y':100},101:{'typ':21,'besitzer':2,'x':103,'y':100},102:{'typ':20,'besitzer':2,'x':110,'y':100},103:{'typ':11,'besitzer':2,'x':120,'y':100}}
  result={r[2] for r in b._kandidaten({},g,set())}
  self.assertNotIn(100,result);self.assertNotIn(101,result);self.assertIn(103,result)
 def test_shared_values(self):
  for values in (raids.WERT,assassinen.WERT):
   self.assertNotIn(10,values);self.assertNotIn(21,values);self.assertIn(11,values)
if __name__=='__main__':unittest.main()
