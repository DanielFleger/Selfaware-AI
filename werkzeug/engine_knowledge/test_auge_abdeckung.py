# -*- coding: utf-8 -*-
import importlib.util
from pathlib import Path
import unittest


PFAD = Path(__file__).with_name("auge_abdeckung.py")
SPEC = importlib.util.spec_from_file_location("auge_abdeckung", PFAD)
abdeckung = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(abdeckung)


class AbdeckungsMetadatenTest(unittest.TestCase):
    def test_status_in_kurzer_registerzeile(self):
        self.assertEqual(
            abdeckung.register_status(["AU3", "Erklaerung", "gemessen (10/10)", "25.10."]),
            "gemessen (10/10)",
        )

    def test_status_trotz_senkrechtem_strich_im_text(self):
        self.assertEqual(
            abdeckung.register_status(["L21", "tax", "popularity", "abgelesen", "Quelle", "25.10."]),
            "abgelesen",
        )

    def test_adresse_trifft_exakt(self):
        muster = abdeckung.adressmuster("00401090")
        self.assertTrue(any(m.search("0x00401090") for m in muster))
        self.assertTrue(any(m.search("401090") for m in muster))
        self.assertFalse(any(m.search("0x004010900") for m in muster))
        self.assertFalse(any(m.search("0x100401090") for m in muster))


if __name__ == "__main__":
    unittest.main()
