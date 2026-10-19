# -*- coding: utf-8 -*-
"""Karte um den eigenen Bergfried erkunden (Haertetest ab Tick 0, Daniel 06.10. 20:54): wo liegen Wald, Stein, Eisen,
Gruenland - und wie weit (Laufweg ueber die Weg-Ebene, 24 Ticks je Feld) vom Bergfried und von den Lager-Kandidaten?

Quellen: Modulbefehle rohstoffkarte (Stein b, Eisen i, Gruenland G; Baeume mit Rest), wegkarte, platzkarte
(Milchviehhof 73, Eisenmine 90, Steinbruch 56, Holzfaellerhuette 51) - alles vom Spiel, nichts geschaetzt.
Ergebnis: data/research/erkundung_<zeit>.json + .png
"""

from selfaware import workspace as _workspace
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.game.ucp.befehl as kanal
import selfaware.runtime.live.erstes_spiel as E
import selfaware.services.wegkarte as W
from selfaware.game.ucp.laden import befehl
from selfaware.macro.standort import platzkarte, abstaende

D = os.path.join(_workspace.DATA)
SP = 1


def main():
    E.LEERE_KI = True
    E.gefecht_starten(100)
    befehl({"pause": True}, 0.5)
    G = E.runde_lesen()[2]
    berg = next(g for g in G.values() if g["besitzer"] == SP and g["typ"] == 41)
    bx, by = berg["x"] + 3, berg["y"] + 3
    r = 75
    x0, y0, x1, y1 = max(bx - r, 1), max(by - r, 1), min(bx + r, 398), min(by + r, 398)
    befehl({"rohstoffkarte": {"x0": x0, "y0": y0, "x1": x1, "y1": y1}}, 20.0, bis="ROHSTOFFKARTE")
    karte = open(os.path.join(kanal.ABZUG, "rohstoffe.txt"), encoding="utf-8").read().splitlines()[1:]
    baeume = []
    for z in open(os.path.join(kanal.ABZUG, "baeume.txt"), encoding="utf-8").read().splitlines()[1:]:
        a = z.split()
        if len(a) >= 9 and 1 <= int(a[1]) <= 4 and int(a[6]) > 0 and x0 <= int(a[3]) <= x1 and y0 <= int(a[4]) <= y1:
            baeume.append((int(a[3]), int(a[4]), int(a[6])))
    k = W.holen(x0, y0, x1, y1)
    plaetze = {name: platzkarte(m, g, x0, y0, x1, y1) for name, m, g in
               (("hof", 73, 10), ("mine", 90, 4), ("steinbruch", 56, 6), ("holzfaeller", 51, 3))}
    feld = {(x0 + i, y0 + j): c for j, z in enumerate(karte) for i, c in enumerate(z)}
    stein = [p for p, c in feld.items() if c == "b"]
    eisen = [p for p, c in feld.items() if c == "i"]
    vom_berg = abstaende(k, [(bx, by + 5), (bx - 4, by + 5), (bx + 4, by + 5)])
    def naechste(liste):
        werte = sorted((vom_berg.get(p, 9999), p) for p in liste)
        return werte[0] if werte else None
    erg = {"bergfried": (bx, by), "fenster": (x0, y0, x1, y1), "baeume": len(baeume),
           "holz_im_umkreis": sum(r2 for _, _, r2 in baeume),
           "naechster_baum": naechste([(x, y) for x, y, _ in baeume]), "naechster_stein": naechste(stein),
           "naechstes_eisen": naechste(eisen), "plaetze": {n: len(v) for n, v in plaetze.items()},
           "naechster_hofplatz": naechste(list(plaetze["hof"])), "naechster_minenplatz": naechste(list(plaetze["mine"])),
           "naechster_steinbruch": naechste(list(plaetze["steinbruch"]))}
    # Wald-Haufen: Baeume im Umkreis 6 eines Baums zaehlen, dichteste Stellen
    dicht = sorted(((sum(r2 for x2, y2, r2 in baeume if abs(x2 - x) <= 6 and abs(y2 - y) <= 6), (x, y)) for x, y, _ in baeume),
                   reverse=True)
    wald, gesehen = [], []
    for n, p in dicht:
        if all(max(abs(p[0] - q[0]), abs(p[1] - q[1])) > 12 for q in gesehen):
            gesehen.append(p)
            wald.append({"mitte": p, "holzeinheiten": n, "weg_vom_berg": vom_berg.get(p)})
        if len(wald) >= 6:
            break
    erg["wald"] = wald
    stempel = time.strftime("%Y%m%d_%H%M%S")
    json.dump(erg, open(os.path.join(D, "erkundung_%s.json" % stempel), "w", encoding="utf-8"), indent=1, default=str)
    zeichne(k, feld, baeume, plaetze, (bx, by), wald, os.path.join(D, "erkundung_%s.png" % stempel))
    for kk, v in erg.items():
        if kk not in ("wald",):
            print(kk, v)
    for w in wald:
        print("WALD", w)
    print("Daten:", os.path.join(D, "erkundung_%s.json" % stempel))


def zeichne(k, feld, baeume, plaetze, berg, wald, pfad, zelle=5):
    from PIL import Image, ImageDraw
    x0, y0, x1, y1 = k["x0"], k["y0"], k["x1"], k["y1"]
    img = Image.new("RGB", ((x1 - x0 + 1) * zelle, (y1 - y0 + 1) * zelle + 24), (240, 228, 200))
    d = ImageDraw.Draw(img)
    farbe = {"b": (150, 150, 160), "i": (70, 90, 200), "G": (150, 200, 120), "w": (80, 140, 220), "x": (80, 140, 220),
             "#": (60, 60, 60), "B": (120, 80, 60), "o": (20, 20, 20)}
    for (x, y), c in feld.items():
        if c in farbe:
            d.rectangle([(x - x0) * zelle, (y - y0) * zelle, (x - x0 + 1) * zelle - 1, (y - y0 + 1) * zelle - 1], fill=farbe[c])
    for x, y, r in baeume:
        d.ellipse([(x - x0) * zelle, (y - y0) * zelle, (x - x0 + 1) * zelle, (y - y0 + 1) * zelle], fill=(30, 110, 40))
    for w in wald:
        x, y = w["mitte"]
        d.ellipse([(x - x0 - 6) * zelle, (y - y0 - 6) * zelle, (x - x0 + 7) * zelle, (y - y0 + 7) * zelle], outline=(0, 90, 0), width=2)
    bx, by = berg
    d.rectangle([(bx - x0 - 3) * zelle, (by - y0 - 3) * zelle, (bx - x0 + 4) * zelle, (by - y0 + 4) * zelle], outline=(200, 0, 0), width=3)
    d.text((4, (y1 - y0 + 1) * zelle + 6), "rot: Bergfried  gruen Punkte: Baeume (Kreise: dichteste Waelder)  grau: Stein  "
           "blau: Eisen/Wasser  hellgruen: Gruenland  dunkel: gesperrt", fill=(0, 0, 0))
    img.save(pfad)


if __name__ == "__main__":
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
