"""#359 (Daniel 16.11.2026 00:09: Assassinen "laufen eine strecke stoppen dann wieder ohne beim ziel zu sein ohne grund"). Probe 4: 454
Runden-Absichten raid_building_route - je Wegpunkt ein Laufbefehl pro Lenker-Runde. Jetzt geht der ganze Weg als Kern-Kette hinaus."""

import pytest


def test_lenker_haengt_den_weg_als_kette_an():
    from selfaware.runtime.live import erstes_spiel as ES

    class Kern:
        kann_ketten, kann_folge, folge_gesendet = True, False, {}

        def __init__(self):
            self.ketten = []

        def aufraeumen(self, lebend):
            pass

        def senden(self, liste):
            return []

        def kette(self, nr, punkte, danach=None):
            self.ketten.append((nr, punkte, danach))
            return True

    k = Kern()
    alt = ES._kernweg
    ES._kernweg = k
    try:
        ES.kernweg_senden(
            [{"angriff": {"einheiten": [5, 6], "lauf": [110, 100]}}],
            [5, 6],
            [],
            routen={
                5: {"punkte": [(110, 100), (120, 100), (130, 100)], "gebaeude": 77},
                6: {"punkte": [(90, 100)], "gebaeude": 78},
            },
        )
    finally:
        ES._kernweg = alt
    assert k.ketten == [(5, [(120, 100), (130, 100)], ("gebaeude", 77))], (
        "6 laeuft nicht zu seinem ersten Wegpunkt: keine Kette"
    )


def test_assassine_uebernimmt_den_fortschritt_der_kette():
    try:
        import selfaware.micro.tasks.assassinen as AS
    except RuntimeError as ex:
        pytest.skip(str(ex))
    a = AS.Einzeln(1)
    a.mitglieder = {5}
    a.ziel[5] = 77
    a.route[5] = {"punkte": [(110, 100), (120, 100), (130, 100)], "gebaeude": 77, "befohlen": 0}
    L = {5: {"x": 100, "y": 100, "laufx": 120, "laufy": 100, "besitzer": 1, "typ": 73}}
    lauf = a._route_pflegen(L, {77: {"x": 150, "y": 100}}, [], [])
    assert a.route[5]["punkte"][0] == (120, 100), "der Kern ist schon beim zweiten Wegpunkt"
    assert not lauf, "kein neuer Laufbefehl zum alten Wegpunkt"
