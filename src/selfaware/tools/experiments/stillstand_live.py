# -*- coding: utf-8 -*-
"""Live-Probe des Stillstand-Waechters (SAI 11.10. 22:50): der Fall von 17:20 nachgestellt - Startholz belegt alle 4
Lagerteile, eine Getreidefarm, KEIN Lageranbau. Der Waechter bekommt dieselben Bausteine wie im Lenker (erstes_spiel.py:
Speicher +0x184 lesen, baue_schnell(10, ...)). Pruefstand gegen eine Ratte mit leerer KI, Baukosten 0 (Rueckweg im
finally, Daten zuerst gesichert).
VORHER festgelegt (Widerlegung): kommt bis Tick 10.000 nach Start kein "Lagerteil angebaut", oder bleibt Weizen danach
2.000 Ticks bei 0, ist der Waechter durchgefallen. Rueckgabe 0 = bestanden.
Aufruf: SHC_INSTANZ=4 uv run python -m selfaware.tools.experiments.stillstand_live [tempo=300]"""

from selfaware import workspace as _workspace
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.game.ucp.befehl as kanal
import selfaware.runtime.live.erstes_spiel as E
import selfaware.runtime.live.stillstand as STW
from selfaware.game.ucp.laden import befehl, peek, TICK
from selfaware.tools.experiments.streitkolben_messen import setze, warte_ticks, GOLD
from selfaware.tools.experiments.wege_abstand import kosten_nullen, kosten_zurueck
from selfaware.tools.experiments.nahrung_messen import wegtest
from selfaware.macro.farmen_mischen import lies_karte
from selfaware.micro.tasks.waechter import schach
from selfaware.game.ucp.bauen import vorrat

D = os.path.join(_workspace.DATA)
SP = 1


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    E.LEERE_KI, E.GEGNER_ERWARTET = True, ""
    E.LIGA_GEFECHT = dict(E.LIGA_GEFECHT, ki=1)
    E.gefecht_starten(int(arg.get("tempo", 300)))
    setze(GOLD, 20000)
    kosten_vorher = kosten_nullen()
    erg = {"ereignisse": [], "weizen": [], "anbau_tick": None, "weizen_tick": None}
    t0 = peek(TICK)[0]
    try:
        info = json.load(open(os.path.join(D, "start_M19.json"), encoding="utf-8"))
        K, F = tuple(info["bergfried_eingang"]), tuple(info["feind_bergfried"]["2"]["eingang"])
        fr = [p for p in lies_karte(os.path.join(D, "start_M19_platz_apfel.txt")) if schach(p, K) < schach(p, F)]
        teile = [g for g in E.runde_lesen()[2].values() if g["besitzer"] == SP and g["typ"] == 10]
        lager = (teile[0]["x"], teile[0]["y"])
        fr.sort(key=lambda p: schach(p, lager))
        ks = E.baue_schnell(19, fr[0][0], fr[0][1], 12)
        warte_ticks(60)
        frei = [p for p in fr if schach(p, ks) >= 12][:40]
        erg["getreide"] = next((o for o in (E.baue_schnell(30, p[0], p[1], 4) for p in wegtest(frei)) if o), None)
        for i in range(3):
            E.baue_schnell(1, K[0] - 7, K[1] - 2, 25)
        befehl({"spielbefehl": {"nr": 35, "werte": [0]}}, 1.0, bis="SPIELBEFEHL")
        befehl({"spielbefehl": {"nr": 34, "werte": [0]}}, 1.0, bis="SPIELBEFEHL")
        print("Kornspeicher", ks, "Getreidefarm", erg["getreide"], "Lager", lager, "Vorrat", vorrat(SP), flush=True)
        # dieselben Bausteine wie im Lenker (erstes_spiel.py phase2)
        w = STW.Stillstand(SP, lambda n: peek(0xF98520 + 0x14 + int(n) * 0x32C + 0x184)[0],
                           lambda: E.baue_schnell(10, lager[0], lager[1], 10, zweck="Stillstand"))
        while peek(TICK)[0] - t0 < 16000:
            kanal.belege()
            st, L, G = E.runde_lesen()
            t = peek(TICK)[0] - t0
            for z in w.schritt(t, L, G):
                print("Tick %d: %s" % (t, z), flush=True)
                erg["ereignisse"].append((t, z))
                if "angebaut" in z and erg["anbau_tick"] is None:
                    erg["anbau_tick"] = t
            v = vorrat(SP).get("weizen", 0)
            erg["weizen"].append((t, v))
            if v > 0 and erg["anbau_tick"] is not None and erg["weizen_tick"] is None:
                erg["weizen_tick"] = t
                print("Tick %d: Weizen im Lager: %d" % (t, v), flush=True)
            if erg["weizen_tick"] or (erg["anbau_tick"] is None and t > 10000) or \
                    (erg["anbau_tick"] is not None and t - erg["anbau_tick"] > 2000):
                break
            warte_ticks(100)
    finally:
        pfad = os.path.join(D, "stillstand_live_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
        json.dump(erg, open(pfad, "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
        try:
            kosten_zurueck(kosten_vorher)
        finally:
            befehl({"pause": True}, 0.5)
    ok = erg["anbau_tick"] is not None and erg["weizen_tick"] is not None
    print("ERGEBNIS: %s - Anbau bei Tick %s, Weizen im Lager bei Tick %s | Daten %s" % (
        "BESTANDEN" if ok else "DURCHGEFALLEN", erg["anbau_tick"], erg["weizen_tick"], pfad), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    kanal.belege()
    try:
        rc = main()
    finally:
        kanal.freigeben()
    raise SystemExit(rc)
