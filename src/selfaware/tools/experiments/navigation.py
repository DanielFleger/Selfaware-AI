# -*- coding: utf-8 -*-
"""M9 Navigation: jeden Kamera-Befehl einzeln ausloesen, Felder vorher/nachher, Bild dazu.

Befehle (logik.lua, 30.09.2026):
  {"kamera": [x, y]}             auf eine Kartenstelle springen
  {"leiste": true}               Leiste unten weg/zurueck (Tab)
  {"drehen": "rechts"|"links"}   einen Schritt drehen (auch 0/2/4/6)
  {"grundriss": true|false}      abflachen (Leertaste, Rechtsklick links)
  {"absenken": true|false}       abgesenkte Ansicht (Rechtsklick unten)
  {"zoom": "raus"|"rein"}        Zoom (Rechtsklick rechts, Strg+Hoch)

Vorher festgelegt: ein Schritt gilt nur, wenn sein Feld sich wie erwartet aendert UND
das Bild sich sichtbar unterscheidet (Anteil geaenderter Bildpunkte). Zu jedem Schritt
gehoert der Rueckweg; am Ende muss jedes Feld wieder auf dem Ausgangswert stehen
(ausser der Kamerastelle). Jeder Schalter geht vom echten Startzustand ins Gegenteil.

Aufruf:  uv run python -m selfaware.tools.experiments.navigation
"""

from selfaware import workspace as _workspace
import io, json, os, sys, time

from selfaware.game.ucp.laden import befehl, peek, SPIEL, BILDER

FELDER = {"kameraX": 0x021AEC74, "kameraY": 0x021AEC78, "hoehe": 0x021AEC60, "breite": 0x021AEC64,
          "zoom": 0x021AEC68, "drehung": 0x01FE7AA4, "grundriss": 0x01FE7AD4,
          "absenkung": 0x01FE7AC4, "menuereiter": 0x01FE7D20, "ansicht": 0x01FE7D1C}
# absenkung: refreshCertainTileMap_old - das Feld davor (0x01FE7AC0) ist nur ein Auftrag,
# den das Spiel sofort verbraucht (gemessen 23:45: Modul las 3, zwei Sekunden spaeter 0).

def felder():
    return {k: peek(a)[0] for k, a in FELDER.items()}

def bild(name, flaeche="karte", vorsilbe="m9"):
    """Speicherbild: "karte" = Kartenflaeche, "menue" = Flaeche mit der Leiste unten."""
    from PIL import Image
    befehl({"bild": flaeche}, 2.0)
    im = Image.open(os.path.join(SPIEL, "ucp", "villagestudio", "vs_%s.bmp" % flaeche)).convert("RGB")
    os.makedirs(BILDER, exist_ok=True)
    im.save(os.path.join(BILDER, "%s_%s_%s.png" % (vorsilbe, name, flaeche)))
    return im

def anteil(a, b):
    """Anteil geaenderter Bildpunkte im sichtbaren Teil (oben links, hoechstens 2200 x 1150)."""
    from PIL import ImageChops
    box = (0, 0, min(2200, a.width, b.width), min(1150, a.height, b.height))
    d = ImageChops.difference(a.crop(box), b.crop(box)).convert("L").point(lambda v: 255 if v > 16 else 0)
    return sum(d.histogram()[255:]) / float(box[2] * box[3])

def schritte(f0):
    """Jeder Schalter vom ECHTEN Startzustand ins Gegenteil und zurueck (erster Lauf 23:44
    zeigte: Grundriss und Zoom standen schon auf an/raus - "an" aenderte dann nichts)."""
    g = [False, True][f0["grundriss"] == 0]          # Gegenteil des Starts
    z = ["raus", "rein"][f0["zoom"] == 1]
    return [  # (Name, Befehl, Feld, das sich aendern muss, Bildflaeche)
        ("kamera", {"kamera": [162, 104]}, "kameraX", "karte"),
        ("leiste_um", {"leiste": True}, "menuereiter", "menue"),
        ("leiste_zurueck", {"leiste": True}, "menuereiter", "menue"),
        ("drehen_rechts", {"drehen": "rechts"}, "drehung", "karte"),
        ("drehen_links", {"drehen": "links"}, "drehung", "karte"),
        ("grundriss_um", {"grundriss": g}, "grundriss", "karte"),
        ("grundriss_zurueck", {"grundriss": not g}, "grundriss", "karte"),
        ("absenken_an", {"absenken": True}, "absenkung", "karte"),
        ("absenken_aus", {"absenken": False}, "absenkung", "karte"),
        ("zoom_um", {"zoom": z}, "zoom", "karte"),
        ("zoom_zurueck", {"zoom": ["raus", "rein"][z == "raus"]}, "zoom", "karte"),
    ]

def main():
    s = time.strftime("%H%M%S")
    bericht = {"zeit": time.strftime("%Y-%m-%d %H:%M:%S"), "schritte": []}
    f0 = felder()
    zuletzt = {"karte": bild("00_ausgang"), "menue": bild("00_ausgang", "menue")}
    bericht["ausgang"] = f0
    print("Ausgang:", f0, flush=True)
    fa = f0
    for i, (name, cmd, feld, flaeche) in enumerate(schritte(f0), 1):
        antwort = befehl(cmd, 1.5)
        time.sleep(0.5)
        fn = felder(); bn = bild("%02d_%s" % (i, name), flaeche)
        p = anteil(zuletzt[flaeche], bn)
        zuletzt[flaeche] = bn
        geaendert = {k: [fa[k], fn[k]] for k in fn if fa[k] != fn[k]}
        gilt = fa[feld] != fn[feld] and p > 0.001
        print("%-15s %-6s Feld %s: %s -> %s | Bild %.1f %% anders | alle Aenderungen %s | %s" % (
            name, "GILT" if gilt else "NICHT", feld, fa[feld], fn[feld], 100 * p, geaendert,
            " / ".join(antwort)), flush=True)
        bericht["schritte"].append({"name": name, "befehl": cmd, "feld": feld, "vorher": fa, "nachher": fn,
                                    "bild_anders": p, "gilt": gilt, "antwort": antwort})
        fa = fn
    rest = {k: [f0[k], fa[k]] for k in f0 if f0[k] != fa[k] and k not in ("kameraX", "kameraY")}
    print("Rueckweg: %s" % ("alles wieder auf Ausgang" if not rest else "NICHT zurueck: %s" % rest))
    bericht["nicht_zurueck"] = rest
    io.open(os.path.join(_workspace.DATA, 'navigation_%s.json' % s),
            "w", encoding="utf-8").write(json.dumps(bericht, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
