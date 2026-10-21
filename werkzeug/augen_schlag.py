# -*- coding: utf-8 -*-
"""B-166 Extremtest SCHLAG (Daniel 21.10.2026 22:35: "keine erfundenen Werte - im Code genau rauslesen, wie viel die Einheit pro
Tick haut; die Messung dann abgleichen mit der Realitaet, Differenzen erklaeren, weitere Extremtests").
EIN Streitkolben steht direkt neben EINER Mauerkachel (der ersten auf dem Durchbruch-Weg von (150,150) zu Franz' Lord, Sandkasten
ohne Soldaten) und bekommt den Mauerbefehl auf genau diese Kachel. Jeden Spieltakt direkt aus dem Speicher: Hoehe der Kachel,
animationCycleNumber, nextAttackHurtsWall, Zustand und Feld des Manns.
VORHERSAGE (mechanik.py, aus dem laufenden Spielcode): ein Bild je (animationSpeed+1) Takte, Schlag nach `bilder` Bildern, nur
jeder 2. Schlag trifft, Schaden je Treffer nach Mauernachbarn, erster Treffer evtl. -20. Gemessen wird, ob genau das passiert.
Messgrenze: doppelte vorhergesagte Zeit bis zur Zerstoerung (aus der Vorhersage, nicht angenommen).
Ergebnis: daten/augen_schlag.jsonl.  Aufruf: SHC_INSTANZ=5 python werkzeug/augen_schlag.py
"""
import json
import os
import re
import sys
import time

os.environ.setdefault("SHC_INSTANZ", "5")
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import numpy as np  # noqa: E402

import feldzug  # noqa: E402
import mechanik  # noqa: E402
import shc  # noqa: E402
import speicher  # noqa: E402
from laden import befehl  # noqa: E402
from waechter import lies_gebaeude, lies_lagebild  # noqa: E402

AUS = os.path.join(HIER, "..", "daten", "augen_schlag.jsonl")
E0, ES = 0x0138854C, 1168


def feldnr(x, y):
    xs, ys, ks = speicher.felder()
    return int(ks[np.nonzero((xs == x) & (ys == y))[0][0]])


def main():
    print("OK:", shc.sandkasten(nur_soldaten="ja"), flush=True)
    befehl({"lagebild": True}, 2.0, bis="LAGEBILD")
    L = lies_lagebild(neu_holen=False)
    lp = next((e["x"], e["y"]) for e in L.values() if e["typ"] == 55 and e["besitzer"] == 2 and e["leben"] > 0)
    G = lies_gebaeude()
    wk = speicher.wegkarte()
    m, h = speicher.mauern(2)
    f = feldzug.Feldzug(1, (80, 260))
    geb = f._ohne_feindtore(wk["gebiet"], wk["gebaeude"], G)
    plan = f._durchbruch(geb, m, h, (150, 150), lp)
    kq = plan["kachel"]
    if kq is None:
        raise SystemExit("UNGUELTIG: kein Durchbruch-Weg")
    neben = plan["weg"][plan["weg"].index(kq) - 1]
    k = feldnr(*kq)
    logik = speicher.ebene(speicher.LOGIK, 4)
    nachbarn = sum(1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if logik[kq[0] + dx, kq[1] + dy] & 0x10000100)
    mk = mechanik.streitkolben()
    hoehe0 = speicher.lies(speicher.HOEHE + k, 1)[0]
    boden = speicher.lies(speicher.BODEN + k, 1)[0]
    bit = bool(logik[kq] & 0x10000)
    d = mechanik.kachel_schaden(mk["mauer"], nachbarn)
    n_tr = mechanik.treffer_bis_zerstoert(hoehe0, boden, d, True, bit)
    vorher = n_tr * mk["takte_je_treffer"]
    print("Kachel %s Hoehe %d Boden %d (ueber Boden %d), Mauernachbarn %d, Bit 0x10000 %s | Code: %s | Vorhersage: %d Schaden je "
          "Treffer, %d Treffer, %d Takte ab dem ersten Schwung | Mann auf %s" % (
              kq, hoehe0, boden, hoehe0 - boden, nachbarn, bit, mk, d, n_tr, vorher, neben), flush=True)
    t = shc.setze(spieler=1, typ=26, x=neben[0] - 1, y=neben[1] - 1, anzahl=1)      # setze: 1 Feld weiter (gemessen 17.10.)
    nr = int(re.search(r"Nummern \[([0-9, ]+)\]", t).group(1).split(",")[0])
    b = speicher.lies(E0 + nr * ES, ES)
    steht = (int.from_bytes(b[0xC4:0xC6], "little", signed=True), int.from_bytes(b[0xC6:0xC8], "little", signed=True))
    print("Einheit %d steht auf %s (Soll %s)" % (nr, steht, neben), flush=True)
    befehl({"angriff": {"einheiten": [nr], "mauer": [lp[0], lp[1], 2, 30, kq[0], kq[1]]}}, 1.0)
    lies = speicher.lies
    tick0 = int.from_bytes(lies(shc.TICK, 4), "little")
    befehl({"pause": False, "tempo": 40}, 0.2)
    reihe, letzt = [], None
    grenze = 2 * vorher
    while True:
        tk = int.from_bytes(lies(shc.TICK, 4), "little")
        if tk == letzt:
            continue
        letzt = tk
        b = lies(E0 + nr * ES, ES)
        hh = lies(speicher.HOEHE + k, 1)[0]
        reihe.append((tk - tick0, hh, int.from_bytes(b[mechanik.E_ZYKLUS:mechanik.E_ZYKLUS + 4], "little", signed=True),
                      b[mechanik.E_TREFFER], int.from_bytes(b[0x8C:0x8E], "little", signed=True),
                      int.from_bytes(b[0xC4:0xC6], "little", signed=True), int.from_bytes(b[0xC6:0xC8], "little", signed=True)))
        if hh <= boden or tk - tick0 >= grenze:
            break
    befehl({"pause": True}, 0.3)
    luecken = sum(1 for a, c in zip(reihe, reihe[1:]) if c[0] - a[0] != 1)
    schlaege = [r[0] for a, r in zip(reihe, reihe[1:]) if r[3] != a[3]]
    spruenge = [(r[0], a[1] - r[1], r[3]) for a, r in zip(reihe, reihe[1:]) if r[1] != a[1]]
    bildwechsel = [r[0] for a, r in zip(reihe, reihe[1:]) if r[2] != a[2]]
    abst = lambda xs: [b_ - a_ for a_, b_ in zip(xs, xs[1:])]
    erg = {"zeit": time.strftime("%Y-%m-%d %H:%M:%S"), "kachel": kq, "hoehe0": hoehe0, "boden": boden, "nachbarn": nachbarn,
           "code": mk, "vorhersage": {"schaden": d, "treffer": n_tr, "takte": vorher}, "takte_gemessen": reihe[-1][0],
           "luecken": luecken, "schlaege": schlaege[:100], "spruenge": spruenge[:100],
           "bildabstand": sorted(set(abst(bildwechsel)))[:20], "schlagabstand": abst(schlaege)[:100],
           "trefferabstand": abst([s[0] for s in spruenge])[:100], "reihe": reihe[:400]}
    print("Takte gelesen %d, Luecken %d" % (len(reihe), luecken), flush=True)
    print("Bildwechsel-Abstaende (Takte):", erg["bildabstand"], flush=True)
    print("Schlag-Abstaende (nextAttackHurtsWall wechselt):", erg["schlagabstand"][:20], flush=True)
    print("Hoehenspruenge (Takt, minus, Schalter danach):", spruenge[:20], flush=True)
    print("Treffer-Abstaende:", erg["trefferabstand"][:20], flush=True)
    print("ZERSTOERT bei Takt %s | Vorhersage %d Takte ab Schwungbeginn" % (
        reihe[-1][0] if reihe[-1][1] <= boden else None, vorher), flush=True)
    with open(AUS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(erg, ensure_ascii=False, default=lambda o: o.item() if isinstance(o, np.generic) else str(o)) + "\n")


if __name__ == "__main__":
    main()
