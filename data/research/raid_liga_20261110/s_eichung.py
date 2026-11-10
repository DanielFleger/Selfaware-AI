# -*- coding: utf-8 -*-
"""Eichung Kauf nach Wirkung (B-182, Fokus 1): je Partie und Art die erwarteten Punkte (Summe der WIRKUNG-KAUF-Zeilen) gegen das, was das
Modul der Art wirklich erreichte, in denselben Punkten (raids.WERT je angezuendetem Gebaeude, raids.ARBEITER je gejagtem Arbeiter).
Die Erwartung gilt je Kauf fuer wirkung.HORIZONT Takte; die Einheiten leben laenger oder kuerzer - darum ist das Verhaeltnis ein Hinweis, kein Faktor.
Aufruf: python s_eichung.py <konsole> [<konsole> ...]"""
import collections
import re
import sys

from selfaware.micro.tasks import raids as RA

for k in sys.argv[1:]:
    txt = open(k, encoding="utf-8", errors="replace").read()
    erw, n = collections.defaultdict(float), collections.Counter()
    for m in re.finditer(r"WIRKUNG-KAUF: (\d+) .*? \(Typ (\d+)\), erwartet ([\d.]+) Punkte", txt):
        n[int(m.group(2))] += int(m.group(1))
        erw[int(m.group(2))] += float(m.group(3))
    brand = [int(t) for t in re.findall(r"BRANDTRUPP: Sklave \d+ hat Gebaeude \d+ \(Typ (\d+)\) angezuendet", txt)]
    jagd = {}
    for r, a, t in re.findall(r"REITERJAGD: Reiter (\d+) jagt Arbeiter (\d+) \(Typ (\d+)\)", txt):
        jagd[a] = int(t)
    raids = re.findall(r"RAIDS: (.*)", txt)
    letzte = raids[-1] if raids else ""
    getoetet = int((re.search(r"Reiterjagd: (\d+) Arbeiter", letzte) or [0, 0])[1])
    nk = re.search(r"Nahkampf-Raid: (\d+) Einheiten, (\d+) Gebaeude zerstoert, (\d+) Arbeiter", letzte)
    mittel_arbeiter = sum(RA.ARBEITER.get(t, 0) for t in jagd.values()) / len(jagd) if jagd else 0
    print("==", k.split("aufstellung_")[-1][:60])
    print("   gekauft:", dict(n), "| erwartet je Art:", {t: round(v) for t, v in erw.items()})
    print("   Sklaven: angezuendet %d, Punkte %d (erwartet %d)" % (len(brand), sum(RA.WERT.get(t, 0) for t in brand), erw.get(71, 0)))
    print("   Reiter: getoetet %d, Punkte etwa %d (Mittel der gejagten Arten %.1f; erwartet %d)" % (getoetet, getoetet * mittel_arbeiter, mittel_arbeiter, erw.get(74, 0)))
    if nk:
        print("   Nahkampf-Raid: %s Einheiten, %s Gebaeude, %s Arbeiter (erwartet: Typen 24-28, 75 zusammen %d)" % (
            nk.group(1), nk.group(2), nk.group(3), sum(v for t, v in erw.items() if t in (24, 25, 26, 27, 28, 75))))
