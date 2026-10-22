# -*- coding: utf-8 -*-
"""Schaden je Takt und Einheit an einem Lord, im Sandkasten gemessen (B-207, 22.10.2026).

Anlass: der Lord-Wettlauf (gefecht.lord_rennen) braucht, wie schnell unsere Nahkaempfer einen Lord toeten. In 378
Lageprotokollen gab es fuer Streitkolben (26) keine einzige reine Probe (lord_messen.py), gefecht.dps nahm das Mittel der
Zeile (89 je Takt) - ungemessen. Hier: Sandkasten laden (shc.sandkasten, Franz' Heer abgeraeumt, beide Lords leben),
ANZAHL Einheiten einer Art 1 Feld neben Franz' Lord setzen, Angriffsbefehl auf ihn, laufen lassen und alle ~0,3 s lesen:
Lebensverlust des Lords je Takt / Zahl der eigenen Lebenden. Gezaehlt wird nur das Stueck, in dem alle noch leben und der
Lord wirklich Leben verliert (Anlaufzeit faellt so heraus).

Aufruf: python werkzeug/lord_nahkampf_messen.py [typ=26] [anzahl=5] [takte=600]
Ergebnis: eine Zeile je Messung nach daten/lord_nahkampf.jsonl."""
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
os.environ.setdefault("SHC_INSTANZ", "5")


def main(argv):
    arg = dict(a.split("=", 1) for a in argv if "=" in a)
    typ, anzahl, takte = int(arg.get("typ", 26)), int(arg.get("anzahl", 5)), int(arg.get("takte", 600))
    import shc
    from laden import befehl
    from befehl import SPIEL
    sys.path.insert(0, os.path.join(HIER, "..", "..", "Selfaware-AI-kern", "src"))
    from selfaware.game.kern_leitung import Leitung
    print("OK:", shc.sandkasten(), flush=True)
    w = Leitung(SPIEL).lesen()
    lord = [(n, e) for n, e in w.einheiten.items() if e["typ"] == 55 and e["besitzer"] == 2 and e["leben"] > 0]
    if not lord:
        raise shc.Fehler("kein Lord von Spieler 2")
    ln, le = lord[0]
    text = shc.setze(spieler="1", typ=str(typ), x=str(le["x"] + 1), y=str(le["y"]), anzahl=str(anzahl))
    print("OK:", text, flush=True)
    nrs = [int(n) for n in text.split("Nummern")[1].strip(" []").split(",")]
    befehl({"angriff": {"einheiten": nrs, "ziel": ln}}, 1.0)
    befehl({"pause": False, "tempo": 40}, 0.3)
    proben, t0 = [], Leitung(SPIEL).lesen().tick
    ende = time.time() + 120
    while time.time() < ende:
        w = Leitung(SPIEL).lesen()
        t = w.tick
        if t <= t0 or (proben and t <= proben[-1][0]):
            time.sleep(.01)
            continue
        lo = w.einheiten.get(ln, {})
        leben_l = lo.get("leben", 0) if lo.get("typ") == 55 else 0
        lebend = sum(1 for n in nrs if n in w.einheiten and w.einheiten[n].get("typ") == typ and w.einheiten[n]["leben"] > 0)
        proben.append((t, leben_l, lebend))
        if leben_l <= 0 or lebend == 0 or t >= t0 + takte:
            break
        time.sleep(0.3)
    befehl({"pause": True}, 0.3)
    # Stueck mit allen am Leben und sinkendem Lord-Leben
    # Nur benachbarte kohaerente Weltbilder: keine Zeitluecke ueber
    # verschwundene Kaempfer und keine vom Weltbild getrennt gelesene Uhr.
    schlag = [(a,b) for a,b in zip(proben,proben[1:])
              if a[2] == b[2] == anzahl and b[0] > a[0] and 0 < b[1] < a[1]]
    if not schlag:
        erg = {"typ":typ,"anzahl":anzahl,"je_takt":None,"grund":"keine gueltigen benachbarten Schlagproben","proben":proben}
    else:
        dt=sum(b[0]-a[0] for a,b in schlag)
        verlust=sum(a[1]-b[1] for a,b in schlag)
        erg={"typ":typ,"anzahl":anzahl,"je_takt":round(verlust/dt/anzahl,1),
             "takte":dt,"lord_verlust":verlust,"proben":proben,"methode":"kern_tick_adjacent_v2"}
    erg["zeit"] = time.strftime("%Y-%m-%d %H:%M")
    with open(os.path.join(HIER, "..", "daten", "lord_nahkampf.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(erg) + "\n")
    print("OK: Typ %d x%d an Lord %d: %s je Takt und Einheit (%s)" % (
        typ, anzahl, ln, erg["je_takt"], erg.get("grund") or "%d Takte, Lord -%d" % (erg["takte"], erg["lord_verlust"])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
