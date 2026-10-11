# -*- coding: utf-8 -*-
"""Formel je Rohstoff aus einer Arbeitsgang-Messung (arbeitsgang_rohstoff.py, SAI 12.10.).

Je Arbeiter die Gaenge aus den Zielwechseln des Spiels (wie nahrung_formel.py): ein Gang ZUM Lager (Ziel hoechstens
LAGER_R Felder neben einem Lagerteil) ist eine Ablieferung. Der Arbeiter gehoert zu dem Betrieb, an dem er die meiste Zeit
stand. Umlauf = Abstand zweier Ablieferungen desselben Arbeiters. Je Betrieb: Median-Umlauf und Abstand (Schach) zum Lager.
Je Art: Gerade Umlauf(d) = fest + je_feld * d durch die Betriebe (kleinste Quadrate); Ladung je Ablieferung = (Zugang +
Verkauf) / Ablieferungen. Ertrag je Betrieb und 1.000 Ticks = 1000 * Ladung / Umlauf(d).
Gegenprobe (vorher festgelegt in arbeitsgang_rohstoff.py): Summe der Formel-Ertraege der Betriebe gegen die Bestandsrate
desselben Laufs (ab der ersten Ablieferung) - Abweichung hoechstens 20 %, sonst "WIDERLEGT".
Aufruf: python werkzeug/rohstoff_formel.py [daten/arbeitsgang_rohstoff_....json]"""
import glob
import json
import os
import statistics as S
import sys
from collections import defaultdict

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
from nahrung_formel import lesen, gaenge, schach

D = os.path.join(HIER, "..", "daten")
LAGER_R = 4
# Art -> (Ware, Arbeiter-Einheitstypen, die zum Lager liefern)
LIEFERER = {"holz": ("holz", {3}), "stein": ("stein", {9}), "eisen": ("eisen", {32}), "hopfen": ("hopfen", {12}),
            "pech": ("pech", {10})}


def gerade(punkte):
    """(fest, je_feld) aus [(d, umlauf)] - kleinste Quadrate; bei nur einem Abstand je_feld None."""
    ds = {d for d, _ in punkte}
    if len(ds) < 2:
        return (S.median([u for _, u in punkte]) if punkte else None), None
    md, mu = S.mean([d for d, _ in punkte]), S.mean([u for _, u in punkte])
    b = sum((d - md) * (u - mu) for d, u in punkte) / sum((d - md) ** 2 for d, _ in punkte)
    return mu - b * md, b


def main():
    pfad = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob(os.path.join(D, "arbeitsgang_rohstoff_2*[0-9].json")))[-1]
    d = json.load(open(pfad, encoding="utf-8"))
    ziele, orte = lesen(d["ew"])
    alle = gaenge(ziele, orte)
    teile = [tuple(x) for k, x in d["gebaeude"].items() if k.startswith("lager_anbau") and x] + [tuple(d["lager"])]
    am_lager = lambda p: min(schach(p, q) for q in teile) <= LAGER_R + 2
    # Typ je Arbeiter aus den Ladungs-Zeilen (t, nr, typ, zustand, ladung, ort)
    typ_von = {}
    for t, nr, typ, *_ in d["ladungen"]:
        typ_von[int(nr)] = typ
    betriebe = {}
    for k, v in d["gebaeude"].items():
        if v and isinstance(v, list) and len(v) == 2 and isinstance(v[0], list):
            art = k.rstrip("0123456789")
            betriebe[k] = dict(art=art, ort=tuple(v[0]), abstand=v[1])
    # Arbeiter -> Betrieb: wo stand er am haeufigsten (ausser am Lager)?
    zu = {}
    for nr, sp in orte.items():
        lieferer = [a for a, (_, typen) in LIEFERER.items() if typ_von.get(nr) in typen]
        if not lieferer:
            continue
        kand = [k for k, b in betriebe.items() if b["art"] in lieferer]
        if not kand:
            continue
        zaehl = defaultdict(int)
        for t, x, y in sp:
            if am_lager((x, y)):
                continue
            k = min(kand, key=lambda k: schach((x, y), betriebe[k]["ort"]))
            if schach((x, y), betriebe[k]["ort"]) <= 12:
                zaehl[k] += 1
        if zaehl:
            zu[nr] = max(zaehl, key=zaehl.get)
    abl = defaultdict(list)                       # betrieb -> [(abgang, ankunft, nr)]
    for nr, gs in alle.items():
        if nr not in zu:
            continue
        for (t0, start, ziel, ank, sch, los, danach) in gs:
            if ank and am_lager(ziel) and not am_lager(start):
                abl[zu[nr]].append((t0, ank, nr))
    best = d["bestand"]
    verkauf = d.get("verkauf", [])
    erg = {}
    print("Datei:", os.path.basename(pfad), "| Lagerteile", teile)
    for art, (ware, _) in LIEFERER.items():
        ks = [k for k, b in betriebe.items() if b["art"] == art]
        if not ks:
            continue
        punkte, zeilen, n_abl = [], [], 0
        for k in sorted(ks):
            a = sorted(abl.get(k, []))
            n_abl += len(a)
            je = defaultdict(list)
            for t0, _, nr in a:
                je[nr].append(t0)
            um = [y - x for ts in je.values() for x, y in zip(ts, ts[1:])]
            u = S.median(um) if um else None
            if u:
                punkte += [(betriebe[k]["abstand"], x) for x in um]
            zeilen.append((k, betriebe[k]["abstand"], len(a), u, a[0][0] if a else None))
        zugang = sum(max(0, b[ware] - a[ware]) for a, b in zip(best, best[1:]))
        verk = sum(max(0, (v["vorher"] or 0) - (v["nachher"] or 0)) for v in verkauf if v["ware"] == ware)
        menge = zugang + verk
        erste = min([z[4] for z in zeilen if z[4] is not None] or [None]) if any(z[4] for z in zeilen) else None
        ladung = menge / float(n_abl) if n_abl else None
        fest, je_feld = gerade(punkte)
        dauer = (best[-1]["t"] - erste) if erste is not None else None
        ist = 1000.0 * menge / dauer if dauer else None
        formel = None
        if ladung and fest is not None:
            formel = sum(1000.0 * ladung / (fest + (je_feld or 0) * ab) for _, ab, n, u, _ in zeilen if n)
        abw = round(100 * (formel - ist) / ist) if formel and ist else None
        e = dict(betriebe=[dict(name=k, abstand=ab, ablieferungen=n, umlauf_median=u) for k, ab, n, u, _ in zeilen],
                 menge=menge, zugang=zugang, verkauft=verk, ablieferungen=n_abl, ladung=round(ladung, 2) if ladung else None,
                 umlauf_fest=round(fest) if fest else None, umlauf_je_feld=round(je_feld, 1) if je_feld else None,
                 rate_gemessen=round(ist, 2) if ist else None, rate_formel=round(formel, 2) if formel else None,
                 abweichung_prozent=abw, gegenprobe=("BESTANDEN" if abw is not None and abs(abw) <= 20 else
                                                     "WIDERLEGT" if abw is not None else "NICHT PRUEFBAR"))
        erg[art] = e
        print("%-7s %s | Ladung %s, Umlauf %s + %s*d | gemessen %s / Formel %s je 1.000 (%s %%) -> %s" % (
            art, ["%s d=%s n=%d u=%s" % (k, ab, n, u) for k, ab, n, u, _ in zeilen], e["ladung"], e["umlauf_fest"],
            e["umlauf_je_feld"], e["rate_gemessen"], e["rate_formel"], abw, e["gegenprobe"]))
    json.dump(erg, open(pfad.replace(".json", "_formel.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
