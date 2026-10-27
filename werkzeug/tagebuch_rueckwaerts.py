# -*- coding: utf-8 -*-
"""B-273 Schritt 0: das Vorhersage-Tagebuch rueckwaerts ueber Lageprotokolle laufen lassen (Lord-Schaden vorhergesagt gegen
gemessen). Aufruf: python werkzeug/tagebuch_rueckwaerts.py <lage_..._spN.jsonl.gz> [...] - schreibt daten/tagebuch_rueck_<datei>.jsonl"""
import gzip, json, sys, glob, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tagebuch as TB
def tab(text):
    z = text.strip().split("\n"); kopf = z[1].split()
    return {int(r.split()[0]): dict(zip(kopf, map(int, r.split()))) for r in z[2:]}
for f in sys.argv[1:]:
    sp = int(f.split("_sp")[-1].split(".")[0])
    tb = TB.Tagebuch(sp, datei=os.path.join(TB.D, "tagebuch_rueck_" + os.path.basename(f).replace(".jsonl.gz", "") + ".jsonl"))
    for z in gzip.open(f, "rt", encoding="utf-8"):
        r = json.loads(z)
        L = tab(r["einheiten"])
        tb.lord_runde(int(r["t"]), L, {sp}, lambda b: b not in (0, sp))
    print(os.path.basename(f), "|", tb.zusammenfassung())
    for z in (open(tb.datei, encoding="utf-8").readlines()[:4] if os.path.exists(tb.datei) else []):
        print("   ", z.strip()[:230])
