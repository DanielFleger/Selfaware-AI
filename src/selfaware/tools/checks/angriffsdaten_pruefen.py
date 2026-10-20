# -*- coding: utf-8 -*-
"""Gegenprobe fuer die Rohdaten, aus denen das wirksame Lord-Minimum gelernt wird.

Aufruf: uv run python -m selfaware.tools.checks.angriffsdaten_pruefen [HEAD]
"""

from selfaware import workspace as _workspace
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import types

HIER = os.path.dirname(os.path.abspath(__file__))


if len(sys.argv) > 1 and sys.argv[1] == "HEAD":
    quelle = subprocess.check_output(
        ["git", "-C", _workspace.ROOT, "show", "HEAD:src/selfaware/micro/tasks/assassinen.py"], text=True)
    A = types.ModuleType("assassinen_alt")
    A.__file__ = _workspace.module_file("assassinen")
    exec(compile(quelle, "HEAD:src/selfaware/micro/tasks/assassinen.py", "exec"), A.__dict__)
else:
    import selfaware.micro.tasks.assassinen as A


def einheit(typ, besitzer, x, y, leben=12500, zielart=0, ziel=0):
    return {"typ": typ, "besitzer": besitzer, "x": x, "y": y, "leben": leben,
            "zielart": zielart, "zieleinheit": ziel, "zustand": 1, "laufx": x, "laufy": y}


def main():
    t = A.Einzeln(1)
    truppe = {100, 101}
    t.mitglieder = set(truppe)
    t.lordtrupp.update(mitglieder=set(truppe), phase="angriff", lord=500)
    t.angriffe.append({"runde": 1, "groesse": 2, "lord_vorher": 75000, "lord_nachher": 75000,
                       "fern": 1, "nah": 1, "weg_min": 5, "weg_max": 6, "am_lord_max": 0,
                       "erreicht_runde": None, "anderes": {}, "truppe": set(truppe), "verluste": 0,
                       "leben_zuletzt": {100: 12500, 101: 12500}})
    L = {
        100: einheit(73, 1, 10, 10, leben=12000, zielart=4, ziel=500),
        101: einheit(73, 1, 11, 10, zielart=4, ziel=500),
        500: einheit(55, 2, 15, 10, leben=75000),
        600: einheit(22, 2, 16, 10, zielart=4, ziel=100),
        601: einheit(24, 2, 30, 30, zielart=0, ziel=0),
        700: einheit(3, 2, 40, 40, zielart=0, ziel=0),
    }
    G = {
        800: {"typ": 1, "besitzer": 2, "x": 20, "y": 20, "leben": 1000},
        801: {"typ": 19, "besitzer": 1, "x": 5, "y": 5, "leben": 1000},
    }
    fd, pfad = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    try:
        t.wellen_protokoll = pfad
        t.gelaende = ["....", ".##."]
        fern, nah = t._feinde(L)
        t._lord_messen(L, G, 500, L[500], (15, 10), fern, nah)
        zeilen = [json.loads(z) for z in open(pfad, encoding="utf-8")]
        karte, daten = zeilen
    finally:
        os.unlink(pfad)
    ang = {e["nr"]: e for e in daten.get("angreifer", [])}
    leute = {e["nr"]: e for e in daten.get("einheiten", [])}
    gebaeude = {e["nr"]: e for e in daten.get("gebaeude", [])}
    pruefungen = [
        ("beide Angreifer mit Ort/Ziel", set(ang) == truppe and all("x" in e and "ziel" in e for e in ang.values())),
        ("echter Lebensverlust je Angreifer", ang.get(100, {}).get("schaden") == 500),
        ("alle Menschen und Einheiten, auch Arbeiter", set(leute) == set(L)),
        ("Schuetze zielt tatsaechlich auf Angreifer", leute.get(600, {}).get("zielt_auf_angreifer") is True),
        ("nur Naehe gilt nicht als Angriff", leute.get(601, {}).get("zielt_auf_angreifer") is False),
        ("alle bestehenden Gebaeude beider Seiten", set(gebaeude) == set(G)),
        ("Gelaende einmal vollstaendig", karte.get("art") == "gelaende" and karte.get("zeilen") == t.gelaende),
    ]
    for text, ok in pruefungen:
        print(("OK  " if ok else "ROT ") + text)
    print("%d von %d gruen" % (sum(ok for _, ok in pruefungen), len(pruefungen)))
    return 0 if all(ok for _, ok in pruefungen) else 1


if __name__ == "__main__":
    raise SystemExit(main())
