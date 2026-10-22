import unittest
from assassinen import Einzeln
class GemeinsamerAngriff(unittest.TestCase):
 def setUp(self):
  self.t=object.__new__(Einzeln);self.t._feindburg=[(100,100)]
  self.L={i:{'x':90,'y':100,'leben':12500,'typ':73,'besitzer':1} for i in range(1,16)}
  self.L[20]={'x':100,'y':100,'leben':10000,'typ':22,'besitzer':2,'erreichbar':1}
  self.f=[(20,(100,100),22)]
 def test_near_lord_is_considered_for_combat_calculation(self):
  self.assertTrue(self.t._stapel_kandidaten(set(range(1,16)),self.f,self.L))
 def test_unreachable_is_not_considered(self):
  self.L[20]['erreichbar']=0
  self.assertFalse(self.t._stapel_kandidaten(set(range(1,16)),self.f,self.L))
 def test_small_group_is_not_committed(self):
  self.assertFalse(self.t._stapel_kandidaten({1,2},self.f,self.L))
if __name__=='__main__':unittest.main()
