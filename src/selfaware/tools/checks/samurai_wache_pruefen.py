# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer samurai_wache.entscheide (19.10. 20:10). Vorher festgelegt:
  1. Hauptmenue (Ansicht 41), kein Lenker -> warten
  2. Gefecht laeuft, Ratte auf Spieler 2 -> starten Spieler 2
  3. Gefecht laeuft, keine Ratte (Schlange 2, Wolf 4) -> warten
  4. Gefecht laeuft, Lenker laeuft schon -> warten (kein zweiter)
  5. Gefecht verlassen (Ansicht 41), Lenker laeuft -> beenden
  6. Partie schon bedient, Lenker abgestuerzt, Gefecht laeuft weiter -> warten (kein Neustart im Kreis)
  7. Partie bedient, zurueck im Menue, Lenker aus -> neue_partie_frei
  8. Ratten auf Spieler 3 und 5 -> starten Spieler 3 (die erste)
  9. Gefecht vorbei (gameOver 1), Lenker laeuft -> beenden
Gegenprobe: uv run python -m selfaware.tools.checks.samurai_wache_pruefen alt  (RATTE = Schlange) -> 2, 3 und 8 rot."""
import os
import sys


import selfaware.runtime.live.samurai_wache as W

if len(sys.argv) > 1 and sys.argv[1] == "alt":
    W.RATTE = 2


def main():
    ok = []

    def pruefe(nr, text, ist, soll):
        ok.append(ist == soll)
        print("%-4s %d %s: %s (soll %s)" % ("OK" if ist == soll else "ROT", nr, text, ist, soll), flush=True)

    keine = {sp: 0 for sp in range(1, 9)}
    ratte2 = {**keine, 2: 1}
    pruefe(1, "Hauptmenue", W.entscheide(41, 0, keine, False, False), ("warten", None))
    pruefe(2, "Ratte auf 2", W.entscheide(14, 0, ratte2, False, False), ("starten", 2))
    pruefe(3, "keine Ratte", W.entscheide(14, 0, {**keine, 2: 2, 3: 4}, False, False), ("warten", None))
    pruefe(4, "Lenker laeuft", W.entscheide(14, 0, ratte2, True, True), ("warten", None))
    pruefe(5, "Gefecht verlassen", W.entscheide(41, 0, ratte2, True, True), ("beenden", None))
    pruefe(6, "abgestuerzt, Partie laeuft", W.entscheide(14, 0, ratte2, False, True), ("warten", None))
    pruefe(7, "zurueck im Menue", W.entscheide(41, 0, keine, False, True), ("neue_partie_frei", None))
    pruefe(8, "Ratten auf 3 und 5", W.entscheide(14, 0, {**keine, 3: 1, 5: 1}, False, False), ("starten", 3))
    pruefe(9, "Gefecht vorbei", W.entscheide(14, 1, ratte2, True, True), ("beenden", None))
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
