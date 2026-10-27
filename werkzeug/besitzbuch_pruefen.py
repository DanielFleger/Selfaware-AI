# -*- coding: utf-8 -*-
"""B-273/B-275 Besitzbuch + Steh-Augen fuer alle Einheiten ohne Spiel pruefen (Soll vorher festgelegt; Faelle aus Partie 221355).
Aufruf: python besitzbuch_pruefen.py"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import besitzbuch as B


def raids_befehl(n):          # Absender-Modul "besitzbuch_pruefen.raids_befehl"
    B.merken({"befehle": [{"player": 1, "id": 1, "angriff": {"einheiten": [n], "ziel": 83}}]})


import types
_W = types.ModuleType("waechter_nachbau")                 # ein zweites Modul als Absender (Doppelbefehl zaehlt nur zwischen Modulen)
exec("import besitzbuch as B\ndef befehl(n):\n    B.merken({'angriff': {'einheiten': [n], 'lauf': [10, 10]}})\n", _W.__dict__)


def waechter_befehl(n):
    _W.befehl(n)


def L(t):
    return {219: {"besitzer": 2, "typ": 73, "x": 222, "y": 219, "zustand": 1},
            548: {"besitzer": 2, "typ": 75, "x": 190, "y": 141, "zustand": 1},
            900: {"besitzer": 3, "typ": 75, "x": 1, "y": 1, "zustand": 1}}


if __name__ == "__main__":
    zeilen = {}
    for t in (3830, 4000, 4140, 4300):
        raids_befehl(219)                       # jede Runde ein frischer Befehl - 219 bewegt sich trotzdem nicht
        zeilen[t] = B.steh_runde(t, L(t), 2, {73, 75})
    z = " | ".join(zeilen[4140])
    waechter_befehl(219)
    raids_befehl(219)                           # zwei Module in derselben Runde
    B.steh_runde(4500, L(4500), 2, {73, 75})
    faelle = [
        ("vor 300 Takten keine Zeile", zeilen[3830] == [] and zeilen[4000] == []),
        ("219: frischer Befehl, bewegt sich nicht - Modul und Ziel genannt", "STEHT 219" in z and "raids_befehl" in z
         and "Befehl frisch, sie bewegt sich trotzdem nicht" in z and "83" in z),
        ("548: KEIN Modul hat ihr je einen Befehl gegeben", "STEHT 548" in z and "KEIN Modul" in z),
        ("fremde Einheit (Spieler 3) meldet nichts", "STEHT 900" not in z),
        ("nicht jede Runde (4300 leer)", zeilen[4300] == []),
        ("Doppelbefehl zweier Module gezaehlt", B.DOPPELT.get(219) == 1),
    ]
    # Haende fuer jede Einheit: Schwertkaempfer 548 (Feldzug) bekommt einen Lauf, steht eine Runde spaeter am selben Feld mit
    # Laufziel = eigenes Feld -> BEFEHL ABGELEHNT; derselbe Befehl wird dann herausgefiltert, ein anderes Ziel geht durch
    def feldzug_lauf(n, p):
        return B.filtern({"befehle": [{"player": 1, "id": 2, "angriff": {"einheiten": [n], "lauf": list(p)}}]})
    LZ = lambda: {548: {"besitzer": 2, "typ": 75, "x": 190, "y": 141, "zustand": 1, "laufx": 190, "laufy": 141}}
    B.steh_runde(5000, LZ(), 2, {75})
    b1, _m = feldzug_lauf(548, (139, 182))
    B.merken(b1)
    abl = B.steh_runde(5100, LZ(), 2, {75})
    b2, m2 = feldzug_lauf(548, (139, 182))
    b3, m3 = feldzug_lauf(548, (170, 180))
    faelle += [("Schwertkaempfer: BEFEHL ABGELEHNT erkannt", any("BEFEHL ABGELEHNT 548" in z for z in abl)),
               ("derselbe abgelehnte Lauf wird nicht wiederholt", b2 is None and any("WIEDERHOLUNG VERHINDERT" in z for z in m2)),
               ("ein anderes Ziel geht durch", b3 is not None and b3["befehle"][0]["angriff"]["einheiten"] == [548] and not m3)]
    for name, ok in faelle:
        print("%s %s" % ("OK  " if ok else "ROT ", name))
    print("%d von %d gruen" % (sum(ok for _, ok in faelle), len(faelle)))
    sys.exit(0 if all(ok for _, ok in faelle) else 1)
