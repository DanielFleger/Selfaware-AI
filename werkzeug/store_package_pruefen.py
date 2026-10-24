"""Inspect the actual built Store ZIPs and separate external applications."""
from pathlib import Path
import json,struct,unittest,zipfile

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'build/store'


class StorePackages(unittest.TestCase):
    def test_native_module_is_x86_with_notices_and_no_external_runtime(self):
        with zipfile.ZipFile(BUILD/'selfaware-bridge-0.1.0.zip') as z:
            names=set(z.namelist())
            self.assertTrue({'LICENSE','init.lua','samurai_kern.dll'}<=names)
            self.assertIn('native-notices/Rust-standard-library.html',names)
            self.assertFalse({'runtime.zip','python.exe','bootstrap.ps1','ipc_probe.exe'}&names)
            dll=z.read('samurai_kern.dll');pe=struct.unpack_from('<I',dll,0x3c)[0]
            self.assertEqual(dll[pe:pe+4],b'PE\0\0')
            self.assertEqual(struct.unpack_from('<H',dll,pe+4)[0],0x14c)
            self.assertNotIn(b'io.open(',z.read('init.lua'))

    def test_secure_application_cannot_replace_signed_module_but_review_is_explicit(self):
        for review in (False,True):
            name='Selfaware-AI-%s-0.2.0.zip'%('review' if review else 'external')
            with zipfile.ZipFile(BUILD/name) as z:
                config=json.loads(z.read('application.json'))
                self.assertEqual(config,{'transport':'memory','unsigned_development':review})
                self.assertEqual('selfaware-bridge-0.1.0.zip' in z.namelist(),review)
                self.assertIn('LICENSE',z.namelist())
                self.assertIn(b'Game security stays enabled',z.read('README.md'))
                with zipfile.ZipFile(__import__('io').BytesIO(z.read('runtime.zip'))) as runtime:
                    self.assertEqual(runtime.read('Selfaware-AI/werkzeug/befehl.py'),(ROOT/'werkzeug/befehl.py').read_bytes())
                    self.assertIn('Selfaware-AI/werkzeug/speicherkanal.py',runtime.namelist())


if __name__=='__main__':unittest.main()
