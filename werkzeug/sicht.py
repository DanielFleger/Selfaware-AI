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
import math
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
# Zielwahl der Schuetzen (acquireShootTarget 0x0054B0D0, L78): jeder Schuetze schiesst auf EIN Ziel, das mit dem kleinsten
# Wert; ein noch von niemandem beschossenes Ziel nimmt er, wenn sein Wert unter dem 1,5-fachen des besten liegt (Feuer
# verteilt sich). Wert = Schach-Abstand in Feinmass + 50 je Schuetze, der schon darauf zielt, dann je Zielart (prio).
SCHUETZE_ART = {22: "bogen", 70: "bogen", 74: "bogen", 23: "armbrust", 72: "schleuder", 76: "feuer"}
BAENDER = {"bogen": (10, 20, 30, 41), "armbrust": (10, 20, 30, 41), "schleuder": (10, 19), "feuer": (12,)}
_SR = os.path.join(HIER, "..", "daten", "schussrate.json")
try:                                     # Schaden je ZUGETEILTEM Schuetzen und Takt (schussrate_messen.py), sonst Mittelwert
    _d = json.load(open(_SR, encoding="utf-8"))
    RATE = {(k.split(":")[0], int(k.split(":")[1])): v for k, v in zip(_d["spalten"], _d["rate"])}
    RATE_QUELLE = "gemessen je Art und Abstand (%s)" % os.path.basename(_SR)
except (OSError, ValueError, KeyError):
    RATE, RATE_QUELLE = {}, "Mittelwert 1,352 (schussrate.json fehlt)"


def band(art, d):
    for i, grenze in enumerate(BAENDER.get(art, ())):
        if d < grenze:
            return i
    return None


def dps(art, d):
    b = band(art, d)
    return 0.0 if b is None else RATE.get((art, b), RATE_FREI)


def prio(typ, d):
    """Zielwert eines Schuetzen fuer ein Ziel der Art typ im Abstand d (Feinmass, schon mit +50 je anderem Schuetzen)."""
    if typ in (22, 23, 70, 74):
        return d + 75
    if typ in (24, 25, 26, 27, 28, 71, 72, 73, 75):
        return d * 5 + 200
    if typ == 29:
        return d * 7 + 300
    if typ in (30, 39, 40, 55):
        return d * 2 + 100
    if typ in (41, 61, 76, 77):
        return d
    return (d * 5 + 200) * 2


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
        self.schuetzen = []                  # (Ort, Reichweite, erhoeht, Nr des Gebaeudes unter ihm, Art)
        for e in sorted(feinde, key=lambda x: x.get("nr", 0)):
            r = REICHWEITE.get(e["typ"])
            if r:
                ort = (e["x"], e["y"])
                steht = self.gebaeude.get(ort)
                self.schuetzen.append((ort, r, bool(steht and steht[1] in ERHOEHT), steht[0] if steht else None,
                                       SCHUETZE_ART[e["typ"]]))
        self.eigene = [(e.get("nr", 0), (e["x"], e["y"]), e["typ"]) for e in L.values()
                       if e["besitzer"] == sp and e["typ"] not in TIERE]
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
        self.zuteilen()

    def zuteilen(self):
        """Wer schiesst gerade auf wen (Nachbau der Zielwahl, siehe oben). self.feuer: eigene Nr -> [(Art, Abstand)];
        self.bestwert[i]: (bester Wert, bester Wert unter den Unbeschossenen) des Schuetzen i - fuer die Frage, was waere,
        wenn eine weitere Assassine an einem Ort auftaucht (beschuss)."""
        self.feuer, self.bestwert, zahl = {}, [], {}
        sichtbar = {nr: self.sichtbar(p) for nr, p, t in self.eigene if t == 73}
        for ort, r, erh, steht, art in self.schuetzen:
            kand = []
            for nr, p, typ in self.eigene:
                if schach(ort, p) > r or (p[0] - ort[0]) ** 2 + (p[1] - ort[1]) ** 2 > r * r:
                    continue
                if typ == 73 and not sichtbar.get(nr):
                    continue
                if not (erh or self.linie_frei(ort, steht, p)):
                    continue
                kand.append((prio(typ, schach(ort, p) * 8 + 50 * zahl.get(nr, 0)), nr, zahl.get(nr, 0) == 0, p))
            if not kand:
                self.bestwert.append((float("inf"), float("inf")))
                continue
            best = min(kand)
            frei = min((k for k in kand if k[2]), default=None)
            wahl = frei if frei is not None and frei[0] < best[0] * 1.5 else best
            zahl[wahl[1]] = zahl.get(wahl[1], 0) + 1
            self.feuer.setdefault(wahl[1], []).append((art, math.hypot(wahl[3][0] - ort[0], wahl[3][1] - ort[1])))
            self.bestwert.append((best[0], frei[0] if frei is not None else float("inf")))

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

    def beschuss(self, feld, rand=0, nr=None):
        """Erwarteter Lebensverlust je Takt. nr = eigene Einheit an ihrem Ort: die Schuetzen, die ihr zugeteilt sind.
        Sonst: eine (weitere) Assassine an feld - jeder Schuetze in Reichweite mit freier Linie nimmt sie, wenn er sonst
        kein Ziel hat oder sie ihm lieber ist (Wert < 1,5 x bester und < bester Unbeschossener). 0, wenn nicht sichtbar."""
        da = [n for n, p, t in self.eigene if p == tuple(feld) and (n == nr or (nr is None and t == 73))]
        if da:                           # dort steht schon eine eigene Einheit: was ihr zugeteilt ist
            return sum(dps(a, d) for n in da[:1] for a, d in self.feuer.get(n, ()))
        if not self.sichtbar(feld, rand):
            return 0.0
        s = 0.0
        for i, (ort, r, erh, steht, art) in enumerate(self.schuetzen):
            d2 = (ort[0] - feld[0]) ** 2 + (ort[1] - feld[1]) ** 2
            if d2 > r * r or not (erh or self.linie_frei(ort, steht, feld)):
                continue
            best, frei = self.bestwert[i]
            w = prio(73, schach(ort, feld) * 8)
            if best == float("inf") or (w < best * 1.5 and w < frei):
                s += dps(art, math.sqrt(d2))
        return s

    def feuer_gesamt(self, feld):
        """Alle Schuetzen, die feld erreichen koennen (Linie frei), zusammen - fuer viele Assassinen an einem Ort (Lord)."""
        s = 0.0
        for ort, r, erh, steht, art in self.schuetzen:
            d2 = (ort[0] - feld[0]) ** 2 + (ort[1] - feld[1]) ** 2
            if d2 <= r * r and (erh or self.linie_frei(ort, steht, feld)):
                s += dps(art, math.sqrt(d2))
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
        for i, (ort, r, erh, steht, art) in enumerate(self.schuetzen):
            best, frei = self.bestwert[i]
            cx, cy = ort[0] // zelle, ort[1] // zelle
            rc = r // zelle + 1
            for y in range(max(0, cy - rc), min(n, cy + rc + 1)):
                for x in range(max(0, cx - rc), min(n, cx + rc + 1)):
                    if (x, y) not in sicht:
                        continue
                    m = mitte((x, y))
                    d2 = (m[0] - ort[0]) ** 2 + (m[1] - ort[1]) ** 2
                    if d2 > r * r:
                        continue
                    w = prio(73, max(0, schach(ort, m) - zelle // 2) * 8)
                    if best != float("inf") and not (w < best * 1.5 and w < frei):
                        continue
                    if erh or self.linie_frei(ort, steht, m):
                        satz[y][x] += dps(art, math.sqrt(d2))
        return satz
