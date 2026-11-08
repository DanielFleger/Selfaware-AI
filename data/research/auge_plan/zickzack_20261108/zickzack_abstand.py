# -*- coding: utf-8 -*-
"""Szene zickzack_g (B-174): Warum wird die Zickzack-Gruppe noch getroffen? Liegt es an der Gruppe selbst?

Vermutung nach dem Lauf: Der Pfeil verfehlt sein Ziel, faellt aber auf einen Nachbarn, weil das Spiel die Gruppe dicht aufstellt
(jedes zweite Feld). Was sie widerlegt: Wird ein Laeufer mit seiner echten Spur auch dann oft getroffen, wenn er allein waere,
liegt es nicht an den Nachbarn.
Gerechnet wird fuer jeden Takt und jeden Schuetzen auf seinen Laeufer, mit der Rechnung, die in zickzack_auswerten.py an den
wirklichen Pfeilen stimmt:
  Gruppe: Der Pfeil trifft den ersten Laeufer auf seinem Weg (wie im Spiel).
  Ziel zuerst: Dieser erste Laeufer ist sein Ziel.
  allein: Es gibt nur diesen einen Laeufer (derselbe Weg, keine Nachbarn).
Danach die Karte der Gefahr: Wie oft waere ein gedachter Nachbar getroffen worden, der mit festem Versatz neben dem Ziel mitlaeuft?
Grenzen: Die Karte zaehlt jeden Nachbarn fuer sich, ein Pfeil trifft aber nur einen. Sie gilt fuer Pfeile von einer Seite und fuer
ebenen Boden. Aufstellungen sind daraus gerechnet, nicht gefahren.
Eingabe wie zickzack_auswerten.py. Ausgabe: zickzack_abstand.txt
"""
import collections
import glob
import json
import math
import os
import sys

import numpy as np

import zickzack_auswerten as za

from zickzack_auswerten import ART, EINLAUF, STUFEN, aat, fm, fp, stufe  # isort: skip

HIER = za.HIER
R = 8  # Rand der Gefahrenkarte in Feldern
AUF = range(-R, R + 1)


def flug(lauf, boden, zeilen, sch, i, t0, q):
    """Die Felder, in denen der Pfeil tief genug fliegt, um zu treffen, relativ zum Ziel im jeweiligen Takt. None = Aufnahme zu Ende."""
    zx, zy, zz = aat.zielpunkt(q, sch, i)
    sx, sy = int(q["mxx"][sch]), int(q["myy"][sch])
    h0 = int(q["hb"][sch]) + int(q["ht"][sch]) + aat.AUFSCHLAG
    gesamt = max(abs(sx - zx), abs(sy - zy)) - 1
    v, w = fm.anfang(ART, gesamt, zz - h0, None)
    r = w * fm.PI / 180.0
    vc, vs = float(np.float32(v * math.cos(r))), float(np.float32(v * math.sin(r)))
    tk = t0
    gefahr = set()
    for _, schritte, h_e, _ in fm.bahn2(sx, sy, h0, zx, zy, vc, vs, fm.TABELLE[ART][2]):
        tk += 1
        u = lauf.u.get(tk)
        if u is None:
            return None
        ux, uy, unten = int(u["x"][i]), int(u["y"][i]), int(u["hb"][i]) + int(u["ht"][i])
        for a, c, h, _wg in schritte:
            if unten <= h <= unten + fm.fenster(71):
                gefahr.add(((a >> 3) - ux, (c >> 3) - uy))
            if h < int(boden[int(zeilen[c >> 3]) + (a >> 3)]):
                return gefahr
        if h_e < 3:
            return gefahr
    return gefahr


def erster(lauf, boden, zeilen, sch, i, gruppe, t0, q):
    """Nummer des Laeufers, den der Pfeil zuerst trifft, False = keinen, None = Aufnahme zu Ende."""
    zx, zy, zz = aat.zielpunkt(q, sch, i)
    sx, sy = int(q["mxx"][sch]), int(q["myy"][sch])
    h0 = int(q["hb"][sch]) + int(q["ht"][sch]) + aat.AUFSCHLAG
    gesamt = max(abs(sx - zx), abs(sy - zy)) - 1
    v, w = fm.anfang(ART, gesamt, zz - h0, None)
    r = w * fm.PI / 180.0
    vc, vs = float(np.float32(v * math.cos(r))), float(np.float32(v * math.sin(r)))
    tk = t0
    for _, schritte, h_e, _ in fm.bahn2(sx, sy, h0, zx, zy, vc, vs, fm.TABELLE[ART][2]):
        tk += 1
        u = lauf.u.get(tk)
        if u is None:
            return None
        lage = [(j, int(u["feld"][j]), int(u["hb"][j]) + int(u["ht"][j])) for j in gruppe]
        for a, c, h, _wg in schritte:
            kn = int(zeilen[c >> 3]) + (a >> 3)
            for j, f, unten in lage:
                if kn == f and unten <= h <= unten + fm.fenster(71):
                    return j
            if h < int(boden[kn]):
                return False
        if h_e < 3:
            return False
    return False


def aufstellungen(karte, n):
    """Erwartete Zahl getroffener Nachbarn je Pfeil fuer gedachte Aufstellungen: Summe der Gefahr ueber alle anderen Plaetze, gemittelt ueber alle Ziele."""
    aus = []
    for name, plaetze in (
        *[("quer, Abstand %d" % s, [(0, j * s) for j in range(n)]) for s in (1, 2, 3, 4, 5, 6)],
        *[("laengs, Abstand %d" % s, [(j * s, 0) for j in range(n)]) for s in (1, 2, 3, 4, 5, 6)],
        *[("2 Reihen, Abstand %d" % s, [((j % 2) * s, (j // 2) * s) for j in range(n)]) for s in (2, 3, 4, 5, 6)],
    ):
        summe = 0.0
        for a in plaetze:
            for b in plaetze:
                if a != b:
                    summe += karte.get((b[0] - a[0], b[1] - a[1]), 0.0)
        aus.append((name, summe / n))
    return aus


def main():
    szene = sys.argv[1] if len(sys.argv) > 1 else "zickzack_g"
    pfad = sorted(glob.glob(os.path.join(HIER, "..", "laeufe", "lauf_s_*_%s.auge" % szene)), key=os.path.getmtime)[-1]
    k = za.Feldkarte.laden(feldliste=za.FELDLISTE)
    lauf = fp.Lauf(pfad, k)
    zeilen = fp.zeilen_lesen()
    boden = lauf.gel[0][1]["hoehe"]
    b = [json.loads(z) for z in open(os.path.join(HIER, "lauf_%s.log" % szene), encoding="utf-8", errors="replace") if z.startswith('{"schritt": "zickzack_bahnen"')][-1]
    von, bis = b["von"] + EINLAUF, b["bis"] - 40
    aus = ["Datei %s, Takte %d bis %d, je Takt der Stand davor (Gegenprobe in zickzack_g_ergebnis.txt)" % (os.path.basename(pfad), von, bis), ""]
    aus.append("Abstand: Schuesse | Gruppe | Ziel zuerst | allein")
    karten = {}
    for x in b["bahnen"]:
        grp = x["laeufer"]
        z = collections.defaultdict(collections.Counter)
        je_laeufer = collections.defaultdict(collections.Counter)
        heiss = collections.Counter()
        fluege = 0
        for t in range(von, bis):
            q = lauf.u.get(t - 1)
            if q is None:
                continue
            for sch, i in zip(x["schuetzen"], grp):
                d = max(abs(int(q["x"][sch]) - int(q["x"][i])), abs(int(q["y"][sch]) - int(q["y"][i])))
                e = erster(lauf, boden, zeilen, sch, i, grp, t, q)
                a = erster(lauf, boden, zeilen, sch, i, [i], t, q)
                if e is None or a is None:
                    continue
                st = stufe(d)
                for s in [st] + (["ab 12"] if st is not None and d >= 12 else []):
                    z[s]["n"] += 1
                    z[s]["gruppe"] += bool(e)
                    z[s]["ziel"] += e == i
                    z[s]["allein"] += bool(a)
                if st is not None and d >= 12:
                    je_laeufer[i]["n"] += 1
                    je_laeufer[i]["allein"] += bool(a)
                    g = flug(lauf, boden, zeilen, sch, i, t, q)
                    if g is not None:
                        fluege += 1
                        for o in g:
                            heiss[o] += 1
        for s in list(STUFEN) + ["ab 12"]:
            c = z[s]
            if c["n"]:
                aus.append("  %-9s %-8s %6d | %5.1f %% | %5.1f %% | %5.1f %%" % (x["muster"], "%d-%d" % s if s != "ab 12" else s, c["n"], 100 * c["gruppe"] / c["n"], 100 * c["ziel"] / c["n"], 100 * c["allein"] / c["n"]))
        aus.append("  je Laeufer ab 12 Feldern, allein: " + ", ".join("%d: %.1f %%" % (i, 100 * c["allein"] / c["n"]) for i, c in sorted(je_laeufer.items())))
        aus.append("")
        karte = {o: v / fluege for o, v in heiss.items()} if fluege else {}
        karten[x["muster"]] = karte
        aus.append("Gefahr fuer einen gedachten Nachbarn (Bahn %s, ab 12 Feldern, %d Fluege), Prozent. Waagerecht Versatz in x (positiv = hinter dem Ziel, vom Schuetzen weg), senkrecht in y (quer zur Schussrichtung)" % (x["muster"], fluege))
        aus.append("      " + "".join("%4d" % dx for dx in AUF))
        for dy in AUF:
            aus.append("  %3d " % dy + "".join("%4.0f" % (100 * karte.get((dx, dy), 0.0)) for dx in AUF))
        aus.append("")
    aus.append("Gerechnete Aufstellungen fuer %d Laeufer im Zickzack: erwartete Zahl getroffener Nachbarn je Pfeil" % za_n(b))
    for name, wert in sorted(aufstellungen(karten["zickzack"], za_n(b)), key=lambda z: z[1]):
        aus.append("  %-24s %.3f" % (name, wert))
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, ("zickzack_abstand.txt" if szene == "zickzack_g" else szene + "_abstand.txt")), "w", encoding="utf-8").write(text)
    print(text)


def za_n(b):
    return len(b["bahnen"][0]["laeufer"])


if __name__ == "__main__":
    main()
