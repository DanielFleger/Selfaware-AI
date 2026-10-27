# -*- coding: utf-8 -*-
"""B-272 (Partie 180423, Tick 28934): Daniels App spielte ohne die gemessenen Kampfwerte - das Paket (distribution/
build_package.py) lieferte nur 8 Datendateien, gefecht.py fiel auf den Ersatzwert 20 je Takt zurueck und der Lord-Wettlauf
ging nie los. Diese Pruefung haelt den Spielweg (alle Module, die erstes_spiel / samurai_wache / local_launcher laden) gegen
das Paket: jede Datei in daten/, deren Name im Spielweg-Code steht und die im Repo liegt, muss im Paket sein - oder mit
Grund in NOT_SHIPPED stehen. Gegenprobe: nimmt man 'editor_duell_*.jsonl' aus SEEDS, wird die Pruefung rot.

Zusaetzlich (mit --app <ordner>): fehlt der installierten App eine Datei, die das Paket liefern wuerde?
Aufruf: python werkzeug/paket_daten_pruefen.py [--app "<...>/Selfaware-AI"]"""
import ast
import glob
import importlib.util
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HIER)
D = os.path.join(ROOT, "daten")
START = ("erstes_spiel", "samurai_wache", "local_launcher")
NAME = re.compile(r"[\"']([A-Za-z0-9_\-]+(?:\*[A-Za-z0-9_\-]*)?\.(?:json|jsonl|csv|txt|gz|npz))[\"']")


def paket():
    spec = importlib.util.spec_from_file_location("build_package", os.path.join(ROOT, "distribution", "build_package.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def spielweg():
    """Module des Spielwegs: Importhuelle der START-Module innerhalb von werkzeug/."""
    mods = {f[:-3] for f in os.listdir(HIER) if f.endswith(".py")}
    gesehen, offen = set(), [m for m in START if m in mods]
    while offen:
        m = offen.pop()
        if m in gesehen:
            continue
        gesehen.add(m)
        baum = ast.parse(open(os.path.join(HIER, m + ".py"), encoding="utf-8").read())
        for n in ast.walk(baum):
            if isinstance(n, ast.Import):
                offen += [a.name.split(".")[0] for a in n.names if a.name.split(".")[0] in mods]
            elif isinstance(n, ast.ImportFrom) and n.module and n.module.split(".")[0] in mods:
                offen.append(n.module.split(".")[0])
    return gesehen


def pruefe(bp=None, app=None):
    """Liste der Fehler (leer = gruen)."""
    bp = bp or paket()
    if hasattr(bp, "seed_files"):
        geliefert = {os.path.basename(str(f)) for f in bp.seed_files()}
    else:                                    # Paketbauer vor B-272: nur feste Namen
        geliefert = set(bp.SEEDS)
    fehler = []
    ausnahmen = getattr(bp, "NOT_SHIPPED", {})
    for m in sorted(spielweg()):
        for name in sorted(set(NAME.findall(open(os.path.join(HIER, m + ".py"), encoding="utf-8").read()))):
            im_repo = [os.path.basename(f) for f in glob.glob(os.path.join(D, name))]
            if not im_repo or name in ausnahmen:
                continue
            if not any(f in geliefert for f in im_repo):
                fehler.append("%s liest %s (%d im Repo) - nicht im Paket und nicht in NOT_SHIPPED" % (m, name, len(im_repo)))
    if app:
        for f in sorted(geliefert):
            if not os.path.exists(os.path.join(app, "daten", f)):
                fehler.append("App %s: daten/%s fehlt" % (app, f))
    return fehler


if __name__ == "__main__":
    app = sys.argv[sys.argv.index("--app") + 1] if "--app" in sys.argv else None
    bp = paket()
    f = pruefe(bp, app)
    # Gegenprobe: ohne die Kampfwerte muss die Pruefung anschlagen (sonst prueft sie nichts)
    alt = bp.SEEDS
    bp.SEEDS = tuple(s for s in alt if s != "editor_duell_*.jsonl")
    gegen = pruefe(bp)
    bp.SEEDS = alt
    for z in f:
        print("ROT:", z)
    print("Gegenprobe ohne editor_duell: %s" % ("schlaegt an" if any("editor_duell" in z for z in gegen) else "SCHLAEGT NICHT AN"))
    ok = not f and any("editor_duell" in z for z in gegen)
    print("%d Module im Spielweg, %d Dateien im Paket: %s" % (len(spielweg()), len(bp.seed_files()) if hasattr(bp, "seed_files") else len(bp.SEEDS), "GRUEN" if ok else "ROT"))
    sys.exit(0 if ok else 1)
