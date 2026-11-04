# -*- coding: utf-8 -*-
"""Wohin ein Schuss zielt: Nachbau von setRandomShootLocation 005330a0 und prepareProjectileTarget 0053cbd0. Reine Rechnung.

Alle Laengen in Mikro (8 je Feld). r ist die Zufallszahl des Spielstroms (currentNumber2), danach ruft das Spiel nextRandomNumber2.
"""

KATAPULT, TREBUCHET, MANGONEL, BALLISTA, FBALLISTA = 39, 40, 41, 61, 77
# Versatz des Feuers (DAT_XYOffsetsInAllDirections, aus dem Speicher): Index ist Zufallszahl & 63. Vier Achsen, je bis 7 oder 8 Mikro, also hoechstens ein Feld daneben
FEUER_VERSATZ = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0), (-8, 0),
                 (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7), (0, -8),
                 (0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7), (-8, -8),
                 (0, 0), (-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6), (-7, 7), (1, -1), (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7), (8, -8)]
# Feuerschaden je Takt (Tabelle im Speicher, processFireDamageToUnit ist umgeleitet): 75, Lord 25, Feuerwehr 1, Feuerwerfer 10
FEUER_SCHADEN = {55: 25, 53: 1, 76: 10}


def feuerschaden(typ, halb):
    """Verlust je Takt auf einem Feuerfeld. halb: Feuer aus einer Flamme des Feuerwerfers (fireIntensity 1)."""
    s = FEUER_SCHADEN.get(typ, 75)
    return s // 2 if halb else s


def _ab(a, b):
    """Ganzzahl-Division wie in C: zur Null hin."""
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


def _rest(a, b):
    return a - b * _ab(a, b)


def streuung_boden(typ, auf_boden, r):
    """(entlang, quer, hoehe) vor dem Halbieren. entlang > 0 heisst zu kurz, entlang < 0 zu weit (in Blickrichtung des Schuetzen). auf_boden: targetingType ist UIT_ATTACK_LAND."""
    if typ == TREBUCHET:
        e = _rest(r, 0x60) - 0x30 if (r & 3) == 0 else 0
        return e, _rest(_ab(r, 256), 0x60) - 0x30, -0x10 + ((r >> 7) & 0x1f)
    if typ == KATAPULT:
        return (r & 0x7f) - 0x60, _rest(_ab(r, 256), 0x60) - 0x30, -0x30 + ((r >> 7) & 0x3f)
    if typ == MANGONEL:
        return _rest(r, 0xe0) - 0x70, ((r >> 8) & 0x7f) - 0x40, -0x40 + ((r >> 7) & 0x7f)
    if typ == BALLISTA:
        if auf_boden:
            return (r & 0x1f) - 0x18, _rest(_ab(r, 256), 0x28) - 0x14, -0x14 + _rest(_ab(r, 128), 0x28)
        return 0, 0, 0
    if typ == FBALLISTA and not auf_boden:
        return 0, 0, _rest(_ab(r, 128), 0x1e)
    return _rest(r, 0x60) - 0x30, _rest(_ab(r, 256), 0x50) - 0x28, -0x28 + _rest(_ab(r, 128), 0x50)


def _d34(v):
    return _ab(v * 3, 4)


def ziel_boden(typ, auf_boden, sx, sy, blick, tx, ty, tz, r):
    """setRandomShootLocation: der Punkt, auf den der Schuss wirklich zielt."""
    abstand = max(abs(sx - tx), abs(sy - ty))
    e, q, dz = streuung_boden(typ, auf_boden, r)
    z = tz + dz
    z = 8 if z < 8 else 0xfa if z > 0xfa else z
    if _ab(abstand, 2) < e:
        e, q = _ab(e, 2), _ab(q, 2)
    if abstand < e:
        e = -e
    if blick == 0:
        x, y = tx + q, ty + e
    elif blick == 1:
        a, b = _d34(q), _d34(e)
        x, y = tx + a - b, ty + b + a
    elif blick == 2:
        x, y = tx - e, ty + q
    elif blick == 3:
        a, b = _d34(q), _d34(e)
        x, y = tx - b - a, ty + a - b
    elif blick == 4:
        x, y = tx + q, ty - e
    elif blick == 5:
        a, b = _d34(q), _d34(e)
        x, y = tx + b - a, ty - a - b
    elif blick == 6:
        x, y = tx + e, ty + q
    elif blick == 7:
        a, b = _d34(q), _d34(e)
        x, y = tx + b + a, ty + b - a
    else:
        x, y = tx, ty
    return x, y, z


def vorhalt(abstand, tempo_zustand, tempo_lauf):
    """Wie weit der Schuetze vor ein laufendes Ziel haelt. abstand: Rueckgabe der Sichtpruefung beim Schuss."""
    v = _ab(abstand * 0x85, 100)
    if tempo_zustand == 0:
        if tempo_lauf < 2:
            return v >> 4 if v >= 0 else _ab(v, 16)
        return _ab(v, tempo_lauf << 4)
    return _ab(v, 8)


def zielpunkt_einheit(ex, ey, ez, laeuft, blick, abstand, tempo_zustand, tempo_lauf):
    """Grundpunkt auf eine Einheit: Feldmitte des Ziels, bei laufendem Ziel plus Vorhalt in seiner Blickrichtung."""
    x, y = ex * 8 + 4, ey * 8 + 4
    if laeuft:
        v = vorhalt(abstand, tempo_zustand, tempo_lauf)
        dx = {1: 1, 2: 1, 3: 1, 5: -1, 6: -1, 7: -1}.get(blick, 0)
        dy = {0: -1, 1: -1, 3: 1, 4: 1, 5: 1, 7: -1}.get(blick, 0)
        x, y = x + dx * v, y + dy * v
    return x, y, ez


def fehler_stufe(typ, z_ziel, z_eigen):
    """Wie stark ein Schuss auf eine Einheit streuen kann (0 heisst gar nicht). Chance auf Streuung: Stufe von 300."""
    if z_ziel < z_eigen:
        return {39: 20, 61: 20, 40: 50, 41: 60, 77: 10}.get(typ, 0)
    v = z_ziel - z_eigen
    if v > 0x4b:
        v = v + _ab(v, 2)
    if typ == 77:
        return 0
    v += {39: 40, 61: 40, 40: 60, 41: 70}.get(typ, 0)
    if v < 1:
        return 0
    return min(v, 0x118)


def streuung_einheit(x, y, z, typ, z_eigen, r, rng_eigen, rng_ziel):
    """prepareProjectileTarget ab Marke 0053cdb9: Punkt nach der Streuung."""
    v = fehler_stufe(typ, z, z_eigen)
    if v <= 0:
        return x, y, z, False
    if _rest(r, 300) >= v:
        return x, y, z, True
    a = r & 7
    if a < 2:
        w = _ab(v, 4) or 1
        halb = _ab(w, 2)
        x += _rest(abs(_ab(r, 512) + rng_eigen), w) - halb
        y += _rest(abs(r + rng_ziel), w) - halb
    elif a < 6:
        w = _ab(v, 6) or 1
        n = _rest(abs(rng_eigen + r), w)
        z = z - (n + 20) if n + 0x1c <= z else z + n + 20
    else:
        w = _ab(v, 6) or 1
        z = z + _rest(abs(r + rng_ziel), w) + 0x28
    return x, y, z, True


def ziel_vorbereiten_boden(typ, auf_boden, sx, sy, blick, tx, ty, tz, z_eigen, rng_eigen, tabelle, i):
    """prepareProjectileTarget mit Ziel -1: erst setRandomShootLocation (Zahl tabelle[i]), dann dieselbe zweite Stufe wie beim Schuss auf eine Einheit (naechste Zahl, Ziel-Zufall 0).
    Rueckgabe: x, y, z, Anzahl gezogener Zahlen. i ist der Platz der aktuellen Zahl in der Tabelle."""
    x, y, z = ziel_boden(typ, auf_boden, sx, sy, blick, tx, ty, tz, tabelle[i % 20000])
    x, y, z, zog = streuung_einheit(x, y, z, typ, z_eigen, tabelle[(i + 1) % 20000], rng_eigen, 0)
    return x, y, z, 2 if zog else 1
