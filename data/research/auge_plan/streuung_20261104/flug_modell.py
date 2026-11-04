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


def bahn2(x, y, h0, zx, zy, vc, vs, b, takte=400, t0=None):
    """Je Takt: Nummer, Schritte (mx, my, h, Schrittzahl), Hoehe am Ende, Zeit des Takts. t0: Zeit im ersten Takt; beim Abschuss der Zeitschritt, nach einem Abprall 0."""
    st = strecke(x, y, zx, zy)
    err = st[5]
    t = np.float32(b if t0 is None else t0)
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
        yield n, schritte, h0 + h_ziel, tt


def bahn(x, y, h0, zx, zy, vc, vs, b, takte=400):
    """Wie bahn2, ohne die Zeit."""
    for n, schritte, h_e, _ in bahn2(x, y, h0, zx, zy, vc, vs, b, takte):
        yield n, schritte, h_e


def drehung(vc, vs, b, t, w0):
    """graphicRotationUnk: Steigung zwischen diesem und dem vorigen Zeitschritt. moveProjectileEntity 004084a0."""
    if vs == 0:
        return w0
    x = lambda u: vs * u - G_HALB * u * u  # noqa: E731
    return _ftol(math.atan(3.0 * (x(t) - x(t - b)) / (vc * b)) * 180.0 / PI)


def bildnummer(w):
    """angleToRotationFrameIndex 00402bd0: Unter 3 fliegt das Geschoss steil nach unten."""
    if w < 6:
        return 0 if w < -0x31 else 1 if w < -0x22 else 2 if w < -0x10 else 3 if w < -4 else 4
    return 5 if w < 0x15 else 6 if w < 0x24 else 7 if w < 0x33 else 8 if w < 0x5b else 4


def wand_bits(fx, fy, ist_wand):
    """setBitFlagBasedOnWallTowerGatehouseOrKeep 004ff870: Welche der 8 Nachbarn sind Mauer, Turm oder Burg."""
    f = 0
    for dx, dy, bit in ((1, 0, 0x20), (-1, 0, 2), (-1, -1, 1), (1, -1, 0x40), (0, -1, 0x80), (-1, 1, 4), (1, 1, 0x10), (0, 1, 8)):
        if ist_wand(fx + dx, fy + dy):
            f |= bit
    return f


def abprall_ziel(orient, mx, my, sx, sy, bits):
    """handleProjectileWallBounce 00403ff0: Wohin das Geschoss nach dem Abprall fliegt. sx, sy: Abschussort. Gespiegelt wird die Achse, die im Feld naeher am Rand liegt; in der Ecke entscheiden die Nachbarn."""
    u4, u7 = mx & 7, my & 7
    if orient in (0x3c, 0x40, 0x44, 0x48):
        return sx, sy
    if orient in (0x3d, 0x3e, 0x3f):
        u7 = 7 - u7
        if u4 == u7:
            b = bits & 10
            if b == 10:
                return sx, sy
            if orient == 0x3f:
                u4, u7 = (100, u7) if b in (0, 2) else (u4, 100)
            else:
                u4, u7 = (u4, 100) if b in (0, 8) else (100, u7)
    elif orient in (0x41, 0x42, 0x43):
        if u4 == u7:
            b = bits & 0x82
            if b == 0x82:
                return sx, sy
            if orient == 0x43:
                u4, u7 = (100, u7) if b in (0, 0x80) else (u4, 100)
            else:
                u4, u7 = (u4, 100) if b in (0, 2) else (100, u7)
    elif orient in (0x45, 0x46, 0x47):
        u4 = 7 - u4
        if u4 == u7:
            b = bits & 0xa0
            if b == 0xa0:
                return sx, sy
            if orient == 0x47:
                u4, u7 = (100, u7) if b in (0, 0x20) else (u4, 100)
            else:
                u4, u7 = (u4, 100) if b in (0, 0x80) else (100, u7)
    elif orient in (0x49, 0x4a, 0x4b):
        u4, u7 = 7 - u4, 7 - u7
        if u4 == u7:
            b = bits & 0x28
            if b == 0x28:
                return sx, sy
            if orient == 0x49:
                u4, u7 = (100, u7) if b in (0, 0x20) else (u4, 100)
            else:
                u4, u7 = (u4, 100) if b in (0, 8) else (100, u7)
    else:
        return 0, 0
    if u4 <= u7:
        return sx, my * 2 - sy
    return mx * 2 - sx, sy


def nach_abprall(w_jetzt, v):
    """Tempo, Winkel, vCos, vSin nach dem Abprall: Tempo durch 8, Winkel wie die Flugrichtung im Moment, hoechstens 80 nach unten."""
    w = max(w_jetzt, -0x50)
    v8 = _ab8(v)
    r = w * PI / 180.0
    return v8, w, float(np.float32(v8 * math.cos(r))), float(np.float32(v8 * math.sin(r)))


def _ab8(v):
    return int(v / 8)


def freund_verschont(art, typ, mensch):
    """processEntityDamageToUnit: Wen ein Geschoss des eigenen Teams nicht trifft. Pfeil, Bolzen, Stein und Ballista keinen Freund; Schild, Turm und Ramme kein Stein; das Mangonel eines Nicht-Menschen keinen Freund."""
    return art in (1, 7, 33, 20) or typ in (UT_SCHILD, UT_TURM, UT_RAMME) or (art == 4 and not mensch)


def fenster_nachbar(typ):
    """Fenster bei einem Treffer vom Nachbarfeld: nur das Trebuchet ist dort niedriger (40 statt 80)."""
    return 40 if typ == UT_TREBUCHET else fenster(typ)
