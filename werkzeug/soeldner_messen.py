# -*- coding: utf-8 -*-
"""Soeldner unter der laufenden Balance messen (SAI 12.10., Daniel 11.10. 23:45: "warum nicht arabische Einheiten - Sklaven
oder Assassinen fuer Raids, arabische Bogenschuetzen fuer Angriff und Verteidigung"; 00:03 "ja mach weiter").

Pruefstand gegen eine Ratte mit leerer KI: Gold gesetzt, Huetten fuer Leute, Soeldnerposten. Dann je arabischem Typ
(70 Bogen, 71 Sklave, 72 Schleuderer, 73 Assassine, 74 Pferdebogen, 75 Schwertkaempfer, 76 Feuerwerfer) EINE Einheit
werben: Gold vorher/nachher (= Preis), Ticks bis sie im Lagebild steht (= Ausbildung), ihr Leben laut Spiel.
Ausgabe: daten/soeldner_<zeit>.json. Aufruf: SHC_INSTANZ=4 python soeldner_messen.py [tempo=300]"""
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import befehl as kanal
import erstes_spiel as E
from laden import befehl, peek, TICK
from streitkolben_messen import setze, warte_ticks, GOLD
from bauen import vorrat, werbe

D = os.path.join(HIER, "..", "daten")
SP = 1
TYPEN = {70: "Arabischer Bogenschuetze", 71: "Sklave", 72: "Schleuderer", 73: "Assassine", 74: "Pferdebogenschuetze",
         75: "Arabischer Schwertkaempfer", 76: "Feuerwerfer"}


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    E.LEERE_KI, E.GEGNER_ERWARTET = True, ""
    E.LIGA_GEFECHT = dict(E.LIGA_GEFECHT, ki=1)
    E.gefecht_starten(int(arg.get("tempo", 300)))
    setze(GOLD, 20000)
    erg = {"einheiten": {}}
    try:
        info = json.load(open(os.path.join(D, "start_M19.json"), encoding="utf-8"))
        K = tuple(info["bergfried_eingang"])
        for i in range(4):
            E.baue_schnell(1, K[0] - 7, K[1] - 2, 25)
        posten = E.baue_schnell(8, K[0], K[1], 25)
        warte_ticks(400)
        nr = next((n for n, g in E.runde_lesen()[2].items() if g["besitzer"] == SP and g["typ"] == 8), None)
        erg["posten"] = (posten, nr)
        print("Soeldnerposten", posten, "Nr", nr, "Gold", vorrat(SP)["gold"], flush=True)
        for typ, name in TYPEN.items():
            L0 = E.runde_lesen()[1]
            vorher = {n for n, e in L0.items() if e["besitzer"] == SP and e["typ"] == typ}
            g0, t0 = vorrat(SP)["gold"], peek(TICK)[0]
            werbe(typ, nr)
            warte_ticks(20)
            g1 = vorrat(SP)["gold"]
            neu, t_da = None, None
            while peek(TICK)[0] - t0 < 1500:
                L = E.runde_lesen()[1]
                neu = [n for n, e in L.items() if e["besitzer"] == SP and e["typ"] == typ and n not in vorher]
                if neu:
                    t_da = peek(TICK)[0] - t0
                    break
                warte_ticks(20)
            e = L[neu[0]] if neu else {}
            erg["einheiten"][typ] = dict(name=name, gold=g0 - g1, ticks_bis_da=t_da, leben=e.get("leben"))
            print("%-28s Gold %d, da nach %s Ticks, Leben %s" % (name, g0 - g1, t_da, e.get("leben")), flush=True)
    finally:
        pfad = os.path.join(D, "soeldner_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
        json.dump(erg, open(pfad, "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
        befehl({"pause": True}, 0.5)
        print("Daten:", pfad, flush=True)


if __name__ == "__main__":
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
