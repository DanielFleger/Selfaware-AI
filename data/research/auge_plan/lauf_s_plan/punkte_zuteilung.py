# -*- coding: utf-8 -*-
"""B-142 Plan Lauf S: Welcher Punkt der Checkliste wird wo gemessen? Schreibt punkte_zuteilung.csv und prueft, dass kein Punkt fehlt oder doppelt ist.

Aufruf: python data/research/auge_plan/lauf_s_plan/punkte_zuteilung.py > data/research/auge_plan/lauf_s_plan/punkte_zuteilung.txt
"""
import collections
import csv
import os
import re

HIER = os.path.dirname(os.path.abspath(__file__))
ZUTEILUNG = {
    "E-V1": ("Editor, Steckbrief", "P330 P343 P346 P347 P351 P352 P358 P365 P371"),
    "E-V2": ("Editor, Duell", "P305 P318 P327 P332 P339"),
    "E-V4": ("Editor, Belagerung samt Bemannen und Munition", "P309 P322 P328 P334 P337 P345 P359 P360 P361 P363 P369 P216"),
    "E-V4b": ("Editor, Fusstruppen gegen Gebaeude", "P353 P354 P355 P356 P357 P366 P367 P368"),
    "E-V5": ("Editor, Massenschlacht", "P370"),
    "E-V6": ("Editor, Marsch und Angriff auf einen Punkt", "P302 P310 P311 P325 P326 P338"),
    "E-V7": ("Editor, Sonderfaelle", "P297 P298 P299 P300 P301 P303 P304 P314 P315 P317 P321 P323 P335 P336 P340 P341 P344 P348 P349 P364 P086 P123 P124 P125 P126 P127 P128 P177 P214"),
    "G": ("Gefecht, Lords stehen, KI ohne Waren", "P192 P199 P201 P306 P313 P329 P331 P362"),
    "K": ("Geladener Stand aus Lauf K, KI spielt", "P268 P308 P316 P319 P320 P324 P333 P342 P350"),
    "nicht": ("Nicht in diesem Lauf: braucht Buendnis (P307) oder die Spielart GM_SIEGE_THAT (P312)", "P307 P312"),
}
zeilen = open(os.path.join(HIER, "..", "Checkliste_Auge.md"), encoding="utf-8").read().splitlines()
INFO = {}
for s in zeilen:
    m = re.match(r"- \[ \] (P\d+) `([^`]+)` \(0x([0-9a-f]+)\): (.*)", s)
    if m:
        INFO[m.group(1)] = (m.group(2), m.group(3), "[Spielart]" in s, "erst schärfen" in s, m.group(4))
SOLL = {p for p in INFO if 297 <= int(p[1:]) <= 371} | {"P086", "P123", "P124", "P125", "P126", "P127", "P128", "P177", "P214", "P216", "P192", "P199", "P201", "P268"}
ist = collections.Counter(p for _, (_, l) in ZUTEILUNG.items() for p in l.split())
print("Punkte Soll", len(SOLL), "zugeteilt", len(ist))
print("fehlen:", sorted(SOLL - set(ist)), "zu viel:", sorted(set(ist) - SOLL), "doppelt:", [p for p, n in ist.items() if n > 1])
assert SOLL == set(ist) and max(ist.values()) == 1
with open(os.path.join(HIER, "punkte_zuteilung.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["punkt", "funktion", "adresse", "abschnitt", "wo", "marke_spielart", "erst_schaerfen", "aus_lauf"])
    for ab, (wo, l) in ZUTEILUNG.items():
        for p in l.split():
            n, a, sp, sch, _ = INFO[p]
            w.writerow([p, n, "0x" + a, ab, wo, "ja" if sp else "", "ja" if sch else "", "S" if 297 <= int(p[1:]) <= 371 else ("K" if p in ("P192", "P199", "P201", "P268") else "F")])
for ab, (wo, l) in ZUTEILUNG.items():
    print("%-6s %3d  %s" % (ab, len(l.split()), wo))
print("mit Marke Spielart in E:", sorted(p for ab, (_, l) in ZUTEILUNG.items() if ab.startswith("E") for p in l.split() if INFO[p][2]))
print("erst schaerfen:", sorted(p for p in ist if INFO[p][3]))
