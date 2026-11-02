# -*- coding: utf-8 -*-
"""B-141 zweite Stichprobe: nachgepruefte Ersetzungen in die Ergebnisdateien; jeder Text muss genau einmal vorkommen.
Danach werkzeug/einspielen.py fuer die Gesamtdatei. Lauf aus dem Ordner funktionswissen."""
import glob, json
ort = {}
for t in glob.glob("korrektur/ergebnisse/*.jsonl"):
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
for z in open("pruefung2/ergebnisse.jsonl", encoding="utf-8"):
    if not z.strip():
        continue
    b = json.loads(z)
    if b["urteil"] == "richtig":
        continue
    t, i = ort[b["adr"].lower()]
    zeilen = open(t, encoding="utf-8").read().splitlines()
    x = json.loads(zeilen[i])
    for e in b["ersetzen"]:
        if zaehlen(x, e["alt"]) != 1:
            miss.append((b["adr"], zaehlen(x, e["alt"]), e["alt"][:70]))
            continue
        x = ersetze(x, e["alt"], e["neu"])
        ok += 1
    x["pruefer3"] = b["urteil"] + ": " + " ".join(b["befunde"])
    zeilen[i] = json.dumps(x, ensure_ascii=False)
    open(t, "w", encoding="utf-8").write("\n".join(zeilen) + "\n")
print("ersetzt", ok, "nicht eindeutig", len(miss), miss)
