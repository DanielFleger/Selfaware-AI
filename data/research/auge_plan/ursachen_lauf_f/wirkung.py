# -*- coding: utf-8 -*-
"""Lauf F: welche Felder aendern sich je Abschnitt, die vorher nie geaendert wurden? Nur lesen. Gibt die Wirkung je Abschnitt."""
import collections, json, struct, sys, zlib
sys.path.insert(0, "src")
from selfaware.tools.analysis.auge_auswertung import RAHMEN, KENNUNG, VOLL
from selfaware.tools.analysis.auge_feldkarte import Feldkarte

PFAD = "data/research/auge_plan/laeufe/lauf_f_20261102_184744.auge"
PROT = "data/research/auge_plan/laeufe/lauf_f_20261102_184744.protokoll.jsonl"
phasen = []
for z in open(PROT, encoding="utf-8"):
    e = json.loads(z)
    if "phase" in e and "takt_von" in e:
        phasen.append((e["phase"], e["takt_von"], e["takt_bis"]))
print(phasen)
karte = Feldkarte.laden()
NUR = {"DAT_GameState", "DAT_TribesState", "DAT_GameCore", "DAT_BuildingsState", "DAT_UnitsState"}
f = open(PFAD, "rb")
f.read(len(KENNUNG))
n = struct.unpack("<I", f.read(4))[0]
kopf = json.loads(f.read(n).decode("utf-8"))
ber = kopf["bereiche"]
zuerst = {}
je = collections.defaultdict(collections.Counter)
gesamt = beschaedigt = 0
cache = {}
while True:
    k = f.read(RAHMEN.size)
    if len(k) < RAHMEN.size:
        break
    art, b, merker, vor, nach, zeit, dauer, rohl, zl = RAHMEN.unpack(k)
    if ber[b][0] not in NUR or art == VOLL:
        f.seek(zl + 4, 1)
        continue
    z = f.read(zl)
    f.read(4)
    try:
        nutz = zlib.decompress(z)
    except zlib.error:
        beschaedigt += 1
        continue
    basis = ber[b][1]
    ph = next((p[0] for p in phasen if p[1] <= vor <= p[2]), "dazwischen")
    i = 0
    while i < len(nutz):
        o, l = struct.unpack_from("<II", nutz, i)
        i += 8 + l
        s = (basis + o, l)
        v = cache.get(s)
        if v is None:
            v = karte.felder_einer_aenderung(basis + o, l)
            cache[s] = v
        for fe in v:
            je[ph][fe] += 1
            if fe not in zuerst:
                zuerst[fe] = ph
print("beschaedigt", beschaedigt)
for p in [x[0] for x in phasen]:
    neu = [(g.replace("DAT_", ""), n) for (g, n), ph in zuerst.items() if ph == p]
    print("==", p, "neue Felder", len(neu))
    print("  ", sorted(n for g, n in neu if g == "GameState")[:60])
    print("   Stamm/Einheiten:", collections.Counter(g for g, n in neu).most_common())
json.dump({"zuerst": [[*k, v] for k, v in zuerst.items()], "phasen": phasen}, open(sys.argv[1], "w", encoding="utf-8"))
