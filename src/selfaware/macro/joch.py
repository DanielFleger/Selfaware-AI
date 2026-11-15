# -*- coding: utf-8 -*-
"""Wo ein Ochsenjoch hingehoert - die eine Stelle fuer alle Bauwege (S168).

Daniel 15.11.2026 01:55 (Bild): "Ochsenjoche nicht direkt neben der Steinablagestelle, dabei waere genug Platz"; 11:29 (Bild,
Joche klebten links am Bruch, 9 Felder vom Haufen): "die Ochsenjoche sollten dort, wo die Steinablage ist, und im besten Fall mit
einem Abstand, weil sonst koennte es sein, dass sie den Stein nicht als solchen erkennen". Also: am Steinhaufen des Bruchs, mit einem
freien Feld dazwischen.

Gemessen 15.11.2026 11:36 (letzte 60 Lageprotokolle, 240 Steinbrueche beider Spieler, je 40-63 in jedem der vier Kartenviertel
zwischen den Diagonalen x=y und x+y=400): der Steinhaufen (Typ 21, Feld "verbund" des Bruchs) liegt in Feldern IMMER bei Bruch + (7, 2).
Abgeleitet, nicht gemessen: gebaut wird mit Drehwert 15 wie per Mausklick, placeBuilding setzt dabei die Drehung 0 - darum dreht das
Kartenviertel die Lage in Feldern nicht (Daniel 11:33: das Bild dreht sich je nach Viertel)."""

HAUFEN_VERSATZ = (7, 2)
HAUFEN_B = 3   # Flaeche des Steinhaufens in Feldern: "~3x3" (erstes_spiel.GROESSE_IST) - nicht genau gemessen
ABSTAND = 1    # freie Felder zwischen Haufen und Joch (Daniel: "mit einem Abstand"), das kleinste Mass, das "nicht beruehren" heisst
JOCH_B = 2     # Ochsenjoch 2x2 (NACH_TYP[4]["b"])


def haufen(bruch):
    """Ecke des Steinhaufens zum Steinbruch an der Ecke bruch (x, y)."""
    return (bruch[0] + HAUFEN_VERSATZ[0], bruch[1] + HAUFEN_VERSATZ[1])


def mitte(h):
    """Mitte des Haufens mit der Ecke h - dort sucht der Bau den naechsten freien Platz."""
    return (h[0] + HAUFEN_B // 2, h[1] + HAUFEN_B // 2)


def sperre(h):
    """[(Ecke, Seitenlaenge)]: der Haufen und ABSTAND Felder rundum - dort darf kein Joch stehen."""
    return [((h[0] - ABSTAND, h[1] - ABSTAND), HAUFEN_B + 2 * ABSTAND)]


def frei(ort, sperren, b=JOCH_B):
    """Ueberdeckt ein Bau der Seitenlaenge b an der Ecke ort keine der Sperrflaechen?"""
    return all(ort[0] + b <= o[0] or o[0] + b2 <= ort[0] or ort[1] + b <= o[1] or o[1] + b2 <= ort[1] for o, b2 in sperren)
