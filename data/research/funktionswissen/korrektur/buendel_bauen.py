# -*- coding: utf-8 -*-
"""B-141: je Agent ein Buendel mit allen offenen Funktionen: Export-Pseudocode (Referenz-exe) statt OpenSHC-Text, alte Erklaerung, Befunde."""
import glob, json, os, re
EX = r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference\functions"
K = "korrektur"
GRENZE = 240000
da = set()
for t in glob.glob(K + "/ergebnisse/*.jsonl"):
    for z in open(t, encoding="utf-8"):
        if z.strip():
            da.add(json.loads(z)["adr"].lower())
bef = json.load(open(K + "/stichprobe_befunde.json", encoding="utf-8"))
abw = json.load(open(K + "/zahlenabgleich.json", encoding="utf-8"))["funktionen"]
def kurz(s):
    return "\n".join(l.strip() for l in s.splitlines() if l.strip() and not l.strip().startswith("/* WARNING"))
gruppen, akt, n = [], [], 0
for p in json.load(open(K + "/liste.json")):
    txt = open(f"{K}/eingang/{p}.txt", encoding="utf-8").read()
    for b in re.split(r"(?m)^(?=### )", txt):
        if not b.startswith("### "):
            continue
        kopf = b.splitlines()[0]; a = kopf.split()[1].lower()
        if a in da:
            continue
        code, alt = b.split("--- CODE ---", 1)[1].split("--- ERKLAERUNG ---", 1)
        ex = json.load(open(os.path.join(EX, a[2:].rjust(8, "0") + ".json"), encoding="utf-8"))
        if "quelle=ghidra" in kopf:
            code = kurz(ex["pseudocode"])
        else:
            code = kurz(code)
            if a in abw:
                zeilen = [l.strip() for l in ex["pseudocode"].splitlines()
                          if any(re.search(r"\b(%d|0x%x)\b" % (v, v), l) for v in abw[a]["im_export_daneben"])]
                code += "\n--- ZAHLEN AUS DEM EXPORT (gelten vor dem Code oben) ---\n" + "\n".join(zeilen[:40])
        t = f"{kopf} | paket={p}\n--- CODE ---\n{code}\n--- ERKLAERUNG ---\n{alt.strip()}\n"
        if a in bef:
            t += "--- BEFUNDE ---\n" + json.dumps(bef[a], ensure_ascii=False) + "\n"
        if akt and n + len(t) > GRENZE:
            gruppen.append(akt); akt, n = [], 0
        akt.append(t); n += len(t)
if akt:
    gruppen.append(akt)
for i, g in enumerate(gruppen, 1):
    open(f"{K}/buendel/b{i:02d}.txt", "w", encoding="utf-8").write("\n".join(g))
print(len(gruppen), [(len(g), sum(map(len, g)) // 1000) for g in gruppen])
