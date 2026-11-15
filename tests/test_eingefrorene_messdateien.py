"""B-196 (15.11.2026): Wache und Ablaufanalyse schrieben in Messdateien, die beim Umzug eingefroren wurden (docs/relocations.json,
content_changed = false). Beide schreiben jetzt in eigene Dateien; dieser Test haelt fest, dass sie die alten nicht mehr anfassen."""
import json
import pathlib

from selfaware import workspace
from selfaware.runtime.live import samurai_wache as W
from selfaware.telemetry import ablaufanalyse as A


def _eingefroren():
    umzug = json.loads((pathlib.Path(workspace.ROOT) / "docs" / "relocations.json").read_text(encoding="utf-8"))
    return {e["new"] for e in umzug["files"] if not e["content_changed"]}


def test_neue_dateien_sind_nicht_eingefroren_die_alten_schon():
    frei = _eingefroren()
    assert "data/research/samurai_wache.log" in frei and "data/research/wissen_ablauf.jsonl" in frei
    assert "data/research/" + W.PROTOKOLL not in frei
    assert "data/research/" + A.WISSEN_DATEI not in frei


def test_wache_schreibt_nicht_in_die_alte_datei(monkeypatch, tmp_path):
    monkeypatch.setattr(W, "D", str(tmp_path))
    W.schreib("Probe B-196")
    assert not (tmp_path / "samurai_wache.log").exists()
    assert "Probe B-196" in (tmp_path / W.PROTOKOLL).read_text(encoding="utf-8")


def test_ablaufanalyse_schreibt_nicht_in_die_alte_datei(monkeypatch, tmp_path):
    monkeypatch.setattr(A._workspace, "DATA", str(tmp_path))
    erg = {"quelle": "probe", "von": 0, "bis": 100, "aufloesung_ticks": 1, "zustaende": {}, "gehen": {}, "ablieferungen": {},
           "vorrat": {"stein": {"zugang_je_1000": 5, "zugaenge": 2}}, "waren_je_1000": {}, "besetzung_mittel": {}}
    pfad = A.wissen_anhaengen(erg)
    assert pathlib.Path(pfad).name == A.WISSEN_DATEI
    assert not (tmp_path / "wissen_ablauf.jsonl").exists()
    assert json.loads((tmp_path / A.WISSEN_DATEI).read_text(encoding="utf-8").splitlines()[0])["groesse"] == "Zugang stein"
