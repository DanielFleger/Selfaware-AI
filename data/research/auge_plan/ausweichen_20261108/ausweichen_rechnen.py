# -*- coding: utf-8 -*-
"""Schritt 4 im Plan_Gehirn (B-173): Was muesste Ausweichen sparen? Reine Rechnung, ruft nichts im Spiel.

Grundlage sind die am 04.11. gegen das Spiel geprueften Nachbauten (streuung_20261104/flug_modell.py, streuung_modell.py): Zielpunkt mit Vorhalt, Flugbahn, Treffer im Feld unter Boden + 42.
Annahmen fuer den Laeufer, aus der Aufzeichnung lauf_s_20261103_193034_laufen: 16 Takte je Feld, gerade und schraeg, das Feld wechselt auf halbem Weg zwischen zwei Mitten, gedreht wird in der Feldmitte.
Der Schuetze steht auf einer Feldecke (Abschuss 38 hoch, Ziel 38 hoch auf ebenem Boden 8), wie in den Aufzeichnungen.

Was die Rechnung nicht weiss: wie lange der Laeufer nach einem neuen Befehl braucht, ob ein neuer Befehl ihn bremst, wie oft der Schuetze abdrueckt. Das misst erst der Lauf.
Ausgabe: ausweichen_rechnung.txt. Aufruf: ausweichen_rechnen.py
"""
import math
import os
import sys

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "streuung_20261104"))
import flug_modell as fm  # noqa: E402
import streuung_modell as sm  # noqa: E402

TAKTE_JE_FELD = 16
BODEN, SCHUSS_HOEHE, ZIEL_HOEHE = 8, 38, 38
ART_PFEIL = 1
RICHTUNG = {0: (0, -1), 1: (1, -1), 2: (1, 0), 3: (1, 1), 4: (0, 1), 5: (-1, 1), 6: (-1, 0), 7: (-1, -1)}  # facingDirection wie in streuung_modell.zielpunkt_einheit

# Muster: Liste (Blickrichtung, Felder), die sich wiederholt. Der Schuetze steht westlich, die Schusslinie laeuft entlang x
MUSTER = {
    "quer": [(0, 200)],  # gerade, quer zur Schusslinie
    "schraeg": [(1, 200)],  # gerade, schraeg
    "laengs": [(6, 200)],  # gerade auf den Schuetzen zu
    "zick quer 3": [(1, 3), (7, 3)],  # quer, alle 3 Felder die andere Diagonale
    "zick quer 2": [(1, 2), (7, 2)],
    "zick quer 1": [(1, 1), (7, 1)],
    "zick zu 3": [(5, 3), (7, 3)],  # auf den Schuetzen zu, alle 3 Felder die andere Diagonale
    "zick zu 2": [(5, 2), (7, 2)],
    "zick zu 1": [(5, 1), (7, 1)],
}
ABSTAENDE = (5, 8, 10, 12, 14, 16, 18)


def spur(muster, x0, y0, takte):
    """Je Takt (mikro x, mikro y, Blick). Start in einer Feldmitte, jeder Abschnitt endet in einer Feldmitte."""
    aus = []
    x, y = x0 * 8 + 4.0, y0 * 8 + 4.0
    i = 0
    while len(aus) < takte:
        blick, felder = muster[i % len(muster)]
        i += 1
        dx, dy = RICHTUNG[blick]
        for _ in range(felder * TAKTE_JE_FELD):
            aus.append((x, y, blick))
            x += dx * 8.0 / TAKTE_JE_FELD
            y += dy * 8.0 / TAKTE_JE_FELD
            if len(aus) >= takte:
                break
    return aus


def feld(m):
    return int(math.floor(m)) >> 3


def schuss(sp, t0, sx, sy):
    """Ein Pfeil im Takt t0 auf den Laeufer. Rueckgabe: getroffen, Flugtakte bis zum Ende."""
    mx, my, blick = sp[t0]
    abstand = int(max(abs(sx - mx), abs(sy - my))) - 1
    zx, zy, _ = sm.zielpunkt_einheit(feld(mx), feld(my), ZIEL_HOEHE, True, blick, abstand, 0, 1)
    gesamt = max(abs(sx - zx), abs(sy - zy)) - 1
    v, w = fm.anfang(ART_PFEIL, gesamt, ZIEL_HOEHE - SCHUSS_HOEHE, None)
    r = w * fm.PI / 180.0
    vc, vs = float(np.float32(v * math.cos(r))), float(np.float32(v * math.sin(r)))
    b = fm.TABELLE[ART_PFEIL][2]
    tk = t0
    for n, schritte, h_e, _ in fm.bahn2(sx, sy, SCHUSS_HOEHE, zx, zy, vc, vs, b):
        tk += 1
        if tk >= len(sp):
            return None, n
        ux, uy, _ = sp[tk]
        for a, c, h, _wg in schritte:
            if (a >> 3, c >> 3) == (feld(ux), feld(uy)) and BODEN <= h <= BODEN + fm.fenster(71):
                return True, n
            if h < BODEN:
                return False, n
        if h_e < BODEN:
            return False, n
    return False, 400


def rate(muster, d):
    """Trefferanteil ueber alle Schusstakte einer Spur. Der Schuetze steht beim Schuss d Felder westlich des Laeufers (Feldecke, wie in den Aufzeichnungen), um 0 bis 4 Reihen versetzt: Sonst flogen alle Pfeile genau entlang einer Feldreihe."""
    laenge = sum(f for _, f in muster) * TAKTE_JE_FELD
    takte = max(laenge * 4, 8 * TAKTE_JE_FELD) + 300
    sp = spur(muster, 200, 200, takte)
    tr = n = 0
    flug = []
    start = TAKTE_JE_FELD * 2
    for t0 in range(start, start + min(laenge * 2, 16 * TAKTE_JE_FELD)):
        for versatz in (-4, -2, 0, 2, 4):
            sx, sy = (feld(sp[t0][0]) - d) * 8, (feld(sp[t0][1]) + versatz) * 8
            ende = schuss(sp, t0, sx, sy)
            if ende[0] is None:
                continue
            n += 1
            tr += ende[0]
            flug.append(ende[1])
    return tr / n if n else None, (sum(flug) / len(flug) if flug else None), n


def main():
    aus = ["Rechnung vom Flug-Nachbau, Pfeil (Art 1), ebener Boden, Laeufer 16 Takte je Feld. Anteil der Schuesse, die treffen, ueber jeden moeglichen Schusstakt.", ""]
    kopf = "%-14s" % "Muster" + "".join("%8s" % ("D=%d" % d) for d in ABSTAENDE)
    aus.append(kopf)
    rein = {}
    for name, m in MUSTER.items():
        z = "%-14s" % name
        for d in ABSTAENDE:
            r, fl, n = rate(m, d)
            rein[(name, d)] = (r, fl, n)
            z += "%8s" % ("%.0f%%" % (r * 100) if r is not None else "-")
        aus.append(z)
    aus.append("")
    aus.append("Flugtakte bis zum Ende, Mittel (quer): " + ", ".join("D=%d: %.1f" % (d, rein[("quer", d)][1]) for d in ABSTAENDE))
    aus.append("Schuesse je Zelle: %d bis %d" % (min(v[2] for v in rein.values()), max(v[2] for v in rein.values())))
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "ausweichen_rechnung.txt"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
