# -*- coding: utf-8 -*-
"""B-253 Test des Taktring-Gegendrucks (Daniel 26.10. 21:04): Sandkasten-Gefecht wie auge_gefecht.py aufstellen, <vorlauf> s
laufen lassen (bis viele Einheiten da sind - vorher gab es auch ohne Gegendruck keine Luecken), dann im selben Gefecht
<sek> s OHNE und <sek> s MIT Gegendruck aufnehmen und je Takt-Luecken, doppelte Takte und Takte/s melden.
Aufruf (Sandkasten muss angehalten bereitstehen, z. B. shc.py sandkasten):
    python werkzeug/engine_knowledge/auge_gegendruck_test.py [sek=20] [vorlauf=60]
"""
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HIER))
sys.path.insert(0, HIER)
import auge  # noqa: E402
import shc  # noqa: E402
import speicher  # noqa: E402
from laden import befehl  # noqa: E402
from auge_pruefen import freie_reihe  # noqa: E402
from auge_gefecht import aufstellen  # noqa: E402

DATEN = os.path.join(os.path.dirname(os.path.dirname(HIER)), "daten")


def bewerten(name, p, dauer):
    t = list(p.takte)
    luecken = [b - a for a, b in zip(t, t[1:]) if b - a > 1]
    return {"teil": name, "takte": [min(t), max(t)] if t else None, "schnappschuesse": len(t),
            "luecken": len(luecken), "fehlende_takte": int(sum(x - 1 for x in luecken)),
            "doppelt_oder_rueckwaerts": int(sum(1 for a, b in zip(t, t[1:]) if b <= a)),
            "takte_je_s": round(len(t) / dauer, 1) if dauer else None,
            "einheiten_je_takt_ende": int(len(p.einheiten[-1])) if p.einheiten else None}


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    sek = float(a[0]) if a else 20.0
    vorlauf = float(a[1]) if len(a) > 1 else 60.0
    z = shc.zustand()
    if z.get("gameover") or not z.get("pause"):
        print("FEHLER: nicht bespielbar/angehalten", z)
        return 1
    s = auge.Schnappschuss()
    lord = next((q["lord"]["feld"] for q in s.spieler_liste() if q["spieler"] == 1 and "feld" in q["lord"]), None)
    k = speicher.wegkarte()
    reihe = None
    for versuch in range(60):
        r = freie_reihe((lord[0], lord[1] + 6 + versuch), 24, suchweite=30)
        if r and all((k["gebiet"][r[1]:r[1] + 24, r[2] + dy] > 0).all() and (k["gebaeude"][r[1]:r[1] + 24, r[2] + dy] == 0).all()
                     for dy in (1, 14, 15)):
            reihe = r
            break
    _, x0, y = reihe
    aufstellen(1, x0, y, k)
    aufstellen(2, x0, y + 14, k)
    befehl({"pause": False, "tempo": 100}, 0.2)
    print("Vorlauf %d s ..." % vorlauf, flush=True)
    time.sleep(vorlauf)
    erg = []
    for name, gd in (("ohne Gegendruck", False), ("mit Gegendruck", True)):
        stempel = time.strftime("%Y%m%d_%H%M%S")
        t0 = time.time()
        pfad, p = auge.protokollieren(sek, None, os.path.join(DATEN, "gegendruck_%s_%s.npz" % ("an" if gd else "aus", stempel)),
                                      mit_trupps=False, alle_takte=1, gegendruck=gd)
        e = bewerten(name, p, time.time() - t0)
        e["datei"] = os.path.basename(pfad)
        erg.append(e)
        print(json.dumps(e, ensure_ascii=False), flush=True)
    befehl({"pause": True}, 0.2)
    aus = os.path.join(DATEN, "gegendruck_test_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
    json.dump(erg, open(aus, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("->", aus)
    return 0


if __name__ == "__main__":
    sys.exit(main())
