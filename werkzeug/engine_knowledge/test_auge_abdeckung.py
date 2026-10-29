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

    def test_inhalt_mit_statuswort_ist_nicht_die_statusspalte(self):
        self.assertEqual(abdeckung.register_status([
            "AU90", "code", "US_IDLE; offene Bedeutung; gemessen nicht", "abgelesen", "Quelle", "Datum"
        ]), "abgelesen")

    def test_leere_semantikdatei_nimmt_nichts_ab(self):
        self.assertEqual(abdeckung.semantikdaten(), {})


class QuellenbindungTest(unittest.TestCase):
    def test_abnahme_braucht_quelle_register_und_gegenprobe(self):
        import hashlib
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            quelle = Path(tmp) / "00401060.json"
            quelle.write_bytes(b"original")
            text = "| pk1 | erklaerung | abgelesen | quelle |"
            eintrag = {k: "geprueft" for k in (
                "kurzaussage", "eingaben", "rueckgabe", "schreibfelder",
                "voraussetzungen", "grenzwerte", "sonderfaelle", "abhaengigkeiten",
                "quelle", "gegenprobe", "pruefdatum")}
            eintrag.update(adresse="0x00401060", status="abgenommen",
                           offene_fragen="keine", registermarke="PK1",
                           registerhash=hashlib.sha256(text.encode()).hexdigest(),
                           funktionshash=hashlib.sha256(b"original").hexdigest())
            def pruefen(e=eintrag, texte=None, belege=None):
                return abdeckung.semantische_abnahme(
                    "00401060", e, belege if belege is not None else [("PK1", "abgelesen")],
                    quelle, texte if texte is not None else {"PK1": text})
            self.assertTrue(pruefen())
            self.assertFalse(pruefen(dict(eintrag, gegenprobe="")))
            self.assertFalse(pruefen(dict(eintrag, offene_fragen="Rueckgabe unklar")))
            self.assertFalse(pruefen(dict(eintrag, adresse="0x00401090")))
            self.assertFalse(pruefen(texte={"PK1": text + " geaendert"}))
            self.assertFalse(pruefen(belege=[]))
            quelle.write_bytes(b"veraendert")
            self.assertFalse(pruefen())

    def test_feldbindung_uebertraegt_sich_nicht(self):
        import hashlib
        text = "| au39 | gebaeude microY +234 |"
        e = dict(struktur="Gebaeude", offset="234", groesse="2", feld="microY",
                 beleg="AU39", registerhash=hashlib.sha256(text.encode()).hexdigest())
        aktiv = {"AU39": text}
        self.assertTrue(abdeckung.feldbeleg_passt(e, "Gebaeude", 234, 2, "microY", aktiv))
        self.assertFalse(abdeckung.feldbeleg_passt(e, "Geschoss", 234, 2, "microY", aktiv))
        self.assertFalse(abdeckung.feldbeleg_passt(e, "Gebaeude", 236, 2, "microY", aktiv))
        self.assertFalse(abdeckung.feldbeleg_passt(e, "Gebaeude", 234, 4, "microY", aktiv))
        self.assertFalse(abdeckung.feldbeleg_passt(e, "Gebaeude", 234, 2, "microY", {}))
        self.assertFalse(abdeckung.feldbeleg_passt(
            e, "Gebaeude", 234, 2, "microY", {"AU39": text + " veraendert"}))

    def test_unbenannte_funktion_ist_nicht_automatisch_technik(self):
        self.assertEqual(abdeckung.funktionsklasse("FUN_00422396"), "unklar")
        self.assertEqual(abdeckung.funktionsklasse("_HoldStrong::Map::update"), "ja")
        self.assertEqual(abdeckung.funktionsklasse("_HoldStrong::Audio::play"), "nein")


if __name__ == "__main__":
    unittest.main()
