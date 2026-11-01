"""Spielt die berichtigten Erklärungen aus korrektur/ergebnisse in funktionen_spiel.jsonl ein.

Prüft je Korrekturpaket Vollständigkeit und Format; die alte Fassung bleibt in funktionen_spiel.vor_korrektur.jsonl.
Baut danach die zweite Stichprobe: die großen Funktionen aus der ersten Stichprobe (vorher/nachher-Vergleich)
plus ebenso viele neue große Funktionen.
"""
import glob, json, os, random, re

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = os.path.join(W, "korrektur")
PFLICHT = {"adr", "name", "quelle", "p1", "p2", "p3"}
e = json.load(open(os.path.join(W, "eingang.json"), encoding="utf-8"))
alt = {json.loads(z)["adr"].lower(): json.loads(z) for z in open(os.path.join(W, "funktionen_spiel.jsonl"), encoding="utf-8")}
neu, offen, kaputt = {}, [], []
for paket in json.load(open(os.path.join(K, "liste.json"))):
    soll = [l.split()[1].lower() for l in open(os.path.join(K, "eingang", paket + ".txt"), encoding="utf-8") if l.startswith("### ")]
    da = {}
    for t in glob.glob(os.path.join(K, "ergebnisse", paket + ".teil*.jsonl")) + glob.glob(os.path.join(K, "ergebnisse", paket + ".jsonl")):
        for z in open(t, encoding="utf-8"):
            if not z.strip():
                continue
            try:
                x = json.loads(z)
                if not PFLICHT <= x.keys():
                    raise ValueError("Felder fehlen")
                da[x["adr"].lower()] = x
            except Exception as ex:
                kaputt.append(f"{os.path.basename(t)}: {ex}")
    fehlt = [a for a in soll if a not in da]
    if fehlt:
        offen.append(paket)
    neu.update({a: da[a] for a in soll if a in da})
korr = sum(1 for x in neu.values() if x.get("korrigiert") == "ja")
for a, x in neu.items():
    alt[a] = x
with open(os.path.join(W, "funktionen_spiel.jsonl"), "w", encoding="utf-8") as f:
    for a in sorted(alt, key=lambda a: int(a, 16)):
        f.write(json.dumps(alt[a], ensure_ascii=False) + "\n")
json.dump(offen, open(os.path.join(K, ".offen.json"), "w"))
print(f"eingespielt {len(neu)}, davon korrigiert {korr}; Pakete unvollständig {len(offen)} {' '.join(offen[:15])}; kaputte Zeilen {len(kaputt)}")

# Zweite Stichprobe: alte große + neue große
vorher = {}
for t in glob.glob(os.path.join(W, "pruefung", "ergebnisse", "pruef_*.jsonl")):
    for z in open(t, encoding="utf-8"):
        if z.strip():
            v = json.loads(z); vorher[v["adr"].lower()] = v["urteil"]
gross_alt = [a for a in vorher if a in neu]
random.seed(1101)
gross_neu = random.sample(sorted(set(neu) - set(gross_alt)), min(len(gross_alt), len(set(neu) - set(gross_alt))))
wahl = gross_alt + gross_neu
os.makedirs(os.path.join(W, "pruefung2", "eingang"), exist_ok=True)
pakete = [wahl[i:i + 3] for i in range(0, len(wahl), 3)]
for i, p in enumerate(pakete, 1):
    with open(os.path.join(W, "pruefung2", "eingang", f"pruef2_{i:02d}.txt"), "w", encoding="utf-8") as f:
        for a in p:
            f.write(f"### {a} {e[a]['name']} | quelle={e[a]['quelle']}\n--- CODE ---\n{e[a]['kurz']}\n--- ERKLAERUNG ---\n"
                    f"{json.dumps(neu[a], ensure_ascii=False)}\n\n")
json.dump({"liste": [f"pruef2_{i:02d}" for i in range(1, len(pakete) + 1)], "vorher": {a: vorher[a] for a in gross_alt}},
          open(os.path.join(W, "pruefung2", "liste.json"), "w"))
print(f"Stichprobe 2: {len(gross_alt)} schon geprüfte + {len(gross_neu)} neue große Funktionen in {len(pakete)} Paketen")
