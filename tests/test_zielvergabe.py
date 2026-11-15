"""Zielvergabe fuer alle Einheiten (Daniel 15.11.2026 22:29: "zielvergabe assassinen und nicht nur assassinen sondern aller einheiten
so koennen auch assassinen und sklaven auf einen steinbruch oder bogenschuetzen und sklaven auf einen holzfaeller etc.").

Gemessen vorher (data/research/erstes_spiel_log2_sp2.txt, Partie ab 22:22:46): bis zu 77 Assassinen ohne Ziel ("alle gefaehrlich"),
je Gebaeude durfte nur einer hin. Jede Szene hier: ein einziges Ziel, zwei Einheiten derselben Art - beide muessen hin."""

import pytest

from selfaware.baukasten import zielvergabe as ZV
from selfaware.micro.tasks import raids as RA


def test_erst_frei_dann_dazu():
    wahl = lambda liste: max(liste)  # noqa: E731
    assert ZV.waehle([1, 2, 3], lambda k: k != 3, wahl) == (2, False), "ein freies Ziel geht vor"
    assert ZV.waehle([1, 2, 3], lambda k: False, wahl) == (3, True), "keins frei: dazu statt warten"
    assert ZV.waehle([], lambda k: True, wahl) == (None, False)
    nur_kleine = lambda liste: max((k for k in liste if k < 2), default=None)  # noqa: E731
    assert ZV.waehle([1, 2, 3], lambda k: k > 1, nur_kleine) == (1, True), (
        "freie, die das Modul nicht nimmt, sperren das Dazustellen nicht"
    )


class _Kern:
    def __init__(self):
        self.gesendet = []

    def ausweichen(self, einheiten, ziel, trupp=1):
        return True

    def senden(self, liste):
        self.gesendet += [b["angriff"] for b in liste]
        return []

    def freigeben(self, einheiten):
        pass

    def aufraeumen(self, lebend):
        pass


def test_zwei_sklaven_zuenden_dasselbe_gebaeude_an():
    k = _Kern()
    t = RA.Brandtrupp(1, lambda nr: 0, kern=k)
    sklave = lambda x, y: {"typ": RA.SKLAVE, "x": x, "y": y, "besitzer": 1, "leben": 6000}  # noqa: E731
    L = {1: sklave(100, 100), 2: sklave(100, 104)}
    aus = t.schritt(L, {100: {"typ": 3, "x": 150, "y": 100, "besitzer": 2}}, lambda *a, **kw: None)
    assert t.ziel == {1: 100, 2: 100}, aus
    assert any("Sklave 2 -> Gebaeude 100" in z and "dazu" in z for z in aus), aus
    assert {"einheiten": [2], "gebaeude": 100} in k.gesendet


def test_zwei_assassinen_greifen_dasselbe_gebaeude_an():
    try:
        import selfaware.micro.tasks.assassinen as AS
    except RuntimeError as ex:  # ohne Spielinstanz laesst sich das Modul nicht laden
        pytest.skip(str(ex))

    def e(nr, besitzer, typ, x, y, **k):
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

    # Szene wie test_unit_log (Partie 12.11. 20:45): ein Holzfaeller-Gebaeude, die Armbrueste weit genug weg zum Angreifen
    G = {
        33: {
            "besitzer": 2,
            "typ": 3,
            "x": 265,
            "y": 100,
            "leben": 60,
            "uid": 1,
            "erreichbar": 1,
            "vorrat": None,
            "grenze": None,
            "verbund": None,
            "ware": None,
        }
    }
    L = {
        1: e(1, 1, 55, 100, 100, leben=150000),
        5: e(5, 1, 73, 240, 100, leben=50000),
        6: e(6, 1, 73, 240, 104, leben=50000),
        60: e(60, 2, 55, 340, 100, leben=150000),
        61: e(61, 2, 23, 300, 100),
        62: e(62, 2, 23, 300, 104),
    }
    a = AS.Einzeln(1)
    a.aufnehmen([5, 6])
    erg = a.schritt(L, G, sichere_orte=[(100, 100)], tick=1000)
    ev = erg[0] if isinstance(erg, tuple) else erg
    assert a.ziel == {5: 33, 6: 33}, [z for z in ev if "ZIEL" in z or "ohne Ziel" in z]
    assert any(z.startswith("ZIELWAHL 6 -> 33") and "dazu (schon 1 dort)" in z for z in ev)


def test_359_folgeziel_je_angegriffenem_gebaeude():
    """#359 (Daniel 23:07): wer ein Gebaeude angreift, hat schon das naechste - vom Ort dieses Gebaeudes aus gewaehlt."""
    try:
        import selfaware.micro.tasks.assassinen as AS
    except RuntimeError as ex:
        pytest.skip(str(ex))

    def e(nr, besitzer, typ, x, y, **k):
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

    def geb(nr, x):
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
        }

    G = {33: geb(33, 265), 34: geb(34, 275)}
    L = {
        1: e(1, 1, 55, 100, 100, leben=150000),
        5: e(5, 1, 73, 240, 100, leben=50000),
        60: e(60, 2, 55, 340, 100, leben=150000),
    }
    a = AS.Einzeln(1)
    a.aufnehmen([5])
    a.schritt(L, G, sichere_orte=[(100, 100)], tick=1000)
    assert a.ziel.get(5) in (33, 34)
    jetzt = a.ziel[5]
    assert a.folgeziele == {5: (jetzt, 34 if jetzt == 33 else 33)}
