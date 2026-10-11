# -*- coding: utf-8 -*-
"""Trockenprobe fuer lord_sturm.py ohne Spiel (SAI 11.10.: zweimal brach ein Lauf am Anfang ab, weil die Starttruppen
noch nicht da waren bzw. die Bogenschuetzen fuer den Abstieg ausgeklammert waren). Die Rundenschleife laeuft gegen eine
gespielte Folge von Lagebildern; Spielbefehle werden nur mitgeschrieben. Soll je Fall vorher festgelegt.
Aufruf: python sturm_trocken.py"""
import sys

import befehl as kanal
import erstes_spiel as E
import lageprotokoll
import lord_sturm

UNSER, SEIN = 3, 137


def einheit(besitzer, typ, x, y, leben=100, nahziel=-1):
    return {"besitzer": besitzer, "typ": typ, "x": x, "y": y, "leben": leben, "nahziel": nahziel}


def lage(t, gegner_leben, bogen=0, speer=0, lord_xy=(141, 269), lord_leben=150000, lord_schlaegt=False, gegner_nah=-1):
    L = {UNSER: einheit(1, 55, lord_xy[0], lord_xy[1], lord_leben, SEIN if lord_schlaegt else -1),
         SEIN: einheit(2, 55, 218, 261, gegner_leben, gegner_nah)}
    for i in range(bogen):
        L[200 + i] = einheit(1, 22, 141, 269)
    for i in range(speer):
        L[300 + i] = einheit(1, 24, 200, 262)
    return {"t": t}, L, {}


class Protokoll:
    def __init__(self, pfad):
        pass

    def schreibe(self, st):
        pass


def fall(name, folge, soll_rc, pruefe=None):
    befehle, texte, it = [], [], iter(folge)
    E.gefecht_starten = lambda tempo: None
    E.runde_lesen = lambda: next(it)
    E.befehl = lambda b, *a, **k: befehle.append(b) or ["OK"]
    E.schreib = lambda s: texte.append(s)
    E.BERGFRIED, E.SP = (141, 269), 1
    kanal.belege = kanal.freigeben = lambda: None
    lageprotokoll.Lageprotokoll = Protokoll
    sys.argv = ["lord_sturm.py", "mit_lord=ja", "lord_rolle=schild", "rueckzug=rechnung", "neu=1"]
    try:
        rc = lord_sturm.main()
    except StopIteration:
        rc = "Folge zu Ende"
    ok = rc == soll_rc and (pruefe is None or pruefe(befehle, texte))
    print("%s %-62s rc %s (soll %s) | letzte Meldung: %s" % ("OK  " if ok else "ROT ", name, rc, soll_rc, texte[-1][:70] if texte else "-"))
    return ok


laeufe = lambda befehle, x, y: any(b.get("angriff", {}).get("lauf") == [x, y] for b in befehle)
erg = [
    fall("Truppen erscheinen spaet, Bogen zuerst: kein Abbruch, Sieg",
         [lage(110, 30000), lage(202, 30000, bogen=5), lage(300, 30000, bogen=5, speer=7)]
         + [lage(400 + 100 * i, 30000 - 4000 * i, bogen=5, speer=7) for i in range(8)] + [lage(1300, 0, bogen=5, speer=7)], 0,
         lambda b, t: laeufe(b, 149, 269)),
    fall("alle Truppen tot: GESCHEITERT erst dann",
         [lage(110, 30000), lage(300, 30000, bogen=5, speer=7), lage(500, 25000, speer=3), lage(600, 25000)], 2),
    fall("Lords 3 Felder auseinander: unser Lord laeuft nach Hause",
         [lage(300, 30000, speer=7), lage(400, 28000, speer=7, lord_xy=(215, 261))], "Folge zu Ende",
         lambda b, t: laeufe(b, 141, 269)),
    fall("unser Lord schlaegt kurz vor dem Tod: Sieg UNGUELTIG",
         [lage(300, 30000, speer=7), lage(400, 2000, speer=7, lord_xy=(230, 270), lord_schlaegt=True), lage(420, 0, speer=7)], 4),
]
print("%d von %d gruen" % (sum(erg), len(erg)))
raise SystemExit(0 if all(erg) else 1)
