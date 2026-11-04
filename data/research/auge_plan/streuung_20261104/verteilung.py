# -*- coding: utf-8 -*-
"""Wie weit streut ein Schuss auf den Boden, je Schuetzenart: gerechnet mit dem geprueften Nachbau ueber die echte Zufallstabelle.

Teil 1: Zielpunkt ueber alle 20.000 Zahlen, nur die erste Stufe. Teil 2: Wo die Geschosse auf ebenem Boden wirklich landen, mit beiden Stufen und dem Flug (jede 10. Zahl der Tabelle). Grenze von Teil 2: ebener Boden ohne Hindernis, Schuetze und Ziel auf gleicher Hoehe, Start ohne den kleinen Versatz des Katapults (bis 7 Mikro).
Die Tabelle des Spiels liegt in tabelle_zufall.npy (aus dem Speicher von Instanz 2). Ausgabe: verteilung.txt.
"""
import os
import struct
import sys

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import flug_modell as fm  # noqa: E402
import streuung_modell as sm  # noqa: E402

NAMEN = {22: "Bogenschuetze (E_ARCHER 22)", 23: "Armbrust (E_XBOW 23)", 70: "Arab. Bogen (A_ARCHER 70)", 72: "Schleuder (A_SLINGER 72)", 74: "Pferdebogen (A_HARCHER 74)", 76: "Feuerwerfer (A_FIRETHROWER 76)", 39: "Katapult (S_CATAPULT 39)", 40: "Trebuchet (S_TREBUCHET 40)", 41: "Mangonel (S_MANGONEL 41)", 61: "Ballista (S_BALLISTA 61)", 77: "Feuerballista (S_FBALLISTA 77)"}
# Art des Geschosses beim Bodenschuss, Hoehe des Abschusses ueber dem Boden, Zusatz zur Zielhoehe (aus der Aufzeichnung: ziel_pruefung.txt)
FLUG = {22: (24, 30, 30), 23: (25, 30, 0), 70: (24, 30, 30), 72: (35, 30, 30), 74: (24, 45, 30), 76: (36, 30, 30), 39: (2, 0x38, 0), 40: (3, 0x82, 0), 41: (4, 0x40, 0), 61: (20, 0x19, 0), 77: (37, 0x19, 0)}
BODEN = 8


def tabelle():
    p = os.path.join(HIER, "tabelle_zufall.npy")
    if not os.path.exists(p):
        from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
        from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz
        from selfaware.tools.experiments.spielcode_rufen import Rufer
        k = Feldkarte.laden(feldliste=FELDLISTE)
        a = k.adresse("SEC_RNG", "randomNumbers[]")
        with Rufer(pid_der_instanz(2)) as r:
            np.save(p, np.array(struct.unpack("<%dh" % a[3], r.lies(a[0], a[3] * a[1]))))
    return np.load(p)


def lande(typ, sx, sy, zx, zy, zz):
    """Landeort auf ebenem Boden (Mikro), None wenn er nach 800 Takten nicht landet."""
    art, ab, zusatz = FLUG[typ]
    h0 = BODEN + ab
    d = max(abs(zx - sx), abs(zy - sy)) - 1
    d = max(d, 0)
    a = fm.anfang_voll(art, d, zz + zusatz - h0)
    if a is None:
        return None
    v, w = a
    r = w * fm.PI / 180.0
    vc, vs = v * np.cos(r), v * np.sin(r)
    b = fm.TABELLE[art][2]
    letzt = (sx, sy)
    for n, schr, h_e in fm.bahn(sx, sy, h0, zx, zy, float(vc), float(vs), b, takte=800):
        for x, y, h, wg in schr:
            letzt = (x, y)
            if h < BODEN and (wg > d // 2 or art in (2, 3, 4)):
                return x, y
    return None


def main():
    t = tabelle()
    t_l = [int(x) for x in t]
    aus = ["Zufallstabelle: %d Zahlen, kleinste %d, groesste %d, Mittel %.0f" % (len(t), t.min(), t.max(), t.mean())]
    aus.append("")
    aus.append("Teil 1, nur erste Stufe, ueber alle Zahlen. Art | entlang kleinste..groesste (Mikro, minus = zu weit) | quer | Hoehe | Anteil ohne Laengsfehler | im Feld (unter 4 Mikro) | bis 1 | bis 2 | bis 4 Felder")
    for typ, name in NAMEN.items():
        for boden in ((False, True) if typ in (61, 77) else (False,)):
            e = [sm.streuung_boden(typ, boden, r) for r in t_l]
            en, qu, hz = zip(*e)
            d = [max(abs(a), abs(b)) for a, b, _ in e]
            n = len(e)
            aus.append("%s%s | %d..%d, Mittel %.1f | %d..%d | %d..%d | %.0f%% | %.0f%% | %.0f%% | %.0f%% | %.0f%%" % (name, " (Bodenbefehl)" if boden else "", min(en), max(en), sum(en) / n, min(qu), max(qu), min(hz), max(hz), 100 * sum(1 for x in en if x == 0) / n, 100 * sum(1 for x in d if x < 4) / n, 100 * sum(1 for x in d if x < 12) / n, 100 * sum(1 for x in d if x < 20) / n, 100 * sum(1 for x in d if x < 36) / n))
    aus.append("")
    aus.append("Schuss auf eine Einheit: Chance auf Streuung (Stufe / 300), Ziel hoeher als der Boden des Schuetzen um d:")
    for typ in (22, 77):
        aus.append("%s: " % NAMEN[typ] + ", ".join("d=%d: %.0f%%" % (d, 100 * min(sm.fehler_stufe(typ, 8 + d, 8), 300) / 300) for d in (-50, 0, 10, 30, 60, 100, 150)))
    aus.append("")
    aus.append("Teil 2, Landeort auf ebenem Boden mit beiden Stufen. Abstand Landefeld zum befohlenen Feld. Art | Abstand in Feldern | Zahl | genau | bis 1 | bis 2 | bis 4 | bis 8 | Mittel Laenge (plus = zu weit) | Mittel quer")
    for typ, name in NAMEN.items():
        for dist in (10, 20, 30):
            sx, sy = 1600, 1600
            ax, ay = sx + dist * 8, sy
            werte = []
            for i in range(0, 20000, 10):
                bx, by, bz = ax, ay, BODEN
                stein = 7 if typ == 41 else 1
                j = i
                for _ in range(stein):
                    x, y, z, zog = sm.ziel_vorbereiten_boden(typ, True, sx, sy, 2, bx, by, bz, BODEN, 12345, t_l, j)
                    bx, by, bz = x, y, z
                    j += zog + 1
                    p = lande(typ, sx, sy, x, y, z)
                    if p is not None:
                        werte.append(p)
            if not werte:
                aus.append("%s | %d | keine Landung" % (name, dist))
                continue
            d = [max(abs((a >> 3) - (ax >> 3)), abs((b >> 3) - (ay >> 3))) for a, b in werte]
            n = len(d)
            lang = sum(a - ax for a, _ in werte) / n / 8
            quer = sum(abs(b - ay) for _, b in werte) / n / 8
            aus.append("%s | %d | %d | %.0f%% | %.0f%% | %.0f%% | %.0f%% | %.0f%% | %+.1f | %.1f" % (name, dist, n, 100 * sum(1 for x in d if x == 0) / n, 100 * sum(1 for x in d if x <= 1) / n, 100 * sum(1 for x in d if x <= 2) / n, 100 * sum(1 for x in d if x <= 4) / n, 100 * sum(1 for x in d if x <= 8) / n, lang, quer))
            print(aus[-1], flush=True)
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "verteilung.txt"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
