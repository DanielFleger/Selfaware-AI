# -*- coding: utf-8 -*-
"""Baut Checkliste_Auge.md: feste Gesamtproben (Teil A) + alle Pruefpunkte aus funktionen_spiel.jsonl, je einem Lauf zugeteilt.
Die Zuteilung geht nach live_art und Stichworten, sie ist ein Vorschlag. Lauf aus dem Repo-Stamm."""
import collections, json, os, re
HIER = os.path.dirname(os.path.abspath(__file__))
G = "data/research/funktionswissen/funktionen_spiel.jsonl"
LAUF = {"tabelle": "S", "markt": "1", "anwerben": "1", "bauen": "1", "wirtschaft": "1", "kampf": "2", "ki-welle": "2", "bewegung": "2"}
HAKEN = r"Hook|per Aufruf|Aufruf in der|Rückgabe|Haltepunkt"
NICHT = r"Maustaste|nur im Mehrspieler|Mitspieler|Netzwerk|DirectPlay|Resync|Desync|\bHost\b|mapSize 160|Kampagne|Mission|Tutorial|Editor|Bestenliste|Video|gesperrtem Gebäude|mit \d+ Spielern im Netz"
KAMPF = r"angriff|Angriff|Schaden|töte|tot\b|stirbt|Feind|Gegner|Belager|Katapult|Tribok|Triböke|Ramme|Turm|Welle|Lord|Pfeil|Schuss|schieß|Feuer|Seuche|Graben|Pech|Öl|Falle|Hund"
ABSCHNITT = {
    "S": "Lauf 1, Start: einmal auslesen, sobald das Gefecht geladen ist",
    "1": "Lauf 1: eigene Burg, Wirtschaft, Bauen, Markt, Anwerben",
    "2": "Lauf 2: Kampf, KI-Wellen, Bewegung",
    "H": "Nur mit Aufruf-Haken: Der Wert steht nicht dauerhaft im Speicher",
    "N": "Nicht in diesen zwei Läufen: braucht anderen Spielmodus oder andere Karte",
}
punkte = collections.defaultdict(list)
form = collections.Counter()
for z in open(G, encoding="utf-8"):
    x = json.loads(z)
    live = (x["p3"].get("live") or "-").strip()
    if live in ("", "-"):
        continue
    art = x["p3"].get("live_art", "-")
    if re.search(NICHT, live):
        k = "N"
    elif re.search(HAKEN, " ".join(t.strip() for t in live.split("→")[:-1])):  # nur Lage und Messung, nicht die Erwartung
        k = "H"
    else:
        k = LAUF.get(art) or ("2" if re.search(KAMPF, live) else "1")
    teile = [t.strip() for t in live.split("→")]
    form["mit_erwartung" if len(teile) >= 3 else "ohne_klare_erwartung"] += 1
    if len(teile) >= 3:
        text = f"**Lage:** {teile[0]} · **Messen:** {' → '.join(teile[1:-1])} · **Erwartet:** {teile[-1]}"
    else:
        text = f"**Punkt ohne klare Erwartung, erst schärfen:** {live}"
    punkte[k].append((x["adr"], x["name"], text))
nr = 0
aus = []
for k in ("S", "1", "2", "H", "N"):
    aus.append(f"\n### {ABSCHNITT[k]} ({len(punkte[k])})\n")
    for a, n, t in punkte[k]:
        nr += 1
        aus.append(f"- [ ] P{nr:03d} `{n}` ({a}): {t}")
kopf = open(os.path.join(HIER, "checkliste_kopf.md"), encoding="utf-8").read()
zahlen = {k: len(v) for k, v in punkte.items()}
kopf = kopf.replace("{{GESAMT}}", str(nr)).replace("{{S}}", str(zahlen.get("S", 0))).replace("{{L1}}", str(zahlen.get("1", 0))).replace("{{L2}}", str(zahlen.get("2", 0))).replace("{{H}}", str(zahlen.get("H", 0))).replace("{{N}}", str(zahlen.get("N", 0))).replace("{{OHNE}}", str(form["ohne_klare_erwartung"]))
open(os.path.join(HIER, "Checkliste_Auge.md"), "w", encoding="utf-8").write(kopf + "\n".join(aus) + "\n")
print(nr, zahlen, dict(form))
for k in ("H", "N"):
    for a, n, t in punkte[k]:
        print(k, n, t[:150])
