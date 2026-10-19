# -*- coding: utf-8 -*-
"""Code-Kennung: ein kurzer Fingerabdruck ueber allen Code, der eine Partie steuert (Daniel 05.10. 20:46: "lass bitte als
Test immer sofort erkennen, ob es den neuen Test benutzt oder ob es noch einen alten benutzt - am besten mit einer
einmaligen Kennung").

Hineingerechnet werden:
  - jede erreichbare Python-Datei aus src/selfaware/, die erstes_spiel.py laden KANN: alle import-Anweisungen im Quelltext, auch die in
    Funktionen (der Planer laedt farmen_mischen erst spaeter), rekursiv - eine Liste, die man nicht pflegen muss;
  - die logik.lua der gewaehlten Instanz (befehl.SPIEL), die das Modul im Spiel laedt;
  - data/research/ertrag_startwerte_*.json (Startwerte aendern das Spiel wie Code).
Gleicher Stand = gleiche Kennung; eine geaenderte Zeile irgendwo darin = andere Kennung. Zeilenenden zaehlen nicht.

Aufruf:  uv run python -m selfaware.telemetry.kennung     -> Kennung des aktuellen Stands mit der Kennung je Datei
"""

from selfaware import workspace as _workspace
import ast, hashlib, os, sys

HIER = os.path.dirname(os.path.abspath(__file__))
START = "erstes_spiel.py"


def python_dateien(start=START):
    """All reachable package sources, including imports inside policy functions.

    Return checkout-relative paths without importing the live bot. The old
    basename-only walk missed dependencies once files moved into packages.
    """
    from pathlib import Path
    from selfaware.module_registry import MODULES

    source = Path(_workspace.ROOT) / "src"
    first = MODULES.get(start.removesuffix(".py"), start)
    seen, pending = set(), [first]
    files = set()
    while pending:
        module = pending.pop()
        if module in seen or not module.startswith("selfaware"):
            continue
        seen.add(module)
        path = source.joinpath(*module.split("."))
        path = path / "__init__.py" if path.is_dir() else path.with_suffix(".py")
        if not path.is_file():
            continue
        files.add(path.relative_to(_workspace.ROOT).as_posix())
        # Python executes each parent package before its requested submodule.
        pending.extend(".".join(module.split(".")[:i]) for i in range(1, len(module.split("."))))
        for node in ast.walk(ast.parse(path.read_bytes())):
            if isinstance(node, ast.Import):
                pending.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                pending.append(node.module)
                pending.extend(node.module + "." + alias.name for alias in node.names if alias.name != "*")
    return sorted(files)


def dateien():

    import selfaware.game.ucp.befehl as befehl
    aus = [os.path.join(_workspace.ROOT, f) for f in python_dateien()]
    lua = os.path.join(befehl.SPIEL, "ucp", "villagestudio", "logik.lua")
    if os.path.exists(lua):
        aus.append(lua)
    d = os.path.join(_workspace.DATA)
    aus += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.startswith("ertrag_startwerte_") and f.endswith(".json")]
    return aus


def kennung():
    """(kennung, {datei: kurz}) - Kennung = 8 Zeichen sha1 ueber Name und Inhalt aller Dateien."""
    gesamt, einzeln = hashlib.sha1(), {}
    for p in dateien():
        roh = open(p, "rb").read().replace(b"\r\n", b"\n")
        name = os.path.relpath(p, _workspace.ROOT).replace(os.sep, "/")
        einzeln[name] = hashlib.sha1(roh).hexdigest()[:6]
        gesamt.update(name.encode() + b"\0" + roh + b"\0")
    return gesamt.hexdigest()[:8], einzeln


def zeile():
    k, e = kennung()
    return "CODE-KENNUNG %s (%d Dateien: %s)" % (k, len(e), ", ".join("%s %s" % kv for kv in sorted(e.items())))


if __name__ == "__main__":
    print(zeile())
