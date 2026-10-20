# -*- coding: utf-8 -*-
"""Auswertung der Editor-Duelle (editor_messen.py duell): Leben je Art, Schaden je Takt X an Y (beide Richtungen jedes Duells),
Streuung zwischen den Wiederholungen (zwei unabhaengige Messungen je Paar) und Gegenprobe mit der Schuetzen-Messung L81
(Bogen ~9,3, Armbrust ~26, arab. Bogen ~13,3, Schleuder ~7,1 je Takt gegen eine Assassine).

Aufruf: uv run python -m selfaware.tools.analysis.duell_auswerten data/research/editor_duell_<stempel>.jsonl [...]"""
import io
import json
import os
import sys


from selfaware.services.gefecht import raten

NAME = {22: "Bogen", 23: "Armbrust", 24: "Speer", 25: "Pike", 26: "Streitkolben", 27: "Schwert", 28: "Ritter",
        70: "arab.Bogen", 71: "Sklave", 72: "Schleuder", 73: "Assassine", 74: "Pferdebogen", 75: "arab.Schwert", 76: "Feuerwerfer"}
L81 = {22: 9.3, 23: 26.0, 70: 13.3, 72: 7.1}


def main():
    werte, leben = {}, {}
    for f in sys.argv[1:]:
        for z in io.open(f, encoding="utf-8"):
            r = json.loads(z)
            a, d = r["a_typ"], r["d_typ"]
            leben[a] = r["leben_a"]; leben[d] = r["leben_d"]
            rt = raten(r)
            if rt["a_an_d"] is not None:
                werte.setdefault((a, d), []).append(rt["a_an_d"])
            if rt["d_an_a"] is not None:
                werte.setdefault((d, a), []).append(rt["d_an_a"])
    print("Leben je Art:", ", ".join("%s %d" % (NAME.get(k, k), v) for k, v in sorted(leben.items())))
    typen = sorted({x for x, _ in werte} | {y for _, y in werte})
    print("\nSchaden je Takt, Zeile greift Spalte an (Mittel; * = Wiederholungen weichen > 15 % ab):")
    print("%-12s" % "" + "".join("%9s" % NAME.get(y, y)[:8] for y in typen))
    streu = []
    for x in typen:
        zeile = []
        for y in typen:
            w = [v for v in werte.get((x, y), []) if v is not None]
            if not w:
                zeile.append("%9s" % "-")
                continue
            m = sum(w) / len(w)
            ab = (max(w) - min(w)) / m if m > 0 and len(w) > 1 else 0.0
            if len(w) > 1:
                streu.append(ab)
            zeile.append("%8.1f%s" % (m, "*" if ab > 0.15 else " "))
        print("%-12s" % NAME.get(x, x)[:12] + "".join(zeile))
    if streu:
        streu.sort()
        print("\nAbweichung zwischen Wiederholungen: Median %.1f %%, 90 %% bei %.1f %%, groesste %.1f %% (n=%d)" % (
            100 * streu[len(streu) // 2], 100 * streu[len(streu) * 9 // 10], 100 * streu[-1], len(streu)))
    print("\nGegenprobe L81 (Schuetze gegen Assassine): " + ", ".join(
        "%s gemessen %.1f / L81 %.1f" % (NAME[k], sum(werte[(k, 73)]) / len(werte[(k, 73)]), v)
        for k, v in L81.items() if werte.get((k, 73))))


if __name__ == "__main__":
    main()
