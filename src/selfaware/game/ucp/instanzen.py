# -*- coding: utf-8 -*-
"""Welche Spielinstanz liegt in welchem Ordner - aus EINER Liste: VillageStudio/lib/instanzen.json.

B-192 (Daniel 15.11.2026 14:18/14:24/14:54): Instanzen heissen nach ihrer Rolle statt nach einer Nummer - "steam" (Steams Ordner,
bleibt unveraendert) und "team-liga" (SamurAI spielen und testen); die frueheren Instanzen 3, 4 und 5 liegen im Archiv auf D:.
SHC_INSTANZ nimmt den Namen oder die Nummer; ohne Angabe gilt "vorgabe" aus der Liste (team-liga, B-197 - frueher Steams Ordner).
Die Nummer bleibt der interne Schluessel fuer Zustandsdateien (.letzte_id2, .lauf2). VillageStudio/werkzeug/instanz.py und
instanz.ps1 lesen dieselbe Liste.
"""

import json
import os

from selfaware import workspace as _workspace

LISTE = os.path.join(_workspace.VILLAGE_STUDIO, "lib", "instanzen.json")


def liste():
    try:
        with open(LISTE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as fehler:
        raise RuntimeError("Instanzen-Liste nicht lesbar: %s (%s)" % (LISTE, fehler)) from fehler


def eintrag(wahl=None):
    """Listeneintrag zu Name oder Nummer; ohne Angabe SHC_INSTANZ, sonst 'vorgabe'. Archiv und Unbekanntes brechen laut ab."""
    L = liste()
    if wahl is None:
        wahl = os.environ.get("SHC_INSTANZ", "").strip() or L["vorgabe"]
    roh = str(wahl).strip()
    for e in L["instanzen"]:
        if roh.lower() == e["name"] or roh == str(e["nummer"]):
            return e
    for a in L.get("archiv", []):
        if roh == str(a["nummer"]):
            raise RuntimeError(
                "Instanz %s liegt seit %s im Archiv: %s - aktiv sind %s"
                % (roh, a["seit"], a["ordner"], ", ".join(x["name"] for x in L["instanzen"]))
            )
    raise RuntimeError(
        "Instanz %r gibt es nicht - aktiv sind %s (%s)"
        % (roh, ", ".join("%s (%d)" % (x["name"], x["nummer"]) for x in L["instanzen"]), LISTE)
    )


def spielordner(wahl=None):
    e = wahl if isinstance(wahl, dict) else eintrag(wahl)
    return os.path.join(liste()["stamm"], e["ordner"])
