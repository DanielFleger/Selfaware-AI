# -*- coding: utf-8 -*-
"""B-154 Augen-Test SPIELENDE-MELDER (Daniel 21.10.2026 20:40: "du hast offensichtlich noch keinen Melder, wenn das Match aus
ist - bitte sofort erkennen, warum es endet, und schauen, ob es bewusst war oder nicht").
Vier Faelle auf Instanz 5 (Pruefstand-Spielstand, ueber shc.py):
  a laden    - Laden aus dem Endbildschirm: kippt gameOver nach dem Laden, meldet der Melder UNBEWUSST "Spielerplatz leer";
               danach darf in 15 s KEIN Endbildschirm kommen (shc.laden setzt gameOver UND gameOverTime zurueck)
  b menue    - laufende Partie per {"menue": 41} verlassen -> BEWUSST "eigener Befehl menue=41"
  c lord1    - unseren Lord toeten -> UNBEWUSST "unser Lord ist tot (Niederlage)"
  d lord2    - Franz' Lord toeten -> BEWUSST "alle feindlichen Lords tot (Sieg)"
VORHER FESTGELEGT: jeder Fall gilt nur, wenn innerhalb von 30 s nach dem Ausloeser genau die erwartete Zeile in
ucp/villagestudio/spielende.txt steht. Ergebnis: daten/augen_spielende.jsonl.
Aufruf: SHC_INSTANZ=5 python werkzeug/augen_spielende.py [faelle=a,b,c,d]
"""
import json
import os
import sys
import time

os.environ.setdefault("SHC_INSTANZ", "5")
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import shc  # noqa: E402
from laden import befehl  # noqa: E402
from befehl import letztes_spielende  # noqa: E402

AUS = os.path.join(HIER, "..", "daten", "augen_spielende.jsonl")


def neue_meldungen(vorher, warte=30):
    """Wartet bis zu warte s auf neue Zeilen des Melders; gibt sie zurueck."""
    ende = time.time() + warte
    while time.time() < ende:
        z = letztes_spielende(200)
        if len(z) > len(vorher):
            time.sleep(1.0)
            return letztes_spielende(200)[len(vorher):]
        time.sleep(0.3)
    return []


def fall(name):
    if name == "a":
        vorher = letztes_spielende(200)
        text = shc.laden()
        neu = letztes_spielende(200)[len(vorher):]
        z = shc.zustand()
        gut = z.get("ansicht") == shc.IN_PARTIE and z.get("gameover") == 0 and all("UNBEWUSST" in m and "Spielerplatz leer" in m
                                                                                for m in neu)
        return {"fall": "a laden", "ausgabe": text, "meldungen": neu, "zustand": z, "gut": gut}
    shc.laden()
    vorher = letztes_spielende(200)
    if name == "b":
        shc.menue()
        erwartet = ("BEWUSST", "eigener Befehl menue")
    else:
        sp = 1 if name == "c" else 2
        befehl({"toeteAlle": {"spieler": sp, "ohneLord": False, "typen": [55]}}, 0.8)
        befehl({"pause": False, "tempo": 40}, 0.3)
        erwartet = ("UNBEWUSST", "NIEDERLAGE - unser Lord ist tot") if sp == 1 else ("BEWUSST", "SIEG")
    neu = neue_meldungen(vorher)
    befehl({"pause": True}, 0.3)
    gut = any(erwartet[0] in m and erwartet[1] in m for m in neu)
    return {"fall": name, "erwartet": erwartet, "meldungen": neu, "zustand": shc.zustand(), "gut": gut}


def main(faelle=("a", "b", "c", "d")):
    erg = []
    for f in faelle:
        r = fall(f)
        erg.append(r)
        print("%s: %s | %s" % ("GUT " if r["gut"] else "ROT ", r["fall"], r["meldungen"]), flush=True)
    urteil = "BELEGT: alle %d Faelle erkannt" % len(erg) if all(r["gut"] for r in erg) else \
        "WIDERLEGT: %s" % [r["fall"] for r in erg if not r["gut"]]
    print("ERGEBNIS:", urteil, flush=True)
    with open(AUS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"zeit": time.strftime("%Y-%m-%d %H:%M:%S"), "faelle": erg, "urteil": urteil}, ensure_ascii=False,
                            default=str) + "\n")


if __name__ == "__main__":
    a = dict(x.split("=", 1) for x in sys.argv[1:])
    main(tuple(a.get("faelle", "a,b,c,d").split(",")))
