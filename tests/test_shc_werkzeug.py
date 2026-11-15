"""Spielmechanik-Werkzeug (Daniel 15.11.2026 21:11): die reinen Rechnungen der Lobby, ohne Spiel gepruefte Werte vom 15.11.
(Partie 36 auf Kykladen, VillageStudio/doku/Partie-starten.md Schritt 2a/2b/3)."""

import pytest

from selfaware.game.ucp import shc

# Schilder auf Kykladen, gelesen 15.11.2026 20:44 (peek 0x1FE9A5C): 1 oben links, 2 oben rechts, 3 unten links, 4 unten Mitte
KYKLADEN = {1: (53, 53), 2: (152, 68), 3: (53, 146), 4: (96, 145)}


def test_karte_per_namen_mit_rollstand_und_zeile():
    namen = ["Close Encounters"] * 42 + ["Cyclades", "Flood plains of Jordan"]
    assert shc.karten_eintrag(namen, "cyclades") == (
        42,
        35,
        7,
    )  # gemessen 20:44: Eintrag 42 -> Rollstand 35, Zeile 7
    assert shc.karten_eintrag(["A", "Cyclades"], "Cyclades") == (1, 0, 1)
    with pytest.raises(shc.Fehler, match="englisch"):
        shc.karten_eintrag(namen, "Kykladen")
    with pytest.raises(shc.Fehler, match="mehrdeutig"):
        shc.karten_eintrag(["Green Haven", "Green Trench"], "green")


def test_plaetze_aus_daniels_woertern():
    # Daniel 20:27: "samurais unten, kriegsfuerst oben rechts" - Spieler 1 Kriegsfuerst, 2 und 3 SamurAI
    assert shc.schilder_nach_woertern(KYKLADEN, ["oben_rechts", "unten", "unten"]) == [2, 3, 4]
    assert shc.schilder_nach_woertern(KYKLADEN, ["s4", "oben links"]) == [4, 1]
    with pytest.raises(shc.Fehler):
        shc.schilder_nach_woertern(KYKLADEN, ["hinten"])
    with pytest.raises(shc.Fehler):
        shc.schilder_nach_woertern(KYKLADEN, ["s2", "s2"])


def test_tauschzuege_bringen_jede_zeile_auf_ihr_schild():
    # Belegung vor dem Tausch, gelesen 20:45: Schild 1 Zeile 2, Schild 2 Zeile 1, Schild 4 Zeile 0
    zuege, danach = shc.tauschzuege({1: 2, 2: 1, 4: 0}, {0: 2, 1: 3, 2: 4})
    assert danach == {2: 0, 3: 1, 4: 2}
    assert zuege[0] == (4, 2), "Zug auf ein besetztes Schild tauscht (gemessen 20:46)"
    assert shc.tauschzuege({2: 0}, {0: 2}) == ([], {2: 0}), "steht schon richtig: kein Zug"
    with pytest.raises(shc.Fehler):
        shc.tauschzuege({1: 0}, {1: 2})


def test_trefferpunkt_wie_gemessen():
    assert shc.trefferpunkt((152, 68), (400, 150)) == (
        1135,
        237,
    )  # 20:46: Kriegsfuerst auf Schild 2 abgelegt


def test_runder_tisch_klicks():
    assert shc.team_klicks([0, 1, 1]) == [2, 3]  # gemessen 20:45: Team-Bytes danach 00 01 01
    assert shc.team_klicks([1, 1, 2, 2]) == [1, 2, 3, 4]
    assert shc.team_klicks([1, 1, 1]) == [1, 2, 3, 1]  # der Neue zuerst (gemessen 21:36)
    assert shc.team_klicks([1, 2, 2, 2]) == [2, 3, 4, 2]
    assert shc.team_klicks([0, 0]) == []


def test_aufruf_ohne_befehl_zeigt_hilfe_und_scheitert(capsys):
    assert shc.main([]) == 1
    assert "Spielmechanik" in capsys.readouterr().out


def test_kein_skript_gefecht_im_werkzeug():
    """Daniel 15.11.: nie per Skript starten - das Werkzeug hat keinen eigenesGefecht-Weg, starten geht ueber den Lobby-Knopf."""
    quelle = open(shc.__file__, encoding="utf-8").read()
    assert "eigenesGefecht" not in quelle.replace("Skript-Gefecht", "")
    assert "gefecht" not in shc.BEFEHLE


def test_samurai_plaetze_aus_der_ki_liste():
    assert shc.samurai_spieler("8,16,16") == [
        2,
        3,
    ]  # Partie 36: Kriegsfuerst Spieler 1, SamurAI 2 und 3
    assert shc.samurai_spieler("16,7") == [1]
    assert shc.samurai_spieler("7,8") == []


def test_partie_startet_nie_ohne_freigabe(monkeypatch):
    """Ohne offene Freigabe bleibt die Lobby stehen - starten wird nicht gerufen (Daniel 15.11.: nie ohne seine Aufstellung)."""
    gerufen = []
    monkeypatch.setattr(shc, "aufstellen", lambda *a, **k: "Lobby steht")
    monkeypatch.setattr(shc, "freigabe_offen", lambda: None)
    monkeypatch.setattr(shc, "starten", lambda: gerufen.append(1))
    assert "KEINE offene Freigabe" in shc.partie("Cyclades", "8,16,16") and not gerufen


def test_lenker_aufstellung_uebernimmt_den_platz():
    from selfaware.baukasten import aufstellung

    arg, daten = aufstellung.anwenden({"aufstellung": "lobby_wie_partie34"})
    assert arg["uebernehmen"] == "ja" and daten["name"] == "lobby_wie_partie34"


def test_stopp_haelt_zuerst_das_spiel_an_dann_die_lenker(monkeypatch):
    """Daniel 15.11.2026 22:26: "Dein stop kam ... locker 30 sekunden ... es sollte instant gehen" - erst Pause (ein Befehl,
    gemessen 0,04 s), dann die Lenker beenden, dann noch einmal Pause (falls ein Lenker sie in der Zwischenzeit aufhob)."""
    folge = []
    monkeypatch.setattr(
        shc, "senden", lambda liste, *a, **k: folge.append(("pause", liste[0].get("pause")))
    )
    monkeypatch.setattr(shc, "lenker_stoppen", lambda: folge.append(("lenker",)) or 2)
    monkeypatch.setattr(shc, "zustand", lambda: {"text": "Partie laeuft (angehalten)"})
    text = shc.stopp()
    assert folge == [("pause", True), ("lenker",), ("pause", True)] and "2 Lenker beendet" in text
    assert shc.BEFEHLE["stopp"] is shc.stopp
