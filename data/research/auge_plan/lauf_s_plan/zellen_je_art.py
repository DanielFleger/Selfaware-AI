# -*- coding: utf-8 -*-
"""B-142 Plan Lauf S: Wie viele ungestoerte Zellen gibt es je Versuchsart, wenn der Laufweg in der Zelle liegt? Nur lesen. Frage-Agent 03.11.: Der Kern allein reicht nicht, wer 60 Felder laeuft, verlaesst ihn.

Eine Zelle ist ein Rechteck, in dem alles liegt: Aufstellung, Laufweg, Ziel. Es ist ganz glatt und eben. Zwei Zellen desselben Durchgangs halten den Abstand S.
Der Abstand gilt von Rand zu Rand, also auch vom Laufweg zur fremden Zelle. Im Gefecht halten die Zellen zusaetzlich S zu den Startplaetzen der beiden Spieler: Dort stehen Lord und Leute.
Gebaeude schiessen nicht. Es zaehlt das schlechteste Paar von Startplaetzen; wo die Lords wirklich stehen, liest der Lauf.

Vorher laufen lassen: karte_flaeche.py (packt die Schichten aus).
Aufruf aus dem Arbeitsbaum:
  python data/research/auge_plan/lauf_s_plan/zellen_je_art.py > data/research/auge_plan/lauf_s_plan/zellen_je_art.txt
"""
import collections
import itertools
import json
import os
import tempfile

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
N = os.path.join(tempfile.gettempdir(), "lauf_s_plan", "grumpy")


def zb(y):
    return (199 - y, 200 + y) if y <= 199 else (y - 200, 599 - y)


def addx(y):
    return y * y + 2 * y - 199 if y <= 199 else 40200 + 400 * (y - 200) - (y - 200) * (y - 200)


lo = np.fromfile(N + ".logik.bin", dtype="<u4")
he = np.fromfile(N + ".hoehe.bin", dtype="u1")
og = np.fromfile(N + ".organismus.bin", dtype="<u2")
ge = np.fromfile(N + ".gebaeude.bin", dtype="<u2")
haeufig = collections.Counter(lo.tolist()).most_common(1)[0][0]
glatt, H = np.zeros((400, 400), dtype=bool), np.zeros((400, 400), dtype=np.int32)
for y in range(400):
    a, b = zb(y)
    for x in range(a, b + 1):
        i = addx(y) + x
        glatt[y, x], H[y, x] = lo[i] == haeufig and og[i] == 0 and ge[i] == 0, int(he[i])
SG = np.zeros((401, 401), dtype=np.int64)
SG[1:, 1:] = glatt.cumsum(0).cumsum(1)
HOEHE = 4


def passt(x, y, b, h):
    if SG[y + h, x + b] - SG[y, x + b] - SG[y + h, x] + SG[y, x] < b * h:
        return False
    t = H[y:y + h, x:x + b]
    return t.max() - t.min() <= HOEHE


def abstand(a, b):
    """Schachabstand zweier Rechtecke (x, y, breite, hoehe), von Rand zu Rand."""
    dx = max(a[0] - (b[0] + b[2]), b[0] - (a[0] + a[2]), 0)
    dy = max(a[1] - (b[1] + b[3]), b[1] - (a[1] + a[3]), 0)
    return max(dx, dy)


def startplaetze():
    """Mitten der Gebaeudehaufen auf der Karte: je Startplatz 9 Gebaeude, ein Lord steht dabei. Die Werte im Kartenkopf sind ein anderes Mass (dort z. B. 36, 101) und taugen hier nicht."""
    pos = {}
    for y in range(400):
        a, b = zb(y)
        for x in range(a, b + 1):
            k = int(ge[addx(y) + x])
            if k:
                pos.setdefault(k, []).append((x, y))
    haufen = []
    for v in pos.values():
        m = (sum(p[0] for p in v) / len(v), sum(p[1] for p in v) / len(v))
        if not any(max(abs(m[0] - h[0]), abs(m[1] - h[1])) < 40 for h in haufen):
            haufen.append((round(m[0]), round(m[1])))
    return haufen


def packen(formen, s, sperre=()):
    """Gierig, zeilenweise. Das ist eine untere Schranke, eine bessere Packung findet mehr. Formen: Liste (breite, hoehe), z. B. beide Lagen eines Streifens."""
    aus = []
    for y in range(0, 400, 2):
        for x in range(0, 400, 2):
            for b, h in formen:
                if x + b > 400 or y + h > 400 or not passt(x, y, b, h):
                    continue
                r = (x, y, b, h)
                if any(abstand(r, a) < s for a in aus) or any(abstand(r, (px, py, 1, 1)) < s for px, py in sperre):
                    continue
                aus.append(r)
                break
    return aus


ARTEN = [
    ("nah", "V1 Reaktion, V2, V3 Fussschuetzen, V4b", [(12, 12)], 60),
    ("bahn", "V1 Gehtempo der Soldaten: 30 Felder schraeg, 30 gerade", [(32, 32)], 60),
    ("weit", "V1 Reichweite Fussschuetzen: Ziel 60 Felder entfernt", [(8, 64), (64, 8)], 60),
    ("lauf", "V3 laufendes Ziel, Fussschuetzen", [(24, 24)], 60),
    ("geraet", "V1 Reaktion Geraete, V3 Geraete, V4, laufendes Ziel Geraete", [(24, 24)], 80),
    ("geraet_bahn", "V1 Gehtempo Geraete", [(32, 32)], 80),
    ("geraet_weit", "V1 Reichweite Geraete: Ziel 84 Felder entfernt", [(8, 88), (88, 8)], 80),
]
ergebnis = {}
print("Glatte Felder", int(glatt.sum()), ". Abstand gilt von Rand zu Rand. Eine Zelle je Durchgang ist die Kontrolle.")
plaetze = startplaetze()
print("Startplaetze, Mitte der Gebaeudehaufen:", plaetze)
for name, wofuer, formen, s in ARTEN:
    e = packen(formen, s)
    je_paar = {p: packen(formen, s, p) for p in itertools.combinations(plaetze, 2)}
    schlecht = min(je_paar, key=lambda p: len(je_paar[p]))
    ergebnis[name] = {"formen": formen, "abstand": s, "editor": e, "gefecht": je_paar[schlecht], "gefecht_schlechtestes_paar": schlecht}
    print("%-12s %-58s Abstand %2d: Editor %2d Zellen, Gefecht %d bis %d Zellen je nach Startplaetzen" % (name, wofuer, s, len(e), len(je_paar[schlecht]), max(len(v) for v in je_paar.values())))
json.dump(ergebnis, open(os.path.join(HIER, "zellen_je_art.json"), "w"), indent=0)
