# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer partner.py (18.10., 1v1 robust). Vorher festgelegt:
  1. Spieler 1 meldet "regelbruch" -> Spieler 2 liest genau diese Meldung (Art, Tick); neu_vom_partner liefert sie EINMAL
  2. erste Meldung gilt: nach "regelbruch" schreibt ein spaeterer "absturz" nichts mehr
  3. eine Ende-Datei aelter als der Prozessstart (frueherer Lauf) zaehlt nicht
  4. anhalten: wer zuerst aufhoert, haelt NICHT an; wer als Zweiter aufhoert (oder Partie vorbei), haelt an
  5. Serie: Fehler 29 s nach der letzten vollstaendigen Runde -> weiter; 31 s -> aufgeben; nach einer guten Runde wieder
     weiter; erste Art "erstes" True, Wiederholung False; Bericht zaehlt 3 Fehler
  6. Stillstand: 10 s warten; 30 s mit Partner fortsetzen, nach 3 Versuchen Abbruch; ohne Partner Abbruch wie bisher
Gegenprobe: mit "alt" wird das alte Verhalten nachgestellt (jeder Abbruch haelt an, jeder Fehler bricht ab, Stillstand bricht
ab) -> Faelle 4, 5 und 6 rot.
Aufruf: uv run python -m selfaware.tools.checks.partner_pruefen [alt]"""
import os
import sys
import tempfile
import time

HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.runtime.live.partner as P

if len(sys.argv) > 1 and sys.argv[1] == "alt":
    P.Ende.anhalten_erlaubt = lambda self, vorbei=False: True
    _alt_fehler = P.Serie.fehler
    P.Serie.fehler = lambda self, ex, runde=None, tick=None: (lambda z: (z[0], True, z[2]))(_alt_fehler(self, ex, runde, tick))
    P.stillstand = lambda s, v, p: "warten" if s < 30 else "abbruch"


def wirf(text):
    try:
        raise RuntimeError(text)
    except RuntimeError as ex:
        return ex


def main():
    ok = []

    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))

    ordner = tempfile.mkdtemp(prefix="partner_pruefen_")
    start = time.time()
    e1, e2 = P.Ende(ordner, 4, 1, start), P.Ende(ordner, 4, 2, start)
    e1.melde("regelbruch", "Beliebtheit 48.25 unter 50", 9002)
    m = e2.partner()
    n1, n2 = e2.neu_vom_partner(), e2.neu_vom_partner()
    pruefe(1, "Spieler 2 liest %s; einmal %s, zweimal %s" % (m and (m["art"], m["tick"]), bool(n1), bool(n2)),
           m and m["art"] == "regelbruch" and m["tick"] == 9002 and m["sp"] == 1 and n1 and n2 is None)
    e1.melde("absturz", "Folgefehler", 9010)
    m2 = e2.partner()
    pruefe(2, "nach spaeterem Absturz steht in der Datei: %s" % (m2 and m2["art"]), m2 and m2["art"] == "regelbruch")
    alt_ordner = tempfile.mkdtemp(prefix="partner_pruefen_alt_")
    a1 = P.Ende(alt_ordner, 4, 1, start - 3600)
    a1.melde("absturz", "frueherer Lauf", 5)
    os.utime(P.ende_datei(alt_ordner, 4, 1), (start - 600, start - 600))
    pruefe(3, "Ende-Datei vor dem Prozessstart: %s" % P.Ende(alt_ordner, 4, 2, start).partner(),
           P.Ende(alt_ordner, 4, 2, start).partner() is None)
    o4 = tempfile.mkdtemp(prefix="partner_pruefen_4_")
    f1, f2 = P.Ende(o4, 4, 1, start), P.Ende(o4, 4, 2, start)
    f1.melde("regelbruch", "x", 100)
    zuerst = f1.anhalten_erlaubt()
    vorbei = f1.anhalten_erlaubt(vorbei=True)
    f2.melde("ende", "Sieg durch Regelbruch", 101)
    zweiter = f2.anhalten_erlaubt()
    pruefe(4, "erster haelt an: %s, mit Partie vorbei: %s, zweiter haelt an: %s" % (zuerst, vorbei, zweiter),
           not zuerst and vorbei and zweiter)
    jetzt = [1000.0]
    s = P.Serie(uhr=lambda: jetzt[0])
    jetzt[0] = 1029.0
    _, auf29, erstes = s.fehler(wirf("a"), 1, 10)
    jetzt[0] = 1031.0
    _, auf31, erstes2 = s.fehler(wirf("a"), 2, 11)
    s.gut()
    jetzt[0] = 1032.0
    z, auf_nach, _ = s.fehler(wirf("b"), 3, 12)
    pruefe(5, "29 s: aufgeben %s, 31 s: %s, nach guter Runde: %s; erstes %s/%s; %s" % (
        auf29, auf31, auf_nach, erstes, erstes2, s.bericht()),
           not auf29 and auf31 and not auf_nach and erstes and not erstes2 and s.gesamt == 3 and "naechste Runde" in z)
    st = [P.stillstand(10, 0, True), P.stillstand(30, 0, True), P.stillstand(30, 2, True), P.stillstand(30, 3, True),
          P.stillstand(30, 0, False)]
    pruefe(6, "Stillstand 10/30/30(2)/30(3)/ohne Partner: %s" % st,
           st == ["warten", "fortsetzen", "fortsetzen", "abbruch", "abbruch"])
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
