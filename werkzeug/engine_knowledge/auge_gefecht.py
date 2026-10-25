# -*- coding: utf-8 -*-
"""B-251 Pruefstein fuers Gehirn (SAI 25.10. 19:15): Sandkasten, ~20 gegen 20 gemischt, Protokoll JEDEN Takt, >= 60 s,
danach Treffer je Takt (auge.treffer_folge) und Kennzahlen: Takt-Luecken, Anteil zugeordneter Lebensverluste je Quelle.

Aufstellung je Seite: 4 E_ARCHER 22, 3 E_XBOW 23, 3 A_ARCHER 70, 3 E_SPEAR 24, 3 E_MACE 26, 2 E_SWORD 27, 2 A_ASSASSIN 73.
Aufruf: python werkzeug/engine_knowledge/auge_gefecht.py [sekunden=90] [tempo=100] [abstand=14]
        python werkzeug/engine_knowledge/auge_gefecht.py --nur_auswerten <npz>
"""
import collections
import json
import os
import sys
import time

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HIER))
sys.path.insert(0, HIER)
import auge  # noqa: E402
import shc  # noqa: E402
import speicher  # noqa: E402
from laden import befehl  # noqa: E402
from auge_pruefen import freie_reihe  # noqa: E402

DATEN = os.path.join(os.path.dirname(os.path.dirname(HIER)), "daten")
AUFSTELLUNG = [(22, 4), (23, 3), (70, 3), (24, 3), (26, 3), (27, 2), (73, 2)]


def aufstellen(spieler, x0, y, k):
    """Zwei Reihen je Seite (Schuetzen hinten, Nahkaempfer vorn); prueft das Gebiet jedes Felds."""
    nr = []
    x = x0
    for typ, n in AUFSTELLUNG:
        for i in range(n):
            if int(k["gebiet"][x, y]) <= 0 or int(k["gebaeude"][x, y]):
                x += 1
            print("  ", shc.setze(str(spieler), str(typ), str(x), str(y), "1"))
            nr.append(typ)
            x += 1
    return nr


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sek = float(args[0]) if args else 90.0
    tempo = int(args[1]) if len(args) > 1 else 100
    abstand = int(args[2]) if len(args) > 2 else 14
    z = shc.zustand()
    print("Zustand:", z["text"])
    if z.get("gameover") or not z.get("pause"):
        print("FEHLER: nicht bespielbar/angehalten", z)
        return 1
    s = auge.Schnappschuss()
    lord = next((p["lord"]["feld"] for p in s.spieler_liste() if p["spieler"] == 1 and "feld" in p["lord"]), None)
    k = speicher.wegkarte()
    reihe = None
    for versuch in range(60):
        r = freie_reihe((lord[0], lord[1] + 6 + versuch), 24, suchweite=30)
        if r and all((k["gebiet"][r[1]:r[1] + 24, r[2] + dy] > 0).all() and (k["gebaeude"][r[1]:r[1] + 24, r[2] + dy] == 0).all()
                     for dy in (1, abstand, abstand + 1)):
            reihe = r
            break
    print("Reihe", reihe, "Lord", lord)
    _, x0, y = reihe
    print("Spieler 1:")
    aufstellen(1, x0, y, k)
    print("Spieler 2:")
    aufstellen(2, x0, y + abstand, k)
    befehl({"pause": False, "tempo": tempo}, 0.2)
    time.sleep(0.1)
    befehl({"pause": True}, 0.2)
    s = auge.Schnappschuss()
    n1 = len(s.einheiten_liste((1,)))
    n2 = len(s.einheiten_liste((2,)))
    print("Einheiten Spieler 1:", n1, "Spieler 2:", n2, "Takt", s.takt)
    befehl({"pause": False, "tempo": tempo}, 0.2)
    t0 = time.time()
    pfad, p = auge.protokollieren(sek, (1, 2), mit_trupps=False, alle_takte=1)
    befehl({"pause": True}, 0.2)
    print("Aufnahme %.1f s, %d Takte (%d..%d) -> %s" % (time.time() - t0, len(p.takte), min(p.takte), max(p.takte), pfad))
    return auswerten(pfad)


def auswerten(pfad):
    L = auge.Protokoll.laden(pfad)
    takte = [s.takt for s in L]
    luecken = [b - a for a, b in zip(takte, takte[1:]) if b - a > 1]
    tr = auge.treffer_folge(L)
    quellen = collections.Counter()
    verlust = collections.Counter()
    for t in tr:
        q = sorted(set(x["quelle"] for x in t["quellen"]))
        quellen["+".join(q)] += 1
        verlust["+".join(q)] += t["verlust"]
    # Leben am Anfang/Ende je Seite
    def leben(s, sp):
        u = s.einheiten
        m = (u["owner"] == sp) & (u["logicalState"] == 2)
        return int(u["health"][m].sum()), int(m.sum())
    erg = {"protokoll": os.path.basename(pfad), "takte": [takte[0], takte[-1]], "schnappschuesse": len(takte),
           "takt_luecken": len(luecken), "fehlende_takte": int(sum(l - 1 for l in luecken)),
           "takte_rueckwaerts_oder_doppelt": int(sum(1 for a, b in zip(takte, takte[1:]) if b <= a)),
           "anteil_takte_erfasst": round(len(takte) / float(takte[-1] - takte[0] + 1), 3),
           "treffer_ereignisse": len(tr), "verlust_summe": int(sum(t["verlust"] for t in tr)),
           "nach_quelle_ereignisse": dict(quellen), "nach_quelle_verlust": dict(verlust),
           "leben_start": {"1": leben(L[0], 1), "2": leben(L[0], 2)}, "leben_ende": {"1": leben(L[-1], 1), "2": leben(L[-1], 2)},
           "geschosse_gesehen": len(set(int(g["uid"]) for s in L for g in s.entities if int(g["entityType"]) in auge.GESCHOSSE)),
           "beispiele": tr[:12]}
    aus = pfad.replace(".npz", "_treffer.json")
    json.dump({"kennzahlen": erg, "treffer": tr}, open(aus, "w", encoding="utf-8"), ensure_ascii=False)
    print(json.dumps({k: v for k, v in erg.items() if k != "beispiele"}, ensure_ascii=False))
    for t in erg["beispiele"]:
        print("  ", json.dumps(t, ensure_ascii=False))
    print("->", aus)
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--nur_auswerten":
        sys.exit(auswerten(sys.argv[2]))
    sys.exit(main())
