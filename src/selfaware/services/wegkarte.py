# -*- coding: utf-8 -*-
"""Alle moeglichen Wege sichtbar machen (Daniel 06.10. 20:14/20:15: "nicht nur Laufwege sichtbar, sondern alle moeglichen
Wege durch Gebaeude durch").

Quelle ist die Weg-Ebene des Spiels selbst (PathLinkageLayer): je Feld ein Byte, jedes Bit erlaubt einen Schritt zum
Nachbarn. Bits im Uhrzeigersinn 1 N (y-1), 2 NO, 4 O (x+1), 8 SO, 0x10 S, 0x20 SW, 0x40 W, 0x80 NW
(abgelesen aus updateSeparateAreaTileMap, research/native/dekomp_wegsuche.c). Die Regel dahinter (research/native/dekomp_weglinks2.c):
  - gerade nie auf ein Gebaeudefeld;
  - schraeg an einer Ecke vorbei nur verboten, wenn BEIDE geraden Nachbarn "Eckensperren" sind (Gebaeudeart mit
    BuildingDefinedData +0x1774 = 1: Soeldnerposten, Kaserne, Waffenlager, Muehle, Kapelle, Bergfriede, Torhaeuser,
    Tuerme, Aussenposten - abgelesen 06.10. aus der Referenz-exe).

Aufruf als Werkzeug: uv run python -m selfaware.services.wegkarte x0 y0 x1 y1 [bild.png]  (holt die Karte aus dem laufenden Spiel)
"""

from selfaware import workspace as _workspace
import os
import re
import sys
from collections import deque

HIER = os.path.dirname(os.path.abspath(__file__))

from selfaware.game.ucp.befehl import ABZUG

RICHTUNG = {1: (0, -1), 2: (1, -1), 4: (1, 0), 8: (1, 1), 0x10: (0, 1), 0x20: (-1, 1), 0x40: (-1, 0), 0x80: (-1, -1)}
NAME = {1: "N", 2: "NO", 4: "O", 8: "SO", 0x10: "S", 0x20: "SW", 0x40: "W", 0x80: "NW"}
GEGEN = {1: 0x10, 2: 0x20, 4: 0x40, 8: 0x80, 0x10: 1, 0x20: 2, 0x40: 4, 0x80: 8}
SCHRAEG = (2, 8, 0x20, 0x80)
ECKSPERRE = {8, 9, 11, 34, 36} | set(range(40, 49)) | set(range(70, 80)) | {106}
KURZ = {1: "Hue", 3: "Hlz", 9: "Kas", 10: "Lag", 11: "Waf", 13: "Sch", 16: "Ger", 26: "Mkt", 32: "Apf", 33: "Mil",
        41: "Berg", 55: "Feuer", 71: "Tuer", 72: "Tuer", 73: "Tuer"}


def kurzname(typ):
    """Kurzname je Gebaeudeart; unbekannte aus data/research/enums_einheit_gebaeude.txt (BT_...), sonst die Nummer."""
    if typ in KURZ:
        return KURZ[typ]
    if not _BT:
        pfad = os.path.join(_workspace.DATA, 'enums_einheit_gebaeude.txt')
        if os.path.exists(pfad):
            for m in re.finditer(r"BT_([A-Z0-9_]+)\s*[=:]\s*(-?\d+)", open(pfad, encoding="utf-8").read()):
                _BT.setdefault(int(m.group(2)), m.group(1)[:5].title())
    return _BT.get(typ, "T%s" % typ)


_BT = {}


def lesen(pfad=None):
    """abzug/wegkarte.txt -> {"tick", "x0", "y0", "x1", "y1", "f": {(x, y): (link, geb, gebiet, logik, hoehe, typ)}}"""
    pfad = pfad or os.path.join(ABZUG, "wegkarte.txt")
    zeilen = open(pfad, encoding="utf-8").read().splitlines()
    kopf = {k: int(v) for k, v in re.findall(r"(\w+)=(\d+)", zeilen[0])}
    kopf["tick"] = int(re.search(r"tick (\d+)", zeilen[0]).group(1))
    f = {}
    for j, z in enumerate(zeilen[1:]):
        for i, t in enumerate(z.split()):
            a = t.split(":")
            f[(kopf["x0"] + i, kopf["y0"] + j)] = (int(a[0], 16), int(a[1]), int(a[2]), int(a[3], 16), int(a[4]),
                                                   int(a[5]) if len(a) > 5 else -1)
    kopf["f"] = f
    return kopf


def holen(x0, y0, x1, y1):
    from selfaware.game.ucp.laden import befehl
    befehl({"wegkarte": {"x0": x0, "y0": y0, "x1": x1, "y1": y1}}, 1.5, bis="WEGKARTE")
    return lesen()


def begehbar(k, xy):
    v = k["f"].get(xy)
    return v is not None and v[0] != 0


def eckdurchgaenge(k):
    """Schraege Schritte, bei denen BEIDE geraden Nachbarn nicht begehbar sind - der Weg geht genau zwischen zwei
    Ecken durch. Gibt [(von, nach, bit)]."""
    aus = []
    for (x, y), v in k["f"].items():
        for bit in SCHRAEG:
            if v[0] & bit:
                dx, dy = RICHTUNG[bit]
                a, b = (x + dx, y), (x, y + dy)
                if a in k["f"] and b in k["f"] and not begehbar(k, a) and not begehbar(k, b):   # Bildrand zaehlt nicht
                    aus.append(((x, y), (x + dx, y + dy), bit))
    return aus


def weg(k, start, ziel, box=None):
    """Kuerzester Weg ueber die erlaubten Schritte (Breitensuche, schraeg zaehlt 1). box = (x0, y0, x1, y1) begrenzt die
    Suche, damit 'drumherum' nicht als 'hindurch' zaehlt. Gibt die Feldliste oder None."""
    if not begehbar(k, start):
        return None
    vor = {start: None}
    q = deque([start])
    while q:
        p = q.popleft()
        if p == ziel:
            aus = []
            while p is not None:
                aus.append(p)
                p = vor[p]
            return aus[::-1]
        link = k["f"][p][0]
        for bit, (dx, dy) in RICHTUNG.items():
            if link & bit:
                n = (p[0] + dx, p[1] + dy)
                if n in vor or n not in k["f"]:
                    continue
                if box and not (box[0] <= n[0] <= box[2] and box[1] <= n[1] <= box[3]):
                    continue
                vor[n] = p
                q.append(n)
    return None


def gebaeude_typen_aus(k, sonst=None):
    """Gebaeudenummer -> Art direkt aus der Wegkarte (6. Feld, seit 06.10. 20:30); fehlt es, aus gebaeude.txt."""
    aus = {v[1]: v[5] for v in k["f"].values() if v[1] and v[5] >= 0}
    return aus or (sonst if sonst is not None else gebaeude_typen())


def gebaeude_typen():
    """Gebaeudenummer -> Typ aus abzug/gebaeude.txt (kommt mit jedem Lagebild)."""
    pfad = os.path.join(ABZUG, "gebaeude.txt")
    if not os.path.exists(pfad):
        return {}
    aus = {}
    for z in open(pfad, encoding="utf-8").read().splitlines()[1:]:
        a = z.split()
        if len(a) >= 3:
            aus[int(a[0])] = int(a[2])
    return aus


def zeichnen(k, pfad, typen=None, spuren=None, wege=None, zelle=16, titel=""):
    """Bild: Gebaeude farbig (Eckensperre dunkel umrandet), begehbare Felder hell, alle erlaubten Schritte als Striche,
    Eckdurchgaenge dick rot. spuren = {name: [(x, y), ...]} gelaufene Wege, wege = [[(x, y), ...]] berechnete."""
    from PIL import Image, ImageDraw
    typen = typen or {}
    x0, y0, x1, y1 = k["x0"], k["y0"], k["x1"], k["y1"]
    rand = 22
    b, h = (x1 - x0 + 1) * zelle, (y1 - y0 + 1) * zelle
    img = Image.new("RGB", (b + 2 * rand, h + 2 * rand + 18), (250, 248, 240))
    d = ImageDraw.Draw(img)

    def mitte(x, y):
        return rand + (x - x0) * zelle + zelle // 2, rand + (y - y0) * zelle + zelle // 2

    farben = {}
    palette = [(214, 150, 90), (120, 160, 210), (160, 200, 120), (200, 120, 170), (230, 200, 90), (130, 200, 200),
               (190, 160, 230), (240, 140, 120)]
    for (x, y), (link, geb, gebiet, logik, hoehe, _t) in k["f"].items():
        px, py = rand + (x - x0) * zelle, rand + (y - y0) * zelle
        if geb:
            typ = typen.get(geb, -1)
            c = farben.setdefault(typ, palette[len(farben) % len(palette)])
            d.rectangle([px, py, px + zelle - 1, py + zelle - 1], fill=c,
                        outline=(60, 40, 40) if typ in ECKSPERRE else c)
        elif link == 0:
            d.rectangle([px, py, px + zelle - 1, py + zelle - 1], fill=(120, 120, 120))
        if (x - x0) % 5 == 0 and (y - y0) % 5 == 0:
            d.point((px, py), fill=(0, 0, 0))
    for (x, y), v in k["f"].items():                 # Striche: beide Richtungen grau, Einbahn orange mit Punkt am Start
        for bit in RICHTUNG:
            if not v[0] & bit:
                continue
            dx, dy = RICHTUNG[bit]
            n = (x + dx, y + dy)
            zurueck = n in k["f"] and k["f"][n][0] & GEGEN[bit]
            a, e = mitte(x, y), mitte(*n)
            if zurueck and bit in (4, 8, 0x10, 0x20):
                d.line([a, e], fill=(175, 170, 160), width=1)
            elif not zurueck and n in k["f"]:
                d.line([a, e], fill=(240, 150, 30), width=2)
                d.ellipse([a[0] - 2, a[1] - 2, a[0] + 2, a[1] + 2], fill=(240, 150, 30))
    for a, e, bit in eckdurchgaenge(k):
        d.line([mitte(*a), mitte(*e)], fill=(220, 30, 30), width=3)
    for w in wege or []:
        d.line([mitte(*p) for p in w], fill=(30, 90, 220), width=3)
    for name, sp in (spuren or {}).items():
        if len(sp) > 1:
            d.line([mitte(*p) for p in sp], fill=(20, 150, 60), width=2)
    gesehen = set()
    for (x, y), v in sorted(k["f"].items(), key=lambda t: (t[0][1], t[0][0])):
        if v[1] and v[1] not in gesehen:
            gesehen.add(v[1])
            px, py = rand + (x - x0) * zelle + 1, rand + (y - y0) * zelle
            d.text((px, py), "%s%d" % (kurzname(typen.get(v[1])), v[1]), fill=(0, 0, 0))
    for i in range(0, x1 - x0 + 1, 5):
        d.text((rand + i * zelle, 4), str(x0 + i), fill=(80, 80, 80))
    for j in range(0, y1 - y0 + 1, 5):
        d.text((2, rand + j * zelle), str(y0 + j), fill=(80, 80, 80))
    d.text((rand, h + 2 * rand), titel or "Tick %d  grau=gesperrt  Striche=Schritte  orange=nur in eine Richtung (Punkt=Start)  rot=Eckdurchgang  "
           "dunkler Rand=Eckensperre" % k["tick"], fill=(0, 0, 0))
    img.save(pfad)
    return pfad


if __name__ == "__main__":
    import selfaware.game.ucp.befehl as kanal
    x0, y0, x1, y1 = map(int, sys.argv[1:5])
    ziel = sys.argv[5] if len(sys.argv) > 5 else os.path.join(_workspace.DATA, 'wegkarte.png')
    kanal.belege()
    try:
        from selfaware.runtime.live.erstes_spiel import runde_lesen
        runde_lesen()                       # schreibt abzug/gebaeude.txt
        k = holen(x0, y0, x1, y1)
    finally:
        kanal.freigeben()
    print(zeichnen(k, ziel, gebaeude_typen()), "Eckdurchgaenge:", len(eckdurchgaenge(k)))


def einbahn(k):
    """Schritte, die nur in eine Richtung gehen: [(von, nach, bit)]."""
    aus = []
    for (x, y), v in k["f"].items():
        for bit, (dx, dy) in RICHTUNG.items():
            n = (x + dx, y + dy)
            if v[0] & bit and n in k["f"] and not k["f"][n][0] & GEGEN[bit]:
                aus.append(((x, y), n, bit))
    return aus
