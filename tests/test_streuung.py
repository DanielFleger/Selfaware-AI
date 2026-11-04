# -*- coding: utf-8 -*-
"""Die Geschoss- und Feuer-Regeln gegen echte Spielwerte: direkt gerufene Zielfunktionen (streuung_beispiele.json) und aufgezeichnete Fluege (flug_beispiele.json). Kein Spiel noetig."""
import json
import os
import sys

import pytest

HIER = os.path.join("data", "research", "auge_plan", "streuung_20261104")
sys.path.insert(0, os.path.abspath(HIER))
import flug_modell as fm  # noqa: E402
import streuung_modell as sm  # noqa: E402

BSP = json.load(open(os.path.join(HIER, "streuung_beispiele.json"), encoding="utf-8"))
FLUG = json.load(open(os.path.join(HIER, "flug_beispiele.json"), encoding="utf-8"))


def test_es_gibt_genug_beispiele_jeder_art():
    for teil in ("boden", "einheit", "bodenweg"):
        assert len(BSP[teil]) >= 300, teil
        assert {b["typ"] for b in BSP[teil]} >= {22, 23, 70, 72, 74, 76, 39, 40, 41, 61, 77}, teil
    assert {f["art"] for f in FLUG["fluege"]} >= {1, 2, 3, 4, 7, 20, 33, 34}
    assert len(FLUG["feuer"]) >= 10


def test_erste_stufe_wie_im_spiel():
    for b in BSP["boden"]:
        assert sm.ziel_boden(b["typ"], bool(b["auf_boden"]), b["sx"], b["sy"], b["blick"], b["tx"], b["ty"], b["tz"], b["r"]) == tuple(b["ist"]), b


def test_schuss_auf_einheit_wie_im_spiel():
    for b in BSP["einheit"]:
        x, y, z = sm.zielpunkt_einheit(b["ex"], b["ey"], b["ez"], b["lauf"] == 2, b["blick"], b["abst"], b["ts"], b["tl"])
        sx, sy, sz, zieht = sm.streuung_einheit(x, y, z, b["typ"], b["eigen"], b["r"], b["rng_e"], b["rng_z"])
        assert (sx, sy, sz) == tuple(b["ist"]), b
        assert int(zieht) == b["zog"], b


def test_bodenweg_zieht_zwei_zahlen_wie_im_spiel():
    zwei = 0
    for b in BSP["bodenweg"]:
        x, y, z, zog = sm.ziel_vorbereiten_boden(b["typ"], bool(b["auf_boden"]), b["sx"], b["sy"], b["blick"], b["tx"], b["ty"], b["tz"], b["eigen"], b["rng_e"], [b["r1"], b["r2"]], 0)
        assert (x, y, z) == tuple(b["ist"]), b
        assert zog == b["zog"], b
        zwei += zog == 2
    assert zwei > 100  # sonst prueft der Test die zweite Stufe nicht


@pytest.mark.parametrize("f", FLUG["fluege"], ids=lambda f: "Art%d_%d" % (f["art"], f["mx"]))
def test_flug_jeder_takt_wie_aufgezeichnet(f):
    assert fm.anfang(f["art"], f["gesamt"], f["zz"] - f["h0"], f["v"]) == (f["v"], f["w"])
    letzt = (f["mx"], f["my"], 0)
    for soll, (n, schr, h_e) in zip(f["reihe"], fm.bahn(f["mx"], f["my"], f["h0"], f["zx"], f["zy"], f["vc"], f["vs"], f["b"])):
        if schr:
            letzt = (schr[-1][0], schr[-1][1], schr[-1][3])
        assert [letzt[0], letzt[1], h_e, letzt[2]] == soll, (n, f["art"])


@pytest.mark.parametrize("b", FLUG["abprall"], ids=lambda b: "Richtung%d_%d" % (b["ori"], b["a"]))
def test_abprall_wie_aufgezeichnet(b):
    tx, ty = fm.abprall_ziel(b["ori"], b["a"], b["c"], b["sx"], b["sy"], b["bits"])
    v, w, vc, vs = fm.nach_abprall(fm.drehung(b["vc"], b["vs"], b["b"], b["tt"], b["w0"]), b["v_alt"])
    assert (v, w) == (b["v"], b["w"])
    letzt = (b["a"], b["c"], 0)
    for soll, (n, schr, h_e, tt) in zip(b["reihe"], fm.bahn2(b["a"], b["c"], b["h"], tx, ty, vc, vs, b["b"], t0=0.0)):
        if schr:
            letzt = (schr[-1][0], schr[-1][1], schr[-1][3])
        assert [letzt[0], letzt[1], h_e, letzt[2]] == soll, n


def test_abprall_mehrere_richtungen():
    assert len({b["ori"] for b in FLUG["abprall"]}) >= 5


FENSTER = json.load(open(os.path.join(HIER, "fenster_beispiele.json"), encoding="utf-8"))


def test_trefferfenster_wie_im_spiel():
    fremd = [b for b in FENSTER if not b["team"]]
    assert len(fremd) >= 80
    for b in fremd:
        f = fm.fenster(b["typ"]) if b["abstand"] == 0 else fm.fenster_nachbar(b["typ"])
        assert b["ist"] == int(8 <= b["h"] <= 8 + f), b


def test_teamregel_wie_im_spiel():
    eigen = [b for b in FENSTER if b["team"]]
    assert len(eigen) >= 70 and {b["art"] for b in eigen} >= {1, 7, 33, 2, 3, 4, 20}
    for b in eigen:
        assert b["ist"] == int(not fm.freund_verschont(b["art"], b["typ"], True)), b


def test_tabellen_wie_im_spiel():
    assert sm.FEUER_VERSATZ == [tuple(x) for x in FLUG["versatz"]]
    for art, (kurve, wert, b) in fm.TABELLE.items():
        assert FLUG["geschoss_tabelle"][str(art)] == [kurve, wert, b], art


def test_feuer_liegt_im_versatz_der_flamme():
    tabelle = set(sm.FEUER_VERSATZ)
    for b in FLUG["feuer"]:
        assert (b["feuer"][0] - b["land"][0], b["feuer"][1] - b["land"][1]) in tabelle, b


def test_fenster_und_feuerschaden_aus_dem_code():
    assert fm.fenster(24) == 42 and fm.fenster(fm.UT_SCHILD) == 90 and fm.fenster(fm.UT_RAMME) == 40
    assert sm.feuerschaden(24, True) == 37 and sm.feuerschaden(24, False) == 75
    assert sm.feuerschaden(76, True) == 5 and sm.feuerschaden(55, False) == 25 and sm.feuerschaden(53, True) == 0


def test_bogenschuetze_streut_auf_gleicher_hoehe_nicht():
    assert sm.fehler_stufe(22, 8, 8) == 0  # gleich hoch
    assert sm.fehler_stufe(22, 8, 58) == 0  # von oben nach unten
    assert sm.fehler_stufe(22, 108, 8) == 150  # 100 hoeher: 100 plus die Haelfte, also 150 von 300
    assert sm.fehler_stufe(77, 108, 8) == 0  # Feuerballista bleibt genau


def test_negative_abstaende_rechnen_wie_c():
    assert sm._ab(-7, 2) == -3 and sm._rest(-7, 2) == -1
    assert sm._d34(-5) == -3
