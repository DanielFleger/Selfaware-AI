# -*- coding: utf-8 -*-
"""Arbeitsgang messen (Daniel 06.10. 20:29: Aufbau fuer 5/15/30 Schmiede und Gerber - Laufweg zu den Rohstoffen,
Arbeitszeit, Weg zur Waffenkammer). Ohne gemessene Laufgeschwindigkeit und Arbeitszeit waere jeder Aufbau geraten.

Messpartie, KEIN Benchmark: Gold gesetzt, Baukosten der Testgebaeude auf 0 (Rueckweg im finally), Eisen am Markt gekauft.
Aufbau: Lager (angebaut) + Markt + Waffenlager am Lager; Schmiede NAH (~Platzsuche r=10) und FERN (~30 Felder weg);
Milchviehhof (Gruenland, Platzsuche) mit Gerberei daneben.
Mitgeschrieben im Spiel selbst (Modulbefehl einheitwacht, alle 2 Ticks): Ort jedes Schmieds (Typ 19), Gerbers (21),
Milchbauern (14) und jeder Zielwechsel; dazu alle 100 Ticks Keulen/Leder/Eisen im Bestand.
Auswertung: Ticks je Feld gerade/schraeg, Stehzeiten je Ort (Lager, Werkstatt, Waffenlager, Hof), gelaufene Felder
gegen den kuerzesten Weg der Weg-Ebene (wegkarte.weg) = Lauftest fuer das Wissensregister.

VORHER festgelegt (Widerlegung): Die Weg-Ebene gilt als bestaetigt, wenn die gelaufenen Wege der Arbeiter nie einen
Schritt nehmen, den die Weg-Ebene verbietet (0 Verstoesse), und hoechstens 20 % laenger sind als der kuerzeste Weg.
Ein einziger verbotener Schritt widerlegt meine Lesart der Bits.
Aufruf: uv run python -m selfaware.tools.experiments.arbeitsgang_messen [ticks=10000] [tempo=300]
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
from selfaware.game.ucp.laden import befehl, peek, TICK
from selfaware.tools.experiments.streitkolben_messen import setze, bestand, warte_ticks, GOLD, EISEN, KEULE
from selfaware.tools.experiments.wege_abstand import kosten_nullen, kosten_zurueck

D = os.path.join(_workspace.DATA)
SP = 1
LAGER, MARKT, WAFFENLAGER, SCHMIEDE, GERBER, MILCH = 10, 26, 11, 13, 16, 33
ARBEITER = {19: "Schmied", 21: "Gerber", 14: "Milchbauer"}


def eigene(typ):
    return {n: g for n, g in E.runde_lesen()[2].items() if g["besitzer"] == SP and g["typ"] == typ}


def baue_und_warte(typ, x, y, r):
    vorher = set(eigene(typ))
    o = E.baue_schnell(typ, x, y, r)
    for _ in range(40):
        warte_ticks(3)
        neu = set(eigene(typ)) - vorher
        if neu:
            return o, min(neu)
    return o, None


def log_ab(marke):
    """Zeilen aus ucp3.log nach der letzten Zeile, die marke enthaelt."""
    zeilen = open(kanal.LOG, encoding="utf-8", errors="replace").read().splitlines()
    for i in range(len(zeilen) - 1, -1, -1):
        if marke in zeilen[i]:
            return zeilen[i:]
    return []


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    dauer, tempo = int(arg.get("ticks", 10000)), int(arg.get("tempo", 300))
    E.LEERE_KI = True
    E.gefecht_starten(tempo)
    setze(GOLD, 20000)
    alt = kosten_nullen()
    erg = {"kosten_alt": {"0x%08X" % a: v for a, v in alt.items()}, "gebaeude": {}, "bestand": [], "arbeiter": {}}
    try:
        teile = [g for g in E.runde_lesen()[2].values() if g["besitzer"] == SP and g["typ"] == LAGER]
        lx, ly = teile[0]["x"], teile[0]["y"]
        plan = [("lager", LAGER, lx, ly, 8), ("markt", MARKT, lx, ly, 20), ("waffenlager", WAFFENLAGER, lx, ly, 10),
                ("schmiede_nah", SCHMIEDE, lx, ly, 10), ("schmiede_fern", SCHMIEDE, lx + 30, ly, 12),
                ("milchviehhof", MILCH, lx, ly, 45)]
        for name, typ, x, y, r in plan:
            erg["gebaeude"][name] = baue_und_warte(typ, x, y, r)
            print("gebaut %-14s %s" % (name, erg["gebaeude"][name]), flush=True)
        m = erg["gebaeude"]["milchviehhof"][0]
        if m:
            erg["gebaeude"]["gerberei"] = baue_und_warte(GERBER, m[0], m[1], 14)
            print("gebaut gerberei       %s" % (erg["gebaeude"]["gerberei"],), flush=True)
        warte_ticks(20)
        for _ in range(4):                                   # 20 Eisen (Lager-Teil frei durch den Anbau)
            befehl({"spielbefehl": {"nr": 38, "werte": [0, EISEN]}}, 1.0, bis="SPIELBEFEHL")
        G = E.runde_lesen()[2]
        for n, g in G.items():
            if g["besitzer"] == SP and g["typ"] == SCHMIEDE:
                befehl({"spielbefehl": {"nr": 33, "werte": [n, KEULE, g.get("uid", 0)]}}, 1.0, bis="SPIELBEFEHL")
        erg["gebaeude_liste"] = {n: g for n, g in G.items() if g["besitzer"] == SP}
        # Arbeiter abwarten (Bauern laufen vom Feuer zur Werkstatt)
        nummern = {}
        for _ in range(60):
            L = E.runde_lesen()[1]
            nummern = {n: e["typ"] for n, e in L.items() if e["besitzer"] == SP and e["typ"] in ARBEITER}
            if sum(1 for t in nummern.values() if t == 19) >= 2 and (not m or len(nummern) >= 4):
                break
            warte_ticks(20)
        erg["arbeiter"] = {str(n): ARBEITER[t] for n, t in nummern.items()}
        print("Arbeiter:", erg["arbeiter"], flush=True)
        befehl({"einheitwacht": {"nr": sorted(nummern), "alle": 2}}, 1.0, bis="EINHEITWACHT")
        k = W.holen(max(lx - 45, 0), max(ly - 45, 0), min(lx + 45, 399), min(ly + 45, 399))
        erg["wegkarte_fenster"] = [k["x0"], k["y0"], k["x1"], k["y1"]]
        t0 = peek(TICK)[0]
        while peek(TICK)[0] - t0 < dauer:
            b = bestand()
            erg["bestand"].append({k2: b[k2] for k2 in ("t", "keule", "leder", "eisen")})
            warte_ticks(100)
        befehl({"einheitwacht": False}, 1.0, bis="EINHEITWACHT")
        erg["ew"] = [z.split("INFO|", 1)[-1] for z in log_ab("EINHEITWACHT: scharf") if " EW " in z or "EW Orte" in z
                     or "EW Tick" in z]
        print("EW-Zeilen:", len(erg["ew"]), flush=True)
    finally:
        kosten_zurueck(alt)
        befehl({"pause": True}, 0.5)
        pfad = os.path.join(D, "arbeitsgang_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
        json.dump(erg, open(pfad, "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
        # Wegkarte des Fensters mitsichern (Lauftest-Vergleich spaeter ohne Spiel)
        import shutil
        shutil.copy(os.path.join(kanal.ABZUG, "wegkarte.txt"), pfad.replace(".json", "_wegkarte.txt"))
        print("Daten:", pfad, flush=True)


if __name__ == "__main__":
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
