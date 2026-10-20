# -*- coding: utf-8 -*-
"""Eingaenge je Gebaeudeart und Bau-Richtung (Daniel 06.10. 20:32: "du kannst Eingaenge blockieren, wodurch andere
Eingaenge genommen werden"). Messpartie, Baukosten 0 (Rueckweg im finally).

1. Je Art und Richtung 0/2/4/6 (placeBuilding: Drehung = Richtung / 2): bauen, Eingang (Gebaeude +0x112/+0x114, Modul-
   befehl "gebaeude") und Grundriss lesen, abreissen.
2. Blockieren: Schmiede (Richtung 0) bauen, Eingang lesen, eine Huette so setzen, dass sie das Eingangsfeld bedeckt,
   Eingang erneut lesen. Aendert sich der gespeicherte Eingang nicht, sagt das noch nichts ueber die Arbeiter - das zeigt
   erst ein Lauftest (offen).
Ergebnis: data/research/eingang_<zeit>.json
"""

from selfaware import workspace as _workspace
import json
import os
import re
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.game.ucp.befehl as kanal
import selfaware.runtime.live.erstes_spiel as E
import selfaware.services.wegkarte as W
from selfaware.game.ucp.laden import befehl
from selfaware.tools.experiments.streitkolben_messen import setze, warte_ticks, GOLD
from selfaware.tools.experiments.wege_abstand import kosten_nullen, kosten_zurueck, freie_flaeche, ART

D = os.path.join(_workspace.DATA)
SP = 1


def gebaeude_liste(typ):
    z = " ".join(befehl({"gebaeude": {"spieler": SP, "typ": typ}}, 1.0, bis="GEBAEUDE:"))
    return {int(n): {"ort": (int(x), int(y)), "eingang": (int(ex), int(ey))} for n, x, y, ex, ey in
            re.findall(r"GEBAEUDE (\d+): Typ \d+, Spieler \d+, Ort \((-?\d+),(-?\d+)\), Eingang \((-?\d+),(-?\d+)\)", z)}


def bauen(name, x, y, richtung):
    typ, mapper, b = ART[name]
    vorher = gebaeude_liste(typ)
    befehl({"baue": {"mapper": mapper, "x": x, "y": y, "groesse": b, "richtung": richtung}}, 0.8, bis="BAUE")
    warte_ticks(4)
    neu = {n: g for n, g in gebaeude_liste(typ).items() if n not in vorher}
    return neu


def main():
    E.LEERE_KI = True
    E.gefecht_starten(100)
    setze(GOLD, 20000)
    alt = kosten_nullen()
    erg = {"richtung": [], "blockieren": {}}
    try:
        teile = [g for g in E.runde_lesen()[2].values() if g["besitzer"] == SP and g["typ"] == 10]
        mitte = (teile[0]["x"], teile[0]["y"])
        k = W.holen(max(mitte[0] - 70, 0), max(mitte[1] - 70, 0), min(mitte[0] + 70, 399), min(mitte[1] + 70, 399))
        u = freie_flaeche(k, 24, mitte)
        x, y = u[0] + 8, u[1] + 8
        for name in ("Schmiede", "Gerberei", "Waffenlager", "Huette", "Markt"):
            for r in (0, 2, 4, 6):
                neu = bauen(name, x, y, r)
                for n, g in neu.items():
                    rel = (g["eingang"][0] - g["ort"][0], g["eingang"][1] - g["ort"][1])
                    erg["richtung"].append({"art": name, "richtung": r, "ort": g["ort"], "eingang": g["eingang"], "relativ": rel})
                    print("EINGANG %-12s Richtung %d: Ort %s Eingang %s -> relativ %s" % (name, r, g["ort"], g["eingang"], rel),
                          flush=True)
                    befehl({"abreissen": {"nr": n}}, 0.6, bis="ABREISSEN")
                if not neu:
                    print("EINGANG %-12s Richtung %d: nicht gebaut" % (name, r), flush=True)
                    erg["richtung"].append({"art": name, "richtung": r, "gebaut": False})
                warte_ticks(3)
        # Blockieren
        neu = bauen("Schmiede", x, y, 0)
        if neu:
            n, g = next(iter(neu.items()))
            ex, ey = g["eingang"]
            erg["blockieren"]["vorher"] = g
            hut = bauen("Huette", ex - 1, ey, 0)          # 4x4 ab (ex-1, ey): bedeckt das Eingangsfeld
            erg["blockieren"]["huette"] = {str(k2): v for k2, v in hut.items()}
            nachher = gebaeude_liste(ART["Schmiede"][0]).get(n)
            erg["blockieren"]["nachher"] = nachher
            print("BLOCKIEREN Schmiede %d: Eingang vorher %s, Huette gebaut %s, Eingang nachher %s" % (
                n, (ex, ey), bool(hut), nachher and nachher["eingang"]), flush=True)
            kk = W.holen(x - 4, y - 4, x + 12, y + 14)
            W.zeichnen(kk, os.path.join(D, "wege_abstand", "eingang_blockiert.png"), W.gebaeude_typen_aus(kk, {}), zelle=24,
                       titel="Schmiede, Eingang %s mit Huette zugebaut" % ((ex, ey),))
    finally:
        kosten_zurueck(alt)
        befehl({"pause": True}, 0.5)
        pfad = os.path.join(D, "eingang_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
        json.dump(erg, open(pfad, "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
        print("Daten:", pfad, flush=True)


if __name__ == "__main__":
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
