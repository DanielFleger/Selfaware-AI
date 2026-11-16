"""Daniel 16.11.2026 19:42 (Bild DD-Berichte/SAI/SAI_2026-11-16_bilder/daniel_1942_kornspeicher_fast_kaputt.webp): "warum hier eine assassine
sich nicht opfert um den kornspeicher der fast kaputt ist zu nehmen, die einheiten sollten die lebenspunkte der gebaeude kennen"; 19:54 "das
kann man auch als spieler sehen ... als regler die todesrisiken rein"; 19:57 "es sollte sowas wie schlaues risiko sein"."""

import json

import pytest

from selfaware.baukasten import regler as RG
from selfaware.baukasten import wirkung as WK
from selfaware.micro.tasks import assassinen as AS


class _Sicht:
    def sicht_abstand(self, p):
        return 50


@pytest.fixture
def leben_datei(tmp_path, monkeypatch):
    p = tmp_path / "gebaeude_leben.json"
    p.write_text(
        json.dumps(
            {
                "gebaeude": {
                    "19": {"leben_max": 300},
                    "9": {"leben_max": 350},
                    "1": {"leben_max": 200},
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(WK, "GEBAEUDE_LEBEN", str(p))
    WK._leben_max.clear()
    yield p
    WK._leben_max.clear()


def _assassine(beschuss=0.0, gesehen=None):
    a = object.__new__(AS.Einzeln)
    a._route_sperre, a.jetzt, a.entdeckt = {}, 0, {}
    a._gb_max = dict(gesehen or {})
    a._beschuss_angriff = lambda gn, G, ort: (
        beschuss.get(gn, 0.0) if isinstance(beschuss, dict) else beschuss
    )
    a._sicht = _Sicht()
    return a


L = {1: {"leben": 12500, "x": 100, "y": 100}}
G = {
    7: {"typ": 19, "x": 110, "y": 100, "leben": 300, "besitzer": 1},  # Kornspeicher heil, 10 Felder
    8: {
        "typ": 19,
        "x": 114,
        "y": 100,
        "leben": 30,
        "besitzer": 1,
    },  # Kornspeicher fast kaputt, 14 Felder, zum ersten Mal gesehen
}
K = [(7, (110, 100), 19, True, 0, 0, 0, None, 0), (8, (114, 100), 19, True, 0, 0, 0, None, 0)]


def test_fast_zerstoertes_gebaeude_wird_gewaehlt_auch_beim_ersten_blick(leben_datei):
    # das volle Leben kommt aus der Datei - ohne sie hielte die Assassine 30 Leben fuer ein ganzes Gebaeude (erste Sichtung)
    beste = _assassine()._ziel_bewerten(1, (100, 100), K, {}, L, G, None, {})
    assert beste[1][0] == 8


def test_rest_anteil(leben_datei):
    assert WK.rest_anteil(19, 300) == 1.0 and WK.rest_anteil(19, 30) == pytest.approx(0.1)
    assert WK.rest_anteil(99, 50, gesehen=100) == 0.5  # Art ohne Eintrag: hoechstes gesehenes Leben
    assert WK.rest_anteil(19, 0) == WK.REST_MIN


def test_nahkaempfer_rechnen_mit_der_restarbeit(leben_datei):
    w = WK.Wissen(
        tabelle=({}, {}, {}), gebaeude={}, eichung={}, gebaeudeschaden={24: 10.0, 73: 75.0}
    )
    heil = WK.Ziel(("g", 7), 19, (110, 100), 100.0, (), (), leben=300.0)
    kaputt = WK.Ziel(("g", 8), 19, (110, 100), 100.0, (), (), leben=30.0)
    assert w.rechnen_mit(24, kaputt)[0] == pytest.approx(w.rechnen_mit(24, heil)[0] * 0.1)


def _kaserne_und_huette():
    G2 = {
        9: {"typ": 9, "x": 110, "y": 100, "leben": 350, "besitzer": 1},
        1: {"typ": 1, "x": 110, "y": 101, "leben": 200, "besitzer": 1},
    }
    return (
        G2,
        (9, (110, 100), 9, True, 0, 0, 0, None, 0),
        (1, (110, 101), 1, True, 0, 0, 0, None, 0),
    )


def test_schlaues_risiko_nimmt_die_kaserne_auch_bei_hohem_todesrisiko(
    leben_datei, tmp_path, monkeypatch
):
    # Beschuss je Ziel so, dass das Todesrisiko an der Kaserne (Wert 800) bei 80 % liegt und an der Huette (Wert 60) bei 60 %:
    # Risiko = Beschuss x (Zeit am Ziel + 10 Felder x 16 Takte) / 12.500 Leben; Kaserne 666 Takte, Huette 194
    monkeypatch.setattr(RG, "STELL_DATEI", str(tmp_path / "stell.json"))
    G2, kas, hue = _kaserne_und_huette()
    a = _assassine(beschuss={9: 0.8 * 12500 / (666 + 160), 1: 0.6 * 12500 / (194 + 160)})
    k = a._ziel_bewerten(1, (100, 100), [kas], {}, L, G2, None, {})
    h = a._ziel_bewerten(1, (100, 100), [hue], {}, L, G2, None, {})
    assert k is not None and k[2] == pytest.approx(
        0.8, abs=0.01
    )  # frueher: weit ueber jeder festen Grenze (10 %, beobachtet 5 %)
    assert h is None  # 60 x 0,4 < 0,6 x 70: die Huette ist das Leben nicht wert
    RG.stell_setzen(
        -10, "Test", "vorsichtig"
    )  # Leben zaehlt vierfach: auch die Kaserne lohnt bei diesem Risiko nicht mehr
    assert a._ziel_bewerten(1, (100, 100), [kas], {}, L, G2, None, {}) is None
    RG.stell_setzen(10, "Test", "wagemutig")
    assert a._ziel_bewerten(1, (100, 100), [kas], {}, L, G2, None, {}) is not None


def test_risiko_grenze_und_regler(tmp_path, monkeypatch):
    monkeypatch.setattr(RG, "STELL_DATEI", str(tmp_path / "stell.json"))
    assert RG.stell_lesen()["risikofreude"] == 0.0 and RG.lebensgewicht() == 1.0
    assert RG.risiko_grenze(60, 70) == pytest.approx(60 / 130)
    RG.stell_setzen(10, "Test")
    assert RG.lebensgewicht() == pytest.approx(0.25)
    RG.stell_setzen(99, "Test")  # ausserhalb -10..10 wird begrenzt
    st = RG.stell_lesen()
    assert st["risikofreude"] == 10.0 and [v["neu"] for v in st["verlauf"]] == [10.0, 10.0]
