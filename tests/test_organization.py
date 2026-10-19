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
