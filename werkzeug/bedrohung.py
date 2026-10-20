# -*- coding: utf-8 -*-
"""Wie viele Assassinen braucht der Lord-Angriff in DIESER Lage? (Daniel 06.10., Uebergabe von Codex)

Grundsatz (Daniel): Jede Einheit, Person, jedes Gebaeude und das Gelaende kann Einfluss haben; entscheidend ist, was
im konkreten Spiel wirklich ablenkt oder schadet. Keine allgemeine Formel aus Lord-Leben oder Fern/Nah-Zahl, keine
unbelegte Zahl fuer unbekannte Lagen. Zeit ist kritisch: so frueh wie sicher moeglich angreifen.

Darum keine Rechnung, sondern ein Vergleich mit GEMESSENEN Lagen (daten/lagen_belegt.json):
  Fingerabdruck einer Lage = Leben und Ort ihres Lords, alle feindlichen Einheiten nach Typ in zwei Ringen um den Lord
  (bis 15 und bis 45 Felder), ihre Gebaeude nach Typ bis 15 Felder.
  Eine gemessene Lage DECKT die aktuelle, wenn die aktuelle in keinem Wert gefaehrlicher ist (Lord nicht staerker, Lord
  am selben Ort, in jedem Ring und Typ nicht mehr Einheiten, nicht mehr Gebaeude). Dann gilt deren belegte Mindestzahl.
  Deckt keine: VORLAEUFIG der vorsichtige Ersatzwert - sichtbar so gekennzeichnet.

Annahmen, die (noch) nicht gemessen sind, stehen offen hier:
  - weniger Verteidiger machen den Angriff nicht schwerer (Monotonie);
  - Einheiten weiter als 45 Felder vom Lord: in der einzigen gemessenen Lage war keine beteiligt (alle Beteiligten
    starteten hoechstens 14 Felder vom Lord). Sie werden mitgeschrieben, aber nicht verglichen.
"""
from parteien import freunde_von   # B-133: Freund/Feind aus den Mannschaften des Spiels (2v2)
import json
import os

HIER = os.path.dirname(os.path.abspath(__file__))
LAGEN = os.path.join(HIER, "..", "daten", "lagen_belegt.json")
RINGE = (15, 45)
GEBAEUDE_RING = 15
LORD_ORT_TOLERANZ = 3
LORD = 55
# Vorlaeufiger Ersatzwert fuer Lagen, die keine Messung deckt: die Angriffsgroesse, die bisher ueberall gewonnen hat
# (Trainingsstand 40: 3/3; ganze Partien gemeinsam_1 mit 47-60: 3/3). Kein Beleg fuer die neue Lage - nur vorsichtig.
VORLAEUFIG = 40
# Nicht verglichen, nur mitgeschrieben (Daniel 06.10. 19:33: "ja"): Bauern (Typ 1). Bei ihrem Lord standen beim Angriff
# mal 1, mal 27, mal 40 Bauern am Feuer - allein deshalb deckte nie eine gemessene Lage (bedarf_partie_3, holz_partie_2);
# in den gemessenen Treffern (zielfeld_1) schlug nie ein Bauer zu.
NICHT_VERGLICHEN = {1}


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def feindlord(L, sp=1):
    return next(((n, e) for n, e in sorted(L.items()) if e["typ"] == LORD and e["besitzer"] not in freunde_von(sp)), None)


def fingerabdruck(L, G, sp=1):
    """Die Lage um ihren Lord als vergleichbare Zahlen. None, wenn kein feindlicher Lord lebt."""
    fl = feindlord(L, sp)
    if fl is None:
        return None
    ln, le = fl
    lp = (le["x"], le["y"])
    einheiten, fern, gebaeude = {}, {}, {}
    for n, e in L.items():
        if n == ln or e["besitzer"] in freunde_von(sp):
            continue
        d = schach((e["x"], e["y"]), lp)
        ring = next((r for r in RINGE if d <= r), None)
        ziel = einheiten if ring else fern
        k = "%s:%d" % (ring or "fern", e["typ"])
        ziel[k] = ziel.get(k, 0) + 1
    for g in (G or {}).values():
        if g["besitzer"] in freunde_von(sp) or schach((g["x"], g["y"]), lp) > GEBAEUDE_RING:
            continue
        k = "%d:%d" % (GEBAEUDE_RING, g["typ"])
        gebaeude[k] = gebaeude.get(k, 0) + 1
    return {"lord_leben": le["leben"], "lord_ort": list(lp), "einheiten": einheiten, "gebaeude": gebaeude, "fern": fern}


def deckt(gemessen, aktuell):
    """None, wenn die gemessene Lage die aktuelle deckt; sonst der erste Grund, warum nicht (fuer das Protokoll)."""
    if aktuell["lord_leben"] > gemessen["lord_leben"]:
        return "Lord staerker (%d > %d)" % (aktuell["lord_leben"], gemessen["lord_leben"])
    if schach(aktuell["lord_ort"], gemessen["lord_ort"]) > LORD_ORT_TOLERANZ:
        return "Lord an anderem Ort %s statt %s" % (tuple(aktuell["lord_ort"]), tuple(gemessen["lord_ort"]))
    for art in ("einheiten", "gebaeude"):
        for k, v in sorted(aktuell[art].items()):
            if art == "einheiten" and int(k.split(":")[1]) in NICHT_VERGLICHEN:
                continue
            if v > gemessen[art].get(k, 0):
                return "%s %s: %d statt hoechstens %d" % (art, k, v, gemessen[art].get(k, 0))
    return None


def lagen_laden(pfad=LAGEN):
    return json.load(open(pfad, encoding="utf-8")) if os.path.exists(pfad) else []


def bedarf(fa, lagen):
    """(Zahl, 'belegt'|'vorlaeufig', Begruendung, Gruppenleben). Unter mehreren deckenden Lagen gilt die kleinste
    belegte Zahl. Gruppenleben = Startleben der gemessenen Gruppe (sie war die gesuendeste); angeschlagene Assassinen
    zaehlen damit nicht wie volle. Vorlaeufig: kein Gruppenleben (None)."""
    if fa is None:
        return None, "kein Lord", "", None
    deckende, gruende = [], []
    for lage in lagen:
        grund = deckt(lage["fingerabdruck"], fa)
        if grund is None:
            deckende.append(lage)
        else:
            gruende.append("%s: %s" % (lage["name"], grund))
    if deckende:
        beste = min(deckende, key=lambda l: l["mindest"])
        return beste["mindest"], "belegt", "gedeckt durch %s (%s)" % (beste["name"], beste["beleg"]), beste.get("gruppe_leben")
    return VORLAEUFIG, "vorlaeufig", "keine gemessene Lage deckt diese: " + ("; ".join(gruende) or "noch keine Lage gemessen"), None
