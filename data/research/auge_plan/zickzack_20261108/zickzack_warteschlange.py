# -*- coding: utf-8 -*-
"""Szenen zickzack_g und zickzack2_g (B-174): Kam der naechste Wegpunkt rechtzeitig an?

Vermutung: Im zweiten Lauf verlor die dichte Gruppe den Richtungswechsel (94 % auf 62 %), weil neben ihrem einen Befehl je Feld acht
Einzelbefehle der breiten Bahn in derselben Schlange standen (ein Gruppenbefehl je Takt, Wissensregister S57). Was sie widerlegt:
Hat die dichte Gruppe im zweiten Lauf nicht laenger auf ihren Befehl gewartet als im ersten, liegt es nicht an der Schlange.
Gemessen wird je Laeufer: Takte zwischen dem Betreten seines Platzes (x, y = plannedDestination) und dem naechsten neuen Platz.
Das Spiel liest ein neues Ziel in der Feldmitte; zwischen Betreten und Mitte liegen bei 12 Takten je Feld 6 Takte.
Aufruf: zickzack_warteschlange.py. Ausgabe: zickzack_warteschlange.txt
"""
import glob
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "streuung_20261104"))
import flug_pruefen as fp  # noqa: E402
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte  # noqa: E402

fp.U_F.update({"planx": "plannedDestinationX", "plany": "plannedDestinationY"})
EINLAUF = 150
FENSTER = 6


def wartezeiten(lauf, i, von, bis):
    aus = []
    plan = da_seit = None
    for t in sorted(lauf.u):
        if not von <= t <= bis:
            continue
        q = lauf.u[t]
        p = (int(q["planx"][i]), int(q["plany"][i]))
        o = (int(q["x"][i]), int(q["y"][i]))
        if plan is not None and p != plan:
            if da_seit is not None:
                aus.append(t - da_seit)
            da_seit = None
        plan = p
        if o == p and da_seit is None:
            da_seit = t
    return aus


def main():
    k = Feldkarte.laden(feldliste=FELDLISTE)
    zeilen = ["Takte vom Betreten des Platzes bis zum naechsten neuen Platz (je Laeufer; das Spiel liest bis zur Feldmitte, 6 Takte):", ""]
    for szene in ("zickzack_g", "zickzack2_g"):
        pfad = sorted(glob.glob(os.path.join(HIER, "..", "laeufe", "lauf_s_*_%s.auge" % szene)), key=os.path.getmtime)[-1]
        lauf = fp.Lauf(pfad, k)
        b = [json.loads(z) for z in open(os.path.join(HIER, "lauf_%s.log" % szene), encoding="utf-8", errors="replace") if z.startswith('{"schritt": "zickzack_bahnen"')][-1]
        von, bis = b["von"] + EINLAUF, b["bis"] - 40
        for x in b["bahnen"]:
            if x["muster"] == "gerade":
                continue
            w = sorted(v for i in x["laeufer"] for v in wartezeiten(lauf, i, von, bis))
            if not w:
                continue
            zeilen.append("  %-12s %-9s %5d Wegpunkte: Median %2d, 90 %% bis %2d, Anteil laenger als %d Takte %3.0f %%" % (szene, x["muster"], len(w), w[len(w) // 2], w[len(w) * 9 // 10], FENSTER, 100 * sum(v > FENSTER for v in w) / len(w)))
    text = chr(10).join(zeilen) + chr(10)
    open(os.path.join(HIER, "zickzack_warteschlange.txt"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
