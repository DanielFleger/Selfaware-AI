# -*- coding: utf-8 -*-
"""Schussfeld und sicherer Weg (SAI 12.10., Daniel 01:03: "den besten und sichersten Weg finden, der trotzdem der kuerzeste
ist"; 01:08: "genau wissen, wo alle gegnerischen Einheiten hinschiessen koennen, und den toten Winkel ausnutzen").

1. Gefahr: jede feindliche Fernkampfeinheit deckt ihre Reichweite ab (REICHWEITE, abgelesen aus ascension_ai.json "ranges",
   12.10.). Gezaehlt wird in Schachfeldern - das deckt mehr ab als ein Kreis, ist also die vorsichtige Seite, solange die
   Zaehlweise des Spiels nicht gemessen ist (offen). Gefahr eines Feldes = Zahl der Schuetzen, die es erreichen.
   OFFEN (Frage-Agent 01:19): Assassinen sind getarnt - ob die Gefahr erst mit der Entdeckung beginnt, ist ungemessen.
2. Weg: Dijkstra auf einem groben Gitter (ZELLE x ZELLE Felder) ueber begehbares Gelaende (Kartenzeichen "Gs." wie
   pruefe_begehbar). Schrittkosten = Laenge * (1 + GEWICHT * Gefahr). Bei grossem GEWICHT ist das der kuerzeste Weg unter
   den Wegen mit der wenigsten Gefahr - der tote Winkel, wenn es einen gibt.
3. Wegpunkte: Zellmitten dort, wo der Weg die Richtung wechselt, hoechstens alle MAX_ABSTAND Felder einer.
Gegenprobe: werkzeug/schussfeld_pruefen.py."""
import heapq

REICHWEITE = {22: 40, 23: 40, 70: 40, 74: 40, 72: 18, 76: 11}   # Bogen, Armbrust, arab. Bogen, Pferdebogen, Schleuder, Feuerwerfer
# GEMESSEN 12.10. 01:51 (beschuss_messen.py, 6 Kampfprotokolle 1012f-k, ~6.900 Runden): Schaden je Schuetze in Reichweite und
# Tick an einer Assassine haengt am Abstand zum NAECHSTEN Feind (Entdeckung, Assassinen sind getarnt) und an Deckung durch
# Gebaeude (Daniel 01:50 "man kann sich hinter Soeldnerposten/Kasernen, Haeusern verstecken"): (Feind bis, (Gebaeude<=5, offen))
SCHADEN_SATZ = ((3, (0.76, 2.10)), (8, (0.37, 1.37)), (15, (0.06, 0.56)), (999, (0.0, 0.06)))
DECKUNG_R = 5
ZELLE = 4
GEWICHT = 50.0
MAX_ABSTAND = 24
GROESSE = 400
BEGEHBAR = "Gs."


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def schuetzen(L, sp):
    """[(Ort, Reichweite)] aller feindlichen Fernkaempfer im Lagebild."""
    return [((e["x"], e["y"]), REICHWEITE[e["typ"]]) for e in L.values()
            if e["besitzer"] not in (0, sp) and e["typ"] in REICHWEITE]


def gefahr_am(ort, schuetzen_liste):
    return sum(1 for p, r in schuetzen_liste if schach(ort, p) <= r)


class Gitter:
    """Grobes Gitter: begehbar je Zelle (Mehrheit der Felder) und Gefahr je Zelle (Mitte der Zelle)."""

    def __init__(self, gelaende, schuetzen_liste, zelle=ZELLE, frei=None, feinde=None, gebaeude=None):
        self.z = zelle
        self.n = GROESSE // zelle
        self.frei = frei if frei is not None else [[True] * self.n for _ in range(self.n)]
        if gelaende and frei is None:
            for cy in range(self.n):
                for cx in range(self.n):
                    gut = alle = 0
                    for y in range(cy * zelle, cy * zelle + zelle):
                        zeile = gelaende[y] if y < len(gelaende) else ""
                        for x in range(cx * zelle, cx * zelle + zelle):
                            alle += 1
                            gut += x < len(zeile) and zeile[x] in BEGEHBAR
                    self.frei[cy][cx] = gut * 2 > alle
        self.gefahr = [[0] * self.n for _ in range(self.n)]
        self.satz = None                  # 01:51: erwarteter Schaden je Tick je Zelle (nur mit feinde/gebaeude)
        for (px, py), r in schuetzen_liste:
            c0x, c1x = max(0, (px - r) // zelle), min(self.n - 1, (px + r) // zelle)
            c0y, c1y = max(0, (py - r) // zelle), min(self.n - 1, (py + r) // zelle)
            for cy in range(c0y, c1y + 1):
                for cx in range(c0x, c1x + 1):
                    if schach(self.mitte((cx, cy)), (px, py)) <= r:
                        self.gefahr[cy][cx] += 1

        if feinde is not None:
            self.satz = [[0.0] * self.n for _ in range(self.n)]
            for cy in range(self.n):
                for cx in range(self.n):
                    k = self.gefahr[cy][cx]
                    if not k:
                        continue
                    m = self.mitte((cx, cy))
                    dn = min((schach(m, f) for f in feinde), default=999)
                    gedeckt = any(schach(m, q) <= DECKUNG_R for q in (gebaeude or ()))
                    satz = next(s for grenze, s in SCHADEN_SATZ if dn <= grenze)
                    self.satz[cy][cx] = k * (satz[0] if gedeckt else satz[1])

    def schaden_je_tick(self, c):
        return self.satz[c[1]][c[0]] if self.satz is not None else float(self.gefahr[c[1]][c[0]])

    def risiko_von(self, start, ticks_je_feld=15):
        """Einquellen-Dijkstra: je Zelle der kleinste erwartete Schaden auf dem Weg dorthin (Schaden je Tick x Ticks in der Zelle,
        plus ein Hauch Weglaenge) und die Weglaenge in Feldern. {Zelle: (Schaden, Felder)}"""
        s = self.zelle_von(start)
        dist, q, out = {s: 0.0}, [(0.0, 0, s)], {}
        tz = ticks_je_feld * self.z
        while q:
            d, lang, c = heapq.heappop(q)
            if c in out:
                continue
            out[c] = (d, lang * self.z)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = c[0] + dx, c[1] + dy
                    if (not dx and not dy) or not (0 <= nx < self.n and 0 <= ny < self.n) or (nx, ny) in out:
                        continue
                    if not self.frei[ny][nx]:
                        out.setdefault((nx, ny), (d + self.schaden_je_tick((nx, ny)) * tz, (lang + 1) * self.z))
                        continue
                    nd = d + self.schaden_je_tick((nx, ny)) * tz + 0.001
                    if nd < dist.get((nx, ny), 1e18):
                        dist[(nx, ny)] = nd
                        heapq.heappush(q, (nd, lang + 1, (nx, ny)))
        return out

    def zelle_von(self, ort):
        return (min(self.n - 1, max(0, ort[0] // self.z)), min(self.n - 1, max(0, ort[1] // self.z)))

    def mitte(self, c):
        return (c[0] * self.z + self.z // 2, c[1] * self.z + self.z // 2)

    def weg(self, start, ziel, gewicht=GEWICHT):
        """Zellenweg von start nach ziel (Felder). Start- und Zielzelle gelten immer als begehbar. None, wenn kein Weg."""
        s, t = self.zelle_von(start), self.zelle_von(ziel)
        dist, vor = {s: 0.0}, {s: None}
        q = [(0.0, s)]
        while q:
            d, c = heapq.heappop(q)
            if c == t:
                break
            if d > dist.get(c, 1e18):
                continue
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if not dx and not dy:
                        continue
                    nx, ny = c[0] + dx, c[1] + dy
                    if not (0 <= nx < self.n and 0 <= ny < self.n):
                        continue
                    if not self.frei[ny][nx] and (nx, ny) != t:
                        continue
                    if dx and dy and not (self.frei[c[1]][nx] or self.frei[ny][c[0]]):
                        continue                   # nicht schraeg zwischen zwei gesperrten Zellen durch
                    # Schraeg kostet im Spiel so viel wie gerade (L59) - dann gibt es viele gleich lange Wege, und Dijkstra
                    # nimmt einen beliebigen (schussfeld_pruefen 01:23: Gegenprobe mit Gewicht 0 blieb zufaellig gruen).
                    # Ein Hauch mehr fuer schraeg bevorzugt bei Gleichstand den geraden Weg.
                    kosten = (1.001 if dx and dy else 1.0) * (1 + gewicht * self.schaden_je_tick((nx, ny)))
                    nd = d + kosten
                    if nd < dist.get((nx, ny), 1e18):
                        dist[(nx, ny)], vor[(nx, ny)] = nd, c
                        heapq.heappush(q, (nd, (nx, ny)))
        if t not in vor:
            return None
        pfad, c = [], t
        while c is not None:
            pfad.append(c)
            c = vor[c]
        return pfad[::-1]

    def belastung(self, zellen):
        """Summe der Gefahr entlang eines Zellenwegs (wie viele Zellen x Schuetzen)."""
        return sum(self.schaden_je_tick(c) for c in zellen)

    def gerade(self, start, ziel):
        """Zellen auf der geraden Linie (so laeuft ein direkter Angriffsbefehl ungefaehr)."""
        a, b = self.zelle_von(start), self.zelle_von(ziel)
        k = max(abs(b[0] - a[0]), abs(b[1] - a[1]), 1)
        out = []
        for i in range(k + 1):
            c = (int(round(a[0] + (b[0] - a[0]) * i / float(k))), int(round(a[1] + (b[1] - a[1]) * i / float(k))))
            if not out or out[-1] != c:
                out.append(c)
        return out


def wegpunkte(gitter, zellen, ziel):
    """Wegpunkte (Felder) entlang des Zellenwegs: bei Richtungswechsel und mindestens alle MAX_ABSTAND Felder. Ohne Start,
    der letzte Punkt ist das Ziel selbst."""
    if not zellen:
        return []
    punkte, letzt_r, letzt_p = [], None, gitter.mitte(zellen[0])
    for a, b in zip(zellen, zellen[1:]):
        r = (b[0] - a[0], b[1] - a[1])
        p = gitter.mitte(a)
        if (letzt_r is not None and r != letzt_r) or schach(p, letzt_p) >= MAX_ABSTAND:
            if a != zellen[0]:
                punkte.append(p)
                letzt_p = p
        letzt_r = r
    punkte.append(tuple(ziel))
    return punkte


def sicherer_weg(gelaende, L, sp, start, ziel, gitter=None):
    """(wegpunkte, belastung_weg, belastung_gerade, gitter). Wegpunkte leer, wenn der gerade Weg nicht gefaehrlicher ist."""
    g = gitter or Gitter(gelaende, schuetzen(L, sp))
    zellen = g.weg(start, ziel)
    gerade = g.gerade(start, ziel)
    bw, bg = (g.belastung(zellen) if zellen else None), g.belastung(gerade)
    if zellen is None or bw >= bg:
        return [], bw, bg, g
    return wegpunkte(g, zellen, ziel), bw, bg, g
