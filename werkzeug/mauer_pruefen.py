# -*- coding: utf-8 -*-
"""Mauern bauen wie ein Mensch - Spielbefehl 25 im Spiel pruefen (18.10., Daniel: "bau den Kornspeicher ein bis auf die Ecken",
"jetzt braucht es Burggraeben, Mauern, gute Defence").

Abgelesen (daten/dekomp_mauer_setzen.c, dekomp_placeWalls.c): Befehl 25 ClickPlaceWall nimmt x1, y1, x2, y2 (je 2 Byte),
Mauerart (Mapper, 1 Byte) und Kachelzahl (2 Byte) und ruft TileMapState::placeWalls(Spieler, ...): validateWallBuildPath,
Laenge begrenzt durch getWallTilesThatCanBeBuilt (was der Spieler bezahlen kann), Preis ueber processWallBuildingLoss
(Steinmauern und Holzmauern getrennt gezaehlt).

Vorher festgelegt (Totschlagtest):
  1. Steinmauer (Mapper 25), 4 Kacheln in einer freien Reihe neben dem eigenen Kornspeicher -> alle 4 Kacheln tragen
     Mauerbit 0x100, Besitzer-Ebene = Spieler - 1, Stein sinkt (Preis je Kachel wird gemessen, nicht angenommen)
  2. Niedrige Mauer (Mapper 46), 4 Kacheln in der Reihe darunter -> Mauerbit 0x100 und 0x10000, Stein sinkt, Holz nicht
     (KORREKTUR 18.10.: zuerst "Holz sinkt" erwartet - nur aus dem Namen M_MAPPER_WOODWALL geschlossen; gemessen kostet
     sie Stein: 4 Kacheln 1 Stein, Holz unveraendert, Spielstand "Gute Wirtschaft")
  3. Gegenprobe der Pruefung: derselbe Befehl mit Kachelzahl 0 an einer dritten freien Reihe -> KEINE Mauerkachel
     (sonst zaehlt die Pruefung etwas anderes als den Befehl)
Aufruf (Spiel laeuft, Lenker aus): SHC_INSTANZ=4 python werkzeug/mauer_pruefen.py ["<Spielstand>"]"""
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
from laden import peek, befehl, lade_stand
from steuerkarte import tick

LOGIK, BESITZER, HOEHE = 0x01BF8368, 0x01D5A058, 0x01D32C38
PD = 0x0115BDF8
SP = 1


def kachel(x, y):
    return peek(0x023372F8 + y * 12 + 8)[0] + x


def byte_an(basis, k):
    adr = basis + k
    return (peek(adr & ~3)[0] >> ((adr & 3) * 8)) & 0xFF


def feld(x, y):
    k = kachel(x, y)
    return {"logik": peek(LOGIK + 4 * k)[0], "besitzer": byte_an(BESITZER, k), "hoehe": byte_an(HOEHE, k)}


def ware(nr):
    return peek(PD + SP * 0x39F4 + 0x4D0 + nr * 4)[0]


FREI_NICHT = 0x01 | 0x02 | 0x30 | 0x100 | 0x200 | 0x400 | 0x800 | 0x1000 | 0x20000 | 0x4000 | 0x40000000


def reihe_frei(x0, y, n):
    return all(feld(x, y)["logik"] & FREI_NICHT == 0 for x in range(x0, x0 + n))


def setze(x1, y1, x2, y2, mapper, n):
    befehl({"player": SP, "spielbefehl": {"nr": 25, "werte": [x1, y1, x2, y2, mapper, n]}}, 1.0, bis="SPIELBEFEHL")
    t0 = tick() or 0
    ende = time.time() + 5
    while time.time() < ende and (tick() or 0) < t0 + 2:
        time.sleep(0.1)


def main():
    if len(sys.argv) > 1:
        print("geladen bei Tick", lade_stand(sys.argv[1], mit_bild=False), flush=True)
    befehl({"pause": False}, 0.5)
    from waechter import lies_gebaeude
    befehl({"lagebild": True}, 1.0)
    G = lies_gebaeude()
    speicher = [g for g in G.values() if g["besitzer"] == SP and g["typ"] == 19]
    if not speicher:
        raise SystemExit("kein Kornspeicher von Spieler %d - %d Gebaeude gelesen" % (SP, len(G)))
    gx, gy = speicher[0]["x"], speicher[0]["y"]
    # drei freie 4er-Reihen: ueber dem Kornspeicher nach oben suchen, sonst darunter
    reihen = [y for y in list(range(gy - 1, gy - 15, -1)) + list(range(gy + 4, gy + 18)) if reihe_frei(gx, y, 4)]
    print("Kornspeicher Spieler %d bei (%d,%d); freie Reihen x %d-%d: %s" % (SP, gx, gy, gx, gx + 3, reihen[:6]), flush=True)
    if len(reihen) < 3:
        raise SystemExit("zu wenig freie Reihen")
    ok = []

    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text), flush=True)

    y1, y2, y3 = reihen[:3]
    s0, h0 = ware(4), ware(2)
    setze(gx, y1, gx + 3, y1, 25, 4)
    f = [feld(x, y1) for x in range(gx, gx + 4)]
    s1, h1 = ware(4), ware(2)
    pruefe(1, "Steinmauer y=%d: Mauerbit %s, Besitzer %s, Hoehe %s; Stein %d -> %d, Holz %d -> %d" % (
        y1, [bool(q["logik"] & 0x100) for q in f], [q["besitzer"] & 7 for q in f], [q["hoehe"] for q in f], s0, s1, h0, h1),
           all(q["logik"] & 0x100 for q in f) and all((q["besitzer"] & 7) == SP - 1 for q in f) and s1 < s0)
    setze(gx, y2, gx + 3, y2, 46, 4)
    f2 = [feld(x, y2) for x in range(gx, gx + 4)]
    s2, h2 = ware(4), ware(2)
    pruefe(2, "Niedrige Mauer y=%d: Mauerbit %s, 0x10000 %s; Stein %d -> %d, Holz %d -> %d" % (
        y2, [bool(q["logik"] & 0x100) for q in f2], [bool(q["logik"] & 0x10000) for q in f2], s1, s2, h1, h2),
           all(q["logik"] & 0x100 for q in f2) and all(q["logik"] & 0x10000 for q in f2) and s2 < s1 and h2 >= h1)
    setze(gx, y3, gx + 3, y3, 25, 0)
    f3 = [feld(x, y3) for x in range(gx, gx + 4)]
    pruefe(3, "Gegenprobe Kachelzahl 0, y=%d: Mauerbit %s, Stein %d -> %d" % (
        y3, [bool(q["logik"] & 0x100) for q in f3], s2, ware(4)), not any(q["logik"] & 0x100 for q in f3))
    befehl({"pause": True}, 0.5)
    if s1 < s0:
        print("PREIS Steinmauer: %.2f Stein je Kachel (4 Kacheln, %d Stein)" % ((s0 - s1) / 4.0, s0 - s1))
    if s2 < s1:
        print("PREIS niedrige Mauer: %.2f Stein je Kachel (4 Kacheln, %d Stein)" % ((s1 - s2) / 4.0, s1 - s2))
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
