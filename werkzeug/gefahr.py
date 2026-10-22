# -*- coding: utf-8 -*-
"""B-157 Angriff nach Daniels Regel "maximale Sicherheit, dann minimaler Widerstand" (21.10.2026 21:11: "du laeufst frontal mit
maximalem Beschuss ... was hast du vom Assassinen gelernt?"; 21:16: "immer diese Metrik updaten; manchmal macht es Sinn,
Einheiten zu besiegen, die auf dem Weg sind, z.B. Fernkaempfer - dann nur die minimale Anzahl, die zum Toeten reicht";
21:21 Bild: "immer noch maximale Einheiten dagegenwerfen und hoffen - das Gegenteil von minimalem Risiko").
Bausteine, ohne Spiel pruefbar (gefahr_pruefen.py):
  bedrohungen    - wer schiesst wohin: feindliche Fernkaempfer (Reichweite gefecht.FERN_REICH, Gewicht 1) und Todeszonen
                   (Burgteil Typ 75: Verlustkarte Pruefstand 21.10. - 58 von 275 eigenen Toten hoechstens 8 Felder daneben)
  Karte          - Gefahr je Feld fuer die ganze Karte, einmal je Runde gerechnet; gesperrte Felder (Feuer); je Startpunkt EINE
                   Kostensuche (skimage MCP), aus der die Wege zu beliebig vielen Zielen abgelesen werden
  gefahr         - Summe der Gewichte, die einen Punkt erreichen
  sicherer_weg   - kleinste Summe aus Weglaenge und K * Gefahr je Feld; Feuer ist gesperrt; danach geglaettet, aber nur so
                   weit, dass keine Abkuerzung gefaehrlicher ist als das Stueck, das sie ersetzt
  weg_gefahr     - Gefahr eines Weges (alle 2 Felder abgetastet) - damit werden Angriffsstellen verglichen
  schuetzen_am_weg / mindestzahl - Fernkaempfer, die den Weg bestreichen, und wie viele Nahkaempfer sie sicher toeten
21.10. 21:50 neu geschrieben (Pruefstand 21:34: Runden bis 4.472 Takte, Zeit "ruestung" bis 11 s - gemessen am Lagebild Tick
59.105: 9 Angriffsstellen x eigener A*-Suche mit 46 Bedrohungen je Feld = 4,8 s): Gefahr einmal je Runde als Feld, eine Suche
je Startpunkt statt je Ziel.
UNGEMESSEN (Startwerte, Daniel bekommt sie so gesagt): TODESZONE-Radius 8 und Gewicht 10, K = 6, Nahkampf-Schaden je Takt.
"""
import math

import numpy as np

TODESZONE = {75: (8, 10)}       # Burgteil-Typ -> (Radius, Gewicht); Typ 75 aus der Verlustkarte 21.10. - UNGEMESSEN
K = 6                           # Gewicht der Gefahr gegenueber 1 Feld Weg - UNGEMESSEN
NAHKAMPF_SCHADEN = 200          # Leben je Nahkaempfer und Takt gegen einen Schuetze - UNGEMESSEN (Assassinen-Raten L-Register)
SICHERHEIT = 1.5                # so viel mehr als rechnerisch noetig wird geschickt
GROESSE = 400                   # Kartenfelder je Seite (groesste Koordinate im Lagebild 21.10.: 388)
ZIEL_UMKREIS = 8                # ist das Ziel nicht begehbar (Gebaeude, Mauer, anderes Gebiet), gilt das naechste erreichbare
                                # Feld bis so weit daneben (Torhaus-Mitte bis vor das Tor: 4-5 Felder)


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def bedrohungen(L, G, ist_feind, fern_reich):
    """[(x, y, r, w, art)] - art "schuetze <nr>" oder "todeszone <gebaeude>"."""
    aus = []
    for n, e in L.items():
        if ist_feind(e.get("besitzer")) and e.get("typ") in fern_reich and e.get("leben", 1) > 0:
            aus.append((e["x"], e["y"], fern_reich[e["typ"]], 1, "schuetze %d" % n))
    for n, g in G.items():
        if ist_feind(g.get("besitzer")) and g.get("typ") in TODESZONE:
            r, w = TODESZONE[g["typ"]]
            aus.append((g["x"], g["y"], r, w, "todeszone %d" % n))
    return aus


def _gefahr_einzeln(p, bed):
    return sum(w for x, y, r, w, _ in bed if schach(p, (x, y)) <= r)


class Karte:
    """Gefahr und Sperren fuer die ganze Karte. Je Feld: Gefahr = Summe der Gewichte, deren Quadrat (Schach-Abstand <= r) das
    Feld trifft - ueber ein Differenzfeld in einem Schritt fuer alle Bedrohungen. Kosten je Feld 1 + k * Gefahr; Feuer (x, y, r)
    und gesperrt (Feld bool [x, y]) sind nicht begehbar; gebiete (Feld int [x, y], 0 = nicht begehbar, aus speicher.wegkarte)
    beschraenkt jede Suche auf das Gebiet ihres Startpunkts. Die Kostensuche je Startpunkt wird zwischengespeichert."""

    def __init__(self, bed, feuer=(), gesperrt=None, k=K, n=GROESSE, gebiete=None, links=None):
        self.bed, self.feuer, self.k, self.n = list(bed), list(feuer), k, n
        d = np.zeros((n + 1, n + 1), np.int64)
        for x, y, r, w, _ in self.bed:
            x0, x1, y0, y1 = max(0, x - r), min(n - 1, x + r), max(0, y - r), min(n - 1, y + r)
            if x0 > x1 or y0 > y1:
                continue
            d[x0, y0] += w
            d[x1 + 1, y0] -= w
            d[x0, y1 + 1] -= w
            d[x1 + 1, y1 + 1] += w
        self.g = d.cumsum(0).cumsum(1)[:n, :n]
        self.sperre = np.zeros((n, n), bool) if gesperrt is None else np.array(gesperrt, bool, copy=True)
        for x, y, r in self.feuer:
            self.sperre[max(0, x - r):max(0, x + r + 1), max(0, y - r):max(0, y + r + 1)] = True
        self.kosten = 1.0 + k * self.g.astype(float)
        self.kosten[self.sperre] = -1.0
        self.gebiete = None if gebiete is None else np.asarray(gebiete)
        self.links = None if links is None else np.asarray(links)
        self._suche, self._frei = {}, {}

    def drin(self, p):
        return 0 <= p[0] < self.n and 0 <= p[1] < self.n

    def gefahr(self, p):
        return int(self.g[p[0], p[1]]) if self.drin(p) else _gefahr_einzeln(p, self.bed)

    def gesperrt(self, p):
        return bool(self.sperre[p[0], p[1]]) if self.drin(p) else any(schach(p, (x, y)) <= r for x, y, r in self.feuer)

    def gebiet_bei(self, p):
        """Gebiet am Feld p; steht dort keins (Gebaeudekante), das haeufigste bis 2 Felder daneben; 0 = keins/ohne Wegkarte."""
        if self.gebiete is None or not self.drin(p):
            return 0
        g = int(self.gebiete[p[0], p[1]])
        if g:
            return g
        fen = self.gebiete[max(0, p[0] - 2):p[0] + 3, max(0, p[1] - 2):p[1] + 3]
        werte, zahl = np.unique(fen[fen > 0], return_counts=True)
        return int(werte[zahl.argmax()]) if len(werte) else 0

    def frei(self, start):
        """bool-Feld [x, y]: wohin, wer bei start steht, gehen darf - nicht gesperrt und (mit Wegkarte) in seinem Gebiet."""
        g = self.gebiet_bei(tuple(start))
        if g not in self._frei:
            self._frei[g] = ~self.sperre & (self.gebiete == g) if self.gebiete is not None and g else ~self.sperre
        return self._frei[g]

    def offen(self, start, p):
        return bool(self.frei(start)[p[0], p[1]]) if self.drin(p) else not self.gesperrt(p)

    def linie(self, a, b):
        """Alle Felder der geraden Strecke a -> b (jedes Feld, nicht nur jedes zweite)."""
        n = max(1, schach(a, b))
        return [(a[0] + (b[0] - a[0]) * i // n, a[1] + (b[1] - a[1]) * i // n) for i in range(n + 1)]

    def suche(self, start):
        """(MCP, Kostenfeld) ab start - einmal je Startpunkt und Runde."""
        start = tuple(start)
        if start not in self._suche:
            from skimage.graph import MCP
            kosten = np.where(self.frei(start), self.kosten, -1.0)
            if self.drin(start) and kosten[start] < 0:      # wer im Feuer oder auf einer Gebaeudekante steht, darf hinaus
                kosten[start] = 1.0
            if self.links is not None:
                from weggraph import LinkSuche
                m = LinkSuche(kosten, self.links, start)
                kum = m.kum
            else:
                m = MCP(kosten, fully_connected=True)
                kum, _ = m.find_costs([start])
            self._suche[start] = (m, kum)
        return self._suche[start]

    def ankunft(self, start, ziel):
        """Das erreichbare Feld am Ziel: das Ziel selbst oder, wenn es gesperrt/unerreichbar ist, das billigste bis
        ZIEL_UMKREIS daneben; None ohne solches Feld."""
        _, kum = self.suche(start)
        bester = None
        for r in range(ZIEL_UMKREIS + 1):
            for x in range(ziel[0] - r, ziel[0] + r + 1):
                for y in range(ziel[1] - r, ziel[1] + r + 1):
                    if schach((x, y), ziel) != r or not self.drin((x, y)) or not np.isfinite(kum[x, y]):
                        continue
                    if bester is None or kum[x, y] < kum[bester]:
                        bester = (x, y)
            if bester is not None:
                return bester
        return None


def _als_karte(bed, feuer=(), k=K):
    return bed if isinstance(bed, Karte) else Karte(bed, feuer=feuer, k=k)


def gefahr(p, bed):
    return bed.gefahr(tuple(p)) if isinstance(bed, Karte) else _gefahr_einzeln(p, bed)


def _strecke(a, b, schritt=2):
    n = max(1, schach(a, b) // schritt)
    return [(a[0] + (b[0] - a[0]) * i // n, a[1] + (b[1] - a[1]) * i // n) for i in range(n + 1)]


def weg_gefahr(start, weg, bed):
    """Summe der Gefahr entlang start -> weg[0] -> ... (alle 2 Felder abgetastet)."""
    s, a = 0, tuple(start)
    for b in weg:
        s += sum(gefahr(p, bed) for p in _strecke(a, tuple(b))[1:])
        a = tuple(b)
    return s


def sicherer_weg(start, ziel, bed, feuer=(), k=K, schritt=None, rand=None):
    """Wegpunkte von start nach ziel mit der kleinsten Summe aus Weglaenge und k * Gefahr; Feuer (x, y, r) ist gesperrt.
    bed ist eine Liste aus bedrohungen() oder eine fertige Karte (dann gelten deren Feuer und k). Gibt [ziel], wenn die gerade
    Strecke ohne Gefahr und Sperre ist; None, wenn das Ziel nicht erreichbar ist. (schritt/rand: frueher Raster und Suchfeld
    des A*, heute ohne Wirkung - die Suche deckt die ganze Karte.)"""
    karte = _als_karte(bed, feuer, k)
    start, ziel = tuple(start), tuple(ziel)
    from weggraph import linie_erlaubt
    if (karte.links is None or linie_erlaubt(karte.linie(start, ziel), karte.links)) and all(karte.gefahr(p) == 0 and karte.offen(start, p) for p in karte.linie(start, ziel)[1:]):
        return [ziel]
    an = karte.ankunft(start, ziel)
    if an is None:
        return None
    m, _ = karte.suche(start)
    pfad = [tuple(int(v) for v in q) for q in m.traceback(an)]
    if pfad[-1] != ziel and karte.offen(start, ziel) and (karte.links is None or linie_erlaubt(karte.linie(pfad[-1], ziel), karte.links)):
        pfad.append(ziel)
    # glaetten: nur Eckpunkte (Richtungswechsel) und jedes dritte Feld kommen als Wegpunkt in Frage; von jedem Punkt der
    # weiteste, dessen gerade Strecke durch kein gesperrtes Feld fuehrt und nicht gefaehrlicher ist als das ersetzte Stueck -
    # beides Feld fuer Feld gezaehlt (21.10.: mit "alle 2 Felder" gegen Stuecke von 3 Feldern blieb ein gerader Schraegweg in
    # 11 Wegpunkte zerlegt)
    summe = [0]
    for q in pfad[1:]:
        summe.append(summe[-1] + karte.gefahr(q))
    kand = [0] + [i for i in range(1, len(pfad) - 1)
                  if i % 3 == 0 or (pfad[i][0] - pfad[i - 1][0], pfad[i][1] - pfad[i - 1][1])
                  != (pfad[i + 1][0] - pfad[i][0], pfad[i + 1][1] - pfad[i][1])] + ([len(pfad) - 1] if len(pfad) > 1 else [])
    weg, i = [], 0
    while i < len(kand) - 1:
        j = len(kand) - 1
        while j > i + 1:
            gerade = karte.linie(pfad[kand[i]], pfad[kand[j]])
            if (karte.links is None or linie_erlaubt(gerade, karte.links)) and all(karte.offen(start, p) for p in gerade[1:]) and \
                    sum(karte.gefahr(p) for p in gerade[1:]) <= summe[kand[j]] - summe[kand[i]]:
                break
            j -= 1
        weg.append(pfad[kand[j]])
        i = j
    return weg or [ziel]


def schuetzen_am_weg(start, weg, bed):
    """Die Schuetzen (art "schuetze"), deren Reichweite den Weg trifft - mit der Zahl der Wegpunkte, die sie treffen."""
    bed = bed.bed if isinstance(bed, Karte) else bed
    punkte, a = [], tuple(start)
    for b in weg:
        punkte += _strecke(a, tuple(b))[1:]
        a = tuple(b)
    aus = []
    for x, y, r, w, art in bed:
        if art.startswith("schuetze"):
            n = sum(1 for p in punkte if schach(p, (x, y)) <= r)
            if n:
                aus.append((n, art, (x, y)))
    return sorted(aus, reverse=True)


def erreichbare_schuetzen(start, bed):
    """Die Bedrohungen "schuetze", deren Feld im Gebiet von start liegt - zu Fuss erreichbar. Wer auf Mauer, Turm oder Bergfried
    steht, ist in einem eigenen Gebiet (gemessen 21.10. Takt 74.036: von Franz' 159 Einheiten 36 im Gebiet 1 vor der Burg, 90 im
    Gebiet 39 um den Lord, die uebrigen in 31/36/41/45). Ohne Wegkarte (Liste statt Karte) zaehlt jeder als erreichbar."""
    if not isinstance(bed, Karte) or bed.gebiete is None:
        return [b for b in (bed.bed if isinstance(bed, Karte) else bed) if b[4].startswith("schuetze")]
    g = bed.gebiet_bei(tuple(start))
    return [b for b in bed.bed if b[4].startswith("schuetze") and g and bed.drin((b[0], b[1]))
            and int(bed.gebiete[b[0], b[1]]) == g]


def mindestzahl(gegner_leben, takte, schaden=NAHKAMPF_SCHADEN, sicherheit=SICHERHEIT):
    """Kleinste Zahl Nahkaempfer, die gegner_leben in takte Takten toetet (mit Sicherheitszuschlag), mindestens 1."""
    return max(1, int(math.ceil(sicherheit * gegner_leben / float(max(1, schaden * takte)))))
