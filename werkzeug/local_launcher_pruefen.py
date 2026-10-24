"""Exercise the ordinary desktop entry and failed handoffs without a game."""
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'distribution'))
import local_launcher


class Launcher(unittest.TestCase):
    def config(self, base):
        starter = base/'local state with spaces/starter'
        game = base/'game with spaces'
        runtime = base/'portable runtime'
        for path in (starter/'local_start.ps1', starter/'bootstrap.ps1',
                     game/'Stronghold Crusader.exe', runtime/'python/python.exe'):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'fixture')
        config = starter/'installation.json'
        config.write_text(json.dumps(dict(starter=str(starter),game=str(game),runtime=str(runtime))))
        return config, game

    def test_success_preserves_space_paths_and_records_completion(self):
        with tempfile.TemporaryDirectory() as folder:
            config, game = self.config(Path(folder))
            notifications = []
            def run(command, **options):
                self.assertIsInstance(command, list)
                self.assertEqual(command[command.index('-Game')+1],str(game))
                return SimpleNamespace(returncode=0)
            self.assertEqual(local_launcher.launch(config,run,notifications.append),0)
            self.assertFalse(notifications)
            self.assertIn('finished successfully',(config.parent.parent/'launcher.log').read_text())

    def test_failed_handoff_shows_error_instead_of_silently_exiting(self):
        with tempfile.TemporaryDirectory() as folder:
            config, game = self.config(Path(folder))
            notifications = []
            def run(command, **options):
                options['stdout'].write(b'elevation declined or interpreter error')
                return SimpleNamespace(returncode=7)
            self.assertEqual(local_launcher.launch(config,run,notifications.append),1)
            self.assertEqual(len(notifications),1)
            self.assertIn('Code 7',notifications[0])
            self.assertIn('elevation declined',notifications[0])

    def test_missing_start_script_is_visible_before_spawning_anything(self):
        with tempfile.TemporaryDirectory() as folder:
            config, game = self.config(Path(folder))
            (config.parent/'local_start.ps1').unlink()
            notifications = []
            def forbidden(*args,**kwargs):self.fail('must not spawn with missing script')
            self.assertEqual(local_launcher.launch(config,forbidden,notifications.append),1)
            self.assertIn('Startdatei fehlt',notifications[0])


if __name__ == '__main__':unittest.main()
