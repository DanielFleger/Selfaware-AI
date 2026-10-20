# -*- coding: utf-8 -*-
"""Burggraben planen wie ein Mensch - Spielbefehl 21 im Spiel pruefen (18.10., Daniel 23:38 "ja such den Grabbefehl fuer den
Burggraben").

Abgelesen (research/native/dekomp_graben_setzen.c, dekomp_graben.c):
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
Ausheben (logik.lua 19.10.: angriff mit "graben": [x, y] = Befehl 36 Art 6), Modus "ausheben":
  4. Block A geplant, bis zu 4 grabfaehige eigene Einheiten (sonst 4 Test-Sklaven, setzeEinheit) bekommen "graben" auf A
     -> nach hoechstens 90 s ist in A mindestens 1 Feld ausgehoben (LogicLayer 0x40000000)
  5. Gegenprobe: danach "Halt" an die Graeber, DANN Block B planen (ohne Graeber) -> 60 s lang 0 Felder ausgehoben.
     KORREKTUR 19.10.: zuerst B gleichzeitig mit A geplant - die Graeber gruben nach A von selbst in B weiter (4, dann 8
     Felder; abgelesen: findNearestFriendlyMoatTileForDigging sucht das naechste geplante Grabenfeld des Spielers)
Aufruf (Spiel laeuft, Lenker aus): SHC_INSTANZ=4 uv run python -m selfaware.tools.experiments.graben_pruefen ["<Spielstand>"] [ausheben]"""
import os
import re
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))

from selfaware.game.ucp.laden import befehl, lade_stand, peek
from selfaware.tools.experiments.mauer_pruefen import feld
from selfaware.game.ucp.steuerkarte import tick

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
    stand = [a for a in sys.argv[1:] if a != "ausheben"]
    if stand:
        from selfaware.tools.experiments.serie import zuruecksetzen
        print("Zuruecksetzen:", zuruecksetzen(), flush=True)
        print("geladen bei Tick", lade_stand(stand[0], mit_bild=False), flush=True)
        # 19.10. (00:11, Daniel sah den Endbildschirm): ohne eigenerPlatz erklaert das Spiel die geladene Partie fuer beendet
        befehl({"eigenerPlatz": SP}, 0.8)
    if "ausheben" in sys.argv[1:]:
        return ausheben()
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


GRAEBER = (24, 25, 26, 71, 30, 22)       # Speer, Pike, Streitkolben, Sklave, Ingenieur, (Kreuzfahrer-)Bogen
GEGRABEN = L_MOAT


def freie_bloecke(n, mitte, abstand=8):
    z = " ".join(befehl({"platzsuche": {"spieler": SP, "mapper": 51, "groesse": 3, "x": mitte[0], "y": mitte[1], "r": 20,
                                        "max": 40}}, 1.0, bis="PLATZSUCHE"))
    frei = [tuple(map(int, q)) for q in re.findall(r"\((\d+),(\d+)\)", z.split("geprueft:")[-1])]
    aus = []
    for q in frei:
        m = (q[0] + 1, q[1] + 1)
        if all(max(abs(m[0] - o[0]), abs(m[1] - o[1])) >= abstand for o in aus):
            aus.append(m)
        if len(aus) == n:
            break
    return aus


def gegraben(m):
    return sum(1 for xx in range(m[0] - 1, m[0] + 2) for yy in range(m[1] - 1, m[1] + 2) if feld(xx, yy)["logik"] & GEGRABEN)


def ausheben():
    from selfaware.tools.experiments.editor_messen import lage, setze
    befehl({"pause": False}, 0.5)
    lord = [tuple(map(int, m)) for m in re.findall(r"LORD \d+: Spieler 1 bei \((\d+),(\d+)\)",
                                                    " ".join(befehl({"lords": True}, 1.0, bis="LORDS")))]
    bloecke = freie_bloecke(2, (lord[0][0] + 12, lord[0][1] + 12))
    if len(bloecke) < 2:
        raise SystemExit("keine zwei freien 3x3 bei der Burg: %s" % bloecke)
    a, b = bloecke
    plane(a[0], a[1], 0)
    t, L = lage()
    eigen = sorted((n for n, e in L.items() if e["besitzer"] == SP and e["typ"] in GRAEBER),
                   key=lambda n: max(abs(L[n]["x"] - a[0]), abs(L[n]["y"] - a[1])))[:4]
    if len(eigen) < 3:
        eigen = [setze(SP, 71, a[0] + 3, a[1] + 3 + i) for i in range(4)]
        time.sleep(0.5)
        print("Test-Sklaven gesetzt:", eigen, flush=True)
    else:
        print("eigene Graeber:", [(n, L[n]["typ"], L[n]["x"], L[n]["y"]) for n in eigen], flush=True)
    z = befehl({"angriff": {"einheiten": eigen, "graben": [a[0], a[1]]}}, 1.5, bis="ANGRIFF")
    print("Modul:", [l for l in z if "ANGRIFF" in l][-1:], flush=True)
    ok = []

    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text), flush=True)

    verlauf, ende = [], time.time() + 90
    while time.time() < ende:
        verlauf.append((tick(), gegraben(a)))
        if verlauf[-1][1] >= 9:
            break
        time.sleep(3)
    pruefe(4, "Block A %s mit Graebern: ausgehoben %d von 9 (Verlauf Tick/A %s)" % (a, verlauf[-1][1], verlauf[::3]),
           verlauf[-1][1] >= 1)
    befehl({"angriff": {"einheiten": eigen}}, 1.5, bis="ANGRIFF")          # Halt (Art 31)
    time.sleep(3)
    plane(b[0], b[1], 0)
    t0, ende, gb = tick() or 0, time.time() + 60, 0
    while time.time() < ende:
        gb = gegraben(b)
        if gb:
            break
        time.sleep(5)
    pruefe(5, "nach Halt geplanter Block B %s ohne Graeber: ausgehoben %d nach %d Ticks" % (b, gb, (tick() or 0) - t0), gb == 0)
    befehl({"pause": True}, 0.5)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
