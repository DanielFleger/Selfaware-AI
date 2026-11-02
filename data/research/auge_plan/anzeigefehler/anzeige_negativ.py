# -*- coding: utf-8 -*-
"""Negativlauf B-144: Jede Sabotage muss die Tests rot machen. Danach steht jede Datei wieder wie vorher."""
import os, subprocess, sys

E = "src/selfaware/tools/experiments/"
FAELLE = [
    ("Normalwert 0", "src/selfaware/game/ucp/drehwert.py", "NORMAL = 15\n", "NORMAL = 0\n"),
    ("Lauf F schickt 0", E + "auge_lauf_f.py", '"richtung": drehwert(g["mapper"])}}, 0.3)', '"richtung": 0}}, 0.3)'),
    ("Reparatur fasst Tore an", E + "anzeige_reparieren.py", 'e["typ"] not in WERKSTAETTEN | TORE', "True"),
    ("Reparatur zerstoert Nachbarfeld", E + "anzeige_reparieren.py", "neu = (alt & 0xFFFF0000) | NORMAL", "neu = NORMAL"),
    ("Modul laesst Nicht-Toren ihren Wert", E + "auge_lauf_f.py", "and (b.richtung or 15) or 15", "and (b.richtung or 15) or (b.richtung or 15)"),
    ("Reparatur prueft nicht nach", E + "anzeige_reparieren.py", "        if rest:\n", "        if False:\n"),
]
env = dict(os.environ, PYTHONPATH="src", PYTHONIOENCODING="utf-8")
schlecht = 0
for name, pfad, alt, neu in FAELLE:
    roh = open(pfad, "rb").read()
    text = roh.decode("utf-8")
    if "\r\n" in text:
        alt_n, neu_n = alt.replace("\n", "\r\n"), neu.replace("\n", "\r\n")
    else:
        alt_n, neu_n = alt, neu
    assert text.count(alt_n) == 1, (name, text.count(alt_n))
    try:
        open(pfad, "wb").write(text.replace(alt_n, neu_n).encode("utf-8"))
        r = subprocess.run([sys.executable, "-m", "pytest", "tests/test_anzeige_drehwert.py", "-q", "--no-header", "-x"], capture_output=True, text=True, env=env, encoding="utf-8", errors="replace")
        rot = r.returncode != 0
        zeile = [z for z in r.stdout.splitlines() if z.startswith("FAILED") or "passed" in z or "failed" in z][:1]
        print(("ROT  " if rot else "GRUEN"), name, "|", (zeile[0][:100] if zeile else ""))
        schlecht += 0 if rot else 1
    finally:
        open(pfad, "wb").write(roh)
print("Sabotage nicht bemerkt:", schlecht)
sys.exit(1 if schlecht else 0)
