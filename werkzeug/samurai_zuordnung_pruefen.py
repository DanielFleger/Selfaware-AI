import copy,unittest,yaml
from pathlib import Path
from samurai_wache import konfigurierte_ki,auswahl
class Zuordnung(unittest.TestCase):
 def config(self,slot):
  return {'config-full':{'modules':{'aiSwapper':{'config':{'ai':{slot:{'lines':{'contents':{'value':{'active':True,'name':'SamurAI','root':'ucp/resources/ai/SamurAI/'}}}}}}}}}}
 def test_abbot_is_16(self):self.assertEqual(konfigurierte_ki(self.config('abbot')),16)
 def test_rat_still_supported(self):self.assertEqual(konfigurierte_ki(self.config('rat')),1)
 def test_never_hijack_rotkaeppchen(self):self.assertEqual(auswahl({1:0,2:1,3:9,4:10},16),[])
 def test_two_samurai(self):self.assertEqual(auswahl({1:0,2:16,3:16,4:9,5:10},16),[2,3])
 def test_explicit_team_test(self):self.assertEqual(auswahl({1:0,2:16,3:9,4:10},16,True),[1,2])
 def test_ambiguous_rejected(self):
  c=self.config('abbot');c['config-full']['modules']['aiSwapper']['config']['ai'].update(self.config('rat')['config-full']['modules']['aiSwapper']['config']['ai'])
  with self.assertRaises(RuntimeError):konfigurierte_ki(c)
if __name__=='__main__':unittest.main()
