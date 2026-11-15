# -*- coding: utf-8 -*-
"""Mitschrift je Takt der eigenen Soldaten (B-182; Daniel 13.11.2026 23:46 "Ja, mitschreiben" auf die Frage, ob in der naechsten
Partie die Bogenschuetzen Takt fuer Takt mitgeschrieben werden - Partie 10: Bogenschuetze 308 verschwand zwischen Takt 1152 und
1362 ohne Feind in der Naehe und ohne Aufloese-Befehl, seine Nummer trug danach ein Bauer am Lagerfeuer, Wissensregister S133).

Liest den Kern jeden Takt (kern_leitung.Leitung, nur lesen, kein Befehl ans Spiel) und schreibt:
  {"t": Takt, "e": {Nummer: [Typ, x, y, Zustand, Leben, Zielart, Zieleinheit, Nahziel, Laufziel x, y, geplantes Ziel x, y, Gruppe,
     logicalState, moveRelatedFlag, goToRallyPoint, usingTeleport, rallyRelatedFlag, moveableUnk]}}  - nur geaenderte eigene Soldaten
     (ab 14.11.2026 21:05, S139; aeltere Mitschriften haben nur die ersten 10)
  {"t": Takt, "verschwunden": Nummer, "jetzt": ..., "verlauf": [die letzten VERLAUF Eintraege], "umgebung": [...]}  - wenn ein eigener
     Soldat fehlt, die Nummer die Art wechselt oder den Besitzer; umgebung = alle Einheiten bis UMGEBUNG Felder um seinen letzten Ort
     im Takt davor (Nummer, Besitzer, Typ, x, y, Zustand, Leben, Zieleinheit, Nahziel)
  {"t": Takt, "stockt": Nummer, "feld": [x, y], "seit": Takt, "umgebung": [...]}  - ein eigener Soldat laeuft (Zustand 101), steht
     aber laenger als STOCK_FELDER flache Felder (laufmodell, je Art) auf demselben Feld; umgebung = alle Einheiten bis STOCK_UMGEBUNG
     Felder (Daniel 14.11.2026 00:01 "Ja, erweitern" - Partie 11: Speertraeger 335 verlor 31 Takte auf 2 Feldern, S134)
Aufruf (PYTHONPATH=src): SHC_INSTANZ=2 python -m selfaware.tools.experiments.soldaten_mitschrift [minuten=30] [spieler=1]
Ende: nach minuten, oder wenn der Takt STILL_SEKUNDEN lang steht (Partie vorbei oder angehalten).
Ausgabe: data/research/soldaten_mitschrift_<Stempel>_i<Instanz>.jsonl
"""

import collections
import json
import os
import sys
import time

from selfaware import workspace as _workspace
from selfaware.micro.rollen import TRUPPE

# S139 (Daniel 14.11.2026 20:56 "Ja, mitschreiben"): hinten die Filterfelder des Marschbefehls - die alten Stellen bleiben
FELDER = (
    "typ",
    "x",
    "y",
    "zustand",
    "leben",
    "zielart",
    "zieleinheit",
    "nahziel",
    "laufx",
    "laufy",
    "planx",
    "plany",
    "gruppe",
    "logikzustand",
    "laufmerker",
    "sammelgang",
    "teleport",
    "sammelmerker",
    "beweglich",
    "merker413",
    "gebiet",
)  # S143: field320_0x413; S148: Gebiet des Wegnetzes am Feld der Einheit
VERLAUF = 40  # Eintraege je Soldat, die beim Verschwinden mitgeschrieben werden
UMGEBUNG = 12  # Felder um den letzten Ort
STILL_SEKUNDEN = 30
STOCK_FELDER = 2  # selbst gesetzt: so viele flache Felder Zeit auf einem Feld gilt als Stocken (nicht gemessen)
STOCK_UMGEBUNG = 2  # Felder um den stockenden Soldaten


def zeile(e):
    return [e.get(k) for k in FELDER]


def soldaten(einheiten, sp):
    return {
        n: e for n, e in einheiten.items() if e.get("besitzer") == sp and e.get("typ") in TRUPPE
    }


def vergleiche(alt, neu, sp):
    """alt, neu: {Nummer: Einheit} zweier Takte -> (geaendert {Nummer: zeile}, verschwunden [(Nummer, was jetzt dort ist oder None)])."""
    a, b = soldaten(alt, sp), soldaten(neu, sp)
    geaendert = {n: zeile(e) for n, e in b.items() if n not in a or zeile(a[n]) != zeile(e)}
    weg = [
        (n, (zeile(neu[n]) + [neu[n].get("besitzer")]) if n in neu else None)
        for n in sorted(set(a) - set(b))
    ]
    return geaendert, weg


def umgebung(einheiten, ort, r=UMGEBUNG):
    return [
        [
            n,
            e.get("besitzer"),
            e.get("typ"),
            e.get("x"),
            e.get("y"),
            e.get("zustand"),
            e.get("leben"),
            e.get("zieleinheit"),
            e.get("nahziel"),
        ]
        for n, e in sorted(einheiten.items())
        if max(abs(e["x"] - ort[0]), abs(e["y"] - ort[1])) <= r
    ]


def stocken(stand, einheiten, tick, sp):
    """stand: {Nummer: [Feld, seit Takt, gemeldet]} (wird fortgeschrieben). -> Ereignisse fuer laufende eigene Soldaten, die laenger als
    STOCK_FELDER flache Felder auf demselben Feld stehen - einmal je Halt."""
    import selfaware.services.laufmodell as LM

    aus = []
    for n, e in soldaten(einheiten, sp).items():
        feld = (e["x"], e["y"])
        s = stand.get(n)
        if e.get("zustand") != 101 or s is None or s[0] != feld:
            stand[n] = [feld, tick, False]
            continue
        grenze = STOCK_FELDER * (LM.flat_ticks_per_field(e["typ"]) if e["typ"] in LM.TYPES else 16)
        if not s[2] and tick - s[1] > grenze:
            s[2] = True
            aus.append(
                {
                    "t": tick,
                    "stockt": n,
                    "typ": e["typ"],
                    "feld": list(feld),
                    "seit": s[1],
                    "umgebung": [u for u in umgebung(einheiten, feld, STOCK_UMGEBUNG) if u[0] != n],
                }
            )
    for n in [n for n in stand if n not in einheiten]:
        del stand[n]
    return aus


def lies(le):
    """Ein Weltbild oder None: auch None, solange der Kern noch nichts geschrieben hat (Partie 14, 14.11.2026 19:32: die Mitschrift
    startete mit dem Spiel vor der Partie und brach mit 'Kennung 0x0 / Aufbau 0' ab - die Partie blieb ohne Mitschrift)."""
    from selfaware.game.kern_leitung import FalscherAufbau

    try:
        return le.lesen()
    except FalscherAufbau:
        return None


def main(argv=None):
    import selfaware.game.kern_leitung as KL
    from selfaware.game.ucp.befehl import SPIEL

    arg = dict(a.split("=", 1) for a in (sys.argv[1:] if argv is None else argv) if "=" in a)
    minuten, sp = float(arg.get("minuten", 30)), int(arg.get("spieler", 1))
    instanz = os.environ.get("SHC_INSTANZ", "1")
    pfad = os.path.join(
        _workspace.DATA,
        "soldaten_mitschrift_%s_i%s.jsonl" % (time.strftime("%Y%m%d_%H%M%S"), instanz),
    )
    le = KL.Leitung(SPIEL)
    verlauf = collections.defaultdict(lambda: collections.deque(maxlen=VERLAUF))
    alt, letzter, still_seit, ende = None, None, time.time(), time.time() + 60 * minuten
    takte = weg_zahl = stock_zahl = 0
    stand = {}
    with open(pfad, "w", encoding="utf-8") as f:
        while time.time() < ende:
            w = lies(le)
            if w is None or w.tick == letzter:
                # erst nach einer laufenden Partie: vor dem Start steht die alte, angehaltene Partie still
                if time.time() - still_seit > STILL_SEKUNDEN and takte > 100:
                    break
                time.sleep(0.002)
                continue
            if letzter is not None and w.tick < letzter:  # eine neue Partie: von vorn
                alt, takte = None, 0
                verlauf.clear()
                stand.clear()
            still_seit, letzter, takte = time.time(), w.tick, takte + 1
            neu = dict(w.einheiten)
            if alt is None:
                alt = neu
                f.write(
                    json.dumps(
                        {
                            "t": w.tick,
                            "start": True,
                            "e": {n: zeile(e) for n, e in soldaten(neu, sp).items()},
                        }
                    )
                    + "\n"
                )
                continue
            geaendert, weg = vergleiche(alt, neu, sp)
            for n, z in geaendert.items():
                verlauf[n].append([w.tick] + z)
            for ereignis in stocken(stand, neu, w.tick, sp):
                f.write(json.dumps(ereignis) + "\n")
                stock_zahl += 1
            if geaendert:
                f.write(json.dumps({"t": w.tick, "e": geaendert}) + "\n")
            for n, jetzt in weg:
                e = alt[n]
                weg_zahl += 1
                f.write(
                    json.dumps(
                        {
                            "t": w.tick,
                            "verschwunden": n,
                            "war": zeile(e),
                            "jetzt": jetzt,
                            "verlauf": list(verlauf[n]),
                            "umgebung": umgebung(alt, (e["x"], e["y"])),
                        }
                    )
                    + "\n"
                )
                f.flush()
                print(
                    "VERSCHWUNDEN Takt %d: %d (Typ %s) bei (%s,%s), jetzt %s"
                    % (w.tick, n, e.get("typ"), e["x"], e["y"], jetzt),
                    flush=True,
                )
            alt = neu
    print(
        "MITSCHRIFT Ende: %d Takte, %d verschwunden, %d Halte -> %s"
        % (takte, weg_zahl, stock_zahl, pfad),
        flush=True,
    )


if __name__ == "__main__":
    main()
