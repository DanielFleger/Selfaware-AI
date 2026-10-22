"""Echte Dateiquittungen, aber kein Spielbefehl: Timeout darf kein Erfolg sein."""
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import befehl as kanal
import lordschutz


class AntwortProbe(unittest.TestCase):
    def versuch(self, suffix):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            log = root/'antwort.txt'
            log.write_text('')
            stop = threading.Event()
            def modul():
                while not stop.wait(.001):
                    try:
                        b = json.loads((root/'befehl.json').read_text())
                    except (OSError, ValueError):
                        continue
                    if 'befehle' not in b or b['befehle'][0].get('zeit') is not True:
                        return
                    if suffix is not None:
                        with log.open('a') as f:
                            f.write('villagestudio | QUITTUNG %s%s\n' % (b['id'], suffix))
                    return
            worker = threading.Thread(target=modul)
            with patch.multiple(kanal, LOG=str(log), BEFEHL=str(root/'befehl.json'),
                                MERKER=str(root/'id'), SENDE=str(root/'senden'),
                                LAUF=str(root/'lauf'), PARTNER=False), patch.object(lordschutz, 'filtern', lambda b: (b, [])):
                worker.start()
                try:
                    return kanal.sende({'zeit': True}, warte=.08)
                finally:
                    stop.set()
                    worker.join(1)

    def test_exact_ack(self):
        self.assertTrue(any('QUITTUNG' in z for z in self.versuch('')))

    def test_missing_ack_is_unknown_not_success(self):
        with self.assertRaisesRegex(TimeoutError, 'Wirkung unbekannt'):
            self.versuch(None)

    def test_longer_id_cannot_match_our_id(self):
        with self.assertRaises(TimeoutError):
            self.versuch('9')

    def test_partner_cleanup(self):
        import os
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'lauf'
            p.write_text(str(os.getpid())+' partner')
            with patch.object(kanal, 'LAUF', str(p)):
                kanal.freigeben()
            self.assertFalse(p.exists())


if __name__ == '__main__':
    unittest.main()
