"""Zieht eine geschichtete Stichprobe (Bereich x Quelle) aus den fertigen Ergebnissen und baut Prüfpakete.

Jedes Prüfpaket enthält je Funktion den Code und den Ergebnis-Eintrag. Ein Sonnet-Agent soll Fehler finden.
Aufruf: python -I werkzeug/stichprobe.py <anteil=0.05> <je_paket=12>
"""
import collections, glob, json, os, random, re, sys

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANTEIL = float(sys.argv[1]) if len(sys.argv) > 1 else 0.05
JE = int(sys.argv[2]) if len(sys.argv) > 2 else 12
e = json.load(open(os.path.join(W, "eingang.json"), encoding="utf-8"))
erg = {}
for f in glob.glob(os.path.join(W, "ergebnisse", "spiel_*.jsonl")):
    if re.search(r"spiel_\d{3}\.jsonl$", f):
        for z in open(f, encoding="utf-8"):
            if z.strip():
                x = json.loads(z); erg[x["adr"].lower()] = x
schichten = collections.defaultdict(list)
for a, x in erg.items():
    v = e.get(a) or e.get("0x" + a[2:].zfill(8))
    if v and len(v["kurz"]) < 15000:  # sehr große Funktionen sprengen ein Prüfpaket
        schichten[(v["bereich"], v["quelle"])].append(a)
random.seed(20261101)
wahl = []
for k, l in sorted(schichten.items()):
    n = max(1, round(len(l) * ANTEIL)); wahl += random.sample(sorted(l), min(n, len(l)))
random.shuffle(wahl)
os.makedirs(os.path.join(W, "pruefung", "eingang"), exist_ok=True)
pakete = [wahl[i:i + JE] for i in range(0, len(wahl), JE)]
for i, p in enumerate(pakete, 1):
    with open(os.path.join(W, "pruefung", "eingang", f"pruef_{i:02d}.txt"), "w", encoding="utf-8") as f:
        for a in p:
            v = e[a]
            f.write(f"### {a} {v['name']} | quelle={v['quelle']}\n--- CODE ---\n{v['kurz']}\n--- ERKLAERUNG ---\n"
                    f"{json.dumps(erg[a], ensure_ascii=False)}\n\n")
json.dump([f"pruef_{i:02d}" for i in range(1, len(pakete) + 1)], open(os.path.join(W, "pruefung", "liste.json"), "w"))
print(f"{len(erg)} Ergebnisse, Stichprobe {len(wahl)} in {len(pakete)} Prüfpaketen")
