# -*- coding: utf-8 -*-
"""Aus der Aufzeichnung von Lauf F: wann aendern sich Waren von Spieler 1 und Kalender? Nur lesen."""
import json, struct, sys, zlib
sys.path.insert(0, "src")
from selfaware.tools.analysis.auge_auswertung import RAHMEN, KENNUNG, VOLL

PFAD = "data/research/auge_plan/laeufe/lauf_f_20261102_184744.auge"
AUS = sys.argv[1]
SP, SCHRITT, WAREN = 0x0115BDF8, 0x39F4, 0x4D0
WANAMEN = {2: "Holz", 3: "Hopfen", 4: "Stein", 6: "Eisen", 7: "Pech", 9: "Weizen", 10: "Brot", 11: "Kaese", 12: "Fleisch", 13: "Apfel", 14: "Bier", 15: "Gold", 16: "Mehl", 17: "Bogen", 18: "Armbrust", 19: "Speer", 20: "Pike", 21: "Keule", 22: "Schwert", 23: "Leder", 24: "Ruestung"}
FELDER = {"week": 0x117cab0, "keepGranary": 0x117c790}

f = open(PFAD, "rb")
f.read(len(KENNUNG))
n = struct.unpack("<I", f.read(4))[0]
kopf = json.loads(f.read(n).decode("utf-8"))
namen = [b[0] for b in kopf["bereiche"]]
g = namen.index("DAT_GameState")
basis = kopf["bereiche"][g][1]
w0 = SP + SCHRITT + WAREN - basis
puffer = None
alt_w = None
alt_f = {}
ereignisse = []
rahmen = 0
while True:
    k = f.read(RAHMEN.size)
    if len(k) < RAHMEN.size:
        break
    art, b, merker, vor, nach, zeit, dauer, rohl, zl = RAHMEN.unpack(k)
    if b != g:
        f.seek(zl + 4, 1)
        continue
    z = f.read(zl)
    f.read(4)
    nutz = zlib.decompress(z)
    rahmen += 1
    if art == VOLL:
        puffer = bytearray(nutz)
    else:
        i = 0
        while i < len(nutz):
            o, l = struct.unpack_from("<II", nutz, i)
            i += 8
            puffer[o:o + l] = nutz[i:i + l]
            i += l
    w = struct.unpack_from("<25i", puffer, w0)
    if alt_w is None:
        ereignisse.append(("start", vor, {WANAMEN.get(a, a): w[a] for a in range(25) if w[a]}))
    elif w != alt_w:
        ereignisse.append(("ware", vor, {WANAMEN.get(a, a): (alt_w[a], w[a]) for a in range(25) if w[a] != alt_w[a]}))
    alt_w = w
    for name, adr in FELDER.items():
        v = struct.unpack_from("<i", puffer, adr - basis)[0]
        if alt_f.get(name) != v:
            ereignisse.append((name, vor, v))
            alt_f[name] = v
print("Rahmen GameState", rahmen, "Ereignisse", len(ereignisse))
with open(AUS, "w", encoding="utf-8") as a:
    for e in ereignisse:
        a.write(json.dumps(e, ensure_ascii=False) + "\n")
