"""B-176, B-177: Baukasten, ohne Spiel."""

import pathlib
import re

import pytest

from selfaware.baukasten.ausweichen import NACHLAUF, SCHUSSWEITE, Schussfeld
from selfaware.baukasten.bestellung import ARTEN, Bestellung

LENKER = (
    pathlib.Path(__file__).resolve().parents[1] / "src/selfaware/runtime/live/erstes_spiel.py"
).read_text(encoding="utf-8")


def test_ohne_schalter_duerfen_alle_arten_werben():
    b = Bestellung()
    assert all(b.darf(a) for a in ARTEN)


def test_nur_raid_laesst_angriff_und_verteidigung_nicht_werben():
    b = Bestellung("raid")
    assert b.darf("raid") and not b.darf("angriff") and not b.darf("verteidigung")
    assert str(b) == "raid"


def test_mehrere_arten_gehen():
    b = Bestellung("raid, verteidigung")
    assert b.darf("raid") and b.darf("verteidigung") and not b.darf("angriff")


@pytest.mark.parametrize("text", ["", "raids", "alle,raid"])
def test_falsche_schreibweise_faellt_auf(text):
    with pytest.raises(ValueError):
        Bestellung(text)


def test_unbekannte_art_faellt_auf():
    with pytest.raises(ValueError):
        Bestellung().darf("heer")


def _e(x, y, typ=71, besitzer=1, leben=1000):
    return {"x": x, "y": y, "typ": typ, "besitzer": besitzer, "leben": leben}


def _runde(s, L=None, G=None):
    s.neue_runde(L or {}, G or {})


def test_keine_feinde_kein_ausweichen():
    s = Schussfeld(1)
    _runde(s)
    assert not s.unter_feuer(1, _e(100, 100))


def test_schuetze_in_reichweite_loest_aus_und_ausserhalb_nicht():
    for abstand, erwartet in ((SCHUSSWEITE, True), (SCHUSSWEITE + 1, False)):
        s = Schussfeld(1)
        _runde(s, {9: _e(100 + abstand, 100, typ=22, besitzer=2)})
        assert s.unter_feuer(1, _e(100, 100)) is erwartet, abstand


def test_nahkaempfer_und_eigene_schuetzen_loesen_nicht_aus():
    s = Schussfeld(1)
    _runde(
        s,
        {
            8: _e(105, 100, typ=26, besitzer=2),
            9: _e(105, 100, typ=22, besitzer=1),
            7: _e(105, 100, typ=22, besitzer=0),
        },
    )
    assert not s.unter_feuer(1, _e(100, 100))


def test_tote_schuetzen_loesen_nicht_aus():
    s = Schussfeld(1)
    _runde(s, {9: _e(105, 100, typ=22, besitzer=2, leben=0)})
    assert not s.unter_feuer(1, _e(100, 100))


def test_feindlicher_turm_loest_aus_eigener_nicht():
    s = Schussfeld(1)
    _runde(s, G={5: {"typ": 75, "x": 110, "y": 100, "besitzer": 2}})
    assert s.unter_feuer(1, _e(100, 100))
    s = Schussfeld(1)
    _runde(s, G={5: {"typ": 75, "x": 110, "y": 100, "besitzer": 1}})
    assert not s.unter_feuer(1, _e(100, 100))


def test_wer_leben_verliert_weicht_aus_auch_ohne_sichtbaren_schuetzen():
    s = Schussfeld(1)
    _runde(s)
    assert not s.unter_feuer(1, _e(100, 100, leben=1000))
    _runde(s)
    assert s.unter_feuer(1, _e(100, 100, leben=900))


def test_nachlauf_haelt_das_ausweichen_noch_die_naechsten_runden():
    s = Schussfeld(1)
    _runde(s, {9: _e(105, 100, typ=22, besitzer=2)})
    assert s.unter_feuer(1, _e(100, 100))
    for _ in range(NACHLAUF):
        _runde(s)
        assert s.unter_feuer(1, _e(100, 100))
    _runde(s)
    assert not s.unter_feuer(1, _e(100, 100))


def _stellen():
    zeilen = LENKER.splitlines()
    return [
        (i, z)
        for i, z in enumerate(zeilen)
        if re.search(r'"werbe":|\bBA\w*\.werbe\(|RA\.werbung\(', z)
        and not z.lstrip().startswith("#")
    ]


def test_jede_rekrutierstelle_steht_hinter_dem_tor():
    """Eine neue Stelle ohne Tor wuerde bestellung=raid still aushebeln: Darum sind Stellen und Tore gezaehlt."""
    zeilen = LENKER.splitlines()
    stellen = _stellen()
    assert len(stellen) == 10, [
        i + 1 for i, _ in stellen
    ]  # RA.werbung und BA_r.werbe sind dieselbe Stelle
    assert LENKER.count("BESTELLUNG.darf(") == 9
    for i, z in stellen:
        davor = "\n".join(zeilen[max(0, i - 50) : i + 1])
        assert "BESTELLUNG.darf(" in davor, (i + 1, z.strip())


def test_arten_der_tore():
    gezaehlt = re.findall(r'BESTELLUNG\.darf\("(\w+)"\)', LENKER)
    assert gezaehlt.count("raid") == 3
    assert gezaehlt.count("angriff") == 5
    assert gezaehlt.count("verteidigung") == 1
