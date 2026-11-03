# -*- coding: utf-8 -*-
"""B-142 Plan Lauf S: Wie viele ungestoerte Versuchsfelder hat die Karte? Rechnung aus den Schichten der .map, nur lesen.

Aufruf aus dem Arbeitsbaum:
  python data/research/auge_plan/lauf_s_plan/karte_flaeche.py > data/research/auge_plan/lauf_s_plan/karte_flaeche.txt

"Glatt" heisst: Logik gleich dem haeufigsten Wert der Karte, kein Baum, kein Fels, kein Gebaeude. Was die anderen Logik-Bits heissen,
ist hier nicht entschieden. Das zaehlt eher zu wenig als zu viel. Einheiten und Gebaeude der Karte werden im Lauf erst abgeraeumt.
"""
import collections
import json
import os
import subprocess
import tempfile

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
KARTE = r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme Instanz2\ucp\plugins\Mod-KI-Team-Liga-2.0.2\resources\maps\Liga_Grumpy Neighbors.map"
ARBEIT = os.path.join(tempfile.gettempdir(), "lauf_s_plan")
os.makedirs(ARBEIT, exist_ok=True)
N = os.path.join(ARBEIT, "grumpy")
print("Schichten:", subprocess.run(["node", os.path.join(HIER, "karte_schichten.js"), KARTE, N], capture_output=True, text=True, check=True).stdout.strip())


def zb(y):
    return (199 - y, 200 + y) if y <= 199 else (y - 200, 599 - y)


def addx(y):
    return y * y + 2 * y - 199 if y <= 199 else 40200 + 400 * (y - 200) - (y - 200) * (y - 200)


lo = np.fromfile(N + ".logik.bin", dtype="<u4")
he = np.fromfile(N + ".hoehe.bin", dtype="u1")
og = np.fromfile(N + ".organismus.bin", dtype="<u2")
ge = np.fromfile(N + ".gebaeude.bin", dtype="<u2")
ei = np.fromfile(N + ".einheit.bin", dtype="<u2")
haeufig = collections.Counter(lo.tolist()).most_common()
print("Felder", len(lo), "haeufigster Logik-Wert", hex(haeufig[0][0]), "auf", haeufig[0][1], "Feldern")
print("Baeume", int(((og > 0) & (og < 2000)).sum()), "Felsen", int((og >= 2000).sum()))
print("Gebaeude auf der Karte: verschieden", len(set(ge.tolist()) - {0}), "Felder", int((ge > 0).sum()))
print("Einheiten auf der Karte:", len(set(ei.tolist()) - {0}))
print("Hoehe kleinste/Median/groesste", int(he.min()), int(np.median(he)), int(he.max()))
G, H, frei = np.full((400, 400), -1, dtype=np.int64), np.zeros((400, 400), dtype=np.int32), np.zeros((400, 400), dtype=bool)
for y in range(400):
    a, b = zb(y)
    for x in range(a, b + 1):
        i = addx(y) + x
        G[y, x], H[y, x], frei[y, x] = int(lo[i]), int(he[i]), og[i] == 0 and ge[i] == 0
glatt = (G == haeufig[0][0]) & frei
print("Glatte Felder:", int(glatt.sum()))
S = np.zeros((401, 401), dtype=np.int64)
S[1:, 1:] = glatt.cumsum(0).cumsum(1)
HOEHE = 4  # Spanne innerhalb einer Zelle: gleiche Hoehe fuer Reichweite und Tempo, Bergauf misst P330 eigens


def passt(x, y, d):
    n = S[y + d, x + d] - S[y, x + d] - S[y + d, x] + S[y, x]
    if n < d * d:
        return False
    t = H[y:y + d, x:x + d]
    return t.max() - t.min() <= HOEHE


def flach(d):
    belegt, aus = np.zeros((400, 400), dtype=bool), []
    for y in range(400 - d + 1):
        for x in range(400 - d + 1):
            if not belegt[y, x] and passt(x, y, d) and not belegt[y:y + d, x:x + d].any():
                belegt[y:y + d, x:x + d] = True
                aus.append((x, y))
    return aus


def mit_abstand(kern, abstand):
    aus = []
    for y in range(0, 400 - kern + 1, 2):
        for x in range(0, 400 - kern + 1, 2):
            if passt(x, y, kern) and all(max(abs(x - a), abs(y - b)) >= abstand + kern for a, b in aus):
                aus.append((x, y))
    return aus


for d in (12, 16, 20, 25, 30, 40, 50):
    print("Quadrat %2d x %2d ganz glatt, Hoehenspanne bis %d: %3d Stueck" % (d, d, HOEHE, len(flach(d))))
zellen = {}
for kern, abstand in ((12, 25), (12, 45), (12, 60), (16, 45), (16, 60), (24, 60), (24, 80)):
    z = mit_abstand(kern, abstand)
    zellen["%d_%d" % (kern, abstand)] = z
    print("Kern %2d, Abstand zwischen zwei Kernen mindestens %2d: %2d Zellen, erste %s" % (kern, abstand, len(z), z[:4]))
json.dump(zellen, open(os.path.join(HIER, "karte_zellen.json"), "w"), indent=0)
