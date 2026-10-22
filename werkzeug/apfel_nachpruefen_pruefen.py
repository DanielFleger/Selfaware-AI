"""Nachpruefung statt endgueltigem Vergessen; auch dauerhaft gesperrte Orte bleiben folgenlos."""
import unittest
import wirtschaft as W

class Nachpruefung(unittest.TestCase):
    def make(self):
        self.orders=[]
        self.free=False
        def bauen(typ,x,y,r,**kw):
            self.orders.append((x,y))
            return ((x,y), 'gebaut') if self.free else (None,'platz')
        w=W.Wirtschaft({'aepfel':[], 'lager':[0,0]},1,bauen,[])
        w.A=[(10,10)]
        w._a_baum=lambda: None
        return w
    def st(self,t):return {'t':t,'holz':30,'gold':150}
    def defer(self,w):
        for t in (0,750,1500):w.schritt(self.st(t),{}, {})
        self.assertFalse(w.A)
        self.assertIn(('A',(10,10)),w.apfel_pause)
    def test_a_later_free_confirm_only_real_building(self):
        w=self.make();self.defer(w);self.free=True
        w.schritt(self.st(3000),{}, {})
        self.assertEqual(len(self.orders),4)
        self.assertFalse(w.A) # Empfang eines Bauauftrags ist kein Gebaeude
        w.schritt(self.st(3010),{}, {1:{'typ':32,'besitzer':1,'x':10,'y':10}})
        self.assertEqual(w.A,[(10,10)])
        self.assertFalse(w.apfel_pause)
    def test_permanently_blocked_no_spam_or_reserve(self):
        w=self.make();self.defer(w)
        for t in range(1501,4500):w.schritt(self.st(t),{}, {})
        self.assertEqual(len(self.orders),4)
        self.assertEqual(w.ruecklage({}),{'gold':0,'holz':0})
        self.assertFalse(w.a_offen({}))
    def test_b_retries_and_real_confirmation(self):
        w=self.make();w.A=[];w.B=[(20,20)];w.apfel_pause[('B',(20,20))]=3000
        self.free=True
        w.schritt(self.st(3000),{}, {})
        self.assertIn(('B',(20,20)),w.apfel_pause)
        w.schritt(self.st(3010),{}, {8:{'typ':32,'besitzer':1,'x':20,'y':20}})
        self.assertFalse(w.apfel_pause)
        self.assertIn(8,w.b_vergeben)
    def test_resource_rejection_is_not_placement_failure(self):
        w=self.make()
        for t in range(0,6000,50):
            self.assertFalse(w._platz_aufgeben('A',(10,10),None,'rohstoff',t))
        self.assertFalse(getattr(w,'_fehl',{}))
    def test_reserved_money_is_not_spent(self):
        w=self.make();w.A=[];w.apfel_pause[('A',(10,10))]=0;w.extra={'gold':150}
        w.schritt(self.st(3000),{}, {})
        self.assertFalse(self.orders)

if __name__=='__main__':unittest.main()
