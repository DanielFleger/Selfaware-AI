import copy,unittest,yaml
from pathlib import Path
from samurai_wache import konfigurierte_ki,auswahl
class Zuordnung(unittest.TestCase):
 def config(self,slot):
  return {'config-full':{'modules':{'aiSwapper':{'config':{'ai':{slot:{'lines':{'contents':{'value':{'active':True,'name':'SamurAI','root':'ucp/resources/ai/SamurAI/'}}}}}}}}}}
 def test_abbot_is_16(self):self.assertEqual(konfigurierte_ki(self.config('abbot')),16)
 def test_versioned_store_content_is_recognized(self):
  for version in ('0.1.0','0.2.0','1.10.4'):
   c=self.config('abbot');c['config-full']['modules']['aiSwapper']['config']['ai']['abbot']['lines']['contents']['value']['root']='ucp/plugins/Selfaware-AI-'+version+'/resources/ai/SamurAI/'
   self.assertEqual(konfigurierte_ki(c),16)
 def test_rat_still_supported(self):self.assertEqual(konfigurierte_ki(self.config('rat')),1)
 def test_resolved_ucp_null_entries_are_not_treated_as_selected_ai(self):
  c=self.config('abbot');c['config-full']['modules']['aiSwapper']['config']['ai'].update(rat=None,wolf={'lines':None},snake={'lines':{'contents':None}})
  self.assertEqual(konfigurierte_ki(c),16)
 def test_never_hijack_rotkaeppchen(self):self.assertEqual(auswahl({1:0,2:1,3:9,4:10},16),[])
 def test_two_samurai(self):self.assertEqual(auswahl({1:0,2:16,3:16,4:9,5:10},16),[2,3])
 def test_explicit_team_test(self):self.assertEqual(auswahl({1:0,2:16,3:9,4:10},16,True),[1,2])
 def test_ambiguous_rejected(self):
  c=self.config('abbot');c['config-full']['modules']['aiSwapper']['config']['ai'].update(self.config('rat')['config-full']['modules']['aiSwapper']['config']['ai'])
  with self.assertRaises(RuntimeError):konfigurierte_ki(c)
if __name__=='__main__':unittest.main()
