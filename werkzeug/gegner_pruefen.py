# -*- coding: utf-8 -*-
"""Gegner-Probe (Daniel 11.10. 14:41 "mach weiter mit dem Nomade"): ein Liga-Gefecht mit Gegner-KI-Art ki starten und
nach ein paar hundert Ticks Lords und Einheitentypen je Spieler zaehlen. Kein Lenker, keine leere KI.
ki = aiType + 1 (logik.lua eigenesGefecht): 1 = Ratte (Rotkaeppchen), 7 = Sultan (Instanz 4: (no)made).
Aufruf: SHC_INSTANZ=4 python gegner_pruefen.py ki=7 [ticks=400] [erwartet=Nomade]

erwartet=<KI-Ordner> (Daniel 11.10. 15:00: "es sind eindeutig sultans starttruppen" - ich hatte aus geaenderten
Typnummern auf den Nomade geschlossen, ohne sie Namen zuzuordnen): Starttruppen 'normal' aus character.json des
Ordners in Typnummern umrechnen und mit Spieler 2 vergleichen; dazu muss ein Lord stehen. Abweichung -> Rueckgabe 1."""
import glob
import json
import os
import sys
import time
from collections import Counter

import befehl as kanal

# character.json-Namen (aiSwapper scripts/troops.lua) -> UnitType (daten/enums_einheit_gebaeude.txt)
TYP = {"EuropArcher": 22, "Crossbowman": 23, "Spearman": 24, "Pikeman": 25, "Maceman": 26, "Swordsman": 27,
       "Knight": 28, "Engineer": 30, "Monk": 37, "ArabArcher": 70, "Slave": 71, "Slinger": 72, "Assassin": 73,
       "HorseArcher": 74, "ArabSwordsman": 75, "FireThrower": 76}
LORD = 55


def erwartete_truppen(ordner):
    pfade = glob.glob(os.path.join(kanal.SPIEL, "ucp", "plugins", "*", "resources", "ai", ordner,
                                   "character.json"))
    # Instanz 4 hat zwei Nomade-Kopien (Ascension-Original + Liga-Kopie vom 11.10.): nur gueltig, wenn sie gleich sind
    werte = [json.load(open(q, encoding="utf-8"))["startTroops"]["normal"] for q in pfade]
    if not werte or any(w != werte[0] for w in werte):
        raise RuntimeError("character.json fuer %s: %d Treffer, Starttruppen %s" % (ordner, len(pfade), werte))
    return Counter({TYP[name]: n for name, n in werte[0].items() if n}), " + ".join(pfade)


def lordfaktor(ordner):
    pfad = glob.glob(os.path.join(kanal.SPIEL, "ucp", "plugins", "*", "resources", "ai", ordner, "character.json"))[0]
    return json.load(open(pfad, encoding="utf-8"))["lord"]["StrengthMultiplier"]


def fruehpruefung(ordner, L):
    """Gleich nach dem Start (Lords stehen, zweite Truppenwelle evtl. noch nicht): Gegner-Lord da, Lebenspunkte im
    Verhaeltnis zu unserem Lord = StrengthMultiplier (gemessen 11.10. 15:10: 30.000 zu 150.000 bei 0,2), und keine
    Truppenart oder Anzahl, die nicht in character.json steht. Gibt die Liste der Abweichungen."""
    soll, _ = erwartete_truppen(ordner)
    l1 = [e for e in L.values() if e["besitzer"] == 1 and e["typ"] == LORD]
    l2 = [e for e in L.values() if e["besitzer"] == 2 and e["typ"] == LORD]
    fehler = []
    if not l1 or not l2:
        return ["Lord fehlt (Spieler 1: %d, Spieler 2: %d)" % (len(l1), len(l2))]
    faktor = lordfaktor(ordner)
    if abs(l2[0]["leben"] / float(l1[0]["leben"]) - faktor) > 0.01:
        fehler.append("Lord-Leben %d zu %d, erwartet Faktor %s" % (l2[0]["leben"], l1[0]["leben"], faktor))
    ist = Counter(e["typ"] for e in L.values() if e["besitzer"] == 2 and e["typ"] in TYP.values())
    fremd = {t: n for t, n in ist.items() if n > soll.get(t, 0)}
    if fremd:
        fehler.append("Truppen %s nicht in character.json (soll %s)" % (sorted(fremd.items()), sorted(soll.items())))
    return fehler


def vergleich(soll, einheiten, lords):
    ist = Counter({t: n for t, n in einheiten.items() if t in TYP.values()})
    fehler = []
    if not lords:
        fehler.append("kein Lord (Burg fehlt?)")
    if ist != soll:
        fehler.append("Truppen ist %s, soll %s" % (sorted(ist.items()), sorted(soll.items())))
    return fehler


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    ki, dauer = int(arg.get("ki", 1)), int(arg.get("ticks", 400))
    import erstes_spiel as E
    from laden import peek, TICK
    from serie import zuruecksetzen
    print("Zuruecksetzen:", zuruecksetzen(), flush=True)
    E.befehl({"tempo": 100}, 1.0, bis="TEMPO")
    saat = E.saat_laden()
    gefecht = dict(E.LIGA_GEFECHT, ki=ki, **({"saat": saat} if saat and "karte" not in arg else {}))
    if "karte" in arg:
        gefecht["karte"] = arg["karte"]
        gefecht.pop("startliste", None)
    zeilen = kanal.sende(gefecht, 4, bis="LaunchSkirmishGame zurueck")
    print("Start:", " | ".join(z for z in zeilen if "GEFECHT" in z or "Launch" in z)[:400], flush=True)
    E.befehl({"pause": False}, 0.5)
    t0, ende = time.time(), None
    while time.time() - t0 < 120:
        t = peek(TICK)[0]
        if t >= dauer:
            break
        time.sleep(0.3)
    st, L, G = E.runde_lesen()
    print("Tick", st.get("t"), flush=True)
    for sp in (1, 2):
        lords = [(e["x"], e["y"], e["leben"]) for e in L.values() if e["besitzer"] == sp and e["typ"] == LORD]
        print("Spieler %d: Lord %s, Einheiten %s" % (sp, lords or "KEINER",
              sorted(Counter(e["typ"] for e in L.values() if e["besitzer"] == sp).items())), flush=True)
    E.befehl({"pause": True}, 0.5)
    if "erwartet" not in arg:
        return 0
    soll, quelle = erwartete_truppen(arg["erwartet"])
    lords2 = [e for e in L.values() if e["besitzer"] == 2 and e["typ"] == LORD]
    fehler = vergleich(soll, Counter(e["typ"] for e in L.values() if e["besitzer"] == 2), lords2)
    print(("STARTTRUPPEN UND LORD PASSEN zu %s (%s)" % (arg["erwartet"], quelle)) if not fehler
          else "STARTTRUPPEN PASSEN NICHT zu %s: %s" % (arg["erwartet"], "; ".join(fehler)), flush=True)
    return 1 if fehler else 0


if __name__ == "__main__":
    kanal.belege()
    try:
        rc = main()
    finally:
        kanal.freigeben()
    raise SystemExit(rc)
