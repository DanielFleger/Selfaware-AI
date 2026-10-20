# -*- coding: utf-8 -*-
"""Bestzeiten des Haertetests (Daniel 06.10. 21:25: "halte die schnellsten Zeiten fest, mache Tests bis ich wieder zurueck
bin und verbessere selbstaendig"). Liest ein Laufprotokoll (erstes_spiel.py streitkolben=...), zieht die Zeitmarken
heraus und fuehrt data/research/bestzeiten.json als Rangliste (schnellste Zeit bis 10 Kaempfer zuerst).
Aufruf: uv run python -m selfaware.tools.analysis.bestzeiten <protokoll> <name> [notiz]      (ohne Argumente: nur Rangliste zeigen)
"""

from selfaware import workspace as _workspace
import json
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
DATEI = os.path.join(_workspace.DATA, 'bestzeiten.json')


def marken(text):
    m = {}
    for k, t in re.findall(r"KAEMPFER (\d+) bei Tick (\d+)", text):
        m.setdefault("kaempfer_%s" % k, int(t))
    for name, muster in (("seasoning_b", r"alle \d+ B-Plantagen stehen \(Tick (\d+)"),
                         ("endspiel", r"ENDSPIEL bei Tick (\d+)"),
                         ("ziel", r"ZIEL \d+ Streitkolbenkaempfer erreicht bei Tick (\d+)"),
                         ("produktion_hoefe", r"^\s*(\d+) \|.*PRODUKTION Milchviehhof"),
                         ("produktion_werkstaetten", r"^\s*(\d+) \|.*PRODUKTION Werkstaetten"),
                         ("abbruch", r"ABBRUCH.*'t': (\d+)")):
        r = re.search(muster, text, re.M)
        if r:
            m[name] = int(r.group(1))
    if "ziel" in m and "kaempfer_10" not in m:          # der 10. steht als ZIEL-Zeile (v4)
        m["kaempfer_10"] = m["ziel"]
    m["fehler"] = "Traceback" in text
    return m


def zeige(liste):
    liste = sorted(liste, key=lambda e: e["marken"].get("kaempfer_10") or 10 ** 9)
    print("Rang | Lauf | 10 Kaempfer | 1 | 5 | Endspiel | Seasoning B | Notiz")
    for i, e in enumerate(liste, 1):
        m = e["marken"]
        print("%2d | %-14s | %s | %s | %s | %s | %s | %s" % (i, e["name"], m.get("kaempfer_10", "-"), m.get("kaempfer_1", "-"),
                                                          m.get("kaempfer_5", "-"), m.get("endspiel", "-"),
                                                          m.get("seasoning_b", "-"), e.get("notiz", "")))


def main():
    liste = json.load(open(DATEI, encoding="utf-8")) if os.path.exists(DATEI) else []
    if len(sys.argv) >= 3:
        text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
        e = {"name": sys.argv[2], "marken": marken(text), "notiz": " ".join(sys.argv[3:])}
        liste = [x for x in liste if x["name"] != e["name"]] + [e]
        json.dump(liste, open(DATEI, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    zeige(liste)


if __name__ == "__main__":
    main()
