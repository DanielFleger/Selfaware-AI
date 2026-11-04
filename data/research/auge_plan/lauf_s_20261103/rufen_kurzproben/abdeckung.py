# -*- coding: utf-8 -*-
"""Wie viel deckt das Auge ab? Nur Zaehlen, jede Zahl sagt, was sie zaehlt."""
import collections, csv, glob, json, os, re

A = "data/research/auge_plan/"
chk = open(A + "Checkliste_Auge.md", encoding="utf-8").read()
punkte = re.findall(r"^- \[[ x]\] (P\d+) `([^`]+)`", chk, re.M)
print("Checkliste: Punkte", len(punkte))
for name, f in (("S", A + "lauf_s_20261103/Punkte_Lauf_S.md"), ("K", A + "lauf_k_20261102/Punkte_Lauf_K.md"), ("F", A + "lauf_f_20261102/Punkte_Lauf_F.md")):
    t = open(f, encoding="utf-8").read()
    print("Datei", name, re.findall(r"^\| ([a-zA-Zäöü ]+) \| (\d+) \|$", t, re.M)[:9])

fu = [json.loads(z) for z in open("data/research/funktionswissen/funktionen_spiel.jsonl", encoding="utf-8")]
print("funktionen_spiel: Zeilen", len(fu), "Schluessel", sorted(fu[0])[:16])
print("  mit live_ergebnis", sum(1 for f in fu if f.get("live_ergebnis")))
D = r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference\functions"
gesamt = collections.Counter()
for f in os.listdir(D):
    if f.endswith(".json"):
        with open(os.path.join(D, f), encoding="utf-8") as d:
            kopf = d.read(300)
        m = re.search(r'"name":"([^"]*)"', kopf)
        n = m.group(1) if m else ""
        gesamt["Oberflaeche, Bild, Ton, Netz" if re.search(r"UI::|Rendering|Audio|Video|Menu|Bink|DirectDraw|Sound|Text::|Synchrony|IO::|Init::|Meta::|Input|Network|FUN_|thunk", n) else "Spiel"] += 1
print("Funktionen im Export, grob nach Name:", dict(gesamt))

zf = list(csv.reader(open(A + "zustand_felder.csv", encoding="utf-8"), delimiter=";"))
print("Feldliste Zeilen", len(zf), "Kopf", zf[0][:8])
for f in ("lauf_k_20261102/nie_gesehen_lauf_f_und_k.csv", "lauf_k_20261102/feldluecken_lauf_k.csv"):
    if os.path.exists(A + f):
        z = list(csv.reader(open(A + f, encoding="utf-8"), delimiter=";"))
        print(f, "Zeilen", len(z), "Kopf", z[0][:6], "Beispiele", [r[:2] for r in z[1:3]])
        for i, k in enumerate(z[0]):
            if k.lower() in ("klasse", "bereich", "global", "gruppe", "art"):
                print("   nach", k, collections.Counter(r[i] for r in z[1:] if len(r) > i).most_common(10))
ca = open(A + "lauf_s_20261103/code_abgleich.txt", encoding="utf-8").read()
print("code_abgleich Kopf:", ca[:240].replace("\n", " | "))
