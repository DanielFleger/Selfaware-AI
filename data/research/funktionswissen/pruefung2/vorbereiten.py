# -*- coding: utf-8 -*-
"""B-141 zweite Stichprobe: Buendel je 4 Funktionen mit vollem Export, dazu Namen und Kommentare, die nur im Paketcode stehen.
Lauf aus dem Ordner funktionswissen."""
import json, os, re, sys
sys.path.insert(0, "korrektur")
from gegenprobe import lade_ergebnisse, lade_export, namen_von, pakete
soll, code = pakete()
da = lade_ergebnisse()
liste = json.load(open("pruefung2/liste.json", encoding="utf-8"))
wahl = []
for p in liste["liste"]:
    for z in open(f"pruefung2/eingang/{p}.txt", encoding="utf-8"):
        if z.startswith("### "):
            wahl.append(z.split()[1].lower())
os.makedirs("pruefung2/buendel", exist_ok=True)
for i in range(0, len(wahl), 4):
    aus = []
    for a in wahl[i:i + 4]:
        ex = lade_export(a)["pseudocode"]
        k = "\n".join(l.strip() for l in ex.splitlines() if l.strip())
        nur = sorted(namen_von(code[a]) - namen_von(ex))
        kom = [l.strip() for l in code[a].splitlines() if "//" in l or "/*" in l]
        x = {f: da[a][f] for f in ("adr", "name", "p1", "p2", "p3")}
        aus.append(f"### {a} {da[a]['name']}\n--- CODE (Ghidra-Export, vollstaendig) ---\n{k}\n--- NAMEN NUR IM PAKETCODE ---\n{', '.join(nur) or '-'}\n--- KOMMENTARE IM PAKETCODE ---\n" + ("\n".join(kom) or "-") + "\n--- ERKLAERUNG ---\n" + json.dumps(x, ensure_ascii=False))
    open(f"pruefung2/buendel/teil_{i // 4 + 1:02d}.txt", "w", encoding="utf-8").write("\n\n".join(aus))
    print(i // 4 + 1, sum(map(len, aus)) // 1000, "KB")
