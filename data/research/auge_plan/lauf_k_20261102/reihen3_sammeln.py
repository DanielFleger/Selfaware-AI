# -*- coding: utf-8 -*-
"""B-142 (Ansatz verworfen: Die Felder von attackInfo gelten nur fuer den ersten Block, je Spieler x 0x177BC liegen dort Feldlisten): Dritter Durchgang fuer Lauf K: der Angriffsblock je Spieler. attackInfo an der Grundadresse ist Platz 0, belegt sind Grundadresse + Spieler * 0x177BC (recomputeAttackInfo). Speichert nach reihen3.pkl (bleibt lokal).

Aufruf aus dem Arbeitsbaum: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/reihen3_sammeln.py <basis>
"""
import collections
import os
import pickle
import struct
import sys

from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

HIER = os.path.dirname(os.path.abspath(__file__))
k = Feldkarte.laden(feldliste=FELDLISTE)
SCHRITT = 0x177BC
FELDER = {f: k.adresse("DAT_TroopValueState", "attackInfo." + f)[0] for f in ("attacker", "macemenTribeCount", "tentPoints", "moat2", "wide3", "spearmenAndMacemen", "pikemenSwordsmenAndMore", "laddermen", "engineers", "ranged", "knights", "field86974_0x20f74", "field86627_0x20e04")}
WELLE = k.adresse("DAT_TroopValueState", "attackInfo.value3Array01[]")[0]
TICKER = k.adresse("DAT_TroopValueState", "attackInfo.attackWaveTicker[]")[0]
GROESSE = k.adresse("DAT_TroopValueState", "attackInfo.aiTribeSizesPerTribeType")[0]
ZELT = k.adresse("DAT_TroopValueState", "attackInfo.tentPointsValues[]")
NEUN = 0x01784290  # die 9 Werte aus P284


def sammeln(pfad):
    auf = aw.Aufzeichnung(pfad)
    i = auf.namen.index("DAT_TroopValueState")
    b, laenge = auf.bereiche[i][1], auf.bereiche[i][2]
    print(pfad[-20:], "Bereich", hex(b), hex(b + laenge), "Platz 8 bis", hex(FELDER["attacker"] + 8 * SCHRITT))
    aus = {"felder": collections.defaultdict(list), "welle": collections.defaultdict(list), "ticker": collections.defaultdict(list), "groessen": collections.defaultdict(list), "zelt": collections.defaultdict(list), "neun": collections.defaultdict(list)}
    letzt = {}

    def merke(tab, kk, t, w):
        if letzt.get((id(tab), kk)) != w:
            tab[kk].append((t, w))
            letzt[(id(tab), kk)] = w

    for r, p, _ in auf.staende():
        if r.bereich != i:
            continue
        t = r.takt
        for sp in range(1, 9):
            ver = sp * SCHRITT - b
            for f, a in FELDER.items():
                if 0 <= a + ver <= laenge - 4:
                    merke(aus["felder"], (sp, f), t, struct.unpack_from("<i", p, a + ver)[0])
            if WELLE + ver + 200 <= laenge:
                merke(aus["welle"], sp, t, struct.unpack_from("<50i", p, WELLE + ver))
                merke(aus["ticker"], sp, t, struct.unpack_from("<50i", p, TICKER + ver))
            if GROESSE + ver + 160 <= laenge:
                merke(aus["groessen"], sp, t, struct.unpack_from("<40i", p, GROESSE + ver))
            if ZELT[0] + ver + ZELT[1] * 6 <= laenge:
                merke(aus["zelt"], sp, t, struct.unpack_from("<48i", p, ZELT[0] + ver))
            if NEUN + ver + 36 <= laenge:
                merke(aus["neun"], sp, t, struct.unpack_from("<9i", p, NEUN + ver))
    return {x: dict(v) for x, v in aus.items()}


if __name__ == "__main__":
    basis = sys.argv[1]
    daten = {}
    for kk, e in (("t1", "_t1.auge"), ("danach", "_danach.auge")):
        if os.path.exists(basis + e):
            daten[kk] = sammeln(basis + e)
            print(kk, {f: len(v) for f, v in list(daten[kk]["felder"].items())[:6]}, flush=True)
    with open(os.path.join(HIER, "reihen3.pkl"), "wb") as f:
        pickle.dump(daten, f)
    print("geschrieben")
