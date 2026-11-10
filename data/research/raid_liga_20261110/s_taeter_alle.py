# -*- coding: utf-8 -*-
"""B-182: s_taeter.py ueber alle Partien vom 10.11. - je Partie eine Zeile, dann die Summe der gueltigen Partien.

Paarung: Mitschrift aufstellung_<Stempel>_..._konsole.txt mit dem ersten Lageprotokoll lage_<Stempel2>_i2.jsonl.gz,
das 0 bis 90 Sekunden nach ihr beginnt. Nicht in der Summe: Partien aus ungueltige_partien.txt (Kern-Vorfall) und
Partien gegen den Bauern (KI-Nummer 5, Attrappe, Daniel 10.11. abends).
Aufruf: python s_taeter_alle.py [<Stempel-Anfang, z. B. 20261110>]
"""
import collections
import datetime
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s_taeter as T  # noqa: E402

import selfaware.baukasten.einheiten as EH  # noqa: E402

F = "data/research"
MUSTER = sys.argv[1] if len(sys.argv) > 1 else "20261110"
WIRKT = ("nah", "schuss", "neben", "schuss_frei")
ARTEN_BERICHT = (22, 24, 70, 71, 73, 74, 75)


def zeit(stempel):
    return datetime.datetime.strptime(stempel, "%Y%m%d_%H%M%S")


def paare():
    lagen = sorted(glob.glob(f"{F}/lage_{MUSTER}*_i2.jsonl.gz"))
    lz = [(zeit(re.search(r"lage_(\d{8}_\d{6})", p).group(1)), p) for p in lagen]
    for k in sorted(glob.glob(f"{F}/aufstellung_{MUSTER}*_i2_konsole.txt")):
        s = re.search(r"aufstellung_(\d{8}_\d{6})_", k).group(1)
        t0 = zeit(s)
        treffer = [p for t, p in lz if 0 <= (t - t0).total_seconds() <= 90]
        yield s, k, (treffer[0] if treffer else None)


def main():
    ungueltig = set(open(f"{F}/raid_liga_20261110/ungueltige_partien.txt", encoding="utf-8").read().split())
    summe_tote, summe_braende, summe_zeit = collections.Counter(), collections.Counter(), collections.Counter()
    summe_gold, summe_stueck, behauptet = collections.Counter(), collections.Counter(), collections.Counter()
    summe_bestellt, summe_bestellt_gold = collections.Counter(), collections.Counter()
    summe_gruppen, summe_unbelegt, summe_geb, summe_zerst = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    n_gueltig = 0
    print("Stempel         | Aufstellung (Gegner) | Ende | Tote je Taeter | Braende Sklave/Ausbreitung/unbelegt | behauptet Reiter/Brand | Notiz")
    for s, k, lage in paare():
        name = os.path.basename(k)
        kurz = re.sub(r"^aufstellung_\d{8}_\d{6}_|_i2_konsole\.txt$", "", name)
        if lage is None:
            print(f"{s} | {kurz} | ohne Lageprotokoll")
            continue
        r = T.auswerten(lage)
        je = collections.Counter()
        for (kl, art, _g, _o), v in r["tote"].items():
            je[art if kl in WIRKT else kl] += v
        b = T.behauptungen(k)
        kauf = T.kaeufe(k)
        notiz = "UNGUELTIG (Kern)" if name in ungueltig else ("Attrappe KI 5" if "gegnerki5" in name else "")
        print("%s | %-38s | %5d | %s | %d/%d/%d | %d/%d | %s" % (
            s, kurz, r["ende"] or 0,
            ", ".join("%s %.1f" % (T.ARTNAME.get(a, a), v) for a, v in je.most_common() if v >= 0.5),
            r["braende"][("sklave", 71)], r["braende"][("ausbreitung", "-")], r["braende"][("unbelegt", "-")],
            b["Reiterjagd 'erledigt'"], b["Brandtrupp 'angezuendet'"], notiz))
        if notiz:
            continue
        n_gueltig += 1
        for (kl, art, grp, typ), v in r["tote"].items():
            summe_gruppen[(art if kl in WIRKT else kl, grp)] += v
            if kl == "unbelegt":
                summe_unbelegt[typ] += v
        summe_geb.update(r["geb_schaden"])
        summe_zerst.update(r["zerstoert"])
        sk_ges = sum(v for (a, _z, _w), v in r["zeit"].items() if a == 71)
        sk_leer = sum(v for (a, z, w), v in r["zeit"].items() if a == 71 and z == "steht_ohne_auftrag" and w == "zuhause")
        if sk_ges:
            print("    Sklaven ohne Auftrag zuhause: %.0f %% von %d Sklaven-Takten" % (100 * sk_leer / sk_ges, sk_ges))
        summe_tote.update(je)
        summe_braende.update(r["braende"])
        summe_zeit.update(r["zeit"])
        behauptet.update(b)
        # 10.11. 23:45 (Daniel): Gold = wirklich erschienene Einheiten x Spielpreis (einheiten.py, gemessen), nicht die Summe der
        # Bestellungen aus den Kaufzeilen - die zaehlten auch abgelehnte und gescheiterte Werbungen mit
        for art, stueck in r["neu_je_art"].items():
            preis = EH.ARTEN[art].gold if art in EH.ARTEN else None
            summe_stueck[art] += stueck
            summe_gold[art] += stueck * preis if preis else 0
        for art, (stueck, _pkt, gold) in kauf.items():
            summe_bestellt[art] += stueck
            summe_bestellt_gold[art] += gold
    print("\nSUMME ueber %d gueltige Partien (ohne Kern-Vorfall und ohne KI 5)" % n_gueltig)
    print("Tote gegnerische Einheiten je Taeter: " + ", ".join("%s %.1f" % (T.ARTNAME.get(a, a), v) for a, v in summe_tote.most_common()))
    print("Opfer je Taeter und Gruppe: " + ", ".join("%s->%s %.0f" % (T.ARTNAME.get(k[0], k[0]), k[1], v)
                                                    for k, v in summe_gruppen.most_common() if v >= 1))
    print("Ohne eigenen Taeter (unbelegt) je Opfer-Typ: " + ", ".join("Typ %s %.0f" % kv for kv in summe_unbelegt.most_common(12)))
    print("Gebaeudeschaden (Lebenspunkte): " + ", ".join("%s %s %.0f" % (k[0], T.ARTNAME.get(k[1], k[1]), v) for k, v in summe_geb.most_common()))
    print("Gegnerische Gebaeude verschwunden, nach letzter Ursache: " + ", ".join("%s %d" % kv for kv in summe_zerst.most_common()))
    print("Braende: " + ", ".join("%s %d" % (k[0], v) for k, v in summe_braende.most_common()))
    print("Behauptet von den Modulen: " + ", ".join("%s %d" % kv for kv in behauptet.items()))
    print("\nGOLD je Soeldnerart: erschienen x Spielpreis (einheiten.py), dazu die Bestellungen laut Kaufzeilen zum Vergleich")
    for art in sorted(set(summe_gold) | set(summe_bestellt) | {a for a in summe_tote if isinstance(a, int)}):
        g = summe_gold.get(art, 0.0)
        print("  %-28s erschienen %5d, Gold %7.0f | bestellt %5d, Gold %7.0f | belegte Tote %7.1f" % (
            T.ARTNAME.get(art, art), summe_stueck.get(art, 0), g, summe_bestellt.get(art, 0), summe_bestellt_gold.get(art, 0.0),
            summe_tote.get(art, 0.0)))   # 10.11. 23:50 (Daniel): keine Kennzahl "Tote je 100 Gold" mehr
    print("\nEINSATZZEIT je Art (Anteil der Einheiten-Takte):")
    for art in ARTEN_BERICHT:
        ges = sum(v for (a, _z, _w), v in summe_zeit.items() if a == art)
        if not ges:
            continue
        zust = collections.Counter()
        orte = collections.Counter()
        for (a, z, w), v in summe_zeit.items():
            if a == art:
                zust[z] += v
                orte[w] += v
        print("  %-28s %9d Takte | %s | Ort: %s" % (
            T.ARTNAME.get(art, art), ges,
            ", ".join("%s %.0f %%" % (z, 100 * v / ges) for z, v in zust.most_common()),
            ", ".join("%s %.0f %%" % (w, 100 * v / ges) for w, v in orte.most_common())))


if __name__ == "__main__":
    main()
