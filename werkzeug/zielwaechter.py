# -*- coding: utf-8 -*-
"""Vorsichtiger Fruehabbruch fuer das Ziel 25 Streitkolbenkaempfer.

Die Rechnung darf einen rettbaren Lauf nie verwerfen. Deshalb bekommt die
Zukunft doppelt so viel Goldzuwachs wie der beste gemessene 1.000- bis
2.500-Tick-Abschnitt aus 118 vorhandenen Lernlaeufen: gemessen 1.195,
aufgerundet 2.400 Gold je 1.000 Ticks. Die laufende Bilanz zaehlt Kasse,
verkaufbare Lagerware, sichere Abrissrueckgabe und bereits kommendes Leder.
"""

import math


GOLD_OBERGRENZE_1000 = 2400
ZIELLINIEN = (
    (12799, "sehr sehr gut"),   # Daniel 08.10.: unter 16 Monaten
    (14400, "sehr gut"),        # hoechstens 18 Monate
    (19200, "harte Grenze"),    # hoechstens 24 Monate
)


def pruefe(tick, habe_gold, bedarf_gold, rate_1000=GOLD_OBERGRENZE_1000, ziellinien=ZIELLINIEN):
    """Erreichbarkeit der Ziellinien mit absichtlich grosszuegiger Goldobergrenze."""
    aus = []
    for ende, name in ziellinien:
        rest_ticks = max(0, ende - tick)
        zukunft = int(math.ceil(rest_ticks * rate_1000 / 1000.0))
        maximal = habe_gold + zukunft
        aus.append({
            "name": name,
            "tick": ende,
            "rest_ticks": rest_ticks,
            "habe_gold": habe_gold,
            "bedarf_gold": bedarf_gold,
            "zukunft_gold": zukunft,
            "maximal_gold": maximal,
            "erreichbar": tick <= ende and maximal >= bedarf_gold,
            "fehlt_gold": max(0, bedarf_gold - maximal),
        })
    return aus


def neue_verfehlungen(pruefung, schon=()):
    """Nur neu unmoeglich gewordene Ziellinien melden; die harte separat erkennen."""
    schon = set(schon)
    neu = [z for z in pruefung if not z["erreichbar"] and z["name"] not in schon]
    hart = next((z for z in pruefung if z["name"] == "harte Grenze"), None)
    return neu, bool(hart and not hart["erreichbar"])
