# -*- coding: utf-8 -*-
"""Lauf F: jeden Bau-Befehl einordnen. Besetzt von frueher Gebautem? Heute laut Spiel erlaubt? Nur lesen."""
import collections, json, sys
sys.path.insert(0, "src")
from selfaware.game.ucp import bauen

d = json.load(open(sys.argv[1], encoding="utf-8"))
p = json.load(open(sys.argv[2], encoding="utf-8"))
B = d["befehle"]
STELLEN = [(205, 181), (205, 195), (212, 181), (212, 195), (219, 181), (219, 195), (205, 188), (219, 188), (198, 174), (198, 202), (205, 174), (205, 202)]
print("Befehle an den 12 Stellen:", sum((b["x"], b["y"]) in STELLEN for b in B), "von", len(B), "| Stellen je Typ hoechstens:", max(collections.Counter(b["typ"] for b in B).values()))
NEU = [n for n in d["neu"] if n["sp"] == 1 and n["takt"] > 4000]
print("Neue Eintraege ab Burg:", [(n["takt"], n["nr"], n["typ"], n["x"], n["y"]) for n in NEU])
# Treffer: Befehl -> Eintrag gleichen Typs, kurz danach
erfolg = []
for n in NEU:
    k = [b for b in B if b["typ"] == n["typ"] and b["takt"] <= n["takt"]]
    if k:
        b = k[-1]
        erfolg.append({"typ": n["typ"], "befehl": b["takt"], "eintrag": n["takt"], "stelle": (b["x"], b["y"]), "b": b["groesse"], "ort": (n["x"], n["y"]), "nr": n["nr"]})
print("Erfolge:")
for e in sorted(erfolg, key=lambda e: e["befehl"]):
    print(" ", e, "Abstand", e["eintrag"] - e["befehl"])
WEG = {w["nr"]: w["takt"] for w in d["weg"]}


def rechteck(x, y, b):
    return x, y, x + b - 1, y + b - 1


def schneidet(a, c):
    return not (a[2] < c[0] or c[2] < a[0] or a[3] < c[1] or c[3] < a[1])


KEEP = rechteck(212 - 4, 188 - 4, 16)  # grob: Burgflaeche, nur fuer die Einordnung
klassen = collections.Counter()
beispiele = collections.defaultdict(list)
for b in B:
    r = rechteck(b["x"], b["y"], b["groesse"])
    if any(e["typ"] == b["typ"] and e["befehl"] == b["takt"] for e in erfolg):
        klassen["gebaut"] += 1
        continue
    im_weg = [e for e in erfolg if e["befehl"] < b["takt"] and schneidet(r, rechteck(*e["stelle"], e["b"]))]
    if (b["x"], b["y"]) not in STELLEN:
        klassen["andere Stelle (Burgsuche)"] += 1
        continue
    heute = p[str(b["typ"])]["an_stellen"][STELLEN.index((b["x"], b["y"]))]
    if im_weg:
        k = "belegt von frueherem Bau"
    elif heute == "+":
        k = "frei und heute erlaubt: UNERKLAERT"
    else:
        k = "Spielregel Grund " + heute
    klassen[k] += 1
    if len(beispiele[k]) < 4:
        beispiele[k].append((b["takt"], b["typ"], b["x"], b["y"], b["groesse"]))
print("Einordnung aller Befehle:", klassen.most_common())
for k, v in beispiele.items():
    print(" ", k, v)
print("Erlaubt auf der ganzen Karte, wenig:", {t: (v["name"], v["gut"], v["naechste"]) for t, v in p.items() if v["gut"] < 2000})
