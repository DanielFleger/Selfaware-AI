# -*- coding: utf-8 -*-
"""plane_holz im Stand vor dem 19.10.2026 21:20 - nur zum Vergleich (eroeffnung_holz_pruefen.py). Neu geschrieben in
eroeffnung.py (Daniel 21:15: "15 Sekunden zum Berechnen, geht das nicht schneller?"); diese Fassung bleibt unveraendert
liegen, damit jede spaetere Aenderung gegen dasselbe Ergebnis geprueft werden kann."""
import math
from selfaware.macro.eroeffnung import felder, HACKEN, JE_FELD, JE_GANG, HOLZ_JE_EINHEIT
import selfaware.macro.eroeffnung as eroeffnung


def plane_holz_alt(karte_huette, karte_lager, B, K, horizont=20000, lager_max=45):
    """Lagerstelle + K Huetten so, dass in <horizont> Ticks moeglichst viel Holz im Lager ankommt.
    Je Huette: geliefert = min(Holz je Tick * horizont, Holz ihrer EIGENEN Baeume im Umkreis 6 um den Eingang);
    ein Baum gehoert nur einer Huette. Lager hoechstens <lager_max> Felder (Schachbrett) vom Bergfried-Eingang."""
    kand = []
    for (x, y) in karte_huette:
        ex, ey = x + 1, y + 3
        nah = [b for b in B if abs(b["x"] - ex) <= 6 and abs(b["y"] - ey) <= 6 and math.hypot(b["x"] - ex, b["y"] - ey) <= 6]
        if not nah:
            continue
        d, naechster = min((math.hypot(b["x"] - ex, b["y"] - ey), b["nr"]) for b in nah)
        if d <= 1.5:          # Eingang direkt am Baum (Daniel: Eingang neben einem Baum; 3 Huetten je Baum, 23:23)
            kand.append({"x": x, "y": y, "e": (ex, ey), "baum": d, "baeume": nah, "am_baum": naechster})
    if not kand:
        return None
    if len(karte_lager) <= 4:      # feste Lagerstelle(n) zum Vergleich - kein Filter
        lager = list(karte_lager)
    else:
        lager = [(x, y) for (x, y) in karte_lager if x % 2 == 0 and y % 2 == 0
                 and max(abs(x + 3 - eroeffnung.BERGFRIED_EINGANG[0]), abs(y + 3 - eroeffnung.BERGFRIED_EINGANG[1])) <= lager_max
                 and any(abs(x + 3 - k["e"][0]) <= 25 and abs(y + 3 - k["e"][1]) <= 25 for k in kand[::5])]
    beste = None
    for (sx, sy) in lager:
        sm = (sx + 3, sy + 3)
        block = felder(sx, sy, 6)
        def rate(k): return JE_GANG / (HACKEN + 2 * JE_FELD * (math.hypot(k["e"][0] - sm[0], k["e"][1] - sm[1]) + k["baum"]))
        wahl, belegt, vergeben, summe = [], set(block), set(), 0.0
        rest_holz = {}   # Baum -> noch nicht verplantes Holz (mehrere Huetten duerfen sich einen Baum teilen, Daniel 22:35)
        je_baum = {}     # Baum -> Huetten mit Eingang direkt daran (hoechstens 3, Daniel 23:23)
        for _ in range(K):
            bester = None
            for k in kand:
                f = felder(k["x"], k["y"], 3) | {k["e"]}
                if f & belegt:
                    continue
                holz = sum(rest_holz.get(b["nr"], HOLZ_JE_EINHEIT * b["rest"]) for b in k["baeume"])
                if holz <= 0:
                    continue
                schon = je_baum.get(k["am_baum"], 0)
                if schon >= 3:
                    continue
                geliefert = min(rate(k) * horizont, holz)
                wert = geliefert * (1.25 if schon in (1, 2) else 1.0)   # Haeufung um einen Baum bevorzugen
                if bester is None or wert > bester[0]:
                    bester = (wert, k, f)
            if bester is None:
                break
            g, k, f = bester
            g = min(rate(k) * horizont, sum(rest_holz.get(b["nr"], HOLZ_JE_EINHEIT * b["rest"]) for b in k["baeume"]))
            je_baum[k["am_baum"]] = je_baum.get(k["am_baum"], 0) + 1
            wahl.append(dict(k, geliefert=g, rate=rate(k))); belegt |= f; summe += g
            offen = g   # das verplante Holz von den naechsten Baeumen abziehen
            for b in sorted(k["baeume"], key=lambda b: math.hypot(b["x"] - k["e"][0], b["y"] - k["e"][1])):
                r = rest_holz.get(b["nr"], HOLZ_JE_EINHEIT * b["rest"])
                nimm = min(r, offen); rest_holz[b["nr"]] = r - nimm; offen -= nimm
                if offen <= 0:
                    break
        if wahl and (beste is None or summe > beste[0]):
            beste = (summe, (sx, sy), wahl, belegt)
    return beste
