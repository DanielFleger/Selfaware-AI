"""S169 (Daniel 15.11.2026 11:44): kein Gefecht per Befehl ohne Daniels abgelegte Aufstellung - ohne Spiel."""
import json

from selfaware.execution import startsperre as SS

GEFECHT = {"befehle": [{"id": 1, "eigenesGefecht": True, "karte": "Liga_Paradise Plains"}]}


def test_ohne_freigabe_kein_gefecht(tmp_path):
    paket, meld = SS.filtern(GEFECHT, pfad=str(tmp_path / "fehlt.json"))
    assert paket is None and "STARTSPERRE" in meld[0] and "Partie-starten.md" in meld[0]


def test_andere_befehle_gehen_immer_durch(tmp_path):
    p = {"befehle": [{"id": 2, "angriff": {"einheiten": [1], "ziel": 5}}]}
    assert SS.filtern(p, pfad=str(tmp_path / "fehlt.json")) == (p, [])


def test_startknopf_der_lobby_braucht_die_freigabe_fuer_den_menueweg(tmp_path):
    start = {"befehle": [{"id": 3, "knopf": "LobbyMenu_LobbyscreenStartButtonClick", "nr": 4}]}
    andere = {"befehle": [{"id": 4, "knopf": "LobbyMenu_LobbyscreenStartButtonClick", "nr": 2}]}     # Lobby verlassen
    assert SS.filtern(start, pfad=str(tmp_path / "fehlt.json"))[0] is None
    assert SS.filtern(andere, pfad=str(tmp_path / "fehlt.json"))[0] is andere
    f = tmp_path / "f.json"
    f.write_text(json.dumps({"zeit": "15.11.2026 12:30", "daniel": "Battle Brothers Strife", "weg": "menue"}), encoding="utf-8")
    assert SS.filtern(start, pfad=str(f))[0] is start and SS.filtern(start, pfad=str(f))[0] is None


def test_freigabe_fuer_den_menueweg_sperrt_den_befehlsweg(tmp_path):
    f = tmp_path / "f.json"
    f.write_text(json.dumps({"zeit": "15.11.2026 11:50", "daniel": "Paradise Plains, ich oben", "weg": "menue"}), encoding="utf-8")
    paket, meld = SS.filtern(GEFECHT, pfad=str(f))
    assert paket is None and "weg='menue'" in meld[0]


def test_freigabe_fuer_den_befehlsweg_gilt_genau_einmal(tmp_path):
    f = tmp_path / "f.json"
    f.write_text(json.dumps({"zeit": "15.11.2026 11:50", "daniel": "per Befehl ist ok", "weg": "befehl"}), encoding="utf-8")
    assert SS.filtern(GEFECHT, pfad=str(f))[0] is GEFECHT
    assert json.loads(f.read_text(encoding="utf-8"))["verbraucht"] is True
    assert SS.filtern(GEFECHT, pfad=str(f))[0] is None


def test_der_echte_kanal_schreibt_ohne_freigabe_nichts(tmp_path, monkeypatch):
    # derselbe Weg wie jeder Start (befehl.sende): ohne Freigabe kommt keine Befehlsdatei beim Spiel an
    from selfaware.game.ucp import befehl as B
    monkeypatch.setattr(B, "_kanal_frei", lambda: None)
    monkeypatch.setattr(B, "BEFEHL", str(tmp_path / "befehl.json"))
    monkeypatch.setattr(SS, "FREIGABE", str(tmp_path / "fehlt.json"))
    antwort = B.sende({"eigenesGefecht": True, "karte": "Liga_Paradise Plains"}, 0.1)
    assert any("STARTSPERRE" in z for z in antwort) and not (tmp_path / "befehl.json").exists()
