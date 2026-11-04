# -*- coding: utf-8 -*-
"""Auf welchem Teil seiner Bahn kann ein Geschoss eine Einheit treffen? Ebener Boden, Schuetze und Ziel auf gleicher Hoehe, gerechnet mit dem geprueften Nachbau.

Getroffen wird, wer zwischen Boden und Boden + 42 Hoehe steht, wenn das Geschoss sein Feld betritt. Ausgabe: gefahr_tabelle.txt.
"""
import math
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import flug_modell as fm  # noqa: E402

BODEN = 8
ARTEN = (("Pfeil (Bogenschuetze, arabisch, Pferd)", 125, 0.18, 30), ("Bolzen (Armbrust)", 125, 0.20, 30), ("Stein (Schleuderer)", 100, 0.20, 30))


def main():
    aus = ["Geschoss | Abstand in Feldern | Winkel | hoechster Punkt ueber dem Boden | Takte Flug | Felder auf dem Weg, ueber denen es zu hoch fliegt, um zu treffen"]
    for name, v, b, ab in ARTEN:
        for feld in (3, 5, 8, 10, 12, 15, 18, 20, 25, 30, 35, 40):
            d = feld * 8 - 1
            w = fm.winkel(v, d, 0)
            vc, vs = v * math.cos(w * fm.PI / 180), v * math.sin(w * fm.PI / 180)
            h0 = BODEN + ab
            hoch = h0
            sicher = []
            takte = 0
            fertig = False
            for n, schr, h_e in fm.bahn(0, 0, h0, feld * 8, 0, vc, vs, b, takte=400):
                takte = n
                for x, y, h, wg in schr:
                    hoch = max(hoch, h)
                    if h > BODEN + 42:
                        sicher.append(x >> 3)
                    if x >= feld * 8:
                        fertig = True
                        break
                if fertig:
                    break
            s = sorted(set(sicher))
            aus.append("%s | %d | %d | %d | %d | %s" % (name, feld, w, hoch - BODEN, takte, ("Feld %d bis %d" % (s[0], s[-1])) if s else "keins, trifft auf dem ganzen Weg"))
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "gefahr_tabelle.txt"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
