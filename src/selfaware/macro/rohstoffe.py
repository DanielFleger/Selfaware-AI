# -*- coding: utf-8 -*-
"""Alle Stein- und Eisenvorkommen der Karte nutzen - die Stelle mit dem kuerzesten Laufweg in Zeit zuerst, ohne Obergrenze (S170).

Daniel 15.11.2026 11:29 (Bild): "es wird immer noch nicht die Wirtschaft priorisiert, es geht hier darum, dass alle sichtbaren
Ressourcen auf dem Feld genutzt werden, also alle Steinbrueche und Eisenminen"; 11:44 auf die Frage, welche Vorkommen: "immer erst
die, wo der Laufweg am wenigsten Zeit braucht (bewusst nicht gesagt die kuerzesten), dann die weiter weg bis zur ganzen Karte. Ich
wuerde bewusst keine Anzahl einbauen, weil es manche Maps mit weniger, manche mit mehr Ressourcen gibt".

Stellen: das Spiel selbst sagt, wo ein Steinbruch / eine Eisenmine stehen kann (Modulbefehl platzkarte = checkBuildingCanBePlacedHere
fuer jede Stelle; ganze Karte unter 1 s, Wissensstand 13l) - kein Raten, ob ein kleines Vorkommen reicht (Paradise Plains:
neben 62 Stein- und 45 Eisenvorkommen ab 4 Feldern 462 und 544 Grueppchen mit 1-3 Feldern).
Laufzeit: Felder auf dem Laufweg ueber die Weg-Ebene des Spiels (um Wasser, Felsen und Gebaeude herum, nicht Luftlinie) vom naechsten
eigenen Lagerfeld bis neben den Bau, mal TAKTE_JE_FELD. Gemessen (Wissensregister G1): Arbeiter laufen 24 Takte je Feld, gerade wie
schraeg gleich schnell - darum zaehlt ein Schraegschritt wie ein gerader."""
from collections import deque

from selfaware.services import schussfeld as SF

GROESSE = {20: 6, 5: 4}                # Seitenlaenge des Baus (NACH_TYP)
TAKTE_JE_FELD = 24                     # Wissensregister G1 (getestet 06.10.2026)


def lagerfelder(G, sp):
    """Felder der eigenen Lagerplaetze (Typ 10, 3x3 je Teil) - dort kommt Stein und Eisen an."""
    return [(g["x"] + dx, g["y"] + dy) for g in G.values() if g.get("besitzer") == sp and g.get("typ") == 10
            for dx in range(3) for dy in range(3)]


def _ring(ecke, b):
    """Felder rund um den Grundriss (Ecke oben links, Seitenlaenge b) - dort steht der Arbeiter, der ein- und auslaedt."""
    x0, y0 = ecke
    return [(x, y) for x in range(x0 - 1, x0 + b + 1) for y in range(y0 - 1, y0 + b + 1)
            if not (x0 <= x < x0 + b and y0 <= y < y0 + b)]


def abstaende(gelaende, quellen):
    """Schritte vom naechsten Quellfeld zu jedem erreichbaren Feld der Gelaendekarte, wie die Wegfuehrung sie haelt
    (services/wegkarte.als_gelaende: Zeile y, Spalte x, "." = das Spiel erlaubt dort einen Schritt; vor dem ersten Lesen die
    Startkarte mit "G"/"s"/"." - begehbar ist, was in schussfeld.BEGEHBAR steht). Schraeg zaehlt 1 (G1).
    S170-Fix (Partie 34, 15.11.2026 12:35: TypeError - die Wegfuehrung haelt die Zeichenkarte, nicht die Feldtabelle)."""
    def frei(p):
        return 0 <= p[1] < len(gelaende) and 0 <= p[0] < len(gelaende[p[1]]) and gelaende[p[1]][p[0]] in SF.BEGEHBAR
    q = deque(p for p in quellen if frei(p))
    d = {p: 0 for p in q}
    while q:
        p = q.popleft()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                n = (p[0] + dx, p[1] + dy)
                if (dx or dy) and n not in d and frei(n):
                    d[n] = d[p] + 1
                    q.append(n)
    return d


def _ueberdeckt(a, ba, b, bb):
    return a[0] < b[0] + bb and b[0] < a[0] + ba and a[1] < b[1] + bb and b[1] < a[1] + ba


class Rohstoffpflicht:
    """Reihenfolge aller Bauplaetze fuer Steinbruch (20) und Eisenmine (5) nach Laufzeit zum Lager. plaetze = {Art: Ecken}, wie die
    platzkarte des Spiels sie liefert. Ist alles verbaut oder weg, holt der Lenker eine frische platzkarte."""

    def __init__(self, plaetze):
        self.plaetze = {art: set(p) for art, p in plaetze.items()}
        self.liste = []                     # [(Takte, Art, Ecke)] nach Laufzeit
        self.unerreichbar = 0
        self._schluessel = None
        self._d = None

    def ordnen(self, karte, lager):
        """Laufzeiten neu, wenn sich Wegkarte, Lager oder Plaetze geaendert haben. karte = Gelaendekarte der Wegfuehrung
        (Liste von Zeilen, "." begehbar)."""
        schluessel = (id(karte), tuple(sorted(lager)), sum(len(p) for p in self.plaetze.values()))
        if schluessel == self._schluessel or not lager:
            return False
        if self._schluessel is None or self._schluessel[:2] != schluessel[:2]:
            self._d = abstaende(karte, lager)
        self._schluessel = schluessel
        self.liste, self.unerreichbar = [], 0
        for art, ecken in self.plaetze.items():
            for e in ecken:
                schritte = [self._d[n] for n in _ring(e, GROESSE[art]) if n in self._d]
                if schritte:
                    self.liste.append((min(schritte) * TAKTE_JE_FELD, art, e))
                else:
                    self.unerreichbar += 1
        self.liste.sort()
        return True

    def offen(self):
        return list(self.liste)

    def weg(self, art, ecke):
        """Diese Stelle geht nicht mehr (Spiel lehnt ab)."""
        self.plaetze[art].discard(ecke)
        self.liste = [t for t in self.liste if not (t[1] == art and t[2] == ecke)]

    def gebaut(self, art, ecke):
        """Ein Bau steht an ecke: jede Stelle, die ihn ueberdecken wuerde, faellt weg - fuer beide Arten."""
        b = GROESSE[art]
        for a2, ecken in self.plaetze.items():
            for e in [e for e in ecken if _ueberdeckt(e, GROESSE[a2], ecke, b)]:
                ecken.discard(e)
        self.liste = [t for t in self.liste if t[2] in self.plaetze[t[1]]]
