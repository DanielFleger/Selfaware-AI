# -*- coding: utf-8 -*-
"""Nahkampf-Raid, Fokus 2: Kommen die Einheiten an ihren Zielen an? Je Zuweisung aus der Mitschrift (Einheit, Ziel, Zielort, Takt) die kleinste
Entfernung, die die Einheit im Lagebild bis zur naechsten Zuweisung oder ihrem Verschwinden erreichte, und ob sie danach noch lebte.
Aufruf: python s_nahkampf_weg.py <konsole> <lage>"""
import collections
import re
import sys

from selfaware.telemetry import lageprotokoll as LP

k, lage = sys.argv[1], sys.argv[2]
zuw = collections.defaultdict(list)   # Einheit -> [(Takt, Art, Ziel, (x, y))]
erf = set()
for zeile in open(k, encoding="utf-8", errors="replace"):
    m = re.match(r"\s*(\d+) \|", zeile)
    if not m:
        continue
    t = int(m.group(1))
    for n, art, z, x, y in re.findall(r"NAHKAMPF-RAID: (\d+) \(Typ \d+\) -> (Gebaeude|Arbeiter) (\d+) \(Typ \d+\) bei \((\d+), (\d+)\)", zeile):
        zuw[int(n)].append((t, art, int(z), (int(x), int(y))))
    for n, art, z in re.findall(r"NAHKAMPF-RAID: (\d+) \(Typ \d+\) hat (Gebaeude|Arbeiter) (\d+) erledigt", zeile):
        erf.add((int(n), int(z)))
orte = collections.defaultdict(list)  # Einheit -> [(Takt, (x, y), leben)]
letzter = 0
for t, st, E, B in LP.runden(lage):
    letzter = t
    for e in E:
        if e["nr"] in zuw and e["besitzer"] == 1:
            orte[e["nr"]].append((t, (e["x"], e["y"]), e["leben"]))
stat = collections.Counter()
naechste = []
for n, liste in zuw.items():
    spur = orte.get(n, [])
    for j, (t0, art, z, ziel) in enumerate(liste):
        t1 = liste[j + 1][0] if j + 1 < len(liste) else letzter
        teil = [(t, o, lb) for t, o, lb in spur if t0 <= t <= t1]
        d = min((max(abs(o[0] - ziel[0]), abs(o[1] - ziel[1])) for _, o, _ in teil), default=None)
        stat[(art, "Zuweisungen")] += 1
        if (n, z) in erf:
            stat[(art, "erledigt")] += 1
        if d is not None and d <= 3:
            stat[(art, "angekommen (<= 3 Felder)")] += 1
        if d is not None:
            naechste.append((art, d))
        if teil and teil[-1][0] < t1 - 200:
            stat[(art, "verschwunden vor dem naechsten Ziel")] += 1
for (art, was), n in sorted(stat.items()):
    print("%-9s %-38s %4d" % (art, was, n))
for art in ("Gebaeude", "Arbeiter"):
    ds = sorted(d for a, d in naechste if a == art)
    if ds:
        print("%-9s naechste Entfernung zum Ziel: Median %d, Viertel %d / %d" % (art, ds[len(ds) // 2], ds[len(ds) // 4], ds[3 * len(ds) // 4]))
tot = sum(1 for n, spur in orte.items() if spur and spur[-1][0] < letzter - 200)
print("Einheiten mit Zuweisung %d, davon vor dem Ende verschwunden %d" % (len(zuw), tot))
