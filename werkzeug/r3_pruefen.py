# -*- coding: utf-8 -*-
"""B-287 Pruefung R3 "Haken beim Schuss" (Plan_Takt_Kern.md, R3 nach Frage-Agent gelb 02:14).

Testaufbau (nur Testgefecht): ein frisches Gefecht auf SHC_INSTANZ, Kern ab Version 24. Eigene Speertraeger (an den Kern),
feindliche Armbrueste 15 Felder und Bogenschuetzen 32 Felder daneben. R1 aus, R3 im Modus "Versuch": je Pfeil entscheidet die
UID (gerade = Haken, ungerade = nur zaehlen) - Vergleichsgruppe im selben Gefecht. Alle LOCK_S Sekunden gehen die
Speertraeger ueber den Kern zurueck in die Linie; faellt ihre Zahl unter die Haelfte, kommen neue dazu.

Vorher festgelegt (Soll): bei Pfeilen mit >= 12 Resttakten bis zur Einheit liegt die Trefferquote mit Haken mindestens ein
Drittel unter der Vergleichsgruppe, bei >= 60 Pfeilen je Gruppe. Jeder Haken-Befehl kommt im Spiel an (<= 1 Takt).
Aufruf: SHC_INSTANZ=5 python werkzeug/r3_pruefen.py [sekunden] [kern-dll]"""
import os
import re
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
os.environ.setdefault("SHC_INSTANZ", "5")
import shc
from laden import befehl
from r1_pruefen import frische_partie, kern_log, lagebild, nummern

N, LOCK_S = 12, 8
EIGEN = (190, 262)
ARMBRUST = (205, 262)
BOGEN = (222, 262)
FEIND_SP = "2"         # Gegner-KI wird im Testgefecht abgeschaltet (ki_aus_testgefecht) - sie fuehrte die Schuetzen sonst weg (02:20);
                      # Spieler 3 ist kein Feind (seine Schuetzen standen untaetig, 02:22)
GRENZE = 12           # Resttakte, ab denen Ausweichen physikalisch moeglich sein kann (Plan)


def auswerten(zeilen):
    erg = {}
    for z in zeilen:
        m = re.search(r"R3 ERGEBNIS Geschoss \d+ Einheit \d+ - (GETROFFEN|verfehlt) \(Haken (ja|nein), Resttakte (-?\d+)", z)
        if m:
            band = "weit" if int(m.group(3)) >= GRENZE else "nah"
            k = (m.group(2), band)
            t, n = erg.get(k, (0, 0))
            erg[k] = (t + (m.group(1) == "GETROFFEN"), n + 1)
    ank = [int(m.group(1)) for m in (re.search(r"R1 ANGEKOMMEN .*\(\+(\d+) Takte\)", z) for z in zeilen) if m]
    haken = sum("R3 HAKEN Gruppe" in z for z in zeilen)
    nicht = sum("NICHT ANGEKOMMEN" in z for z in zeilen)
    return erg, ank, haken, nicht


def main():
    sek = int(sys.argv[1]) if len(sys.argv) > 1 else 180
    kern = sys.argv[2] if len(sys.argv) > 2 else "samurai_kern_26.dll"
    frische_partie(kern)                 # schaltet auch die KI von Spieler 2 aus
    befehl({"kern": {"lauf": {"x": 0, "y": 0, "einheiten": [-1]}}}, 1.0, bis="KERN")      # R1 aus
    befehl({"kern": {"lauf": {"x": 2, "y": 0, "einheiten": [-2]}}}, 1.0, bis="KERN")      # R3 Versuch je Pfeil
    eigene = nummern(shc.setze("1", "24", str(EIGEN[0]), str(EIGEN[1]), str(N)))
    shc.setze(FEIND_SP, "23", str(ARMBRUST[0]), str(ARMBRUST[1]), "4")
    shc.setze(FEIND_SP, "22", str(BOGEN[0]), str(BOGEN[1]), "4")
    befehl({"kern": {"uebernehmen": eigene}}, 1.5, bis="KERN")
    log = kern_log()
    start = sum(1 for _ in open(log, encoding="utf-8", errors="replace"))
    befehl({"pause": False}, 0.5)
    ende = time.time() + sek
    nachschub = 0
    while time.time() < ende:
        time.sleep(LOCK_S)
        befehl({"pause": True}, 0.5)
        L = lagebild()
        leben = [n for n in eigene if n in L and L[n]["besitzer"] == 1 and L[n]["typ"] == 24]
        if len(leben) < N // 2:
            neu = nummern(shc.setze("1", "24", str(EIGEN[0]), str(EIGEN[1]), str(N - len(leben))))
            befehl({"kern": {"uebernehmen": neu}}, 1.5, bis="KERN")
            eigene = leben + neu
            nachschub += len(neu)
        else:
            eigene = leben
        befehl({"kern": {"lauf": {"x": EIGEN[0], "y": EIGEN[1], "einheiten": eigene}}}, 0.8)
        befehl({"pause": False}, 0.5)
    befehl({"pause": True}, 0.5)
    befehl({"kern": {"lauf": {"x": 1, "y": 0, "einheiten": [-1]}}}, 1.0, bis="KERN")      # R1 wieder an
    befehl({"kern": {"lauf": {"x": 1, "y": 0, "einheiten": [-2]}}}, 1.0, bis="KERN")      # R3 wieder an
    zeilen = open(log, encoding="utf-8", errors="replace").read().splitlines()[start:]
    erg, ank, haken, nicht = auswerten(zeilen)
    print("Nachschub %d Speertraeger, Haken-Befehle %d, angekommen %d (max +%s), NICHT ANGEKOMMEN %d" % (
        nachschub, haken, len(ank), max(ank) if ank else "-", nicht))
    for band in ("weit", "nah"):
        for h in ("ja", "nein"):
            t, n = erg.get((h, band), (0, 0))
            print("  %s (Resttakte %s %d), Haken %-4s: %3d Pfeile, getroffen %3d = %s" % (
                band, ">=" if band == "weit" else "<", GRENZE, h, n, t, "%.0f %%" % (100.0 * t / n) if n else "-"))
    tj, nj = erg.get(("ja", "weit"), (0, 0))
    tn, nn = erg.get(("nein", "weit"), (0, 0))
    f = [("1 >= 60 Pfeile je Gruppe (weit)", nj >= 60 and nn >= 60),
         ("2 Trefferquote mit Haken >= ein Drittel niedriger (weit)", nj > 0 and nn > 0 and tj / nj <= (tn / nn) * 2 / 3),
         ("3 jeder Haken im Spiel angekommen, <= 1 Takt", haken > 0 and nicht == 0 and bool(ank) and max(ank) <= 1)]
    for name, ok in f:
        print("%s %s" % ("OK  " if ok else "ROT ", name))
    print("%d von %d gruen" % (sum(ok for _, ok in f), len(f)))


if __name__ == "__main__":
    main()
