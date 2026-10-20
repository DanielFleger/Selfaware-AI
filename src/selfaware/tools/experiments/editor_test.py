# -*- coding: utf-8 -*-
"""Testen im Karteneditor (Daniel 17.10.2026: "selbst ansteuern, notieren wie gemacht ins Handbuch unter Testing, dann
moeglichst schlau testen"). Statt Schadensraten aus alten Partien zu schaetzen, wird im Editor ("Eigene Szenarien ->
Neue Karte") ein kontrollierter Aufbau gesetzt: eigene Assassine, feindliche Schuetzen, Gebaeude dazwischen - jeder
Abstand frei waehlbar, beliebig oft wiederholbar.

Menue-Weg ohne Klick: das Modul ruft die Knopf-Handler des Spiels (Befehl "knopf" in ucp/villagestudio/logik.lua,
eingebaut 17.10.; Adressen aus VillageStudio/lib/funktionen.csv). Jeder Schritt wird an der Menueansicht
(currentMenuViewType 0x01FE7D1C) und an einem Bild geprueft.

Aufruf:
  uv run python -m selfaware.tools.experiments.editor_test ansicht                      aktuelle Menueansicht
  uv run python -m selfaware.tools.experiments.editor_test bild <name>                  Bild nach data/research/editor_bilder/<name>.png
  uv run python -m selfaware.tools.experiments.editor_test schritte '<json-liste>' [bildname]   Befehle einzeln absetzen, nach jedem die Ansicht
"""

from selfaware import workspace as _workspace
import io
import json
import os
import re
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.game.ucp.befehl as K

BILDER = os.path.join(_workspace.DATA, 'editor_bilder')
ANSICHT = 0x01FE7D1C


def peek(adr, worte=1):
    z = K.sende({"befehle": [{"peek": adr, "worte": worte}]}, 3.0, bis="PEEK 0x%08X" % adr)
    for x in reversed(z):
        m = re.search(r"PEEK 0x%08X: ([0-9A-F ]+)" % adr, x)
        if m:
            return [int(w, 16) for w in m.group(1).split()]
    return None


def ansicht():
    w = peek(ANSICHT)
    return w[0] if w else None


def bild(name, art="menue"):
    """Bild der Menue- oder Kartenflaeche. Das Spiel (hohe Rechtestufe) schreibt in seinen eigenen Ordner, von dort wird
    es als PNG nach data/research/editor_bilder kopiert (ein Pfad im Benutzer-Temp kam nicht an, 17.10.)."""
    rel = "ucp/villagestudio/test_%s.bmp" % name
    quelle = os.path.join(K.SPIEL, rel.replace("/", os.sep))
    if os.path.exists(quelle):
        os.remove(quelle)
    K.sende({"befehle": [{"bild": art, "datei": rel}]}, 5.0, bis="erste acht Pixel")
    groesse = -1
    for _ in range(100):                     # warten, bis die Datei fertig geschrieben ist (Groesse steht)
        time.sleep(0.15)
        g = os.path.getsize(quelle) if os.path.exists(quelle) else -1
        if g > 1000 and g == groesse:
            break
        groesse = g
    from PIL import Image
    os.makedirs(BILDER, exist_ok=True)
    ziel = os.path.join(BILDER, "%s.png" % name)
    Image.open(quelle).convert("RGB").save(ziel)
    return os.path.abspath(ziel)


def schritt(befehl, warte=1.2):
    z = K.sende({"befehle": [befehl]}, 3.0)
    time.sleep(warte)
    melde = [x for x in z if any(w in x for w in ("KNOPF", "MENUE", "HAUPTMENUE", "WARN", "Fehler"))]
    return melde, ansicht()


def main():
    was = sys.argv[1] if len(sys.argv) > 1 else "ansicht"
    if was == "ansicht":
        print("Ansicht", ansicht())
    elif was == "bild":
        print(bild(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "menue"))
    elif was == "schritte":
        for b in json.loads(sys.argv[2]):
            melde, a = schritt(b)
            print(json.dumps(b), "->", melde[-2:], "Ansicht", a, flush=True)
        if len(sys.argv) > 3:
            print("Bild:", bild(sys.argv[3]))


if __name__ == "__main__":
    main()
