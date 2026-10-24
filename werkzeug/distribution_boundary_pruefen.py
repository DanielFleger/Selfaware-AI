"""Verify external runtime ownership; deliberately do NOT certify the legacy bridge."""
from pathlib import Path
import sys,tempfile,unittest,zipfile,json,yaml
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'distribution'))
import local_setup

class Distribution(unittest.TestCase):
    def fixture(self,base):
        game=base/'game';game.mkdir();(game/'Stronghold Crusader.exe').write_bytes(b'fixture')
        config={'config-sparse':{'modules':{'aiSwapper':{'config':{'ai':{'abbot':{'lord':{'kept':True}},'rat':{'kept':True}}}}}},'config-full':{'modules':{'selfaware-runtime':{'config':{'startTroops':{'Assassin':{'contents':{'value':3}}}}}}}}
        (game/'ucp-config.yml').write_text(yaml.safe_dump(config))
        package=base/'packages';package.mkdir()
        for name,contents in [('runtime.zip',{'python/python.exe':b'python','python/pythonw.exe':b'windowless python'}),('selfaware-runtime-0.1.0.zip',{'init.lua':b'local bridge'}),('Selfaware-AI-0.1.0.zip',{'definition.yml':b'name: Selfaware-AI'})]:
            with zipfile.ZipFile(package/name,'w') as z:
                for path,data in contents.items():z.writestr(path,data)
        return game,package

    def test_upgrade_preserves_learning_and_unrelated_configuration(self):
        with tempfile.TemporaryDirectory() as t:
            base=Path(t);game,package=self.fixture(base)
            first=local_setup.install(game,package,base/'local',shortcut=False)
            model=Path(first['runtime'])/'Selfaware-AI/daten/lernprofile/test/verlust_raten.json'
            model.parent.mkdir(parents=True);model.write_text('{"measured":123}')
            second=local_setup.install(game,package,base/'local',shortcut=False)
            self.assertEqual(first['runtime'],second['runtime'])
            self.assertEqual(model.read_text(),'{"measured":123}')
            config=yaml.safe_load((game/'ucp-config.yml').read_text())
            self.assertEqual(config['config-sparse']['modules']['aiSwapper']['config']['ai']['abbot']['lord'],{'kept':True})
            self.assertEqual(config['config-sparse']['modules']['aiSwapper']['config']['ai']['rat'],{'kept':True})
            self.assertEqual(config['config-full']['modules']['selfaware-runtime']['config']['startTroops']['Assassin']['contents']['value'],3)
            self.assertFalse(second['store_compatible'])
            self.assertFalse(second['module_extracts_runtime'])

    def test_old_self_extracting_package_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            base=Path(t);game,package=self.fixture(base)
            raw=(game/'ucp-config.yml').read_bytes()
            with zipfile.ZipFile(package/'selfaware-runtime-0.1.0.zip','a') as z:z.writestr('runtime.zip',b'old embedded runtime')
            with self.assertRaises(AssertionError):local_setup.install(game,package,base/'local',shortcut=False)
            self.assertEqual((game/'ucp-config.yml').read_bytes(),raw)
            self.assertFalse((base/'local').exists())

    def test_zip_cannot_escape_install_directory(self):
        with tempfile.TemporaryDirectory() as t:
            base=Path(t);archive=base/'bad.zip'
            with zipfile.ZipFile(archive,'w') as z:z.writestr('../outside.txt','must not escape')
            with self.assertRaises(ValueError):local_setup.safe_extract(archive,base/'target')
            self.assertFalse((base/'outside.txt').exists())

    def test_built_bridge_contains_no_external_runtime_or_launcher(self):
        package=ROOT/'build/selfaware-runtime-0.1.0.zip'
        if not package.is_file():self.skipTest('run package_local.py first')
        with zipfile.ZipFile(package) as z:
            self.assertFalse({'runtime.zip','bootstrap.ps1','sai_launcher.dll'} & set(z.namelist()))
            init=z.read('init.lua').decode()
            self.assertNotIn('copyFile',init);self.assertNotIn('sai_start',init)
            self.assertNotIn("io.open",init)

if __name__=='__main__':unittest.main()
