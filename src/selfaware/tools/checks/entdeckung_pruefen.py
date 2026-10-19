# -*- coding: utf-8 -*-
"""Wann darf auf eine Assassine geschossen werden? Gegenprobe an den Kampfmitschriften (SAI 17.10., Daniel 09:41: "das
Erhalten von Assassinen durch schlaues Angreifen und Beachten der 'Assassine beobachtet'-Trigger ist das Wichtigste").

ABGELESEN 17.10. aus dem Spielcode (Ghidra, OpenSHC-Namen; Belege data/research/entdeckung_spielcode.md):
  acquireShootTarget (0x0054B0D0): ein Schuetze waehlt eine Assassine von sich aus nur, wenn ihr Feld
  assassinsMicroDistanceToEnemyUnk (Einheit +1080) <= 160 Feinmass (= 20 Felder) ist.
  Das Feld schreibt updateUnits (0x00579300) nur in der eigenen Pruefrunde der Assassine: alle 128 Takte
  (Maske 127 aus DAT_UNIT_ENEMY_NOTICE_RANGE[73]). Es ist der Abstand zum naechsten feindlichen Einheit mit gesetztem
  isSelectable (Soldaten, Lord, Sklaven, Tunnelgraeber, Moenche, Belagerung) - Arbeiter und Bauern zaehlen NICHT.
  Abstand = Naeherung max(a,b) + (2*min/5)*min/max in Feinmass (8 je Feld).

VORHER FESTGELEGT (Widerlegung), bevor die Zahlen gelesen werden:
  Betrachtet werden Rundenpaare einer eigenen Assassine ohne JEDEN Feind (alle Arten) im Umkreis 2 Felder (Schach) zu
  Beginn und Ende - so faellt Nahkampfschaden weg. "Verdeckt" heisst: in ALLEN Runden der 256 Takte davor war der
  naechste waehlbare Feind weiter als 176 Feinmass (160 + 16 fuer das Runden der Felder).
  1. Liegt der Anteil verdeckter Runden MIT Lebensverlust ueber 2 % der verdeckten Runden, ist die Regel widerlegt
     (dann enttarnt noch etwas anderes - z.B. Arbeiter oder der eigene Angriff, Daniel 09:58).
  2. Gegenprobe gegen hohles Gruen: unter den "sichtbaren" Runden (naechster waehlbarer Feind <= 160 in der Runde selbst)
     mit Schuetzen in Reichweite muss der Anteil mit Lebensverlust deutlich hoeher sein (mindestens 5x der verdeckten).
     Sonst unterscheidet die Pruefung nichts.
  3. Daniels Punkt 1 (Angriff enttarnt): verdeckte Runden, in denen die Assassine im Nahkampfzustand an einem Gebaeude
     oder einem Arbeiter steht, getrennt zaehlen - hier faellt der Umkreis-2-Ausschluss fuer Gebaeude weg, fuer Arbeiter
     nicht (deren Schlag waere Nahkampfschaden). Mehr als 2 % mit Verlust = Angriff enttarnt auch fuer die Schuetzen.
Aufruf: uv run python -m selfaware.tools.checks.entdeckung_pruefen data/research/lage_....jsonl.gz [...]"""
import os
import sys
from collections import deque

HIER = os.path.dirname(os.path.abspath(__file__))

from selfaware.telemetry.lageprotokoll import runden

WAEHLBAR = {5, 22, 23, 24, 25, 26, 27, 28, 29, 30, 37, 39, 40, 41, 55, 58, 59, 60, 61,
            70, 71, 72, 73, 74, 75, 76, 77}
FERN = {22: 54, 23: 40, 70: 54, 74: 54, 72: 18, 76: 11}       # live gelesen 17.10. (Geschosstabelle 0x005B6358)
SICHT, RAND, FENSTER = 160, 16, 256
TIERE = {44, 45, 46, 47, 48, 49, 51, 52, 62, 67, 68, 69}


def abstand_fein(a, b):
    """Spielnaeherung (findNearestEnemyAndHeadTowardsIt) in Feinmass, Felder x 8."""
    dx, dy = abs(a[0] - b[0]) * 8, abs(a[1] - b[1]) * 8
    if dx < dy:
        return ((dx * 2) // 5) * dx // dy + dy
    if dx == 0:
        return 0
    return ((dy * 2) // 5) * dy // dx + dx


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def main():
    pfade = [a for a in sys.argv[1:] if "=" not in a]
    sp = 1
    z = dict(verdeckt=0, verdeckt_verlust=0, sichtbar_fern=0, sichtbar_fern_verlust=0, angriff_verdeckt=0,
             angriff_verdeckt_verlust=0, verdeckt_verlust_d=0)
    beispiele = []
    for pfad in pfade:
        vorher, verlauf = {}, {}
        for t, st, E, G in runden(pfad):
            feinde = [e for e in E if e["besitzer"] not in (0, sp) and e["typ"] not in TIERE]
            waehl = [(e["x"], e["y"]) for e in feinde if e["typ"] in WAEHLBAR]
            schuetzen = [((e["x"], e["y"]), FERN[e["typ"]]) for e in feinde if e["typ"] in FERN]
            arbeiter = [(e["x"], e["y"]) for e in feinde if e["typ"] not in WAEHLBAR]
            alle = [(e["x"], e["y"]) for e in feinde]
            for e in E:
                if e["typ"] != 73 or e["besitzer"] != sp:
                    continue
                nr, ort = e["nr"], (e["x"], e["y"])
                d = min((abstand_fein(ort, w) for w in waehl), default=99999)
                v = verlauf.setdefault(nr, deque())
                v.append((t, d))
                while v and v[0][0] < t - FENSTER:
                    v.popleft()
                a = vorher.get(nr)
                if not a or t <= a[0]:
                    continue
                verlust = max(0, a[1] - e["leben"])
                nah = any(schach(ort, p) <= 2 for p in alle) or any(schach(a[2], p) <= 2 for p in alle)
                in_reichweite = any((ort[0] - p[0]) ** 2 + (ort[1] - p[1]) ** 2 <= r * r for p, r in schuetzen)
                verdeckt = v[0][0] <= t - FENSTER + 40 and all(dd > SICHT + RAND for _, dd in v)
                kampf = e.get("zustand") in (106, 107)          # 106 Nahkampf (mit Nahziel), 107 Gebaeude/Mauer - gezaehlt 17.10.
                if verdeckt and kampf and not any(schach(ort, p) <= 2 for p in arbeiter if p):
                    z["angriff_verdeckt"] += 1
                    z["angriff_verdeckt_verlust"] += verlust > 0
                if nah:
                    continue
                if verdeckt:
                    z["verdeckt"] += 1
                    if verlust:
                        z["verdeckt_verlust"] += 1
                        z["verdeckt_verlust_d"] += verlust
                        if len(beispiele) < 8:
                            beispiele.append((os.path.basename(pfad), t, nr, ort, verlust, min(dd for _, dd in v)))
                elif d <= SICHT and in_reichweite:
                    z["sichtbar_fern"] += 1
                    z["sichtbar_fern_verlust"] += verlust > 0
            vorher = {e["nr"]: (t, e["leben"], (e["x"], e["y"])) for e in E if e["typ"] == 73 and e["besitzer"] == sp}
    q = lambda a, b: (100.0 * z[a] / z[b]) if z[b] else float("nan")
    print("verdeckt (256 Takte kein waehlbarer Feind <= %d Feinmass, kein Feind im Umkreis 2): %d Runden, mit Verlust %d = %.2f %%"
          % (SICHT + RAND, z["verdeckt"], z["verdeckt_verlust"], q("verdeckt_verlust", "verdeckt")))
    print("sichtbar (<= %d) und Schuetze in Reichweite: %d Runden, mit Verlust %d = %.2f %%"
          % (SICHT, z["sichtbar_fern"], z["sichtbar_fern_verlust"], q("sichtbar_fern_verlust", "sichtbar_fern")))
    print("verdeckt UND im Angriff (Gebaeude/Einheit, kein Arbeiter daneben): %d Runden, mit Verlust %d = %.2f %%"
          % (z["angriff_verdeckt"], z["angriff_verdeckt_verlust"], q("angriff_verdeckt_verlust", "angriff_verdeckt")))
    for b in beispiele:
        print("  verdeckt mit Verlust:", b)
    w1 = z["verdeckt"] and q("verdeckt_verlust", "verdeckt") > 2.0
    w2 = not (z["sichtbar_fern"] and q("sichtbar_fern_verlust", "sichtbar_fern") >= 5 * max(q("verdeckt_verlust", "verdeckt"), 0.5))
    print("URTEIL (nur fuer diese Mitschriften): Regel %s; Gegenprobe %s" % ("WIDERLEGT" if w1 else "nicht widerlegt", "HOHL (unterscheidet nicht)" if w2 else "trennt"))


if __name__ == "__main__":
    main()
