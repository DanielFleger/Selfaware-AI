"""Aufstellungen und Steckplaetze (B-176, docs/plans/Plan_Baukasten.md).

Eine Aufstellung ist eine Datei unter configs/aufstellungen/: Sie nennt Schalter des Lenkers und, unter "versionen", welche Klasse auf welchem
Steckplatz laeuft. Damit startet jede Partie mit einem Namen, und zwei Aufstellungen lassen sich vergleichen (aufstellung_vergleich.py).
Was auf der Befehlszeile steht, gilt vor der Datei. Eine Aufstellung darf mit "basis" auf einer anderen aufbauen, muss dann aber unter
"gruende" fuer jede Aenderung einen Grund nennen (Daniel: "Wenn du nicht auf alles einen guten grund hast dann erfinde keinen").

Neue Version eines Moduls: Klasse, die am einfachsten von der heutigen erbt, in eine eigene Datei; in der Aufstellung
"versionen": {"brandtrupp": "selfaware.paket.modul:Klasse"}. Die Pruefung dafuer laeuft vor dem Start, nicht mitten in der Partie.
"""

import hashlib
import importlib
import inspect
import json
import pathlib

from selfaware import workspace
from selfaware.baukasten import karte as K

ORDNER = pathlib.Path(workspace.ROOT) / "configs" / "aufstellungen"


def laden(name, ordner=ORDNER, _weg=()):
    """Liest eine Aufstellung samt ihrer Basis. Was nicht stimmt, faellt sofort auf: Eine Partie darf nicht still mit etwas anderem laufen."""
    if name in _weg:
        raise ValueError(f"Aufstellung {name} baut im Kreis auf sich selbst auf: {_weg}")
    pfad = pathlib.Path(ordner) / f"{name}.json"
    daten = json.loads(pfad.read_text(encoding="utf-8"))
    if daten.get("name") != name or not isinstance(daten.get("schalter"), dict):
        raise ValueError(f"Aufstellung {pfad} braucht name={name} und schalter")
    if "basis" not in daten:
        return daten
    ohne_grund = sorted(
        (set(daten["schalter"]) | set(daten.get("versionen", {}))) - set(daten.get("gruende", {}))
    )
    if ohne_grund:
        raise ValueError(f"Aufstellung {name} aendert ohne Grund: {ohne_grund}")
    basis = laden(daten["basis"], ordner, (*_weg, name))
    return {
        **daten,
        "schalter": {**basis["schalter"], **daten["schalter"]},
        "versionen": {**basis.get("versionen", {}), **daten.get("versionen", {})},
    }


def anwenden(arg, ordner=ORDNER):
    """Fuegt die Schalter der Aufstellung arg["aufstellung"] hinzu. Was auf der Befehlszeile steht, gilt vor der Datei."""
    if "aufstellung" not in arg:
        return arg, None
    daten = laden(arg["aufstellung"], ordner)
    return {**{k: str(v) for k, v in daten["schalter"].items()}, **arg}, daten


def startzeile(roh, arg, daten):
    """Die Argumente der START-BEFEHL-Zeile. Ohne Aufstellung wie eingegeben, mit Aufstellung jeder Schalter, damit die Mitschrift die Partie allein beschreibt."""
    return list(roh) if daten is None else [f"{k}={v}" for k, v in arg.items()]


def _holen(pfad):
    modul, _, klasse = pfad.partition(":")
    return getattr(importlib.import_module(modul), klasse)


def _vertrag_pruefen(name, neu, alt):
    """Eine neue Version muss alles anbieten, was die heutige Klasse oeffentlich kann, mit denselben Aufrufen."""
    for f, alte in inspect.getmembers(alt, inspect.isfunction):
        if f.startswith("_") and f != "__init__":
            continue
        neue = getattr(neu, f, None)
        if neue is None or inspect.signature(neue) != inspect.signature(alte):
            raise ValueError(
                f"Steckplatz {name}: {neu.__name__}.{f} passt nicht zu {alt.__name__}.{f}"
            )


class Steckplaetze:
    """Welche Klasse je Modul laeuft. Ohne Eintrag die von heute."""

    def __init__(self, versionen=None):
        self.standard = K.steckplaetze()
        self.versionen = dict(versionen or {})
        for name, pfad in self.versionen.items():
            if name not in self.standard:
                raise ValueError(
                    f"Unbekannter Steckplatz {name}, vorhanden: {sorted(self.standard)}"
                )
            _vertrag_pruefen(name, _holen(pfad), _holen(self.standard[name]))

    def klasse(self, name):
        return _holen(self.versionen.get(name, self.standard[name]))

    def __str__(self):
        """Fuer die Mitschrift, mit Pruefsumme: Die Code-Kennung folgt nur den import-Zeilen und sieht eine gesteckte Datei nicht."""
        teile = []
        for name, pfad in sorted(self.versionen.items()):
            datei = pathlib.Path(inspect.getsourcefile(_holen(pfad)))
            teile.append(
                f"{name}={pfad} sha256:{hashlib.sha256(datei.read_bytes()).hexdigest()[:12]}"
            )
        return ", ".join(teile) or "alle von heute"
