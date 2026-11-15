"""Je Befehl an Einheiten eine Zeile mit ihren Nummern (game/ucp/befehl.einheiten_zeilen). Daniel 14.11.2026 00:12 "Ja, Nummern" -
Partie 12: das Protokoll des Spielmoduls nannte nur "ANGRIFF Tick 2197: 1 Einheiten", nicht welche (S136)."""

import pytest


def test_jeder_befehl_an_einheiten_nennt_ihre_nummern_und_den_takt_der_ausfuehrung():
    try:
        from selfaware.game.ucp import befehl as B
    except RuntimeError as ex:  # ohne Spiel-Instanz laesst sich der Befehlsweg nicht laden
        pytest.skip(str(ex))
    paket = {
        "befehle": [
            {"angriff": {"einheiten": [336, 335], "lauf": [246, 174]}},
            {"halten": {"nr": [309], "x": 147, "y": 235}},
            {"angriff": {"einheiten": [312], "ziel": 355}},
        ]
    }
    antwort = [
        "[villagestudio]: ANGRIFF eingereiht Tick 2196: 2 Einheiten, Schlange 1",
        "[villagestudio]: ANGRIFF Tick 2197: 2 Einheiten, Gruppe 1241, Art 17, Ziel 246 (uid 174) - Auswahl=true Befehl=true",
        "[villagestudio]: HALTEN Tick 2197: 1 Einheiten",
        "[villagestudio]: QUITTUNG 1",
    ]
    assert B.einheiten_zeilen(paket, antwort) == [
        'BEFEHL Tick 2197 angriff {"lauf":[246,174]} an 2 Einheiten: [335, 336]',
        'BEFEHL Tick 2197 halten {"x":147,"y":235} an 1 Einheiten: [309]',
        'BEFEHL Tick ? angriff {"ziel":355} an ? Einheiten: [312]',
    ]  # ohne Ausfuehrungszeile: ehrlich "?"
    assert B.einheiten_zeilen({"pause": True}, antwort) == []


def test_sende_schreibt_die_zeilen_fuer_jeden_befehl():
    import os

    quelle = open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "src",
            "selfaware",
            "game",
            "ucp",
            "befehl.py",
        ),
        encoding="utf-8",
    ).read()
    i = quelle.index("def sende(")
    assert (
        "for z in einheiten_zeilen(befehl, zeilen):"
        in quelle[i : quelle.index("def einheiten_zeilen(")]
    )
