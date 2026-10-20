"""Read-only dependency inventory. A file existing does not prove live compatibility."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import platform
from dataclasses import asdict, dataclass

from selfaware.config import LivePaths


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str


def live_checks(paths: LivePaths) -> tuple[Check, ...]:
    checks = []
    if platform.system() != "Windows":
        checks.append(Check("platform", "blocked", "legacy live tools require Windows"))
    else:
        checks.append(Check("platform", "present", "Windows; game compatibility unverified"))
    for module in ("yaml", "PIL", "numpy"):
        present = importlib.util.find_spec(module) is not None
        checks.append(
            Check(module, "present" if present else "blocked", "install the legacy extra")
        )
    if paths.game is None:
        checks.append(
            Check("game_path", "blocked", "configure SELFAWARE_GAME_PATH or [live].game_path")
        )
    else:
        for relative in ("Stronghold Crusader.exe",):
            file = paths.game / relative
            checks.append(Check(relative, "present" if file.is_file() else "blocked", str(file)))
        module = paths.game / "ucp/villagestudio/logik.lua"
        if module.is_file():
            digest = hashlib.sha256(module.read_bytes()).hexdigest()
            matched = digest == paths.expected_module_sha256
            checks.append(
                Check("logik.lua", "matched" if matched else "unverified", f"sha256={digest}")
            )
        else:
            checks.append(Check("logik.lua", "blocked", str(module)))
    if paths.module_init is None:
        checks.append(
            Check("module_init", "blocked", "configure the actual deployed module_init_path")
        )
    else:
        checks.append(
            Check(
                "module_init",
                "present" if paths.module_init.is_file() else "blocked",
                str(paths.module_init),
            )
        )
    if paths.village_studio is None:
        checks.append(Check("VillageStudio", "blocked", "configure SELFAWARE_VILLAGE_STUDIO_PATH"))
    else:
        catalogue = paths.village_studio / "lib/gebaeude.json"
        if catalogue.is_file():
            try:
                data = json.loads(catalogue.read_text(encoding="utf-8-sig"))
                if not isinstance(data, dict) or not isinstance(data.get("gebaeude"), dict):
                    raise ValueError("expected a gebaeude object")
                checks.append(Check("building_catalogue", "present", str(catalogue)))
            except (OSError, ValueError) as error:
                checks.append(Check("building_catalogue", "blocked", str(error)))
        else:
            checks.append(Check("building_catalogue", "blocked", str(catalogue)))
        helper = paths.village_studio / "werkzeug/instanz.py"
        checks.append(
            Check("instanz.py", "present" if helper.is_file() else "blocked", str(helper))
        )
    # Until a live GamePort is implemented and validated, never announce readiness.
    checks.append(
        Check("live_game_port", "unverified", "use legacy tools; live adapter migration is pending")
    )
    return tuple(checks)


def report(paths: LivePaths, *, offline: bool = False) -> dict:
    checks = () if offline else live_checks(paths)
    return {
        "offline_framework_available": True,
        "live_validation_performed": False,
        "live_ready": False,
        "checks": [asdict(check) for check in checks],
    }
