# -*- coding: utf-8 -*-
"""B-149 Sandkasten (Daniel 21.10.2026 18:17 "du kannst in die Sandbox und Angriffe ausprobieren, Castles nachbauen und
Laufwege erproben"): Franz' Burg aus dem Pruefstand-Spielstand, die Heere abgeraeumt (Lords bleiben), Franz' KI ohne Waren;
dann gezielt Truppen setzen, EINEN Befehl geben und in festen Abstaenden messen. Jede Messung eine Zeile in
daten/sandkasten.jsonl.

Aufruf (Instanz 5):
  SHC_INSTANZ=5 python sandkasten.py a_turm [gebaeude=241] [anzahl=20] [typ=26] [takte=4000] [von=160,186] [franz_heer=nein]

Versuche (Widerlegung steht je Versuch im Code und in der Ausgabe):
  a_turm   Nahkaempfer greifen einen Turm/ein Torhaus an (Befehl 36 Art 9) - nimmt er Schaden?
"""
import json
import os
import re
import sys
import time

os.environ.setdefault("SHC_INSTANZ", "5")
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "..", "Selfaware-AI-kern", "src"))
from laden import lade_stand, befehl  # noqa: E402
from selfaware.game.kern_leitung import Leitung  # noqa: E402

STAND = "B140 Burg Franz T40126"
SPIEL = r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme Instanz%s" % os.environ["SHC_INSTANZ"]
AUS = os.path.join(HIER, "..", "daten", "sandkasten.jsonl")
le = Leitung(SPIEL)


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def welt():
    return le.lesen()


def laufen(takte, tempo=300):
    """Spiel takte Takte laufen lassen, dann anhalten. Gibt den Tick danach."""
    t0 = welt().tick
    befehl({"pause": False, "tempo": tempo}, 0.2)
    while welt().tick < t0 + takte:
        time.sleep(0.2)
    befehl({"pause": True}, 0.3)
    return welt().tick


def vorbereiten(franz_heer=False):
    """Spielstand laden, beide Heere ohne Lord abraeumen, Franz' KI ohne Waren. Gibt Einheiten je Spieler danach."""
    lade_stand(STAND, mit_bild=False)
    befehl({"eigenerPlatz": 1}, 0.8)
    laufen(5, 40)                                  # (ohne Takt hat der Kern noch die Welt vor dem Laden)
    befehl({"leereKI": [2]}, 0.5)
    befehl({"toeteAlle": {"spieler": 1, "ohneLord": True}}, 0.8)
    if not franz_heer:
        befehl({"toeteAlle": {"spieler": 2, "ohneLord": True}}, 0.8)
    laufen(400, 100)                               # Steintod abwarten
    w = welt()
    zahl = {}
    for e in w.einheiten.values():
        if e["leben"] > 0:
            zahl[e["besitzer"]] = zahl.get(e["besitzer"], 0) + 1
    return w.tick, zahl


def setze(spieler, typ, anzahl, x, y):
    """Einheiten setzen (setzeEinheit -> spawnUnit). Gibt ihre Nummern."""
    for z in befehl({"setzeEinheit": {"spieler": spieler, "typ": typ, "x": x, "y": y, "anzahl": anzahl}}, 1.0):
        m = re.search(r"Nummern ([0-9,]+)", z)
        if m:
            return [int(n) for n in m.group(1).split(",") if int(n) > 0]
    raise RuntimeError("setzeEinheit ohne Nummern")


def schreibe(zeile):
    zeile["zeit"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(AUS, "a", encoding="utf-8") as f:
        f.write(json.dumps(zeile, ensure_ascii=False) + "\n")


def a_turm(gebaeude=241, anzahl=20, typ=26, takte=4000, von=(160, 186), franz_heer=False):
    """Widerlegt ("Nahkaempfer beschaedigen den Turm auf Befehl 36 Art 9"), wenn der Turm nach `takte` Takten noch sein
    volles Leben hat."""
    t, zahl = vorbereiten(franz_heer)
    g0 = welt().gebaeude.get(gebaeude)
    if g0 is None:
        raise SystemExit("Gebaeude %d gibt es im Spielstand nicht" % gebaeude)
    nrs = setze(1, typ, anzahl, von[0], von[1])
    laufen(3, 40)
    befehl({"angriff": {"einheiten": nrs, "gebaeude": gebaeude}}, 1.0)
    ort = (g0["x"], g0["y"])
    verlauf = []
    for k in range(takte // 500):
        tick = laufen(500)
        w = welt()
        g = w.gebaeude.get(gebaeude)
        leben = [w.einheiten[n] for n in nrs if n in w.einheiten and w.einheiten[n]["leben"] > 0]
        nah = [e for e in leben if schach((e["x"], e["y"]), ort) <= 3]
        zust = {}
        for e in leben:
            zust[e["zustand"]] = zust.get(e["zustand"], 0) + 1
        verlauf.append({"tick": tick, "leben_gebaeude": g["leben"] if g else 0, "lebend": len(leben), "bis_3_felder": len(nah),
                        "zustaende": zust, "naechster": min((schach((e["x"], e["y"]), ort) for e in leben), default=None)})
        print(verlauf[-1], flush=True)
        if g is None:
            break
    ende = verlauf[-1]["leben_gebaeude"]
    ergebnis = "WIDERLEGT (kein Schaden)" if ende >= g0["leben"] else "Schaden %d -> %d" % (g0["leben"], ende)
    zeile = {"versuch": "a_turm", "gebaeude": gebaeude, "typ_gebaeude": g0["typ"], "ort": ort, "leben_vorher": g0["leben"],
             "anzahl": anzahl, "typ": typ, "von": von, "franz_heer": franz_heer, "einheiten_nach_abraeumen": zahl,
             "verlauf": verlauf, "ergebnis": ergebnis}
    schreibe(zeile)
    print("ERGEBNIS a_turm:", ergebnis)
    return zeile


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    a = dict(x.split("=", 1) for x in sys.argv[2:])
    if sys.argv[1] == "a_turm":
        a_turm(int(a.get("gebaeude", 241)), int(a.get("anzahl", 20)), int(a.get("typ", 26)), int(a.get("takte", 4000)),
               tuple(int(v) for v in a.get("von", "160,186").split(",")), a.get("franz_heer", "nein") == "ja")
    else:
        raise SystemExit("unbekannter Versuch %s\n%s" % (sys.argv[1], __doc__))
