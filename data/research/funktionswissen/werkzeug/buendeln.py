import json, sys, os, re
e = json.load(open("eingang.json", encoding="utf-8"))
ZIEL = int(sys.argv[1]) if len(sys.argv) > 1 else 40000
def schluessel(a, v):
    m = re.search(r"\b(\w+)::\w+\s*\(", v["kurz"][:400])
    return (v["bereich"], m.group(1) if m else "", int(a, 16))
for gruppe, filt in (("spiel", lambda v: v["spiel"]), ("rest", lambda v: not v["spiel"])):
    fs = sorted([(a, v) for a, v in e.items() if filt(v) and v["kurz"]], key=lambda t: schluessel(*t))
    pakete, akt, n = [], [], 0
    for a, v in fs:
        L = len(v["kurz"])
        if akt and n + L > ZIEL: pakete.append(akt); akt, n = [], 0
        akt.append(a); n += L
    if akt: pakete.append(akt)
    os.makedirs("pakete", exist_ok=True)
    json.dump(pakete, open(f"pakete/{gruppe}.json", "w"), indent=0)
    print(gruppe, "Funktionen", len(fs), "Pakete", len(pakete), "groesstes", max(sum(len(e[a]["kurz"]) for a in p) for p in pakete))
