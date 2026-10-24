import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lernbuch import Lernbuch, atomar, ausgang


class Lernen(unittest.TestCase):
    def test_native_team_outcome(self):
        self.assertEqual(ausgang(1,{1:0,2:1,3:4,4:0},1,[2,3]),'sieg')
        self.assertEqual(ausgang(1,{1:0,2:1,3:0},1,[2,3]),'unbestaetigt')
        self.assertEqual(ausgang(0,{1:0,2:1},1,[2]),'unbestaetigt')
        self.assertEqual(ausgang(1,{1:2,2:0},1,[2]),'niederlage')
        self.assertEqual(ausgang(1,{1:0},1,[]),'unbestaetigt')
        self.assertEqual(ausgang(1,{1:0,2:-1},1,[2]),'unbestaetigt')

    def test_learning_profile_follows_settings_not_yaml_key_order(self):
        from runtime_start import profilkennung
        self.assertEqual(profilkennung({'a':1,'b':2}),profilkennung({'b':2,'a':1}))
        self.assertNotEqual(profilkennung({'damage':1}),profilkennung({'damage':2}))

    def test_persisted_model_is_used_without_llm(self):
        import gefahrenschutz as gs
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            console=root/'run_sp1.txt'
            console.write_text('SIEG bei Tick 1\nHUNGER\nSTILLSTAND\n',encoding='utf-8')
            book=Lernbuch(root)
            run=book.beginnen(1,[2],console,{'karte':'A'})
            rates={'typen':{'71':{'verlust':1000,'vorhersage':500,'felder':100,'takte':900}}}
            atomar(root/'verlust_raten.json',rates)
            result=book.beenden(run,0,{1:0,2:1},100,'Spiel geschlossen')
            self.assertEqual(result['status'],'unbestaetigt') # console victory is not evidence
            self.assertEqual(result['beobachtungen']['HUNGER'],1)
            self.assertTrue(any('aktualisiert' in s for s in result['schluesse']))
            with patch.object(gs,'RATEN',str(root/'verlust_raten.json')):
                self.assertEqual(gs.faktor(gs.raten_laden(),71),(2.0,True))
                self.assertEqual(gs.takte_je_feld(gs.raten_laden(),71),(9.0,True))
            self.assertEqual(book.beenden(run,1,{1:0,2:1},100)['status'],'unbestaetigt')
            self.assertEqual(len(list((root/'lernen').glob('*.json'))),1)

    def test_corrupt_model_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'verlust_raten.json';p.write_text('{broken',encoding='utf-8')
            record=Lernbuch(temp).beginnen(1,[2],'none',{})
            self.assertIn('lesefehler',record['modell_vorher'])
            self.assertEqual(p.read_text(),'{broken')


if __name__=='__main__':unittest.main()
