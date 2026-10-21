# -*- coding: utf-8 -*-
"""B-153 Augen-Test BERGFRIED STAPELN (Daniel 21.10.2026 20:23: "man kommt nur auf das Keep, wenn man dort drauf geht, sonst
bekommt der Lord keinen Schaden; auf einen Keep koennen ca. 30 Leute, und wenn du sie in Trueppchen draufschickst bzw. alle
einzeln, koennen sie sich unendlich stacken - 100 auf einmal: nur ca. 30 gehen hoch, der Rest steht unten").
Sandkasten (Franz' Burg, nur Soldaten abgeraeumt). N eigene Streitkolben werden auf einem Feld abgesetzt, von dem der
Wegfinder des Spiels den Lord erreicht (gesucht auf Ringen um den Lord), dann EIN Angriffsbefehl auf Franz' Lord:
  gruppe  - ein Befehl fuer alle N
  trupp1  - logik.lua "trupp": 1 (jede Einheit ein eigener Befehl)
  trupp5  - Trueppchen zu 5
Gemessen: Leben des Lords alle 20 Takte, Takt seines Todes (= SIEG-Meldung des Spielende-Melders), eigene Verluste.
VORHER FESTGELEGT (21.10. 20:47, neu - der erste Massstab "Schaden in 1.200 Takten" war falsch gewaehlt: in Lauf 1 starb
der Lord schon nach 259 Takten, also in jeder Variante voll): Daniels Regel belegt, wenn trupp1 oder trupp5 den Lord in
hoechstens 60 % der Zeit von gruppe toetet; widerlegt bei mindestens 90 %. UNGUELTIG, wenn kein Lauf den Lord in TAKTE
toetet. Ergebnis: daten/augen_bergfried.jsonl.
Aufruf: SHC_INSTANZ=5 python werkzeug/augen_bergfried.py [laeufe=gruppe,trupp1,trupp5] [n=60] [takte=2000]
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
from laden import befehl  # noqa: E402
from waechter import lies_lagebild  # noqa: E402
from augen_feuer import laufen  # noqa: E402
from erstes_spiel import wegtest  # noqa: E402

AUS = os.path.join(HIER, "..", "daten", "augen_bergfried.jsonl")
LORD = 55


def lage():
    befehl({"lagebild": True}, 2.0, bis="LAGEBILD")
    return lies_lagebild(neu_holen=False)


def franz_lord(L):
    return next((n, e) for n, e in L.items() if e["typ"] == LORD and e["besitzer"] == 2 and e["leben"] > 0)


def startfeld(L, lp):
    """Ein Feld, von dem der Wegfinder des Spiels ein Feld bis 3 am Lord erreicht: Ringe 6..16 um den Lord, je 8 Richtungen;
    je Kandidat eine Probe-Einheit setzen und wegtest fragen."""
    ziele = [(lp[0] + dx * r, lp[1] + dy * r) for r in (1, 2, 3)
             for dx, dy in ((0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1))]
    for r in (6, 8, 10, 12, 16):
        for dx, dy in ((0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)):
            c = (lp[0] + dx * r, lp[1] + dy * r)
            t = shc.setze(spieler=1, typ=26, x=c[0], y=c[1], anzahl=1)
            m = re.search(r"Nummern \[([0-9, ]+)\]", t)
            if not m:
                continue
            nr = int(m.group(1).split(",")[0])
            gut = wegtest(nr, ziele)
            befehl({"toeteAlle": {"spieler": 1, "ohneLord": True, "typen": [26]}}, 0.8)
            if any(gut):
                return c, [z for z, g in zip(ziele, gut) if g]
    return None, []


def lauf(art, n, takte, start=None):
    print("OK:", shc.sandkasten(nur_soldaten="ja"), flush=True)
    L = lage()
    lnr, le = franz_lord(L)
    lp = (le["x"], le["y"])
    if start is None:
        start, erreichbar = startfeld(L, lp)
        print("Lord %d bei %s, Startfeld %s (erreicht am Lord: %s)" % (lnr, lp, start, erreichbar[:4]), flush=True)
        if start is None:
            raise SystemExit("FEHLER: kein Startfeld, von dem der Lord erreichbar ist")
        laufen(400, 100)                       # Steintod der Probe-Einheiten abwarten
    t = shc.setze(spieler=1, typ=26, x=start[0], y=start[1], anzahl=n)
    nrs = [int(x) for x in re.search(r"Nummern \[([0-9, ]+)\]", t).group(1).split(",")]
    laufen(3, 40)
    L = lage()
    leben0 = L[lnr]["leben"]
    b = {"einheiten": nrs, "ziel": lnr}
    if art.startswith("trupp"):
        b["trupp"] = int(art[5:])
    t0 = shc.zustand()["tick"]
    befehl({"angriff": b}, 1.0)
    verlauf, tod = [], None
    while shc.zustand()["tick"] < t0 + takte:
        try:
            laufen(20, 40)
        except shc.Fehler as e:                # B-154: der Tod des Lords beendet die Partie - der Melder sagt SIEG
            if "SIEG" not in str(e):
                raise
            tod = shc.zustand()["tick"] - t0
            break
        L = lage()
        t_ = shc.zustand()["tick"] - t0
        le = L.get(lnr)
        lebt = le is not None and le["leben"] > 0
        eigene = sum(1 for k in nrs if k in L and L[k]["leben"] > 0)
        nah = sum(1 for k in nrs if k in L and max(abs(L[k]["x"] - lp[0]), abs(L[k]["y"] - lp[1])) <= 3)
        verlauf.append((t_, le["leben"] if lebt else 0, eigene, nah))
        if not lebt:
            tod = t_
            break
    return {"art": art, "n": n, "lord": lnr, "lord_bei": lp, "start": start, "leben0": leben0, "tod": tod, "verlauf": verlauf}


def main(laeufe=("gruppe", "trupp1", "trupp5"), n=60, takte=2000):
    erg, start = {}, None
    for art in laeufe:
        r = lauf(art, n, takte, start)
        start = r["start"]
        erg[art] = r
        print("%s: Lord tot nach %s Takten (Leben vorher %d), Verlauf (Takt, Leben, eigene, <=3 am Lord) %s" % (
            art, r["tod"], r["leben0"], r["verlauf"]), flush=True)
    urteil = None
    if "gruppe" in erg:
        g = erg["gruppe"]["tod"]
        t = min((erg[a_]["tod"] for a_ in erg if a_.startswith("trupp") and erg[a_]["tod"]), default=None)
        if g is None and t is None:
            urteil = "UNGUELTIG: kein Lauf toetete den Lord in %d Takten" % takte
        elif g is None:
            urteil = "BELEGT: nur in Trueppchen tot (nach %d Takten), als Gruppe gar nicht" % t
        elif t is None:
            urteil = "WIDERLEGT: als Gruppe tot nach %d Takten, in Trueppchen gar nicht" % g
        elif t <= 0.6 * g:
            urteil = "BELEGT: Trueppchen %d Takte gegen Gruppe %d (%.0f %%)" % (t, g, 100.0 * t / g)
        elif t >= 0.9 * g:
            urteil = "WIDERLEGT: Trueppchen %d Takte gegen Gruppe %d (%.0f %%)" % (t, g, 100.0 * t / g)
        else:
            urteil = "UNENTSCHIEDEN: Trueppchen %d Takte gegen Gruppe %d (%.0f %%)" % (t, g, 100.0 * t / g)
    print("ERGEBNIS:", urteil, flush=True)
    with open(AUS, "a", encoding="utf-8") as f:
        f.write(json.dumps({"zeit": time.strftime("%Y-%m-%d %H:%M:%S"), "laeufe": erg, "urteil": urteil}, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    a = dict(x.split("=", 1) for x in sys.argv[1:])
    main(tuple(a.get("laeufe", "gruppe,trupp1,trupp5").split(",")), int(a.get("n", 60)), int(a.get("takte", 2000)))
