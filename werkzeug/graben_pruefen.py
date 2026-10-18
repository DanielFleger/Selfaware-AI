# -*- coding: utf-8 -*-
"""Burggraben planen wie ein Mensch - Spielbefehl 21 im Spiel pruefen (18.10., Daniel 23:38 "ja such den Grabbefehl fuer den
Burggraben").

Abgelesen (daten/dekomp_graben_setzen.c, dekomp_graben.c):
  - Befehl 21 ClickSetTerrain: x (2 Byte), y (2), Pinsel (1), Flag 1 (4), Flag 2 (1) -> TileMapState::setTerrain fuer den
    Absender. Flag 1 = L_MOAT (0x40000000): Pinsel egal, immer 9 Felder (3x3); Flag 2 = L2_NONE (0) plant (LogicLayer-Bit
    0x4000 L_MOAT_DUG_OR_PLANNED, createMoatData mit Besitzer), L2_SCRUB (1) loescht die Planung.
  - VERBOTEN: Flag 2 = L2_EARTH_AND_STONES (2) legt SOFORT einen fertig ausgehobenen Graben an (Editorweg, kein Graeber,
    keine Kosten) - wird hier und im Lenker nie gesendet (Daniel: keine kostenlosen Bauten).
  - Planen nur auf leerem Boden (kein Baum, Gebaeude, Mauer, Wasser, Fluss, Furt, Fels, Eisen, Pech, Feld), Hoehe < 13,
    kein Feind naeher als 15 Felder, kein feindliches Gebaeude naeher als 7 (+ Burgbereich).
  - Ausheben: Befehl 36 mit Art 6 (UIT_DIG_MOAT) und Ziel x, y (AICState::digNearestMoat -> giveTribeAnInstruction);
    graben koennen Streitkolben, Kreuzfahrer-Bogen, Sklaven, Pikeniere, Speertraeger, Ingenieure (advanceMoatDigProgress).
Vorher festgelegt (Totschlagtest):
  1. Befehl 21 (Flag 1 L_MOAT, Flag 2 = 0) auf ein freies 3x3 nahe der eigenen Burg -> die 9 Felder tragen Bit 0x4000
  2. Gegenprobe: derselbe Befehl mit Flag 2 = 1 (loeschen) -> kein Feld traegt das Bit mehr
  3. Holz, Stein, Gold nehmen nicht ab (Graben kostet im Gefecht nichts, nur Arbeit) - KORREKTUR 18.10.: zuerst
     "unveraendert" verlangt; das Spiel laeuft beim Test, Steuern brachten +28 Gold -> "nimmt nicht ab"
Aufruf (Spiel laeuft, Lenker aus): SHC_INSTANZ=4 python werkzeug/graben_pruefen.py ["<Spielstand>"]"""
import os
import re
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
from laden import befehl, lade_stand, peek
from mauer_pruefen import feld
from steuerkarte import tick

L_MOAT, GEPLANT = 0x40000000, 0x4000
SP = 1
PD = 0x0115BDF8


def waren():
    b = PD + SP * 0x39F4
    return {"holz": peek(b + 0x4D0 + 8)[0], "stein": peek(b + 0x4D0 + 16)[0], "gold": peek(b + 0x50C)[0]}


def plane(x, y, flag2):
    assert flag2 in (0, 1), "nur planen (0) oder loeschen (1) - 2 waere ein kostenloser fertiger Graben"
    befehl({"player": SP, "spielbefehl": {"nr": 21, "werte": [x, y, 0, L_MOAT, flag2]}}, 1.0, bis="SPIELBEFEHL")
    t0 = tick() or 0
    ende = time.time() + 5
    while time.time() < ende and (tick() or 0) < t0 + 2:
        time.sleep(0.1)


def bits(x, y, r=2):
    return {(xx, yy): bool(feld(xx, yy)["logik"] & GEPLANT) for xx in range(x - r, x + r + 1) for yy in range(y - r, y + r + 1)}


def main():
    if len(sys.argv) > 1:
        from serie import zuruecksetzen
        print("Zuruecksetzen:", zuruecksetzen(), flush=True)
        print("geladen bei Tick", lade_stand(sys.argv[1], mit_bild=False), flush=True)
    befehl({"pause": False}, 0.5)
    lord = [tuple(map(int, m)) for m in re.findall(r"LORD \d+: Spieler 1 bei \((\d+),(\d+)\)",
                                                    " ".join(befehl({"lords": True}, 1.0, bis="LORDS")))]
    if not lord:
        raise SystemExit("kein Lord von Spieler 1")
    z = " ".join(befehl({"platzsuche": {"spieler": SP, "mapper": 51, "groesse": 3, "x": lord[0][0] + 12, "y": lord[0][1] + 12,
                                        "r": 15, "max": 8}}, 1.0, bis="PLATZSUCHE"))
    frei = [tuple(map(int, q)) for q in re.findall(r"\((\d+),(\d+)\)", z.split("geprueft:")[-1])]
    if not frei:
        raise SystemExit("kein freies 3x3 bei der Burg")
    mx, my = frei[0][0] + 1, frei[0][1] + 1          # Mitte des freien 3x3
    ok = []

    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text), flush=True)

    vorher_b, w0 = bits(mx, my), waren()
    plane(mx, my, 0)
    nach_b, w1 = bits(mx, my), waren()
    neu = sorted(k for k in nach_b if nach_b[k] and not vorher_b[k])
    pruefe(1, "Graben geplant um (%d,%d): %d Felder neu mit Bit 0x4000: %s" % (mx, my, len(neu), neu), len(neu) == 9)
    plane(mx, my, 1)
    weg_b = bits(mx, my)
    rest = sorted(k for k in weg_b if weg_b[k] and not vorher_b[k])
    pruefe(2, "geloescht: noch geplant %s" % rest, not rest)
    w2 = waren()
    pruefe(3, "Waren vorher %s, nach Planen %s, nach Loeschen %s" % (w0, w1, w2),
           all(w1[k] >= w0[k] and w2[k] >= w0[k] for k in ("stein", "gold")))
    befehl({"pause": True}, 0.5)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
