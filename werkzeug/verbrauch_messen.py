# -*- coding: utf-8 -*-
"""Nahrungsverbrauch je Kopf messen (SAI 11.10. 23:05; Frage-Agent 23:02: "Wovon lebt das Volk zwischen Verkauf der
Startnahrung und der ersten Lieferung? Ohne Verbrauchsmessung nicht pruefbar").

Pruefstand gegen eine Ratte mit leerer KI, Baukosten 0 (Rueckweg im finally, Daten zuerst gesichert): Kornspeicher, Markt,
4 Huetten, Aepfel gekauft, KEINE Nahrungserzeugung, Steuer 0 (Bestechung). Dann je Rationsstufe `dauer` Ticks: alle 100
Ticks Nahrung gesamt und Leute. Verbrauch je Kopf und 1.000 Ticks = Abnahme / mittlere Leute / Dauer * 1000.
Rationsstufen (haushalt.py RATION_BEL): 0 keine, 1 halbe, 2 normal, 3 extra, 4 doppelt.
Aufruf: SHC_INSTANZ=4 python verbrauch_messen.py [stufen=2,4] [dauer=2500] [tempo=300]"""
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
from wege_abstand import kosten_nullen, kosten_zurueck
from bauen import vorrat

D = os.path.join(HIER, "..", "daten")
SP = 1
ESSEN = ("apfel", "kaese", "fleisch", "brot")


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    stufen = [int(x) for x in arg.get("stufen", "2,4").split(",")]
    dauer = int(arg.get("dauer", 2500))
    E.LEERE_KI, E.GEGNER_ERWARTET = True, ""
    E.LIGA_GEFECHT = dict(E.LIGA_GEFECHT, ki=1)
    E.gefecht_starten(int(arg.get("tempo", 300)))
    setze(GOLD, 20000)
    kosten_vorher = kosten_nullen()
    erg = {"stufen": {}, "reihe": []}
    try:
        info = json.load(open(os.path.join(D, "start_M19.json"), encoding="utf-8"))
        K = tuple(info["bergfried_eingang"])
        erg["kornspeicher"] = E.baue_schnell(19, K[0], K[1], 15)
        erg["markt"] = E.baue_schnell(26, K[0], K[1], 25)
        for i in range(4):
            E.baue_schnell(1, K[0] - 7, K[1] - 2, 25)
        befehl({"spielbefehl": {"nr": 34, "werte": [0]}}, 1.0, bis="SPIELBEFEHL")      # Bestechung haelt die Leute
        warte_ticks(300)
        E.sende({"befehle": [{"player": 1, "id": E.neue_id(), "spielbefehl": {"nr": 38, "werte": [0, E.WAREN_NR["apfel"]]}}
                             for _ in range(34)]}, 2.0, bis="SPIELBEFEHL")
        warte_ticks(100)
        print("Aufbau:", erg["kornspeicher"], erg["markt"], "Vorrat", {k: vorrat(SP).get(k) for k in ESSEN}, flush=True)
        t0 = peek(TICK)[0]
        for stufe in stufen:
            befehl({"spielbefehl": {"nr": 35, "werte": [stufe]}}, 1.0, bis="SPIELBEFEHL")
            warte_ticks(200)                        # Uebergang abwarten
            reihe = []
            ts = peek(TICK)[0]
            while peek(TICK)[0] - ts < dauer:
                kanal.belege()
                v = vorrat(SP)
                st = E.runde_lesen()[0]
                reihe.append((peek(TICK)[0] - t0, sum(v.get(k, 0) for k in ESSEN), st.get("leute"), st.get("beliebt")))
                warte_ticks(100)
            erg["reihe"] += [(stufe,) + r for r in reihe]
            ab = reihe[0][1] - reihe[-1][1]
            leute = sum(r[2] for r in reihe) / float(len(reihe))
            dt = reihe[-1][0] - reihe[0][0]
            je = 1000.0 * ab / leute / dt if leute and dt else None
            erg["stufen"][stufe] = dict(abnahme=ab, leute_mittel=round(leute, 1), ticks=dt, je_kopf_1000=round(je, 3) if je else None,
                                        nahrung_ende=reihe[-1][1])
            print("Ration %d: Nahrung %d -> %d in %d Ticks, Leute im Mittel %.1f -> %.3f je Kopf und 1.000 Ticks" % (
                stufe, reihe[0][1], reihe[-1][1], dt, leute, je or -1), flush=True)
            if reihe[-1][1] <= 5:
                print("Nahrung fast leer - Messung endet", flush=True)
                break
    finally:
        pfad = os.path.join(D, "verbrauch_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
        json.dump(erg, open(pfad, "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
        try:
            kosten_zurueck(kosten_vorher)
        finally:
            befehl({"pause": True}, 0.5)
        print("Daten:", pfad, flush=True)


if __name__ == "__main__":
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
