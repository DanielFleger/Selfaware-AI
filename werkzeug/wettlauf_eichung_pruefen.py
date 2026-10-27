# -*- coding: utf-8 -*-
"""B-273 Eichung des Lord-Wettlaufs an der Sandkasten-Messreihe (daten/lord_nahkampf.jsonl, 22.10.2026: N Einheiten einer
Art 1 Feld neben dem Lord gestapelt, Zeitverlauf Lord-Leben und Ueberlebende).

Soll (vorher festgelegt, 27.10. 22:15): gestapelt und ohne Ablenkung muss gefecht.lord_rennen mit den Spielwerten des Auges
den gemessenen Ausgang treffen - Lord-Rest innerhalb 15 % seines Startlebens, Ende (Lord tot oder alle eigenen tot) innerhalb
20 % der gemessenen Takte, Ueberlebende +-1. Gemessen 27.10.: Streitkolben x5 gerechnet Lord-Rest ~18.000 (gemessen 32.400),
Ende 600 (561); arab. Schwert x5 gerechnet Lord faellt nach 240-250 (279), 4 leben (4).
Aufruf: python wettlauf_eichung_pruefen.py"""
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import gefecht as G
import kaufrechnung as KR

LORD_TOL, ZEIT_TOL, REST_TOL = 0.15, 0.20, 1


def eichen():
    sch, leb, fern = G.tabelle()
    aus = []
    for z in open(os.path.join(HIER, "..", "daten", "lord_nahkampf.jsonl"), encoding="utf-8"):
        r = json.loads(z)
        p = r.get("proben") or []
        if len(p) < 2:
            continue
        typ, n = r["typ"], r["anzahl"]
        t0, l0, _ = p[0]
        t_e, l_e, a_e = p[-1]
        wir = [dict(typ=typ, leben=leb[typ], x=101, y=100) for _ in range(n)]
        sie = [dict(typ=55, leben=l0, x=100, y=100, steht=True)]
        G.lord_rennen(wir, sie, 0, bis=2000)
        rr = G.LETZTES_RENNEN
        tote = sum(1 for _t, art, s, _ty, _n in rr["verlauf"] if art == "tot" and s == "wir")
        ok = (abs(rr["lord_rest"] - l_e) <= LORD_TOL * l0 and abs(rr["takte"] - (t_e - t0)) <= ZEIT_TOL * (t_e - t0)
              and abs((n - tote) - a_e) <= REST_TOL)
        aus.append((ok, "Art %d x%d: gemessen Lord-Rest %d nach %d Takten, %d leben | gerechnet %d nach %d, %d leben" % (
            typ, n, l_e, t_e - t0, a_e, rr["lord_rest"], rr["takte"], n - tote)))
    return aus


if __name__ == "__main__":
    sw = KR.spielwerte_laden()
    if sw is None:
        print("UEBERSPRUNGEN: keine live-Datei daten/spielwerte_*.json")
        sys.exit(0)
    G.SPIELWERTE, G._TABELLE = sw, None
    erg = eichen()
    for ok, text in erg:
        print("%s %s" % ("OK  " if ok else "ROT ", text))
    print("%d von %d Messungen getroffen (Toleranz Lord %.0f %%, Zeit %.0f %%, Ueberlebende +-%d)" % (
        sum(ok for ok, _ in erg), len(erg), 100 * LORD_TOL, 100 * ZEIT_TOL, REST_TOL))
    sys.exit(0 if erg and all(ok for ok, _ in erg) else 1)
