# -*- coding: utf-8 -*-
"""Szene ausweichen (B-173, Plan_Gehirn Schritt 4): Wie oft trifft ein Pfeil je Laufmuster und Abstand, gegen die Vorausrechnung?

Vor dem Lauf von mir gesetzt, ohne Messung und ohne Vorgabe dahinter (der Plan sagt nur spuerbar):
  Zickzack fliegt raus, wenn es ab 12 Feldern Abstand die Trefferquote gegenueber dem geraden Lauf gleichen Abstands nicht um mindestens 15 Prozentpunkte senkt
  oder wenn der Laeufer dabei weniger als drei Viertel der Felder des geraden Laufs schafft.
  Die Rechnung gilt als widerlegt, wenn eine Bahn mit mindestens 30 Schuessen um mehr als 25 Prozentpunkte daneben liegt.
Treffer: Das Geschoss endet am Laeufer (Zustand 3, Bodenmerker 9). Zweite Quelle: die Leben des Laeufers.
Gewertet werden Schuesse ab 150 Takte nach dem Start: Vorher laufen manche Laeufer noch nicht.
Eingabe: neueste lauf_s_*_ausweichen.auge unter laeufe/, Protokoll lauf_ausweichen.log. Ausgabe: ausweichen_ergebnis.txt.
"""
import collections
import glob
import json
import math
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
sys.path.insert(0, os.path.join(HIER, "..", "streuung_20261104"))
import ausweichen_rechnen as ar  # noqa: E402
import flug_pruefen as fp  # noqa: E402
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte  # noqa: E402

fp.U_F.update({"blick": "facingDirection", "lauf": "tunnelerFinishedDigging"})
EINLAUF = 150
FUSS = 16  # Takte je Feld in der Vorausrechnung


def fehler(p, n):
    return 100 * math.sqrt(p * (1 - p) / n) if n else 0


def bahnen_lesen(szene):
    zeilen = [json.loads(z) for z in open(os.path.join(HIER, "lauf_%s.log" % szene), encoding="utf-8", errors="replace") if z.startswith('{"schritt": "ausweichen_bahnen"')]
    return zeilen[-1]


def main():
    szene = sys.argv[1] if len(sys.argv) > 1 else "ausweichen"
    pfad = sorted(glob.glob(os.path.join(HIER, "..", "laeufe", "lauf_s_*_%s.auge" % szene)), key=os.path.getmtime)[-1]
    k = Feldkarte.laden(feldliste=FELDLISTE)
    lauf = fp.Lauf(pfad, k)
    b = bahnen_lesen(szene)
    von = b["von"] + EINLAUF
    je_laeufer = {x["laeufer"]: x for x in b["bahnen"]}
    takte = sorted(lauf.u)
    stat = collections.defaultdict(lambda: collections.Counter())
    richtung = collections.defaultdict(lambda: collections.Counter())
    ohne_ende = 0
    for s, f in lauf.fluege.items():
        z = f[0][1]
        t0 = f[0][0]
        if z["art"] != 1 or z["ziel"] not in je_laeufer or t0 < von:
            continue
        ende = next(((t, q) for t, q in f[1:] if q["da"] != 2 or q["boden"] != 0), None)
        if ende is None:
            ohne_ende += 1
            continue
        x = je_laeufer[z["ziel"]]
        name = (x["muster"], x["abstand"], x["echt"])
        treffer = ende[1]["da"] == 3 and ende[1]["boden"] == 9
        stat[name]["schuss"] += 1
        stat[name]["treffer"] += treffer
        stat[name]["flug"] += ende[0] - t0
        if t0 in lauf.u:
            bl = int(lauf.u[t0]["blick"][z["ziel"]])
            seite = "zu" if bl in (5, 6, 7) else "weg" if bl in (1, 2, 3) else "quer"
            richtung[(x["muster"], x["abstand"], x["echt"], seite)]["schuss"] += 1
            richtung[(x["muster"], x["abstand"], x["echt"], seite)]["treffer"] += treffer
    aus = ["Datei %s, Takte %d, Schuesse ohne Ende in der Aufnahme %d" % (os.path.basename(pfad), len(takte), ohne_ende)]
    aus.append("")
    aus.append("Bahn: Schuesse, getroffen, Trefferquote, gerechnet, Unterschied | Felder je 1000 Takte, Anteil am geraden Lauf, Befehle, nachgeschickt, Lebensverlust-Takte")
    grob = {}
    for x in b["bahnen"]:
        i = x["laeufer"]
        name = (x["muster"], x["abstand"], x["echt"])
        c = stat[name]
        n = c["schuss"]
        p = c["treffer"] / n if n else 0
        erwartung = None
        if x["muster"] in ar.MUSTER and not x["echt"]:  # gerechnet ist nur der direkte Befehl (16 Takte je Feld)
            r, _, _ = ar.rate(ar.MUSTER[x["muster"]], x["abstand"])
            erwartung = r
        # Weg und Leben aus den Einheiten je Takt
        felder = verlust = stand = 0
        vor = None
        for t in takte:
            if t < von:
                continue
            u = lauf.u[t]
            f_ = int(u["feld"][i])
            if vor is not None:
                felder += f_ != vor[0]
                verlust += int(u["leben"][i]) < vor[1]
                stand += int(u["lauf"][i]) != 2
            vor = (f_, int(u["leben"][i]))
        je = [t for t in takte if t >= von]
        tempo = 1000 * felder / max(len(je), 1)
        grob[name] = (p, n, tempo, erwartung)
        aus.append("  %-13s D=%2d%s: %3d %3d  %3.0f %% (+- %2.0f)  %s  %s | %5.1f  %3.0f %%  %3d %2d  %3d" % (x["muster"], x["abstand"], " echt" if x["echt"] else "     ", n, c["treffer"], p * 100, fehler(p, n), "%3.0f %%" % (erwartung * 100) if erwartung is not None else "  -  ", "%+4.0f" % ((p - erwartung) * 100) if erwartung is not None else "    ", tempo, 100 * tempo / (1000 / (12 if x["echt"] else FUSS)), len(x["befehle"]), x["nachgeschickt"], verlust))
    aus.append("")
    aus.append("Nach Laufrichtung (zu = auf den Schuetzen zu):")
    for n in sorted(richtung, key=str):
        c = richtung[n]
        if n[0] in ("laengs", "zick zu 2", "zick zu 1") and c["schuss"]:
            aus.append("  %-11s D=%2d%s %-4s %3d Schuss, %3.0f %%" % (n[0], n[1], " echt" if n[2] else "", n[3], c["schuss"], 100 * c["treffer"] / c["schuss"]))
    aus.append("")
    aus.append("Zickzack gegen geraden Lauf, gleicher Abstand (Punkte Unterschied, negativ heisst weniger Treffer):")
    for gerade, zick in (("quer", "zick quer 2"), ("quer", "zick quer 1"), ("laengs", "zick zu 2"), ("laengs", "zick zu 1")):
        for d in (12, 16):
            ist_echt = szene != "ausweichen"
            a, c = grob.get((gerade, d, ist_echt)), grob.get((zick, d, ist_echt))
            if a and c and a[1] and c[1]:
                aus.append("  %-11s gegen %-6s D=%2d: %+4.0f Punkte, %3.0f %% der Felder" % (zick, gerade, d, (c[0] - a[0]) * 100, 100 * c[2] / a[2] if a[2] else 0))
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "%s_ergebnis.txt" % szene), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
