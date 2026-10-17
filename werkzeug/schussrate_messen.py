# -*- coding: utf-8 -*-
"""Schaden je Schuetze und Takt an einer sichtbaren Assassine nach ART und ABSTAND (SAI 17.10.; Anlass: Partie 1017a,
Assassine 195 starb neben 21 Schuetzen mit ~110 Leben je Takt - der Mittelwert 1,352 je Schuetze unterschaetzte die Naehe).

Runden wie angriff_raten_messen (sichtbar <= 160 Feinmass in beiden Runden, kein Feind im Umkreis 2, kein Nahangreifer).
Erster Versuch (17.10. 10:30, alle Schuetzen in Reichweite als Merkmal): Gegenprobe -29 % - durchgefallen. Grund aus dem
Spielcode: jeder Schuetze schiesst auf EIN Ziel (acquireShootTarget). Darum jetzt: Merkmale je Runde = Zahl der Schuetzen,
die die nachgebaute Zielwahl (sicht.Lage.zuteilen) DIESER Assassine zuteilt, je (Art, Abstandsband). Geschaetzt wird
Verlust je Takt = Summe Zahl x Rate mit nicht-negativen kleinsten Quadraten, Runden nach Laenge gewichtet.
VORHER FESTGELEGT:
  1. Gegenprobe Haelfte: Raten aus den Dateien 1, 3, 5 ...; damit den Gesamtverlust der Dateien 2, 4, 6 ... vorhersagen.
     Liegt die Vorhersage mehr als 25 % daneben, gelten die Raten nicht (dann bleibt der Mittelwert).
  2. Liegt beim Bogen das Band 0-9 nicht ueber dem Band 20-29, gibt es keinen Abstands-Effekt (dann ein Wert je Art).
Ergebnis: daten/schussrate.json (Raten aus ALLEN Dateien, wenn 1 und 2 halten).
Aufruf: python werkzeug/schussrate_messen.py daten/lage_....jsonl.gz [...]"""
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import nnls

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
from lageprotokoll import runden
import sicht as S

GRUPPE = {22: "bogen", 70: "bogen", 74: "bogen", 23: "armbrust", 72: "schleuder", 76: "feuer"}
BAENDER = {"bogen": (10, 20, 30, 41), "armbrust": (10, 20, 30, 41), "schleuder": (10, 19), "feuer": (12,)}
SPALTEN = [(g, i) for g, b in BAENDER.items() for i in range(len(b))]


def band(g, d):
    for i, grenze in enumerate(BAENDER[g]):
        if d < grenze:
            return i
    return None


def zeilen(pfad):
    aus = []
    vor = None
    for t, st, E, G in runden(pfad):
        Ed = {e["nr"]: e for e in E}
        if vor and t > vor[0]:
            dt, E0 = t - vor[0], vor[1]
            L = {e["nr"]: e for e in E}
            Gd = {g["nr"]: g for g in G}
            lg = None
            feinde = [e for e in E if e["besitzer"] not in (0, 1) and e["typ"] not in S.TIERE]
            alle = [(e["x"], e["y"]) for e in feinde]
            for e in E:
                if e["typ"] != 73 or e["besitzer"] != 1 or e["nr"] not in E0:
                    continue
                a = E0[e["nr"]]
                o, o0 = (e["x"], e["y"]), (a["x"], a["y"])
                if e.get("nahangreifer") or a.get("nahangreifer") or any(S.schach(o, p) <= 2 or S.schach(o0, p) <= 2 for p in alle):
                    continue
                if lg is None:
                    lg = S.Lage(L, Gd, 1, {})
                if not lg.sichtbar(o) or not lg.sichtbar(o0):
                    continue
                x = [0.0] * len(SPALTEN)
                for g, d in lg.feuer.get(e["nr"], ()):
                    b = band(g, d)
                    if b is not None:
                        x[SPALTEN.index((g, b))] += 1
                aus.append((x, max(0, a["leben"] - e["leben"]) / float(dt), dt))
        vor = (t, Ed)
    return aus


def schaetze(z):
    A = np.array([r[0] for r in z]) * np.sqrt([[r[2]] for r in z])
    b = np.array([r[1] for r in z]) * np.sqrt([r[2] for r in z])
    rate, _ = nnls(A, b)
    return rate


def main():
    pfade = [a for a in sys.argv[1:] if "=" not in a]
    je = {p: zeilen(p) for p in pfade}
    lern = [r for i, p in enumerate(pfade) if i % 2 == 0 for r in je[p]]
    test = [r for i, p in enumerate(pfade) if i % 2 == 1 for r in je[p]]
    r_l = schaetze(lern)
    vorher = sum(float(np.dot(r[0], r_l)) * r[2] for r in test)
    echt = sum(r[1] * r[2] for r in test)
    abw = (vorher - echt) / echt if echt else float("nan")
    print("Gegenprobe Haelfte: Lern %d Runden, Test %d Runden: vorhergesagt %.0f, echt %.0f Leben (%+.0f %%)" % (
        len(lern), len(test), vorher, echt, 100 * abw))
    alle = lern + test
    r_a = schaetze(alle)
    for (g, i), v in zip(SPALTEN, r_a):
        grenzen = (0,) + BAENDER.get(g, (0,))
        n = sum(1 for r in alle if r[0][SPALTEN.index((g, i))])
        print("   %-10s %s: %.2f je Takt (%d Runden mit so einem Schuetzen)" % (
            g, "%d-%d Felder" % (grenzen[i], grenzen[i + 1] - 1) if g != "versperrt" else "     ", v, n))
    ok1 = abs(abw) <= 0.25
    ok2 = r_a[SPALTEN.index(("bogen", 0))] > r_a[SPALTEN.index(("bogen", 2))]
    print("URTEIL (diese Mitschriften): Gegenprobe %s, Abstands-Effekt Bogen %s" % ("haelt" if ok1 else "NICHT", "ja" if ok2 else "NEIN"))
    if ok1 and ok2:
        json.dump({"spalten": ["%s:%d" % s for s in SPALTEN], "rate": [round(float(v), 3) for v in r_a],
                   "baender": BAENDER, "gegenprobe_abweichung": round(abw, 3), "runden": len(alle)},
                  open(os.path.join(HIER, "..", "daten", "schussrate.json"), "w"), indent=1)
        print("-> daten/schussrate.json")


if __name__ == "__main__":
    main()
