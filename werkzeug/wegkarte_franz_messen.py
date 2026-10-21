# -*- coding: utf-8 -*-
# B-161 Beleg (21.10.2026 22:05): alte gegen neue sichere Wege an Franz Burg im LAUFENDEN Spiel (Instanz 5, angehalten bei Takt
# 74.036) - Einheiten direkt aus dem Speicher, Gebaeude aus dem Lagebild 21:34. Ergebnis damals: alte Wege 17-77 Felder durch
# Mauern, 4 von 9 Stellen unerreichbar, 0 von 39 Schuetzen zu Fuss erreichbar. Aufruf (in werkzeug/): SHC_INSTANZ=5 python wegkarte_franz_messen.py
import gzip, json, sys
sys.path.insert(0, ".")
import numpy as np
import gefahr as GF, gefecht, feldzug, speicher
w = speicher.wegkarte()
raw = speicher.lies(0x0138854C, 2500 * 1168)
def f(b, o, n=2, s=True): return int.from_bytes(raw[b + o:b + o + n], "little", signed=s)
L = {}
for i in range(1, 2500):
    b = i * 1168
    if f(b, 0x8C) != 0 and f(b, 0x3C8, 4) > 0:
        L[i] = {"besitzer": f(b, 0x96), "typ": f(b, 0x8E), "x": f(b, 0xC4), "y": f(b, 0xC6), "leben": f(b, 0x3C8, 4)}
G = {}
for z in gzip.open("../daten/lage_20261021_213455_i5.jsonl.gz", "rt", encoding="utf-8"):
    d = json.loads(z)
kopf = None
for r in d["gebaeude"].split("\n"):
    t = r.split()
    if t and t[0] == "nr":
        kopf = t; continue
    if kopf and len(t) == len(kopf):
        e = dict(zip(kopf, map(int, t))); G[e["nr"]] = e
bed = GF.bedrohungen(L, G, lambda b: b == 2, gefecht.FERN_REICH)
alt, neu = GF.Karte(bed), GF.Karte(bed, gebiete=w["gebiet"])
eig = [e for e in L.values() if e["besitzer"] == 1 and e["typ"] == 26]
m = (sorted(e["x"] for e in eig)[len(eig) // 2], sorted(e["y"] for e in eig)[len(eig) // 2])
lords = [e for e in L.values() if e["besitzer"] == 2 and e["typ"] == 55]
if not lords:
    raise SystemExit("kein lebender Lord von Spieler 2 im laufenden Spiel - die Messung braucht den Pruefstand vor Franz' Burg")
lord = lords[0]
lp = (lord["x"], lord["y"])
print("Streitkolben %d, Mitte %s Gebiet %d | Lord %s Gebiet %d | Schuetzen %d, davon zu Fuss erreichbar %d" % (
    len(eig), m, neu.gebiet_bei(m), lp, w["gebiet"][lp], sum(1 for b in bed if b[4].startswith("schuetze")),
    len(GF.erreichbare_schuetzen(m, neu))))
def felder(k, weg):
    out, a = [], m
    for b in weg:
        out += k.linie(a, b)[1:]; a = b
    return out
g0 = neu.gebiet_bei(m)
kand = [(n, g) for n, g in G.items() if g["besitzer"] == 2 and g["typ"] in feldzug.BURG_TEILE and GF.schach((g["x"], g["y"]), lp) <= feldzug.Feldzug.BURG_R]
for n, g in [(0, {"x": lp[0], "y": lp[1], "typ": 55})] + kand:
    z = (g["x"], g["y"])
    wa, wn = GF.sicherer_weg(m, z, alt), GF.sicherer_weg(m, z, neu)
    fa = felder(alt, wa) if wa else []
    print("%-5s Typ %3d %s | alt: %2d Punkte, %3d Felder nicht im Gebiet %d, Gefahr %4d | neu: %s Ende %s (Gebiet %s, %s Felder vom Ziel), Gefahr %s" % (
        n or "Lord", g["typ"], z, len(wa or []), sum(1 for p in fa if w["gebiet"][p] != g0), g0, GF.weg_gefahr(m, wa or [z], alt),
        "%2d Punkte" % len(wn) if wn else "KEIN WEG", wn and wn[-1], wn and w["gebiet"][wn[-1]], wn and GF.schach(wn[-1], z),
        wn and GF.weg_gefahr(m, wn, neu)))
