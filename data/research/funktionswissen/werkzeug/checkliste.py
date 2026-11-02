"""Sammelt alle Prüfpunkte (p3.live) aus funktionen_spiel.jsonl zu einer Checkliste für möglichst wenige Spielläufe.

Gruppiert nach Spielsituation, damit ein Lauf viele Punkte nebenbei abhakt. Schreibt checkliste.md.
"""
import collections, json, os, re

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRUPPEN = [  # (Überschrift, Suchmuster im Prüfpunkt), erste passende gewinnt
    ("Markt: kaufen/verkaufen", r"Befehl 38|kauf|verkauf|Markt|Preis"),
    ("Anwerben", r"anwerb|recruit|Kaserne|Söldner|Gilde"),
    ("Bauen/Abreißen", r"bau|platzier|abreiß|Mauer|Graben"),
    ("Kampf/Einheiten", r"angriff|Schaden|Leben|huntedBy|Nahkampf|Schuss|Pfeil|tot"),
    ("Bewegung/Wegfindung", r"lauf|Weg|Pfad|Kletter|Ziel"),
    ("KI-Verhalten", r"KI|AI|Welle|attackInfo"),
    ("Wirtschaft/Lager", r"Lager|Bestand|Kornspeicher|Waffenkammer|Steuer|Beliebtheit|Nahrung"),
]
ARTEN = {"markt": "Markt: kaufen/verkaufen", "anwerben": "Anwerben", "bauen": "Bauen/Abreißen", "kampf": "Kampf/Einheiten",
         "bewegung": "Bewegung/Wegfindung", "ki-welle": "KI-Verhalten", "wirtschaft": "Wirtschaft/Lager",
         "tabelle": "Tabellen einmal auslesen", "sonstiges": "Sonstiges"}
GRUPPEN.append(("Tabellen einmal auslesen", r"Tabelle.*auslesen|einmal auslesen"))
punkte = collections.defaultdict(list)
for pfad in [os.path.join(W, "funktionen_spiel.jsonl")]:
    for z in open(pfad, encoding="utf-8"):
        if not z.strip():
            continue
        x = json.loads(z)
        live = (x.get("p3") or {}).get("live", "-").strip()
        if live in ("", "-"):
            continue
        art = (x.get("p3") or {}).get("live_art", "-")
        g = ARTEN.get(art) or next((t for t, m in GRUPPEN if re.search(m, live, re.I)), "Sonstiges")
        punkte[g].append((x["name"], x["adr"], live))
with open(os.path.join(W, "checkliste.md"), "w", encoding="utf-8") as f:
    f.write("# Spiel-Checkliste (aus p3.live)\n\nZiel: alles in 1–2 Läufen. Je Gruppe eine Spielsituation, die Punkte werden nebenbei gemessen.\n")
    for t, _ in GRUPPEN + [("Sonstiges", "")]:
        if punkte[t]:
            f.write(f"\n## {t} ({len(punkte[t])})\n")
            for n, a, l in punkte[t]:
                f.write(f"- [ ] `{n}` ({a}): {l}\n")
print(sum(map(len, punkte.values())), "Prüfpunkte;", {k: len(v) for k, v in punkte.items()})
