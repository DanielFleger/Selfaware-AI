from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LivePaths:
    game: Path | None = None
    village_studio: Path | None = None
    expected_module_sha256: str | None = None
    module_init: Path | None = None


def load_live_paths(path: Path | None = None) -> LivePaths:
    """Read explicit TOML/env settings; never create files or infer a Steam path.

    Relative TOML paths resolve against that file. Environment paths resolve
    against the current working directory and override the TOML values.
    """
    section: dict = {}
    base = Path.cwd()
    if path is not None:
        with path.open("rb") as stream:
            section = tomllib.load(stream).get("live", {})
        base = path.resolve().parent
        if not isinstance(section, dict):
            raise ValueError("[live] must be a TOML table")

    def configured_path(key: str, env: str) -> Path | None:
        raw = os.environ.get(env, section.get(key, ""))
        if not isinstance(raw, str):
            raise ValueError(f"{key} must be a path string")
        if not raw.strip():
            return None
        value = Path(raw).expanduser()
        anchor = Path.cwd() if env in os.environ else base
        return (anchor / value).resolve() if not value.is_absolute() else value.resolve()

    digest = os.environ.get("SELFAWARE_MODULE_SHA256", section.get("module_sha256", ""))
    if not isinstance(digest, str):
        raise ValueError("module_sha256 must be a string")
    digest = digest.strip().lower()
    if digest and (len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest)):
        raise ValueError("module_sha256 must contain 64 hexadecimal characters")
    return LivePaths(
        configured_path("game_path", "SELFAWARE_GAME_PATH"),
        configured_path("village_studio_path", "SELFAWARE_VILLAGE_STUDIO_PATH"),
        digest or None,
        configured_path("module_init_path", "SELFAWARE_MODULE_INIT_PATH"),
    )
