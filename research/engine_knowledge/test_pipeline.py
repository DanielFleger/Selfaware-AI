import copy
import json
from pathlib import Path
import unittest
import pipeline as p

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.f=json.loads((p.ROOT/'exports/reference/functions/00401000.json').read_text())
        self.exe=p.GAME/'Stronghold Crusader.exe'
    def test_original_bytes_and_boundary(self):
        p.validate_function(self.f)
        self.assertEqual(p.mapped_bytes(self.exe.read_bytes(),p.pe(self.exe),0x401000,54),bytes.fromhex(self.f['raw'][0]['hex']))
        with self.assertRaises(ValueError):p.mapped_bytes(self.exe.read_bytes(),p.pe(self.exe),0x3fffff,1)
    def test_modified_bytes_rejected(self):
        bad=copy.deepcopy(self.f);bad['raw'][0]['hex']='00'+bad['raw'][0]['hex'][2:]
        with self.assertRaisesRegex(ValueError,'corrupt'):p.validate_function(bad)
    def test_false_assembly_rejected(self):
        bad=copy.deepcopy(self.f);bad['assembly'][0]['bytes']='90'
        with self.assertRaisesRegex(ValueError,'assembly'):p.validate_function(bad)
    def test_rea_agrees_on_real_function_boundary(self):
        rea=json.loads((p.ROOT/'evidence/rea-function.json').read_text(encoding='utf-8-sig'))
        r=rea['normalized_result']
        self.assertEqual(int(r['procedure']['address'],16),int(self.f['address'],16))
        self.assertEqual(r['procedure']['body']['total_bytes'],self.f['size'])
        self.assertEqual(len(r['assembly']),len(self.f['assembly']))
        self.assertIn('400',r['pseudocode'])
        self.assertTrue(r['incoming_references'])
    def test_rule_invalidated_by_changed_dependency_or_version(self):
        rule=json.loads((p.ROOT/'rules.json').read_text())[0]
        self.assertEqual(p.rule_status(rule,rule['function_sha256'],rule['reference_sha256']),'confirmed')
        self.assertEqual(p.rule_status(rule,'changed',rule['reference_sha256']),'stale')
        self.assertEqual(p.rule_status(rule,rule['function_sha256'],'other-version'),'stale')
        rule['evidence_files'][0]['sha256']='changed'
        self.assertEqual(p.rule_status(rule,rule['function_sha256'],rule['reference_sha256']),'stale')

if __name__=='__main__':unittest.main()
