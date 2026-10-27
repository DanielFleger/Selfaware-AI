# -*- coding: utf-8 -*-
"""Augen fuer die eigenen Entscheidungen (Daniel 27.10. 22:24): STEHT-Zeile der Assassinen ohne Spiel pruefen.
Nachgestellt: Partie 221355, Assassine 217 steht 8 Felder neben Hopfenfarm 137 - die Zeile muss nach STEH_ERKLAER Takten kommen,
den Lenker-Zustand und die naechsten Ziele mit Grund nennen, nicht jede Runde wiederholen und nach einem Schritt neu zaehlen.
Aufruf: python steh_erklaerung_pruefen.py"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import assassinen as A


def neu():
    a = A.Einzeln.__new__(A.Einzeln)
    a.mitglieder, a._still, a._ablehnung = {217}, {}, {}
    a.lordtrupp, a.stapel = {"mitglieder": set(), "phase": None}, {"mitglieder": set(), "ziel": None}
    a.flucht, a.entdeckt, a.ziel, a.jagd, a.warte = {}, {}, {}, {}, {}
    return a


def L(x=279, zustand=1):
    return {217: {"x": x, "y": 283, "zustand": zustand, "leben": 12500}}


if __name__ == "__main__":
    a = neu()
    a._ablehnung[217] = {137: (31, 8, "nicht erreichbar (Wegkarte: anderes Gebiet)"), 142: (3, 75, "GEWAEHLT")}
    zeilen = {}
    for t in (11000, 11200, 11300, 11400, 11700):
        a.jetzt = t
        zeilen[t] = a._steh_erklaerung(L(), {})
    a.jetzt = 11800
    weg = a._steh_erklaerung(L(x=280, zustand=101), {})
    a.jetzt = 11900
    neu_z = a._steh_erklaerung(L(x=280), {})
    z = zeilen[11300][0] if zeilen[11300] else ""
    faelle = [
        ("vor 300 Takten keine Zeile", zeilen[11000] == [] and zeilen[11200] == []),
        ("nach 300 Takten: STEHT 217 mit Zustand und Grund", z.startswith("STEHT 217 seit 300 Takten") and "ohne Auftrag" in z
         and "Hopfenfarm" in z and "nicht erreichbar" in z),
        ("naechstes Ziel zuerst (Hopfenfarm 8 Felder vor dem gewaehlten Holzfaeller)", z.find("Hopfenfarm") < z.find("GEWAEHLT")),
        ("nicht jede Runde (11400 leer), wieder nach 300 Takten (11700)", zeilen[11400] == [] and len(zeilen[11700]) == 1),
        ("nach Bewegung neu gezaehlt", weg == [] and neu_z == []),
    ]
    for name, ok in faelle:
        print("%s %s" % ("OK  " if ok else "ROT ", name))
    print("%d von %d gruen" % (sum(ok for _, ok in faelle), len(faelle)))
    sys.exit(0 if all(ok for _, ok in faelle) else 1)
