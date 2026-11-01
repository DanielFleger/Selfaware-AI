"""Prüft die Ergebnisse gegen die Eingangspakete: Vollständigkeit, gültiges JSON, Pflichtfelder."""
import glob, json, os, re, sys

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PFLICHT = {"adr", "name", "quelle", "p1", "p2", "p3"}
gesamt, fehlt, kaputt, offen_pakete = 0, [], [], []
gruppen = sys.argv[1:] or ["spiel", "rest"]
for g in gruppen:
    for i, paket in enumerate(json.load(open(os.path.join(W, "pakete", g + ".json"))), 1):
        name = f"{g}_{i:03d}"
        pfad = os.path.join(W, "ergebnisse", name + ".jsonl")
        teile = sorted(glob.glob(os.path.join(W, "ergebnisse", name + ".teil*.jsonl")),
                       key=lambda t: int(re.search(r"teil(\d+)", t).group(1)))
        if teile and not os.path.exists(pfad):  # Teildateien zu einer Paketdatei zusammenfuehren
            with open(pfad, "w", encoding="utf-8") as f:
                for t in teile:
                    f.writelines(z.rstrip("\n") + "\n" for z in open(t, encoding="utf-8") if z.strip())
            os.makedirs(os.path.join(W, "ergebnisse", "teile"), exist_ok=True)
            for t in teile: os.replace(t, os.path.join(W, "ergebnisse", "teile", os.path.basename(t)))
        if not os.path.exists(pfad):
            offen_pakete.append(name); continue
        da = {}
        for nr, z in enumerate(open(pfad, encoding="utf-8"), 1):
            if not z.strip(): continue
            try:
                x = json.loads(z)
                if not PFLICHT <= x.keys(): raise ValueError("Felder fehlen")
                da[x["adr"].lower()] = x
            except Exception as ex:
                kaputt.append(f"{name}:{nr} {ex}")
        for a in paket:
            gesamt += 1
            if a.lower() not in da: fehlt.append(f"{name} {a}")
print(f"Funktionen in fertigen Paketen: {gesamt - len(fehlt)} von {gesamt}")
print(f"Pakete ohne Ergebnis: {len(offen_pakete)}  {' '.join(offen_pakete[:20])}")
print(f"Fehlende Funktionen: {len(fehlt)}  {' | '.join(fehlt[:10])}")
print(f"Kaputte Zeilen: {len(kaputt)}  {' | '.join(kaputt[:10])}")
