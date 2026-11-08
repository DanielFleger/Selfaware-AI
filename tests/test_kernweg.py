"""P5 (B-157): Uebersetzung der Lenker-Befehle fuer den Kern und Verfolgung ihres Fortgangs (offline)."""

import pathlib
import re
import struct

from selfaware.execution import kernweg as KW
from selfaware.game import kern_leitung as KL

KERN = pathlib.Path(__file__).resolve().parents[1] / "crates" / "samurai-kern" / "src"


class FalscherRing:
    def __init__(self, platz=10_000):
        self.liste, self.ergebnisse, self.platz = [], {}, platz
        self.jetzt, self.zu_alt = 0, set()

    def takt(self):
        return self.jetzt

    def auftrag(self, art, nr, a=0, b=0, vorrang=0, frist=0, auftraggeber=0):
        if len(self.liste) >= self.platz:
            raise RuntimeError("Auftragsring voll")
        self.liste.append((art, nr, a, b, vorrang, frist, auftraggeber))
        return len(self.liste) - 1

    def lesbar(self, ring):
        return ring not in self.zu_alt

    def ergebnis(self, ring):
        return self.ergebnisse.get(ring)


def test_uebersetzung_der_befehlsarten():
    lauf = {"angriff": {"einheiten": [1, 2], "lauf": [50, 60]}}
    flucht = {"angriff": {"einheiten": [3], "lauf": [7, 8], "vorrang": True}}
    assert KW.uebersetze(lauf) == ([1, 2], KL.LAUF, 50, 60, KL.VORRANG_LAUFEN)
    assert KW.uebersetze(flucht) == ([3], KL.LAUF, 7, 8, KL.VORRANG_FLUCHT)
    einheit = {"angriff": {"einheiten": [4], "ziel": 90}}
    gebaeude = {"angriff": {"einheiten": [5], "gebaeude": 91}}
    assert KW.uebersetze(einheit) == ([4], KL.ANGRIFF_EINHEIT, 90, 0, KL.VORRANG_ANGRIFF)
    assert KW.uebersetze(gebaeude) == ([5], KL.ANGRIFF_GEBAEUDE, 91, 0, KL.VORRANG_ANGRIFF)


def test_was_der_kern_nicht_kann_bleibt_beim_modul():
    ring = FalscherRing()
    w = KW.Kernweg(ring)
    halten = {"halten": {"nr": [1], "x": 3, "y": 4}}
    anhalten = {"angriff": {"einheiten": [1], "halt": True}}
    assert w.senden([halten, anhalten]) == [halten, anhalten]
    assert ring.liste == []


def test_halten_nimmt_die_einheit_dem_kern_weg():
    ring = FalscherRing()
    w = KW.Kernweg(ring)
    w.senden([{"angriff": {"einheiten": [1, 2], "lauf": [5, 6]}}])
    ring.liste.clear()
    halten = {"halten": {"nr": [1], "x": 3, "y": 4}}
    assert w.senden([halten]) == [halten]
    assert ring.liste == [(KL.FREIGEBEN, 1, 0, 0, 0, 0, 0)]
    assert w.uebergeben == {2}


def test_einheiten_werden_einmal_uebergeben_flucht_bekommt_frist():
    ring = FalscherRing()
    ring.jetzt = 1000
    w = KW.Kernweg(ring)
    w.senden([{"angriff": {"einheiten": [1, 2], "lauf": [50, 60], "vorrang": True}}])
    w.senden([{"angriff": {"einheiten": [1], "ziel": 9}}])
    arten = [z[0] for z in ring.liste]
    assert arten == [KL.UEBERNEHMEN, KL.UEBERNEHMEN, KL.LAUF, KL.LAUF, KL.ANGRIFF_EINHEIT]
    assert ring.liste[0][2] == KW.ASSASSINEN  # Auftraggeber steht beim Uebernehmen in a
    assert ring.liste[2][4:] == (KL.VORRANG_FLUCHT, 1000 + KW.FLUCHT_FRIST, KW.ASSASSINEN)
    assert ring.liste[4][4:] == (KL.VORRANG_ANGRIFF, 0, KW.ASSASSINEN)


def test_voller_ring_gibt_den_befehl_ans_modul_zurueck():
    ring = FalscherRing(platz=2)
    w = KW.Kernweg(ring)
    b = {"angriff": {"einheiten": [1, 2, 3], "lauf": [5, 6]}}
    assert w.senden([b]) == [b]
    assert w.stand["ring voll"] == 1


def test_fortgang_zaehlt_nur_endgueltige_ergebnisse():
    ring = FalscherRing()
    w = KW.Kernweg(ring)
    w.senden([{"angriff": {"einheiten": [1, 2, 3, 4, 5, 6], "lauf": [5, 6]}}])
    n = sorted(w.offen)
    ring.ergebnisse = {
        n[0]: KL.ERG_ABGESETZT,
        n[1]: KL.ERG_WIRKT,
        n[2]: KL.ERG_VERFALLEN,
        n[3]: KL.ERG_GEPARKT,
    }
    ring.zu_alt = {n[5]}
    stand = w.fortgang()
    assert stand == {"wirkt": 1, "verfallen": 1, "nicht mehr lesbar": 1}
    assert sorted(w.offen) == [n[0], n[3], n[4]]


def test_tote_einheiten_werden_freigegeben():
    ring = FalscherRing()
    w = KW.Kernweg(ring)
    w.senden([{"angriff": {"einheiten": [1, 2], "lauf": [5, 6]}}])
    ring.liste.clear()
    w.aufraeumen({2})
    assert ring.liste == [(KL.FREIGEBEN, 1, 0, 0, 0, 0, 0)]
    assert w.uebergeben == {2}


def test_oeffnen_ohne_kern_ergibt_none(tmp_path):
    assert KW.oeffnen(str(tmp_path)) is None


def test_speicher_ohne_gueltigen_kopf_ist_nicht_bereit(monkeypatch):
    class Leer:
        def __init__(self, ordner):
            self.ordner = ordner

        def lesen(self):
            raise KL.FalscherAufbau("leerer Speicher")

    monkeypatch.setattr(KL, "Leitung", Leer)
    assert KW.oeffnen("egal") is None


def _leitung_ohne_spiel():
    leitung = KL.Leitung.__new__(KL.Leitung)
    leitung.speicher = bytearray(KL.GROESSE)
    return leitung


def test_ringeintrag_traegt_vorrang_frist_und_auftraggeber():
    leitung = _leitung_ohne_spiel()
    n = leitung.auftrag(KL.LAUF, 7, 50, 60, KL.VORRANG_FLUCHT, 1234, KW.ASSASSINEN)
    o = KL.RING_START + KL.RING_KOPF + n * KL.RING_EINTRAG
    assert struct.unpack_from("<8i", leitung.speicher, o) == (
        KL.LAUF,
        7,
        50,
        60,
        KL.OFFEN,
        KL.VORRANG_FLUCHT,
        1234,
        KW.ASSASSINEN,
    )


def test_ein_eintrag_ist_lesbar_bis_sein_platz_neu_belegt_wird():
    leitung = _leitung_ohne_spiel()
    struct.pack_into("<I", leitung.speicher, KL.RING_START, KL.RING_N + 5)
    assert leitung.lesbar(5)
    assert not leitung.lesbar(4)


def test_python_und_kern_lesen_den_ring_gleich():
    quelle = (KERN / "leitung.rs").read_text(encoding="utf-8")
    assert f"pub const AUFBAU: u32 = {KL.AUFBAU};" in quelle
    assert f"pub const RING_EINTRAG: usize = {KL.RING_EINTRAG};" in quelle
    assert "(i, lies(0), lies(4), lies(8), lies(12), lies(20), lies(24), lies(28))" in quelle


def test_ergebnisse_und_vorrang_wie_im_kern():
    quelle = (KERN / "haende.rs").read_text(encoding="utf-8")
    werte = dict(re.findall(r"pub const ((?:ERG|VORRANG)_\w+): i32 = (-?\d+);", quelle))
    assert len(werte) == 17
    for name, wert in werte.items():
        assert getattr(KL, name) == int(wert), name
