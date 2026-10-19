# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer endspurt.py und den Endspurt im Feldzug (19.10.). Vorher festgelegt:
  1. Nachspiel 1018i/j/k Runde fuer Runde, je Spieler nur sein eigenes Lageprotokoll und seine Ertragsdatei (wie im Spiel):
     beim Verlierer (Spieler 2) zuendet der Endspurt zwischen Tick 18.000 und 35.000, beim Sieger (Spieler 1) nie
     (UEBERSPRUNGEN, wenn die Dateien fehlen)
  2. Feldzug, 20 Schwertkaempfer, 10 am Sammelpunkt, Gefechtsrechnung sagt "lohnt nicht": ohne Endspurt bleibt er beim
     Sammeln; mit Endspurt greift er an; mit Endspurt und nur 9 von 20 am Punkt bleibt er beim Sammeln
  3. Werbung: 1.050 Gold / 20 am Feuer -> 10; 1.050 / 4 -> 4; 99 / 20 -> 0; (KORREKTUR 1018l) 1.050 / 20, Nahrung 5 bei
     Puffer 10 -> 0 (Gold bleibt fuer den Notkauf); Nahrung 30 bei Puffer 10 -> 10
  4. Lageprotokoll.schreibe gibt die beiden Rohtabellen zurueck, die es schreibt
Gegenprobe: mit "alt" ist die Schwelle 0, der Feldzug kennt keinen Endspurt, die Werbung zaehlt das Feuer nicht und
schreibe gibt nichts zurueck -> Faelle 1, 2, 3 und 4 rot.
Aufruf: uv run python -m selfaware.tools.checks.endspurt_pruefen [alt]"""

from selfaware import workspace as _workspace
import os
import sys
import tempfile

HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.strategy.endspurt as ES
import selfaware.micro.tasks.feldzug as FZ
import selfaware.telemetry.lageprotokoll as LP

ALT = len(sys.argv) > 1 and sys.argv[1] == "alt"
if ALT:
    ES.SCHWELLE = 0.0
    ES.schwertkaempfer = lambda gold, feuer, nahrung=None, puffer=None: max(0, int(gold) // ES.SCHWERT_GOLD)
    _sammeln = FZ.Feldzug.schritt

    def _ohne_endspurt(self, *a, **k):
        self.endspurt = False
        return _sammeln(self, *a, **k)
    FZ.Feldzug.schritt = _ohne_endspurt
    _schreibe = LP.Lageprotokoll.schreibe
    LP.Lageprotokoll.schreibe = lambda self, st: (_schreibe(self, st), None)[1]

D = os.path.join(_workspace.DATA)
LAEUFE = {"1018i": ("20261019_110344", "20261019_110345"), "1018j": ("20261019_121535", "20261019_121535"),
          "1018k": ("20261019_164522", "20261019_164522")}


def nachspiel(stempel, sp):
    lage = os.path.join(D, "lage_%s_i4%s.jsonl.gz" % (stempel, "" if sp == 1 else "_sp2"))
    ertrag = os.path.join(D, "ertrag_live_%s_i4%s.jsonl" % (stempel, "" if sp == 1 else "_sp2"))
    if not (os.path.exists(lage) and os.path.exists(ertrag)):
        return "fehlt"
    es = ES.Endspurt(sp, ertrag)
    for t, st, E, G in LP.runden(lage):
        es.runde_tabellen(t, st, E, G)
        if es.lauf.vorbei is not None:
            break
        es.pruefen(t)
        if es.aktiv:
            return es.aktiv_seit
    return None


def feldzug_fall(endspurt, am_punkt):
    f = FZ.Feldzug(1, (10, 10), 0, n=30)
    f._lohnt = lambda L, da, lord: (False, "")
    f.endspurt = endspurt
    f.punkt = (50, 50)
    f.runde = 1                        # kein Neuberechnen des Sammelpunkts (runde % 20)
    L = {100: {"typ": FZ.LORD, "besitzer": 2, "leben": 150000, "x": 200, "y": 200, "zustand": 0}}
    for i in range(20):
        ort = (50, 50) if i < am_punkt else (20, 20)
        L[i + 1] = {"typ": 75, "besitzer": 1, "leben": 28000, "x": ort[0], "y": ort[1], "zustand": 0}
    f.schritt({"t": 20000}, L, {}, lambda *a, **k: [])
    return f.phase


def main():
    ok = []

    def pruefe(nr, text, bed):
        ok.append(bool(bed))
        print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text), flush=True)

    erg = {(n, sp): nachspiel(s[sp - 1], sp) for n, s in LAEUFE.items() for sp in (1, 2)}
    if any(v == "fehlt" for v in erg.values()):
        print("UEBERSPRUNGEN 1 (Dateien fehlen: %s)" % [k for k, v in erg.items() if v == "fehlt"])
    else:
        pruefe(1, "Nachspiel - Endspurt bei Tick: %s" % {"%s Sp%d" % k: v for k, v in sorted(erg.items())},
               all(erg[(n, 1)] is None for n in LAEUFE) and all(erg[(n, 2)] is not None and 18000 <= erg[(n, 2)] <= 35000 for n in LAEUFE))

    a, b, c = feldzug_fall(False, 10), feldzug_fall(True, 10), feldzug_fall(True, 9)
    pruefe(2, "Feldzug: ohne Endspurt %s, mit Endspurt %s, mit Endspurt und 9 von 20 %s" % (a, b, c),
           a == "sammeln" and b == "angriff" and c == "sammeln")

    w = (ES.schwertkaempfer(1050, 20), ES.schwertkaempfer(1050, 4), ES.schwertkaempfer(99, 20),
         ES.schwertkaempfer(1050, 20, 5, 10), ES.schwertkaempfer(1050, 20, 30, 10))
    pruefe(3, "Werbung 1050/20, 1050/4, 99/20, Nahrung 5 von 10, Nahrung 30 von 10: %s" % (w,), w == (10, 4, 0, 0, 10))

    import selfaware.micro.tasks.waechter as waechter
    tmp = tempfile.mkdtemp()
    e_pfad, g_pfad = os.path.join(tmp, "lagebild.txt"), os.path.join(tmp, "gebaeude.txt")
    open(e_pfad, "w").write("tick 5\nnr besitzer typ x y leben\n1 1 75 5 5 28000\n")
    open(g_pfad, "w").write("nr besitzer typ x y leben uid erreichbar vorrat grenze verbund ware\n1 1 41 9 9 0 7 1 0 0 0 0\n")
    alt_e, alt_g = waechter.LAGEBILD, waechter.GEBAEUDEDATEI
    waechter.LAGEBILD, waechter.GEBAEUDEDATEI = e_pfad, g_pfad
    try:
        roh = LP.Lageprotokoll(os.path.join(tmp, "lage.jsonl.gz")).schreibe({"t": 5})
    finally:
        waechter.LAGEBILD, waechter.GEBAEUDEDATEI = alt_e, alt_g
    tab = (LP._tabelle(roh[0], 1), LP._tabelle(roh[1], 0)) if roh else None
    pruefe(4, "schreibe gibt zurueck: %s" % (tab,), tab and tab[0][0]["typ"] == 75 and tab[1][0]["typ"] == 41)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
