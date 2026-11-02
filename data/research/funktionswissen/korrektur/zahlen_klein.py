# -*- coding: utf-8 -*-
"""B-141: Kleinere Funktionen, deren Paketcode eine Zahl enthaelt, die im Export nur um 1 verschoben steht.
Haelt ihre Erklaerungen gegen den Export. Meldet Verdacht, kein Urteil. Lauf aus dem Ordner funktionswissen."""
import json, os, re, sys
sys.path.insert(0, "korrektur")
from gegenprobe import EX, ansprueche, lade_export, pakete, pruefe, schnitte_asm, schnitte_pseudo, wert, zahlen
ZAHLW = re.compile(r"(?<![\w.])(0x[0-9a-fA-F]+|\d+)(?![\w.])")
soll, _ = pakete()
ein = json.load(open("eingang.json", encoding="utf-8"))
ges = {json.loads(z)["adr"].lower(): json.loads(z) for z in open("funktionen_spiel.jsonl", encoding="utf-8")}
def treffer(v, s):
    return re.search(r"(?<![\w.])(%d|0x%x)(?![\w.])" % (v, v), s, re.I) is not None
liste, ohne_export = {}, []
for a, x in ges.items():
    if not os.path.exists(os.path.join(EX, a[2:].rjust(8, "0") + ".json")):
        ohne_export.append(a)
        continue
    e = lade_export(a)
    im_ex = zahlen(e.get("pseudocode") or "", [])  # nur Pseudocode: im Assembly steht dieselbe Zahl oft fuer etwas anderes
    c = ein[a].get("kurz") or ""
    nur = sorted(n for n in {wert(w) for w in ZAHLW.findall(c)} - im_ex if n >= 2 and (n - 1 in im_ex or n + 1 in im_ex))
    if nur:
        liste[a] = {"nur_im_paketcode": nur, "im_export_daneben": sorted({m for n in nur for m in (n - 1, n + 1) if m in im_ex})}
gross = {a: v for a, v in liste.items() if a in soll}
klein = {a: v for a, v in liste.items() if a not in soll}
print("alle", len(ges), "ohne Export", len(ohne_export), "mit Abweichung", len(liste), "gross", len(gross), "klein", len(klein))
aus = {}
for a, v in sorted(klein.items()):
    x = ges[a]
    text = json.dumps({k: x[k] for k in ("p1", "p2", "p3")}, ensure_ascii=False)
    e = lade_export(a)
    zahl = [n for n in v["nur_im_paketcode"] if treffer(n, text)]
    fl = [f for f in pruefe(x, e, ein[a].get("kurz") or "") if f["art"] in ("grenze_um_eins", "zahl_da_grenze_nicht", "zahl_fehlt")]
    if zahl or fl:
        aus[a] = {"name": x["name"], "quelle": x.get("quelle"), "zahlen_nur_im_paketcode_in_der_erklaerung": zahl, "gegenprobe": fl, **v}
json.dump({"erzeugt": "B-141", "funktionen": klein}, open("korrektur/zahlenabgleich_klein.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
json.dump(aus, open("korrektur/zahlen_klein_treffer.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
alt44 = json.load(open("korrektur/zahlenabgleich.json", encoding="utf-8"))["funktionen"]
print("gegen alte Liste: gleich", len(set(alt44) & set(gross)), "nur alt", len(set(alt44) - set(gross)), "nur neu", len(set(gross) - set(alt44)))
print("Treffer", len(aus), "mit Zahl nur im Paketcode", sum(1 for v in aus.values() if v["zahlen_nur_im_paketcode_in_der_erklaerung"]), "mit Grenzfund", sum(1 for v in aus.values() if v["gegenprobe"]))
for a, v in aus.items():
    print("==", a, v["name"], v["quelle"], "nur:", v["zahlen_nur_im_paketcode_in_der_erklaerung"], "daneben:", v["im_export_daneben"][:6])
    tx = [r for r in ges[a]["p2"]["regeln"] if any(treffer(n, r) for n in v["zahlen_nur_im_paketcode_in_der_erklaerung"])]
    for r in tx[:3]:
        print("   R", r[:210])
    for t in ("erklaerung", "gehirn", "live"):
        s = str(ges[a]["p3"].get(t, ""))
        if any(treffer(n, s) for n in v["zahlen_nur_im_paketcode_in_der_erklaerung"]):
            print("   P", t, s[:210])
    for f in v["gegenprobe"][:3]:
        print("   G", f["art"], f["stelle"], "|", f["regel"][:170])
