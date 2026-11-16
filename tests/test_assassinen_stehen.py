"""Daniel 16.11.2026 20:52 "fixe davor auch alles untaetige herumstehen ... es muss ja eine begruendung geben warum sie rumstehen lies und
fixe", 20:57 "es hoert sich nach einem falschen gebaeudenummern mapping an?". Gefunden in Probe 9b und 10:
- das Spiel vergibt die Nummer eines zerstoerten Gebaeudes neu (Holzfaellerhuette 75 -> Lagerplatz 75); Assassinen und Wegfuehrung
  erkannten ihr Ziel nur an der Nummer bzw. an Art und Besitzer,
- eine Assassine mit fernem Laufziel, die sich nicht bewegt, galt nie als stehend (568: 564 Takte, "NO PROGRESS"),
- nach dem Loesen waehlte eine Assassine dasselbe Ziel sofort wieder (2 am Steinbruch 15, "ATTACK DID NOT START")."""

import pytest

from selfaware.baukasten import zielvergabe as ZV
from selfaware.micro import wegfuehrung as WF

try:
    import selfaware.micro.tasks.assassinen as AS
except RuntimeError as ex:  # pragma: no cover - ohne Spielordner
    AS = None
    GRUND = str(ex)


def _e(nr, owner, typ, x, y, **k):
    d = {
        "nr": nr,
        "gruppe": 0,
        "besitzer": owner,
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


def _g(typ, uid, leben):
    return {
        33: {
            "besitzer": 2,
            "typ": typ,
            "x": 265,
            "y": 100,
            "leben": leben,
            "uid": uid,
            "erreichbar": 1,
            "vorrat": None,
            "grenze": None,
            "verbund": None,
            "ware": None,
        }
    }


def _l(x=240, **k):
    return {
        1: _e(1, 1, 55, 100, 100, leben=150000),
        5: _e(5, 1, 73, x, 100, leben=50000, **k),
        60: _e(60, 2, 55, 340, 100, leben=150000),
    }


def test_kennung_unterscheidet_neue_gebaeude_unter_alter_nummer():
    assert ZV.kennung({"typ": 3, "besitzer": 2, "uid": 1}) != ZV.kennung(
        {"typ": 3, "besitzer": 2, "uid": 2}
    )


def test_wegfuehrung_merkt_eine_neue_huette_unter_alter_nummer():
    w = WF.Wegfuehrung(1)
    w.fuehre(9, "gebaeude", 33, "nahkampfraid")
    L = {9: _e(9, 1, 24, 200, 100)}
    w.schritt(L, _g(3, 1, 60), lambda *a, **k: None)
    assert w.status(9) != "ziel_weg"
    w.schritt(L, _g(3, 2, 60), lambda *a, **k: None)  # gleiche Art, neue uid: das alte Ziel ist weg
    assert w.status(9) == "ziel_weg"


@pytest.mark.skipif(AS is None, reason="Assassinen-Modul ohne Spielordner nicht ladbar")
def test_assassine_laesst_ein_neues_gebaeude_unter_alter_nummer():
    a = AS.Einzeln(1)
    a.aufnehmen([5])
    a.schritt(_l(), _g(3, 1, 60), sichere_orte=[(100, 100)], tick=1000)
    assert a.ziel.get(5) == 33
    # gleiche Art, neue uid: eine neue Holzfaellerhuette unter Nummer 33 - die alte gilt als zerstoert; nimmt die Assassine die neue,
    # dann mit ihrer Kennung
    # (die Assassine laeuft weiter - sonst loeste die Stillstandswache sie ohnehin)
    a.schritt(_l(x=245), _g(3, 2, 60), sichere_orte=[(100, 100)], tick=1200)
    assert a.ziel.get(5) is None or a.ziel_kennung[33][2] == 2


@pytest.mark.skipif(AS is None, reason="Assassinen-Modul ohne Spielordner nicht ladbar")
def test_assassine_mit_fernem_laufziel_die_nicht_laeuft_wird_geloest_und_nimmt_das_ziel_nicht_gleich_wieder():
    a = AS.Einzeln(1)
    a.aufnehmen([5])
    for tick in (1000, 1100):
        a.schritt(_l(laufx=265, laufy=100), _g(3, 1, 60), sichere_orte=[(100, 100)], tick=tick)
        assert a.ziel.get(5) == 33
    a.schritt(
        _l(laufx=265, laufy=100), _g(3, 1, 60), sichere_orte=[(100, 100)], tick=1000 + a.STEH_TICKS
    )
    assert a.ziel.get(5) is None
    assert a._route_sperre.get((5, 33), 0) > 1000 + a.STEH_TICKS
