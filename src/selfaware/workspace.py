"""Paths shared by the relocated research bot; importing this module writes nothing.

The installed offline framework does not need a checkout. Existing live/research
modules do: their measured data and assets remain versioned beside the source.
"""

from __future__ import annotations

import os
from pathlib import Path

from selfaware.module_registry import MODULES


def workspace_root() -> Path:
    configured = os.environ.get("SELFAWARE_WORKSPACE")
    if configured:
        root = Path(configured).expanduser().resolve()
        if (
            not (root / "pyproject.toml").is_file()
            or not (root / "docs/relocations.json").is_file()
        ):
            raise FileNotFoundError(f"SELFAWARE_WORKSPACE is not a project checkout: {root}")
        return root
    for root in (*Path(__file__).resolve().parents, Path.cwd(), *Path.cwd().parents):
        if (root / "pyproject.toml").is_file() and (root / "docs/relocations.json").is_file():
            return root
    raise FileNotFoundError(
        "Current-bot tools require a checkout; set SELFAWARE_WORKSPACE to its root"
    )


ROOT = os.fspath(workspace_root())
DATA = os.path.join(ROOT, "data", "research")
STATE = os.path.abspath(os.environ.get("SELFAWARE_STATE_DIR", os.path.join(ROOT, "var", "legacy")))
VILLAGE_STUDIO = os.path.abspath(
    os.environ.get("SELFAWARE_VILLAGE_STUDIO_PATH", os.path.join(ROOT, "..", "VillageStudio"))
)
AI_ASSETS = os.path.join(ROOT, "assets", "ai")


def module_file(name: str) -> str:
    """Locate a registered former flat script, including source-comparison tools."""
    module = MODULES[name.removesuffix(".py")]
    return os.path.join(ROOT, "src", *module.split(".")) + ".py"


def module_command(name: str, *arguments: str) -> list[str]:
    """Use the active interpreter and package imports in every child process."""
    import sys

    return [sys.executable, "-u", "-m", MODULES[name.removesuffix(".py")], *arguments]
