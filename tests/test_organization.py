from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from selfaware import workspace
from selfaware.module_registry import MODULES
from selfaware.telemetry.kennung import python_dateien


def invoke(code: str, cwd: Path, **environment: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=cwd,
        env=dict(os.environ, PYTHONUTF8="1", **environment),
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=20,
    )


def test_listing_modules_is_safe_and_independent_of_working_directory(tmp_path):
    result = invoke(
        "from selfaware.cli import main; import sys; main(['modules']); "
        "assert 'selfaware.game.ucp.befehl' not in sys.modules; "
        "assert 'selfaware.runtime.live.erstes_spiel' not in sys.modules",
        tmp_path,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == MODULES
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize(
    "name",
    [
        "bierkette_pruefen",
        "brotbau_trocken",
        "fallenwache_pruefen",
        "gefahrenzone_pruefen",
        "lordschutz_trocken",
        "partner_pruefen",
        "raids_pruefen",
        "stillstand_trocken",
    ],
)
def test_existing_offline_checks_run_through_new_launcher(name, tmp_path):
    # Explicitly selected pure checks, not discovery of arbitrary game probes.
    result = invoke(f"from selfaware.cli import main; main(['run', {name!r}])", tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout


def test_recorded_code_fingerprint_follows_relocated_policy_dependencies():
    paths = set(python_dateien())
    for name in ("erstes_spiel", "befehl", "wirtschaft", "assassinen", "kennung"):
        assert "src/" + MODULES[name].replace(".", "/") + ".py" in paths
    assert "src/selfaware/workspace.py" in paths
    assert "src/selfaware/module_registry.py" in paths
    assert len(paths) > 50
    assert all((Path(workspace.ROOT) / path).is_file() for path in paths)


def test_child_process_commands_use_installed_modules():
    command = workspace.module_command("erstes_spiel", "tempo=40")
    assert command == [sys.executable, "-u", "-m", MODULES["erstes_spiel"], "tempo=40"]
    assert Path(workspace.module_file("erstes_spiel.py")).is_file()


def test_external_and_state_path_overrides_do_not_create_files(tmp_path):
    result = invoke(
        "from selfaware import workspace as w; import json; "
        "print(json.dumps([w.ROOT, w.VILLAGE_STUDIO, w.STATE]))",
        tmp_path,
        SELFAWARE_WORKSPACE=workspace.ROOT,
        SELFAWARE_VILLAGE_STUDIO_PATH=str(tmp_path / "external"),
        SELFAWARE_STATE_DIR=str(tmp_path / "state"),
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [
        workspace.ROOT,
        str(tmp_path / "external"),
        str(tmp_path / "state"),
    ]
    assert not list(tmp_path.iterdir())


def test_relocated_backlog_reads_its_authoritative_source_from_foreign_cwd(tmp_path):
    from selfaware.tools.planning import backlog

    root = Path(workspace.ROOT)
    assert Path(backlog.QUELLE) == root / "docs/backlog/backlog.json"
    assert Path(backlog.ANSICHT) == root / "docs/backlog/Backlog.html"
    before = Path(backlog.QUELLE).read_bytes()
    result = invoke("from selfaware.cli import main; main(['run', 'backlog', 'fokus'])", tmp_path)
    assert result.returncode == 0, result.stderr
    assert "JETZT DRAN:" in result.stdout
    assert Path(backlog.QUELLE).read_bytes() == before
    retired = {
        entry["old"]
        for entry in json.loads((root / "docs/relocations.json").read_text(encoding="utf-8"))[
            "files"
        ]
    }
    assert not {path for point in backlog.lade()["punkte"] for path in point["wo"]} & retired


def test_audit_suite_discovery_excludes_real_game_probes(tmp_path):
    script = Path(workspace.ROOT) / "audit/run_checks.py"
    result = subprocess.run(
        [sys.executable, str(script), "--list-suites"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    suites = json.loads(result.stdout)
    assert "absender_pruefen.py" in suites
    assert "absender_live_pruefen.py" not in suites
    assert "spieler2_pruefen.py" not in suites


def test_post_match_training_launches_relocated_analysis_modules(monkeypatch, tmp_path):
    from selfaware.learning import partie_lernen

    calls = []

    def analysis(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, "VERGLEICH ok\n Einnahmen 25\n", "")

    monkeypatch.setattr(partie_lernen.subprocess, "run", analysis)
    monkeypatch.setattr(partie_lernen, "AUS", str(tmp_path))
    monkeypatch.setattr(workspace, "ROOT", str(tmp_path))
    assert partie_lernen.vergleich("recording.gz", "stamp")["zeilen"] == ["VERGLEICH ok"]
    assert partie_lernen.gold("console.txt", "recording.gz", "stamp")["fehler"] is None
    assert calls == [
        [
            sys.executable,
            "-P",
            "-m",
            MODULES["partie_vergleich"],
            "recording.gz",
            "json=" + str(tmp_path / "partievergleich_stamp.json"),
        ],
        [sys.executable, "-P", "-m", MODULES["gold_bilanz"], "console.txt", "recording.gz"],
    ]
    assert not list(tmp_path.iterdir())


def test_paired_training_preserves_game_and_recording_launches(monkeypatch, tmp_path):
    from selfaware.learning import lernen_1v1

    calls = []
    trace = tmp_path / "recording.jsonl.gz"
    trace.touch()

    def launch(command, **kwargs):
        calls.append(command)
        if command[3] == MODULES["erstes_spiel"]:
            kwargs["stdout"].write(
                f"CODE-KENNUNG abc123\nLageprotokoll (jede Runde komplett): {trace}\n"
            )
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(lernen_1v1.subprocess, "run", launch)
    monkeypatch.setattr(lernen_1v1, "AUS", str(tmp_path))
    monkeypatch.setattr(lernen_1v1, "wert", lambda *args: {"tick": lernen_1v1.BIS_TICK})
    # Reads the actual relocated watcher, without importing or starting the live bot.
    watcher_args = lernen_1v1.wache_args()
    monkeypatch.setattr(lernen_1v1, "wache_args", lambda: watcher_args)
    monkeypatch.setattr(workspace, "ROOT", str(tmp_path))
    result = lernen_1v1.lauf({"heer_anteil": 0.3}, ("Green Haven", "4,3"), 1, "A", {})
    assert result["code"] == "abc123"
    assert "ungueltig" not in result
    assert calls[0][:4] == [sys.executable, "-u", "-m", MODULES["erstes_spiel"]]
    assert calls[0][4 : 4 + len(watcher_args)] == watcher_args
    assert "heer_anteil=0.3" in calls[0]
    assert calls[1][:4] == [sys.executable, "-P", "-m", MODULES["partie_lernen"]]
    assert calls[1][5] == str(trace)
    assert Path(lernen_1v1.STOP) == Path(workspace.STATE) / "STOP_LERNEN"
    assert Path(lernen_1v1.PAUSE) == Path(workspace.STATE) / "PAUSE_LERNEN"
