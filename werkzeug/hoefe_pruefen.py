# -*- coding: utf-8 -*-
"""Gegenprobe Hofbau ohne Spiel (SAI 11.10., Nomade-Lauf 1011f: Holzmangel verwarf 46 von 55 Hofplaetzen -> Abbruch
"Hofplatzvorrat erschoepft"). Soll je Fall vorher festgelegt. Aufruf: python hoefe_pruefen.py"""
import erstes_spiel as E

# Baupreise je Balance (liga_ai.json / ascension_ai.json: Dairy farm cost [Holz, Stein, Eisen, Pech, Gold])
LIGA = {33: {"holz": 7, "stein": 0, "gold": 15}}
ASCENSION = {33: {"holz": 12, "stein": 0, "gold": 0}}


class Buch:
    offen = []

    def offen_bei(self, typ, p, r):
        return False


def fall(name, antworten, soll_offen, soll_verworfen, soll_erschoepft=False, orte=6, hoefe=5, preise=LIGA, gold=500, holz=100, runden=1):
    """antworten: je Bauversuch der Grund aus baue_schnell ("gebaut", "rohstoff", "platz", "schutz")."""
    versuche = list(antworten)
    E.BUCH = Buch()
    E._KOSTEN_SPIEL.clear()
    E._KOSTEN_SPIEL.update(preise)
    E.steht_bei = lambda G, typ, p, r: False

    def bauen(typ, x, y, r, **k):
        grund = versuche.pop(0) if versuche else "platz"
        return ((x, y), "gebaut") if grund == "gebaut" else (None, grund)
    E.baue_schnell = bauen
    p = E.Produktion.__new__(E.Produktion)
    p.hoefe, p.hof_orte, p.hof_verworfen = hoefe, [(10 * i, 10) for i in range(orte)], set()
    aus = []
    for _ in range(runden):
        offen = p.hoefe_bauen({}, [], gold, holz, 20, aus)
    erschoepft = E.hofvorrat_erschoepft(p.hoefe, 0, offen, p.hof_orte, p.hof_verworfen)
    ok = offen == soll_offen and len(p.hof_verworfen) == soll_verworfen and erschoepft == soll_erschoepft
    print("%s %-62s offen %d, verworfen %d, erschoepft %s" % ("OK  " if ok else "ROT ", name, offen, len(p.hof_verworfen), erschoepft))
    return ok


erg = [
    fall("Holz fehlt beim ersten Platz: nichts verworfen, Runde endet", ["rohstoff", "gebaut"], 0, 0),
    fall("2 gebaut, dann Holz weg: 2 offen, nichts verworfen", ["gebaut", "gebaut", "rohstoff", "gebaut"], 2, 0),
    fall("echte Platzablehnung verwirft, naechster Platz wird gebaut", ["platz", "gebaut", "rohstoff"], 1, 1),
    # 19.10. (1018x): eine Laufspur ("schutz") verwirft den Platz nicht mehr - er bleibt im Vorrat (hoefe_bauen)
    fall("Laufspur (schutz) verwirft nicht, naechster Platz wird gebaut", ["schutz", "gebaut", "rohstoff"], 1, 0),
    fall("alle 6 Plaetze echt abgelehnt (2 Runden): Vorrat erschoepft", ["platz"] * 6, 0, 6, soll_erschoepft=True, runden=2),
    fall("10 Plaetze belegt: je Runde hoechstens 4 Bauversuche", ["platz"] * 10, 0, 4, orte=12),
    fall("Lauf 1011f nachgestellt: 5 Plaetze belegt, 2 gebaut, dann Holzmangel", ["platz"] * 5 + ["gebaut"] * 2 + ["rohstoff"] * 48,
         2, 5, orte=55, runden=2),
    fall("Ascension-Preise (12 Holz, 0 Gold): ohne Gold, 30 Holz -> 2 Hoefe", ["gebaut"] * 5, 2, 0, preise=ASCENSION, gold=0, holz=30),
    fall("Liga-Preise: ohne Gold kein Hof", ["gebaut"] * 5, 0, 0, gold=0, holz=30),
]


class Ausbau:
    sperr = []


def radien(name, antworten, mindestens, soll_anzahl, soll_radien):
    """B-269: Platzsuche in Stufen - antworten {radius: Anzahl Plaetze}."""
    gefragt = []

    def live(kern, r=45):
        gefragt.append(r)
        return [(12 * i, r) for i in range(antworten.get(r, 0))]
    E.V14, E.hofplaetze_live = False, live
    aus = E.produktions_hofplaetze(None, (100, 100), mindestens=mindestens)
    ok = len(aus) == soll_anzahl and gefragt == soll_radien
    print("%s %-62s %d Plaetze, Radien %s" % ("OK  " if ok else "ROT ", name, len(aus), gefragt))
    return ok


def auffrischen(name, soll, plaetze, schritte, soll_hoefe, soll_fragen):
    """B-269: Partie 180423 nachgestellt - Start mit 0 Plaetzen, Soll bleibt; schritte = Ticks der Aufrufe."""
    fragen = []

    def hofplaetze(anzahl=None, kern=None, mindestens=1):
        fragen.append(mindestens)
        return [(12 * i, 5) for i in range(plaetze.pop(0) if plaetze else 0)]
    E.V14, E.produktions_hofplaetze = False, hofplaetze
    E.steht_bei = lambda G, typ, p, r: False
    p = E.Produktion.__new__(E.Produktion)
    p.hoefe, p.hoefe_soll, p.hof_orte, p.hof_verworfen, p.hof_kern = 0, soll, [], set(), (0, 0)
    aus = []
    for t in schritte:
        p.hofplaetze_auffrischen(t, {}, [], 0, Ausbau(), aus)
    ok = p.hoefe == soll_hoefe and len(fragen) == soll_fragen
    print("%s %-62s Hoefe %d, %d Anfragen" % ("OK  " if ok else "ROT ", name, p.hoefe, len(fragen)))
    return ok


ALT_PLAETZE = E.produktions_hofplaetze
erg += [
    radien("45 reicht: nur Radius 45", {45: 3, 80: 9}, 3, 3, [45]),
    radien("Partie 180423: 45 leer, 80 hat Gruenland", {45: 0, 80: 4}, 3, 4, [45, 80]),
    radien("nirgends Platz: alle Stufen, 0 Plaetze", {}, 3, 0, [45, 80, 120]),
]
E.produktions_hofplaetze = ALT_PLAETZE
erg += [
    auffrischen("Start 0 Plaetze, nach 1.000 Ticks 5 da: Soll 3 kommt", 3, [5], [5000], 3, 1),
    auffrischen("Spiel kennt erst keine, dann 2: Soll 3 -> 2 Hoefe", 3, [0, 2], [5000, 5500, 6100], 2, 2),
    auffrischen("Soll erreicht: keine Anfrage mehr", 0, [5], [5000, 7000], 0, 0),
]

print("%d von %d gruen" % (sum(erg), len(erg)))
raise SystemExit(0 if all(erg) else 1)
