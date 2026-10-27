# -*- coding: utf-8 -*-
"""Besitzbuch (B-273 Stufe 1, erster Baustein) und Steh-Augen fuer ALLE Einheiten (B-275; Daniel 27.10. 22:35 "kannst du das
Log auch fuer alle anderen Einheiten machen? hier stehen einfach auch Schwertkaempfer rum").

Anlass Partie 221355: Assassine 219 bekam ab Takt 3.830 immer wieder Ziel und Weg und stand trotzdem 10.189 Takte am selben
Fleck (die Haende kommen nicht an); 10 arab. Schwertkaempfer standen ab 25.806 in der eigenen Burg ohne eine einzige Logzeile
(kein Modul fuehrt sie).

merken(befehl): jeder Befehl, der durch befehl.sende geht - je Einheit der LETZTE Befehl mit Absender-Modul, Art, Ziel und
Zaehler; Doppelbefehle (zwei verschiedene Module in derselben Runde fuer dieselbe Einheit) werden gezaehlt.
steh_runde(t, L, sp, arten): jede eigene Einheit, die STEH_ERKLAER Takte auf demselben Feld steht (Zustand 0/1), meldet -
hoechstens alle STEH_ERKLAER Takte - wer sie zuletzt befehligt hat, womit und wann, oder dass kein Modul sie je befehligt hat."""
import sys

STEH_ERKLAER = 300
BEFEHLSARTEN = ("angriff", "halten", "aufloesen", "mauerziel", "lauf", "gruppe", "stapel")
FREMD = ("befehl", "laden", "besitzbuch", "lordschutz")

LETZTER = {}             # Einheit -> {"modul", "art", "ziel", "runde", "anzahl"}
DOPPELT = {}             # Einheit -> Zahl der Runden mit Befehlen aus zwei verschiedenen Modulen
RUNDE = [0]
_IN_RUNDE = {}           # Einheit -> Modul in der laufenden Runde
_STILL = {}              # Einheit -> (Feld, seit, zuletzt gemeldet)


def _absender():
    f = sys._getframe(2)
    while f is not None:
        m = f.f_globals.get("__name__", "?")
        if m.split(".")[-1] not in FREMD:
            return "%s.%s" % (m, f.f_code.co_name)
        f = f.f_back
    return "?"


def _einheiten(wert):
    if isinstance(wert, dict):
        for k in ("einheiten", "nr"):
            v = wert.get(k)
            if isinstance(v, list):
                return [int(x) for x in v if isinstance(x, int)]
            if isinstance(v, int):
                return [v]
    return []


def merken(befehl):
    """Aus einem Befehl (auch {"befehle": [...]}) je Einheit den letzten Befehl festhalten. Wirft nie."""
    try:
        liste = befehl.get("befehle") if isinstance(befehl, dict) and "befehle" in befehl else [befehl]
        modul = None
        for c in liste or []:
            if not isinstance(c, dict):
                continue
            for art in BEFEHLSARTEN:
                if art not in c:
                    continue
                ns = _einheiten(c[art])
                if not ns:
                    continue
                modul = modul or _absender()
                w = c[art]
                ziel = w.get("ziel") or w.get("gebaeude") or w.get("lauf") or (w.get("x"), w.get("y")) if isinstance(w, dict) else None
                for n in ns:
                    alt = LETZTER.get(n, {})
                    LETZTER[n] = {"modul": modul, "art": art, "ziel": ziel, "runde": RUNDE[0], "anzahl": alt.get("anzahl", 0) + 1}
                    vor = _IN_RUNDE.get(n)
                    if vor is not None and vor != modul.split(".")[0]:
                        DOPPELT[n] = DOPPELT.get(n, 0) + 1
                    _IN_RUNDE[n] = modul.split(".")[0]
    except Exception:
        pass


def steh_runde(t, L, sp, arten):
    """Am Ende jeder Lenker-Runde: Runde weiterzaehlen und STEHT-Zeilen fuer stehende eigene Einheiten der arten."""
    RUNDE[0] += 1
    _IN_RUNDE.clear()
    aus = []
    for n, e in L.items():
        if e.get("besitzer") != sp or e.get("typ") not in arten:
            continue
        f = (e["x"], e["y"])
        alt = _STILL.get(n)
        if e.get("zustand") not in (0, 1) or alt is None or alt[0] != f:
            _STILL[n] = (f, t, None)
            continue
        seit, gemeldet = alt[1], alt[2]
        if t - seit < STEH_ERKLAER or (gemeldet is not None and t - gemeldet < STEH_ERKLAER):
            continue
        _STILL[n] = (f, seit, t)
        b = LETZTER.get(n)
        if b is None:
            wer = "KEIN Modul hat ihr je einen Befehl gegeben"
        else:
            wer = "zuletzt %s: %s %s vor %d Runden (%d Befehle insgesamt%s)" % (
                b["modul"], b["art"], b["ziel"], RUNDE[0] - b["runde"], b["anzahl"],
                ", %d Runden mit Doppelbefehl" % DOPPELT[n] if DOPPELT.get(n) else "")
            if RUNDE[0] - b["runde"] <= 2:
                wer += " - Befehl frisch, sie bewegt sich trotzdem nicht"
        aus.append("STEHT %d (Art %d) seit %d Takten bei %s: %s" % (n, e["typ"], t - seit, f, wer))
    for n in [n for n in _STILL if n not in L]:
        del _STILL[n]
    return aus
