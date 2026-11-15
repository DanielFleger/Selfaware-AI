"""B-192 Schritt 6: grosse Aufzeichnungen in den Datenordner, im Repo nur das Verzeichnis (selfaware.tools.checks.datenordner)."""

import json
import os
import re
import subprocess

import pytest

from selfaware import workspace
from selfaware.tools.checks import datenordner as d

GIT = [
    "git",
    "-c",
    "user.name=probe",
    "-c",
    "user.email=probe@example.invalid",
    "-c",
    "core.autocrlf=false",
]


def _schreib(pfad, n):
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    with open(pfad, "wb") as f:
        f.write(b"x" * n)


@pytest.fixture
def repo(tmp_path):
    """Kleines Repo mit Grenze 100 Bytes: eine kleine und eine grosse neue Datei, ein Lauf-Ordner, ein gewachsenes Protokoll."""
    w, daten = tmp_path / "repo", tmp_path / "daten"
    w.mkdir()
    subprocess.run([*GIT, "init", "-q", str(w)], check=True)
    os.makedirs(w / "data" / "research")
    verzeichnis = {
        "regeln": {"grenze_bytes": 100, "ganze_ordner": ["data/research/laeufe"]},
        "dateien": [],
    }
    (w / "data" / "research" / "datenordner.json").write_text(
        json.dumps(verzeichnis), encoding="utf-8"
    )
    _schreib(w / "data" / "research" / "lage_20261115_130357_i2.jsonl.gz", 60)
    subprocess.run([*GIT, "-C", str(w), "add", "-A"], check=True)
    subprocess.run([*GIT, "-C", str(w), "commit", "-q", "-m", "start"], check=True)
    _schreib(w / "data" / "research" / "klein.txt", 50)
    _schreib(w / "data" / "research" / "kern_20261115_003941.log", 200)
    _schreib(w / "data" / "research" / "laeufe" / "lauf_k_20261102_234952.proben" / "p.json", 10)
    _schreib(
        w / "data" / "research" / "lage_20261115_130357_i2.jsonl.gz", 300
    )  # nach dem Commit gewachsen (B-194)
    return str(w), str(daten)


def test_ohne_tun_wird_nur_angezeigt(repo):
    w, daten = repo
    vorher = sorted(os.listdir(os.path.join(w, "data", "research")))
    gezeigt = d.kandidaten(w, d.lies_verzeichnis(w)["regeln"])
    assert d.auslagern(w, daten, tun=False) == []
    assert sorted(os.listdir(os.path.join(w, "data", "research"))) == vorher and not os.path.exists(
        daten
    )
    assert sorted(p for _, p in gezeigt) == [
        "data/research/kern_20261115_003941.log",
        "data/research/laeufe/lauf_k_20261102_234952.proben/p.json",
        "data/research/lage_20261115_130357_i2.jsonl.gz",
    ], "klein.txt (50 Bytes, ausserhalb der ganzen Ordner) bleibt im Repo"


def test_auslagern_verschiebt_traegt_ein_und_prueft_gruen(repo):
    w, daten = repo
    assert len(d.pruefen(w, daten)) == 3, "vorher rot: drei Dateien gehoeren in den Datenordner"
    e = {x["pfad"]: x for x in d.auslagern(w, daten, tun=True, heute="2026-11-15")}
    assert set(e) == {
        "data/research/kern_20261115_003941.log",
        "data/research/lage_20261115_130357_i2.jsonl.gz",
        "data/research/laeufe/lauf_k_20261102_234952.proben/p.json",
    }
    assert not os.path.exists(os.path.join(w, "data", "research", "kern_20261115_003941.log"))
    assert (
        os.path.getsize(os.path.join(daten, "data", "research", "kern_20261115_003941.log")) == 200
    )
    # das gewachsene Protokoll: lange Fassung im Datenordner, im Repo wieder die committete
    assert (
        os.path.getsize(os.path.join(daten, "data", "research", "lage_20261115_130357_i2.jsonl.gz"))
        == 300
    )
    assert (
        os.path.getsize(os.path.join(w, "data", "research", "lage_20261115_130357_i2.jsonl.gz"))
        == 60
    )
    assert e["data/research/lage_20261115_130357_i2.jsonl.gz"]["hinweis"]
    assert e["data/research/kern_20261115_003941.log"]["stempel"] == "20261115_003941"
    gespeichert = d.lies_verzeichnis(w)["dateien"]
    assert [x["pfad"] for x in gespeichert] == sorted(e) and all(
        len(x["sha256"]) == 64 for x in gespeichert
    )
    assert d.pruefen(w, daten) == []


def test_pruefen_findet_fehlende_veraenderte_und_neue_grosse_dateien(repo):
    w, daten = repo
    d.auslagern(w, daten, tun=True)
    kern = os.path.join(daten, "data", "research", "kern_20261115_003941.log")
    with open(kern, "r+b") as f:
        f.write(b"y")  # gleiche Groesse, anderer Inhalt
    assert d.pruefen(w, daten, schnell=True) == [], "schnell vergleicht nur die Groesse"
    assert d.pruefen(w, daten) == [
        "andere Pruefsumme im Datenordner: data/research/kern_20261115_003941.log"
    ]
    os.remove(
        os.path.join(daten, "data", "research", "laeufe", "lauf_k_20261102_234952.proben", "p.json")
    )
    _schreib(os.path.join(w, "data", "research", "neu_gross.bin"), 101)
    befunde = d.pruefen(w, daten)
    assert (
        "fehlt im Datenordner: data/research/laeufe/lauf_k_20261102_234952.proben/p.json" in befunde
    )
    assert "im Repo, gehoert in den Datenordner (neu): data/research/neu_gross.bin" in befunde


def test_auslagern_ueberschreibt_nichts(repo):
    w, daten = repo
    _schreib(os.path.join(daten, "data", "research", "kern_20261115_003941.log"), 7)
    with pytest.raises(SystemExit, match="ANGEHALTEN"):
        d.auslagern(w, daten, tun=True)
    assert os.path.getsize(os.path.join(daten, "data", "research", "kern_20261115_003941.log")) == 7
    assert os.path.exists(os.path.join(w, "data", "research", "kern_20261115_003941.log"))


def test_verzeichnis_im_repo_ist_vollstaendig_und_eindeutig():
    v = d.lies_verzeichnis(workspace.ROOT)
    assert int(v["regeln"]["grenze_bytes"]) == 50_000_000 and v["regeln"]["ganze_ordner"]
    pfade = [e["pfad"] for e in v["dateien"]]
    assert len(pfade) == len(set(pfade)) and pfade == sorted(pfade)
    for e in v["dateien"]:
        assert e["pfad"].startswith("data/") and "\\" not in e["pfad"], e
        assert (
            re.fullmatch(r"[0-9a-f]{64}", e["sha256"]) and int(e["bytes"]) >= 0
        )  # leere .stop-Marken der Auge-Laeufe gibt es wirklich, e


def test_datenordner_liegt_neben_dem_repo():
    assert os.path.dirname(workspace.DATEN) == os.path.dirname(workspace.ROOT)
    assert workspace.AUGE_LAEUFE.startswith(workspace.DATEN)


def test_abbruch_mitten_im_lauf_traegt_das_schon_verschobene_ein(repo):
    """ADR-073: haelt auslagern bei der dritten Datei an, stehen die ersten zwei trotzdem im Verzeichnis."""
    w, daten = repo
    _schreib(
        os.path.join(daten, "data", "research", "lage_20261115_130357_i2.jsonl.gz"), 7
    )  # die letzte kollidiert
    with pytest.raises(SystemExit, match="ANGEHALTEN"):
        d.auslagern(w, daten, tun=True)
    eingetragen = [e["pfad"] for e in d.lies_verzeichnis(w)["dateien"]]
    assert eingetragen == [
        "data/research/kern_20261115_003941.log",
        "data/research/laeufe/lauf_k_20261102_234952.proben/p.json",
    ]
    assert os.path.isfile(os.path.join(daten, "data", "research", "kern_20261115_003941.log"))
    assert (
        os.path.getsize(os.path.join(w, "data", "research", "lage_20261115_130357_i2.jsonl.gz"))
        == 300
    ), "die kollidierende Datei bleibt unangetastet im Repo"
