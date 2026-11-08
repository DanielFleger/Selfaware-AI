"""B-145 S4, B-169: der Leser des gemeinsamen Speichers versteht den Aufbau und lehnt einen fremden ab (offline)."""

import csv
import pathlib
import re
import struct

import pytest

from selfaware.game import kern_leitung as KL

STAMM = pathlib.Path(__file__).resolve().parents[1]
RUST = (STAMM / "crates/samurai-kern/src/leitung.rs").read_text(encoding="utf-8")
LISTE = STAMM / "data/research/auge_plan/feldliste_gehirn.csv"
ICH, GEGNER = 1, 2


def _einheit(b, i, **w):
    """Eine Einheit in den Puffer; nicht genannte Felder sind 0."""
    werte = [w.get(n, 0) for n in KL.EINHEIT_FELDER]
    struct.pack_into(KL.EINHEIT_FORMAT, b, KL.KOPF + i * KL.EINHEIT, *werte)


def _puffer(aufbau=KL.AUFBAU, nt=0, nq=0, lord=0, ne=2):
    b = bytearray(KL.GROESSE)
    struct.pack_into(
        KL.KOPF_FORMAT, b, 0, KL.KENNUNG, aufbau, 4, 40471, 2, ICH, ne, 1, 9, 63, 9, 3, lord, nt, nq
    )
    _einheit(
        b,
        0,
        nr=85,
        leben=12000,
        besitzer=ICH,
        typ=70,
        x=163,
        y=192,
        zustand=6,
        laufx=163,
        laufy=192,
        gruppe=16,
        zielart=17,
        bild=6,
        feinx=1307,
        feindabstand=120,
        schusseinheit=91,
        getoetet=0,
    )
    _einheit(
        b,
        1,
        nr=91,
        leben=28000,
        besitzer=GEGNER,
        typ=26,
        x=162,
        y=191,
        zustand=2,
        laufx=162,
        laufy=191,
        gruppe=16,
        zielart=17,
        nahziel=-1,
        bildzyklus=3,
        feiny=1533,
        teilzustand=1,
    )
    struct.pack_into(
        KL.GEBAEUDE_FORMAT, b, KL.GEBAEUDE_START, 239, 46, 2, 149, 104, 1500, 46, 1
    )  # B-150: Feuerwert 46 = brennt
    struct.pack_into("<i", b, KL.VORRAT_START + (1 * KL.WAREN + 15) * 4, 5000)
    struct.pack_into("<i", b, KL.VORRAT_START + (1 * KL.WAREN + 2) * 4, 120)
    return b


def test_aufbau_wird_vollstaendig_gelesen():
    w = KL.entpacken(bytes(_puffer()))
    assert (w.tick, w.epoche, w.ich, w.kern, w.graben_geplant, w.graben_ausgehoben) == (
        40471,
        2,
        ICH,
        9,
        9,
        63,
    )
    assert set(w.einheiten) == {85, 91}
    assert w.einheiten[85]["laufx"] == 163 and w.einheiten[85]["gruppe"] == 16
    assert w.einheiten[91]["nahziel"] == -1
    assert w.beschuss == 3
    assert w.gebaeude == {
        239: {
            "nr": 239,
            "typ": 46,
            "besitzer": 2,
            "x": 149,
            "y": 104,
            "leben": 1500,
            "feuer": 46,
            "tor": 1,
        }
    }
    assert w.vorrat[1]["gold"] == 5000 and w.vorrat[1]["holz"] == 120 and w.vorrat[2]["gold"] == 0


def test_neue_felder_kommen_an():
    e = KL.entpacken(bytes(_puffer())).einheiten[85]
    assert (e["bild"], e["feinx"], e["feindabstand"], e["schusseinheit"]) == (6, 1307, 120, 91)


def test_fremde_einheit_hat_keine_verbotenen_schluessel():
    fremd = KL.entpacken(bytes(_puffer())).einheiten[91]
    assert not KL.NUR_EIGEN & set(fremd)
    assert (fremd["bildzyklus"], fremd["feiny"], fremd["teilzustand"]) == (3, 1533, 1)


def test_trupps_geschosse_und_lord():
    b = _puffer(nt=1, nq=1, lord=321)
    struct.pack_into(KL.TRUPP_FORMAT, b, KL.TRUPP_START, 16, 7777, 3, 120, 130, 239)
    struct.pack_into(
        KL.GESCHOSS_FORMAT,
        b,
        KL.GESCHOSS_START,
        44,
        24,
        1,
        GEGNER,
        1300,
        1500,
        60,
        162,
        187,
        12,
        0,
        31000,
        5,
        0.5,
        -0.25,
    )
    w = KL.entpacken(bytes(b))
    assert w.lord_feindabstand == 321
    assert w.trupps == {
        16: {
            "nr": 16,
            "zielgebaeude_uid": 7777,
            "zustand": 3,
            "zielx": 120,
            "ziely": 130,
            "zielgebaeude": 239,
        }
    }
    q = w.geschosse[44]
    assert (q["typ"], q["besitzer"], q["feinx"], q["feld"], q["vcos"], q["vsin"]) == (
        24,
        GEGNER,
        1300,
        31000,
        0.5,
        -0.25,
    )


def test_fremder_aufbau_wird_abgelehnt():
    with pytest.raises(KL.FalscherAufbau):
        KL.entpacken(bytes(_puffer(aufbau=2)))


def test_groessen_passen_zu_den_formaten():
    assert struct.calcsize(KL.KOPF_FORMAT) <= KL.KOPF
    for format_, groesse in (
        (KL.EINHEIT_FORMAT, KL.EINHEIT),
        (KL.GEBAEUDE_FORMAT, KL.GEBAEUDE),
        (KL.TRUPP_FORMAT, KL.TRUPP),
        (KL.GESCHOSS_FORMAT, KL.GESCHOSS),
    ):
        assert struct.calcsize(format_) == groesse


def test_konstanten_gleich_wie_im_kern():
    for name, wert in (
        ("AUFBAU: u32", KL.AUFBAU),
        ("EINHEIT: usize", KL.EINHEIT),
        ("GEBAEUDE: usize", KL.GEBAEUDE),
        ("TRUPP: usize", KL.TRUPP),
        ("GESCHOSS: usize", KL.GESCHOSS),
        ("MAX_TRUPPS: usize", KL.MAX_TRUPPS),
        ("MAX_GESCHOSSE: usize", KL.MAX_GESCHOSSE),
    ):
        assert f"pub const {name} = {wert};" in RUST


def _reihe(erstes):
    """Die Felder in der Reihenfolge, in der der Kern sie schreibt (Liste, die mit diesem Namen beginnt)."""
    m = re.search(r"\[(" + re.escape(erstes) + r"[^\]]*)\]", RUST)
    assert m, erstes
    return [
        n.strip().split(".", 1)[1].replace(" as i16", "")
        for n in m.group(1).split(",")
        if n.strip()
    ]


def test_reihenfolge_wie_der_kern_schreibt():
    kern = ["nr", "leben", *_reihe("e.besitzer"), *_reihe("e.bild"), *_reihe("e.feinx")]
    assert tuple(kern) == KL.EINHEIT_FELDER
    assert ("nr", *_reihe("b.typ")) == KL.GEBAEUDE_FELDER
    assert ("nr", "zielgebaeude_uid", *_reihe("t.zustand")) == KL.TRUPP_FELDER
    assert ("nr", *_reihe("q.typ"), "feld", "richtung", "vcos", "vsin") == KL.GESCHOSS_FELDER


def test_kern_schwaerzt_genau_was_python_als_nur_eigen_fuehrt():
    welt = (STAMM / "crates/samurai-kern/src/welt.rs").read_text(encoding="utf-8")
    block = re.search(r"pub fn fuer_fremde.*?\.\.\*e", welt, re.S).group(0)
    assert set(re.findall(r"(\w+): 0,", block)) == set(KL.NUR_EIGEN)


def _liste():
    with open(LISTE, encoding="utf-8") as d:
        return list(csv.DictReader(d, delimiter=";"))


def test_kein_takt_feld_fehlt():
    fehlt = [z["feld"] for z in _liste() if z["bedarf"] == "takt" and z["ankunft"] == "fehlt"]
    assert fehlt == []


def test_sichtschranke_passt_zu_den_feldern_der_leitung():
    marken = {z["feld"]: z for z in _liste()}
    for name, spiel in KL.EINHEIT_SPIELFELD.items():
        z = marken[f"units[].{spiel}"]
        assert z["eigen"] == "erlaubt", spiel
        assert (z["fremd"] == "erlaubt") == (name not in KL.NUR_EIGEN), spiel
