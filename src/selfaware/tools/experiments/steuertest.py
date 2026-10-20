# -*- coding: utf-8 -*-
"""Steuerbarkeitstest: laesst sich eine Speicherstelle vom Modul aus steuern?

Ablauf: pausieren -> Original lesen -> Wert schreiben -> sofort zuruecklesen
(angekommen?) -> N Ticks laufen lassen -> pausieren -> zuruecklesen und
einordnen -> Original wiederherstellen (Rueckweg, abschaltbar mit --behalten).

Einordnung:
  GEHALTEN        der geschriebene Wert steht noch da -> steuerbar
  WEITERGERECHNET das Spiel hat vom geschriebenen Wert aus weitergezaehlt -> steuerbar
  ZURUECKGESETZT  das Spiel hat den alten Stand wiederhergestellt -> wird berechnet
  NEU BERECHNET   weder Original noch Wert, weit weg von beiden -> wird berechnet

Aufruf:  uv run python -m selfaware.tools.experiments.steuertest <adresse_hex> <wert> [ticks=100] [tempo=100] [--behalten]
"""
import os, re, sys, time

from selfaware.game.ucp.befehl import sende

def s32(v): return v - 0x100000000 if v > 0x7FFFFFFF else v

def lies(adr):
    for z in sende({"player": 1, "peek": adr, "worte": 1}, 1.0):
        m = re.search(r"PEEK 0x%08X: (\S+)" % adr, z)
        if m:
            return s32(int(m.group(1), 16) & 0xFFFFFFFF)
    return None

def tick():
    m = re.search(r"Tick (\d+)", " ".join(sende({"player": 1, "zeit": True}, 1.0)))
    return int(m.group(1)) if m else None

def main():
    adr, wert = int(sys.argv[1], 16), int(sys.argv[2])
    ticks = int(sys.argv[3]) if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else 100
    tempo = int(sys.argv[4]) if len(sys.argv) > 4 and not sys.argv[4].startswith("--") else 100
    sende({"player": 1, "pause": True}, 1.0)
    t0, orig = tick(), lies(adr)
    sende({"player": 1, "poke": adr, "wert": wert}, 1.0)
    sofort = lies(adr)
    sende({"player": 1, "tempo": tempo}, 0.8)
    sende({"player": 1, "pause": False}, max(0.5, ticks / tempo))
    sende({"player": 1, "pause": True}, 1.0)
    t1, danach = tick(), lies(adr)
    print("Stelle 0x%08X | Tick %s -> %s (%s Ticks)" % (adr, t0, t1, (t1 - t0) if t0 is not None and t1 is not None else "?"))
    print("  Original %s | geschrieben %d | sofort gelesen %s | nach dem Lauf %s" % (orig, wert, sofort, danach))
    if sofort != wert:
        urteil = "NICHT ANGEKOMMEN - Schreiben wirkt nicht einmal im pausierten Spiel"
    elif danach == wert:
        urteil = "GEHALTEN - steuerbar"
    elif orig is not None and danach == orig:
        urteil = "ZURUECKGESETZT - das Spiel stellt den alten Stand her, wird berechnet"
    elif danach is not None and abs(danach - wert) < abs(danach - (orig or 0)):
        urteil = "WEITERGERECHNET - das Spiel zaehlt vom geschriebenen Wert aus weiter, steuerbar"
    else:
        urteil = "NEU BERECHNET - weit weg von Original und Wert, wird berechnet"
    print("  URTEIL:", urteil)
    if "--behalten" not in sys.argv and orig is not None:
        sende({"player": 1, "poke": adr, "wert": orig}, 1.0)
        print("  Rueckweg: Original %s wieder eingetragen (gelesen: %s)" % (orig, lies(adr)))

if __name__ == "__main__":
    main()
