# -*- coding: utf-8 -*-
"""Gegenprobe zum Lauf ausweichen: Sind die Schuesse unabhaengig, und warum trifft der echte Befehl so anders?

Fragen, vorher aufgeschrieben:
  1. Rastern die Schuesse ein? Je Bahn und Schuetze: Schuesse, Treffer, Abstand zweier Schuesse, Lage des Schusses im Takt des Laufmusters. Schiesst jeder Schuetze immer in derselben Phase, zaehlen 44 Schuesse nicht als 44 unabhaengige Proben.
  2. Warum ist der echte Befehl schneller? Tempo-Felder und Takte je Feld, echt gegen direkt.
  3. Wohin zielt das Spiel beim echten Befehl? Abstand des Zielpunkts vom Ort des Laeufers bei der Landung.
Ausgabe: ausweichen_gegenprobe.txt
"""
import collections
import glob
import json
import os
import statistics as st
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
sys.path.insert(0, os.path.join(HIER, "..", "streuung_20261104"))
import flug_pruefen as fp  # noqa: E402
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte  # noqa: E402

fp.U_F.update({"blick": "facingDirection", "lauf": "tunnelerFinishedDigging", "ts": "stateBasedSpeed", "tl": "calculatedMovementSpeed", "mxx": "microXPosition", "myy": "microYPosition"})


def main():
    pfad = sorted(glob.glob(os.path.join(HIER, "..", "laeufe", "lauf_s_*_ausweichen.auge")), key=os.path.getmtime)[-1]
    k = Feldkarte.laden(feldliste=FELDLISTE)
    lauf = fp.Lauf(pfad, k)
    b = [json.loads(z) for z in open(os.path.join(HIER, "lauf_ausweichen.log"), encoding="utf-8", errors="replace") if z.startswith('{"schritt": "ausweichen_bahnen"')][-1]
    von = b["von"] + 150
    aus = []
    takte = sorted(lauf.u)
    # 2. Tempo
    aus.append("Tempo der Laeufer: Bahn, Anzahl (stateBasedSpeed, calculatedMovementSpeed, laeuft), Takte je Feld (Median)")
    for x in b["bahnen"]:
        i = x["laeufer"]
        c = collections.Counter()
        wechsel = []
        vor = None
        for t in takte:
            if t < von:
                continue
            u = lauf.u[t]
            c[(int(u["ts"][i]), int(u["tl"][i]), int(u["lauf"][i]))] += 1
            f = int(u["feld"][i])
            if vor is not None and f != vor:
                wechsel.append(t)
            vor = f
        d = [q - p for p, q in zip(wechsel, wechsel[1:])]
        if x["muster"] in ("quer", "zick quer 1", "zick zu 1", "stand"):
            aus.append("  %-12s D=%2d%s: %s Takte je Feld %s" % (x["muster"], x["abstand"], " echt" if x["echt"] else "", c.most_common(3), st.median(d) if d else "-"))
    # 1. und 3. je Schuss
    aus.append("")
    aus.append("Je Bahn: Schuetze (Nr): Schuesse/Treffer | Abstand zweier Schuesse (Median) | Lage im Muster (Takt des Schusses modulo Laenge eines Abschnitts): Anzahl verschiedener Lagen")
    je_laeufer = {x["laeufer"]: x for x in b["bahnen"]}
    daten = collections.defaultdict(lambda: collections.defaultdict(list))
    fehl = collections.defaultdict(list)
    for s, f in lauf.fluege.items():
        z = f[0][1]
        t0 = f[0][0]
        if z["art"] != 1 or z["ziel"] not in je_laeufer or t0 < von:
            continue
        ende = next(((t, q) for t, q in f[1:] if q["da"] != 2 or q["boden"] != 0), None)
        if ende is None:
            continue
        x = je_laeufer[z["ziel"]]
        tr = ende[1]["da"] == 3 and ende[1]["boden"] == 9
        daten[(x["muster"], x["abstand"], x["echt"])][z["sch"]].append((t0, tr))
        if not tr and ende[0] in lauf.u:
            i = z["ziel"]
            u = lauf.u[ende[0]]
            fehl[(x["muster"], x["abstand"], x["echt"])].append(max(abs(int(u["x"][i]) - (ende[1]["mx"] >> 3)), abs(int(u["y"][i]) - (ende[1]["my"] >> 3))))
    for x in b["bahnen"]:
        name = (x["muster"], x["abstand"], x["echt"])
        if x["muster"] not in ("zick quer 1", "zick zu 1", "quer", "laengs") or x["abstand"] != 12:
            continue
        zeile = []
        lang = 16 if not x["echt"] else 12
        for sch, l in sorted(daten[name].items()):
            ts = sorted(t for t, _ in l)
            d = [q - p for p, q in zip(ts, ts[1:])]
            lagen = len({t % lang for t in ts})
            zeile.append("%d: %d/%d | %s | %d" % (sch, len(l), sum(tr for _, tr in l), st.median(d) if d else "-", lagen))
        aus.append("  %-12s D=%2d%s  %s" % (x["muster"], x["abstand"], " echt" if x["echt"] else "", "  ;  ".join(zeile)))
    aus.append("")
    aus.append("Fehlschuesse: Abstand in Feldern zwischen Laeufer und Geschoss am Ende (Median), je Bahn")
    for x in b["bahnen"]:
        name = (x["muster"], x["abstand"], x["echt"])
        if fehl[name]:
            aus.append("  %-12s D=%2d%s: %s von %d" % (x["muster"], x["abstand"], " echt" if x["echt"] else "", st.median(fehl[name]), len(fehl[name])))
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "ausweichen_gegenprobe.txt"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
