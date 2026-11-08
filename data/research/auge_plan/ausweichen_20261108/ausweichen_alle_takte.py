# -*- coding: utf-8 -*-
"""Szene ausweichen: Trefferquote fuer jeden Takt als moeglichen Schusstakt (B-173).

Warum: Die Schuetzen schiessen alle 129 Takte, jede Bahn hat nur 44 Schuesse, und die vier Schuetzen einer Bahn schiessen gleichzeitig. Der Flug-Nachbau stimmte auf dieser Aufnahme in 25.106 Flugtakten ohne Abweichung (flug_pruefung_ausweichen.txt).
Darum wird hier mit der ECHTEN Spur des Laeufers aus der Aufzeichnung fuer jeden Takt und jeden Schuetzen gerechnet: Zielpunkt mit Vorhalt, Flug, Treffer im Feld unter Boden + 42.
Gegenprobe im selben Lauf: Die Rechnung wird auch an den wirklich abgefeuerten Pfeilen gehalten. Stimmt dort der Zielpunkt oder das Ergebnis nicht, gilt die Zeile nicht.
Grenzen: Nur der Laeufer zaehlt als Opfer. Das Gelaende ist der Stand am Anfang der Aufnahme.
Aufruf: ausweichen_alle_takte.py <Szene>, zum Beispiel ausweichen oder ausweichen2. Ausgabe: <Szene>_alle_takte.txt
"""
import collections
import glob
import json
import math
import os
import sys

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
sys.path.insert(0, os.path.join(HIER, "..", "streuung_20261104"))
import flug_modell as fm  # noqa: E402
import flug_pruefen as fp  # noqa: E402
import streuung_modell as sm  # noqa: E402
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte  # noqa: E402

fp.U_F.update({"blick": "facingDirection", "lauf": "tunnelerFinishedDigging", "ts": "stateBasedSpeed", "tl": "calculatedMovementSpeed", "mxx": "microXPosition", "myy": "microYPosition"})
EINLAUF, ART = 150, 1
AUFSCHLAG = 30  # Zielhoehe und Abschusshoehe ueber dem Boden der Einheit bei Pfeilen (ziel_pruefung.txt)


def zielpunkt(q, sch, i):
    ez = int(q["hb"][i]) + int(q["ht"][i])
    ab = max(abs(int(q["mxx"][sch]) - int(q["mxx"][i])), abs(int(q["myy"][sch]) - int(q["myy"][i]))) - 1
    x, y, _ = sm.zielpunkt_einheit(int(q["x"][i]), int(q["y"][i]), ez, int(q["lauf"][i]) == 2, int(q["blick"][i]), ab, int(q["ts"][i]), int(q["tl"][i]))
    return x, y, ez + AUFSCHLAG


def rechnen(lauf, boden, zeilen, sch, i, t0, q):
    """Ein Pfeil im Takt t0 von Schuetze sch auf Einheit i. Rueckgabe: getroffen oder nicht, None wenn die Aufnahme zu Ende ist."""
    zx, zy, zz = zielpunkt(q, sch, i)
    sx, sy = int(q["mxx"][sch]), int(q["myy"][sch])
    h0 = int(q["hb"][sch]) + int(q["ht"][sch]) + AUFSCHLAG
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
        feld, unten = int(u["feld"][i]), int(u["hb"][i]) + int(u["ht"][i])
        for a, c, h, _wg in schritte:
            kn = int(zeilen[c >> 3]) + (a >> 3)
            if kn == feld and unten <= h <= unten + fm.fenster(71):
                return True
            if h < int(boden[kn]):
                return False
        if h_e < 3:
            return False
    return False


def main():
    szene = sys.argv[1] if len(sys.argv) > 1 else "ausweichen"
    pfad = sorted(glob.glob(os.path.join(HIER, "..", "laeufe", "lauf_s_*_%s.auge" % szene)), key=os.path.getmtime)[-1]
    k = Feldkarte.laden(feldliste=FELDLISTE)
    lauf = fp.Lauf(pfad, k)
    zeilen = fp.zeilen_lesen()
    boden = lauf.gel[0][1]["hoehe"]
    b = [json.loads(z) for z in open(os.path.join(HIER, "lauf_%s.log" % szene), encoding="utf-8", errors="replace") if z.startswith('{"schritt": "ausweichen_bahnen"')][-1]
    von, bis = b["von"] + EINLAUF, b["bis"] - 40
    je_laeufer = {x["laeufer"]: x for x in b["bahnen"]}
    # Gegenprobe an den wirklichen Pfeilen
    probe = collections.Counter()
    wirklich = collections.defaultdict(collections.Counter)
    for s, f in lauf.fluege.items():
        z = f[0][1]
        t0 = f[0][0]
        if z["art"] != ART or z["ziel"] not in je_laeufer or t0 < von or t0 not in lauf.u or t0 - 1 not in lauf.u:
            continue
        ende = next(((t, q) for t, q in f[1:] if q["da"] != 2 or q["boden"] != 0), None)
        if ende is None:
            continue
        tr = ende[1]["da"] == 3 and ende[1]["boden"] == 9
        x = je_laeufer[z["ziel"]]
        w = wirklich[(x["muster"], x["abstand"], x["echt"])]
        w["schuss"] += 1
        w["treffer"] += tr
        for name, q in (("Takt", lauf.u[t0]), ("Takt davor", lauf.u[t0 - 1])):
            pz = zielpunkt(q, z["sch"], z["ziel"])
            probe[(name, "Zielpunkt gleich")] += pz[:2] == (z["zx"], z["zy"])
            e = rechnen(lauf, boden, zeilen, z["sch"], z["ziel"], t0, q)
            probe[(name, "Ergebnis gleich")] += e == tr
            probe[(name, "Pfeile")] += 1
    wahl = max(("Takt", "Takt davor"), key=lambda n: probe[(n, "Zielpunkt gleich")])
    aus = ["Datei %s, Takte %d bis %d" % (os.path.basename(pfad), von, bis), "Gegenprobe an den wirklichen Pfeilen: %s" % sorted(probe.items()), "Rechnung mit dem Stand: %s" % wahl, ""]
    aus.append("Bahn: wirkliche Schuesse und Quote | jeder Takt, jeder Schuetze: Schuesse und Quote")
    ergebnis = {}
    for x in b["bahnen"]:
        i = x["laeufer"]
        tr = n = 0
        for t in range(von, bis):
            q = lauf.u.get(t if wahl == "Takt" else t - 1)
            if q is None:
                continue
            for sch in x["schuetzen"]:
                e = rechnen(lauf, boden, zeilen, sch, i, t, q)
                if e is not None:
                    n += 1
                    tr += e
        name = (x["muster"], x["abstand"], x["echt"])
        w = wirklich[name]
        ergebnis[name] = tr / n if n else None
        aus.append("  %-12s D=%2d%s:  %3d  %3.0f %%  |  %6d  %5.1f %%" % (x["muster"], x["abstand"], " echt" if x["echt"] else "     ", w["schuss"], 100 * w["treffer"] / w["schuss"] if w["schuss"] else 0, n, 100 * tr / n if n else 0))
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "%s_alle_takte.txt" % szene), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
