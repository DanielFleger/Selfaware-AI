import sys,unittest
from unittest.mock import patch
sys.path.insert(0,'werkzeug')
import raids,parteien
import gefahrenschutz as GS
parteien.setzen(1,{1})
def e(t,sp,x,y):return dict(typ=t,besitzer=sp,x=x,y=y,leben=15000,zustand=1,zieleinheit=0)
class Safety(unittest.TestCase):
 def test_no_firing_spot_does_not_fall_through_to_attack(self):
  L={1:e(74,1,100,100),2:e(72,2,110,100),3:e(3,2,101,101)};cmd=[]
  with patch.object(raids,'reichweitenposition',return_value=None):
   raids.Reiterjagd(1,raten={}).schritt(L,{},lambda b,*a,**kw:cmd.append(b))
  self.assertTrue(cmd)
  self.assertTrue(all('ziel' not in c['angriff'] for c in cmd))
 def test_worker_firing_position_keeps_distance(self):
  l=GS.Lage({}, {},lambda _:True,{},raten={})
  p=raids.reichweitenposition(l,(100,100),(160,100),44,0)
  self.assertGreaterEqual(raids.schach(p['an'],(160,100)),32)
if __name__=='__main__':unittest.main()
