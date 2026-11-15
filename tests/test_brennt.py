"""Daniel 15.11.2026 23:31: "manchmal gehen sklaven und einheiten auf ein gebaeude, es brennt und sie verbrennen auch, das ist aber erwartbar,
bitte sofort ein neues gebaeude auswaehlen wenn ein gebaeude erwartbar stirbt". Brennen = fireDuration > 0 (B-150 L177: faellt erst auf 0,
wenn das Gebaeude weg ist) - Spalte 13 der Gebaeudeliste aus logik.lua."""

import pytest

from selfaware.micro.tasks import waechter as W


def test_gebaeudeliste_liest_das_feuer(monkeypatch, tmp_path):
    datei = tmp_path / "gebaeude.txt"
    datei.write_text(
        "nr besitzer typ x y leben uid erreichbar vorrat grenze verbund ware feuer\n"
        "33 2 3 265 100 60 1 1 0 0 0 0 57\n34 2 3 275 100 60 2 1 0 0 0 0 0\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(W, "GEBAEUDEDATEI", str(datei))
    G = W.lies_gebaeude()
    assert G[33]["feuer"] == 57 and W.brennt(G[33]) and not W.brennt(G[34])


def _e(nr, besitzer, typ, x, y, **k):
    d = {
        "nr": nr,
        "gruppe": 0,
        "besitzer": besitzer,
        "typ": typ,
        "x": x,
        "y": y,
        "leben": 10000,
        "zustand": 1,
        "zielart": 0,
        "zieleinheit": 0,
        "laufx": x,
        "laufy": y,
        "ladung": 0,
        "arbeitsplatz": 0,
        "erreichbar": 1,
        "nahziel": -1,
        "nahangreifer": -1,
    }
    d.update(k)
    return d


def _geb(nr, x, feuer=0):
    return {
        "besitzer": 2,
        "typ": 3,
        "x": x,
        "y": 100,
        "leben": 60,
        "uid": nr,
        "erreichbar": 1,
        "vorrat": None,
        "grenze": None,
        "verbund": None,
        "ware": None,
        "feuer": feuer,
    }


def test_assassine_nimmt_kein_brennendes_und_wechselt_sofort():
    try:
        import selfaware.micro.tasks.assassinen as AS
    except RuntimeError as ex:
        pytest.skip(str(ex))
    L = {
        1: _e(1, 1, 55, 100, 100, leben=150000),
        5: _e(5, 1, 73, 240, 100, leben=50000),
        60: _e(60, 2, 55, 340, 100, leben=150000),
    }
    a = AS.Einzeln(1)
    a.aufnehmen([5])
    a.schritt(
        L, {33: _geb(33, 265, feuer=40), 34: _geb(34, 275)}, sichere_orte=[(100, 100)], tick=1000
    )
    assert a.ziel.get(5) == 34, "das brennende 33 ist kein Ziel"
    erg = a.schritt(
        L, {33: _geb(33, 265), 34: _geb(34, 275, feuer=5)}, sichere_orte=[(100, 100)], tick=1200
    )
    ev = erg[0] if isinstance(erg, tuple) else erg
    assert any(z.startswith("BRENNT 5: Gebaeude 34") for z in ev) and a.ziel.get(5) == 33, (
        "34 brennt jetzt: sofort 33"
    )


def test_nahkampf_raid_zielt_nicht_auf_brennende():
    from selfaware.baukasten import wirkung as WK

    z = {x.schluessel for x in WK.ziele({}, {33: _geb(33, 265, feuer=9), 34: _geb(34, 275)}, 1)}
    assert ("g", 34) in z and ("g", 33) not in z
