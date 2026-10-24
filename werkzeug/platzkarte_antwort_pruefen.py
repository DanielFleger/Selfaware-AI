"""Placement-map completion belongs to its own transaction, never a shared log."""
import ast,os,re,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch

SOURCE=Path(__file__).with_name('bauen.py')
node=next(n for n in ast.parse(SOURCE.read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef) and n.name=='platzkarte')


class PlacementReply(unittest.TestCase):
    def run_case(self,valid):
        with tempfile.TemporaryDirectory() as t:
            folder=Path(t);(folder/'platzkarte.txt').write_bytes(b'own map')
            calls=[]
            def command(value,timeout,bis):
                calls.append(value)
                return ['PLATZKARTE Mapper %d Groesse 4 (0,0)-(1,1): 2 von 4 gehen'%(72 if valid else 80)]
            scope={'NACH_TYP':{1:{'mapper':72,'b':4}},'befehl':command,'os':os,'re':re}
            exec(compile(ast.Module(body=[node],type_ignores=[]),str(SOURCE),'exec'),scope)
            # No LOG/SPIEL attribute exists: a shared file cannot influence it.
            with patch.dict(sys.modules,befehl=types.SimpleNamespace(ABZUG=str(folder))):
                if valid:
                    self.assertEqual(scope['platzkarte'](1,0,0,1,1,str(folder/'copied'))[:2],(2,4))
                    self.assertEqual((folder/'copied').read_bytes(),b'own map')
                else:
                    with self.assertRaisesRegex(RuntimeError,'eigene Fertig-Zeile fehlt'):
                        scope['platzkarte'](1,0,0,1,1,str(folder/'copied'))
                    self.assertFalse((folder/'copied').exists())
                self.assertEqual(len(calls),1)
    def test_correct_completion_needs_no_game_log(self):self.run_case(True)
    def test_other_building_completion_is_rejected(self):self.run_case(False)


if __name__=='__main__':unittest.main()
