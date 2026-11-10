"""FAIRNESS F12 (Daniel 11.11.2026 00:10: "das einzige was verborgen ist sind holfallen und wo das pech ist"): gegnerische
Fallgruben sind im Spiel verborgen - keine Pruefung darf sie lesen. Tuerme sind sichtbar und bleiben Gefahr."""

from selfaware.micro.tasks import raids as RA


def test_gegnerische_fallgrube_macht_kein_ziel_gefaehrlich():
    G = {1: {"besitzer": 2, "typ": RA.GRUBE, "x": 101, "y": 100}}
    assert RA.gefaehrlich((100, 100), {}, G, 1) is None


def test_gegnerischer_turm_bleibt_gefaehrlich():
    G = {1: {"besitzer": 2, "typ": 77, "x": 110, "y": 100}}  # Turm in 10 Feldern
    assert RA.gefaehrlich((100, 100), {}, G, 1) is not None
