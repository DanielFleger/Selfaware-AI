# -*- coding: utf-8 -*-
"""Wie viele Farmen passen hoechstens - und wo, moeglichst nah am Kornspeicher (M13b, 04.10.2026).

Grundlage ist die Platzkarte des Spiels (Modulbefehl "platzkarte"): fuer jede Stelle "+" = die
Spielpruefung erlaubt den Bau dort. Der Grundriss einer Farm (Groesse 10) beginnt an der Stelle
und reicht 10 Felder nach rechts und unten (gemessen 04.10.: Versatz (0,0) passt, alle anderen
nicht). Zwei Farmen stossen sich, wenn sich ihre Grundrisse ueberschneiden:
|dx| < 10 und |dy| < 10 (ob das Spiel zusaetzlich Abstand verlangt, prueft der Bau-Lauf).

Rechnung: Suche mit Schranke (branch and bound). Ziel = erst moeglichst viele Farmen, dann
moeglichst kurzer Weg (Summe der Abstaende Farm-Mitte -> Kornspeicher-Mitte).
Schranke: ein Gitter mit Maschenweite 10 trifft jeden 10x10-Grundriss in genau einem Punkt;
also hoechstens eine Farm je Gitterpunkt. Fuer jede der 100 Gitterlagen ergibt die Summe der
besten Werte je Gitterpunkt eine obere Grenze - die kleinste davon gilt. Findet die Suche
eine Loesung, die diese Grenze erreicht, ist sie bewiesen die beste.

Grenzen: gilt fuer die Platzkarte EINES Zeitpunkts (stehende Einheiten sperren, Baeume koennen
verschwinden) und nur fuer eine Farmgroesse; Mischungen kann dieses Werkzeug nicht.
Gemessen 04.10.: 9 berechnete Apfelplantagen, 5 davon lueckenlos aneinander, alle im Spiel gebaut.

Aufruf:  uv run python -m selfaware.macro.farmen_packen <platzkarte.txt> <x> <y> <radius> [groesse=10]
         (x, y = Kornspeicher-Mitte; radius = Schachbrett-Abstand Farm-Mitte -> x, y)
Als Baustein:  from farmen_packen import lies_karte, packe
"""
import math, sys, time

def lies_karte(pfad):
    z = open(pfad, encoding="utf-8").read().split("\n")
    kopf = dict(t.split("=") for t in z[0].split())
    x0, y0 = int(kopf["x0"]), int(kopf["y0"])
    return {(x0 + i, y0 + j) for j, r in enumerate(z[1:]) for i, c in enumerate(r) if c == "+"}

def _gruppen(kand, g):
    """Stellen, die sich nicht gegenseitig stoeren koennen, getrennt rechnen (Zusammenhangsteile)."""
    rest, teile = set(kand), []
    while rest:
        a = rest.pop(); teil, offen = [a], [a]
        while offen:
            p = offen.pop()
            nah = [q for q in rest if abs(p[0] - q[0]) < g and abs(p[1] - q[1]) < g]
            for q in nah:
                rest.discard(q); teil.append(q); offen.append(q)
        teile.append(sorted(teil, key=lambda p: (p[1], p[0])))
    return teile

def _suche(kand, g, wert, zeitgrenze):
    """Hoechste Summe von wert[] ohne Ueberschneidung. Schranke: Gitterpunkte (s. oben)."""
    lagen = [(ox, oy) for ox in range(g) for oy in range(g)]
    schl = {p: [((p[0] + (ox - p[0]) % g), (p[1] + (oy - p[1]) % g)) for ox, oy in lagen] for p in kand}

    def schranke(rest, noetig):
        """kleinste Gitter-Summe; bricht ab, sobald sie <= noetig ist (dann wird beschnitten)."""
        beste = None
        for i in range(len(lagen)):
            je = {}
            for p in rest:
                k = schl[p][i]
                if wert[p] > je.get(k, -1.0):
                    je[k] = wert[p]
            s = sum(je.values())
            if beste is None or s < beste:
                beste = s
                if s <= noetig:
                    return s
        return beste or 0.0

    best = {"wert": 0.0, "wahl": []}
    for p in sorted(kand, key=lambda p: -wert[p]):           # Startloesung: gierig nach Wert
        if all(abs(p[0] - q[0]) >= g or abs(p[1] - q[1]) >= g for q in best["wahl"]):
            best["wahl"].append(p)
    best["wert"] = sum(wert[p] for p in best["wahl"])
    t0, knoten, abgebrochen = time.time(), [0], [False]

    def rek(rest, wahl, summe):
        knoten[0] += 1
        if summe > best["wert"] + 1e-9:
            best["wert"], best["wahl"] = summe, list(wahl)
        if not rest:
            return
        if time.time() - t0 > zeitgrenze:
            abgebrochen[0] = True
            return
        if summe + schranke(rest, best["wert"] - summe + 1e-9) <= best["wert"] + 1e-9:
            return
        a = rest[0]
        rek([p for p in rest[1:] if abs(p[0] - a[0]) >= g or abs(p[1] - a[1]) >= g], wahl + [a], summe + wert[a])
        rek(rest[1:], wahl, summe)

    rek(kand, [], 0.0)
    return best["wahl"], not abgebrochen[0], knoten[0], schranke(kand, -1)

def packe(stellen, cx, cy, radius, g=10, zeitgrenze=120.0):
    h = (g - 1) / 2.0
    kand = [p for p in stellen if max(abs(p[0] + h - cx), abs(p[1] + h - cy)) <= radius]
    abstand = {p: math.hypot(p[0] + h - cx, p[1] + h - cy) for p in kand}
    t0 = time.time()
    wahl, bewiesen, knoten, schr_anzahl = [], True, 0, 0
    for teil in _gruppen(kand, g):
        eins = {p: 1.0 for p in teil}
        w1, ok1, k1, s1 = _suche(teil, g, eins, zeitgrenze)        # 1. Schritt: hoechste Anzahl
        n = len(w1)
        gross = 1000.0                                             # 2. Schritt: bei dieser Anzahl kuerzester Weg
        w = {p: gross - abstand[p] for p in teil}
        w2, ok2, k2, _ = _suche(teil, g, w, zeitgrenze)
        if len(w2) < n:                                            # darf nicht passieren - dann Schritt 1 behalten
            w2, ok2 = w1, False
        wahl += w2; bewiesen = bewiesen and ok1 and ok2; knoten += k1 + k2; schr_anzahl += s1
    gierig = []
    for p in sorted(kand, key=lambda p: abstand[p]):
        if all(abs(p[0] - q[0]) >= g or abs(p[1] - q[1]) >= g for q in gierig):
            gierig.append(p)
    return {"kandidaten": len(kand), "gierig": gierig, "wahl": sorted(wahl, key=lambda p: abstand[p]),
            "schranke": int(round(schr_anzahl)), "bewiesen": bewiesen, "knoten": knoten,
            "sekunden": round(time.time() - t0, 1), "abstand": {p: round(abstand[p], 1) for p in kand}}

def bild(stellen, wahl, g=10, extra=None):
    """Textkarte: + moegliche Stelle, A..Z gewaehlte Farmen (Grundriss), K/B fuer extra-Punkte."""
    xs = [p[0] for p in stellen] + [p[0] + g for p in wahl]; ys = [p[1] for p in stellen] + [p[1] + g for p in wahl]
    feld = {}
    for p in stellen:
        feld[p] = "+"
    for i, (x, y) in enumerate(wahl):
        for a in range(g):
            for b in range(g):
                feld[(x + a, y + b)] = chr(65 + i % 26)
    for (x, y), c in (extra or {}).items():
        feld[(x, y)] = c
        xs.append(x); ys.append(y)
    zeilen = ["%3d " % y + "".join(feld.get((x, y), ".") for x in range(min(xs), max(xs) + 1))
              for y in range(min(ys), max(ys) + 1)]
    return "\n".join(zeilen + ["    x ab %d" % min(xs)])

if __name__ == "__main__":
    pfad, cx, cy, r = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
    g = int(sys.argv[5]) if len(sys.argv) > 5 else 10
    e = packe(lies_karte(pfad), cx, cy, r, g)
    n, ng = len(e["wahl"]), len(e["gierig"])
    print("Umkreis %g um (%g,%g): %d moegliche Stellen" % (r, cx, cy, e["kandidaten"]))
    print("gierig (immer die naechste): %d Farmen, Weg-Summe %.0f" % (ng, sum(e["abstand"][p] for p in e["gierig"])))
    print("beste Packung: %d Farmen (Gitter-Grenze %d), Weg-Summe %.0f, %s (%d Knoten, %.1f s)" % (
        n, e["schranke"], sum(e["abstand"][p] for p in e["wahl"]),
        "bewiesen beste fuer DIESE Platzkarte" if e["bewiesen"] else "Zeitgrenze erreicht - nicht bewiesen", e["knoten"], e["sekunden"]))
    print("   Stellen:", " ".join("(%d,%d)" % p for p in e["wahl"]))
