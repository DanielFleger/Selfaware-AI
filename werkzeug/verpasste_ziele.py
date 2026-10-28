# -*- coding: utf-8 -*-
"""B-285 Verpasste Ziele (Daniel 28.10. 01:12 "eigentlich solltest du die Fehler sehen, welche Gebaeude nicht zerstoert wurden,
obwohl sie besiegt werden haetten koennen"). Liest die Mitschrift einer Partie und listet je feindlichem Gebaeude, das die
Assassinen-Zielwahl gesehen hat: zerstoert ja/nein, wie oft und mit welchem Grund es verworfen wurde, das kleinste
Todesrisiko, wie oft es gewaehlt wurde - und wie viele Assassinen in denselben Runden OHNE Ziel standen. "Verpasst" heisst:
nicht zerstoert, mindestens einmal mit Todesrisiko unter VERPASST_RISIKO gerechnet oder nur "belegt", waehrend Assassinen
ohne Ziel standen. Nur Spielerwissen (Mitschrift), keine Spielwerte.
Aufruf: python verpasste_ziele.py <konsole.txt>"""
import re
import sys
from collections import defaultdict

VERPASST_RISIKO = 50


def auswerten(pfad):
    geb = defaultdict(lambda: {"typ": "?", "gruende": defaultdict(int), "risiko_min": None, "gewaehlt": 0, "runden_frei": 0,
                               "zerstoert": None})
    for z in open(pfad, encoding="utf-8", errors="replace"):
        m = re.match(r"\s*(\d+) \|", z)
        if not m:
            continue
        t = int(m.group(1))
        ohne = sum(int(x) for x in re.findall(r"(\d+) Assassinen ohne Ziel", z))
        for nr, typ, grund in re.findall(r"Gebaeude (\d+) \(([^)]+)\) in \d+: ([^;|]+)", z):
            g = geb[int(nr)]
            g["typ"] = typ
            kurz = re.sub(r"\(.*", "", grund).strip()
            g["gruende"][kurz] += 1
            r = re.search(r"Todesrisiko (\d+) %", grund)
            if r:
                g["risiko_min"] = int(r.group(1)) if g["risiko_min"] is None else min(g["risiko_min"], int(r.group(1)))
            if ohne:
                g["runden_frei"] += 1
        for nr, typ, risiko in re.findall(r"ZIELWAHL \d+ -> (\d+) Typ (\d+) in \d+: [^;]*?Todesrisiko (\d+) %", z):
            g = geb[int(nr)]
            g["gewaehlt"] += 1
            g["risiko_min"] = int(risiko) if g["risiko_min"] is None else min(g["risiko_min"], int(risiko))
        for nr in re.findall(r"Gebaeude (\d+) \(Typ \d+\) zerstoert", z):
            geb[int(nr)]["zerstoert"] = geb[int(nr)]["zerstoert"] or t
    return geb


def verpasst(g):
    if g["zerstoert"]:
        return False
    leicht = g["risiko_min"] is not None and g["risiko_min"] < VERPASST_RISIKO
    nur_belegt = set(g["gruende"]) <= {"belegt", "GEWAEHLT"} and g["gruende"]
    return bool((leicht or nur_belegt) and g["runden_frei"])


if __name__ == "__main__":
    geb = auswerten(sys.argv[1])
    v = {n: g for n, g in geb.items() if verpasst(g)}
    print("Gebaeude gesehen %d, zerstoert %d, VERPASST %d (nicht zerstoert, Risiko < %d %% oder nur 'belegt', und Assassinen "
          "standen ohne Ziel)" % (len(geb), sum(1 for g in geb.values() if g["zerstoert"]), len(v), VERPASST_RISIKO))
    for n, g in sorted(v.items(), key=lambda kv: (kv[1]["risiko_min"] if kv[1]["risiko_min"] is not None else 999)):
        print("  Gebaeude %d (%s): kleinstes Risiko %s %%, %d x gewaehlt, %d Runden mit freien Assassinen, Gruende %s" % (
            n, g["typ"], g["risiko_min"], g["gewaehlt"], g["runden_frei"],
            ", ".join("%s %d" % kv for kv in sorted(g["gruende"].items(), key=lambda kv: -kv[1]))))
