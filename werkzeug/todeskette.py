# -*- coding: utf-8 -*-
"""Die toedliche Kette einer Assassine Runde fuer Runde (19.10.2026): in den letzten <Takte> vor dem Tod je Runde Ort, Leben,
Zustand, Laufziel, sichtbar laut Regel (L75) mit dem naechsten waehlbaren Feind, Schuetzen in Reichweite (mit Linie) und
darunter die, die gerade zielen/schiessen (Zustand 4/5/6) - dazu jede Meldung des Lenkers zu ihr in dieser Zeit.

Aufruf: python todeskette.py <konsole.txt> <lage.jsonl.gz> <Nr> <Todestick> [Takte davor, Standard 600]
"""
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import lageprotokoll as LP
import sicht as SI

NAME = {22: "Bogen", 23: "Armbrust", 24: "Speer", 25: "Pike", 26: "Streitkolben", 27: "Schwert", 28: "Ritter", 55: "Lord",
        70: "arab.Bogen", 71: "Sklave", 72: "Schleuder", 73: "Assassine", 74: "Pferdebogen", 75: "arab.Schwert",
        76: "Feuerwerfer"}


def ch(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def main():
    konsole, lage, nr, tod = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    davor = int(sys.argv[5]) if len(sys.argv) > 5 else 600
    mel = []
    tick = 0
    for z in open(konsole, encoding="utf-8", errors="replace"):
        m = re.match(r"^ *([0-9]+) \|", z)
        if not m:
            continue
        tick = int(m.group(1))
        if tick < tod - davor or tick > tod + 100:
            continue
        for teil in z.split("; "):
            if re.search(r"\b(ENTDECKT|ENTDECKT vorbei|ZIELWAHL|ZIELWECHSEL|WEG|ROUTE GEFAEHRLICH|FLUCHT|AUSWEICHEN|BEUTE|"
                         r"LORD-[A-Z]+)( [a-z]+)? %d\b" % nr, teil):
                mel.append((tick, re.sub(r"^.*?\| ", "", teil.strip())[:200]))
    for t, st, E, G in LP.runden(lage):
        if t < tod - davor:
            continue
        if t > tod + 60:
            break
        L = {d["nr"]: d for d in E}
        a = L.get(nr)
        for mt, mz in [m for m in mel if m[0] == t]:
            print("      Lenker %d: %s" % (mt, mz))
        if not a or a["besitzer"] != 1 or a["typ"] != 73:
            print("%6d: tot" % t)
            break
        ort = (a["x"], a["y"])
        s = SI.Lage(L, {g["nr"]: g for g in G}, 1)
        sp = min(((SI.abstand_fein(ort, (e["x"], e["y"])), e["typ"], ch(ort, (e["x"], e["y"]))) for e in L.values()
                  if e["besitzer"] not in (0, 1) and e["typ"] in SI.WAEHLBAR), default=None)
        reich, zielen = 0, []
        for k, (p, r, erh, steht, art) in zip(s.schuetzen_nr, s.schuetzen):
            if (p[0] - ort[0]) ** 2 + (p[1] - ort[1]) ** 2 <= (r + 4) ** 2 and (erh or s.linie_frei(p, steht, ort)):
                reich += 1
                if L[k]["zustand"] in (4, 5, 6):
                    zielen.append("%s%d" % (NAME.get(L[k]["typ"], "?")[:4], ch(p, ort)))
        print("%6d: %s Leben %5d Z%3d lauf (%d,%d) | %s | Schuetzen in Reichweite+4 mit Linie %d, zielend: %s" % (
            t, ort, a["leben"], a["zustand"], a["laufx"], a["laufy"],
            ("SICHTBAR durch %s in %d (%d Fm)" % (NAME.get(sp[1], sp[1]), sp[2], sp[0]) if sp and sp[0] <= SI.SICHT
             else "unsichtbar (naechster %s in %d, %d Fm)" % (NAME.get(sp[1], sp[1]), sp[2], sp[0]) if sp else "-"),
            reich, " ".join(zielen[:8]) or "-"))


if __name__ == "__main__":
    main()
