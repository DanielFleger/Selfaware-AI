"""Backlog = GitHub-Issues (Daniel 15.11.2026 19:49/19:53). Kein Test spricht mit GitHub: GH wird durch eine Attrappe ersetzt."""

import os

import pytest

from selfaware import workspace
from selfaware.tools.planning import backlog as BL


class Attrappe:
    def __init__(self, issues=None, suche=None):
        self.aufrufe, self.issues, self.suche = [], issues or {}, suche or []

    def __call__(self, methode, pfad, daten=None):
        self.aufrufe.append((methode, pfad, daten))
        if methode == "GET" and pfad.startswith("search/issues"):
            return {"items": self.suche}
        if methode == "GET" and "/issues/" in pfad:
            return self.issues[int(pfad.rsplit("/", 1)[1])]
        if methode == "POST" and pfad.endswith("/issues"):
            return {"number": 500, "title": daten["title"]}
        if methode == "PATCH":
            return {
                "number": int(pfad.rsplit("/", 1)[1]),
                "state": daten["state"],
                "labels": daten["labels"],
            }
        return {}


@pytest.fixture
def gh(monkeypatch):
    a = Attrappe(
        issues={
            7: {
                "number": 7,
                "title": "B-184 Assassinen",
                "labels": [{"name": "Kampf"}, {"name": "zurückgestellt"}],
            }
        },
        suche=[
            {"number": 7, "title": "B-184 Assassinen"},
            {"number": 8, "title": "B-1840 anderes"},
        ],
    )
    monkeypatch.setattr(BL, "GH", a)
    monkeypatch.setattr(BL, "repo", lambda: "eigner/repo")
    return a


def test_neu_verlangt_eine_bekannte_kategorie_und_setzt_beide_etiketten(gh):
    with pytest.raises(SystemExit, match="ategorie"):
        BL.neu("Probe", "Kampf", "Gibt es nicht", "Test")
    with pytest.raises(SystemExit, match="ategorie"):
        BL.neu("Probe", "Allgemein", "Ordnung", "Test")
    assert gh.aufrufe == [], "bei unbekannter Kategorie geht nichts an GitHub"
    BL.neu("Probe", "Kampf", "Lord", "Daniel 15.11.", wo=["src/x.py"])
    methode, pfad, daten = gh.aufrufe[-1]
    assert (methode, pfad) == ("POST", "repos/eigner/repo/issues")
    assert daten["labels"] == ["Kampf", "Kampf: Lord"] and "`src/x.py`" in daten["body"]


def test_gebaut_schliesst_als_erledigt_und_nimmt_den_arbeitsstand_weg(gh):
    i = BL.stand("B-184", "gebaut", notiz="fertig", commit="abc1234")
    kommentar = [d for m, p, d in gh.aufrufe if p.endswith("/comments")][0]["body"]
    assert "abc1234" in kommentar and "gebaut" in kommentar
    assert i["state"] == "closed" and gh.aufrufe[-1][2]["state_reason"] == "completed"
    assert i["labels"] == ["Kampf"], "in Arbeit / zurückgestellt fallen beim Schliessen weg"


def test_in_arbeit_oeffnet_und_tauscht_das_etikett(gh):
    i = BL.stand("#7", "in_arbeit")
    assert i["state"] == "open" and i["labels"] == ["Kampf", "in Arbeit"]
    assert (
        BL.stand("7", "verworfen")["state"] == "closed"
        and gh.aufrufe[-1][2]["state_reason"] == "not_planned"
    )
    with pytest.raises(SystemExit, match="unbekannt"):
        BL.stand("#7", "fertig")


def test_b_nummer_findet_nur_den_exakten_titel(gh):
    assert BL.finde("B-184")["number"] == 7, "B-1840 darf nicht passen"
    gh.suche = []
    with pytest.raises(SystemExit, match="0 passende"):
        BL.finde("B-184")
    with pytest.raises(SystemExit, match="erwartet"):
        BL.finde("184a")


def test_pruefen_meldet_commits_ohne_punkt(monkeypatch):
    monkeypatch.setattr(
        BL,
        "git",
        lambda *a: "aaa1111 #12 Lord laeuft\nbbb2222 B-184 Assassinen\nccc3333 nur so geaendert\n",
    )
    assert BL.pruefen() == ["ccc3333 nur so geaendert"]


def test_repo_kommt_aus_dem_remote(monkeypatch):
    for url in (
        "https://github.com/eigner/repo.git",
        "git@github.com:eigner/repo.git",
        "https://github.com/eigner/repo",
    ):
        monkeypatch.setattr(BL, "git", lambda *a, u=url: u)
        assert BL.repo() == "eigner/repo"
    monkeypatch.setattr(BL, "git", lambda *a: "https://gitlab.com/eigner/repo.git")
    with pytest.raises(SystemExit, match="GitHub"):
        BL.repo()


def test_keine_zweite_liste_im_repo():
    """Daniel 19:49 'nicht doppelt': die Liste lebt nur auf GitHub."""
    backlog_ordner = os.path.join(workspace.ROOT, "docs", "backlog")
    assert not os.path.exists(os.path.join(backlog_ordner, "backlog.json"))
    assert not os.path.exists(os.path.join(backlog_ordner, "Backlog.html"))
    assert os.path.isfile(BL.KATEGORIEN)
