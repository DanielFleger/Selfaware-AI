# -*- coding: utf-8 -*-
"""Gegenprobe Notkauf Nahrung ohne Spiel (SAI 11.10., Nomade-Lauf 1011g: elf Wochen Nahrung 0 bei 3.500+ Gold, Regelbruch).
Soll je Fall vorher festgelegt. Aufruf: uv run python -m selfaware.tools.checks.notkauf_pruefen"""
import selfaware.runtime.live.erstes_spiel as E

FAELLE = [
    ("Lauf 1011g: Nahrung 0, Gold frei 3.500 -> kaufen", 0, 3500, True),
    ("Lauf 1011i Tick ~3.000: Nahrung 5 unter Puffer 6, Gold 197 -> NICHT", 5, 197, False),
    ("Lauf 1011i: Nahrung 3, Gold 413 -> NICHT (Nahrung auf Kante)", 3, 413, False),
    ("Nahrung 0, aber nur 100 Gold frei -> nicht kaufen", 0, 100, False),
    ("Nahrung 0, Gold genau an der Grenze -> kaufen", 0, E.NOTKAUF_GOLD, True),
]
erg = []
for name, nahrung, gold, soll in FAELLE:
    ist = E.nahrung_notkauf(nahrung, gold)
    erg.append(ist == soll)
    print("%s %-58s %s" % ("OK  " if ist == soll else "ROT ", name, ist))
print("%d von %d gruen" % (sum(erg), len(erg)))
raise SystemExit(0 if all(erg) else 1)
