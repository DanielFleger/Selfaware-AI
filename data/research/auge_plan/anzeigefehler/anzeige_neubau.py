# -*- coding: utf-8 -*-
"""B-144 Hauptprobe: frischer Burgenbau, jede Art mit dem Wert des Mausklicks; vier Drehungen; Vergleich 15/15/0 je Art."""
import collections, json, math, os, struct, sys, time
sys.path.insert(0, "src")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from selfaware.game.ucp import bauen, laden
from selfaware.game.ucp.drehwert import drehwert
from selfaware.game.ucp.befehl import LOG
from selfaware.tools.experiments import auge_lauf_f as lf, anzeige_reparieren as ar

ordner = sys.argv[1]
TMP = os.path.join(ordner, "platz.txt")
BURG = 41
protokoll = {"gebaut": [], "vergleich": {}, "wirkung": {}}


def merke():
    json.dump(protokoll, open(os.path.join(ordner, "neubau.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)


# 1. Modul
ziel = os.path.join(lf.ordner(2), "ucp", "villagestudio", "logik.lua")
quelle = os.path.join(lf.ordner(lf.QUELL_INSTANZ), "ucp", "villagestudio", "logik.lua")
fehler = lf.lua_fehler(lf.logik_text(quelle))
if fehler:
    raise SystemExit("logik.lua hat einen Fehler: " + str(fehler))
vorher_log = os.path.getsize(LOG)
print("Sicherung logik.lua:", lf.logik_einspielen(ziel, quelle), flush=True)
ende = time.time() + 20
gesehen = False
while time.time() < ende and not gesehen:
    with open(LOG, encoding="utf-8", errors="replace") as f:
        f.seek(vorher_log)
        gesehen = "logik.lua neu geladen" in f.read()
    time.sleep(0.5)
print("Modul neu geladen:", gesehen, flush=True)
if not gesehen:
    raise SystemExit("Modul hat die neue logik.lua nicht geladen")

# 2. Frisches Spiel
k = lf.EchterKanal()
print(lf.burgenbau_starten(k), flush=True)
k.befehl({"pause": True}, 0.5)
spiel = ar.Spiel(2, laden.befehl)
print("Pause", spiel.wert(ar.PAUSE), "Takt", spiel.wert(ar.TICK), "Drehung", spiel.wert(ar.DREHUNG), flush=True)


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
                      "x": struct.unpack_from("<h", roh, b + 0x102)[0], "y": struct.unpack_from("<h", roh, b + 0x104)[0], "sp": struct.unpack_from("<h", roh, b + ar.BESITZER)[0], "roh": roh[b:b + ar.SCHRITT]}
    return aus


def karte(typ):
    gut, alle, _ = bauen.platzkarte(typ, 0, 0, 399, 399, TMP)
    return gut, open(TMP, encoding="utf-8").read().splitlines()[1:]


def naechste(zeilen, anker):
    best = None
    for y, z in enumerate(zeilen):
        for x, c in enumerate(z):
            if c == "+":
                d = max(abs(x - anker[0]), abs(y - anker[1]))
                if best is None or d < best[0]:
                    best = (d, x, y)
    return best


def baue(typ, x, y, wert):
    g = bauen.NACH_TYP[typ]
    return {"baue": {"mapper": g["mapper"], "x": x, "y": y, "groesse": g["b"], "richtung": wert}}


def spirale(mitte, schritt, n):
    orte = [(mitte[0] + i * schritt, mitte[1] + j * schritt) for i in range(-6, 7) for j in range(-6, 7) if (i, j) != (0, 0)]
    orte.sort(key=lambda p: (max(abs(p[0] - mitte[0]), abs(p[1] - mitte[1])), p))
    return orte[:n]


# 3. Burg, dann jede Art einmal, weit auseinander
gut, z = karte(BURG)
d, bx, by = naechste(z, (212, 188))
laden.befehl(baue(BURG, bx, by, drehwert(bauen.NACH_TYP[BURG]["mapper"])), 0.2)
laufe(20)
e0 = eintraege()
print("Burg:", [(n, e["typ"], e["x"], e["y"], e["v"]) for n, e in e0.items() if e["typ"] == BURG], flush=True)
arten = [t for t in sorted(bauen.NACH_TYP) if t != BURG]
for typ, anker in zip(arten, spirale((bx, by), 10, len(arten))):
    gut, z = karte(typ)
    wert = drehwert(bauen.NACH_TYP[typ]["mapper"])
    eintrag = {"typ": typ, "name": bauen.NACH_TYP[typ].get("name"), "erlaubt": gut, "soll": wert}
    if not gut:
        eintrag["ergebnis"] = "keine erlaubte Stelle"
    else:
        d, x, y = naechste(z, anker)
        vorher = set(eintraege())
        laden.befehl(baue(typ, x, y, wert), 0.15)
        laufe(20)
        neu = {n: e for n, e in eintraege().items() if n not in vorher and e["typ"] == typ}
        eintrag["ort"] = (x, y)
        if neu:
            werte = sorted({e["v"] for e in neu.values()})
            eintrag.update(v=werte, ergebnis="steht" if werte == [wert] else "FALSCHER WERT")
        elif typ == 68:
            d = spiel.q.lies(33366668, 20 * 4000)
            n_pech = sum(1 for i in range(1, 4000) if struct.unpack_from("<h", d, i * 20 + 8)[0])
            eintrag.update(pechgraeben=n_pech, ergebnis="steht" if n_pech else "NICHT GEBAUT")
        else:
            eintrag["ergebnis"] = "NICHT GEBAUT"
    protokoll["gebaut"].append(eintrag)
    print(typ, eintrag.get("name"), eintrag.get("ort"), eintrag["ergebnis"], eintrag.get("v"), flush=True)
merke()
print("Ergebnis Einzelbau:", collections.Counter(e["ergebnis"] for e in protokoll["gebaut"]).most_common(), flush=True)

# 4. Vier Drehungen, im frischen Stand ohne jede Reparatur (Drehen zeichnet neu, Start ist die Standardansicht)
import anzeige
protokoll["drehungen"] = [(a, z) for a, z, _ in anzeige.alle_drehungen(ordner, "neu")]
print("Werte nach dem Kreis:", collections.Counter(e["v"] for e in eintraege().values()).most_common(), flush=True)
merke()

# 5. Je Art drei Kopien im selben Takt: 15, 15 und 0. Was nur zwischen 15 und 0 abweicht, haengt am Wert
from selfaware.tools.analysis.auge_feldkarte import Feldkarte
fk = Feldkarte.laden()
name_von = {}
for o in range(ar.SCHRITT):
    t = fk.felder_einer_aenderung(ar.GEBAEUDE + ar.SCHRITT + o, 1)
    name_von[o] = t[0][1] if t else f"+0x{o:x}"
AUS = {BURG, 6, 10, 11, 19, 68} | ar.TORE  # Burg nur einmal, Pechgrube ohne Boden, Lager/Kornspeicher nur neben dem ersten, Pechgraben ohne Eintrag
wirkung = collections.defaultdict(list)
for typ in [t for t in sorted(bauen.NACH_TYP) if t not in AUS]:
    gut, z = karte(typ)
    b = bauen.NACH_TYP[typ]["b"]
    stellen = []
    for y, zeile in enumerate(z):
        for x, c in enumerate(zeile):
            if c == "+" and all(max(abs(x - a), abs(y - e)) >= b + 4 for a, e in stellen):
                stellen.append((x, y))
                if len(stellen) == 3:
                    break
        if len(stellen) == 3:
            break
    if len(stellen) < 3:
        protokoll["vergleich"][typ] = "zu wenig Stellen"
        continue
    vorher = set(eintraege())
    k.liste([baue(typ, *stellen[0], 15), baue(typ, *stellen[1], 15), baue(typ, *stellen[2], 0)], 0.15)
    laufe(4)
    neu = {(e["x"], e["y"]): e for n, e in eintraege().items() if n not in vorher and e["typ"] == typ}
    if not all(s in neu for s in stellen):
        protokoll["vergleich"][typ] = {"nicht alle gebaut": len(neu)}
        print(typ, "nicht alle gebaut", len(neu), flush=True)
        continue
    a, b2, c = (neu[s]["roh"] for s in stellen)
    kontrolle = {o for o in range(ar.SCHRITT) if a[o] != b2[o]}
    test = {o for o in range(ar.SCHRITT) if a[o] != c[o]}
    felder = sorted({name_von[o] for o in test - kontrolle})
    protokoll["vergleich"][typ] = {"v": [neu[s]["v"] for s in stellen], "nur_am_wert": felder, "kontrolle": len(kontrolle)}
    for f in felder:
        wirkung[f].append(typ)
    print(typ, bauen.NACH_TYP[typ].get("name"), "Werte", [neu[s]["v"] for s in stellen], "nur am Wert:", felder, flush=True)
protokoll["wirkung"] = dict(wirkung)
merke()
print("Felder, die am Wert haengen:", {k_: len(v_) for k_, v_ in wirkung.items()}, flush=True)

# 6. Zurueck auf den reparierten Stand
print("Geladen:", laden.lade_stand("Anzeigebug repariert", mit_bild=False), "Pause", spiel.wert(ar.PAUSE), "Drehung", spiel.wert(ar.DREHUNG), flush=True)
