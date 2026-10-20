# -*- coding: utf-8 -*-
"""Gleiches Ergebnis? Der neue Holzfaeller-Plan (eroeffnung.plane_holz, 19.10. 21:20) gegen den alten
(eroeffnung_holz_alt.plane_holz_alt) - ganzer Eroeffnungsplan (A=0) fuer jeden vermessenen Startplatz, Feld fuer Feld
verglichen (Lager, jede Huette mit Holz und Rate, belegte Felder), dazu die Zeit.
Gegenprobe: uv run python -m selfaware.tools.checks.eroeffnung_holz_pruefen kaputt  -> der neue Plan rechnet mit 1 Feld Laufweg mehr je
Gang (JE_FELD + 1) - muss ROT werden, sonst vergleicht der Pruefer nichts.
Aufruf: uv run python -m selfaware.tools.checks.eroeffnung_holz_pruefen [kaputt] [kurz ...]"""

from selfaware import workspace as _workspace
import glob
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))

D = os.path.join(_workspace.DATA)
import selfaware.macro.eroeffnung as E
import selfaware.tools.checks.eroeffnung_holz_alt as ALT


def rechne(kurz, fn, kaputt=False):
    alt_fn, je_feld = E.plane_holz, E.JE_FELD
    E.plane_holz = fn
    if kaputt:
        E.JE_FELD = je_feld + 1
    try:
        t = time.time()
        p = E.plane(K=14, A=0, start=kurz)
        return p, time.time() - t
    finally:
        E.plane_holz, E.JE_FELD = alt_fn, je_feld


def main():
    args = sys.argv[1:]
    kaputt = "kaputt" in args
    namen = [a for a in args if a != "kaputt"] or sorted(
        os.path.basename(p)[6:-5] for p in glob.glob(os.path.join(D, "start_*.json")) if "_platz_" not in p)
    neu_fn = E.plane_holz
    gleich, s_alt, s_neu = 0, 0.0, 0.0
    for kurz in namen:
        pa, ta = rechne(kurz, ALT.plane_holz_alt)
        pn, tn = rechne(kurz, neu_fn, kaputt)
        s_alt, s_neu = s_alt + ta, s_neu + tn
        ja = json.dumps(pa, sort_keys=True, default=str) == json.dumps(pn, sort_keys=True, default=str)
        gleich += ja
        unterschied = "" if ja else " | alt Lager %s Holz %s, neu Lager %s Holz %s" % (
            pa.get("lager"), pa.get("holz_in_20000_ticks"), pn.get("lager"), pn.get("holz_in_20000_ticks"))
        print("%-4s %-30s alt %5.1f s  neu %5.1f s%s" % ("OK" if ja else "ROT", kurz, ta, tn, unterschied), flush=True)
    print("%d von %d gleich - alt %.0f s, neu %.0f s zusammen%s" % (gleich, len(namen), s_alt, s_neu,
                                                                    " (GEGENPROBE kaputt)" if kaputt else ""))
    return 0 if gleich == len(namen) else 1


if __name__ == "__main__":
    sys.exit(main())
