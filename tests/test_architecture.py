from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_domain_and_coordination_do_not_import_live_legacy_tools():
    """Keep the I/O boundary enforceable as more policies are migrated."""
    for path in (ROOT / "src/selfaware").rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_bytes())):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            assert not ({n.split(".")[0] for n in names} & {"befehl", "laden", "erstes_spiel"}), (
                path
            )


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
    paths = list((ROOT / "werkzeug").glob("*.py"))
    assert paths
    for path in paths:
        compile(path.read_bytes(), str(path), "exec")
