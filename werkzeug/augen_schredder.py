# -*- coding: utf-8 -*-
"""B-164 Augen-Test SCHREDDER (Daniel 21.10.2026 21:59: "mit jeweils 1er Stacks gestackt auf eine Mauer, mit einem Schredder
durch alle Mauern durchraspeln, dann waere er direkt drinnen"; 22:04 "ja so machen"). Sandkasten (Franz' Burg, nur Soldaten
abgeraeumt). Die Mauerkachel, die logik.lua "mauer" waehlen wuerde (Franz' Mauer bis 30 Felder um den Lord, mit freiem
Nachbarfeld in Gebiet 1, die dem Lord naechste), davor auf EINEM Feld N Streitkolben, dann EIN Mauerbefehl:
  gruppe  - ein Befehl fuer alle N
  trupp1  - logik.lua "trupp": 1 (jede Einheit ein eigener Mauerbefehl, alle auf dieselbe Kachel)
Gemessen alle 20 Takte direkt aus dem Speicher (speicher.py): Hoehe der Kachel ueber dem Boden, Zahl von Franz' Mauerkacheln
bis 6 Felder daneben, Gebiet am Lord gegen Gebiet am Startfeld.
VORHER FESTGELEGT (21.10. 22:10): Messgroesse = Takte bis zur ersten zerstoerten Kachel bis 6 Felder um die gewaehlte.
Belegt, wenn trupp1 hoechstens 60 % der Takte von gruppe braucht; widerlegt bei mindestens 90 %; UNGUELTIG, wenn keine Variante
in TAKTE eine Kachel zerstoert. Nebenbei: Takt, ab dem der Lord im Gebiet des Startfelds liegt (Durchbruch bis zum Lord).
Ergebnis: daten/augen_schredder.jsonl.
Aufruf: SHC_INSTANZ=5 python werkzeug/augen_schredder.py [laeufe=gruppe,trupp1] [n=30] [takte=3000]
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

import shc  # noqa: E402
import speicher  # noqa: E402
from augen_feuer import laufen  # noqa: E402
from laden import befehl  # noqa: E402
from waechter import lies_lagebild  # noqa: E402

AUS = os.path.join(HIER, "..", "daten", "augen_schredder.jsonl")
UMKREIS = 6


def lage():
    befehl({"lagebild": True}, 2.0, bis="LAGEBILD")
    return lies_lagebild(neu_holen=False)


def kachel_und_start(lp):
    """Wie logik.lua mauer: Franz' Mauerkacheln bis 30 um den Lord mit einem Nachbarfeld in Gebiet 1 - die dem Lord naechste;
    Startfeld = dieses Nachbarfeld."""
    m, _ = speicher.mauern(2)
    geb = speicher.wegkarte()["gebiet"]
    beste = None
    for x in range(lp[0] - 30, lp[0] + 31):
        for y in range(lp[1] - 30, lp[1] + 31):
            if not (0 <= x < 400 and 0 <= y < 400) or not m[x, y]:
                continue
            nb = [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx or dy) and geb[x + dx, y + dy] == 1]
            if nb:
                w = (max(abs(x - lp[0]), abs(y - lp[1])), x, y)
                if beste is None or w < beste[0]:
                    beste = (w, (x, y), nb[0])
    return (beste[1], beste[2]) if beste else (None, None)


def lauf(art, n, takte):
    print("OK:", shc.sandkasten(nur_soldaten="ja"), flush=True)
    L = lage()
    lnr, le = next((k, e) for k, e in L.items() if e["typ"] == 55 and e["besitzer"] == 2 and e["leben"] > 0)
    lp = (le["x"], le["y"])
    kachel, start = kachel_und_start(lp)
    if kachel is None:
        raise SystemExit("FEHLER: keine Mauerkachel mit Nachbarfeld in Gebiet 1")
    t = shc.setze(spieler=1, typ=26, x=start[0] - 1, y=start[1] - 1, anzahl=n)      # setze: Einheiten stehen 1 Feld weiter
    nrs = [int(x) for x in re.search(r"Nummern \[([0-9, ]+)\]", t).group(1).split(",")]
    laufen(3, 40)
    m0, h0 = speicher.mauern(2)
    um = (slice(kachel[0] - UMKREIS, kachel[0] + UMKREIS + 1), slice(kachel[1] - UMKREIS, kachel[1] + UMKREIS + 1))
    n0 = int(m0[um].sum())
    g_start = int(speicher.wegkarte()["gebiet"][start])
    print("%s: Lord %d bei %s, Kachel %s (Hoehe %d), Startfeld %s Gebiet %d, %d Mauerkacheln bis %d daneben" % (
        art, lnr, lp, kachel, h0[kachel], start, g_start, n0, UMKREIS), flush=True)
    b = {"einheiten": nrs, "mauer": [lp[0], lp[1], 2, 30]}
    if art.startswith("trupp"):
        b["trupp"] = int(art[5:])
    t0 = shc.zustand()["tick"]
    befehl({"angriff": b}, 1.0)
    verlauf, erste, durch = [], None, None
    while shc.zustand()["tick"] < t0 + takte:
        laufen(20, 100)
        m, h = speicher.mauern(2)
        geb = speicher.wegkarte()["gebiet"]
        t_ = shc.zustand()["tick"] - t0
        n_jetzt = int(m[um].sum())
        lord_frei = int(geb[lp]) == g_start or any(int(geb[lp[0] + dx, lp[1] + dy]) == g_start
                                                  for dx in (-1, 0, 1) for dy in (-1, 0, 1))
        verlauf.append((t_, int(h[kachel]), n_jetzt, lord_frei))
        if erste is None and n_jetzt < n0:
            erste = t_
        if lord_frei:
            durch = t_
            break
    return {"art": art, "n": n, "kachel": kachel, "start": start, "hoehe0": int(h0[kachel]), "kacheln0": n0,
            "erste": erste, "lord_frei": durch, "verlauf": verlauf}


def main(laeufe=("gruppe", "trupp1"), n=30, takte=3000):
    erg = {}
    for art in laeufe:
        r = lauf(art, n, takte)
        erg[art] = r
        print("%s: erste Kachel weg nach %s Takten, Lord im eigenen Gebiet nach %s; Verlauf (Takt, Hoehe, Kacheln, Lord frei) %s" % (
            art, r["erste"], r["lord_frei"], r["verlauf"][::5]), flush=True)
    urteil = None
    if "gruppe" in erg and "trupp1" in erg:
        g, t = erg["gruppe"]["erste"], erg["trupp1"]["erste"]
        if g is None and t is None:
            urteil = "UNGUELTIG: keine Kachel in %d Takten" % takte
        elif g is None:
            urteil = "BELEGT: nur einzeln eine Kachel zerstoert (%d Takte), als Gruppe gar nicht" % t
        elif t is None:
            urteil = "WIDERLEGT: als Gruppe %d Takte, einzeln gar nicht" % g
        elif t <= 0.6 * g:
            urteil = "BELEGT: einzeln %d Takte gegen Gruppe %d (%.0f %%)" % (t, g, 100.0 * t / g)
        elif t >= 0.9 * g:
            urteil = "WIDERLEGT: einzeln %d Takte gegen Gruppe %d (%.0f %%)" % (t, g, 100.0 * t / g)
        else:
            urteil = "UNENTSCHIEDEN: einzeln %d Takte gegen Gruppe %d (%.0f %%)" % (t, g, 100.0 * t / g)
    print("ERGEBNIS:", urteil, flush=True)
    with open(AUS, "a", encoding="utf-8") as f:
        f.write(json.dumps({"zeit": time.strftime("%Y-%m-%d %H:%M:%S"), "laeufe": erg, "urteil": urteil},
                           ensure_ascii=False, default=lambda o: o.item() if isinstance(o, np.generic) else str(o)) + "\n")


if __name__ == "__main__":
    a = dict(x.split("=", 1) for x in sys.argv[1:])
    main(tuple(a.get("laeufe", "gruppe,trupp1").split(",")), int(a.get("n", 30)), int(a.get("takte", 3000)))
