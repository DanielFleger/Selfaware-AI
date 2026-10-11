# -*- coding: utf-8 -*-
"""Gegenprobe Rueckzug nach Rechnung (Daniel 11.10. 16:11). Spielt die Entscheidung Runde fuer Runde ueber die beiden
gespielten Fruehstuerme nach und prueft gebaute Grenzfaelle. Soll vorher festgelegt:
  - echte Laeufe 1011a/b (Gegner-Lord starb 35 bzw. 8 Ticks nach unserem 50-%-Rueckzug): KEIN Rueckzug bis zu seinem Tod
  - hoffnungslos (wir verlieren schnell, er kaum): Rueckzug
  - am Boden: Rueckzug; zu kurze Reihe / kein Schaden am Gegner: alte 50-%-Regel
Aufruf: python rueckzug_pruefen.py"""
import glob
import os

from lageprotokoll import runden
from lord_sturm import rueckzug_rechnung, BODEN

DATEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten")
LORD_MAX = 150000


def nachspielen(pfad):
    """Erster Tick, an dem die Rechnung den Rueckzug verlangt haette (None = nie), und Tick seines Todes."""
    verlauf, tod = [], None
    for t, st, E, G in runden(pfad):
        g = next((e for e in E if e["typ"] == 55 and e["besitzer"] == 2), None)
        w = next((e for e in E if e["typ"] == 55 and e["besitzer"] == 1), None)
        if g is None or g["leben"] <= 0:
            tod = t
            break
        if w is None:
            break
        verlauf.append((t, g["leben"], w["leben"]))
        zurueck, grund = rueckzug_rechnung(verlauf, LORD_MAX)
        if zurueck:
            return t, grund, tod
    return None, "", tod


def main():
    ergebnisse = []
    for pfad in sorted(glob.glob(os.path.join(DATEN, "lage_20261011_16*_i4_sturm.jsonl.gz")))[:2]:
        rz, grund, tod = nachspielen(pfad)
        ok = rz is None
        ergebnisse.append(ok)
        print("%s %-45s Rueckzug %s %s" % ("OK  " if ok else "ROT ", os.path.basename(pfad) + ": kein Rueckzug bis zum Sieg",
                                           rz if rz else "nie", grund))
    reihe = lambda hp_g, r_g, hp_w, r_w, n=11: [(t, hp_g + r_g * (n - 1 - i) * 20, hp_w + r_w * (n - 1 - i) * 20)
                                                for i, t in enumerate(range(0, 20 * n, 20))]
    faelle = [
        ("hoffnungslos: er 20.000 (-10/Tick), wir 80.000 (-300/Tick)", reihe(20000, 10, 80000, 300), True),
        ("gut: er 6.000 (-50/Tick), wir 76.000 (-160/Tick)", reihe(6000, 50, 76000, 160), False),
        ("am Boden: wir %d" % BODEN, reihe(5000, 50, BODEN, 0), True),
        ("zu kurze Reihe, wir 45 %%", [(0, 30000, 67500), (40, 30000, 67500)], True),
        ("zu kurze Reihe, wir 60 %%", [(0, 30000, 90000), (40, 30000, 90000)], False),
        ("er verliert nichts, wir 60 %% fallend", reihe(30000, 0, 90000, 50), False),
        ("er verliert nichts, wir 45 %%, Boden in 950 Ticks", reihe(30000, 0, 67500, 50), False),
        ("er verliert nichts, wir 45 %%, Boden in 150 Ticks", reihe(30000, 0, 67500, 317), True),
        ("Kampfbeginn 1011a: er kaum Schaden, wir 147.000", reihe(30000, 1, 147000, 12), False),
    ]
    for name, verlauf, soll in faelle:
        ist, grund = rueckzug_rechnung(verlauf, LORD_MAX)
        ergebnisse.append(ist == soll)
        print("%s %-55s Rueckzug %s (%s)" % ("OK  " if ist == soll else "ROT ", name, ist, grund))
    print("%d von %d gruen" % (sum(ergebnisse), len(ergebnisse)))
    return 0 if all(ergebnisse) else 1


if __name__ == "__main__":
    raise SystemExit(main())
