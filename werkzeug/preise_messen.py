# -*- coding: utf-8 -*-
"""Marktpreise unter der laufenden Balance messen (SAI 12.10., Daniel 01:09: "du brauchst Cash von Steinen/Eisen/Brot etc.").

Anlass: 1012g baute 103 Holzfaeller und hatte bei Tick 14.242 nur 37 Gold - das Kausalmodell rechnet je Holz 1 Gold, die
Ascension-Balance (ascension_ai.json "resources") nennt fuer Holz aber gar keinen Verkaufspreis. Abgelesene Werte sind
keine Messung: je Ware EIN Los kaufen und EIN Los verkaufen (Spielbefehl 38, [0, Ware] / [1, Ware], wie der Lenker) und
Gold und Bestand davor/danach lesen. Preis je Stueck = Gold-Aenderung / Bestand-Aenderung, getrennt fuer Kauf und Verkauf.
(12.10. 01:12, erster Versuch: Vorrat per "ware" setzen kommt nicht an - das Spiel zaehlt Waren aus den Lagern nach;
nur Gold laesst sich setzen. Darum Gold setzen, Marktplatz + Kornspeicher bauen, kaufen.)
Pruefstand: Grumpy Neighbors gegen eine Ratte mit leerer KI (kein funktionierender Gegner).
Ausgabe: daten/preise_<zeit>.json. Aufruf: SHC_INSTANZ=4 python preise_messen.py [tempo=100] [menge=50]"""
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import befehl as kanal
import erstes_spiel as E
from laden import befehl
from streitkolben_messen import warte_ticks, setze, GOLD
from bauen import vorrat

D = os.path.join(HIER, "..", "daten")
SP = 1
# Ware -> (Nummer im Spiel, Name in der Vorratszeile); Nummern wie WAREN_NR im Lenker
WAREN = {"holz": 2, "hopfen": 3, "stein": 4, "eisen": 6, "pech": 7, "weizen": 9, "brot": 10, "kaese": 11,
         "fleisch": 12, "apfel": 13, "mehl": 16}


def setze_ware(nr, menge):
    befehl({"player": SP, "ware": {"typ": nr, "menge": menge}}, 0.8, bis="WARE")


def verkaufe(nr):
    kanal.sende({"befehle": [{"player": SP, "id": kanal.neue_id(), "spielbefehl": {"nr": 38, "werte": [1, nr]}}]},
                1.0, bis="SPIELBEFEHL")


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    menge = int(arg.get("menge", 50))
    E.LEERE_KI, E.GEGNER_ERWARTET = True, ""
    E.LIGA_GEFECHT = dict(E.LIGA_GEFECHT, ki=1)
    E.gefecht_starten(int(arg.get("tempo", 100)))
    erg = {"waren": {}}
    try:
        setze(GOLD, 20000)
        info = json.load(open(os.path.join(D, "start_M19.json"), encoding="utf-8"))
        K = tuple(info["bergfried_eingang"])
        for typ in (26, 19):                       # Marktplatz, Kornspeicher (Nahrung landet dort)
            ort = E.freier_platz(typ, K, 25)
            erg["bau_%d" % typ] = (ort, E.baue_schnell(typ, ort[0], ort[1], 25) if ort else None)
        warte_ticks(200)
        def schritt(nr, wert):
            v0 = vorrat(SP)
            kanal.sende({"befehle": [{"player": SP, "id": kanal.neue_id(), "spielbefehl": {"nr": 38, "werte": [wert, nr]}}]},
                        1.0, bis="SPIELBEFEHL")
            warte_ticks(10)
            v1 = vorrat(SP)
            return v0, v1
        nur = [w for w in arg.get("nur", "").split(",") if w]
        if nur:
            # 01:13: Lagerware (Stein, Eisen, Pech, Weizen, Mehl) liess sich nicht kaufen - vermutlich kein freies Lagerteil
            # (jedes Teil haelt nur eine Ware). Vorher Holz verkaufen, bis es weg ist, damit Teile frei werden.
            for _ in range(40):
                if vorrat(SP).get("holz", 0) <= 0:
                    break
                schritt(WAREN["holz"], 1)
            erg["holz_nach_leeren"] = vorrat(SP).get("holz")
            print("Holz nach dem Leeren:", erg["holz_nach_leeren"], flush=True)
        for name, nr in WAREN.items():
            if nur and name not in nur:
                continue
            k0, k1 = schritt(nr, 0)                # kaufen
            s0, s1 = schritt(nr, 1)                # verkaufen
            zu, kost = k1.get(name, 0) - k0.get(name, 0), k0.get("gold", 0) - k1.get("gold", 0)
            ab, erl = s0.get(name, 0) - s1.get(name, 0), s1.get("gold", 0) - s0.get("gold", 0)
            erg["waren"][name] = dict(nr=nr, kauf_stueck=zu, kauf_gold=kost, kauf_je=round(kost / float(zu), 2) if zu else None,
                                      verkauf_stueck=ab, verkauf_gold=erl, verkauf_je=round(erl / float(ab), 2) if ab else None,
                                      bestand=[k0.get(name), k1.get(name), s1.get(name)])
            print("%-8s Nr %2d: kauf %s Stueck fuer %s Gold (je %s) | verkauf %s Stueck fuer %s Gold (je %s) | Bestand %s" % (
                name, nr, zu, kost, erg["waren"][name]["kauf_je"], ab, erl, erg["waren"][name]["verkauf_je"],
                erg["waren"][name]["bestand"]), flush=True)
    finally:
        pfad = os.path.join(D, "preise_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
        json.dump(erg, open(pfad, "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
        befehl({"pause": True}, 0.5)
        print("Daten:", pfad, flush=True)


if __name__ == "__main__":
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
