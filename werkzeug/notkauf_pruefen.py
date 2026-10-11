# -*- coding: utf-8 -*-
"""Gegenprobe Notkauf Nahrung ohne Spiel (SAI 11.10., Nomade-Lauf 1011g: elf Wochen Nahrung 0 bei 3.500+ Gold, Regelbruch).
Soll je Fall vorher festgelegt. Aufruf: python notkauf_pruefen.py"""
import erstes_spiel as E

FAELLE = [
    ("Lauf 1011g: Nahrung 0, Puffer 11, Gold frei 3.500 -> kaufen", 0, 11, 3500, True),
    ("Nahrung 10 knapp unter Puffer 11, Gold da -> kaufen", 10, 11, 400, True),
    ("Nahrung gleich Puffer -> nicht kaufen", 11, 11, 3500, False),
    ("Nahrung 0, aber nur 100 Gold frei -> nicht kaufen", 0, 11, 100, False),
    ("Nahrung 0, Gold genau an der Grenze -> kaufen", 0, 11, E.NOTKAUF_GOLD, True),
]
erg = []
for name, nahrung, puffer, gold, soll in FAELLE:
    ist = E.nahrung_notkauf(nahrung, puffer, gold)
    erg.append(ist == soll)
    print("%s %-58s %s" % ("OK  " if ist == soll else "ROT ", name, ist))
print("%d von %d gruen" % (sum(erg), len(erg)))
raise SystemExit(0 if all(erg) else 1)
