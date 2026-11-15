"""Schuetzen angreifen bei erwartetem Sieg (Daniel 15.11.2026 23:28: "wenn sie die ueberhand haben, heisst beim erwarteten beschuss von anderen
die auf dem weg noch dazukommen und auf sie schiessen aktiv (nicht nur geschaetzt) dann sollen sie auch die bogenschuetzen absnacken ...
natuerlich nur bei erwartetem gewinn"). Probe 23:05: 11 Stapel-Versuche, keiner - alle Schuetzen standen naeher als STAPEL_BURG an ihrem Lord."""

import pytest


def _modul():
    try:
        import selfaware.micro.tasks.assassinen as AS
    except RuntimeError as ex:
        pytest.skip(str(ex))
    return AS


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


def _szene(schuetzen_am_weg=0):
    AS = _modul()
    L = {
        1: _e(1, 1, 55, 100, 100, leben=150000),
        60: _e(60, 2, 55, 275, 100, leben=150000),
        61: _e(61, 2, 22, 240, 100),  # 35 Felder vom Lord: vorher gesperrt (STAPEL_BURG 45)
    }
    for i in range(14):
        L[200 + i] = _e(200 + i, 1, 73, 200, 93 + i, leben=12500)
    for i in range(
        schuetzen_am_weg
    ):  # treffen den Weg ab (200, 100), aber nicht das Ziel bei (240, 100)
        L[400 + i] = _e(400 + i, 2, 22, 200 + (i % 6), 132 + i // 6)
    a = AS.Einzeln(1)
    a.aufnehmen(list(range(200, 214)))
    erg = a.schritt(L, {}, sichere_orte=[(100, 100)], tick=1000)
    return a, (erg[0] if isinstance(erg, tuple) else erg)


def test_stapel_greift_schuetzen_nahe_am_lord_an_wenn_er_gewinnt():
    a, ev = _szene()
    assert a.stapel["ziel"] == 61, [z for z in ev if "STAPEL" in z]
    assert any(z.startswith("STAPEL: 14 Assassinen gebuendelt auf Fernkaempfer 61") for z in ev)


def test_beschuss_auf_dem_weg_zaehlt_mit():
    a, ev = _szene(schuetzen_am_weg=30)
    assert a.stapel["ziel"] != 61, [z for z in ev if "STAPEL" in z]
