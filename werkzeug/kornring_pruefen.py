# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer kornring.py und den Ringabstand in nahrungswahl.speicherplatz (18.10.). Vorher festgelegt:
  1. Ring um (100, 50): 16 Kacheln, je Seite 4, alle direkt am 4x4-Speicher, keine der 4 Ecken
  2. leerer Ring, 8 Stein: genau 3 Seiten gesendet (je 3 Stein noetig, 2 verbraucht), die vierte wartet auf Stein;
     bleibt der Wartegrund gleich, kommt keine zweite Wartemeldung (Lauf 1018f: 4 Zeilen alle 100 Ticks)
  3. leerer Ring, 0 Stein: NICHTS gesendet (das Spiel wuerde eine Gratiskachel setzen)
  4. eine ganze Seite gesendet, stand danach nicht (jemand stand darauf): beim naechsten Blick (100 Ticks spaeter) wird
     diese Seite Kachel fuer Kachel gesendet, die anderen nicht
  5. alles steht: eine Meldung "steht", kein Befehl, Steinbedarf 0
  6. zweiter Aufruf nach 50 Ticks: keine Pruefung, kein Befehl
  7. Kornspeicherplatz beider 1v1-Plaetze auf Close Encounters: keine geplante Apfelplantage auf dem Ring
Gegenprobe: mit "alt" sendet der Baustein ohne Steinpruefung und die Platzwahl ohne Ringabstand -> Faelle 2, 3 und 7 rot.
Aufruf: python werkzeug/kornring_pruefen.py [alt]"""
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import kornring as KR
import nahrungswahl as N

if len(sys.argv) > 1 and sys.argv[1] == "alt":
    KR.bezahlbar = lambda stein, kacheln: True
    N.RING_RAND = 0


def neu(stehen=()):
    gesendet = []
    stehen = set(stehen)
    r = KR.Kornring((100, 50), lambda ks: {k: k in stehen for k in ks},
                    lambda x1, y1, x2, y2, n: gesendet.append((x1, y1, x2, y2, n)))
    return r, gesendet, stehen


def main():
    ok = []

    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))

    s = KR.seiten(100, 50)
    alle = [k for _, _, _, ks in s for k in ks]
    ecken = {(99, 49), (104, 49), (99, 54), (104, 54)}
    innen = {(x, y) for x in range(100, 104) for y in range(50, 54)}
    am_speicher = all(any(abs(k[0] - i[0]) + abs(k[1] - i[1]) == 1 for i in innen) for k in alle)
    pruefe(1, "16 Kacheln %s, je Seite %s, Ecken drin %s, alle am Speicher %s" % (
        len(set(alle)), [len(ks) for _, _, _, ks in s], bool(ecken & set(alle)), am_speicher),
           len(set(alle)) == 16 and all(len(ks) == 4 for _, _, _, ks in s) and not ecken & set(alle) and am_speicher)
    r, g, _ = neu()
    ev = r.schritt(1000, 8)
    ev2 = r.schritt(1100, 0)       # gleicher Wartegrund? nein - jetzt fehlen weniger Kacheln nicht (nichts stand), 0 Stein
    ev3 = r.schritt(1200, 0)       # derselbe Grund wie eben -> keine neue Meldung
    pruefe(2, "8 Stein: %d Seiten gesendet, wartet: %s; gleicher Grund erneut gemeldet: %s" % (
        len(g), [e for e in ev if "wartet" in e], [e for e in ev3 if "wartet" in e]),
           len(g) == 3 and all(x[4] == 4 for x in g) and sum("wartet" in e for e in ev) == 1
           and not any("wartet" in e for e in ev3))
    r, g, _ = neu()
    r.schritt(1000, 0)
    pruefe(3, "0 Stein: %d Befehle" % len(g), len(g) == 0)
    r, g, stehen = neu()
    r.schritt(1000, 20)
    erste = list(g)
    stehen |= {k for _, _, _, ks in KR.seiten(100, 50)[1:] for k in ks}      # alle Seiten ausser "oben" stehen jetzt
    del g[:]
    r.schritt(1100, 20)
    pruefe(4, "zuerst %d ganze Seiten; danach einzeln: %s" % (len(erste), g),
           len(erste) == 4 and len(g) == 4 and all(x[4] == 1 and x[1] == 49 and x[3] == 49 for x in g))
    r, g, _ = neu(alle)
    ev = r.schritt(1000, 20)
    pruefe(5, "alles steht: %s, Befehle %d, Steinbedarf %d" % (ev, len(g), r.stein_bedarf()),
           len(ev) == 1 and "steht" in ev[0] and not g and r.stein_bedarf() == 0)
    r, g, _ = neu()
    r.schritt(1000, 20)
    n1 = len(g)
    r.schritt(1050, 20)
    pruefe(6, "nach 50 Ticks: %d neue Befehle" % (len(g) - n1), len(g) == n1)
    erg = []
    for kurz in ("CloseEncounters_pl3-2_1v1", "CloseEncounters_pl2-3_1v1"):
        plan = json.load(open(os.path.join(HIER, "..", "daten", "eroeffnung_plan_%s.json" % kurz), encoding="utf-8"))
        w = N.waehle(kurz, plan, bev_ziel=90, ration="doppelt", horizont=80000)
        gx, gy = w["kornspeicher"]
        ring = {k for _, _, _, ks in KR.seiten(gx, gy) for k in ks}
        auf = sum(len({(x + i, y + j) for i in range(10) for j in range(10)} & ring) for x, y in (w["aepfel"] or []))
        erg.append((kurz.split("_")[1], (gx, gy), auf))
    pruefe(7, "Plantagen-Kacheln auf dem Ring je Platz: %s" % erg, all(a == 0 for _, _, a in erg))
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
