# -*- coding: utf-8 -*-
"""Wer ist Freund, wer Feind (B-133, 20.10.2026 - Daniel: "2v2 gegen Rotkaeppchen und Rattenfaenger").

Bis hierhin galt im ganzen Lenker "jeder Besitzer ausser mir und 0 ist Feind" (47 Stellen in raids, feldzug, waechter,
assassinen, ...). Im 2v2 haetten sich die beiden SamurAIs gegenseitig angegriffen. Jetzt fragt jede dieser Stellen hier.

Die Mannschaften kommen aus dem Spiel: DAT_PlayerGroupArray @ 0x01A275B5, byte[9] - je Spieler seine Mannschaft
(logik.lua eigenesGefecht schreibt sie: "teams" fuer KI-Plaetze, "mensch_teams" fuer menschliche Plaetze).
0 heisst KEINE Mannschaft (jeder gegen jeden): gemessen 30.09. an Daniels Lobby-Aufbau, zwei KIs beide auf 0 spielten
gegeneinander; 0xFF heisst Platz nicht besetzt. Verbuendet sind darum nur Spieler mit gleicher Mannschaft 1..254.
Freunde = 0 (neutral), ich selbst und meine Verbuendeten. Gelesen wird einmal, sobald eine gueltige Mannschaft dasteht;
geht das Lesen schief, bleibt es beim alten Verhalten (nur 0 und ich)."""
GRUPPE = 0x01A275B5
_FEST = {}


def gruppen_aus_worten(worte):
    """3 Worte ab 0x01A275B4 (peek liefert 32 Bit, little endian) -> Mannschaft je Spieler 0..8."""
    b = b"".join((int(w) & 0xFFFFFFFF).to_bytes(4, "little") for w in worte)
    return list(b[1:10])


def freunde_aus_gruppen(sp, gruppen):
    meine = gruppen[sp] if 0 <= sp < len(gruppen) else 0
    if meine in (0, 0xFF):
        return frozenset((0, sp))
    return frozenset([0, sp] + [i for i in range(1, 9) if gruppen[i] == meine])


def freunde_von(sp):
    if sp in _FEST:
        return _FEST[sp]
    try:
        from laden import peek
        gruppen = gruppen_aus_worten(peek(GRUPPE - 1, 3))
    except Exception:
        return frozenset((0, sp))
    f = freunde_aus_gruppen(sp, gruppen)
    if gruppen[sp] != 0xFF:            # erst merken, wenn das Spiel die Mannschaft eingetragen hat
        _FEST[sp] = f
    return f


def setzen(sp, freunde):
    """Ohne Spiel (Pruefungen): Freunde fest vorgeben."""
    _FEST[sp] = frozenset(freunde) | {0, sp}
