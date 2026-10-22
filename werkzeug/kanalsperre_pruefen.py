"""Echte Prozesse: langsamer Besitzer, Absturz und konkurrierender Zaehler."""
import multiprocessing as mp
import os
from pathlib import Path
import tempfile
import time
import unittest
from kanalsperre import Sperre


def halten(pfad, bereit):
    with Sperre(pfad):
        bereit.set()
        time.sleep(20)


def zaehlen(pfad, start):
    start.wait()
    for _ in range(20):
        with Sperre(pfad + '.lock'):
            p = Path(pfad)
            n = int(p.read_text())
            time.sleep(.001)
            p.write_text(str(n + 1))


class KanalProbe(unittest.TestCase):
    def test_live_owner_age_does_not_grant_ownership(self):
        with tempfile.TemporaryDirectory() as d:
            lock = str(Path(d)/'kanal')
            ready = mp.Event()
            child = mp.Process(target=halten, args=(lock, ready))
            child.start()
            try:
                self.assertTrue(ready.wait(5))
                os.utime(lock, (time.time()-100, time.time()-100))
                with self.assertRaises(TimeoutError):
                    with Sperre(lock, timeout=.1):
                        pass
            finally:
                child.terminate()
                child.join(5)
            # Ein echter Prozessabbruch muss die Betriebssystem-Sperre freigeben.
            with Sperre(lock, timeout=.2):
                pass

    def test_same_counter_four_processes(self):
        with tempfile.TemporaryDirectory() as d:
            path = str(Path(d)/'counter')
            Path(path).write_text('0')
            start = mp.Event()
            children = [mp.Process(target=zaehlen, args=(path, start)) for _ in range(4)]
            for p in children:
                p.start()
            start.set()
            try:
                for p in children:
                    p.join(10)
                    self.assertEqual(p.exitcode, 0)
                self.assertEqual(int(Path(path).read_text()), 80)
            finally:
                for p in children:
                    if p.is_alive():
                        p.terminate()
                        p.join(5)


if __name__ == '__main__':
    mp.freeze_support()
    unittest.main()
