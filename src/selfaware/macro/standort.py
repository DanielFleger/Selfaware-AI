# -*- coding: utf-8 -*-
"""Bester Platz fuer das Vorratslager (Daniel 06.10. 20:48: "ich bin mir eigentlich 100 % sicher, dass Vorratslager
umplatzieren effektiver waere, als das am Bergfried zu lassen - bitte dafuer auch den optimalen Platz finden").

Warum diese Bewertung (Wissensregister, gemessen): je Streitkolbenkaempfer laeuft ein Gerber 2/3 x Abstand Hoftor ->
Waffenlager (3 Leder je Kuh, ein Gang hin und zurueck je Kuh und je Abgabe), und das Eisen muss mit 2/3 Eisen je Keule
(1,5 Keulen je Eisen, Daniel G6) vom Bergwerk ins Lager - laut Liga holt der Bergmann doppelt (enable_iron_double_pickup),
also 1/3 Gang x 2 x Abstand = 2/3 x Abstand Mine -> Lager. Beide Wege wiegen damit gleich (Annahme: ungeprueft, solange
die Bergleute nicht gemessen sind). Waffenlager und Schmieden liegen direkt am Lager (Planer).
  Fall MARKT: Eisen wird gekauft (liegt sofort im Lager) -> nur der Kuhweg zaehlt.
  Fall MINE : Kuhweg + Eisenweg.

Woher die Plaetze kommen: das Spiel selbst (Modulbefehl platzkarte, checkBuildingCanBePlacedHere) fuer Milchviehhof
(Bau-Nummer 73, 10x10) und Eisenmine (90, 4x4); Wege ueber die Weg-Ebene (wegkarte), Laufzeit 24 Ticks je Feld.
Naeherung: "naechster moeglicher Hof" - drei Hoefe brauchen drei Plaetze ohne Ueberlappung (offen).
Ergebnis: data/research/standort_<zeit>.json + data/research/standort_<zeit>.png
Aufruf: uv run python -m selfaware.macro.standort [r=70]
"""

from selfaware import workspace as _workspace
import json
import os
import re
import sys
import time
from collections import deque

HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.game.ucp.befehl as kanal
import selfaware.runtime.live.erstes_spiel as E
import selfaware.services.wegkarte as W
from selfaware.game.ucp.laden import befehl

D = os.path.join(_workspace.DATA)
SP = 1


def platzkarte(mapper, groesse, x0, y0, x1, y1):
    befehl({"platzkarte": {"spieler": SP, "mapper": mapper, "groesse": groesse, "x0": x0, "y0": y0, "x1": x1, "y1": y1}},
           120.0, bis="PLATZKARTE")
    zeilen = open(os.path.join(kanal.ABZUG, "platzkarte.txt"), encoding="utf-8").read().splitlines()
    return {(x0 + i, y0 + j) for j, z in enumerate(zeilen[1:]) for i, c in enumerate(z) if c == "+"}


def abstaende(k, quellen):
    """Felder-Abstand jedes Felds zur naechsten Quelle, ueber die erlaubten Schritte (rueckwaerts gleich, weil die
    Weg-Ebene bis auf Lager/Stufen symmetrisch ist - gemessen: Einbahn nur an Lagerteilen und Bergfried)."""
    q = deque(p for p in quellen if p in k["f"] and k["f"][p][0])
    d = {p: 0 for p in q}
    while q:
        p = q.popleft()
        for bit, (dx, dy) in W.RICHTUNG.items():
            n = (p[0] + dx, p[1] + dy)
            if k["f"][p][0] & bit and n in k["f"] and n not in d:
                d[n] = d[p] + 1
                q.append(n)
    return d


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    r = int(arg.get("r", 70))
    E.LEERE_KI = True
    E.gefecht_starten(100)
    befehl({"pause": True}, 0.5)
    G = E.runde_lesen()[2]
    berg = next(g for g in G.values() if g["besitzer"] == SP and g["typ"] == 41)
    bx, by = berg["x"] + 3, berg["y"] + 3
    x0, y0, x1, y1 = max(bx - r, 1), max(by - r, 1), min(bx + r, 398), min(by + r, 398)
    t = time.time()
    k = W.holen(x0, y0, x1, y1)
    hof = platzkarte(73, 10, x0, y0, x1, y1)
    mine = platzkarte(90, 4, x0, y0, x1, y1)
    print("Platzkarten: Hof %d Stellen, Mine %d Stellen (%.0f s)" % (len(hof), len(mine), time.time() - t), flush=True)
    tore = {(x + dx, y + dy) for x, y in hof for dx, dy in ((4, -1), (5, -1), (-1, 4), (-1, 5), (10, 4), (10, 5), (4, 10), (5, 10))}
    minen_eingang = {(x + 2, y + 4) for x, y in mine} | {(x - 1, y + 2) for x, y in mine} | \
                    {(x + 1, y - 1) for x, y in mine} | {(x + 4, y + 1) for x, y in mine}      # alle Richtungen (G10)
    d_hof, d_mine = abstaende(k, tore), abstaende(k, minen_eingang)
    # Kandidaten: 5x5 frei fuer das Lager + Platz drumherum fuer Waffenlager/Werkstaetten (Umkreis 8: >= 60 % frei)
    frei = {p for p, v in k["f"].items() if v[0] == 0xFF and v[1] == 0}
    kand = []
    for (x, y) in frei:
        if (x - x0) % 2 or (y - y0) % 2:
            continue
        if not all((x + i, y + j) in frei for i in range(5) for j in range(5)):
            continue
        umfeld = sum(1 for i in range(-8, 13) for j in range(-8, 13) if (x + i, y + j) in frei)
        if umfeld < 0.6 * 21 * 21:
            continue
        m = (x + 2, y + 2)
        if m in d_hof:
            kand.append({"lager": (x, y), "hof": d_hof[m], "mine": d_mine.get(m), "umfeld": umfeld,
                         "berg": max(abs(m[0] - bx), abs(m[1] - by))})
    markt = sorted(kand, key=lambda c: (c["hof"], c["berg"]))[:10]
    mit_mine = sorted([c for c in kand if c["mine"] is not None], key=lambda c: (c["hof"] + c["mine"], c["berg"]))[:10]
    jetzt = {"hof": d_hof.get((bx, by + 6)), "mine": d_mine.get((bx, by + 6))}
    erg = {"bergfried": (bx, by), "fenster": (x0, y0, x1, y1), "hof_stellen": len(hof), "mine_stellen": len(mine),
           "heute_am_bergfried": jetzt, "beste_markt": markt, "beste_mine": mit_mine, "kandidaten": len(kand)}
    print("Heute (Lager am Bergfried): Kuhweg %s, Eisenweg %s Felder" % (jetzt["hof"], jetzt["mine"]))
    for c in markt[:5]:
        print("MARKT  Lager %s: Kuhweg %d, Eisenweg %s, Abstand Bergfried %d" % (c["lager"], c["hof"], c["mine"], c["berg"]))
    for c in mit_mine[:5]:
        print("MINE   Lager %s: Kuhweg %d + Eisenweg %d = %d, Abstand Bergfried %d" % (c["lager"], c["hof"], c["mine"],
                                                                                   c["hof"] + c["mine"], c["berg"]))
    stempel = time.strftime("%Y%m%d_%H%M%S")
    zeichne(k, hof, mine, d_hof, d_mine, markt, mit_mine, (bx, by), os.path.join(D, "standort_%s.png" % stempel))
    pfad = os.path.join(D, "standort_%s.json" % stempel)
    json.dump(erg, open(pfad, "w", encoding="utf-8"), indent=1, default=str)
    print("Daten:", pfad, flush=True)


def zeichne(k, hof, mine, d_hof, d_mine, markt, mit_mine, berg, pfad, zelle=5):
    from PIL import Image, ImageDraw
    x0, y0, x1, y1 = k["x0"], k["y0"], k["x1"], k["y1"]
    img = Image.new("RGB", ((x1 - x0 + 1) * zelle, (y1 - y0 + 1) * zelle + 30), (250, 248, 240))
    d = ImageDraw.Draw(img)
    gmax = max([d_hof.get(p, 0) + d_mine.get(p, 0) for p in k["f"]] + [1])
    for (x, y), v in k["f"].items():
        px, py = (x - x0) * zelle, (y - y0) * zelle
        if v[0] == 0:
            c = (110, 110, 110) if not v[1] else (60, 60, 60)
        else:
            s = (d_hof.get((x, y), gmax) + d_mine.get((x, y), gmax)) / gmax
            g = int(255 * (1 - min(s, 1)))
            c = (255, 200 + g // 5, 120 + g // 2)
        if (x, y) in hof:
            c = (110, 190, 90)
        elif (x, y) in mine:
            c = (90, 130, 210)
        d.rectangle([px, py, px + zelle - 1, py + zelle - 1], fill=c)
    for liste, farbe in ((markt[:3], (220, 120, 0)), (mit_mine[:3], (200, 0, 0))):
        for c in liste:
            x, y = c["lager"]
            d.rectangle([(x - x0) * zelle, (y - y0) * zelle, (x - x0 + 5) * zelle, (y - y0 + 5) * zelle], outline=farbe, width=2)
    bx, by = berg
    d.rectangle([(bx - x0 - 3) * zelle, (by - y0 - 3) * zelle, (bx - x0 + 4) * zelle, (by - y0 + 4) * zelle], outline=(0, 0, 0), width=2)
    d.text((4, (y1 - y0 + 1) * zelle + 8), "gruen: Hof moeglich, blau: Mine moeglich, schwarz: Bergfried, orange: beste Lagerplaetze "
           "(Eisen vom Markt), rot: beste (Eisen aus Minen); heller = kuerzere Wege", fill=(0, 0, 0))
    img.save(pfad)
    return pfad


if __name__ == "__main__":
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
