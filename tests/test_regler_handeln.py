"""Regler aendern das Handeln (Daniel 16.11.2026 18:18 "am wichtigsten ... dass auch wirklich anders gehandelt wird wenn man regler umstellt";
18:37 "ja, verbinde die regler"). Je Kopplung: Startgewicht = Verhalten wie vorher, verstellter Regler = andere Entscheidung."""

import json

import pytest

from selfaware.baukasten import regler as RG
from selfaware.micro import wegfuehrung as W
from selfaware.services import gefecht


@pytest.fixture
def regler(tmp_path, monkeypatch):
    datei = tmp_path / "regler.json"
    monkeypatch.setattr(RG, "DATEI", str(datei))
    RG.neu_lesen()

    def setzen(**gewichte):
        r = [
            {"id": k, "messgroesse": k, "arten": "alle", "gewicht": float(v), "archiviert": False}
            for k, v in gewichte.items()
        ]
        datei.write_text(json.dumps({"regler": r}), encoding="utf-8")
        RG.neu_lesen()

    yield setzen
    RG.neu_lesen()


def test_ohne_datei_und_mit_startgewichten_wie_vorher(regler):
    assert RG.staerke("kehrtwende") == 1.0
    assert (
        RG.wechsel_huerde() == 1.0
        and RG.leer_runden(W.LEER_RUNDEN) == W.LEER_RUNDEN
        and gefecht.behalten() == gefecht.BEHALTEN
    )
    regler(kehrtwende=-1, steht_ohne_wirkung=-1, vorstoss=1)
    assert (
        RG.wechsel_huerde() == 1.0
        and RG.leer_runden(W.LEER_RUNDEN) == W.LEER_RUNDEN
        and gefecht.behalten() == pytest.approx(gefecht.BEHALTEN)
    )


def test_kehrtwende_staerker_hebt_die_huerde(regler):
    regler(kehrtwende=-5)
    assert RG.wechsel_huerde(24) == pytest.approx(1.4)


def test_leben_einsetzen_staerker_nimmt_knappe_gefechte_an(regler):
    regler(vorstoss=5)
    assert gefecht.behalten() == pytest.approx(0.2)


class _B:
    def __init__(self):
        self.liste = []

    def __call__(self, b, _w=None, bis=None):
        self.liste.append(b)


def _e(owner, typ, x, y, leben=10000, **k):
    d = {"besitzer": owner, "typ": typ, "x": x, "y": y, "leben": leben}
    d.update(k)
    return d


def _bis_kein_weg():
    """Runden, bis ein Speertraeger, der neben seinem Ziel steht und nichts bewirkt, 'kein_weg' meldet (#362)."""
    w = W.Wegfuehrung(1)
    w.fuehre(1, "gebaeude", 7, "nahkampfraid")
    for runde in range(1, 20):
        st = w.schritt({1: _e(1, 24, 199, 101, zustand=2)}, {7: _e(2, 3, 200, 100, leben=60)}, _B())
        if st[1] == "kein_weg":
            return runde
    return None


def test_steht_ohne_wirkung_staerker_wechselt_frueher(regler):
    regler(steht_ohne_wirkung=-1)
    normal = _bis_kein_weg()
    regler(steht_ohne_wirkung=-3)
    schnell = _bis_kein_weg()
    assert normal == 4 and schnell == 2, (
        normal,
        schnell,
    )  # 1 Runde Angriff, dann 3 bzw. 1 Runde ohne Wirkung
