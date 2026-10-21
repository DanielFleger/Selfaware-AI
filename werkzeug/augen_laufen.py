# -*- coding: utf-8 -*-
"""B-167 Messung LAUFEN (21.10.2026 23:05, fuer den Durchbruch-Weg ueber die Schrittbits: Laufen gegen Hacken in Takten).
EIN Streitkolben laeuft im Sandkasten eine gerade Strecke ueber freies Feld (Gebiet 1, alle Felder mit Schrittbit in Laufrichtung),
gerade (O) und schraeg (SO). Jeden Takt aus dem Speicher: Feld des Manns. Gemessen: Takte je Feldwechsel gerade und schraeg.
Strecke: die laengste freie Gerade ab (150,150) nach O bzw. SO, hoechstens bis ein Feld kein Schrittbit mehr hat.
Ergebnis: daten/augen_laufen.jsonl.   Aufruf: SHC_INSTANZ=5 python werkzeug/augen_laufen.py
"""
import json
import os
import re
import sys
import time

os.environ.setdefault("SHC_INSTANZ", "5")
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import shc  # noqa: E402
import speicher  # noqa: E402
from laden import befehl  # noqa: E402

AUS = os.path.join(HIER, "..", "daten", "augen_laufen.jsonl")
E0, ES = 0x0138854C, 1168
BIT = {(1, 0): 0x04, (1, 1): 0x08}       # Schrittbits O, SO (logik.lua wegkarte: Uhrzeigersinn ab N = 1)


def strecke(link, geb, start, d):
    p, aus = start, [start]
    while link[p] & BIT[d] and geb[(p[0] + d[0], p[1] + d[1])] == geb[start]:
        p = (p[0] + d[0], p[1] + d[1])
        aus.append(p)
    return aus


def main():
    print("OK:", shc.sandkasten(nur_soldaten="ja"), flush=True)
    wk = speicher.wegkarte()
    erg = {"zeit": time.strftime("%Y-%m-%d %H:%M:%S")}
    for name, d in (("gerade_O", (1, 0)), ("schraeg_SO", (1, 1))):
        weg = strecke(wk["link"], wk["gebiet"], (150, 150), d)
        ziel = weg[-1]
        t = shc.setze(spieler=1, typ=26, x=weg[0][0] - 1, y=weg[0][1] - 1, anzahl=1)
        nr = int(re.search(r"Nummern \[([0-9, ]+)\]", t).group(1).split(",")[0])
        befehl({"angriff": {"einheiten": [nr], "lauf": [ziel[0], ziel[1]]}}, 1.0)
        t0 = int.from_bytes(speicher.lies(shc.TICK, 4), "little")
        befehl({"pause": False, "tempo": 40}, 0.2)
        spur, letzt = [], None
        while True:
            tk = int.from_bytes(speicher.lies(shc.TICK, 4), "little")
            if tk == letzt:
                continue
            letzt = tk
            b = speicher.lies(E0 + nr * ES, 0xC8)
            p = (int.from_bytes(b[0xC4:0xC6], "little", signed=True), int.from_bytes(b[0xC6:0xC8], "little", signed=True))
            if not spur or spur[-1][1] != p:
                spur.append((tk - t0, p))
            if p == ziel:
                break
        befehl({"pause": True}, 0.3)
        abst = [b_[0] - a_[0] for a_, b_ in zip(spur, spur[1:])]
        erg[name] = {"felder": len(weg) - 1, "takte": spur[-1][0] - spur[0][0], "abstaende": abst,
                     "takte_je_feld": (spur[-1][0] - spur[1][0]) / float(len(spur) - 2) if len(spur) > 2 else None}
        print("%s: %d Felder, Feldwechsel-Abstaende %s, Takte je Feld (ab dem 1. Wechsel) %.2f" % (
            name, len(weg) - 1, abst, erg[name]["takte_je_feld"] or -1), flush=True)
    with open(AUS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(erg, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
