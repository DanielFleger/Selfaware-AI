# -*- coding: utf-8 -*-
# B-160 Beleg (21.10.2026 21:44): Zeit der Wegsuche am Lagebild der langsamen Runde (Pruefstand 21:34, Takt 59.105) - 5 Ziele
# einzeln + Profil. Aufruf (in werkzeug/): python wegsuche_zeit_messen.py [Takt]. Alt (A* je Ziel): 0,17-1,19 s, 9 Stellen 4,8 s;
# neu (Karte + MCP): 0,02-0,04 s je Ziel.
import gzip, json, sys, time, cProfile, pstats, os
sys.path.insert(0, ".")
import gefahr as GF, gefecht
p = "../daten/lage_20261021_213455_i5.jsonl.gz"
TICK = int(sys.argv[1]) if len(sys.argv) > 1 else 59105
with gzip.open(p, "rt", encoding="utf-8") as f:
    for z in f:
        d = json.loads(z)
        if d["t"] >= TICK:
            break


def tab(s):
    kopf, aus = None, {}
    for r in s.split("\n"):
        w = r.split()
        if w and w[0] == "nr":
            kopf = w
            continue
        if kopf and len(w) == len(kopf):
            e = dict(zip(kopf, map(int, w)))
            aus[e["nr"]] = e
    return aus


L, G = tab(d["einheiten"]), tab(d["gebaeude"])
bed = GF.bedrohungen(L, G, lambda b: b == 2, gefecht.FERN_REICH)
print("Tick", d["t"], "Bedrohungen", len(bed), "davon Schuetzen", sum(1 for b in bed if b[4].startswith("schuetze")))
eig = [e for e in L.values() if e["besitzer"] == 1 and e["typ"] == 26]
mx = sorted(e["x"] for e in eig)[len(eig) // 2]
my = sorted(e["y"] for e in eig)[len(eig) // 2]
lord = [e for e in L.values() if e["besitzer"] == 2 and e["typ"] == 55][0]
tore = [g for g in G.values() if g["besitzer"] == 2 and g["typ"] == 75]
print("Streitkolben", len(eig), "Mitte", (mx, my), "Lord", (lord["x"], lord["y"]), "Torhaeuser75", [(g["x"], g["y"]) for g in tore])
for ziel in [(lord["x"], lord["y"])] + [(g["x"], g["y"]) for g in tore]:
    t0 = time.time()
    w = GF.sicherer_weg((mx, my), ziel, bed)
    dt = time.time() - t0
    print("Ziel", ziel, "Abstand", GF.schach((mx, my), ziel), "Zeit %.2f s" % dt, "Wegpunkte", None if w is None else len(w),
          "Gefahr", None if w is None else GF.weg_gefahr((mx, my), w, bed))
PROF = os.path.join(os.environ.get("TEMP", "."), "prof_weg")
cProfile.run("GF.sicherer_weg((mx, my), (lord['x'], lord['y']), bed)", PROF)
pstats.Stats(PROF).sort_stats("tottime").print_stats(8)
