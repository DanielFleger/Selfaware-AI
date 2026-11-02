# -*- coding: utf-8 -*-
"""B-141 Prueferbuendel: Vollstaendigkeit, verdaechtige Zahlen in fertigen Erklaerungen, feste Stichprobe aus der Sparfassung."""
import glob, json, os, random, re
EX = r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference\functions"
K = "korrektur"
PFLICHT = {"adr", "name", "quelle", "p1", "p2", "p3", "korrigiert", "aenderung"}
soll = {}
for p in json.load(open(K + "/liste.json")):
    for l in open(f"{K}/eingang/{p}.txt", encoding="utf-8"):
        if l.startswith("### "):
            soll[l.split()[1].lower()] = p
da, spar, kaputt = {}, [], []
for t in glob.glob(K + "/ergebnisse/*.jsonl"):
    for z in open(t, encoding="utf-8"):
        if z.strip():
            try:
                x = json.loads(z)
                assert PFLICHT <= x.keys()
                da[x["adr"].lower()] = x
                if ".teilb" in t:
                    spar.append(x["adr"].lower())
            except Exception as ex:
                kaputt.append(os.path.basename(t) + ": " + str(ex)[:60])
fehlt = sorted(a for a in soll if a not in da)
abw = json.load(open(K + "/zahlenabgleich.json", encoding="utf-8"))["funktionen"]
def pc(a):
    return json.load(open(os.path.join(EX, a[2:].rjust(8, "0") + ".json"), encoding="utf-8"))["pseudocode"]
def treffer(v, s):
    return re.search(r"(?<![\w.])(%d|0x%x)(?![\w.])" % (v, v), s, re.I) is not None
aus = []
for a, e in abw.items():
    if a not in da:
        continue
    text = json.dumps({k: da[a][k] for k in ("p2", "p3")}, ensure_ascii=False)
    v = [n for n in e["nur_im_paketcode"] if treffer(n, text)]
    if not v:
        continue
    zeilen = [l.strip() for l in pc(a).splitlines() if any(treffer(n, l) for n in e["im_export_daneben"])]
    regeln = [r for r in da[a]["p2"]["regeln"] if any(treffer(n, r) for n in v)]
    aus.append(f"### VERDACHT {a} {da[a]['name']}\nZahlen in der Erklaerung, die im Export nicht vorkommen: {v}\nExportzeilen mit den Nachbarzahlen:\n" + "\n".join(zeilen[:15]) + "\nBetroffene Regeln:\n" + "\n".join(regeln))
random.seed(1102)
wahl = random.sample(sorted(set(spar)), min(12, len(set(spar))))
for a in wahl:
    code = "\n".join(l.strip() for l in pc(a).splitlines() if l.strip())
    if len(code) > 14000:
        code = "[gekuerzt auf Zeilen mit Vergleich/Zuweisung einer Zahl]\n" + "\n".join(l for l in code.splitlines() if re.search(r"[<>=]=?.*\b(0x[0-9a-f]+|\d+)\b", l))[:14000]
    aus.append(f"### STICHPROBE {a} {da[a]['name']}\n--- CODE ---\n{code}\n--- ERKLAERUNG ---\n" + json.dumps(da[a], ensure_ascii=False))
open(K + "/pruefer_buendel.txt", "w", encoding="utf-8").write("\n\n".join(aus))
print(f"soll {len(soll)} da {sum(1 for a in soll if a in da)} fehlt {len(fehlt)} {fehlt[:20]} kaputt {len(kaputt)} {kaputt[:5]}; Buendel {len(aus)} Eintraege, {sum(map(len,aus))//1000} KB, davon Stichprobe {len(wahl)}")
