# -*- coding: utf-8 -*-
"""B-141: Ersetzungen aus pruefer_befunde.jsonl in die Ergebnisdateien; jeder Text muss genau einmal vorkommen, sonst Meldung."""
import glob, json, sys
K = "data/research/funktionswissen/korrektur"
ort = {}
for t in glob.glob(K + "/ergebnisse/*.jsonl"):
    for i, z in enumerate(open(t, encoding="utf-8")):
        if z.strip():
            ort[json.loads(z)["adr"].lower()] = (t, i)
def zaehlen(o, s):
    if isinstance(o, str): return o.count(s)
    if isinstance(o, list): return sum(zaehlen(v, s) for v in o)
    if isinstance(o, dict): return sum(zaehlen(v, s) for v in o.values())
    return 0
def ersetze(o, a, b):
    if isinstance(o, str): return o.replace(a, b)
    if isinstance(o, list): return [ersetze(v, a, b) for v in o]
    if isinstance(o, dict): return {k: ersetze(v, a, b) for k, v in o.items()}
    return o
ok, miss = 0, []
for z in open(K + "/pruefer_befunde.jsonl", encoding="utf-8"):
    if not z.strip(): continue
    b = json.loads(z); a = b["adr"].lower()
    if not b.get("ersetzen"): continue
    t, i = ort[a]
    zeilen = open(t, encoding="utf-8").read().splitlines()
    x = json.loads(zeilen[i])
    for e in b["ersetzen"]:
        if zaehlen(x, e["alt"]) != 1:
            miss.append((a, zaehlen(x, e["alt"]), e["alt"][:70])); continue
        x = ersetze(x, e["alt"], e["neu"]); ok += 1
    x["pruefer"] = b["urteil"] + ": " + b.get("befund", "-")
    zeilen[i] = json.dumps(x, ensure_ascii=False)
    open(t, "w", encoding="utf-8").write("\n".join(zeilen) + "\n")
print("ersetzt", ok, "nicht eindeutig", len(miss), miss)
