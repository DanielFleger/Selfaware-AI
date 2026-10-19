# -*- coding: utf-8 -*-
"""Wertet data/research/arbeitsgang_<zeit>.json aus (siehe arbeitsgang_messen.py). Neu geschrieben 06.10. 20:36: die erste
Fassung zaehlte jedes Feld ab 10 Ticks als Halt - Laufen dauert aber ~24 Ticks je Feld.

Je Arbeiter, aus den Orten alle 2 Ticks:
  - Felder: wie lange stand er auf jedem Feld, und mit welchem Schritt kam er hinein (gerade/schraeg);
  - Laufzeit je Feld = haeufigste Dauer (gerade und schraeg getrennt);
  - Halt = Aufenthalt >= HALT Ticks (deutlich laenger als Laufen) mit naechstem Gebaeude -> Arbeits-/Abholzeiten;
  - Gaenge zwischen zwei Halten: Ticks, gelaufene Felder, kuerzester Weg der Weg-Ebene;
  - Lauftest: Schritte, die die Weg-Ebene verbietet (mit Ziel-Gebaeude, damit man sieht, WO).
Aufruf: uv run python -m selfaware.tools.analysis.arbeitsgang_auswerten [data/research/arbeitsgang_....json]
"""

from selfaware import workspace as _workspace
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.services.wegkarte as W

D = os.path.join(_workspace.DATA)
NAMEN = {10: "Lager", 26: "Markt", 11: "Waffenlager", 13: "Schmiede", 16: "Gerberei", 33: "Milchviehhof", 41: "Bergfried",
         55: "Feuer", 1: "Huette", 71: "Tuer", 72: "Tuer", 73: "Tuer"}
GROESSE = {10: 2, 26: 5, 11: 4, 13: 4, 16: 4, 33: 10, 41: 7, 55: 7, 1: 4, 71: 1, 72: 1, 73: 1}
BIT = {v: k for k, v in W.RICHTUNG.items()}
HALT = 60


def reihen(ew):
    s = defaultdict(list)
    for z in ew:
        m = re.search(r"EW Orte Tick (\d+): (.*)", z)
        if m:
            t = int(m.group(1))
            for nr, x, y in re.findall(r"(\d+)@\((-?\d+),(-?\d+)\)", m.group(2)):
                s[int(nr)].append((t, int(x), int(y)))
    return s


def felder(reihe):
    """[(feld, von, bis, schritt_hinein)] - schritt_hinein = (dx, dy) vom vorigen Feld, None beim ersten."""
    aus, start, vor_feld = [], reihe[0], None
    for a, b in zip(reihe, reihe[1:] + [None]):
        if b is None or b[1:] != a[1:]:
            schritt = (start[1] - vor_feld[0], start[2] - vor_feld[1]) if vor_feld else None
            aus.append((start[1:], start[0], (b or a)[0], schritt))
            vor_feld = start[1:]
            start = b
    return aus


def naechstes(gebaeude, x, y):
    best = None
    for n, g in gebaeude.items():
        gr = GROESSE.get(g["typ"], 4)
        d = max(max(g["x"] - x, 0, x - (g["x"] + gr - 1)), max(g["y"] - y, 0, y - (g["y"] + gr - 1)))
        if best is None or d < best[0]:
            best = (d, "%s %s" % (NAMEN.get(g["typ"], "Typ%d" % g["typ"]), n))
    return best


def main():
    pfad = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob(os.path.join(D, "arbeitsgang_2*[0-9].json")))[-1]
    erg = json.load(open(pfad, encoding="utf-8"))
    k = W.lesen(pfad.replace(".json", "_wegkarte.txt"))
    gebaeude = {int(n): g for n, g in erg.get("gebaeude_liste", {}).items()}
    aus = {"datei": os.path.basename(pfad), "halt_ab": HALT, "arbeiter": {}}
    for nr, reihe in sorted(reihen(erg.get("ew", [])).items()):
        name = erg["arbeiter"].get(str(nr), "?")
        F = felder(reihe)
        gerade = Counter(b - a for _, a, b, s in F if s and max(map(abs, s)) == 1 and 0 in s and b - a < HALT)
        schraeg = Counter(b - a for _, a, b, s in F if s and max(map(abs, s)) == 1 and 0 not in s and b - a < HALT)
        verstoss = []
        for (x, y), a, b, s in F:
            if s and max(map(abs, s)) == 1:
                q = (x - s[0], y - s[1])
                v, z = k["f"].get(q), k["f"].get((x, y))
                if v is not None and not v[0] & BIT[s]:
                    verstoss.append({"t": a, "von": q, "nach": (x, y), "nach_gebaeude": W.kurzname(z[5]) if z and z[1] else "Boden"})
        halte = [{"von": a, "bis": b, "dauer": b - a, "feld": f, "bei": naechstes(gebaeude, *f)[1] if gebaeude else "?",
                  "abstand": naechstes(gebaeude, *f)[0] if gebaeude else None} for f, a, b, s in F if b - a >= HALT]
        gaenge = []
        for h1, h2 in zip(halte, halte[1:]):
            n = sum(1 for f, a, b, s in F if h1["bis"] <= a < h2["von"] and s)
            w = W.weg(k, tuple(h1["feld"]), tuple(h2["feld"]))
            gaenge.append({"von": h1["bei"], "nach": h2["bei"], "ticks": h2["von"] - h1["bis"], "felder": n,
                           "kuerzest": (len(w) - 1) if w else None})
        e = {"name": name, "felder": len(F), "laufzeit_gerade": gerade.most_common(3), "laufzeit_schraeg": schraeg.most_common(3),
             "verstoesse": verstoss, "halte": halte, "gaenge": gaenge}
        aus["arbeiter"][str(nr)] = e
        print("%s %d: %d Felder; Ticks je Feld gerade %s, schraeg %s; verbotene Schritte %d (%s)" % (
            name, nr, len(F), gerade.most_common(2), schraeg.most_common(2), len(verstoss),
            ", ".join(sorted({v["nach_gebaeude"] for v in verstoss})) or "-"))
        for h in halte:
            print("   Halt %5d-%5d %5d Ticks  bei %-16s (Abstand %s)  Feld %s" % (h["von"], h["bis"], h["dauer"], h["bei"],
                                                                                 h["abstand"], tuple(h["feld"])))
        for g in gaenge:
            print("   Gang %-16s -> %-16s %5d Ticks, %3d Felder, kuerzest %s" % (g["von"], g["nach"], g["ticks"], g["felder"],
                                                                                 g["kuerzest"]))
    # Plan gegen Messung (aufbau_bauen.py): Arbeitsfeld = laengster Halt; Plan-Eingang mit Abstand <= 1 zuordnen
    if "plan" in erg:
        geplant = [("Schmiede", s2) for s2 in erg["plan"].get("schmiede", []) if "eingang" in s2] +                   [("Gerberei", s2) for s2 in erg["plan"].get("gerber", []) if "eingang" in s2]
        vergleich = []
        for nr, e in aus["arbeiter"].items():
            if not e["halte"] or not e["gaenge"]:
                continue
            arbeit = max(e["halte"], key=lambda h: h["dauer"])["feld"]
            treffer = [(a, s2) for a, s2 in geplant if max(abs(s2["eingang"][0] - arbeit[0]), abs(s2["eingang"][1] - arbeit[1])) <= 1]
            gemessen = sorted(g["felder"] for g in e["gaenge"])
            mitte = gemessen[len(gemessen) // 2]
            arbeitszeit = sorted(h["dauer"] for h in e["halte"])[len(e["halte"]) // 2]
            v = {"arbeiter": nr, "name": e["name"], "arbeitsfeld": arbeit, "gaenge": len(gemessen),
                 "gang_felder_median": mitte, "arbeit_median": arbeitszeit,
                 "geplant": treffer[0][1].get("gang_felder") if treffer else None}
            vergleich.append(v)
            print("VERGLEICH %-8s %s Feld %s: Gang gemessen %s Felder (Median aus %d), geplant %s; Halt-Median %s Ticks" % (
                e["name"], nr, tuple(arbeit), mitte, len(gemessen), v["geplant"], arbeitszeit))
        aus["vergleich"] = vergleich
    b = erg.get("bestand", [])
    if b:
        aus["bestand"] = [b[0], b[-1]]
        print("Bestand: Start %s  Ende %s" % (b[0], b[-1]))
    ziel = pfad.replace(".json", "_auswertung.json")
    json.dump(aus, open(ziel, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("Auswertung:", ziel)


if __name__ == "__main__":
    main()
