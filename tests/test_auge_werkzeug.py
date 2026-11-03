"""B-142: Aufzeichnung und Auswerter an einem kuenstlichen Spiel, ohne echtes Spiel. Jede Probe auch mit eingebautem Fehler."""
from __future__ import annotations

import ctypes
import json
import os
import struct
import sys

import pytest

pytest.importorskip("numpy")

from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis.auge_feldkarte import EXPORT, FELDLISTE, Feldkarte
from selfaware.tools.experiments.auge_aufzeichnung import AENDERUNG, Aufzeichner, Bereich, FeldWache, ProzessQuelle, Streng, aenderungen, pruefe_instanz, standard_bereiche

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


def test_packfehler_kommt_beim_schliessen_an(tmp_path, monkeypatch):
    import selfaware.tools.experiments.auge_aufzeichnung as az
    monkeypatch.setattr(az.zlib, "compress", lambda *a: (_ for _ in ()).throw(ValueError("kaputt")))
    auf = Aufzeichner(Spiel(), BEREICHE, tmp_path / "f.auge", {}, takt_adresse=TAKT)
    auf.schritt()
    with pytest.raises(ValueError, match="kaputt"):
        auf.schliessen()


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


def test_felder_der_teile_nennt_jedes_feld_je_stueck_einmal():
    import numpy as np

    ids = np.array([0, 0, 1, 1, 2, 2, 2, 3], dtype=np.int32)
    nummern, stuecke, anfang, laengen = aw.felder_der_teile(ids, [(1, 2), (6, 1), (3, 1), (2, 1)])
    assert nummern.tolist() == [0, 1, 2, 1, 1], "Stueck 1 beruehrt zwei Felder, die letzten beiden Stuecke dasselbe Feld und zaehlen beide"
    assert stuecke.tolist() == [0, 0, 1, 2, 3]
    assert anfang.tolist() == [1, 6, 3, 2] and laengen.tolist() == [2, 1, 1, 1]


def test_a1_zaehlt_wie_oft_und_ab_wann(tmp_path):
    def stoer(s, i):
        if i >= 3:
            struct.pack_into("<i", s.m[FREI], 0, i + 1)
    e = aw.a1_aenderungsmelder(aufzeichnen(tmp_path / "z.auge", stoerung=stoer), karte())
    z = next(x for x in e.daten["luecken"] if x["feld"] == "ungelistet")
    assert z["aenderungen"] >= 2 and z["erster_takt"] > 0, "Die Luecke beginnt erst spaeter und wird je Rahmen gezaehlt"


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


def test_a3_auf_hohem_tempo_ist_ausgelassen_nur_gemessen(tmp_path):
    def spring(s, i):
        s.weiter()
    e = aw.a3_takttreue(aufzeichnen(tmp_path / "h.auge", stoerung=spring, kopf={"tempo": 1000}))
    assert e.status == aw.GEMESSEN and e.daten["fehlende_takte"] > 0
    assert aw.a3_takttreue(aufzeichnen(tmp_path / "n.auge", stoerung=spring, kopf={"tempo": 40})).status == aw.WIDERLEGT


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
    assert e.status == aw.GEMESSEN
    assert e.daten["takte"] == 10 and e.daten["ohne_lesen"] == 1000.0


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
    assert e.status == aw.GEMESSEN and e.daten["takte_je_s"] > 95


def treppe(tempo, o1, mit, o2, gelesen=100, gesamt=100):
    return {"tempo": tempo, "sekunden": 20, "ohne_1": o1, "mit": mit, "ohne_2": o2, "gelesen": gelesen, "gesamt": gesamt}


def test_a4_tempotreppe_ohne_abzug_mit_kleinem_rauschen():
    e = aw.a4_tempotreppe([treppe(40, 40.0, 40.0, 40.0), treppe(1000, 600.0, 598.0, 595.0, 50, 12000)])
    assert e.status == aw.BESTAETIGT
    assert "1000" in e.text.split("ausgelassen auf")[1]


def test_a4_tempotreppe_kleiner_abzug_ist_widerlegt_es_gibt_keine_prozentgrenze():
    e = aw.a4_tempotreppe([treppe(40, 40.0, 39.7, 40.0)])
    assert e.status == aw.WIDERLEGT and "[40]" in e.text and e.daten["zeilen"][0]["abzug"] > 0


def test_a4_tempotreppe_ohne_messung_ist_nicht_gesehen():
    assert aw.a4_tempotreppe([]).status == aw.NICHT_GESEHEN


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
    listen = [("Einheiten", U + 4, 16, 4, 0)]
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
    assert aw.echte_listen(k)[0][2:] == (1168, 2500, 1) and aw.echte_grenzen(k)[0][0] == "Monat"
    basis = aw.SPIELERDATEN + aw.SPIELER_SCHRITT
    assert [k.ziel(basis + f)[1] for f in aw.FELD_STEUER] == ["playerDataArray[].taxBribeMonthlyAccumulator", "playerDataArray[].taxIncomeMonthlyAccumulator"]
    assert k.klasse("DAT_DirectionAlgorithmState", "gibt_es_nicht") == "luecke"


# --- B-142: strenger Modus, Takte statt Sekunden, Stufe ohne Messung ---
def test_streng_endet_beim_ersten_fehlenden_takt_und_zaehlt_sonst_nur(tmp_path):
    spiel = Spiel()
    auf = Aufzeichner(spiel, BEREICHE, tmp_path / "s.auge", {}, takt_adresse=TAKT, streng=True)
    auf.schritt()
    spiel.weiter()
    auf.schritt()
    spiel.weiter()
    spiel.weiter()
    with pytest.raises(Streng, match="fehlt"):
        auf.schritt()
    auf.schliessen()
    spiel = Spiel()
    auf = Aufzeichner(spiel, BEREICHE, tmp_path / "n.auge", {}, takt_adresse=TAKT)
    auf.schritt()
    spiel.weiter()
    spiel.weiter()
    auf.schritt()
    auf.schliessen()
    assert auf.fehlend == 1


def gemischt(tmp_path, bereiche, streng):
    spiel = Spiel()
    auf = Aufzeichner(spiel, bereiche, tmp_path / "g.auge", {}, takt_adresse=TAKT, streng=streng)
    auf.schritt()
    spiel.weiter()
    spiel.waehrend_lesen = spiel.weiter
    try:
        auf.schritt()
    finally:
        spiel.waehrend_lesen = None
        auf.schliessen()
    return auf


def test_streng_endet_bei_gemischtem_bereich_der_jeden_takt_gelesen_wird(tmp_path):
    with pytest.raises(Streng, match="gemischt"):
        gemischt(tmp_path, [Bereich("einheiten", U, 68)], True)


def test_gemischter_seltener_bereich_ist_kein_abbruch_und_zaehlt_getrennt(tmp_path):
    spiel = Spiel()
    auf = Aufzeichner(spiel, [Bereich("einheiten", U, 68, 2)], tmp_path / "g.auge", {}, takt_adresse=TAKT, streng=True)
    auf.schritt()
    spiel.weiter()
    auf.schritt()  # dieser Takt ist fuer den seltenen Bereich nicht dran
    spiel.weiter()
    spiel.waehrend_lesen = spiel.weiter
    auf.schritt()
    spiel.waehrend_lesen = None
    auf.schliessen()
    assert auf.gemischt == 0 and auf.gemischt_selten == 1
    a = aw.Aufzeichnung(tmp_path / "g.auge")
    e = aw.a3_takttreue(a)
    assert e.daten["unreine_rahmen"] == 0 and e.daten["unrein_selten"] == 1


def test_streng_endet_wenn_die_schlange_voll_ist(tmp_path, monkeypatch):
    spiel = Spiel()
    auf = Aufzeichner(spiel, BEREICHE, tmp_path / "q.auge", {}, takt_adresse=TAKT, streng=True)
    monkeypatch.setattr(auf._schlange, "full", lambda: True)
    with pytest.raises(Streng, match="voll"):
        auf.schritt()
    monkeypatch.undo()
    auf.schliessen()


def test_lauf_rechnet_in_takten_und_aussetzen_zaehlt_nicht_als_fehlend(tmp_path, monkeypatch):
    spiel = Spiel()
    auf = Aufzeichner(spiel, BEREICHE, tmp_path / "l.auge", {}, takt_adresse=TAKT)
    monkeypatch.setattr("time.sleep", lambda _: spiel.weiter())
    assert auf.lauf(bis_takt=spiel.takt + 5) >= 5
    aus = [True, True, False]
    n = auf.lauf(takte=3, aussetzen=lambda: bool(aus) and aus.pop(0))
    auf.schliessen()
    assert n == 3 and auf.fehlend == 0
    with pytest.raises(TypeError):
        auf.lauf(sekunden=1)


def test_feldwache_meldet_neue_felder_und_das_ende_der_neuigkeiten(tmp_path):
    k = karte()
    datei = str(tmp_path / "felder.json")
    w = FeldWache(k, BEREICHE, datei, alle=10)
    import numpy as np
    w.merke(0, np.array([4, 5]), 8)  # DAT_Zeit.month ist gelistet
    w.pruefe(100)
    w.pruefe(110)
    a = json.load(open(datei))
    assert a["felder"] == 1 and a["letzter_neuer_takt"] == 110
    w.merke(0, np.array([4]), 8)
    w.pruefe(120)
    b = json.load(open(datei))
    assert b["felder"] == 1 and b["letzter_neuer_takt"] == 110 and b["takt"] == 120
    w.merke(3, np.array([0]), 8)  # DAT_Frei.ungelistet steht nicht in der Feldliste: zaehlt nicht als neues Feld der Liste
    w.pruefe(130)
    assert json.load(open(datei))["felder"] == 1


def test_aufzeichnung_mit_feldwache_schreibt_ihren_stand(tmp_path):
    k = karte()
    spiel = Spiel()
    datei = str(tmp_path / "f.json")
    auf = Aufzeichner(spiel, BEREICHE, tmp_path / "a.auge", {}, takt_adresse=TAKT, felder=FeldWache(k, BEREICHE, datei, alle=5))
    for _ in range(30):
        auf.schritt()
        spiel.weiter()
    auf.schliessen()
    d = json.load(open(datei))
    assert d["felder"] >= 2 and d["letzter_neuer_takt"] is not None


def test_a4_tempotreppe_stufe_mit_zu_wenig_takten_ist_nicht_gemessen():
    z = treppe(1, 0.9, 0.0, 0.0)  # so sah Stufe 1 im Lauf 18:54 aus: 1 Takt, und es hiess "bestaetigt"
    z.update(soll=20, gezaehlt=1, ohne_1=1.0, mit=1.0, ohne_2=1.0)
    e = aw.a4_tempotreppe([z])
    assert e.status == aw.NICHT_GESEHEN and "[1]" in e.text
    z.update(gezaehlt=20)
    assert aw.a4_tempotreppe([z]).status == aw.BESTAETIGT


def test_a10_sieht_doppelte_uid_auch_wenn_nur_ein_platz_sich_aendert(tmp_path):
    def doppelt(s, i):
        if i == 5:
            struct.pack_into("<i", s.m[U], 4 + 16 * 2, 100)
    a = aufzeichnen(tmp_path / "d.auge", stoerung=doppelt)
    e = aw.a10_lebenslauf(a, [("Einheiten", U + 4, 16, 4, 0)])
    assert e.status == aw.WIDERLEGT and "uid 100" in e.text


def test_a10_kopie_auf_dem_merkplatz_ist_kein_verstoss_doppelte_echte_plaetze_schon(tmp_path):
    def kopie(s, i):  # wie setDestinationForUnit: Die Einheit von Platz 2 wird auf Platz 0 kopiert
        if i == 3:
            struct.pack_into("<i", s.m[U], 4, 777)
            struct.pack_into("<i", s.m[U], 4 + 32, 777)
    a = aufzeichnen(tmp_path / "k.auge", stoerung=kopie)
    assert aw.a10_lebenslauf(a, [("Einheiten", U + 4, 16, 4, 1)]).status == aw.BESTAETIGT
    assert aw.a10_lebenslauf(a, [("Einheiten", U + 4, 16, 4, 0)]).status == aw.WIDERLEGT

    def doppelt(s, i):
        if i == 3:
            struct.pack_into("<i", s.m[U], 4 + 16, 777)
            struct.pack_into("<i", s.m[U], 4 + 32, 777)
    b = aufzeichnen(tmp_path / "d2.auge", stoerung=doppelt)
    assert aw.a10_lebenslauf(b, [("Einheiten", U + 4, 16, 4, 1)]).status == aw.WIDERLEGT


A8_TYPEN = dict(TYPEN)


def a8_lauf(tmp_path, stoerung):
    """Kleines Spiel mit den echten Adressen der Spielerdaten: Bestand, Startwaren, Befehlsring."""
    best = aw.SPIELERDATEN + aw.SPIELER_SCHRITT + aw.FELD_BESTAND
    start = aw.SPIELERDATEN + aw.SPIELER_SCHRITT + aw.FELD_START
    gs = start - 8
    laenge = aw.SPIELERDATEN + aw.SPIELER_SCHRITT + max(aw.FELD_STEUER) + 4 - gs

    class S:
        def __init__(self):
            self.m = {gs: bytearray(laenge), TAKT: bytearray(8), 0x5000: bytearray(32)}
            self.t = 1
            struct.pack_into("<i", self.m[TAKT], 0, 1)

        def lies(self, a, n):
            for b, p in self.m.items():
                if b <= a < b + len(p):
                    return bytes(p[a - b:a - b + n])
            raise OSError(a)

        def setze(self, adr, w):
            struct.pack_into("<i", self.m[gs], adr - gs, w)
    s = S()
    bereiche = [Bereich("DAT_GameState", gs, laenge), Bereich("befehle", 0x5000, 32)]
    k = Feldkarte({"G": {"laenge": laenge, "felder": [(start - gs, "int[25]", 100, "startResources"), (best - gs, "int[25]", 100, "currentResources")]}}, [(gs, gs + laenge, "DAT_GameState", "G")], {}, [])
    auf = Aufzeichner(s, bereiche, tmp_path / "a8.auge", {"tempo": 40}, takt_adresse=TAKT)
    for i in range(60):
        auf.schritt()
        struct.pack_into("<i", s.m[TAKT], 0, 2 + i)
        stoerung(s, i, best, start)
    auf.schritt()
    auf.schliessen()
    return aw.a8_buchfuehrung(aw.Aufzeichnung(tmp_path / "a8.auge"), k)


def test_a8_startwaren_und_befehl_sind_ursachen(tmp_path):
    def st(s, i, best, start):
        if i == 10:
            s.setze(start + 4 * 4, 7)
        if i == 11:
            s.setze(start + 4 * 4, 6)
            s.setze(best + 4 * 4, 1)
        if i == 30:
            s.m[0x5000][0] = 1
        if i == 31:
            s.setze(best + 15 * 4, 500)
    e = a8_lauf(tmp_path, st)
    assert e.status == aw.BESTAETIGT, e.daten
    assert e.daten["je_ware"]["Stein"] == {"Startwaren": 1} and e.daten["je_ware"]["Gold"] == {"Befehl": 1}


def test_a8_aenderung_ohne_ursache_ist_widerlegt(tmp_path):
    def st(s, i, best, start):
        if i == 20:
            s.setze(best + 4 * 4, 9)
    e = a8_lauf(tmp_path, st)
    assert e.status == aw.WIDERLEGT and e.daten["ohne_ursache"][0][1] == "Stein"


def test_a8_gold_mit_dem_sammelfeld_im_selben_takt_ist_steuer(tmp_path):
    sammel = aw.SPIELERDATEN + aw.SPIELER_SCHRITT + aw.FELD_STEUER[1]

    def st(s, i, best, start):
        if i == 10:
            s.setze(sammel, 160)  # Woche: nur das Sammelfeld, kein Gold
        if i == 20:
            s.setze(sammel, 0)  # Monatswechsel: Sammelfeld leer, ein Zehntel aufs Gold
            s.setze(best + 15 * 4, 16)
    e = a8_lauf(tmp_path, st)
    assert e.status == aw.BESTAETIGT and e.daten["je_ware"]["Gold"] == {"Steuer": 1}, e.daten
    assert "Stueck fuer Stueck" in e.text


def test_a8_gold_ohne_sammelfeld_ist_ohne_ursache(tmp_path):
    def st(s, i, best, start):
        if i == 20:
            s.setze(best + 15 * 4, 16)
    assert a8_lauf(tmp_path, st).status == aw.WIDERLEGT


def test_a8_neuer_weg_im_selben_takt_erklaert_waren_aber_nie_gold():
    assert aw._ursache(16, False, False, False, set(), False, True) == "Arbeiter neuer Weg"
    assert aw._ursache(15, False, False, False, set(), False, True) is None
    assert aw._ursache(16, False, False, False, set(), False, False) is None


def test_a9_zaehlt_nebeneinanderliegende_plaetze_einzeln(tmp_path):
    def stoer(s, i):
        if i == 4:
            struct.pack_into("<ii", s.m[FREI], 0, 1, 1)
    a = aufzeichnen(tmp_path / "a.auge", stoerung=stoer, bereiche=[Bereich("zeit", TAKT, 8), Bereich("befehle", FREI, 8)])
    assert aw.a9_befehle(a, groesse=4).daten["plaetze"] == 2


def test_a8_ein_betrieb_erklaert_waren_aber_nie_gold():
    assert aw._ursache(4, False, False, False, set(), True) == "Arbeiter"
    assert aw._ursache(15, False, False, False, set(), True) is None
    assert aw._ursache(4, False, True, False, set(), False) is None


def test_a8_ohne_bestandsaenderung_ist_nicht_gesehen(tmp_path):
    assert a8_lauf(tmp_path, lambda *_: None).status == aw.NICHT_GESEHEN


# --- Einzelpunkte ---
LISTE = """# Kopf
### Lauf F, Start: einmal auslesen (2)
- [ ] P001 `eins` (0x00401000): **Lage:** Tabelle lesen · **Messen:** DAT_Zeit.month · **Erwartet:** notieren
### Lauf F: Burgenbau (3)
- [ ] P002 `zwei` (0x00401001): **Lage:** Einheit beobachten · **Messen:** units[id].leben · **Erwartet:** 45
- [ ] P003 `drei` (0x00401002): **Punkt ohne klare Erwartung, erst schärfen:** nichts Bekanntes hier **[Spielart]**
- [ ] P004 `vier` (0x00401003): **Lage:** Monat beobachten · **Messen:** units[id].leben · **Erwartet:** 777
### Lauf K: Gefecht (1)
- [ ] P005 `fuenf` (0x00401004): **Lage:** nie · **Messen:** month · **Erwartet:** 1
"""


def test_einzelpunkte_lesen_urteilen_und_lauf_k_bleibt_draussen(tmp_path):
    from selfaware.tools.analysis import auge_punkte as ap

    d = tmp_path / "liste.md"
    d.write_text(LISTE, encoding="utf-8")
    pp = ap.punkte_lesen(d)
    assert [p.nr for p in pp] == ["P001", "P002", "P003", "P004"]
    assert pp[0].start and not pp[1].start and pp[2].spielart and pp[1].erwartet == "45"
    e = ap.auswerten(d, [aufzeichnen(tmp_path / "a.auge", takte=40)], karte())
    u = {x["nr"]: x["urteil"] for x in e["punkte"]}
    assert u["P002"] == "zahl passt"   # leben laeuft durch 50 - t % 40, 45 kommt vor
    assert u["P003"] == "nicht zuordenbar"
    assert u["P004"] == "zahl weicht ab"
    assert u["P001"] in ("gemessen", "nicht zuordenbar")
    assert "P004" in ap.bericht(e)


def test_rechne_hash_wie_compute_hash():
    import numpy as np

    from selfaware.tools.analysis import auge_auswertung as aw

    # 1 -> gedreht 2; 2 + 2 = 4 -> gedreht 8. Das hoechste Bit kommt unten wieder an.
    werte = np.array([[1, 2], [0x80000000, 0]], dtype=np.uint64)
    assert aw.rechne_hash(werte).tolist() == [8, 2]
    # Die Summe laeuft ueber 32 Bit hinaus: 0xFFFFFFFF + 0x80000001 ist unten 0x80000000, gedreht 1.
    assert aw.rechne_hash(np.array([[0xFFFFFFFF, 0x80000001]], dtype=np.uint64)).tolist() == [1]


def test_spielstand_gleich_achtet_nur_auf_die_maske(tmp_path, monkeypatch):
    import numpy as np

    from selfaware.tools.analysis import auge_auswertung as aw
    from selfaware.tools.experiments import auge_aufzeichnung as aa

    class Quelle:
        def __init__(self, stand):
            self.t, self.stand = 0, stand

        def lies(self, adr, n):
            return struct.pack("<I", self.t) if adr == 0x2000 else bytes(self.stand)

    def aufnahme(name, staende):
        q = Quelle(bytearray(4))
        a = aa.Aufzeichner(q, [aa.Bereich("x", 0x1000, 4, 1)], str(tmp_path / name), takt_adresse=0x2000)
        for i, s in enumerate(staende):
            q.t, q.stand = i + 1, s
            a.schritt()
        a.schliessen()
        return aw.Aufzeichnung(str(tmp_path / name))

    monkeypatch.setattr(aw, "spielmasken", lambda karte, auf: {"x": np.array([True, True, False, False])})

    class Karte:
        def felder_einer_aenderung(self, adr, l):
            return [("g", f"feld{adr - 0x1000}")]

    a = aufnahme("a.auge", [bytes((1, 0, 0, 0)), bytes((2, 0, 0, 0))])
    assert aw.spielstand_gleich(a, 1, aufnahme("b.auge", [bytes((1, 0, 7, 0)), bytes((2, 0, 9, 9))]), 1, 1, Karte()).status == aw.BESTAETIGT, "Ausserhalb der Maske zaehlt nicht"
    e = aw.spielstand_gleich(a, 1, aufnahme("c.auge", [bytes((1, 0, 0, 0)), bytes((3, 0, 0, 0))]), 1, 1, Karte())
    assert e.status == aw.WIDERLEGT and e.daten["erster"] == 1 and e.daten["felder"][0][0] == "g feld0"


def test_spielstand_gleich_ueberspringt_gemischte_takte(tmp_path, monkeypatch):
    import numpy as np

    from selfaware.tools.analysis import auge_auswertung as aw

    class Rahmen:
        def __init__(self, takt, rein):
            self.takt, self.bereich, self.rein = takt, 0, rein

    class Auf:
        namen = ["x"]
        bereiche = [("x", 0x1000, 4, 1)]

    monkeypatch.setattr(aw, "spielmasken", lambda karte, auf: {"x": np.array([True, True, True, True])})
    folge = {"a": [(Rahmen(1, True), bytes(4)), (Rahmen(2, False), bytes((1, 0, 0, 0)))], "b": [(Rahmen(1, True), bytes(4)), (Rahmen(2, True), bytes((2, 0, 0, 0)))]}
    a, b = Auf(), Auf()
    a.name, b.name = "a", "b"
    monkeypatch.setattr(aw, "_je_takt", lambda auf, von, bis: iter(folge[auf.name]))
    e = aw.spielstand_gleich(a, 1, b, 1, 2, None)
    assert e.status == aw.BESTAETIGT and e.daten["gemischt"] == 1, "Ein gemischter Takt sagt nichts ueber das Spiel"


def test_zeilen_nullt_die_merkfelder():
    import numpy as np

    from selfaware.tools.analysis import auge_auswertung as aw

    roh = bytes(range(16))
    z = aw._zeilen(roh, 0, 0, 8, 2, 8, ((4, 4),))
    assert z.shape == (2, 2) and z[:, 1].tolist() == [0, 0] and z[0, 0] == int.from_bytes(bytes(range(4)), "little")


def test_a11_rechnet_die_teilsummen_nach(tmp_path, monkeypatch):
    import numpy as np

    from selfaware.tools.analysis import auge_auswertung as aw
    from selfaware.tools.experiments import auge_aufzeichnung as aa

    FELDER = {("DAT_GameSynchronyState", "HASH_HashTotal"): (0x100, 4, 4, 9), ("DAT_GameSynchronyState", "HASH_Units"): (0x200, 4, 4, 1), ("DAT_GameSynchronyState", "HASH_Buildings"): (0x300, 4, 4, 1), ("DAT_GameSynchronyState", "HASH_Trees"): (0x400, 4, 4, 1), ("DAT_GameSynchronyState", "HASH_Tribes"): (0x500, 4, 4, 1), ("DAT_GameSynchronyState", "HASH_PlayerDatas"): (0x600, 4, 4, 1),
              ("DAT_UnitsState", "units[].animationTicker"): (0x1010, 4, 0x480, 1), ("DAT_BuildingsState", "buildings[].animationIndex"): (0x3010, 2, 0x340, 1), ("DAT_LandscapeState", "trees[].state"): (0x5000, 4, 0x58, 1), ("DAT_TribesState", "tribes[].owner"): (0x6000, 4, 0x330, 1), ("DAT_GameState", "playerDataArray[].someAiCountdown3"): (0xB84C, 4, 0x39F4, 1)}

    class Karte:
        def adresse(self, g, f):
            return FELDER[(g, f)]

    groessen = {"DAT_UnitsState": (0x1000, 0x500), "DAT_BuildingsState": (0x3000, 0x400), "DAT_LandscapeState": (0x5000, 0x58), "DAT_TribesState": (0x6000, 0x330), "DAT_GameState": (0x8000, 0x39F4)}
    stand = {n: bytearray((i * 7 + 3) % 251 for i in range(g)) for n, (b, g) in groessen.items()}

    def hash_von(n, adr, laenge, nullen=(), plus=0):
        z = aw._zeilen(bytes(stand[n]), groessen[n][0], adr, 0x10000, 1, laenge, nullen)
        return (int(aw.rechne_hash(z)[0]) + plus) & 0xFFFFFFFF

    def i32(n, adr):
        return struct.unpack_from("<I", stand[n], adr - groessen[n][0])[0]

    u = 0x1010
    einheiten = hash_von("DAT_UnitsState", u + 0x4C, 0x404, ((0x3DC - 0x4C, 8),), sum(i32("DAT_UnitsState", u + o) for o in (-4, 0, 4)))
    g = 0x3010
    kurz = struct.unpack_from("<h", stand["DAT_BuildingsState"], g - 0x3000)[0]
    gebaeude = hash_von("DAT_BuildingsState", g + 0xB0, 0x25C, ((0x2DC - 0xB0, 2),), kurz + sum(struct.unpack_from("<i", stand["DAT_BuildingsState"], g - 0x3000 + o)[0] for o in (0x34, 0x30, 0x2C, 0x28, -0x10)))
    baeume, gruppen = hash_von("DAT_LandscapeState", 0x5000, 0x58), hash_von("DAT_TribesState", 0x6000, 0x330)
    spieler = hash_von("DAT_GameState", 0x8000, 0x399C, ((0x384C, 16), (0x384C + 0x12C, 4)))

    def block(falsch=0):
        d = bytearray(0x700)
        struct.pack_into("<9i", d, 0x100, 5, 0, 0, 0, 0, 0, 0, 0, 0)
        for a, w in ((0x200, einheiten + falsch), (0x300, gebaeude), (0x400, baeume), (0x500, gruppen), (0x600, spieler)):
            struct.pack_into("<I", d, a, w & 0xFFFFFFFF)
        return bytes(d)

    class Quelle:
        def __init__(self, d):
            self.d = d

        def lies(self, adr, n):
            if adr == 0x20000:
                return struct.pack("<I", 1)
            if adr == 0:
                return self.d
            for name, (b, gr) in groessen.items():
                if adr == b:
                    return bytes(stand[name])
            raise AssertionError(hex(adr))

    def aufnahme(name, d):
        be = [aa.Bereich("datenblock", 0, 0x700, 1)] + [aa.Bereich(n, b, gr, 1) for n, (b, gr) in groessen.items()]
        a = aa.Aufzeichner(Quelle(d), be, str(tmp_path / name), takt_adresse=0x20000)
        a.schritt()
        a.schliessen()
        return aw.Aufzeichnung(str(tmp_path / name))

    assert aw.a11_pruefsummen(aufnahme("gut.auge", block()), Karte()).status == aw.BESTAETIGT
    e = aw.a11_pruefsummen(aufnahme("falsch.auge", block(1)), Karte())
    assert e.status == aw.WIDERLEGT and e.daten["teile"]["Einheiten"]["gleich"] == 0 and e.daten["teile"]["Baeume"]["gleich"] == 1


def test_auswertung_k_kennt_alle_fenster_und_geht_nach_abbruch_weiter(tmp_path, monkeypatch):
    from selfaware.tools.analysis import auge_ergebnis as ae

    prot = [{"abschnitt": "sichern", "daten": {"t": 100, "t1": {"von": 100, "bis": 2100}}}]
    da = ["haupt", "t1", "danach", "t2", "t3", "t4", "t5", "t6", "t7", "t8", "t9"]
    aufg = ae.aufgaben_k(da, prot)
    gleich = [a[2] for a in aufg if a[0] == "gleich"]
    assert ("t1", 101, "t2", 100, 1999) in gleich, "Das Laden rechnet einen Schritt: t1 einen Takt spaeter"
    assert [g[0] for g in gleich] == ["t1", "t2", "t4", "t6", "t8"]
    assert {a[1] for a in aufg if a[0] == "A1"} == set(da)
    assert [a[1] for a in aufg if a[0] == "Punkte"] == ["K", "F"]
    ohne = ae.aufgaben_k(["haupt", "t1", "danach"], prot)
    assert not [a for a in ohne if a[0] in ("A5", "gleich")], "Ohne Ladefenster gibt es nichts zu vergleichen"

    laeufe = []

    def rechne(basis, lauf_f, art, zu, arg):
        laeufe.append((art, zu))
        return aw.Ergebnis(art, aw.GEMESSEN, "x")

    monkeypatch.setattr(ae, "_rechne_k", rechne)
    a = ae.probe_k("b", None, ("A1", "t1", ("t1",)), str(tmp_path))
    b = ae.probe_k("b", None, ("A1", "t1", ("t1",)), str(tmp_path))
    c = ae.probe_k("b", None, ("A1", "t2", ("t2",)), str(tmp_path))
    assert a.text == b.text == c.text == "x" and laeufe == [("A1", "t1"), ("A1", "t2")], "Fertige Proben werden nicht neu gerechnet, andere schon"
    ae.probe_k("b", None, ("A1", "t1", ("t1",)))
    assert len(laeufe) == 3, "Ohne Ordner kein Merken"


def test_warten_nach_dem_hochzaehlen(tmp_path):
    from selfaware.tools.experiments import auge_aufzeichnung as aa

    class Quelle:
        def __init__(self):
            self.gelesen = []

        def lies(self, adr, n):
            self.gelesen.append((adr, uhr.jetzt))
            return bytes(n)

    class Uhr:
        jetzt = 0.0

        def __call__(self):
            Uhr.jetzt += 0.001
            return Uhr.jetzt
    uhr = Uhr()
    q = Quelle()
    a = aa.Aufzeichner(q, [aa.Bereich("x", 0x1000, 8, 1)], str(tmp_path / "a.auge"), takt_adresse=0x2000, uhr=uhr, warte_ms=5)
    t0 = uhr.jetzt
    a.schritt()
    a.schliessen()
    erste = next(z for ad, z in q.gelesen if ad == 0x1000)
    assert erste - t0 >= 0.005, "Das Lesen beginnt erst nach der Wartezeit"


def test_einzelpunkte_von_lauf_k_lassen_sich_einzeln_lesen(tmp_path):
    from selfaware.tools.analysis import auge_punkte as ap

    d = tmp_path / "liste.md"
    d.write_text(LISTE, encoding="utf-8")
    assert [p.nr for p in ap.punkte_lesen(d, "K")] == ["P005"]


def test_einzelpunkt_feld_ohne_aenderung_ist_nicht_gesehen():
    from selfaware.tools.analysis import auge_punkte as ap

    p = ap.Punkt("P9", "f", "0x1", False, lage="x", messen="y", erwartet="3")
    b = [{"aenderungen": 0, "werte": [3], "mehr_werte": False}]
    assert ap.urteil(p, b)[0] == "nicht gesehen"
    b = [{"aenderungen": 2, "werte": list(range(40)), "mehr_werte": True}]
    assert ap.urteil(ap.Punkt("P9", "f", "0x1", False, erwartet="77"), b)[0] == "gesehen", "bei abgeschnittener Werteliste darf keine Abweichung gemeldet werden"


def test_belege_lesen_jedes_stueck_an_seiner_stelle(tmp_path):
    from selfaware.tools.analysis import auge_punkte as ap

    def stoer(s, i):
        struct.pack_into("<h", s.m[U], 4 + 16 * 0 + 8, 1000 + i)
        struct.pack_into("<h", s.m[U], 4 + 16 * 2 + 8, 2000 + i)

    b = ap.Belege([("DAT_Einheiten", "units[].x", U + 4 + 8, 2, 16, 4, 1)], karte())
    b.lies(aufzeichnen(tmp_path / "b.auge", stoerung=stoer))
    d = b.daten[("DAT_Einheiten", "units[].x")]
    assert any(w >= 2000 for w in d["werte"]) and any(1000 <= w < 2000 for w in d["werte"]), "Zwei Stuecke im selben Rahmen, zwei Einheiten"
    assert d["aenderungen"] >= 2 * 25


def test_einzelpunkt_zahl_im_ruhenden_feld_zaehlt_mit():
    from selfaware.tools.analysis import auge_punkte as ap

    # P142 in der Probe: aleRate steht auf 36, es aendert sich nur die mitgenommene Warenliste. Das ist keine Abweichung
    b = [{"aenderungen": 0, "werte": [36], "mehr_werte": False}, {"aenderungen": 5, "werte": [1, 2], "mehr_werte": False}]
    assert ap.urteil(ap.Punkt("P9", "f", "0x1", False, erwartet="36"), b)[0] == "zahl passt"
    assert ap.urteil(ap.Punkt("P9", "f", "0x1", False, erwartet="37"), b)[0] == "zahl weicht ab"
