# -*- coding: utf-8 -*-
"""B-144: Haengt ausser dem Bild etwas am Wert? Je Art drei Kopien im selben Takt per Rohbefehl: 15, 15, 0; Vergleich je Feld."""
import collections, json, os, struct, sys, time
sys.path.insert(0, "src")
from selfaware.game.ucp import bauen, laden
from selfaware.tools.analysis.auge_feldkarte import Feldkarte
from selfaware.tools.experiments import auge_lauf_f as lf, anzeige_reparieren as ar

ordner = sys.argv[1]
TMP = os.path.join(ordner, "platz3.txt")
k = lf.EchterKanal()
spiel = ar.Spiel(2, laden.befehl)
if spiel.wert(ar.PAUSE) != 1:
    raise SystemExit("Spiel laeuft, abgebrochen")
print("Spielerplatz nach dem Laden:", spiel.wert(0x1a275dc), flush=True)
k.befehl({"eigenerPlatz": 1}, 0.5)  # ohne ihn baut man nach dem Laden still fuer den neutralen Spieler 0 (Wissensstand, Lua eigenerPlatz)


def laufe(n):
    t0 = spiel.wert(ar.TICK)
    laden.befehl({"tickpause": {"bei": t0 + n}}, 0.15)
    laden.befehl({"pause": False}, 0.05)
    ende = time.time() + 30  # Schutz gegen Haengen
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
print("Felder im Eintrag:", len(felder), flush=True)
AUS = {41, 6, 10, 11, 19, 68} | ar.TORE  # Burg nur einmal, Pechgrube ohne Boden, Lager/Waffenlager/Kornspeicher nur neben dem ersten, Pechgraben ohne Eintrag
ergebnis, wirkung = {}, collections.defaultdict(list)
for typ in [t for t in sorted(bauen.NACH_TYP) if t not in AUS]:
    g = bauen.NACH_TYP[typ]
    gut, alle, _ = bauen.platzkarte(typ, 0, 0, 399, 399, TMP)
    z = open(TMP, encoding="utf-8").read().splitlines()[1:]
    abstand = max(20, g["b"] * 3)
    stellen = []
    for y, zeile in enumerate(z):
        for x, c in enumerate(zeile):
            if c == "+" and all(abs(x - a) >= abstand and abs(y - e) >= abstand for a, e in stellen):
                stellen.append((x, y))
            if len(stellen) == 3:
                break
        if len(stellen) == 3:
            break
    if len(stellen) < 3:
        ergebnis[typ] = {"name": g.get("name"), "ergebnis": "zu wenig Stellen"}
        print(typ, g.get("name"), "zu wenig Stellen", flush=True)
        continue
    vorher = set(eintraege())
    k.liste([{"spielbefehl": {"nr": 28, "werte": [x, y, g["mapper"], g["b"], w, 0]}} for (x, y), w in zip(stellen, (15, 15, 0))], 0.15)
    laufe(4)
    neu = {(e["x"], e["y"]): e for n, e in eintraege().items() if n not in vorher and e["typ"] == typ}
    if not all(s in neu for s in stellen):
        ergebnis[typ] = {"name": g.get("name"), "ergebnis": f"nur {len(neu)} gebaut"}
        print(typ, g.get("name"), "nur", len(neu), "gebaut", flush=True)
        continue
    a, b, c = (neu[s]["roh"] for s in stellen)
    nur = sorted(n for n, os_ in felder.items() if any(a[o] != c[o] for o in os_) and all(a[o] == b[o] for o in os_))
    werte = [neu[s]["v"] for s in stellen]
    ergebnis[typ] = {"name": g.get("name"), "werte": werte, "nur_am_wert": nur}
    for n in nur:
        wirkung[n].append(typ)
    print(typ, g.get("name"), "Werte", werte, "nur am Wert:", nur, flush=True)
json.dump({"arten": ergebnis, "wirkung": wirkung}, open(os.path.join(ordner, "vergleich.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("Felder, die am Wert haengen:", {n: v for n, v in wirkung.items()}, flush=True)
print("Geladen:", laden.lade_stand("Anzeigebug repariert", mit_bild=False), "Pause", spiel.wert(ar.PAUSE), "Drehung", spiel.wert(ar.DREHUNG), flush=True)
print("Falsche Werte im geladenen Stand:", len(ar.falsche(spiel.gebaeude())), flush=True)
print("Spielerplatz am Ende:", spiel.wert(0x1a275dc), "Takt", spiel.wert(ar.TICK), flush=True)
