# -*- coding: utf-8 -*-
"""Regler aendern das Handeln (Daniel 16.11.2026 18:18 "am wichtigsten natuerlich ist dass auch wirklich anders gehandelt wird wenn man regler
umstellt"; 18:37 "ja, verbinde die regler und starte die proben"). Plan: Documents/DD-Berichte/SAI/SAI_2026-11-16_plan-regler-handeln.html.

Liest dieselbe Datei wie die Wertungsseite (data/research/wertung/regler.json, telemetry/wertung.REGLER_DATEI). staerke() ist der Betrag der
Summe aller aktiven Gewichte einer Messgroesse, die fuer die Einheitenart gelten. Startgewicht 1 bzw. -1 heisst Staerke 1 und ergibt genau das
Verhalten von vorher; ohne Datei gilt ebenfalls 1. Die Datei wird hoechstens alle NEU_LESEN Sekunden neu gelesen, damit ein Regler auch in
einer laufenden Partie wirkt.

Kopplungen (jede an einer Stelle hier, die Module fragen nur):
  wechsel_huerde  Kehrtwende           -> nahkampf: ein neues Ziel muss um diesen Faktor besser sein als das jetzige
  leer_runden     Steht ohne Wirkung   -> wegfuehrung: Runden ohne Wirkung, bis die Einheit ein anderes Ziel nimmt (#362)
  behalten        Leben eingesetzt     -> gefecht: Rest-Leben, mit dem ein Gefecht als Sieg zaehlt (Vorstoss, Assassinen, Gegenangriff)
Die Stufen je Staerke (HUERDE_JE, BEHALTEN_JE) sind Startwerte, nicht gemessen."""

import json
import os
import time

from selfaware import workspace

DATEI = os.path.join(workspace.DATA, "wertung", "regler.json")
NEU_LESEN = 5.0  # Sekunden
HUERDE_JE = 0.1  # je Staerke ueber 1: so viel muss ein neues Ziel besser sein (Startwert)
BEHALTEN_JE = (
    0.05  # je Staerke ueber 1: so viel weniger Rest-Leben reicht fuer einen Sieg (Startwert)
)
_merk = {"zeit": -1e18, "regler": None}


def neu_lesen():
    _merk["zeit"] = -1e18


def _regler():
    if time.monotonic() - _merk["zeit"] > NEU_LESEN:
        try:
            with open(DATEI, encoding="utf-8") as f:
                _merk["regler"] = json.load(f)["regler"]
        except (OSError, ValueError, KeyError):
            _merk["regler"] = None
        _merk["zeit"] = time.monotonic()
    return _merk["regler"]


def staerke(messgroesse, typ=None):
    """Betrag der Summe der aktiven Gewichte dieser Messgroesse fuer diese Art; 1.0 ohne Datei, 0.0 wenn kein Regler gilt (archiviert)."""
    r = _regler()
    if not r:
        return 1.0
    ws = [
        x["gewicht"]
        for x in r
        if not x.get("archiviert")
        and x.get("messgroesse") == messgroesse
        and (x.get("arten", "alle") == "alle" or typ in x["arten"])
    ]
    return abs(sum(ws)) if ws else 0.0


def wechsel_huerde(typ=None):
    """Faktor, um den ein neues Ziel besser sein muss (1.0 = wie vorher: nur besser). Kehrtwende staerker -> seltener umdrehen."""
    return max(1.0, 1.0 + HUERDE_JE * (staerke("kehrtwende", typ) - 1.0))


def leer_runden(basis, typ=None):
    """Runden ohne Wirkung bis zum Zielwechsel (basis = wegfuehrung.LEER_RUNDEN). Steht ohne Wirkung staerker -> frueher wechseln."""
    s = staerke("steht_ohne_wirkung", typ)
    return max(1, int(round(basis / max(s, 0.1))))


def behalten(basis):
    """Rest-Leben fuer einen Sieg (basis = gefecht.BEHALTEN). Leben eingesetzt fuer andere staerker -> auch knappe Gefechte annehmen."""
    return min(0.9, max(0.05, basis - BEHALTEN_JE * (staerke("vorstoss") - 1.0)))
