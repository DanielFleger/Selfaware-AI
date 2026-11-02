"""B-142: Aufzeichnung und Auswerter an einem kuenstlichen Spiel, ohne echtes Spiel. Jede Probe auch mit eingebautem Fehler."""
from __future__ import annotations

import ctypes
import os
import struct
import sys

import pytest

pytest.importorskip("numpy")

from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis.auge_feldkarte import EXPORT, FELDLISTE, Feldkarte
from selfaware.tools.experiments.auge_aufzeichnung import AENDERUNG, Aufzeichner, Bereich, ProzessQuelle, aenderungen, pruefe_instanz, standard_bereiche

TAKT, U, Z, RNG, FREI, TON = 0x1000, 0x2000, 0x3000, 0x4000, 0x20000, 0x21000
TYPEN = {
    "Einheit": {"laenge": 16, "felder": [(0, "int", 4, "uid"), (4, "int", 4, "leben"), (8, "short", 2, "x"), (10, "short[3]", 6, "rest")]},
    "Einheiten": {"laenge": 4 + 16 * 4, "felder": [(0, "int", 4, "anzahl"), (4, "Einheit[4]", 64, "units")]},
    "Zeit": {"laenge": 8, "felder": [(0, "int", 4, "takt"), (4, "int", 4, "month")]},
    "RNG": {"laenge": 40016, "felder": [(0, "short", 2, "currentNumber1"), (2, "short", 2, "currentNumber2"), (4, "int", 4, "seed"), (8, "short[20000]", 40000, "randomNumbers"), (40008, "int", 4, "index2"), (40012, "int", 4, "index1")]},
    "Frei": {"laenge": 8, "felder": [(0, "int", 4, "ungelistet"), (4, "int", 4, "gelistet")]},
    "Ton": {"laenge": 4, "felder": [(0, "int", 4, "lautstaerke")]},
}
STRUKTUREN = [(TAKT, TAKT + 8, "DAT_Zeit", "Zeit"), (U, U + 68, "DAT_Einheiten", "Einheiten"), (RNG, RNG + 40016, "SEC_RNG", "RNG"), (FREI, FREI + 8, "DAT_Frei", "Frei"), (TON, TON + 4, "DAT_SoundSystemState", "Ton")]
BEKANNT = [("DAT_Zeit", "takt"), ("DAT_Zeit", "month"), ("DAT_Einheiten", "units[].leben"), ("DAT_Einheiten", "units[].uid"), ("DAT_Einheiten", "units[].x"), ("SEC_RNG", "index2"), ("SEC_RNG", "index1"), ("SEC_RNG", "currentNumber1"), ("SEC_RNG", "currentNumber2"), ("DAT_Frei", "gelistet"), ("DAT_Einheiten", "anzahl"), ("DAT_Zeit", "nie_geaendert")]
BEREICHE = [Bereich("zeit", TAKT, 8), Bereich("einheiten", U, 68), Bereich("rng", RNG, 40016), Bereich("frei", FREI, 8), Bereich("ton", TON, 4)]


def karte():
    return Feldkarte(TYPEN, STRUKTUREN, {}, BEKANNT)


class Spiel:
    """Kuenstlicher Spielspeicher; jeder Schritt rechnet einen Takt festgelegt weiter."""

    def __init__(self):
        self.m = {b.adresse: bytearray(b.laenge) for b in BEREICHE}
        for i in range(20000):
            struct.pack_into("<h", self.m[RNG], 8 + 2 * i, (i * 7) % 3000)
        struct.pack_into("<i", self.m[U], 4, 2)
        for i in range(2):
            struct.pack_into("<ii", self.m[U], 4 + 16 * i, 100 + i, 50)
        self.takt_setzen(1)
        self.waehrend_lesen = None

    def lies(self, adresse, laenge):
        if self.waehrend_lesen and adresse != TAKT:
            self.waehrend_lesen()
        for a, p in self.m.items():
            if a <= adresse < a + len(p):
                return bytes(p[adresse - a:adresse - a + laenge])
        raise OSError(adresse)

    def takt_setzen(self, t):
        struct.pack_into("<i", self.m[TAKT], 0, t)

    @property
    def takt(self):
        return struct.unpack_from("<i", self.m[TAKT], 0)[0]

    def weiter(self):
        t = self.takt + 1
        self.takt_setzen(t)
        struct.pack_into("<i", self.m[U], 4 + 4, 50 - t % 40)
        struct.pack_into("<h", self.m[U], 4 + 8, t)
        struct.pack_into("<i", self.m[TAKT], 4, (t // 3) % 12)
        i = struct.unpack_from("<i", self.m[RNG], 40008)[0]
        struct.pack_into("<h", self.m[RNG], 2, struct.unpack_from("<h", self.m[RNG], 8 + 2 * i)[0])
        struct.pack_into("<i", self.m[RNG], 40008, 0 if i + 1 > 19999 else i + 1)


def aufzeichnen(pfad, spiel=None, takte=30, stoerung=None, kopf=None, bereiche=BEREICHE):
    spiel = spiel or Spiel()
    auf = Aufzeichner(spiel, bereiche, pfad, kopf or {"lauf": "T"}, takt_adresse=TAKT)
    for i in range(takte):
        auf.schritt()
        spiel.weiter()
        if stoerung:
            stoerung(spiel, i)
    auf.schliessen()
    return aw.Aufzeichnung(pfad)


def test_wiedergabe_entspricht_genau_dem_speicher(tmp_path):
    spiel = Spiel()
    auf = Aufzeichner(spiel, BEREICHE, tmp_path / "a.auge", {}, takt_adresse=TAKT)
    wahr = []
    for _ in range(40):
        auf.schritt()
        wahr.append((spiel.takt, bytes(spiel.m[U])))
        spiel.weiter()
    auf.schliessen()
    a = aw.Aufzeichnung(tmp_path / "a.auge")
    gelesen = [(r.takt, bytes(p)) for r, p, _ in a.staende() if a.namen[r.bereich] == "einheiten"]
    assert gelesen == wahr
    assert any(r.art == AENDERUNG for r in a.rahmen())


def test_aenderungen_finden_auch_einzelne_bytes_am_rand():
    alt = bytes(100)
    neu = bytearray(alt)
    neu[0] = 1
    neu[99] = 2
    n = aenderungen(alt, bytes(neu))
    assert struct.unpack_from("<II", n, 0) == (0, 1)
    assert aenderungen(alt, alt) == b""


def test_a1_gut_und_mit_unbekanntem_byte(tmp_path):
    k = karte()
    gut = aw.a1_aenderungsmelder(aufzeichnen(tmp_path / "g.auge"), k)
    assert gut.status == aw.BESTAETIGT and gut.daten["luecke"] == 0

    def stoer(s, i):
        struct.pack_into("<i", s.m[FREI], 0, i + 1)
    schlecht = aw.a1_aenderungsmelder(aufzeichnen(tmp_path / "s.auge", stoerung=stoer), k)
    assert schlecht.status == aw.WIDERLEGT
    assert schlecht.daten["luecken"][0]["feld"] == "ungelistet"


def test_a1_zaehlt_technik_getrennt_und_nicht_als_luecke(tmp_path):
    def stoer(s, i):
        struct.pack_into("<i", s.m[TON], 0, i + 1)
    e = aw.a1_aenderungsmelder(aufzeichnen(tmp_path / "t.auge", stoerung=stoer), karte())
    assert e.status == aw.BESTAETIGT and e.daten["technik"] == 1


def test_a2_nennt_nie_geaenderte_felder(tmp_path):
    k = karte()
    e1 = aw.a1_aenderungsmelder(aufzeichnen(tmp_path / "g.auge"), k)
    e2 = aw.a2_nie_gesehen(k, e1.daten["gesehen"])
    assert ["DAT_Zeit", "nie_geaendert"] in e2.daten["nie"]
    assert ["DAT_Einheiten", "units[].leben"] not in e2.daten["nie"]


def test_a3_gut_fehlender_takt_und_gemischter_rahmen(tmp_path):
    assert aw.a3_takttreue(aufzeichnen(tmp_path / "g.auge")).status == aw.BESTAETIGT

    def spring(s, i):
        if i == 10:
            s.weiter()
            s.weiter()
    e = aw.a3_takttreue(aufzeichnen(tmp_path / "f.auge", stoerung=spring))
    assert e.status == aw.WIDERLEGT and e.daten["fehlende_takte"] == 2

    spiel = Spiel()
    auf = Aufzeichner(spiel, BEREICHE, tmp_path / "m.auge", {}, takt_adresse=TAKT)
    auf.schritt()
    spiel.weiter()
    spiel.waehrend_lesen = lambda: spiel.takt_setzen(spiel.takt + 1)
    auf.schritt()
    auf.schliessen()
    e = aw.a3_takttreue(aw.Aufzeichnung(tmp_path / "m.auge"))
    assert e.status == aw.WIDERLEGT and e.daten["unreine_rahmen"] > 0


def test_a3_erkennt_abgeschnittene_und_verfaelschte_datei(tmp_path):
    a = aufzeichnen(tmp_path / "g.auge")
    roh = (tmp_path / "g.auge").read_bytes()
    (tmp_path / "ab.auge").write_bytes(roh[:-3])
    e = aw.a3_takttreue(aw.Aufzeichnung(tmp_path / "ab.auge"))
    assert e.status == aw.WIDERLEGT and e.daten["beschaedigt"] == 1
    kaputt = bytearray(roh)
    kaputt[-10] ^= 0xFF
    (tmp_path / "ka.auge").write_bytes(bytes(kaputt))
    assert aw.a3_takttreue(aw.Aufzeichnung(tmp_path / "ka.auge")).daten["beschaedigt"] == 1
    assert a.kopf["lauf"] == "T"


def test_a4_vergleicht_mit_tempo_ohne_lesen(tmp_path):
    uhr = iter(float(i) for i in range(100000))
    spiel = Spiel()
    auf = Aufzeichner(spiel, BEREICHE, tmp_path / "a.auge", {"tempo_ohne_lesen": 1000.0}, takt_adresse=TAKT, uhr=lambda: next(uhr))
    for _ in range(10):
        auf.schritt()
        spiel.weiter()
    auf.schliessen()
    e = aw.a4_lesedauer(aw.Aufzeichnung(tmp_path / "a.auge"))
    assert e.status == aw.WIDERLEGT
    assert e.daten["takte"] == 10


def test_a4_pause_im_lauf_zaehlt_nicht_als_bremsen(tmp_path):
    jetzt = [0.0]

    def uhr():
        jetzt[0] += 0.001
        return jetzt[0]
    spiel = Spiel()
    auf = Aufzeichner(spiel, [Bereich("zeit", TAKT, 8)], tmp_path / "p.auge", {"tempo_ohne_lesen": 100.0}, takt_adresse=TAKT, uhr=uhr)
    for i in range(20):
        auf.schritt()
        spiel.weiter()
        jetzt[0] += 500.0 if i == 10 else 0.005
    auf.schliessen()
    e = aw.a4_lesedauer(aw.Aufzeichnung(tmp_path / "p.auge"))
    assert e.status == aw.BESTAETIGT and e.daten["takte_je_s"] > 95


def test_a4_ohne_vergleichswert_ist_nur_gemessen(tmp_path):
    assert aw.a4_lesedauer(aufzeichnen(tmp_path / "a.auge")).status == aw.GEMESSEN


def test_a5_und_a6_gleich_und_mit_einem_falschen_byte(tmp_path):
    k = karte()
    a = aufzeichnen(tmp_path / "a.auge")
    b = aufzeichnen(tmp_path / "b.auge")
    assert aw.a5_laden_gleich_sichern(a, 5, b, 5, k).status == aw.BESTAETIGT
    assert aw.a6_gleicher_verlauf(a, 5, b, 5, 20, k).status == aw.BESTAETIGT

    def stoer(s, i):
        if i == 12:
            struct.pack_into("<i", s.m[U], 4 + 16 + 4, 7)
    c = aufzeichnen(tmp_path / "c.auge", stoerung=stoer)
    e = aw.a6_gleicher_verlauf(a, 5, c, 5, 20, k)
    assert e.status == aw.WIDERLEGT
    assert e.daten["felder"] == [["DAT_Einheiten", "units[].leben"]]
    assert e.daten["takt"] == 14 - 5  # erster Rahmen mit dem Fehler: nach Durchgang 12 steht der Takt auf 14
    e5 = aw.a5_laden_gleich_sichern(a, 20, c, 20, k)
    assert e5.status == aw.WIDERLEGT and e5.daten["abweichend"][0][:2] == ["DAT_Einheiten", "units[].leben"]


def test_a5_a6_keine_fehlalarme_durch_selten_gelesene_bereiche(tmp_path):
    k = karte()
    b1 = [Bereich("zeit", TAKT, 8), Bereich("einheiten", U, 68), Bereich("selten", U, 68, 7)]
    a = aufzeichnen(tmp_path / "a.auge", bereiche=b1, takte=20)
    s2 = Spiel()
    for _ in range(3):
        s2.weiter()
    b = aufzeichnen(tmp_path / "b.auge", spiel=s2, bereiche=b1, takte=20)
    assert aw.a5_laden_gleich_sichern(a, 10, b, 10, k).status == aw.BESTAETIGT
    assert aw.a6_gleicher_verlauf(a, 10, b, 10, 8, k).status == aw.BESTAETIGT


def test_voll_bei_liest_alle_bereiche_im_takt_des_speicherns(tmp_path):
    spiel = Spiel()
    auf = Aufzeichner(spiel, [Bereich("zeit", TAKT, 8), Bereich("selten", U, 68, 100)], tmp_path / "v.auge", {}, takt_adresse=TAKT, voll_bei=[5])
    for _ in range(8):
        auf.schritt()
        spiel.weiter()
    auf.schliessen()
    a = aw.Aufzeichnung(tmp_path / "v.auge")
    assert sorted(a.stand_bei(5)) == ["selten", "zeit"]
    assert sorted(a.stand_bei(6)) == ["zeit"]


def test_a7_gut_und_mit_falscher_zufallszahl(tmp_path):
    a = aufzeichnen(tmp_path / "a.auge", bereiche=[Bereich("zeit", TAKT, 8), Bereich("SEC_RNG", RNG, 40016)])
    e = aw.a7_zufall(a)
    assert e.status == aw.BESTAETIGT and e.daten["gezogen"] > 0

    def stoer(s, i):
        if i == 7:
            struct.pack_into("<h", s.m[RNG], 2, -999)
    b = aufzeichnen(tmp_path / "b.auge", stoerung=stoer, bereiche=[Bereich("zeit", TAKT, 8), Bereich("SEC_RNG", RNG, 40016)])
    assert aw.a7_zufall(b).status == aw.WIDERLEGT


def test_a7_ohne_bereich_ist_nicht_gesehen(tmp_path):
    assert aw.a7_zufall(aufzeichnen(tmp_path / "a.auge", takte=2, bereiche=[Bereich("zeit", TAKT, 8)])).status == aw.NICHT_GESEHEN


def test_a9_zaehlt_plaetze_und_vergleicht_mit_gesendeten(tmp_path):
    def stoer(s, i):
        if i == 4:
            struct.pack_into("<i", s.m[FREI], 4, 1)
    a = aufzeichnen(tmp_path / "a.auge", stoerung=stoer, bereiche=[Bereich("zeit", TAKT, 8), Bereich("befehle", FREI, 8)])
    wann = [r.takt for r, _, t in a.staende() if a.namen[r.bereich] == "befehle" and r.art == AENDERUNG and t][0]
    gut = aw.a9_befehle(a, {wann: 1}, groesse=4)
    assert gut.status == aw.BESTAETIGT
    assert aw.a9_befehle(a, {wann: 2}, groesse=4).status == aw.WIDERLEGT
    assert aw.a9_befehle(a, {wann + 10: 1}, groesse=4).status == aw.WIDERLEGT
    assert aw.a9_befehle(a, groesse=4).status == aw.GEMESSEN


def test_a10_uid_doppelt_und_grenze_verletzt(tmp_path):
    listen = [("Einheiten", U + 4, 16, 4)]
    grenzen = [("Monat", TAKT + 4, "<i", 0, 11)]
    assert aw.a10_lebenslauf(aufzeichnen(tmp_path / "a.auge"), listen, grenzen).status == aw.BESTAETIGT

    def doppelt(s, i):
        if i == 3:
            struct.pack_into("<i", s.m[U], 4 + 32, 100)
    e = aw.a10_lebenslauf(aufzeichnen(tmp_path / "b.auge", stoerung=doppelt), listen, grenzen)
    assert e.status == aw.WIDERLEGT and "uid 100" in e.daten["verstoesse"][0][3]

    class Monat12(Spiel):
        def weiter(self):
            super().weiter()
            struct.pack_into("<i", self.m[TAKT], 4, 12)
    e = aw.a10_lebenslauf(aufzeichnen(tmp_path / "c.auge", spiel=Monat12()), listen, grenzen)
    assert e.status == aw.WIDERLEGT and e.daten["verstoesse"][0][1] == "Monat"


def test_a12_zaehlt_wechsel(tmp_path):
    e = aw.a12_fluechtig(aufzeichnen(tmp_path / "a.auge"), [("Monat", TAKT + 4, "<i")])
    assert e.daten["wechsel"]["Monat"] > 0


def test_a13_vermutung_bestaetigt_und_widerlegt(tmp_path):
    def rec(n, sp):
        return aufzeichnen(tmp_path / f"{n}.auge", takte=1, kopf={"spielart": sp})
    f, s = rec("f", {"currentGameMode": 0, "gameMode_2": 2}), rec("s", {"currentGameMode": 0, "gameMode_2": 2})
    k = rec("k", {"currentGameMode": 99, "gameMode_2": 3})
    assert aw.a13_spielart({"F": f, "K": k, "S": s}).status == aw.BESTAETIGT
    assert aw.a13_spielart({"F": f, "K": f, "S": s}).status == aw.WIDERLEGT
    assert aw.a13_spielart({"F": f}).status == aw.GEMESSEN


def test_laden_rueckwaerts_schreibt_vollen_stand_und_zaehlt_keine_fehlenden_takte(tmp_path):
    spiel = Spiel()
    auf = Aufzeichner(spiel, BEREICHE, tmp_path / "l.auge", {}, takt_adresse=TAKT)
    for _ in range(10):
        auf.schritt()
        spiel.weiter()
    spiel.takt_setzen(3)
    auf.schritt()
    auf.schliessen()
    a = aw.Aufzeichnung(tmp_path / "l.auge")
    e = aw.a3_takttreue(a)
    assert e.daten["rueckspruenge"] == len(BEREICHE) and e.daten["fehlende_takte"] == 0
    assert aw.a1_aenderungsmelder(a, karte()).status == aw.BESTAETIGT


def test_feldkarte_pfad_und_sprung_ueber_ganze_felder():
    k = karte()
    assert k.ziel(U + 4 + 16 + 4) == ("DAT_Einheiten", "units[].leben")
    assert k.felder_einer_aenderung(U + 4 + 4, 4) == [("DAT_Einheiten", "units[].leben")]
    assert k.felder_einer_aenderung(U + 4 + 8, 4)[:2] == [("DAT_Einheiten", "units[].x"), ("DAT_Einheiten", "units[].rest[]")]
    assert k.adresse("DAT_Einheiten", "units[].leben") == (U + 8, 4, 16, 4)
    assert k.klasse("DAT_Frei", "ungelistet") == "luecke"
    assert k.klasse("DAT_SoundSystemState", "lautstaerke") == "technik"


def test_instanz_5_wird_abgelehnt():
    with pytest.raises(PermissionError):
        pruefe_instanz(r"C:\Games\Stronghold Crusader Extreme Instanz5\Stronghold_Crusader_Extreme.exe")
    pruefe_instanz(r"C:\Games\Stronghold Crusader Extreme Instanz2\Stronghold_Crusader_Extreme.exe")


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-Speicherzugriff")
def test_prozessquelle_liest_den_eigenen_prozess():
    puffer = ctypes.create_string_buffer(b"auge-probe")
    q = ProzessQuelle(os.getpid())
    assert q.lies(ctypes.addressof(puffer), 10) == b"auge-probe"
    with pytest.raises(OSError):
        q.lies(0x10, 4)


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-Speicherzugriff")
def test_pid_der_instanz_findet_einen_laufenden_prozess_am_ordner():
    from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz, prozesspfade
    assert any(p.lower() == sys.executable.lower() for p in prozesspfade())
    assert pid_der_instanz(1, stamm=os.path.dirname(sys.executable)) is not None
    assert pid_der_instanz(1, stamm=r"C:\gibt\es\nicht") is None


@pytest.mark.skipif(not os.path.exists(os.path.join(EXPORT, "types.json")), reason="Export fehlt")
def test_echte_feldkarte_kennt_die_belegten_adressen():
    k = Feldkarte.laden(feldliste=FELDLISTE)
    assert k.ziel(0x0117CADC) == ("DAT_GameState", "mapAndTime.totalGameTicksUnk")
    assert k.struktur("DAT_UnitsState")[0] == 0x01387F38
    assert k.adresse("DAT_UnitsState", "units[].uid")[2:] == (1168, 2500)
    assert k.adresse("DAT_EntityState", "entityArray[].uid")[2:] == (232, 3000)
    assert k.adresse("DAT_BuildingsState", "buildings[].uid")[2:] == (812, 2000)
    assert k.klasse(*k.ziel(k.adresse("DAT_GameState", "mapAndTime.month")[0])) == "bekannt"
    assert k.adresse("DAT_GameSynchronyState", "DAT_GameCommandArray")[2:] == (1272, 200)
    assert k.adresse("SEC_RNG", "index2")[0] == 0x01A279C0 + 40008
    bereiche = standard_bereiche(k)
    assert all(0x005B6000 <= b.adresse and b.adresse + b.laenge <= 0x02429240 for b in bereiche)
    assert {"DAT_UnitsState", "SEC_RNG", "befehle", "datenblock"} <= {b.name for b in bereiche}
    assert aw.echte_listen(k)[0][2:] == (1168, 2500) and aw.echte_grenzen(k)[0][0] == "Monat"
    assert k.klasse("DAT_DirectionAlgorithmState", "gibt_es_nicht") == "luecke"
