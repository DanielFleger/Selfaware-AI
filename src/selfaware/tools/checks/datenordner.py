"""Datenordner fuer grosse Aufzeichnungen (B-192 Schritt 6, Daniel 15.11.2026 "Ja, Schritt 6").

Regel (README "Pflicht nach jeder Partie", Punkt 3): Grosse Aufzeichnungen kommen nicht ins Repo, sondern in den Datenordner
neben dem Repo (workspace.DATEN, aenderbar mit SELFAWARE_DATEN_PATH), unter demselben Unterpfad wie im Repo. Im Repo steht nur
das Verzeichnis data/research/datenordner.json: Pfad, Groesse, SHA-256, Zeitstempel des Laufs, Datum. Was "gross" ist, steht
dort unter "regeln" (Grenze je Datei, Ordner, die immer ganz hinueber gehen) - nicht hier im Code.
GitHub nimmt Einzeldateien ueber 100 MiB gar nicht an; die Grenze 50 MB ist die Regel vom 17.10.2026.

Aufruf:
  python -m selfaware.tools.checks.datenordner pruefen [--schnell]   Rueckgabe 1 (rot), wenn eine grosse Datei im Repo liegt
                                                                      oder eine Datei des Verzeichnisses fehlt oder anders ist;
                                                                      --schnell vergleicht nur die Groesse, nicht die Pruefsumme
  python -m selfaware.tools.checks.datenordner auslagern [--tun]     zeigt, was verschoben wuerde; erst mit --tun wird verschoben

Eine versionierte Datei, die nach ihrem Commit ueber die Grenze gewachsen ist (B-194: ein Lageprotokoll wurde in der Pause
weitergeschrieben), gilt auch als gross: auslagern --tun legt die lange Fassung in den Datenordner und holt im Repo die
committete Fassung zurueck - erst nachdem die Pruefsumme im Datenordner stimmt.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

from selfaware import workspace

VERZEICHNIS = os.path.join("data", "research", "datenordner.json")
STEMPEL = re.compile(r"\d{8}_\d{6}")


def _git(wurzel: str, *args: str) -> str:
    r = subprocess.run(["git", "-C", wurzel, *args], capture_output=True, check=True)
    return r.stdout.decode("utf-8", "replace")


def lies_verzeichnis(wurzel: str) -> dict:
    with open(os.path.join(wurzel, VERZEICHNIS), encoding="utf-8") as f:
        return json.load(f)


def schreib_verzeichnis(wurzel: str, verzeichnis: dict) -> None:
    verzeichnis["dateien"] = sorted(verzeichnis["dateien"], key=lambda e: e["pfad"])
    with open(os.path.join(wurzel, VERZEICHNIS), "w", encoding="utf-8", newline="\n") as f:
        json.dump(verzeichnis, f, ensure_ascii=False, indent=1)
        f.write("\n")


def pruefsumme(pfad: str) -> str:
    h = hashlib.sha256()
    with open(pfad, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _unter(pfad: str, ordner: list[str]) -> bool:
    return any(pfad == o or pfad.startswith(o.rstrip("/") + "/") for o in ordner)


def kandidaten(wurzel: str, regeln: dict) -> list[tuple[str, str]]:
    """(art, pfad) je Datei, die in den Datenordner gehoert: art 'neu' (unversioniert) oder 'gewachsen' (versioniert, geaendert)."""
    grenze, ganz = int(regeln["grenze_bytes"]), list(regeln.get("ganze_ordner", []))
    aus = []
    for p in _git(wurzel, "ls-files", "--others", "--exclude-standard", "-z").split("\0"):
        if p and (_unter(p, ganz) or os.path.getsize(os.path.join(wurzel, p)) > grenze):
            aus.append(("neu", p))
    for p in _git(wurzel, "ls-files", "--modified", "-z").split("\0"):
        voll = os.path.join(wurzel, p)
        # das Verzeichnis selbst bleibt immer im Repo, auch wenn es einmal ueber die Grenze waechst
        if (
            p
            and p != VERZEICHNIS.replace(os.sep, "/")
            and os.path.isfile(voll)
            and os.path.getsize(voll) > grenze
        ):
            aus.append(("gewachsen", p))
    return sorted(set(aus), key=lambda x: x[1])


def pruefen(wurzel: str, daten: str, schnell: bool = False) -> list[str]:
    """Befunde als Saetze; leere Liste = gruen."""
    v = lies_verzeichnis(wurzel)
    befunde = [
        "im Repo, gehoert in den Datenordner (%s): %s" % (art, p)
        for art, p in kandidaten(wurzel, v["regeln"])
    ]
    for e in v["dateien"]:
        ziel = os.path.join(daten, e["pfad"])
        if not os.path.isfile(ziel):
            befunde.append("fehlt im Datenordner: " + e["pfad"])
        elif os.path.getsize(ziel) != e["bytes"]:
            befunde.append(
                "andere Groesse im Datenordner: %s (%d statt %d)"
                % (e["pfad"], os.path.getsize(ziel), e["bytes"])
            )
        elif not schnell and pruefsumme(ziel) != e["sha256"]:
            befunde.append("andere Pruefsumme im Datenordner: " + e["pfad"])
    return befunde


def auslagern(wurzel: str, daten: str, tun: bool = False, heute: str | None = None) -> list[dict]:
    """Verschiebt jede grosse Datei in den Datenordner und traegt sie ins Verzeichnis ein. Ohne tun: nur anzeigen."""
    v = lies_verzeichnis(wurzel)
    eintraege = {e["pfad"]: e for e in v["dateien"]}
    heute = heute or datetime.date.today().isoformat()
    erledigt = []
    try:
        for art, p in kandidaten(wurzel, v["regeln"]):
            quelle, ziel = os.path.join(wurzel, p), os.path.join(daten, p)
            groesse = os.path.getsize(quelle)
            print("%s %-9s %12d  %s" % ("verschiebe" if tun else "wuerde    ", art, groesse, p))
            if not tun:
                continue
            if os.path.exists(ziel):
                raise SystemExit(
                    "ANGEHALTEN: im Datenordner liegt schon " + ziel + " - nichts ueberschrieben"
                )
            summe = pruefsumme(quelle)
            os.makedirs(os.path.dirname(ziel), exist_ok=True)
            if art == "neu":
                shutil.move(quelle, ziel)
            else:
                shutil.copy2(quelle, ziel)
            if os.path.getsize(ziel) != groesse or pruefsumme(ziel) != summe:
                raise SystemExit("ANGEHALTEN: Kopie im Datenordner stimmt nicht: " + ziel)
            if art == "gewachsen":
                # erst jetzt: die lange Fassung liegt geprueft im Datenordner
                _git(wurzel, "restore", "--", p)
            stempel = STEMPEL.search(p)
            e = {
                "pfad": p,
                "bytes": groesse,
                "sha256": summe,
                "stempel": stempel.group(0) if stempel else "",
                "ausgelagert": heute,
            }
            if art == "gewachsen":
                e["hinweis"] = (
                    "nach dem Commit weitergeschrieben; im Repo steht die committete Fassung"
                )
            eintraege[p] = e
            erledigt.append(e)
    finally:
        # auch bei einem Abbruch mitten im Lauf: was schon verschoben ist, steht im Verzeichnis (ADR-073)
        if tun and erledigt:
            v["dateien"] = list(eintraege.values())
            schreib_verzeichnis(wurzel, v)
    return erledigt


def main(argv: list[str]) -> int:
    befehl = argv[0] if argv else "pruefen"
    wurzel, daten = workspace.ROOT, workspace.DATEN
    if befehl == "pruefen":
        befunde = pruefen(wurzel, daten, schnell="--schnell" in argv)
        for b in befunde:
            print("ROT  " + b)
        n = len(lies_verzeichnis(wurzel)["dateien"])
        print(
            "%s  Datenordner %s, %d Dateien im Verzeichnis, %d Befunde"
            % ("ROT " if befunde else "GRUEN", daten, n, len(befunde))
        )
        return 1 if befunde else 0
    if befehl == "auslagern":
        e = auslagern(wurzel, daten, tun="--tun" in argv)
        print(
            "%d Dateien %s nach %s"
            % (
                len(e),
                "verschoben" if "--tun" in argv else "(nur angezeigt; mit --tun verschieben)",
                daten,
            )
        )
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
