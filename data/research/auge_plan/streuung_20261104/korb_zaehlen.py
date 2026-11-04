# -*- coding: utf-8 -*-
"""Neuzaehlung der Mauerfelder fuer die Oberflaeche (P312): Je Feldnummer genau einmal, ohne x und y.

Die alte Zaehlung (korb_klassen.py) ging x und y von 0 bis 399 durch. Ausserhalb der Raute liefert die Zeilentabelle die Nummer eines anderen Feldes, so zaehlte sie 40.002 von 80.400 Feldnummern doppelt oder dreifach.
Die Rechnung ist der Mauerzweig von getHeightAtTileIncludingOwnersBuildings (004fff10): PathConnectionLayer ungleich 0, MiscDisplayLayer ohne 0x1000, Logik mit 0x100. Der Besitzer ist hier immer der Mauerbesitzer.
Die Rechnung wird zuerst an der Szene korb_g gegen die direkten Aufrufe gehalten, dann erst gezaehlt. Ausgabe: korb_zaehlung.txt.
Aufruf: python korb_zaehlen.py [Aufzeichnung mit KI-Burgen unter laeufe/]
"""
import collections
import glob
import json
import os
import sys

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
from selfaware.tools.analysis.auge_auswertung import Aufzeichnung  # noqa: E402
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte  # noqa: E402

KACHELN = 80400


def schichten_lesen(pfad, k, erster=False):
    """Der erste oder der letzte saubere Stand der Karte."""
    auf = Aufzeichnung(pfad)
    i = auf.namen.index("DAT_TileMapState")
    be = auf.bereiche[i][1]
    stand, takt = None, None
    for r, p, _ in auf.staende():
        if r.bereich == i and r.rein:
            stand, takt = bytes(p), r.takt
            if erster:
                break
    if stand is None:
        raise SystemExit("Kein sauberer Stand der Karte in " + pfad)

    def schicht(name, t):
        return np.frombuffer(stand, dtype=t, count=KACHELN, offset=k.adresse("DAT_TileMapState", name)[0] - be)
    return takt, {"logik": schicht("LogicLayer[]", "<u4"), "weg": schicht("PathConnectionLayer[]", "<u2"), "misc": schicht("MiscDisplayLayer[]", "<u2"), "hoehe": schicht("HeightLayer[]", "u1")}


def oberflaeche_mauer(s):
    """Mauerzweig der Pruefung, je Feldnummer."""
    return (s["weg"] != 0) & ((s["misc"] & 0x1000) == 0) & ((s["logik"] & 0x100) != 0)


def mehrfach(zeilen):
    """Wie oft trifft die alte Abtastung (x und y von 0 bis 399, Feldnummer im gueltigen Bereich) jede Feldnummer?"""
    treffer = np.zeros(KACHELN, dtype=int)
    for y in range(400):
        feld = int(zeilen[y]) + np.arange(400)
        np.add.at(treffer, feld[(feld >= 0) & (feld < KACHELN)], 1)
    return int((treffer == 1).sum()), int((treffer == 2).sum()), int((treffer >= 3).sum()), int((treffer == 0).sum())


def main():
    k = Feldkarte.laden(feldliste=FELDLISTE)
    aus = []
    a1, a2, a3, a0 = mehrfach(np.load(os.path.join(HIER, "zeilen.npy")))
    aus.append("Alte Abtastung, Feldnummern getroffen: einmal %d, zweimal %d, dreimal oder oefter %d, nie %d. Mehrfach zusammen %d von %d" % (a1, a2, a3, a0, a2 + a3, KACHELN))
    # Gegenprobe der Rechnung an den direkten Aufrufen der Szene korb_g
    pfad = sorted(glob.glob(os.path.join(HIER, "..", "laeufe", "lauf_s_*_korb_g.auge")), key=os.path.getmtime)[-1]
    takt, s = schichten_lesen(pfad, k, erster=True)
    zeilen = np.load(os.path.join(HIER, "zeilen.npy"))
    ziele = [json.loads(z) for z in open(os.path.join(HIER, "lauf_korb_g.log"), encoding="utf-8", errors="replace") if z.startswith('{"schritt": "korb_ziele')][-1]["ziele"]
    ja = oberflaeche_mauer(s)
    gleich, ungleich = 0, []
    for z in ziele:
        if z["aussen"] or not z["logik"] & 0x100 or z["gebaeude"]:
            continue
        feld = int(zeilen[z["y"]]) + z["x"]
        if bool(ja[feld]) == (z["ober"] > 0):
            gleich += 1
        else:
            ungleich.append((z["art"], z["x"], z["y"], z["ober"], bool(ja[feld])))
    aus.append("Gegenprobe an korb_g, erster Stand Takt %s: Rechnung gleich dem direkten Aufruf auf %d Mauerfeldern, ungleich %s" % (takt, gleich, ungleich))
    if ungleich or not gleich:
        print(chr(10).join(aus))
        raise SystemExit("Die Rechnung stimmt nicht mit dem Spiel ueberein, keine Zaehlung")
    # Die Zaehlung
    pfad = os.path.join(HIER, "..", "laeufe", sys.argv[1] if len(sys.argv) > 1 else "lauf_k_20261102_233313_danach.auge")
    takt, s = schichten_lesen(pfad, k)
    ja = oberflaeche_mauer(s)
    c = collections.Counter()
    for feld in np.nonzero((s["logik"] & 0x100) != 0)[0]:
        l = int(s["logik"][feld])
        name = "Treppe" if l & 0x800 else "Zinne ohne Bit 0x400000" if l & 0x200 and not l & 0x400000 else "Zinne mit Bit 0x400000" if l & 0x200 else "Mauer"
        c[(name, "ja" if ja[feld] else "nein")] += 1
    aus.append("Zaehlung in %s, letzter Stand Takt %s, je Feldnummer einmal:" % (os.path.basename(pfad), takt))
    aus += ["  %s: %s %d" % (n, a, z) for (n, a), z in sorted(c.items())]
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "korb_zaehlung.txt"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
