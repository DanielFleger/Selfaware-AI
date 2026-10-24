# -*- coding: utf-8 -*-
"""Aufnahme Torhaus-Durchgang fuer den Laufwegbeweis (B-211, Auftrag der SRE-Sitzung 24.10.2026, Daniel 22:00 "gerne").

Sandkasten (shc.sandkasten: Franz' Burg, Heere abgeraeumt, Lords leben) auf einer eigenen Instanz. Wir handeln als Spieler 2
(Franz' Burg hat Torhaus, Mauern und Tuerme): ANZAHL Einheiten je Art werden neben seinem Lord gesetzt, die Nahkaempfer laufen
durch das Torhaus nach draussen, die Bogenschuetzen auf den naechsten Turm. Mitgeschrieben wird nur, was SRE braucht:
  - Wegkarte dreimal (vor dem Loslaufen, nach ~200 Takten, am Ende): daten/torhaus_wegkarte_<zeit>_<takt>.npz (link, gebiet,
    gebaeude, hoehe, boden - speicher.wegkarte())
  - Einheitenorte alle 2 Takte (Modulbefehl einheitwacht), roh aus dem ucp3.log: daten/torhaus_aufnahme_<zeit>.json ("ew",
    "arbeiter" Nummer -> Typname, Instanz, Takt Start/Ende, Torhaus x/y)
Keine Auswertung, keine Aenderung an logik.lua. Aufruf: SHC_INSTANZ=4 SHC_SPIELER=2 python werkzeug/torhaus_aufnahme.py [takte=1500]"""
import json
import os
import sys
import time

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
D = os.path.join(HIER, "..", "daten")
TORHAUS, TUERME, LORD = (45, 46), (74, 75, 76, 77, 78), 55
TYPEN = {24: "Speertraeger", 22: "Bogenschuetze", 26: "Streitkolben"}


def log_ab(marke):
    import befehl as kanal
    zeilen = open(kanal.LOG, encoding="utf-8", errors="replace").read().splitlines()
    for i in range(len(zeilen) - 1, -1, -1):
        if marke in zeilen[i]:
            return zeilen[i:]
    return []


def main(argv):
    arg = dict(a.split("=", 1) for a in argv if "=" in a)
    takte_max = int(arg.get("takte", 1500))
    sp = int(os.environ.get("SHC_SPIELER", "2"))
    inst = int(os.environ.get("SHC_INSTANZ", "4"))
    import shc
    import speicher
    from laden import befehl
    from befehl import SPIEL
    sys.path.insert(0, os.path.join(HIER, "..", "..", "Selfaware-AI-kern", "src"))
    from selfaware.game.kern_leitung import Leitung
    zeit = time.strftime("%Y%m%d_%H%M%S")
    print("OK:", shc.sandkasten(), flush=True)
    w = Leitung(SPIEL).lesen()
    G = {n: g for n, g in w.gebaeude.items() if g.get("besitzer") == sp}
    lord = next(((e["x"], e["y"]) for e in w.einheiten.values() if e["typ"] == LORD and e["besitzer"] == sp), None)
    tore = [(g["x"], g["y"]) for g in G.values() if g["typ"] in TORHAUS]
    tuerme = [(g["x"], g["y"]) for g in G.values() if g["typ"] in TUERME]
    if lord is None or not tore:
        raise shc.Fehler("Spieler %d hat keinen Lord oder kein Torhaus im Sandkasten (Tore %s)" % (sp, tore))
    tor = min(tore, key=lambda q: max(abs(q[0] - lord[0]), abs(q[1] - lord[1])))
    turm = min(tuerme, key=lambda q: max(abs(q[0] - lord[0]), abs(q[1] - lord[1]))) if tuerme else None
    dx, dy = tor[0] - lord[0], tor[1] - lord[1]
    n_ = max(abs(dx), abs(dy), 1)
    draussen = (tor[0] + 10 * dx // n_, tor[1] + 10 * dy // n_)      # 10 Felder hinter dem Torhaus, vom Lord aus gesehen
    print("Lord %s, Torhaus %s, Ziel draussen %s, Turm %s" % (lord, tor, draussen, turm), flush=True)

    def karte(takt):
        k = speicher.wegkarte()
        pfad = os.path.join(D, "torhaus_wegkarte_%s_%d.npz" % (zeit, takt))
        np.savez(pfad, **{n: np.asarray(k[n]) for n in ("link", "gebiet", "gebaeude", "hoehe", "boden") if n in k})
        print("Wegkarte gespeichert:", os.path.basename(pfad), flush=True)
        return pfad

    dateien = []
    nummern = {}
    for typ, anzahl in ((24, 4), (22, 4)):
        text = shc.setze(spieler=str(sp), typ=str(typ), x=str(lord[0] + 2), y=str(lord[1] + 2), anzahl=str(anzahl))
        for n in [int(v) for v in text.split("Nummern")[1].strip(" []").split(",")]:
            nummern[n] = typ
    print("Einheiten:", nummern, flush=True)
    t0 = shc.zustand()["tick"]
    dateien.append(karte(t0))
    befehl({"einheitwacht": {"nr": sorted(nummern), "alle": 2}}, 1.0, bis="EINHEITWACHT")
    nah = [n for n, t in nummern.items() if t == 24]
    fern = [n for n, t in nummern.items() if t == 22]
    befehl({"angriff": {"einheiten": nah, "lauf": [draussen[0], draussen[1]]}}, 1.0, bis="ANGRIFF")
    if turm and fern:
        befehl({"angriff": {"einheiten": fern, "lauf": [turm[0] + 1, turm[1] + 1]}}, 1.0, bis="ANGRIFF")
    befehl({"pause": False, "tempo": 40}, 0.3)
    zweite = False
    ende = time.time() + 240
    while time.time() < ende:
        t = shc.zustand()["tick"]
        if not zweite and t - t0 >= 200:
            dateien.append(karte(t)); zweite = True
        w = Leitung(SPIEL).lesen()
        fertig = all(n in w.einheiten and max(abs(w.einheiten[n]["x"] - z[0]), abs(w.einheiten[n]["y"] - z[1])) <= 2
                     for n, z in [(n, draussen) for n in nah] + ([(n, (turm[0] + 1, turm[1] + 1)) for n in fern] if turm else []))
        if fertig or t - t0 >= takte_max:
            break
        time.sleep(0.5)
    befehl({"pause": True}, 0.3)
    t1 = shc.zustand()["tick"]
    befehl({"einheitwacht": False}, 1.0, bis="EINHEITWACHT")
    dateien.append(karte(t1))
    ew = [z.split("INFO|", 1)[-1] for z in log_ab("EINHEITWACHT: scharf") if " EW " in z or "EW Orte" in z or "EW Tick" in z]
    erg = {"zweck": "B-211 Torhaus-Durchgang (SRE)", "instanz": inst, "spieler": sp, "takt_start": t0, "takt_ende": t1,
           "torhaus": list(tor), "turm": list(turm) if turm else None, "lord": list(lord), "ziel_draussen": list(draussen),
           "arbeiter": {str(n): TYPEN.get(t, str(t)) for n, t in nummern.items()}, "wegkarten": [os.path.basename(p) for p in dateien],
           "ew": ew, "zeit": zeit}
    pfad = os.path.join(D, "torhaus_aufnahme_%s.json" % zeit)
    json.dump(erg, open(pfad, "w", encoding="utf-8"), indent=1)
    print("OK: %s EW-Zeilen, Takte %d-%d, Dateien: %s + %s" % (len(ew), t0, t1, os.path.basename(pfad), ", ".join(erg["wegkarten"])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
