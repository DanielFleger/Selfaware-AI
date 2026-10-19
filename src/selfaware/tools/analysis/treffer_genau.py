# -*- coding: utf-8 -*-
"""Ein Treffer ganz genau (19.10.2026, Daniel: "bei jedem verlorenen Assassinen genau notieren, warum er verletzt wurde").

Fuer eine Assassine und einen Tick: ihre Spur in den 250 Takten davor (Ort, Leben, Zustand) und in jeder dieser Runden jeder
feindliche Fernkaempfer bis 45 Felder und jeder waehlbare Feind bis 30 Felder - mit Schach-Abstand, Feinmass (Sichtregel L75:
<= 160), Gebaeude unter ihm (Typ, erhoeht?) und ob die Schusslinie laut Modell frei ist. Zeigt, wer ihn gesehen haben kann.

Aufruf: uv run python -m selfaware.tools.analysis.treffer_genau <lage.jsonl.gz> <Nr> <Tick des Treffers> [Takte davor, Standard 250]
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.telemetry.lageprotokoll as LP
import selfaware.services.sicht as SI

NAME = {22: "Bogen", 23: "Armbrust", 24: "Speer", 25: "Pike", 26: "Streitkolben", 27: "Schwert", 28: "Ritter", 29: "Tunnel",
        30: "Leiter", 37: "Moench", 55: "Lord", 70: "arab.Bogen", 71: "Sklave", 72: "Schleuder", 73: "Assassine",
        74: "Pferdebogen", 75: "arab.Schwert", 76: "Feuerwerfer", 5: "Ingenieur"}


def ch(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def main():
    lage, nr, tick = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    davor = int(sys.argv[4]) if len(sys.argv) > 4 else 250
    for t, st, E, G in LP.runden(lage):
        if t < tick - davor:
            continue
        if t > tick + 60:
            break
        L = {d["nr"]: d for d in E}
        Gd = {g["nr"]: g for g in G}
        a = L.get(nr)
        if not a or a["besitzer"] != 1 or a["typ"] != 73:
            print("Tick %d: Nr %d keine eigene Assassine" % (t, nr))
            continue
        ort = (a["x"], a["y"])
        s = SI.Lage(L, Gd, 1)
        print("Tick %d: Assassine %d bei %s, Leben %d, Zustand %d, Laufziel (%d, %d); sichtbar laut Regel: %s; Modell %.0f je Takt" % (
            t, nr, ort, a["leben"], a["zustand"], a["laufx"], a["laufy"], s.sichtbar(ort), s.beschuss(ort, nr=nr)))
        zeilen = []
        for e in L.values():
            if e["besitzer"] in (0, 1):
                continue
            p = (e["x"], e["y"])
            d = ch(ort, p)
            fern = e["typ"] in SI.REICHWEITE
            if not ((fern and d <= 45) or (e["typ"] in SI.WAEHLBAR and d <= 30)):
                continue
            unter = s.gebaeude.get(p)
            erh = bool(unter and unter[1] in SI.ERHOEHT)
            linie = "-"
            if fern:
                linie = "frei" if (erh or s.linie_frei(p, unter[0] if unter else None, ort)) else "zu"
            zeilen.append((d, "    %-12s Nr %4d Sp %d bei %s: %2d Felder, %3d Feinmass%s, Gebaeude darunter %s, Linie %s, Zustand %d" % (
                NAME.get(e["typ"], "Typ %d" % e["typ"]), e["nr"], e["besitzer"], p, d, SI.abstand_fein(ort, p),
                " (SIEHT)" if e["typ"] in SI.WAEHLBAR and SI.abstand_fein(ort, p) <= SI.SICHT else "",
                ("Typ %d%s" % (unter[1], " ERHOEHT" if erh else "")) if unter else "keins", linie, e["zustand"])))
        for _, z in sorted(zeilen):
            print(z)


if __name__ == "__main__":
    main()
