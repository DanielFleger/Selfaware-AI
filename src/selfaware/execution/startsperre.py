# -*- coding: utf-8 -*-
"""Startsperre fuer jedes Gefecht, das per Befehl aufgebaut wird (S169).

Daniel 15.11.2026 11:31: "warum du das Spiel aus dem Hauptmenue direkt startest, anstatt wie besprochen mich erst fragst, wer gegen
wen, auf welcher Map, welche Position und Teams"; 11:33: "bitte starte das Spiel nicht ueber ein Skript, sondern ueber das Spiel -
eigenes Gefecht, Karte auswaehlen, Position auswaehlen (mich davor fragen ...)"; 11:44: "Dann mach daraus einfach keine Disziplin,
sondern erstelle eine Wissensdatenbank, wo drinsteht, wie man ein Spiel startet, dort sollte ganz oben stehen, dass man mich erst
fragen sollte". Die Wissensdatenbank: VillageStudio/doku/Partie-starten.md.

Diese Sperre sitzt in befehl.sende - durch diese Stelle geht jeder Befehl an das Spiel. Ein Start - "eigenesGefecht" (der Skriptweg,
der das Gefecht ohne Menue aufbaut) oder der Startknopf der Lobby (S171, {"knopf": START_KNOPF}) - geht nur durch, wenn in FREIGABE Daniels Aufstellung mit seinem Wortlaut steht und
der Weg zur Freigabe passt ("weg": "menue" fuer den Startknopf, "befehl" nur, wenn Daniel den Befehlsweg ausdruecklich erlaubt). Jede Freigabe gilt fuer genau einen Start; danach steht sie auf
"verbraucht". Ohne Freigabe: Befehl verworfen, Meldung mit dem Verweis auf die Wissensdatenbank.

Freigabe (data/research/partie_freigabe.json), von der Sitzung nach Daniels Antwort geschrieben:
  {"zeit": "15.11.2026 11:50", "daniel": "<sein Wortlaut>", "weg": "menue" | "befehl",
   "aufstellung": {"karte": ..., "gold_spieler": ..., "gold_ki": ..., "spieler": [...], "teams": ..., "positionen": ...},
   "verbraucht": false}"""

import json
import os

from selfaware import workspace as _workspace

FREIGABE = os.path.join(_workspace.DATA, "partie_freigabe.json")
WISSEN = "VillageStudio/doku/Partie-starten.md"


START_KNOPF = (
    "LobbyMenu_LobbyscreenStartButtonClick",
    4,
)  # S171: Startknopf der Lobby (Ghidra: case 4 "start game")


def _weg(c):
    """'befehl' (eigenesGefecht), 'menue' (Startknopf der Lobby) oder None (kein Start)."""
    if not isinstance(c, dict):
        return None
    if c.get("eigenesGefecht"):
        return "befehl"
    if c.get("knopf") == START_KNOPF[0] and str(c.get("nr")) == str(START_KNOPF[1]):
        return "menue"
    return None


def _hat_gefecht(paket):
    if not isinstance(paket, dict):
        return None
    return _weg(paket) or next((w for w in map(_weg, paket.get("befehle") or []) if w), None)


def lesen(pfad=None):
    try:
        return json.load(open(pfad or FREIGABE, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def filtern(paket, pfad=None):
    """Fuer befehl.sende: (Paket oder None, Meldungen). Nur Pakete mit eigenesGefecht werden geprueft."""
    weg = _hat_gefecht(paket)
    if not weg:
        return paket, []
    f = lesen(pfad)
    if not f or not f.get("daniel") or f.get("verbraucht"):
        return None, [
            "STARTSPERRE: kein Gefecht ohne Daniels Aufstellung - erst fragen (%s), dann die Freigabe schreiben (%s)"
            % (WISSEN, pfad or FREIGABE)
        ]
    if f.get("weg") != weg:
        return None, [
            "STARTSPERRE: Start per %s, Daniels Freigabe gilt fuer weg=%r (%s)"
            % (weg, f.get("weg"), WISSEN)
        ]
    f["verbraucht"] = True
    with open(pfad or FREIGABE, "w", encoding="utf-8") as d:
        json.dump(f, d, ensure_ascii=False, indent=1)
    return paket, [
        "STARTSPERRE: Start per %s mit Daniels Freigabe vom %s (jetzt verbraucht)"
        % (weg, f.get("zeit"))
    ]
