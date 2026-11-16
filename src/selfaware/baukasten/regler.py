# -*- coding: utf-8 -*-
"""Regler aendern das Handeln (Daniel 16.11.2026 18:18 "am wichtigsten natuerlich ist dass auch wirklich anders gehandelt wird wenn man regler
umstellt"; 18:37 "ja, verbinde die regler und starte die proben"). Plan: Documents/DD-Berichte/SAI/SAI_2026-11-16_plan-regler-handeln.html.

Liest dieselbe Datei wie die Wertungsseite (data/research/wertung/regler.json, telemetry/wertung.REGLER_DATEI). staerke() ist der Betrag der
Summe aller aktiven Gewichte einer Messgroesse, die fuer die Einheitenart gelten. Startgewicht 1 bzw. -1 heisst Staerke 1 und ergibt genau das
Verhalten von vorher; ohne Datei gilt ebenfalls 1. Die Datei wird hoechstens alle NEU_LESEN Sekunden neu gelesen, damit ein Regler auch in
einer laufenden Partie wirkt.

SCHALTER (Daniel 16.11.2026 19:30 "Ja, so starten" auf "Regler nur bewerten lassen und Probe 9 mit Kern 38 starten?" - 19:03 "das wichtigste
ist dass daraus eine aktion an den code folgt und nicht direkt an den regler"): Die Regler bewerten nur. Aufs Handeln wirken sie erst, wenn
der Schalter in SCHALTER_DATEI an ist - gedacht fuer eine Testreihe mit genau einem Regler. Aus (Standard, auch ohne Datei) gilt das Verhalten
der Startgewichte, also das vor den Kopplungen.

Kopplungen (jede an einer Stelle hier, die Module fragen nur):
  wechsel_huerde  Kehrtwende           -> nahkampf: ein neues Ziel muss um diesen Faktor besser sein als das jetzige
  leer_runden     Steht ohne Wirkung   -> wegfuehrung: Runden ohne Wirkung, bis die Einheit ein anderes Ziel nimmt (#362)
  behalten        Leben eingesetzt     -> gefecht: Rest-Leben, mit dem ein Gefecht als Sieg zaehlt (Vorstoss, Assassinen, Gegenangriff)
  dazu_vorzug     Gemeinsam gewirkt    -> zielvergabe: ein schon angegriffenes Ziel bekommt so viel mehr Wert (Nahkampf-Raid, Assassinen)
  chance_radius   Chance verpasst      -> nahkampf: so weit schaut eine Einheit, die sonst wartet, nach Arbeitern (sonst nur direkt am Weg)
  zielwert        Gebaeude/Arbeiter/   -> nahkampf: Faktor auf den Wert je Zielart (Gebaeudeschaden + Gebaeude zerstoert, Arbeiter getoetet)
                  Soldat                  und aufs Zurueckschlagen gegen einen Soldaten (Soldat verletzt + Soldat getoetet)
Daniel 16.11.2026 18:50: "versuche alle kopplungen zu machen". Der Lord ist nicht gekoppelt: auf ihn gehen alle ohne Wertrechnung, sobald die
Assassinen ihn angreifen (Daniel 15.11.2026 01:50 "so schnell und erbarmungslos wie moeglich killen") - ein Lord-Regler haette dort
nichts zu verstellen. Die Stufen je Staerke (HUERDE_JE, BEHALTEN_JE, VORZUG_JE, CHANCE_JE) sind Startwerte, nicht gemessen."""

import json
import os
import time

from selfaware import workspace

DATEI = os.path.join(workspace.DATA, "wertung", "regler.json")
SCHALTER_DATEI = os.path.join(workspace.DATA, "wertung", "handeln.json")
NEU_LESEN = 5.0  # Sekunden
HUERDE_JE = 0.1  # je Staerke ueber 1: so viel muss ein neues Ziel besser sein (Startwert)
BEHALTEN_JE = (
    0.05  # je Staerke ueber 1: so viel weniger Rest-Leben reicht fuer einen Sieg (Startwert)
)
VORZUG_JE = (
    0.1  # je Staerke ueber 1: so viel mehr Wert bekommt ein schon angegriffenes Ziel (Startwert)
)
CHANCE_JE = 5.0  # Felder je Staerke ueber 1: so weit sieht eine sonst wartende Einheit nach Arbeitern (Startwert)
# Zielart -> Lohn-Messgroessen, deren Gewichte ihren Wert bestimmen (Mittel; telemetry/wertung.MESSGROESSEN)
ZIELWERT = {
    "gebaeude": ("gebaeude_schaden", "gebaeude_zerstoert"),
    "arbeiter": ("bevoelkerung_kill",),
    "soldat": ("einheit_schaden", "einheit_kill"),
}
_merk = {"zeit": -1e18, "regler": None}


def neu_lesen():
    _merk["zeit"] = -1e18


def handeln_lesen():
    """Stand des Schalters: {"an": bool, "zeit", "wer", "grund", "verlauf": [...]}; ohne Datei aus."""
    try:
        with open(SCHALTER_DATEI, encoding="utf-8") as f:
            d = json.load(f)
        return dict(d, an=d.get("an") is True)
    except (OSError, ValueError, AttributeError):
        return {"an": False, "verlauf": []}


def handeln_setzen(an, wer, grund=""):
    """Schaltet um und haengt die Aenderung an den Verlauf des Schalters (der Rueckweg ist dasselbe mit dem alten Wert)."""
    import datetime

    alt = handeln_lesen()
    zeit = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    eintrag = {"zeit": zeit, "wer": wer, "grund": grund, "alt": alt["an"], "neu": bool(an)}
    neu = {
        "an": bool(an),
        "zeit": zeit,
        "wer": wer,
        "grund": grund,
        "verlauf": (alt.get("verlauf") or []) + [eintrag],
    }
    os.makedirs(os.path.dirname(SCHALTER_DATEI), exist_ok=True)
    with open(SCHALTER_DATEI, "w", encoding="utf-8") as f:
        json.dump(neu, f, ensure_ascii=False, indent=1)
    neu_lesen()
    return neu


def _regler():
    if time.monotonic() - _merk["zeit"] > NEU_LESEN:
        try:
            with open(DATEI, encoding="utf-8") as f:
                _merk["regler"] = json.load(f)["regler"] if handeln_lesen()["an"] else None
        except (OSError, ValueError, KeyError):
            _merk["regler"] = None
        _merk["zeit"] = time.monotonic()
    return _merk["regler"]


def _gewichte(messgroesse, typ):
    """Gewichte der aktiven Regler dieser Messgroesse fuer diese Art; None ohne Datei."""
    r = _regler()
    if not r:
        return None
    return [
        x["gewicht"]
        for x in r
        if not x.get("archiviert")
        and x.get("messgroesse") == messgroesse
        and (x.get("arten", "alle") == "alle" or typ in x["arten"])
    ]


def staerke(messgroesse, typ=None):
    """Betrag der Summe der aktiven Gewichte dieser Messgroesse fuer diese Art; 1.0 ohne Datei oder bei Schalter aus, 0.0 wenn kein Regler
    gilt (archiviert)."""
    ws = _gewichte(messgroesse, typ)
    if ws is None:
        return 1.0
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


def dazu_vorzug(typ=None):
    """Mehrwert eines schon angegriffenen Ziels (0.0 = wie vorher: erst ein freies, nur ohne freies dazu). Gemeinsam gewirkt staerker ->
    lieber zu einem Ziel, an dem schon einer kaempft."""
    return max(0.0, VORZUG_JE * (staerke("gemeinsam", typ) - 1.0))


def chance_radius(typ=None):
    """Felder, bis zu denen eine sonst wartende Einheit einen Arbeiter als Ziel nimmt (0.0 = wie vorher: nur direkt am Weg).
    Chance verpasst staerker -> weiter schauen."""
    return max(0.0, CHANCE_JE * (staerke("chance_verpasst", typ) - 1.0))


def zielwert(art, typ=None):
    """Faktor auf den Wert einer Zielart (ZIELWERT): Mittel der Summen ihrer Lohn-Gewichte, nie unter 0; 1.0 ohne Datei und wenn keine
    ihrer Messgroessen einen aktiven Regler hat (dann hat der Nutzer zu dieser Zielart nichts eingestellt)."""
    summen = []
    for m in ZIELWERT[art]:
        ws = _gewichte(m, typ)
        if ws:
            summen.append(sum(ws))
    if not summen:
        return 1.0
    return max(0.0, sum(summen) / len(summen))
