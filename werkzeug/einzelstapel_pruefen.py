import unittest
import feldzug as F
from feldzug_pruefen import einheit,Befehle
class Einzelstapel(unittest.TestCase):
 def scene(self):
  f=F.Feldzug(1,(80,260),lord_schutz_bis=0,n=10);f.ziel=500;f.phase='angriff';f.punkt=(280,100);f.wegtest=lambda nr,p:[True]*len(p)
  L={500:einheit(55,2,300,100,150000)};L.update({n:einheit(75,1,297,100,28000) for n in range(10,20)})
  return f,L
 def test_nearby_units_move_individually_to_exact_same_point(self):
  f,L=self.scene();b=Befehle();f.schritt({'t':20000},L,{},b)
  moves=[x['angriff'] for x in b.liste if 'lauf' in x.get('angriff',{})]
  self.assertTrue(moves);self.assertTrue(all(x['lauf']==[300,100] and x.get('trupp')==1 for x in moves))
  self.assertEqual(set(n for x in moves for n in x['einheiten']),set(range(10,20)))
 def test_arrived_units_attack_individually(self):
  f,L=self.scene()
  for n in range(10,20):L[n]['x']=300
  b=Befehle();f.schritt({'t':20000},L,{},b)
  attacks=[x['angriff'] for x in b.liste if x.get('angriff',{}).get('ziel')==500]
  self.assertTrue(attacks);self.assertTrue(all(x.get('trupp')==1 for x in attacks))
 def test_home_guard_is_not_sent(self):
  f,L=self.scene();f.heimwache={10};b=Befehle();f.schritt({'t':20000},L,{},b)
  self.assertNotIn(10,{n for x in b.liste for n in x.get('angriff',{}).get('einheiten',[])})
if __name__=='__main__':unittest.main()
