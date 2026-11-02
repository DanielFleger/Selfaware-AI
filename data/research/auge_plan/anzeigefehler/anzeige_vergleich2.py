# -*- coding: utf-8 -*-
"""B-144 Nachprobe: Sind Eingang und surfaceAreaUnk Zufall der Stelle oder haengen sie am Wert? Je Art 6 Kopien, 3 mit 15, 3 mit 0, abwechselnd.
Dazu Eisenmine und Steinbruch, die im ersten Vergleich zu wenig weit auseinanderliegende Stellen hatten."""
import collections, json, os, struct, sys, time
sys.path.insert(0, "src")
from selfaware.game.ucp import bauen, laden
from selfaware.tools.analysis.auge_feldkarte import Feldkarte
from selfaware.tools.experiments import auge_lauf_f as lf, anzeige_reparieren as ar

ordner = sys.argv[1]
TMP = os.path.join(ordner, "platz4.txt")
k = lf.EchterKanal()
spiel = ar.Spiel(2, laden.befehl)
if spiel.wert(ar.PAUSE) != 1:
    raise SystemExit("Spiel laeuft, abgebrochen")
k.befehl({"eigenerPlatz": 1}, 0.5)


def laufe(n):
    t0 = spiel.wert(ar.TICK)
    laden.befehl({"tickpause": {"bei": t0 + n}}, 0.15)
    laden.befehl({"pause": False}, 0.05)
    ende = time.time() + 30
    while time.time() < ende:
        if spiel.wert(ar.TICK) >= t0 + n and spiel.wert(ar.PAUSE) == 1:
            return
        time.sleep(0.01)
    laden.befehl({"pause": True}, 0.2)
    raise SystemExit("Takte kamen nicht an")


def eintraege():
    roh = spiel.q.lies(ar.GEBAEUDE, ar.SCHRITT * ar.ANZAHL)
    aus = {}
    for i in range(1, ar.ANZAHL):
        b = i * ar.SCHRITT
        if struct.unpack_from("<h", roh, b + ar.ZUSTAND)[0]:
            aus[i] = {"typ": struct.unpack_from("<h", roh, b + ar.TYP)[0], "v": struct.unpack_from("<h", roh, b + ar.BILDWERT)[0],
                      "x": struct.unpack_from("<h", roh, b + 0x102)[0], "y": struct.unpack_from("<h", roh, b + 0x104)[0], "roh": roh[b:b + ar.SCHRITT]}
    return aus


fk = Feldkarte.laden()
felder = collections.defaultdict(list)
for o in range(ar.SCHRITT):
    t = fk.felder_einer_aenderung(ar.GEBAEUDE + ar.SCHRITT + o, 1)
    felder[t[0][1] if t else f"+0x{o:x}"].append(o)
ERGEBNIS = {}
for typ, abstand in ((27, 20), (30, 25), (32, 25), (37, 25), (5, 8), (20, 9)):
    g = bauen.NACH_TYP[typ]
    gut, alle, _ = bauen.platzkarte(typ, 0, 0, 399, 399, TMP)
    z = open(TMP, encoding="utf-8").read().splitlines()[1:]
    stellen = []
    for y, zeile in enumerate(z):
        for x, c in enumerate(zeile):
            if c == "+" and all(max(abs(x - a), abs(y - e)) >= abstand for a, e in stellen):
                stellen.append((x, y))
            if len(stellen) == 6:
                break
        if len(stellen) == 6:
            break
    vorher = set(eintraege())
    werte = [15 if i % 2 == 0 else 0 for i in range(len(stellen))]
    k.liste([{"spielbefehl": {"nr": 28, "werte": [x, y, g["mapper"], g["b"], w, 0]}} for (x, y), w in zip(stellen, werte)], 0.15)
    laufe(4)
    neu = {(e["x"], e["y"]): e for n, e in eintraege().items() if n not in vorher and e["typ"] == typ}
    gebaut = [(s, w, neu[s]) for s, w in zip(stellen, werte) if s in neu]
    aufgeteilt = {}
    trennt = []
    for name, os_ in felder.items():
        wert15 = {bytes(e["roh"][o] for o in os_) for _, w, e in gebaut if w == 15}
        wert0 = {bytes(e["roh"][o] for o in os_) for _, w, e in gebaut if w == 0}
        if wert15 and wert0 and not (wert15 & wert0) and len(wert15) == 1 and len(wert0) == 1:
            trennt.append(name)   # innerhalb einer Gruppe gleich, zwischen den Gruppen verschieden: haengt am Wert
    ERGEBNIS[typ] = {"name": g.get("name"), "stellen": len(stellen), "gebaut": len(gebaut), "v": [e["v"] for _, _, e in gebaut], "trennt": trennt}
    print(typ, g.get("name"), "Stellen", len(stellen), "gebaut", len(gebaut), "Werte", [e["v"] for _, _, e in gebaut], "trennt genau:", trennt, flush=True)
json.dump(ERGEBNIS, open(os.path.join(ordner, "vergleich2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("Geladen:", laden.lade_stand("Anzeigebug repariert", mit_bild=False), flush=True)
k.befehl({"eigenerPlatz": 1}, 0.5)
k.befehl({"pause": True}, 0.3)
print("Falsche Werte:", len(ar.falsche(spiel.gebaeude())), "Platz", spiel.wert(0x1a275dc), "Takt", spiel.wert(ar.TICK), "Pause", spiel.wert(ar.PAUSE), "Drehung", spiel.wert(ar.DREHUNG), flush=True)
a = spiel.wert(ar.TICK); time.sleep(1.0); print("steht" if a == spiel.wert(ar.TICK) else "LAEUFT", flush=True)
