"""B-192 (Daniel 15.11.2026 14:01/14:18/14:24): ein Backlog, jede Nummer genau einmal, jeder Punkt in einer Kategorie aus
docs/backlog/kategorien.json, Erledigtes zaehlt nicht mit."""

import json
import re

import pytest

from selfaware.tools.planning import backlog as BL


def test_jede_nummer_genau_einmal_und_jede_kategorie_im_baum():
    punkte = BL.lade()["punkte"]
    nummern = [p["nr"] for p in punkte]
    assert len(nummern) == len(set(nummern))
    baum, _ = BL.baum()
    erlaubt = {(k, u) for k, us in baum for u in us}
    assert all((p.get("kategorie"), p.get("unterkategorie")) in erlaubt for p in punkte)
    # die alten Punkte tragen ihre alte Nummer, die neue liegt ab B-290 - keine Nummer heisst zwei Dinge
    alte = [p for p in punkte if p.get("alte_nr")]
    assert len(alte) == 150 and min(int(p["nr"][2:]) for p in alte) >= 290


def test_neu_verlangt_eine_bekannte_kategorie():
    b = {"punkte": [{"nr": "B-439"}]}
    with pytest.raises(SystemExit, match="ategorie"):
        BL.neu(b, "Probe", None, "Test", kategorie="Kampf", unter="Gibt es nicht")
    with pytest.raises(SystemExit, match="ategorie"):
        BL.neu(b, "Probe", None, "Test", kategorie="Allgemein", unter="Ordnung")
    p = BL.neu(b, "Probe", None, "Test", kategorie="Struktur", unter="Ordnung")
    assert p["nr"] == "B-440" and p["kategorie"] == "Struktur"


def test_einordnung_laeuft_nur_einmal():
    with pytest.raises(SystemExit, match="schon uebernommen"):
        BL.einordnen(BL.lade(), str(BL.WURZEL) + "/docs/backlog/einordnung_20261115.json")


def test_erledigtes_zaehlt_nicht_mit(monkeypatch, tmp_path):
    ziel = tmp_path / "Backlog.html"
    monkeypatch.setattr(BL, "ANSICHT", str(ziel))
    monkeypatch.setattr(BL, "git_log", lambda repo, seit=None: [])
    b = {"punkte": []}
    for titel, stand in (
        ("offen eins", "offen"),
        ("fertig", "gebaut"),
        ("verworfen", "verworfen"),
        ("offen zwei", "offen"),
    ):
        BL.neu(b, titel, None, "Test", status=stand, kategorie="Wirtschaft", unter="Nahrung")
    BL.bauen(b)
    seite = ziel.read_text(encoding="utf-8")
    assert re.search(r"Wirtschaft <span class=\"leise\">– 2 offen", seite)
    assert "Erledigt (2, zählt nicht mit)" in seite
    assert "2 offene Punkte" in seite
    assert (
        json.loads(json.dumps(b))["punkte"][1]["status"] == "gebaut"
    )  # nichts geloescht, nur nicht gezaehlt
