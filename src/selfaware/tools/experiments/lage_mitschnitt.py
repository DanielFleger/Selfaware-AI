# -*- coding: utf-8 -*-
"""Mitschnitt ohne Eingriff: laufende Partie weiterlaufen lassen und alle <schritt> Ticks die ganze Lage ins
Lageprotokoll schreiben (Daniel 22:39). Baut, kauft, verkauft nichts.
Aufruf: SHC_INSTANZ=1 uv run python -m selfaware.tools.experiments.lage_mitschnitt dauer=1500 [schritt=25] [tempo=60] [name=x]"""

from selfaware import workspace as _workspace
import os, sys, time
HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.game.ucp.befehl as kanal
from selfaware.telemetry.lageprotokoll import Lageprotokoll


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    dauer, schritt, tempo = int(arg.get("dauer", 1500)), int(arg.get("schritt", 25)), int(arg.get("tempo", 60))
    import selfaware.runtime.live.erstes_spiel as E
    from selfaware.game.ucp.laden import befehl
    from selfaware.game.ucp.steuerkarte import tick
    pfad = os.path.join(_workspace.DATA, 'lage_%s_%s_i%d.jsonl.gz' % (arg.get('name', 'mitschnitt'), time.strftime('%Y%m%d_%H%M%S'), kanal.INSTANZ))
    lage = Lageprotokoll(pfad)
    st, L, G = E.runde_lesen()
    lage.schreibe(st)
    t0 = st["t"]
    befehl({"tempo": tempo}, 0.5)
    befehl({"pause": False}, 0.5)
    try:
        while st["t"] - t0 < dauer:
            t1 = tick()
            while tick() - t1 < schritt:
                time.sleep(0.03)
            st, L, G = E.runde_lesen()
            lage.schreibe(st)
    finally:
        befehl({"pause": True}, 0.5)
    print("Mitschnitt Tick %d bis %d, %d Runden: %s" % (t0, st["t"], lage.runden, os.path.abspath(pfad)))


if __name__ == "__main__":
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
