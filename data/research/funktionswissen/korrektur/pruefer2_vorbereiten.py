# -*- coding: utf-8 -*-
"""B-141 zweite Pruefstufe: Stichprobe aus allen 334 ohne die schon gepruefte, voller Code bis 16 KB."""
import glob, json, os, random, re, sys
sys.path.insert(0, "korrektur")
from gegenprobe import EX, K, lade_ergebnisse, lade_export, pakete
soll, code = pakete()
da = lade_ergebnisse()
herkunft = {}
for t in glob.glob(K + "/ergebnisse/*.jsonl"):
    for z in open(t, encoding="utf-8"):
        if z.strip():
            herkunft[json.loads(z)["adr"].lower()] = "spar" if ".teilb" in t else "sonnet"
bef = {json.loads(l)["adr"].lower() for l in open(K + "/pruefer_befunde.jsonl", encoding="utf-8") if l.strip()}
alle = json.load(open(K + "/zahlenabgleich.json", encoding="utf-8"))["funktionen"]
gr = {a: len(lade_export(a).get("pseudocode") or "") for a in soll}
frei = [a for a in sorted(soll) if a not in bef]
pass_ = [a for a in frei if gr[a] <= 16000]
print("alle", len(soll), "schon geprueft", len(bef), "frei", len(frei), "davon bis 16 KB", len(pass_), "| spar", sum(herkunft[a] == "spar" for a in pass_), "sonnet", sum(herkunft[a] == "sonnet" for a in pass_))
print("Zahlenabgleich-Liste", len(alle), "davon frueh fertig (ohne Eintrag): nicht messbar aus Liste")
random.seed(1103)
wahl = random.sample([a for a in pass_ if herkunft[a] == "sonnet"], 16) + random.sample([a for a in pass_ if herkunft[a] == "spar"], 8)
aus = []
for a in wahl:
    e = lade_export(a)
    k = "\n".join(l.strip() for l in e["pseudocode"].splitlines() if l.strip())
    x = {f: da[a][f] for f in ("adr", "name", "p1", "p2", "p3")}
    aus.append(f"### {a} {da[a]['name']} herkunft={herkunft[a]}\n--- CODE (Ghidra-Export, vollstaendig) ---\n{k}\n--- ERKLAERUNG ---\n" + json.dumps(x, ensure_ascii=False))
open(K + "/pruefer2_buendel.txt", "w", encoding="utf-8").write("\n\n".join(aus))
print(len(wahl), "Funktionen,", sum(map(len, aus)) // 1000, "KB, kleinste/groesste", min(gr[a] for a in wahl), max(gr[a] for a in wahl))
