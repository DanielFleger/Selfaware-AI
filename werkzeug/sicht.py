# -*- coding: utf-8 -*-
"""Was der Gegner von einer Assassine sieht und was ihr droht (SAI 17.10., Plan_Entdeckung.md; Daniel 09:41: "beachten der
'Assassine beobachtet'-Trigger, verstecken hinter Gebaeuden, welche Einheiten wann getriggert werden").

Ersetzt den Schadenssatz nach Abstand (L73) durch die Regeln des Spiels:
  SICHTBAR (L75): ein waehlbarer Feind (Soldat, Lord, Sklave, Moench, Belagerung - KEIN Arbeiter) hoechstens 160 Feinmass
    entfernt (Naeherung des Spiels, 8 je Feld, ~20 Felder). Nur dann waehlen feindliche Schuetzen sie als Ziel.
  BESCHUSS (L78/L79, gemessen 17.10. angriff_raten_messen.py): je Schuetze in Reichweite (Kreis) 1,352 Leben je Takt bei
    freier Linie, 0,070 bei versperrter. Versperrt = ein nicht flaches Gebaeude auf der Linie (nicht das, auf dem der
    Schuetze steht); wer auf Turm/Torhaus/Bergfried steht, schiesst immer frei.
    Reichweite Bogen 40: einzelner Bogenschuetze mit freier Linie traf bis 39 Felder, 40-79 Felder 0 von 78 Runden (17.10.);
    die Spieltabelle sagt 54 (L78) - gemessen schlaegt abgelesen. Armbrust 40, Schleuder 18, Feuerwerfer 11 (live 17.10.).
  VERFOLGT (L77): Nahkaempfer laufen jeder Feind-Einheit nach, auch einer verdeckten Assassine, aber nur nach Haltung ihres
    Trupps: Verteidigung 40 Feinmass (5 Felder), Angriff 200 (25 Felder), Stehen und ohne Trupp gar nicht.
Was hier NICHT drin ist (Plan, Frage-Agent 17.10.): Pruefungs-Phase der Assassine (Start nach der Pruefung) - erst messen,
wie schnell ein Befehl im Spiel ankommt; Gebaeudehoehen (jedes nicht flache Gebaeude sperrt).
Gegenprobe: werkzeug/sicht_pruefen.py."""
import json
import os

HIER = os.path.dirname(os.path.abspath(__file__))

WAEHLBAR = {5, 22, 23, 24, 25, 26, 27, 28, 29, 30, 37, 39, 40, 41, 55, 58, 59, 60, 61,
            70, 71, 72, 73, 74, 75, 76, 77}
REICHWEITE = {22: 40, 23: 40, 70: 40, 74: 40, 72: 18, 76: 11}
NAHKAMPF = {24, 25, 26, 27, 28, 37, 55, 71, 73, 75}
TIERE = {44, 45, 46, 47, 48, 49, 51, 52, 62, 67, 68, 69}
SICHT = 160                      # Feinmass (acquireShootTarget 0x0054B0D0)
RATE_FREI, RATE_ZU = 1.352, 0.070
HALTUNG_RADIUS = {0: 0, 1: 5, 2: 25}     # Felder (stanceBasedRange 0x28 / 200 Feinmass)
FLACH = {10, 30, 31, 32, 33}             # Lagerplatz, Felder (vermutet flach)
ERHOEHT = {41, 45, 46, 74, 75, 76, 77, 78}
_GJ = os.path.join(HIER, "..", "..", "VillageStudio", "lib", "gebaeude.json")
GROESSE = {int(v["laufzeit"]): int(v["b"]) for v in json.load(open(_GJ, encoding="utf-8"))["gebaeude"].values()
           if isinstance(v, dict) and v.get("laufzeit")}


def abstand_fein(a, b):
    """Naeherung des Spiels (findNearestEnemyAndHeadTowardsIt) in Feinmass; a, b in Feldern."""
    dx, dy = abs(a[0] - b[0]) * 8, abs(a[1] - b[1]) * 8
    if dx < dy:
        return ((dx * 2) // 5) * dx // dy + dy
    if dx == 0:
        return 0
    return ((dy * 2) // 5) * dy // dx + dx


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def linie(a, b):
    """Felder zwischen a und b (ohne Endpunkte), Bresenham."""
    x0, y0 = int(a[0]), int(a[1])
    x1, y1 = int(b[0]), int(b[1])
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err, aus = dx + dy, []
    while (x0, y0) != (x1, y1):
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x0 += sx
        if e2 <= dx:
            err += dx; y0 += sy
        if (x0, y0) != (x1, y1):
            aus.append((x0, y0))
    return aus


class Lage:
    """Eine Runde: L (Einheiten), G (Gebaeude), sp (wir), haltung {Gruppe: 0/1/2} oder None (unbekannt -> Verteidigung)."""

    def __init__(self, L, G, sp=1, haltung=None):
        self.sp = sp
        feinde = [e for e in L.values() if e["besitzer"] not in (0, sp) and e["typ"] not in TIERE]
        self.waehl = [(e["x"], e["y"]) for e in feinde if e["typ"] in WAEHLBAR]
        self.gebaeude = {}                   # Feld -> (Nr, Typ) aller Gebaeude mit bekannter Grundflaeche
        for nr, g in (G or {}).items():
            b = GROESSE.get(g["typ"])
            for x in range(g["x"], g["x"] + (b or 0)):
                for y in range(g["y"], g["y"] + (b or 0)):
                    self.gebaeude[(x, y)] = (nr, g["typ"])
        self.schuetzen = []                  # (Ort, Reichweite, erhoeht, Nr des Gebaeudes unter ihm)
        for e in feinde:
            r = REICHWEITE.get(e["typ"])
            if r:
                ort = (e["x"], e["y"])
                steht = self.gebaeude.get(ort)
                self.schuetzen.append((ort, r, bool(steht and steht[1] in ERHOEHT), steht[0] if steht else None))
        self.verfolger = []                  # (Ort, Typ, Radius in Feldern)
        for e in feinde:
            if e["typ"] not in NAHKAMPF:
                continue
            g = e.get("gruppe") or 0
            if not g:
                continue                     # ohne Trupp keine Haltung -> verfolgt nicht (tribeID 0)
            h = (haltung or {}).get(g, 1)
            if HALTUNG_RADIUS.get(h, 5):
                self.verfolger.append(((e["x"], e["y"]), e["typ"], HALTUNG_RADIUS.get(h, 5)))

    # --- Punktabfragen ---------------------------------------------------------------------------------------------
    def sicht_abstand(self, feld):
        return min((abstand_fein(feld, w) for w in self.waehl), default=99999)

    def sichtbar(self, feld, rand=0):
        return any(abstand_fein(feld, w) <= SICHT + rand for w in self.waehl if schach(feld, w) <= 21 + rand // 8)

    def linie_frei(self, s, steht, ziel):
        for q in linie(s, ziel):
            b = self.gebaeude.get(q)
            if b and b[1] not in FLACH and b[0] != steht:
                return False
        return True

    def beschuss(self, feld, rand=0):
        """Erwarteter Lebensverlust je Takt am Feld (0, wenn nicht sichtbar)."""
        if not self.sichtbar(feld, rand):
            return 0.0
        s = 0.0
        for ort, r, erh, steht in self.schuetzen:
            if (ort[0] - feld[0]) ** 2 + (ort[1] - feld[1]) ** 2 <= r * r:
                s += RATE_FREI if erh or self.linie_frei(ort, steht, feld) else RATE_ZU
        return s

    def verfolgt(self, feld):
        """Nahkaempfer, deren Haltungs-Radius das Feld deckt: [(Ort, Typ)]."""
        return [(o, t) for o, t, r in self.verfolger if schach(o, feld) <= r]

    def sicher(self, feld):
        """Hier trifft ihn gerade nichts: kein Beschuss (unsichtbar ODER kein Schuetze mit Linie) und kein Verfolger.
        17.10.: zuerst "unsichtbar" verlangt - dann wartete jede Assassine 20 Felder neben dem feindlichen Lord weg, obwohl
        dort kein Schuetze stand (lordanlauf_pruefen Fall 2). Gesehen werden allein schadet nicht."""
        return self.beschuss(feld, 16) <= 0 and not self.verfolgt(feld)

    # --- Zellen fuer schussfeld.Gitter -----------------------------------------------------------------------------
    def zellsatz(self, zelle, n):
        """Beschuss je Takt je Zelle (Zellmitte, Rand 16 Feinmass fuer die Lage in der Zelle)."""
        satz = [[0.0] * n for _ in range(n)]
        mitte = lambda c: (c[0] * zelle + zelle // 2, c[1] * zelle + zelle // 2)
        rand = 16 + zelle * 4
        sicht = set()
        rz = (21 + rand // 8) // zelle + 1
        for w in self.waehl:
            cx, cy = w[0] // zelle, w[1] // zelle
            for y in range(max(0, cy - rz), min(n, cy + rz + 1)):
                for x in range(max(0, cx - rz), min(n, cx + rz + 1)):
                    if (x, y) not in sicht and abstand_fein(mitte((x, y)), w) <= SICHT + rand:
                        sicht.add((x, y))
        for ort, r, erh, steht in self.schuetzen:
            cx, cy = ort[0] // zelle, ort[1] // zelle
            rc = r // zelle + 1
            for y in range(max(0, cy - rc), min(n, cy + rc + 1)):
                for x in range(max(0, cx - rc), min(n, cx + rc + 1)):
                    if (x, y) not in sicht:
                        continue
                    m = mitte((x, y))
                    if (m[0] - ort[0]) ** 2 + (m[1] - ort[1]) ** 2 > r * r:
                        continue
                    satz[y][x] += RATE_FREI if erh or self.linie_frei(ort, steht, m) else RATE_ZU
        return satz
