"""Nach einem (abgebrochenen) Lauf: vollständige Pakete aus Teildateien zusammenführen,
unvollständige Teile beiseitelegen und die Liste der offenen Pakete schreiben.

Aufruf: python -I werkzeug/aufraeumen.py <gruppe=spiel>
"""
import glob, json, os, re, sys

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = sys.argv[1] if len(sys.argv) > 1 else "spiel"
E = os.path.join(W, "ergebnisse")
offen, zusammen, beiseite = [], 0, 0
for i, paket in enumerate(json.load(open(os.path.join(W, "pakete", G + ".json"))), 1):
    name = f"{G}_{i:03d}"
    soll = {a.lower() for a in paket}
    ziel = os.path.join(E, name + ".jsonl")
    if os.path.exists(ziel):
        da = {json.loads(z)["adr"].lower() for z in open(ziel, encoding="utf-8") if z.strip()}
        if soll <= da:
            continue
        os.makedirs(os.path.join(E, "abgebrochen"), exist_ok=True)
        os.replace(ziel, os.path.join(E, "abgebrochen", name + ".jsonl")); beiseite += 1
    teile = sorted(glob.glob(os.path.join(E, name + ".teil*.jsonl")),
                   key=lambda t: int(re.search(r"teil(\d+)", t).group(1)))
    zeilen, da = [], set()
    for t in teile:
        for z in open(t, encoding="utf-8"):
            if not z.strip():
                continue
            try:
                x = json.loads(z)
            except ValueError:
                continue
            if x.get("adr", "").lower() in soll and x["adr"].lower() not in da:
                da.add(x["adr"].lower()); zeilen.append(json.dumps(x, ensure_ascii=False) + "\n")
    if teile and soll <= da:
        reihen = {a.lower(): n for n, a in enumerate(paket)}
        zeilen.sort(key=lambda z: reihen[json.loads(z)["adr"].lower()])
        open(ziel, "w", encoding="utf-8").writelines(zeilen); zusammen += 1
        os.makedirs(os.path.join(E, "teile"), exist_ok=True)
        for t in teile: os.replace(t, os.path.join(E, "teile", os.path.basename(t)))
    else:
        if teile:
            os.makedirs(os.path.join(E, "abgebrochen"), exist_ok=True)
            for t in teile: os.replace(t, os.path.join(E, "abgebrochen", os.path.basename(t)))
            beiseite += 1
        offen.append(name)
json.dump(offen, open(os.path.join(E, f".offen_{G}.json"), "w"))
print(f"zusammengeführt {zusammen}, beiseitegelegt {beiseite}, offen {len(offen)}")
print(" ".join(offen))
