# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer bierkette.py (Daniel 19.10.2026, 1019a: "wir haben sogar schon Bier und noch keine Schenke -
sobald das erste Bier geliefert ist, soll der erste Wirt losgehen koennen, um Bier zu holen").
Vorher festgelegt:
  1. (1019a) 1 Hopfenfarm, 1 Brauerei, 0 Schenken, 100 Einwohner, fuer Hopfen kein Platz -> diese Runde wird die SCHENKE
     bestellt (vorher: Hopfen "kein Platz", dann eine weitere Brauerei - die Schenke kam nie dran)
  2. 1 Hopfenfarm, 1 Brauerei, 1 Schenke -> keine zweite Brauerei vor der zweiten Hopfenfarm (Kette 1:1:1); Hopfen wird bestellt
  3. (1019a: der reservierte Hopfenplatz (52, 205), auf dem Hopfenfarm 1 stand, wurde alle 3.000 Ticks wieder versucht)
     reservierter Platz einmal versucht, 3.000 Ticks spaeter neue Platzliste -> der reservierte Platz kommt NICHT wieder
  4. (1019a: "kein Platz fuer Hopfenfarm" ab Tick 7.559 - im Umkreis 45 alles verbaut) im Umkreis 45 kein Hopfenplatz, im
     Umkreis 90 einer -> er wird genommen
  5. ein Bau scheitert (Spiel setzt nicht) -> in derselben Runde kommt das naechste Glied dran
  6. (1019b: das Wirtshaus scheiterte 7-mal an "fehlt stein 8") Schenke faellig, Stein 3 statt 10 -> kein Bauversuch,
     die Kette meldet 10 Stein Bedarf (der Lenker haelt ihn vom Verkauf zurueck)
Aufruf: uv run python -m selfaware.tools.checks.bierkette_pruefen [<alte bierkette.py>]   (Rueckgabe 0 = gruen)
"""
import importlib.util
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) > 1:
    spec = importlib.util.spec_from_file_location("bierkette", sys.argv[1])
    B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
else:
    import selfaware.macro.bierkette as B

ok = []


def pruefe(nr, text, bed):
    ok.append(bool(bed))
    print("%s %d %s" % ("OK  " if bed else "ROT ", nr, text))


def geb(typ, x, y, sp=1):
    return {"typ": typ, "besitzer": sp, "x": x, "y": y, "leben": 100}


def kette(hopfen, brauerei, schenke, plaetze, setzt=lambda typ: True):
    G = {1: geb(B.LAGER, 100, 100), 2: geb(B.KORNSPEICHER, 110, 100)}
    i = 10
    for typ, zahl in ((B.HOPFEN, hopfen), (B.BRAUEREI, brauerei), (B.SCHENKE, schenke)):
        for k in range(zahl):
            G[i] = geb(typ, 60 + 12 * k, 60 + typ); i += 1
    gebaut = []

    def baue(typ, x, y, r):
        gebaut.append((typ, (x, y)))
        return (x, y) if setzt(typ) else None
    b = B.Bierkette(1, baue, plaetze, lambda typ, ware: 10)
    return b, G, gebaut


ST = {"leute": 100, "feuer": 3, "holz": 500, "gold": 500, "stein": 500, "t": 10000}
RL = {"holz": 0, "gold": 0}


def main():
    # 1
    def pl1(typ, kern, r):
        return [] if typ == B.HOPFEN else [(kern[0] + 5, kern[1] + 5)]
    b, G, gebaut = kette(1, 1, 0, pl1)
    aus = b.schritt(ST, G, RL)
    pruefe(1, "1 Hopfen, 1 Brauerei, 0 Schenken, Hopfen ohne Platz: bestellt %s %s" % (gebaut, aus[-1:]),
           gebaut and gebaut[0][0] == B.SCHENKE)
    # 2
    b, G, gebaut = kette(1, 1, 1, lambda typ, kern, r: [(kern[0] + 5, kern[1] + 5)])
    b.schritt(ST, G, RL)
    pruefe(2, "1:1:1 steht: bestellt %s" % gebaut, gebaut and gebaut[0][0] == B.HOPFEN and all(t != B.BRAUEREI for t, _ in gebaut))
    # 3: das Spiel meldet nur freie Plaetze; jeder Bau gelingt und steht ab der naechsten Runde
    G3 = {}

    def pl3(typ, kern, r):
        belegt = {(g["x"], g["y"]) for g in G3.values()}
        alle = [(150 + 12 * i, 150) for i in range(8)] if typ == B.HOPFEN else [(kern[0] + 5 + 12 * i, kern[1] + 5) for i in range(8)]
        return [p for p in alle if p not in belegt]
    b, G, gebaut = kette(0, 0, 0, pl3)
    G3.update(G)
    b.reserviert = [(52, 205)]
    t = 10000
    for runde in range(16):
        vorher = len(gebaut)
        b.schritt(dict(ST, t=t), G3, RL)
        for typ, p in gebaut[vorher:]:
            G3[1000 + len(G3)] = geb(typ, p[0], p[1])
        t += 700
    pruefe(3, "16 Runden ueber 11.000 Ticks: reservierter Platz (52, 205) %d-mal bestellt, Hopfen gesamt %d" % (
        sum(1 for typ, p in gebaut if p == (52, 205)), sum(1 for typ, _ in gebaut if typ == B.HOPFEN)),
        sum(1 for typ, p in gebaut if p == (52, 205)) == 1)
    # 4
    def pl4(typ, kern, r):
        if typ == B.HOPFEN:
            return [(180, 180)] if r >= 90 else []
        return [(kern[0] + 5, kern[1] + 5)]
    b, G, gebaut = kette(0, 0, 0, pl4)
    b.schritt(ST, G, RL)
    pruefe(4, "Hopfen erst im Umkreis 90: bestellt %s" % gebaut, gebaut and gebaut[0] == (B.HOPFEN, (180, 180)))
    # 5
    b, G, gebaut = kette(1, 1, 0, lambda typ, kern, r: [(kern[0] + 5, kern[1] + 5)], setzt=lambda typ: typ != B.SCHENKE)
    b.schritt(ST, G, RL)
    pruefe(5, "Schenke scheitert: in derselben Runde bestellt %s" % gebaut,
           len(gebaut) >= 2 and gebaut[0][0] == B.SCHENKE and gebaut[1][0] == B.HOPFEN)
    # 6
    b, G, gebaut = kette(1, 1, 0, lambda typ, kern, r: [(kern[0] + 5, kern[1] + 5)])
    b.schritt(dict(ST, stein=3), G, RL)
    sb = b.stein_bedarf() if hasattr(b, "stein_bedarf") else None
    pruefe(6, "Schenke faellig, 3 Stein (braucht 10): bestellt %s, Steinbedarf gemeldet %s" % (gebaut, sb), not gebaut and sb == 10)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
