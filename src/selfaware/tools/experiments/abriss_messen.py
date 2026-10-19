# -*- coding: utf-8 -*-
"""Abriss-Rueckgabe bei ungeraden Kosten (Daniel 06.10. 20:11: "schau mal bei geraden/ungeraden Ressourcen/Abriss").
Messpartie, KEIN Benchmark - Gold direkt gesetzt, Holz/Stein echt am Markt gekauft.

Code (research/native/dekomp_abriss_rueckgabe.c): je Ware Kosten * Prozent / 100 in ganzen Zahlen, der Abriss-Knopf schickt 50.
VORHER festgelegt (Liga-Kosten [Holz, Stein, Eisen, Pech, Gold], liga_ai.json):
  Gerberei     [15, 3, 0, 0, 75] -> Holz +7, Stein +1, Gold +37   (abgerundet)
  Gerberei 2   gleich wie die erste                                 (kein mitgefuehrter Rest)
  Milchviehhof [7, 0, 0, 0, 15]  -> Holz +3, Gold +7
  Kaserne      [0, 12, 0, 0, 0]  -> Stein +6                        (gerade, Gegenstueck)
  Huette       [5, 0, 0, 0, 0]   -> Holz +2
WIDERLEGT, wenn: irgendwo aufgerundet wird (8/2/38, 4/8, 3), oder die zweite Gerberei mehr bringt als die erste.
Ergebnis: data/research/abriss_messung_<zeit>.json + Zeilen im Log.
Aufruf: uv run python -m selfaware.tools.experiments.abriss_messen [tempo=300]
"""

from selfaware import workspace as _workspace
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.game.ucp.befehl as kanal
import selfaware.runtime.live.erstes_spiel as E
from selfaware.game.ucp.laden import befehl, peek, TICK
from selfaware.tools.experiments.streitkolben_messen import setze, bestand, differenz, warte_ticks, SP, GOLD, HOLZ, STEIN, LAGER, MARKT

D = os.path.join(_workspace.DATA)
GERBER, MILCH, KASERNE, HUETTE = 16, 33, 9, 1
ERWARTET = [("Gerberei", GERBER, {"holz": 7, "stein": 1, "gold": 37}),
            ("Gerberei 2", GERBER, {"holz": 7, "stein": 1, "gold": 37}),
            ("Milchviehhof", MILCH, {"holz": 3, "stein": 0, "gold": 7}),
            ("Kaserne", KASERNE, {"holz": 0, "stein": 6, "gold": 0}),
            ("Huette", HUETTE, {"holz": 2, "stein": 0, "gold": 0})]


def eigene(typ):
    return [n for n, g in E.runde_lesen()[2].items() if g["besitzer"] == SP and g["typ"] == typ]


def baue_und_warte(typ, lx, ly, r):
    vorher = len(eigene(typ))
    o = E.baue_schnell(typ, lx, ly, r)
    for _ in range(40):
        warte_ticks(3)
        if len(eigene(typ)) > vorher:
            return o
    return ("nicht gebaut", o)


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    tempo = int(arg.get("tempo", 300))
    plan = json.load(open(os.path.join(D, "eroeffnung_plan_M19.json"), encoding="utf-8"))
    lx, ly = plan["lager"]
    E.LEERE_KI = True
    E.gefecht_starten(tempo)
    teile0 = [g for g in E.runde_lesen()[2].values() if g["besitzer"] == SP and g["typ"] == LAGER]
    if teile0:
        lx, ly = teile0[0]["x"], teile0[0]["y"]
    erg = {"erwartet": ERWARTET, "gebaut": [], "abriss": []}
    setze(GOLD, 20000)
    # Lager erst anbauen (jedes Teil nur eine Warenart), dann Markt, dann Holz und Stein echt kaufen
    for typ, r in ((LAGER, 8), (MARKT, 20)):
        erg["gebaut"].append([typ, baue_und_warte(typ, lx, ly, r)])
    for art, lose in ((STEIN, 10), (HOLZ, 10)):
        for _ in range(lose):
            befehl({"spielbefehl": {"nr": 38, "werte": [0, art]}}, 1.0, bis="SPIELBEFEHL")
    warte_ticks(10)
    for name, typ, _ in ERWARTET:
        erg["gebaut"].append([name, baue_und_warte(typ, lx, ly, 45 if typ == MILCH else 15)])
    print("gebaut:", erg["gebaut"], flush=True)
    warte_ticks(100)
    # je Typ die Nummern einsammeln, DANN abreissen (das Array wird beim Abreissen umgeraeumt - rezepte.lua)
    nummern = {typ: eigene(typ) for typ in (GERBER, MILCH, KASERNE, HUETTE)}
    gezaehlt = {}
    for name, typ, soll in ERWARTET:
        i = gezaehlt.get(typ, 0)
        gezaehlt[typ] = i + 1
        if i >= len(nummern[typ]):
            erg["abriss"].append({"name": name, "fehlt": True})
            print("ABRISS %s: nicht gebaut" % name, flush=True)
            continue
        nr = nummern[typ][i]
        vor_anzahl = len(eigene(typ))
        a = bestand()
        befehl({"abreissen": {"nr": nr}}, 0.8, bis="ABREISSEN")
        warte_ticks(60)
        b = bestand()
        d = differenz(a, b)
        weg = len(eigene(typ)) < vor_anzahl
        passt = all(d.get(k) == v for k, v in soll.items())
        erg["abriss"].append({"name": name, "nr": nr, "diff": d, "soll": soll, "passt": passt, "gebaeude_weg": weg})
        print("ABRISS %-12s Nr %3d: Holz %+d Stein %+d Gold %+d | erwartet %s -> %s%s" % (
            name, nr, d.get("holz", 0), d.get("stein", 0), d.get("gold", 0), soll,
            "PASST" if passt else "ABWEICHUNG", "" if weg else " (Gebaeude NICHT weg!)"), flush=True)
    befehl({"pause": True}, 0.5)
    pfad = os.path.join(D, "abriss_messung_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
    json.dump(erg, open(pfad, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("Daten:", pfad)


if __name__ == "__main__":
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
