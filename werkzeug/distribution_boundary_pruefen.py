"""Verify external runtime ownership; deliberately do NOT certify the legacy bridge."""
from pathlib import Path
import sys,tempfile,unittest,zipfile,json,yaml
from unittest.mock import patch
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

    def test_default_migrates_appdata_learning_to_shared_documents_without_deletion(self):
        with tempfile.TemporaryDirectory() as t:
            base=Path(t);game,package=self.fixture(base);profile=base/'profile'
            with patch.object(Path,'home',return_value=profile):
                old=local_setup.install(game,package,profile/'AppData/Local',shortcut=False)
                model=Path(old['runtime'])/'Selfaware-AI/daten/lernprofile/measured.json'
                model.parent.mkdir(parents=True);model.write_text('{"measured":321}')
                new=local_setup.install(game,package,shortcut=False)
                self.assertTrue(Path(new['runtime']).is_relative_to(profile/'Documents'))
                self.assertEqual((Path(new['runtime'])/model.relative_to(old['runtime'])).read_bytes(),model.read_bytes())
                self.assertTrue(model.is_file(),'Migration must not remove the old learning state')

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

    def test_new_runtime_version_copies_measured_models_without_deleting_previous(self):
        with tempfile.TemporaryDirectory() as t:
            base=Path(t);game,package=self.fixture(base)
            old=local_setup.install(game,package,base/'local',shortcut=False)
            model=Path(old['runtime'])/'Selfaware-AI/daten/lernprofile/proven/model.json'
            model.parent.mkdir(parents=True);model.write_bytes(b'{"measured":456}')
            with zipfile.ZipFile(package/'runtime.zip','a') as z:z.writestr('version.txt','new code version')
            new=local_setup.install(game,package,base/'local',shortcut=False)
            self.assertNotEqual(old['runtime'],new['runtime'])
            self.assertTrue(model.is_file())
            self.assertEqual((Path(new['runtime'])/model.relative_to(old['runtime'])).read_bytes(),model.read_bytes())

    def test_old_self_extracting_package_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            base=Path(t);game,package=self.fixture(base)
            raw=(game/'ucp-config.yml').read_bytes()
            with zipfile.ZipFile(package/'selfaware-runtime-0.1.0.zip','a') as z:z.writestr('runtime.zip',b'old embedded runtime')
            with self.assertRaises(AssertionError):local_setup.install(game,package,base/'local',shortcut=False)
            self.assertEqual((game/'ucp-config.yml').read_bytes(),raw)
            self.assertFalse((base/'local').exists())

    def memory_fixture(self,base,review):
        game,package=self.fixture(base)
        (package/'application.json').write_text(json.dumps({'transport':'memory','unsigned_development':review}))
        module=package/'selfaware-bridge-0.1.0.zip' if review else game/'ucp/modules/selfaware-bridge-0.1.0.zip'
        module.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(module,'w') as z:z.writestr('init.lua',b'Store signed placeholder')
        with zipfile.ZipFile(package/'Selfaware-AI-0.2.0.zip','w') as z:z.writestr('definition.yml',b'name: Selfaware-AI')
        return game,package,module

    def test_memory_production_preserves_store_module_and_removes_legacy_activation(self):
        with tempfile.TemporaryDirectory() as t:
            base=Path(t);game,package,module=self.memory_fixture(base,False)
            before=module.read_bytes()
            # A foreign unsigned package must never replace the Store module.
            (package/module.name).write_bytes(b'not the installed signed Store module')
            result=local_setup.install(game,package,base/'local',shortcut=False)
            self.assertEqual(module.read_bytes(),before)
            self.assertFalse(result['unsigned_development'])
            self.assertEqual(result['transport'],'memory')
            self.assertIsNone(result['store_compatible'],'Maintainers certify Store compatibility')
            self.assertFalse((game/'ucp/villagestudio').exists())
            config=yaml.safe_load((game/'ucp-config.yml').read_text())
            for section in ('config-sparse','config-full'):
                block=config[section]
                self.assertNotIn('selfaware-runtime',block['modules'])
                self.assertIn({'extension':'Selfaware-AI','version':'0.2.0'},block['load-order'])
            self.assertEqual(config['config-full']['modules']['selfaware-bridge']['config']['startTroops']['Assassin']['contents']['value'],3)
            self.assertEqual(config['config-sparse']['modules']['aiSwapper']['config']['ai']['rat'],{'kept':True})

    def test_memory_production_requires_store_module_before_any_installation(self):
        with tempfile.TemporaryDirectory() as t:
            base=Path(t);game,package,module=self.memory_fixture(base,False)
            module.unlink();before=(game/'ucp-config.yml').read_bytes()
            with self.assertRaisesRegex(ValueError,'install Selfaware AI from the UCP Store first'):
                local_setup.install(game,package,base/'local',shortcut=False)
            self.assertFalse((base/'local').exists())
            self.assertEqual((game/'ucp-config.yml').read_bytes(),before)

    def test_migration_clears_only_obsolete_owned_rat_display_not_foreign_fields(self):
        with tempfile.TemporaryDirectory() as t:
            base=Path(t);game,package,module=self.memory_fixture(base,True)
            config=yaml.safe_load((game/'ucp-config.yml').read_text())
            rat=config['config-sparse']['modules']['aiSwapper']['config']['ai']['rat']
            rat.update(lines={'contents':{'value':{'name':'SamurAI','root':'ucp/resources/ai/SamurAI/','active':True}}},portrait={'name':'another mod','root':'foreign/'},lord={'kept':True})
            (game/'ucp-config.yml').write_text(yaml.safe_dump(config))
            local_setup.install(game,package,base/'local',shortcut=False)
            rat=yaml.safe_load((game/'ucp-config.yml').read_text())['config-sparse']['modules']['aiSwapper']['config']['ai']['rat']
            self.assertNotIn('lines',rat)
            self.assertEqual(rat['portrait'],{'name':'another mod','root':'foreign/'})
            self.assertEqual(rat['lord'],{'kept':True})

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
