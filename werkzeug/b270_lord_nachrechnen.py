# B-270/B-272 (SAI 27.10.): Lord-Wettlauf einer Partie aus dem Lageprotokoll nachrechnen und zerlegen. Aufruf: python b270_lord_nachrechnen.py [tick]
import gzip, json, sys, collections
sys.path.insert(0, r"C:\Users\danie\Documents\PC_Affe\Games\Stronghold_Crusader\Stronghold Crusader Modding\Tools\Selfaware-AI\werkzeug")
import gefecht
from feldzug import TRUPPE, HEER

LAGE = r"C:\Users\danie\Documents\Selfaware AI\EA64FD94CCB49822\A902BEB6E4511A79\Selfaware-AI\daten\lage_20261027_180423_i1_sp3.jsonl.gz"
SP, TICK = 3, int(sys.argv[1]) if len(sys.argv) > 1 else 28934


def tabelle(text):
    z = text.strip().split("\n")
    return [dict(zip(z[1].split(), map(int, r.split()))) for r in z[2:]]


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


for z in gzip.open(LAGE, "rt", encoding="utf-8"):
    r = json.loads(z)
    if abs(int(r["t"]) - TICK) < 60:
        break
E = tabelle(r["einheiten"])
lord = min((e for e in E if e["typ"] == 55 and e["besitzer"] != SP), key=lambda e: e["nr"])
lp = (lord["x"], lord["y"])
eig = [e for e in E if e["besitzer"] == SP and e["typ"] in HEER]
sch, leb, fern = gefecht.tabelle()
print("Lord an:", {x: round(sch.get(x, {}).get(55, -1), 1) for x in sorted({e["typ"] for e in eig})})
print("Fern-Schaden je Takt an eigene Arten:", {(s, w): round(gefecht.dps(s, w, sch, fern, 5), 1) for s in (22, 23, 70) for w in sorted({e["typ"] for e in eig})})
print("Leben eigene:", {w: leb.get(w) for w in sorted({e["typ"] for e in eig})})

for ab in (0, 10, 20):
    ort = (lp[0] + ab, lp[1])
    wir = [dict(typ=e["typ"], leben=e["leben"], x=ort[0], y=ort[1]) for e in eig]
    sie = [dict(typ=e["typ"], leben=e["leben"], x=e["x"], y=e["y"], steht=False) for e in E
           if e["besitzer"] not in (0, SP) and e["typ"] in TRUPPE and e["typ"] != 55 and (
               schach((e["x"], e["y"]), lp) <= 25 or (e["typ"] in gefecht.FERN_REICH and schach((e["x"], e["y"]), lp) <= gefecht.FERN_REICH[e["typ"]]))]
    sie.insert(0, dict(typ=55, leben=lord["leben"], x=lp[0], y=lp[1], steht=True))
    for bis in (4000,):
        print("Start %d Felder vor dem Lord:" % ab, gefecht.lord_rennen(wir, sie, 0, bis=bis)[1])
    # ohne Schuetzen: nur der Lord
    print("   nur gegen den Lord:", gefecht.lord_rennen(wir, sie[:1], 0, bis=4000)[1])
    print("   Schuetzen-Schaden je Takt, alle 113 auf uns (Summe):", round(sum(gefecht.dps(s["typ"], 75, sch, fern, 5) for s in sie[1:])))
    print("   Lord-Schaden je Takt von uns (Summe):", round(sum(gefecht.dps(w["typ"], 55, sch, fern, 1) for w in wir)))
