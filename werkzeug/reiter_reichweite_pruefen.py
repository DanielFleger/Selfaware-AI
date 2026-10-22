import unittest
import raids,parteien
parteien.setzen(1,{1})
def unit(typ,sp,x,y):return {'typ':typ,'besitzer':sp,'x':x,'y':y,'leben':15000,'zustand':1,'zieleinheit':0}
class Reichweite(unittest.TestCase):
 def run_scene(self,d,typ=72):
  L={1:unit(74,1,100,100),2:unit(typ,2,100+d,100)};commands=[]
  r=raids.Reiterjagd(1,raten={});r.schritt(L,{},lambda b,*a,**k:commands.append(b));return r,commands,L
 def test_shoot_outside_slinger_range_without_advancing(self):
  r,cmd,L=self.run_scene(26)
  self.assertEqual(r.befohlen[1][:2],('jagd',2));self.assertEqual(cmd[-1]['angriff']['ziel'],2)
 def test_escape_before_slinger_targets_us(self):
  r,cmd,L=self.run_scene(15)
  self.assertEqual(r.befohlen[1][0],'abstand')
  q=r.befohlen[1][1];self.assertGreaterEqual(raids.schach(q,(115,100)),21)
 def test_far_slinger_approach_ends_at_firing_position(self):
  r,cmd,L=self.run_scene(60)
  self.assertEqual(r.befohlen[1][0],'anritt')
  a=cmd[-1]['angriff'];q=(a.get('danach') or [a['lauf']])[-1]
  self.assertGreaterEqual(raids.schach(q,(160,100)),21);self.assertLessEqual(raids.schach(q,(160,100)),39)
 def test_equal_range_does_not_claim_advantage(self):
  import gefahrenschutz as g
  lage=g.Lage({}, {},lambda _:True,{},raten={})
  self.assertIsNone(raids.reichweitenposition(lage,(100,100),(120,100),44,44))
 def test_ally_slinger_is_not_threat(self):
  parteien.setzen(1,{1,2})
  try:
   r,cmd,L=self.run_scene(15);self.assertFalse(cmd)
  finally:parteien.setzen(1,{1})
if __name__=='__main__':unittest.main()
