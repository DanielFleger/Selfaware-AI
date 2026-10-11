# -*- coding: utf-8 -*-
"""Gegenprobe Hofbau ohne Spiel (SAI 11.10., Nomade-Lauf 1011f: Holzmangel verwarf 46 von 55 Hofplaetzen -> Abbruch
"Hofplatzvorrat erschoepft"). Soll je Fall vorher festgelegt. Aufruf: python hoefe_pruefen.py"""
import erstes_spiel as E


class Buch:
    offen = []

    def offen_bei(self, typ, p, r):
        return False


def fall(name, antworten, soll_offen, soll_verworfen, soll_erschoepft=False, orte=6, hoefe=5):
    """antworten: je Bauversuch der Grund aus baue_schnell ("gebaut", "rohstoff", "platz", "schutz")."""
    versuche = list(antworten)
    E.BUCH = Buch()
    E.steht_bei = lambda G, typ, p, r: False

    def bauen(typ, x, y, r, **k):
        grund = versuche.pop(0) if versuche else "platz"
        return ((x, y), "gebaut") if grund == "gebaut" else (None, grund)
    E.baue_schnell = bauen
    p = E.Produktion.__new__(E.Produktion)
    p.hoefe, p.hof_orte, p.hof_verworfen = hoefe, [(10 * i, 10) for i in range(orte)], set()
    aus = []
    offen = p.hoefe_bauen({}, [], 500, 100, 20, aus)
    erschoepft = E.hofvorrat_erschoepft(p.hoefe, 0, offen, p.hof_orte, p.hof_verworfen)
    ok = offen == soll_offen and len(p.hof_verworfen) == soll_verworfen and erschoepft == soll_erschoepft
    print("%s %-62s offen %d, verworfen %d, erschoepft %s" % ("OK  " if ok else "ROT ", name, offen, len(p.hof_verworfen), erschoepft))
    return ok


erg = [
    fall("Holz fehlt beim ersten Platz: nichts verworfen, Runde endet", ["rohstoff", "gebaut"], 0, 0),
    fall("2 gebaut, dann Holz weg: 2 offen, nichts verworfen", ["gebaut", "gebaut", "rohstoff", "gebaut"], 2, 0),
    fall("echte Platzablehnung verwirft, naechster Platz wird gebaut", ["platz", "gebaut", "rohstoff"], 1, 1),
    fall("Laufspur (schutz) verwirft wie bisher", ["schutz", "gebaut", "rohstoff"], 1, 1),
    fall("alle 6 Plaetze echt abgelehnt: Vorrat erschoepft", ["platz"] * 6, 0, 6, soll_erschoepft=True),
    fall("Lauf 1011f nachgestellt: 5 Plaetze belegt, 2 gebaut, dann Holzmangel", ["platz"] * 5 + ["gebaut"] * 2 + ["rohstoff"] * 48,
         2, 5, orte=55),
]
print("%d von %d gruen" % (sum(erg), len(erg)))
raise SystemExit(0 if all(erg) else 1)
