# -*- coding: utf-8 -*-
"""Szene zickzack_g (B-174): Zickzack des Kerns fuer eine ganze Gruppe gegen einen geraden Gruppenlauf, gleiche Bahn, gleiche Schuetzen.

Vor dem Lauf festgelegt (die Grenzen sind meine, ohne Vorgabe dahinter):
  Der Bau gilt als widerlegt, wenn in der Zickzack-Bahn weniger als die Haelfte der Schritte die Richtung wechselt
  oder wenn die Zickzack-Gruppe ab 12 Feldern nicht seltener getroffen wird als die gerade Gruppe.
Die Quote steht zweimal: aus den wirklichen Pfeilen (wenige, an der Schussfolge gebunden, Wissensregister S78) und aus der
Rechnung fuer jeden Takt mit der echten Spur aller 8 Laeufer (ein Pfeil trifft jeden Laeufer der Gruppe auf seinem Weg).
Die Rechnung wird an den wirklichen Pfeilen gehalten; stimmt sie dort nicht, gilt ihre Zeile nicht.
Grenzen: nur Sklaven gegen Bogenschuetzen, Ziel auf einer Achse, freies Feld. Eine Bahn je Muster: kein Streumass ueber Laeufe.
Eingabe: neueste lauf_s_*_zickzack_g.auge unter laeufe/, Protokoll lauf_zickzack_g.log. Ausgabe: zickzack_g_ergebnis.txt.
"""
import collections
import glob
import json
import math
import os
import sys

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "ausweichen_20261108"))
sys.path.insert(0, os.path.join(HIER, "..", "streuung_20261104"))
import ausweichen_alle_takte as aat  # noqa: E402
import flug_modell as fm  # noqa: E402
import flug_pruefen as fp  # noqa: E402
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte  # noqa: E402

fp.U_F.update({"planx": "plannedDestinationX", "plany": "plannedDestinationY"})
EINLAUF, ART = aat.EINLAUF, aat.ART
STUFEN = ((8, 10), (11, 13), (14, 16), (17, 19), (20, 24))
AB_12 = (11, 24)  # die Stufen ab 12 Feldern: Stufe 11 bis 13 hat 12 in der Mitte


def stufe(d):
    return next((s for s in STUFEN if s[0] <= d <= s[1]), None)


def rechnen_gruppe(lauf, boden, zeilen, sch, i, gruppe, t0, q):
    """Wie ausweichen_alle_takte.rechnen, nur trifft der Pfeil jeden Laeufer der Gruppe auf seinem Weg, nicht bloss sein Ziel."""
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
        lage = [(int(u["feld"][j]), int(u["hb"][j]) + int(u["ht"][j])) for j in gruppe]
        for a, c, h, _wg in schritte:
            kn = int(zeilen[c >> 3]) + (a >> 3)
            if any(kn == f and unten <= h <= unten + fm.fenster(71) for f, unten in lage):
                return True
            if h < int(boden[kn]):
                return False
        if h_e < 3:
            return False
    return False


def bewegung(lauf, gruppe, von, bis):
    """Je Laeufer die Feldwechsel: Felder je 1000 Takte, Anteil der Schritte mit neuer Richtung, Anteil schraeg."""
    felder = wechsel = paare = schraeg = 0
    takte = [t for t in sorted(lauf.u) if von <= t <= bis]
    for i in gruppe:
        schritte = []
        vor = None
        for t in takte:
            p = (int(lauf.u[t]["x"][i]), int(lauf.u[t]["y"][i]))
            if vor is not None and p != vor:
                schritte.append((p[0] - vor[0], p[1] - vor[1]))
            vor = p
        felder += len(schritte)
        schraeg += sum(1 for a, b in schritte if a and b)
        paare += max(len(schritte) - 1, 0)
        wechsel += sum(1 for a, b in zip(schritte, schritte[1:]) if a != b)
    n = len(gruppe)
    return {
        "felder_je_1000": 1000 * felder / n / max(len(takte), 1),
        "wechsel": wechsel / paare if paare else None,
        "schraeg": schraeg / felder if felder else None,
    }


def versatz(lauf, gruppe, von, bis):
    """Bleibt die Aufstellung? Mittlerer Abstand zum Leiter und wie oft sich der Abstand je Laeufer aendert."""
    takte = [t for t in sorted(lauf.u) if von <= t <= bis]
    leiter = gruppe[0]
    weit = []
    for i in gruppe[1:]:
        for t in takte[::12]:
            u = lauf.u[t]
            weit.append(max(abs(int(u["x"][i]) - int(u["x"][leiter])), abs(int(u["y"][i]) - int(u["y"][leiter]))))
    return sum(weit) / len(weit) if weit else None


def main():
    szene = sys.argv[1] if len(sys.argv) > 1 else "zickzack_g"
    pfad = sorted(glob.glob(os.path.join(HIER, "..", "laeufe", "lauf_s_*_%s.auge" % szene)), key=os.path.getmtime)[-1]
    k = Feldkarte.laden(feldliste=FELDLISTE)
    lauf = fp.Lauf(pfad, k)
    zeilen = fp.zeilen_lesen()
    boden = lauf.gel[0][1]["hoehe"]
    b = [json.loads(z) for z in open(os.path.join(HIER, "lauf_%s.log" % szene), encoding="utf-8", errors="replace") if z.startswith('{"schritt": "zickzack_bahnen"')][-1]
    von, bis = b["von"] + EINLAUF, b["bis"] - 40
    je = {}
    for x in b["bahnen"]:
        for i in x["laeufer"]:
            je[i] = x
    aus = ["Datei %s, Takte %d bis %d" % (os.path.basename(pfad), von, bis), "Kern (Python-Seite): %s" % b["kern"], ""]
    wirklich = collections.defaultdict(collections.Counter)
    probe = collections.Counter()
    for s, f in lauf.fluege.items():
        z = f[0][1]
        t0 = f[0][0]
        if z["art"] != ART or z["ziel"] not in je or t0 < von or t0 not in lauf.u or t0 - 1 not in lauf.u:
            continue
        ende = next(((t, q) for t, q in f[1:] if q["da"] != 2 or q["boden"] != 0), None)
        if ende is None:
            continue
        tr = ende[1]["da"] == 3 and ende[1]["boden"] == 9
        x = je[z["ziel"]]
        u = lauf.u[t0]
        d = max(abs(int(u["x"][z["sch"]]) - int(u["x"][z["ziel"]])), abs(int(u["y"][z["sch"]]) - int(u["y"][z["ziel"]])))
        st = stufe(d)
        for schluessel in ((x["muster"], "alle"), (x["muster"], st)):
            wirklich[schluessel]["schuss"] += 1
            wirklich[schluessel]["treffer"] += tr
        if st is not None and d >= 12:
            wirklich[(x["muster"], "ab 12")]["schuss"] += 1
            wirklich[(x["muster"], "ab 12")]["treffer"] += tr
        for name, q in (("Takt", lauf.u[t0]), ("Takt davor", lauf.u[t0 - 1])):
            probe[(name, "Zielpunkt gleich")] += aat.zielpunkt(q, z["sch"], z["ziel"])[:2] == (z["zx"], z["zy"])
            probe[(name, "Ergebnis gleich")] += rechnen_gruppe(lauf, boden, zeilen, z["sch"], z["ziel"], x["laeufer"], t0, q) == tr
            probe[(name, "Pfeile")] += 1
    wahl = max(("Takt", "Takt davor"), key=lambda n: probe[(n, "Zielpunkt gleich")])
    aus += ["Gegenprobe an den wirklichen Pfeilen: %s" % sorted(probe.items()), "Rechnung mit dem Stand: %s" % wahl, ""]
    rechnung = {}
    for x in b["bahnen"]:
        m = x["muster"]
        grp = x["laeufer"]
        zahl = collections.defaultdict(collections.Counter)
        for t in range(von, bis):
            q = lauf.u.get(t if wahl == "Takt" else t - 1)
            if q is None:
                continue
            for sch, i in zip(x["schuetzen"], grp):
                d = max(abs(int(q["x"][sch]) - int(q["x"][i])), abs(int(q["y"][sch]) - int(q["y"][i])))
                e = rechnen_gruppe(lauf, boden, zeilen, sch, i, grp, t, q)
                if e is None:
                    continue
                st = stufe(d)
                zahl[st]["schuss"] += 1
                zahl[st]["treffer"] += e
                if st is not None and d >= 12:
                    zahl["ab 12"]["schuss"] += 1
                    zahl["ab 12"]["treffer"] += e
        rechnung[m] = zahl
        be = bewegung(lauf, grp, von, bis)
        aus.append("Bahn %s: Befehle Python %d, Wenden %d, nachgeschickt %d | Felder je 1000 Takte %.1f, Schritte mit neuer Richtung %s, schraeg %s, mittlerer Abstand zum Leiter %.2f" % (
            m, len(x["befehle"]), len(x["wendepunkte"]), x["nachgeschickt"], be["felder_je_1000"], "-" if be["wechsel"] is None else "%.0f %%" % (100 * be["wechsel"]), "-" if be["schraeg"] is None else "%.0f %%" % (100 * be["schraeg"]), versatz(lauf, grp, von, bis) or 0))
    aus.append("")
    aus.append("Abstand: wirkliche Pfeile (Schuss, Quote) | jeder Takt, jeder Schuetze (Schuss, Quote)")

    def zeile(m, s, name):
        w = wirklich[(m, s)]
        r = rechnung[m][s]
        return "  %-9s %-8s %4d %4s  | %7d %6s" % (m, name, w["schuss"], "%3.0f%%" % (100 * w["treffer"] / w["schuss"]) if w["schuss"] else "-", r["schuss"], "%5.1f%%" % (100 * r["treffer"] / r["schuss"]) if r["schuss"] else "-")

    for m in rechnung:
        for s in STUFEN:
            aus.append(zeile(m, s, "%d-%d" % s))
        aus.append(zeile(m, "ab 12", "ab 12"))
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "%s_ergebnis.txt" % szene), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
