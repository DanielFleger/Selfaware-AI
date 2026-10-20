from __future__ import annotations

import json
from pathlib import Path

import pytest

from selfaware.cli import main
from selfaware.config import LivePaths, load_live_paths
from selfaware.diagnostics import live_checks


def test_offline_doctor_needs_no_machine_paths_or_game(capsys, monkeypatch):
    monkeypatch.setenv("SHC_INSTANZ", "not-a-live-instance")
    assert main(["doctor", "--offline"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["offline_framework_available"]
    assert not data["live_ready"] and not data["live_validation_performed"]


def test_replay_cli_runs_the_existing_record_schema(capsys):
    fixture = Path(__file__).parent / "fixtures/legacy_sample.jsonl"
    assert main(["replay", str(fixture)]) == 0
    data = json.loads(capsys.readouterr().out)
    assert (data["frames"], data["first_tick"], data["last_tick"]) == (2, 100, 110)
    assert data["submitted_actions"] == 0 and not data["game_effects_simulated"]
    assert data["last_entities_without_uid"] == 2


@pytest.mark.parametrize("content", ["", "[]\n", "{broken}\n"])
def test_empty_or_malformed_replay_exits_with_actionable_error(tmp_path, capsys, content):
    trace = tmp_path / "trace.jsonl"
    trace.write_text(content)
    assert main(["replay", str(trace)]) == 2
    assert "error" in json.loads(capsys.readouterr().out)


def test_paths_resolve_relative_to_config_and_environment_overrides_it(tmp_path, monkeypatch):
    config = tmp_path / "local.toml"
    config.write_text('[live]\ngame_path = "game"\nvillage_studio_path = "vs"\n')
    for key in ("SELFAWARE_GAME_PATH", "SELFAWARE_VILLAGE_STUDIO_PATH", "SELFAWARE_MODULE_SHA256"):
        monkeypatch.delenv(key, raising=False)
    paths = load_live_paths(config)
    assert paths.game == tmp_path / "game"
    assert paths.village_studio == tmp_path / "vs"
    monkeypatch.setenv("SELFAWARE_GAME_PATH", str(tmp_path / "override"))
    assert load_live_paths(config).game == tmp_path / "override"
    assert not paths.game.exists()  # Reading configuration did not create a game directory.


def test_bad_hash_is_reported_without_attempting_module_loading(tmp_path, capsys):
    config = tmp_path / "local.toml"
    config.write_text('[live]\nmodule_sha256 = "bad"\n')
    assert main(["doctor", "--config", str(config)]) == 2
    assert "64 hexadecimal" in capsys.readouterr().out


def test_missing_external_dependencies_remain_explicit_blockers():
    checks = {c.name: c for c in live_checks(LivePaths())}
    assert checks["game_path"].status == checks["VillageStudio"].status == "blocked"
    assert checks["live_game_port"].status == "unverified"
    assert checks["module_init"].status == "blocked"


def test_module_entry_location_is_explicit_instead_of_assuming_an_install_layout(tmp_path):
    module_init = tmp_path / "custom-module-location" / "init.lua"
    module_init.parent.mkdir()
    module_init.write_text("-- module fixture, never executed\n")
    checks = {c.name: c for c in live_checks(LivePaths(module_init=module_init))}
    assert checks["module_init"].status == "present"
