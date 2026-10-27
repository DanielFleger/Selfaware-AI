# -*- coding: utf-8 -*-
"""B-282 Pause = nichts tun (Daniel 28.10. 00:51; Partie 002852: im pausierten Spiel liefen die Runden weiter, die Steuer ging
von 2 auf 8 und zurueck auf 0). Pruefung am Quelltext der Phase-2-Schleife (eine Partie ohne Spiel gibt es dafuer nicht):
  1. die Pausenwache steht direkt nach runde_lesen() - vor JEDEM Modul und vor "runde += 1"
  2. sie vergleicht den Takt mit dem der letzten Runde und springt mit continue zurueck
  3. der Takt der letzten Runde wird erst nach der Wache fortgeschrieben
Grenze: das prueft die Stelle im Quelltext, nicht das Spiel - im Spiel belegt erst eine Partie mit Pause (keine STEUER-Zeile
waehrend der Pause).
Aufruf: python pause_pruefen.py"""
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
q = open(os.path.join(HIER, "erstes_spiel.py"), encoding="utf-8").read()
start = q.index("    pause_t = None")
lesen = q.index("st, L, G = runde_lesen()", start)
wache = q.find('if st and st.get("t") is not None and st["t"] == pause_t:', lesen)
weiter = q.find("continue", wache)
setzen = q.find('pause_t = st.get("t")', lesen)
zaehlen = q.index("runde += 1", lesen)
erstes_modul = min(i for i in (q.find("zielboerse.runde", lesen), q.find("wirt.heer_einnahme", lesen), q.find("lage.schreibe", lesen)) if i > 0)
faelle = [
    ("1 Wache direkt nach runde_lesen, vor allen Modulen und vor runde += 1", 0 < wache < erstes_modul and wache < zaehlen),
    ("2 Wache springt mit continue zurueck (vor dem Fortschreiben)", 0 < weiter < setzen),
    ("3 Takt erst nach der Wache fortgeschrieben", wache < setzen < erstes_modul),
]
for name, ok in faelle:
    print("%s %s" % ("OK  " if ok else "ROT ", name))
print("%d von %d gruen" % (sum(ok for _, ok in faelle), len(faelle)))
sys.exit(0 if all(ok for _, ok in faelle) else 1)
