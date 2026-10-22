import unittest,numpy as np
import gefahrenschutz as GS
import gefahr as GF
from weggraph import LinkSuche,linie_erlaubt

class Hoehen(unittest.TestCase):
    def karte(self,rampe=True):
        n=12;links=np.zeros((n,n),np.uint8)
        from weggraph import RICHTUNGEN
        for x in range(n):
            for y in range(n):
                for bit,dx,dy in RICHTUNGEN:
                    xx,yy=x+dx,y+dy
                    if not(0<=xx<n and 0<=yy<n):continue
                    # Klippe zwischen x5 und x6, Aufgang nur bei y10
                    if (x<=5)!=(xx<=5) and not(rampe and y==10 and yy==10):continue
                    links[x,y]|=bit
        return {'link':links,'gebiet':np.ones((n,n),np.int32),'gebaeude':np.zeros((n,n),np.int32)}
    def test_ramp_instead_of_cliff(self):
        k=self.karte();lage=GS.Lage({}, {},lambda _:True,{},n=12,raten={},wegkarte=k)
        p=lage.plan((4,3),(7,3),71,6000)
        self.assertTrue(linie_erlaubt(p['weg'],k['link']))
        self.assertIn((5,10),p['weg']);self.assertIn((6,10),p['weg'])
    def test_no_ramp_no_reachable_opposite_tile(self):
        k=self.karte(False);m=LinkSuche(np.ones((12,12)),k['link'],(4,3))
        self.assertFalse(np.isfinite(m.kum[7,3]))
    def test_direction_is_not_symmetric(self):
        k=np.zeros((3,3),np.uint8);k[1,1]=4
        a=LinkSuche(np.ones((3,3)),k,(1,1));b=LinkSuche(np.ones((3,3)),k,(2,1))
        self.assertTrue(np.isfinite(a.kum[2,1]));self.assertFalse(np.isfinite(b.kum[1,1]))
    def test_smoothing_keeps_ramp(self):
        k=self.karte();karte=GF.Karte([],n=12,gebiete=k['gebiet'],links=k['link'])
        w=GF.sicherer_weg((4,3),(7,3),karte);a=(4,3)
        for b in w:
            self.assertTrue(linie_erlaubt(karte.linie(a,b),k['link']));a=b
        self.assertEqual(a,(7,3))
    def test_flat_direct_path_still_works(self):
        k=self.karte();k['link'][:]=255
        m=LinkSuche(np.ones((12,12)),k['link'],(4,3))
        self.assertEqual(len(m.traceback((7,3))),4)
    def test_building_cannot_be_attacked_across_cliff(self):
        k=self.karte(False)
        k['gebaeude'][6,3]=99
        k['boden']=np.zeros((12,12),np.uint8);k['boden'][6:,:]=40
        lage=GS.Lage({}, {},lambda _:True,{},n=12,raten={},wegkarte=k)
        self.assertIsNone(lage.plan((4,3),(6,3),71,6000,gebaeude=99))
    def test_waypoint_uses_exact_arrival_for_native_path(self):
        k=self.karte();lage=GS.Lage({}, {},lambda _:True,{},n=12,raten={},wegkarte=k)
        p=lage.plan((4,3),(7,3),71,6000)
        self.assertEqual(GS.lauf_befehl(lage,1,p)['angriff']['weg_radius'],0)
if __name__=='__main__':unittest.main()
