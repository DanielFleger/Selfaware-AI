# -*- coding: utf-8 -*-
"""S161 (Daniel 15.11.2026 01:32 "bis auf assassinen will keine einheit wirklich gebaeude angreifen ... kannst du bitte allen auch
diese faehigkeiten geben nicht nur assassinen?"): Spielwerte aus der Balance-Datei, die die Instanz wirklich laedt (Erweiterung
rebalancer, ucp-config.yml balance_config_file_selector; Instanz 2: Mod-KI-Team-Liga-2.0.2/.../liga_ai.json). Hier der
Gebaeudeschaden je Einheitenart (buildingDamage, abgelesen 15.11.2026 01:31: Speertraeger 10, Assassine 75, arab. Schwertkaempfer 100).
Ohne lesbare Datei: {} - die Wertrechnung rechnet dann wie bisher."""
import glob
import json
import os

# Namen der Einheiten in der Balance-Datei -> Art im Spiel (micro/unit_log.NAMES)
ARTEN = {"Tunneler": 5, "European archer": 22, "European crossbowman": 23, "European spearman": 24, "European pikeman": 25,
         "European maceman": 26, "European swordsman": 27, "European knight": 28, "Lord": 55, "Arabian archer": 70,
         "Arabian slave": 71, "Arabian slinger": 72, "Arabian assassin": 73, "Arabian horse archer": 74, "Arabian swordsman": 75,
         "Arabian firethrower": 76}


def datei(spiel_ordner):
    """Pfad der Balance-Datei, die ucp-config.yml dem rebalancer gibt, oder None."""
    try:
        zeilen = open(os.path.join(spiel_ordner, "ucp-config.yml"), encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        return None
    for i, z in enumerate(zeilen):
        if "balance_config_file_selector" in z:
            for w in zeilen[i + 1:i + 6]:
                if w.strip().startswith("value:"):
                    muster = w.split("value:", 1)[1].strip().strip("'\"")
                    treffer = sorted(glob.glob(os.path.join(spiel_ordner, muster)))
                    return treffer[-1] if treffer else None
    return None


def gebaeudeschaden(spiel_ordner=None):
    """{Art: buildingDamage} der aktiven Balance, {} wenn sie nicht lesbar ist."""
    if spiel_ordner is None:
        try:
            from selfaware.game.ucp.befehl import SPIEL as spiel_ordner
        except Exception:
            return {}
    pfad = datei(spiel_ordner)
    if not pfad:
        return {}
    try:
        d = json.load(open(pfad, encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    aus = {}
    for name, werte in (d.get("units") or {}).items():
        if name in ARTEN and isinstance(werte, dict) and werte.get("buildingDamage"):
            aus[ARTEN[name]] = float(werte["buildingDamage"])
    return aus
