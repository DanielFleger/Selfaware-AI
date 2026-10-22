import unittest
from unittest.mock import patch
import feldzug as F,parteien

def unit(t,sp,x,y,hp=15000):return dict(typ=t,besitzer=sp,x=x,y=y,leben=hp,zustand=1,zielart=0,nahziel=0)
class NachSieg(unittest.TestCase):
 def scene(self):
  parteien.setzen(1,{1});f=F.Feldzug(1,(20,20),lord_schutz_bis=0,n=30)
  f.ziel=500;f._ziel_ort=(100,100);f.phase='angriff'
  L={n:unit(26,1,100,100) for n in range(1,31)}
  L[501]=unit(55,2,220,100,150000)
  return f,L
 def test_next_opponent_without_home_detour(self):
  f,L=self.scene();cmd=[];f._lohnt=lambda *a,**kw:(True,'Gegenprobe: ausreichend')
  out=f.schritt({'t':12000},L,{},lambda b,*a,**kw:cmd.append(b))
  self.assertEqual(f.ziel,501);self.assertEqual(f.phase,'angriff')
  self.assertTrue(any('ohne Heimat-Umweg' in s for s in out))
  for b in cmd:
   a=b.get('angriff',{})
   if 'lauf' in a:self.assertGreaterEqual(a['lauf'][0],100)
 def test_losing_force_does_not_bypass_combat_gate(self):
  f,L=self.scene();cmd=[];f._lohnt=lambda *a,**kw:(False,'Gegenprobe: verliert')
  f.schritt({'t':12000},L,{},lambda b,*a,**kw:cmd.append(b))
  self.assertEqual(f.phase,'sammeln')
  self.assertFalse(any('ziel' in b.get('angriff',{}) for b in cmd))
 def test_no_remaining_opponent_keeps_safe_exit(self):
  f,L=self.scene();del L[501];cmd=[]
  out=f.schritt({'t':12000},L,{},lambda b,*a,**kw:cmd.append(b))
  self.assertTrue(any('zum sicheren Punkt' in s for s in out));self.assertIsNone(f.ziel)
 def test_next_target_is_nearest_to_army_not_home(self):
  f,L=self.scene();L[501].update(x=130,y=100);L[502]=unit(55,3,20,60,150000)
  f._lohnt=lambda *a,**kw:(False,'wartet')
  f.schritt({'t':12000},L,{},lambda *a,**kw:None)
  self.assertEqual(f.ziel,501)
if __name__=='__main__':unittest.main()
