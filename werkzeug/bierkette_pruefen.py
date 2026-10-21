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
  7. (B-151, Pruefstand 21.10.: 12 Schenke-Versuche, immer dieselben 2-3 Plaetze, jeder von der Laufweg-Pruefung
     gestrichen) die ersten 5 Plaetze der Liste sind belegt, der 6. frei -> die Schenke steht in DERSELBEN Runde auf dem
     6.; sind alle 12 Plaetze einer Runde belegt, nimmt die naechste Runde die Plaetze ab dem 13. (nicht wieder die ersten)
Aufruf: python werkzeug/bierkette_pruefen.py [<alte bierkette.py>]   (Rueckgabe 0 = gruen)
"""
import importlib.util
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
if len(sys.argv) > 1:
    spec = importlib.util.spec_from_file_location("bierkette", sys.argv[1])
    B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
else:
    import bierkette as B

ok = []


def pruefe(nr, text, bed):
    ok.append(bool(bed))
    print("%s %d %s" % ("OK  " if bed else "ROT ", nr, text))


def geb(typ, x, y, sp=1):
    return {"typ": typ, "besitzer": sp, "x": x, "y": y, "leben": 100}


def kette(hopfen, brauerei, schenke, plaetze, setzt=lambda typ: True, frei=lambda typ, p: True):
    G = {1: geb(B.LAGER, 100, 100), 2: geb(B.KORNSPEICHER, 110, 100)}
    i = 10
    for typ, zahl in ((B.HOPFEN, hopfen), (B.BRAUEREI, brauerei), (B.SCHENKE, schenke)):
        for k in range(zahl):
            G[i] = geb(typ, 60 + 12 * k, 60 + typ); i += 1
    gebaut = []

    def baue(typ, kand):
        # wie erstes_spiel.baue_aus_liste: der erste freie Platz wird gebaut, die davor sind geprueft
        for i, p in enumerate(kand):
            if frei(typ, p):
                gebaut.append((typ, p))
                return (p if setzt(typ) else None), list(kand[:i + 1])
        return None, list(kand)
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
    # 7
    liste7 = [(120 + i, 120) for i in range(20)]
    belegt7 = set(liste7[:5])
    b, G, gebaut = kette(1, 1, 0, lambda typ, kern, r: list(liste7) if typ == B.SCHENKE else [],
                         frei=lambda typ, p: p not in belegt7)
    aus7 = b.schritt(ST, G, RL)
    b2, G2, gebaut2 = kette(1, 1, 0, lambda typ, kern, r: list(liste7) if typ == B.SCHENKE else [],
                            frei=lambda typ, p: p not in liste7[:12])
    b2.schritt(ST, G2, RL)
    vorher2 = len(gebaut2)
    b2.schritt(dict(ST, t=ST["t"] + 700), G2, RL)
    pruefe(7, "5 belegt, 6. frei: gebaut %s %s | alle 12 belegt: Runde 1 %s, Runde 2 %s" % (
        gebaut, [a for a in aus7 if "Schenke" in a][:1], gebaut2[:vorher2], gebaut2[vorher2:]),
        gebaut and gebaut[0] == (B.SCHENKE, liste7[5]) and gebaut2[:vorher2] == []
        and gebaut2[vorher2:] == [(B.SCHENKE, liste7[12])])
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
