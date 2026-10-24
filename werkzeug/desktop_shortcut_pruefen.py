"""Independent Windows Shell checks for literal, stable shortcut destinations."""
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'distribution'))
from desktop_shortcut import absolute_link,NO_TRACKING


class Shortcut(unittest.TestCase):
    def test_windows_shell_reads_literal_unicode_paths_and_arguments(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)/'space and \u00dcmlaut';base.mkdir()
            target=base/'pythonw.exe';target.write_bytes(b'fixture')
            link=base/'test.lnk'
            args='"C:\\Users\\test\\AppData\\Local\\Selfaware AI\\starter.py" "settings with spaces.json"'
            raw=absolute_link(target,args,base,target,'Selfaware test')
            link.write_bytes(raw)
            flags=struct.unpack_from('<I',raw,20)[0]
            self.assertEqual(flags & NO_TRACKING,NO_TRACKING)
            ps=("[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false); "
                "$s=New-Object -ComObject WScript.Shell; $l=$s.CreateShortcut('"+str(link).replace("'","''")+"'); "
                "@{target=$l.TargetPath;arguments=$l.Arguments;working=$l.WorkingDirectory}|ConvertTo-Json -Compress")
            exe=Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
            def read():return json.loads(subprocess.check_output([str(exe),'-NoProfile','-Command',ps],encoding='utf-8'))
            first=read();second=read()
            self.assertEqual(first['target'],str(target));self.assertEqual(first['arguments'],args)
            self.assertEqual(first['working'],str(base));self.assertEqual(second,first)
            self.assertEqual(link.read_bytes(),raw,'Resolver must not silently rewrite destination')

    def test_package_cache_and_relative_paths_are_rejected(self):
        good=r'C:\Users\test\AppData\Local\Selfaware AI\pythonw.exe'
        for target in ('relative.exe',r'C:\Users\test\AppData\Local\Packages\OpenAI.Codex_test\LocalCache\pythonw.exe'):
            with self.assertRaises(ValueError):absolute_link(target,'',r'C:\Users\test',good,'test')


if __name__=='__main__':unittest.main()
