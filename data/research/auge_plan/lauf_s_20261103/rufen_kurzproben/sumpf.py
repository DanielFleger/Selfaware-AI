# -*- coding: utf-8 -*-
"""P059 direkt: Sumpf-Bit auf 7x7 Feldern setzen, die Funktion des Spiels rufen, MacroLayer & 0x3f lesen, Bit zuruecknehmen. Das Spiel steht."""
import json
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.experiments.spielcode_rufen import Rufer
from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz

K = Feldkarte.laden(feldliste=FELDLISTE)
TM = K.struktur("DAT_TileMapState")[0]
lo = K.adresse("DAT_TileMapState", "LogicLayer[]")
ma = K.adresse("DAT_TileMapState", "MacroLayer[]")
bau = K.adresse("DAT_TileMapState", "BuildingLayer[]")
# Feldnummer aus x, y: Das Spiel rechnet ueber translationMatrix[y].addXgetTile + x
tr = K.adresse("DAT_ViewportRenderState", "translationMatrix[]")
print("Ebenen", lo, ma, tr)
X, Y = 160, 245


def kachel(r, x, y):
    return r.lies_i(tr[0] + y * tr[2]) + x


with Rufer(pid_der_instanz(2)) as r:
    felder = [(i, j) for j in range(-1, 8) for i in range(-1, 8)]
    alt_l = {(i, j): r.lies_i(lo[0] + kachel(r, X + i, Y + j) * (lo[2] or lo[1])) for i, j in felder}
    alt_m = {(i, j): r.lies_i(ma[0] + kachel(r, X + i, Y + j) * (ma[2] or ma[1]), ma[1]) for i, j in felder}
    print("MacroLayer vorher & 0x3f:")
    for j in range(-1, 8):
        print("  ", [alt_m[(i, j)] & 0x3f for i in range(-1, 8)])
    for i in range(7):
        for j in range(7):
            a = lo[0] + kachel(r, X + i, Y + j) * (lo[2] or lo[1])
            r.setze_i(a, (alt_l[(i, j)] | 0x20000000) & 0xFFFFFFFF if False else alt_l[(i, j)] | 0x20000000)
    r.rufe(0x004fdb00, 0x20000000, 0, 0, this=TM)
    neu = {(i, j): r.lies_i(ma[0] + kachel(r, X + i, Y + j) * (ma[2] or ma[1]), ma[1]) for i, j in felder}
    print("MacroLayer danach & 0x3f (Sumpf 7x7 ab Zeile, Spalte 2):")
    for j in range(-1, 8):
        print("  ", [neu[(i, j)] & 0x3f for i in range(-1, 8)])
    for (i, j), v in alt_l.items():
        r.setze_i(lo[0] + kachel(r, X + i, Y + j) * (lo[2] or lo[1]), v)
    for (i, j), v in alt_m.items():
        r.setze_i(ma[0] + kachel(r, X + i, Y + j) * (ma[2] or ma[1]), v, ma[1])
    print("zurueck gestellt")
