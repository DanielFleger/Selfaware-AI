# -*- coding: utf-8 -*-
"""Ertragsformel je Nahrungsgebaeude aus einer Arbeitsgang-Messung (SAI 11.10., Daniel 17:12: "per Tick per Entfernung -
dann weisst du, wie viel mehr Ertrag es pro Feld Naehe gibt; damit kann man eine maximal effektive, kompakte Burg
berechnen").

Neu geschrieben 17:36: die erste Fassung zaehlte Besuche nach Naehe zum Gebaeude - Schritte auf dem eigenen Feld liefen als
Weg mit (Aepfel 10 statt ~17 Ticks je Feld), und wer am Lager vorbeilief, galt als Besucher. Jetzt aus den ZIELWECHSELN
des Spiels ("EW Tick t: nr Ziel (a)->(b) bei (c)"): jeder Gang hat einen festen Start, ein festes Ziel und eine Ankunft
(erste Ortsmeldung AUF dem Ziel). Nummern werden wiederverwendet (17:32: Nr. 1 erst Apfel-, dann Milchbauer) - darum
wird jeder Gang nach seinem Start (naechster Arbeitsort) eingeordnet, nicht nach der Nummer.

Je Ware: Ablieferungen = Gaenge ZUM Kornspeicher-Eingang (bzw. Lagerteil), Umlauf = Zeit zwischen zwei Abgaengen derselben
Einheit zur Ablage, Hin-/Rueckweg (Ticks, Schritte), Arbeitszeit = Umlauf - Hinweg - Rueckweg, Ladung = Bestandszuwachs /
Ablieferungen. Formel: Ertrag je 1.000 Ticks = 1000 * Ladung / (Arbeitszeit + 2 * Schritte * Ticks_je_Schritt).
Gegenprobe (vorher festgelegt): Formel trifft die Rate dieses Laufs UND die lange Messung (lauf5, andere Wege) auf 20 %.
Aufruf: uv run python -m selfaware.tools.analysis.nahrung_formel [data/research/arbeitsgang_nahrung_....json]"""

from selfaware import workspace as _workspace
import glob
import json
import os
import re
import statistics as S
import sys
from collections import defaultdict

D = os.path.join(_workspace.DATA)
# Ware je Arbeitsort; Ablage "korn" = Kornspeicher, "lager" = Lagerteil
WARE = {"apfel": ("apfel", "korn"), "milch": ("kaese", "korn"), "jaeger": ("fleisch", "korn"), "baeckerei": ("brot", "korn"),
        "getreide": ("weizen", "lager"), "muehle": ("mehl", "lager")}


def lesen(ew):
    ziele, orte = defaultdict(list), defaultdict(list)
    for z in ew:
        m = re.search(r"EW Tick (\d+): (\d+) Ziel \(\S+?\)->\((-?\d+),(-?\d+)\) bei \((-?\d+),(-?\d+)\)", z)
        if m:
            t, nr, zx, zy, bx, by = map(int, m.groups())
            ziele[nr].append((t, (zx, zy), (bx, by)))
            continue
        m = re.search(r"EW Orte Tick (\d+): (.*)", z)
        if m:
            t = int(m.group(1))
            for nr, x, y in re.findall(r"(\d+)@\((-?\d+),(-?\d+)\)", m.group(2)):
                orte[int(nr)].append((t, int(x), int(y)))
    return ziele, orte


def gaenge(ziele, orte):
    """Je Einheit: [(abgang, start, ziel, ankunft, schritte)] - ankunft None, wenn das Ziel nie erreicht wurde."""
    erg = defaultdict(list)
    for nr, zs in ziele.items():
        sp = orte.get(nr, [])
        for i, (t0, ziel, start) in enumerate(zs):
            ank, schritte, letzt, los = None, 0, start, None
            for t, x, y in sp:
                if t < t0:
                    continue
                if (x, y) != letzt:
                    schritte += 1
                    letzt = (x, y)
                    los = los or t
                if (x, y) == ziel:
                    ank = t
                    break
            danach = zs[i + 1][1] if i + 1 < len(zs) else None
            erg[nr].append((t0, start, ziel, ank, schritte, los, danach))
    return erg


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def main():
    pfad = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob(os.path.join(D, "arbeitsgang_nahrung_2*[0-9].json")))[-1]
    d = json.load(open(pfad, encoding="utf-8"))
    g = {n: tuple(o) for n, o in d["gebaeude"].items() if o}
    ziele, orte = lesen(d["ew"])
    alle = gaenge(ziele, orte)
    # Ablage-Eingaenge MESSEN statt annehmen: haeufigstes Gang-Ziel nahe Kornspeicher bzw. nahe den Lagerteilen
    zielzahl = defaultdict(int)
    for gs in alle.values():
        for _, _, ziel, ank, *_ in gs:
            if ank:
                zielzahl[ziel] += 1
    korn = max((z for z in zielzahl if schach(z, g["kornspeicher"]) <= 6), key=zielzahl.get)
    lager = {z for z in zielzahl if schach(z, g.get("lager_anbau", (145, 259))) <= 6 or schach(z, (145, 264)) <= 6}
    werke = {n: o for n, o in g.items() if n in WARE}

    def werk_von(p, danach=None):
        n = min(werke, key=lambda n: schach(p, werke[n]))
        if danach is not None and schach(p, werke[n]) > 4:
            return min(werke, key=lambda m: schach(danach, werke[m]))
        return n
    # Zuordnung der Gaenge
    hin = defaultdict(list)          # werk -> [(abgang, ankunft, schritte, nr, start)]
    zur = defaultdict(list)          # werk -> [(abgang, ankunft, schritte)]
    for nr, gs in alle.items():
        for (t0, start, ziel, ank, sch, los, danach) in gs:
            if not ank:
                continue
            if ziel == korn:
                hin[werk_von(start, danach)].append((t0, ank, sch, nr, start, los))
            elif ziel in lager and schach(start, korn) > 3:
                w = werk_von(start, danach)
                if WARE[w][1] == "lager":
                    hin[w].append((t0, ank, sch, nr, start, los))
            elif schach(start, korn) <= 1 or start in lager:
                zur[werk_von(ziel)].append((t0, ank, sch, los))
    best = d["bestand"]
    p5 = os.path.join(D, "nahrung_messung_ascension_lauf5_20000.json")
    l5 = json.load(open(p5, encoding="utf-8")) if os.path.exists(p5) else None
    print("Datei:", os.path.basename(pfad), "| Kornspeicher-Eingang", korn, "| Lagerteile", sorted(lager))
    erg = {}
    for werk in ("apfel", "milch", "jaeger", "baeckerei", "getreide", "muehle"):
        ware, ablage = WARE[werk]
        h = sorted(hin.get(werk, []))
        if len(h) < 2:
            print("%-10s zu wenig Ablieferungen (%d)" % (werk, len(h)))
            continue
        # Umlauf: Abstand zweier Abgaenge DERSELBEN Einheit zur Ablage
        je = defaultdict(list)
        for t0, ank, sch, nr, _, _ in h:
            je[nr].append(t0)
        umlauf = [b - a for ts in je.values() for a, b in zip(ts, ts[1:])]
        hw = [(a - t0, s) for t0, a, s, _, _, _ in h]
        rw = [(a - t0, s) for t0, a, s, _ in zur.get(werk, [])]
        tps = S.median([(a - l) / s for t0, a, s, *_r, l in [(x[0], x[1], x[2], x[5]) for x in h] + list(zur.get(werk, [])) if s > 1 and l])
        anlauf = S.median([l - t0 for t0, a, s, *_r, l in [(x[0], x[1], x[2], x[5]) for x in h] if l])
        schritte = S.median([s for _, s in hw])
        hinweg, rueckweg = S.median([t for t, _ in hw]), (S.median([t for t, _ in rw]) if rw else S.median([t for t, _ in hw]))
        u = S.median(umlauf) if umlauf else None
        arbeit = u - hinweg - rueckweg if u else None
        zuwachs = sum(max(0, b[ware] - a[ware]) for a, b in zip(best, best[1:])) if ablage == "korn" else None
        ladung = zuwachs / len(h) if zuwachs is not None else None
        rate = 1000.0 * zuwachs / (best[-1]["t"] - best[0]["t"]) if zuwachs is not None else None
        e = dict(ablieferungen=len(h), umlauf=u, anlauf_hinweg=anlauf, hinweg=hinweg, rueckweg=rueckweg, schritte=schritte,
                 ticks_je_schritt=round(tps, 1), arbeitszeit=arbeit, ladung=round(ladung, 2) if ladung else None,
                 rate_ganzer_lauf=round(rate, 2) if rate is not None else None,
                 schach_zur_ablage=schach(werke[werk], korn if ablage == "korn" else min(lager, key=lambda z: schach(z, werke[werk]))))
        zeile = "%-10s %2d Ablief., Umlauf %s, Hinweg %d (Anlauf %d) / Rueckweg %d Ticks, %d Schritte (Schach %d), %.1f Ticks/Schritt, Arbeit %s, Ladung %s" % (
            werk, len(h), u, hinweg, anlauf, rueckweg, schritte, e["schach_zur_ablage"], tps, arbeit, e["ladung"])
        if ladung and arbeit is not None:
            f = lambda sch, L=ladung, A=arbeit, T=tps: 1000.0 * L / (A + 2 * sch * T)
            e["formel_hier"] = round(f(schritte), 2)
            e["rate_dauerbetrieb"] = round(1000.0 * ladung / u, 2)
            zeile += " | Dauerbetrieb %.2f, Formel %.2f" % (e["rate_dauerbetrieb"], e["formel_hier"])
            name5 = {"apfel": "apfel", "milch": "kaese", "jaeger": "fleisch", "baeckerei": "brot"}[werk]
            weg5 = (l5 or {}).get("wege_zum_kornspeicher", {}).get(werk)
            ist5 = (l5 or {}).get("ertrag", {}).get(name5, {}).get("je_1000_ticks")
            if weg5 and ist5:
                sch5 = weg5 * schritte / max(e["schach_zur_ablage"], 1)        # Schritte je Schachfeld aus diesem Lauf
                vor = f(sch5)
                e["lauf5"] = dict(weg_schach=weg5, gemessen=ist5, formel=round(vor, 2), abweichung=round(100 * (vor - ist5) / ist5))
                zeile += " | Lauf5 (Schach %d): gemessen %.2f, Formel %.2f (%+d %%)" % (weg5, ist5, vor, e["lauf5"]["abweichung"])
        erg[werk] = e
        print(zeile)
    json.dump(erg, open(pfad.replace(".json", "_formel.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
