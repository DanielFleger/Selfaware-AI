# -*- coding: utf-8 -*-
"""B-157 Angriff nach Daniels Regel "maximale Sicherheit, dann minimaler Widerstand" (21.10.2026 21:11: "du laeufst frontal mit
maximalem Beschuss ... was hast du vom Assassinen gelernt?"; 21:16: "immer diese Metrik updaten; manchmal macht es Sinn,
Einheiten zu besiegen, die auf dem Weg sind, z.B. Fernkaempfer - dann nur die minimale Anzahl, die zum Toeten reicht";
21:21 Bild: "immer noch maximale Einheiten dagegenwerfen und hoffen - das Gegenteil von minimalem Risiko").
Bausteine, ohne Spiel pruefbar (gefahr_pruefen.py):
  bedrohungen    - wer schiesst wohin: feindliche Fernkaempfer (Reichweite gefecht.FERN_REICH, Gewicht 1) und Todeszonen
                   (Burgteil Typ 75: Verlustkarte Pruefstand 21.10. - 58 von 275 eigenen Toten hoechstens 8 Felder daneben)
  gefahr         - Summe der Gewichte, die einen Punkt erreichen
  sicherer_weg   - A* auf einem 2er-Raster, jeder Schritt kostet 1 + K * Gefahr; Feuer ist gesperrt; danach geglaettet, aber
                   nur so weit, dass keine Abkuerzung gefaehrlicher ist als das Stueck, das sie ersetzt
  weg_gefahr     - Gefahr eines Weges (alle 2 Felder abgetastet) - damit werden Angriffsstellen verglichen
  schuetzen_am_weg / mindestzahl - Fernkaempfer, die den Weg bestreichen, und wie viele Nahkaempfer sie sicher toeten
UNGEMESSEN (Startwerte, Daniel bekommt sie so gesagt): TODESZONE-Radius 8 und Gewicht 10, K = 6, Nahkampf-Schaden je Takt.
"""
import heapq
import math

TODESZONE = {75: (8, 10)}       # Burgteil-Typ -> (Radius, Gewicht); Typ 75 aus der Verlustkarte 21.10. - UNGEMESSEN
K = 6                           # Gewicht der Gefahr gegenueber 1 Feld Weg - UNGEMESSEN
NAHKAMPF_SCHADEN = 200          # Leben je Nahkaempfer und Takt gegen einen Schuetzen - UNGEMESSEN (Assassinen-Raten L-Register)
SICHERHEIT = 1.5                # so viel mehr als rechnerisch noetig wird geschickt


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


def gefahr(p, bed):
    return sum(w for x, y, r, w, _ in bed if schach(p, (x, y)) <= r)


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


def sicherer_weg(start, ziel, bed, feuer=(), k=K, schritt=2, rand=None):
    """Wegpunkte von start nach ziel mit der kleinsten Summe aus Weglaenge und k * Gefahr; Feuer (x, y, r) ist gesperrt.
    Gibt [ziel], wenn die gerade Strecke ohne Gefahr und Feuer ist; None ohne Weg im Suchfeld. Das Suchfeld waechst in Stufen
    (30, 60, 90 Felder um die Strecke - Franz' Bogen schiessen 44 weit), bis ein Weg ohne Gefahr gefunden ist."""
    if rand is None:
        bester = None
        for r_ in (30, 60, 90):
            w = sicherer_weg(start, ziel, bed, feuer, k, schritt, r_)
            if w is not None and (bester is None or weg_gefahr(start, w, bed) < weg_gefahr(start, bester, bed)):
                bester = w
            if bester is not None and weg_gefahr(start, bester, bed) == 0:
                break
        return bester

    def im_feuer(p):
        return any(schach(p, (x, y)) <= r for x, y, r in feuer)
    gerade = _strecke(start, ziel)
    if all(gefahr(p, bed) == 0 and not im_feuer(p) for p in gerade):
        return [tuple(ziel)]
    x0, x1 = min(start[0], ziel[0]) - rand, max(start[0], ziel[0]) + rand
    y0, y1 = min(start[1], ziel[1]) - rand, max(start[1], ziel[1]) + rand
    nah = [b for b in bed if x0 - b[2] <= b[0] <= x1 + b[2] and y0 - b[2] <= b[1] <= y1 + b[2]]
    sx, sy = start
    punkt = lambda q: (sx + q[0] * schritt, sy + q[1] * schritt)
    # Gefahr einmal je Rasterpunkt vorrechnen (je Schuetze sein Quadrat), statt je Punkt alle Schuetzen durchzugehen
    gef = {}
    for x, y, r, w, _ in nah:
        for i in range(-((sx - (x - r)) // schritt), (x + r - sx) // schritt + 1):
            for j in range(-((sy - (y - r)) // schritt), (y + r - sy) // schritt + 1):
                gef[(i, j)] = gef.get((i, j), 0) + w
    kosten_cache = {}

    def kosten(q):
        if q not in kosten_cache:
            kosten_cache[q] = None if im_feuer(punkt(q)) else 1 + k * gef.get(q, 0)
        return kosten_cache[q]
    h = lambda q: schach(punkt(q), ziel) / float(schritt)
    offen, her, g_best, am_ziel = [(h((0, 0)), 0.0, (0, 0))], {(0, 0): None}, {(0, 0): 0.0}, None
    while offen:
        _, g, q = heapq.heappop(offen)
        if g > g_best[q]:
            continue
        if schach(punkt(q), ziel) <= schritt:
            am_ziel = q
            break
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                r = (q[0] + di, q[1] + dj)
                p = punkt(r)
                if r == q or not (x0 <= p[0] <= x1 and y0 <= p[1] <= y1):
                    continue
                c = kosten(r)
                if c is None:
                    continue
                if g + c < g_best.get(r, 1e18):
                    g_best[r], her[r] = g + c, q
                    heapq.heappush(offen, (g + c + h(r), g + c, r))
    if am_ziel is None:
        return None
    pfad = [am_ziel]
    while her[pfad[-1]] is not None:
        pfad.append(her[pfad[-1]])
    pfad = [punkt(q) for q in reversed(pfad)] + [tuple(ziel)]
    # glaetten: von jedem Punkt der weiteste, dessen gerade Strecke nicht gefaehrlicher ist als das ersetzte Stueck und
    # durch kein Feuer fuehrt
    weg, i = [], 0
    while i < len(pfad) - 1:
        j = len(pfad) - 1
        while j > i + 1:
            gerade = _strecke(pfad[i], pfad[j])
            if not any(im_feuer(p) for p in gerade) and \
                    sum(gefahr(p, nah) for p in gerade) <= weg_gefahr(pfad[i], pfad[i + 1:j + 1], nah):
                break
            j -= 1
        weg.append(pfad[j])
        i = j
    return weg


def schuetzen_am_weg(start, weg, bed):
    """Die Schuetzen (art "schuetze"), deren Reichweite den Weg trifft - mit der Zahl der Wegpunkte, die sie treffen."""
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


def mindestzahl(gegner_leben, takte, schaden=NAHKAMPF_SCHADEN, sicherheit=SICHERHEIT):
    """Kleinste Zahl Nahkaempfer, die gegner_leben in takte Takten toetet (mit Sicherheitszuschlag), mindestens 1."""
    return max(1, int(math.ceil(sicherheit * gegner_leben / float(max(1, schaden * takte)))))
