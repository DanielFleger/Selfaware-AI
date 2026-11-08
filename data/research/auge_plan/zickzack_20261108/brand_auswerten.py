# -*- coding: utf-8 -*-
"""Szene brand_g (B-175): Kommen Sklaven im Zickzack besser durchs Feuer als gerade?

Vier Bahnen im Gefecht, je 4 Sklaven, 60 Felder bis zu 4 Holzfaellerhuetten, unterwegs 8 Bogenschuetzen, die von selbst schiessen.
Vor dem Lauf festgelegt (die Grenzen sind meine, ohne Vorgabe dahinter): widerlegt, wenn die Sklaven im Zickzack bis zur Ankunft nicht
seltener getroffen werden als die geraden, oder wenn in den Zickzack-Bahnen weniger Huetten brennen als in den geraden.
Treffer je Sklave: wie oft ihm bis zur Ankunft ein Pfeil Leben nimmt (ab PFEIL Leben; gemessen 7.000). Im Test hat er kuenstlich viel Leben, damit jeder bis ans Ziel kommt.
Wie viele Treffer ihn im Spiel toeten, folgt aus seinem echten Leben (Spalte voll im Plan des Laufs, auf Instanz 2 15.000: drei Treffer). Darum steht dazu, wer ohne Treffer ankommt und wer vor der Ankunft tot waere.
Ankunft: erster Takt, an dem er hoechstens 4 Felder vor einer Huette steht.
Grenzen: zwei Bahnen je Muster, ein Lauf, Pfeile sind wenige und an der Schussfolge gebunden (Wissensregister S78). Die Schuetzen waehlen ihre Ziele selbst.
Eingabe: neueste lauf_s_*_brand_g.auge unter laeufe/, Protokoll lauf_brand_g.log. Ausgabe: brand_g_ergebnis.txt.
"""
import collections
import glob
import json
import math
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "streuung_20261104"))
import flug_pruefen as fp  # noqa: E402
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte  # noqa: E402

ART = 1
AM_ZIEL = 4
PFEIL = 5000  # Leben: So viel nimmt nur ein Pfeil (7.000), Nahkampf und Feuer nehmen 20 bis 150 je Takt
EIN_PFEIL = 7000  # Leben je Pfeil, gemessen in dieser Aufnahme (haeufigster Wert, Ausgabe unten)


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def main():
    pfad = sorted(glob.glob(os.path.join(HIER, "..", "laeufe", "lauf_s_*_brand_g.auge")), key=os.path.getmtime)[-1]
    k = Feldkarte.laden(feldliste=FELDLISTE)
    lauf = fp.Lauf(pfad, k)
    b = [json.loads(z) for z in open(os.path.join(HIER, "lauf_brand_g.log"), encoding="utf-8", errors="replace") if z.startswith('{"schritt": "brand_probe"')][-1]
    takte = [t for t in sorted(lauf.u) if b["von"] <= t <= b["bis"]]
    plan = json.load(open(pfad + ".plan.json", encoding="utf-8"))
    voll = next(x["voll"] for x in plan["einheiten"] if x.get("rolle") == "sklave")
    schaden = collections.Counter()
    aus = ["Datei %s, Takte %d bis %d" % (os.path.basename(pfad), b["von"], b["bis"]), ""]
    aus.append("Bahn: Treffer je Sklave bis zur Ankunft (einzeln) | Summe | Pfeile der Schuetzen, davon Treffer | Ankunft in Takten nach dem Start (Median) | Felder je 1000 Takte | Schritte mit neuer Richtung | schraeg | Huetten angezuendet")
    summe = collections.defaultdict(collections.Counter)
    ankunft_je = collections.defaultdict(list)
    ersttreffer = collections.defaultdict(list)
    je_sklave = collections.defaultdict(list)
    for x in b["bahnen"]:
        huetten = [(h["x"], h["y"]) for h in x["huetten"]]
        treffer, an, erste = [], [], []
        schritte = paare = wechsel = schraeg = dauer = 0
        for i in x["sklaven"]:
            vor = richt = leben = None
            t_an = t_erst = None
            h = 0
            for t in takte:
                q = lauf.u[t]
                p = (int(q["x"][i]), int(q["y"][i]))
                l = int(q["leben"][i])
                if t_an is None:
                    if leben is not None and leben - l >= PFEIL:
                        # 14.000 sind zwei Pfeile im selben Takt: Ein Takt allein zaehlt sonst nur einen (Fund 09.11. in der ersten Auswertung)
                        h += (leben - l + EIN_PFEIL // 2) // EIN_PFEIL
                        schaden[leben - l] += 1
                        if t_erst is None:
                            t_erst = t
                    if min(schach(p, o) for o in huetten) <= AM_ZIEL:
                        t_an = t
                    elif vor is not None and p != vor:
                        r = (p[0] - vor[0], p[1] - vor[1])
                        schritte += 1
                        schraeg += bool(r[0] and r[1])
                        if richt is not None:
                            paare += 1
                            wechsel += r != richt
                        richt = r
                leben, vor = l, p
            treffer.append(h)
            erste.append(None if t_erst is None else t_erst - b["von"])
            if t_an is not None:
                an.append(t_an - b["von"])
                dauer += t_an - b["von"]
            else:
                dauer += takte[-1] - b["von"]
        pf = tr = 0
        for _s, f in lauf.fluege.items():
            z = f[0][1]
            if z["art"] != ART or z["sch"] not in x["schuetzen"]:
                continue
            ende = next(((t, q) for t, q in f[1:] if q["da"] != 2 or q["boden"] != 0), None)
            if ende is None:
                continue
            pf += 1
            tr += ende[1]["da"] == 3 and ende[1]["boden"] == 9
        brennt = sum("angezuendet" in v.get("ereignis", "") for v in b["verlauf"] if v["bahn"] == x["name"])
        c = summe[x["muster"]]
        c["treffer"] += sum(treffer)
        c["sklaven"] += len(treffer)
        c["pfeile"] += pf
        c["pfeile_treffer"] += tr
        c["brennt"] += brennt
        c["schritte"] += schritte
        c["paare"] += paare
        c["wechsel"] += wechsel
        c["schraeg"] += schraeg
        c["dauer"] += dauer
        c["angekommen"] += len(an)
        ankunft_je[x["muster"]] += an
        an = sorted(an)
        c["ohne"] += sum(1 for v in erste if v is None)
        je_sklave[x["muster"]] += treffer
        ersttreffer[x["muster"]] += [v for v in erste if v is not None]
        aus.append("  %-11s %s (erster Treffer nach Takten %s) | %3d | %3d, %3d (%s) | %s | %.1f | %s | %s | %d" % (
            x["name"], treffer, erste, sum(treffer), pf, tr, "%.0f %%" % (100 * tr / pf) if pf else "-", an[len(an) // 2] if an else "-",
            1000 * schritte / dauer if dauer else 0, "%.0f %%" % (100 * wechsel / paare) if paare else "-", "%.0f %%" % (100 * schraeg / schritte) if schritte else "-", brennt))
    pfeil = schaden.most_common(1)[0][0]
    toedlich = math.ceil(voll / pfeil)
    aus += ["", "Echtes Leben eines Sklaven %d, ein Pfeil nimmt %d (haeufigster Wert %s): toedlich ist der %d. Treffer" % (voll, pfeil, schaden.most_common(3), toedlich)]
    aus += ["", "Zusammen je Muster:"]
    for m, c in summe.items():
        a = sorted(ankunft_je[m])
        e = sorted(ersttreffer[m])
        aus.append("  %-9s %d Sklaven, %d angekommen (Median Takt %s), %d ohne jeden Treffer, erster Treffer im Median nach Takt %s: %.2f Treffer je Sklave bis zur Ankunft; %d Pfeile, %d Treffer (%s); %d Huetten angezuendet; %.1f Felder je 1000 Takte; Schritte mit neuer Richtung %s" % (
            m, c["sklaven"], c["angekommen"], a[len(a) // 2] if a else "-", c["ohne"], e[len(e) // 2] if e else "-", c["treffer"] / c["sklaven"], c["pfeile"], c["pfeile_treffer"], "%.0f %%" % (100 * c["pfeile_treffer"] / c["pfeile"]) if c["pfeile"] else "-", c["brennt"], 1000 * c["schritte"] / c["dauer"] if c["dauer"] else 0, "%.0f %%" % (100 * c["wechsel"] / c["paare"]) if c["paare"] else "-"))
    aus += ["", "Waeren vor der Ankunft tot (echtes Leben):"]
    for m in summe:
        t = je_sklave[m]
        aus.append("  %-9s %d von %d (Treffer je Sklave %s)" % (m, sum(v >= toedlich for v in t), len(t), sorted(t)))
    aus += ["", "Bericht je Bahn:"] + ["  %s: %s" % (x["name"], x["bericht"]) for x in b["bahnen"]]
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "brand_g_ergebnis.txt"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
