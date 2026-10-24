"""Two independent runtime copies must share one game channel and ID store."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class Kanal(unittest.TestCase):
    def exercise(self, legacy=False):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);game=root/'game';game.mkdir()
            workers=[]
            for i in range(2):
                code=root/str(i);code.mkdir()
                for name in ('befehl.py','kanalsperre.py'):
                    shutil.copy2(Path(__file__).parent/name,code/name)
                script='import befehl,json;befehl.time.time=lambda:1000000;'
                if legacy:
                    script+='befehl.MERKER='+repr(str(code/'.legacy_ids'))+';'
                script+="print(json.dumps({'ids':[befehl.neue_id() for _ in range(1024)],'lock':befehl.SENDE,'owner':befehl.LAUF}))"
                env=dict(os.environ,SHC_GAME_DIR=str(game),SHC_INSTANZ=str(i+1),SHC_SPIELER='1')
                workers.append(subprocess.Popen([sys.executable,'-c',script],cwd=code,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True))
            results=[]
            for p in workers:
                out,err=p.communicate(timeout=20)
                self.assertEqual(p.returncode,0,err)
                results.append(json.loads(out))
            return results

    def test_one_game_two_copies(self):
        a,b=self.exercise()
        self.assertEqual(a['lock'],b['lock'])
        self.assertEqual(a['owner'],b['owner'])
        self.assertFalse(set(a['ids']) & set(b['ids']))

    def test_counterexample_detects_old_per_copy_ids(self):
        a,b=self.exercise(legacy=True)
        self.assertTrue(set(a['ids']) & set(b['ids']))


if __name__=='__main__':unittest.main()
