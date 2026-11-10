# -*- coding: utf-8 -*-
"""Wie schnell arbeiten die Raid-Einheiten wirklich? (B-182 Eichung) Je Partie: Einheiten-Takte je Art aus dem Lagebild (lebende eigene
Einheiten je Runde mal Rundenlaenge), Ergebnisse je Modul aus der Mitschrift, daraus Ergebnisse je 1000 Einheiten-Takte. Dazu, wie oft
mehrere Reiter denselben Arbeiter jagen. Aufruf: python s_raten.py <konsole> <lage> [<konsole> <lage> ...]"""
import collections
import re
import sys

from selfaware.telemetry import lageprotokoll as LP

ARTEN = {71: "Sklave", 74: "Berittener", 75: "Arab. Schwertkaempfer", 73: "Assassine", 70: "Arab. Bogen"}
args = sys.argv[1:]
for k, lage in zip(args[::2], args[1::2]):
    takte, vorher, sp = collections.Counter(), None, None
    for t, st, E, B in LP.runden(lage):
        if sp is None:
            c = collections.Counter(e["besitzer"] for e in E if e["typ"] == 71 and e["leben"] > 0)
            sp = c.most_common(1)[0][0] if c else None
        if vorher is not None and sp is not None:
            dt = t - vorher
            for e in E:
                if e["besitzer"] == sp and e["typ"] in ARTEN and e["leben"] > 0:
                    takte[e["typ"]] += dt
        vorher = t
    txt = open(k, encoding="utf-8", errors="replace").read()
    raids = re.findall(r"RAIDS: (.*)", txt)
    letzte = raids[-1] if raids else ""
    brand = int((re.search(r"Brandtrupp: (\d+) Gebaeude", letzte) or [0, 0])[1])
    jagd = int((re.search(r"Reiterjagd: (\d+) Arbeiter", letzte) or [0, 0])[1])
    nk = re.search(r"Nahkampf-Raid: (\d+) Einheiten, (\d+) Gebaeude zerstoert, (\d+) Arbeiter", letzte)
    print("==", k.split("aufstellung_")[-1][:58], "| eigener Spieler", sp)
    for typ, name, n in ((71, "Sklave: angezuendet", brand), (74, "Berittener: Arbeiter", jagd)):
        print("   %-22s %4d | %7d Einheiten-Takte | %.2f je 1000" % (name, n, takte[typ], 1000.0 * n / takte[typ] if takte[typ] else 0))
    if nk:
        n = int(nk.group(2)) + int(nk.group(3))
        print("   %-22s %4d | %7d Einheiten-Takte | %.2f je 1000 (%s Gebaeude, %s Arbeiter)" % (
            "Schwertkaempfer: Ziele", n, takte[75], 1000.0 * n / takte[75] if takte[75] else 0, nk.group(2), nk.group(3)))
    # Gedraenge: bei jeder neuen Jagd, wie viele andere Reiter dasselbe Ziel in den letzten 300 Takten bekamen
    ziel, geteilt, alle = {}, 0, 0
    for zeile in txt.splitlines():
        m = re.match(r"\s*(\d+) \|", zeile)
        if not m:
            continue
        t = int(m.group(1))
        for r, a in re.findall(r"REITERJAGD: Reiter (\d+) jagt Arbeiter (\d+)", zeile):
            andere = sum(1 for r2, (a2, t2) in ziel.items() if r2 != r and a2 == a and t - t2 <= 300)
            alle += 1
            geteilt += andere > 0
            ziel[r] = (a, t)
    if alle:
        print("   Reiterjagd: %d neue Jagden, %d davon auf einen Arbeiter, den schon ein anderer Reiter jagt (%.0f %%)" % (alle, geteilt, 100.0 * geteilt / alle))
