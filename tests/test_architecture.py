from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest

from selfaware.module_registry import MODULES

ROOT = Path(__file__).resolve().parents[1]


def test_domain_and_coordination_do_not_import_live_legacy_tools():
    """Keep the I/O boundary enforceable as more policies are migrated."""
    for area in ("domain", "coordination"):
        for path in (ROOT / "src/selfaware" / area).rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_bytes())):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module]
                assert not any(
                    name.startswith(("selfaware.game.ucp", "selfaware.runtime.live"))
                    or name in {"befehl", "laden", "erstes_spiel"}
                    for name in names
                ), path


def test_domain_remains_free_of_filesystem_process_and_game_imports():
    banned = {"os", "pathlib", "subprocess", "io", "ctypes", "selfaware.game"}
    for path in (ROOT / "src/selfaware/domain").glob("*.py"):
        for node in ast.walk(ast.parse(path.read_bytes())):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            assert not any(n == b or n.startswith(b + ".") for n in names for b in banned), path


def test_all_legacy_python_still_compiles_without_importing_it():
    assert MODULES
    for module in MODULES.values():
        path = ROOT / "src" / (module.replace(".", "/") + ".py")
        compile(path.read_bytes(), str(path), "exec")


def test_relocated_modules_use_package_imports_and_resolve_local_dependencies():
    for module in MODULES.values():
        path = ROOT / "src" / (module.replace(".", "/") + ".py")
        for node in ast.walk(ast.parse(path.read_bytes())):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            assert not set(names) & set(MODULES), (path, names)
            for name in names:
                if name.startswith("selfaware."):
                    local = ROOT / "src" / name.replace(".", "/")
                    assert (
                        local.with_suffix(".py").is_file() or (local / "__init__.py").is_file()
                    ), (path, name)


def test_relocation_manifest_preserves_research_and_removes_old_paths():
    if not (ROOT / "data/research").is_dir() and not (ROOT / ".git").exists():
        pytest.skip("The source distribution excludes the 578 MiB historical corpus")
    manifest = json.loads((ROOT / "docs/relocations.json").read_text(encoding="utf-8"))
    destinations = set()
    for entry in manifest["files"]:
        old, new = ROOT / entry["old"], ROOT / entry["new"]
        assert not old.exists(), old
        assert new.is_file(), new
        assert entry["new"] not in destinations
        destinations.add(entry["new"])
        if not entry["content_changed"]:
            assert hashlib.sha256(new.read_bytes()).hexdigest() == entry["sha256_before"], new
    assert {
        "src/" + module.replace(".", "/") + ".py" for module in MODULES.values()
    } <= destinations
