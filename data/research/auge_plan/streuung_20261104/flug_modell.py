# -*- coding: utf-8 -*-
"""Nachbau der Geschoss-Regeln aus dem Spielcode (Export, gegen den Speicher geprueft). Reine Rechnung, ruft nichts im Spiel.

Quellen: prepareProjectileTarget 0053cbd0, setRandomShootLocation 005330a0, initializeProjectileVelocities 00403a20,
math_atan_1 00402c50, moveProjectileEntity 004084a0, updateEntityMicroMovement 00402ae0, processEntityHitBuildingOrUnit 00407190,
processEntityDamageToUnit 00531920. Alle Laengen in Mikro (8 je Feld), Takte als ganze Zahlen.
"""
import math

import numpy as np

PI = 3.1415926535
G = 9.812
G_HALB = 4.906
# Art: Flugkurve, Tempo oder Startwinkel, Zeitschritt je Takt. Aus dem Speicher von Instanz 2 gelesen (tabellen.py), Liga aktiv
TABELLE = {1: (0, 125, 0.18), 2: (2, 10, 0.08), 3: (1, 30, 0.14), 4: (1, 15, 0.10), 7: (0, 125, 0.20), 20: (0, 170, 0.18), 24: (6, 81, 0.14), 25: (6, 81, 0.16), 33: (0, 100, 0.20), 34: (0, 80, 0.20), 35: (6, 70, 0.14), 36: (6, 60, 0.14), 37: (0, 125, 0.18)}
GEBAEUDE_HOEHE = {40: 0x40, 41: 0x5c, 42: 0xbe, 45: 0x80, 46: 0x80, 69: 0x76, 74: 0x128, 75: 0x94, 76: 0xb4, 77: 0xc0, 78: 0xc0}  # getBuildingHeightForBuildingID, Arten BT_* aus dem Export
# Fenster ueber dem Boden der Einheit, in dem ein Geschoss sie trifft (processEntityDamageToUnit)
UT_TREBUCHET, UT_TURM, UT_KATAPULT, UT_SCHILD, UT_RAMME, UT_MANGONEL, UT_BALLISTA, UT_FBALLISTA = 40, 58, 39, 60, 59, 41, 61, 77


def _ftol(x):
    return int(x)


def winkel(v, d, hd):
    """math_atan_1: flacher der beiden Winkel, unmoeglich oder gar kein Abstand gibt 45 Grad."""
    if d == 0:
        return 45
    q = v * v
    f = d * 4.0
    a = q / (f * G)
    w = (q * q) / (96.275344 * f * f) - ((q + q) * _ftol(hd / 2)) / (f * f * G) - 1.0
    if w < 0:
        return 45
    s = math.sqrt(w)
    w1 = _ftol(math.atan(a - s) * 180.0 / PI + 0.4999000132083893)
    w2 = _ftol(math.atan(a + s) * 180.0 / PI + 0.4999000132083893)
    r = w1 if w2 > w1 else w2
    if w2 <= w1:
        r = w2
    if r < -90:
        r = w1 if w1 > w2 else w2
        if r < -90:
            return 45
    if r > 90:
        return 45
    return r


def tempo(w, d, hd):
    """computeVelocity 00402da0: Das Tempo, mit dem ein Schuss im festen Winkel w genau am Ziel landet."""
    r = w * PI / 180.0
    c = math.cos(r)
    n = d * 2
    unten = math.tan(r) * n - _ftol(hd / 4)
    if unten == 0:
        return 0
    q = (G * n * n / (c * c)) / unten
    if q < 0:
        return 0
    return _ftol(math.sqrt(q))


def anfang(art, d, hd, v_aufzeichnung=None):
    """(Tempo, Winkel) wie initializeProjectileVelocities 00403a20. d: Laenge der Sichtlinie, hd: Zielhoehe minus Starthoehe.
    Kurve 0 und 6 haben festes Tempo und rechnen den Winkel, Kurve 1 und 2 haben festen Winkel und rechnen das Tempo.
    Gebrannte Pfeile, Feuerballisten und Schuesse auf den Boden tragen nach dem Start die Art des normalen Geschosses, darum darf das aufgezeichnete Tempo die Kurve bestimmen."""
    kurve, wert, _ = TABELLE[art]
    if kurve == 0:
        v = v_aufzeichnung if v_aufzeichnung else wert
        return v, winkel(v, d, hd)
    if kurve == 1:
        return tempo(wert, d, hd), wert
    if kurve == 2:
        w = 3 if hd < 0 else wert
        v = tempo(w, d, hd)
        if v < 1:
            return tempo(15, d, hd), 15
        return v, w
    return None


def anfang_voll(art, d, hd):
    """(Tempo, Winkel) wie beim Abschuss, nur aus der Art. Kurve 6: Bodenschuss, ueber 150 Mikro Tempo 125."""
    kurve, wert, _ = TABELLE[art]
    if kurve == 6:
        v = 125 if d > 150 else wert
        return v, winkel(v, d, hd)
    return anfang(art, d, hd)


def strecke(x, y, zx, zy):
    """Bresenham wie initializeProjectileVelocities: Art, Schritte, Zustand."""
    dx, dy = abs(zx - x), abs(zy - y)
    sx, sy = (1 if x <= zx else -1), (1 if y <= zy else -1)
    if dx == 0:
        return (1 if dy else 0), sx, sy, 0, 0, 0
    if dy == 0:
        return 2, sx, sy, 0, 0, 0
    if dx < dy:
        return 3, sx, sy, 2 * dx, 2 * dx - 2 * dy, 2 * dx - dy
    return 4, sx, sy, 2 * dy, 2 * dy - 2 * dx, 2 * dy - dx


def schritt(x, y, st, err):
    a, sx, sy, f47, f48, _ = st
    if a == 1:
        return x, y + sy, err
    if a == 2:
        return x + sx, y, err
    if a == 3:
        if err > 0:
            return x + sx, y + sy, err + f48
        return x, y + sy, err + f47
    if a == 4:
        if err > 0:
            return x + sx, y + sy, err + f48
        return x + sx, y, err + f47
    return x, y, err


def fenster(typ):
    """Wie hoch ueber dem Boden der Einheit ein Geschoss sie noch trifft."""
    return {UT_TREBUCHET: 80, UT_TURM: 80, UT_KATAPULT: 50, UT_SCHILD: 90, UT_RAMME: 40, UT_MANGONEL: 70}.get(typ, 42)


def gebaeude_hoehe(art):
    """getBuildingHeightForBuildingID 00409db0, Arten aus dem Export."""
    return GEBAEUDE_HOEHE.get(int(art), 0)


def bahn(x, y, h0, zx, zy, vc, vs, b, takte=400):
    """Erzeugt je Takt die Liste der Schritte: (takt_nummer, [(mx, my, h), ...], h_ende). Ohne Einschlag, das entscheidet der Aufrufer."""
    st = strecke(x, y, zx, zy)
    err = st[5]
    t = np.float32(b)
    wg = 0
    hd = 0
    for n in range(1, takte + 1):
        tt = float(t)
        ziel = _ftol(vc * tt * 0.25)
        h_ziel = _ftol(2.0 * (vs * tt - G_HALB * tt * tt))
        rest = ziel - wg
        lokal = _ftol((h_ziel - hd) / rest) if rest else 0
        schritte = []
        h_t = hd
        while wg < ziel:
            wg += 1
            x, y, err = schritt(x, y, st, err)
            h_t += lokal
            schritte.append((x, y, h0 + h_t, wg))
        hd = h_ziel
        t = np.float32(t + np.float32(b))
        yield n, schritte, h0 + h_ziel
