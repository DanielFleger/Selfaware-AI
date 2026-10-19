# -*- coding: utf-8 -*-
"""Jede Partie wird Trainingsdaten (Daniel 19.10.2026 22:48: "in Zukunft kann so eine Partie gerne auch fuer mehr
Trainingsdaten genutzt werden"; Backlog B-119).

Liest nach einer Partie die Mitschrift des Lenkers (samurai_*_spN_konsole.txt) und sein Lageprotokoll (lage_*_spN.jsonl.gz),
und schreibt
  - daten/lernen/partie_<stamp>.json   alles zu dieser Partie
  - daten/lernen/partien.jsonl         eine Zeile je Partie (waechst; Grundlage fuers Selbstlernen)
Inhalt (alles gemessen, nichts geschaetzt):
  - Kampfeinheiten je Spieler alle 3.000 Ticks, mit Namen aus dem Spiel (OpenSHC-Enum UnitType, daten/enum_einheiten.txt);
    Huehner/Muetter/Kinder (62-64) zaehlen NICHT
  - Gold des Lenkers ueber die Zeit (aus seinen ANWERBEN-BREMSE-Zeilen), Zahl der Bremsen und Anwerbungen
  - Ereigniszaehler (Feldzug, Raid, Stillstand, Hunger, Planer wartet, Seasoning)
  - Partievergleich (partie_vergleich.py): ab wann wer hinten, Einbruch, Kette
  - letzter Tick und Truppen am Ende (wer gewonnen hat, steht in "anmerkung" - aus dem Protokoll noch nicht abgelesen)
Aufruf: python werkzeug/partie_lernen.py <konsole.txt> <lage.jsonl.gz> [gegner=Daniel] [anmerkung="..."]"""
import gzip
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter

HIER = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HIER, "..", "daten")
AUS = os.path.join(D, "lernen")
KAMPF = set(range(22, 31)) | {39, 60, 61, 77} | set(range(70, 77))
FENSTER = 3000
EREIGNISSE = ("ANWERBEN-BREMSE", "WERBE", "FELDZUG", "RAID", "STILLSTAND", "HUNGER", "PLANER wartet", "Seasoning", "LORDWACHE",
              "ENDSPURT", "Reiter")


def namen():
    n, drin = {}, False
    for z in open(os.path.join(D, "enum_einheiten.txt"), encoding="utf-8"):
        if z.startswith("### "):
            drin = z.split()[1] == "UnitType"
            continue
        m = re.match(r"\s+(\d+)\s+UT_(\S+)", z)
        if drin and m:
            n[int(m.group(1))] = m.group(2)
    return n


def truppen(lage, N):
    aus, naechster, letzter = [], 0, None
    for z in gzip.open(lage, "rt", encoding="utf-8"):
        r = json.loads(z)
        letzter = r
        if r["t"] < naechster:
            continue
        naechster = (r["t"] // FENSTER + 1) * FENSTER
        c = {}
        for e in r["einheiten"].split("\n")[2:]:
            w = e.split()
            if len(w) >= 3 and int(w[2]) in KAMPF and int(w[1]) > 0:
                c.setdefault(w[1], Counter())[N.get(int(w[2]), w[2])] += 1
        aus.append({"t": r["t"], "je_spieler": {sp: dict(k) for sp, k in c.items()}})
    return aus, (letzter or {}).get("t")


def mitschrift(konsole):
    text = open(konsole, encoding="utf-8", errors="replace").read()
    gold = []
    for m in re.finditer(r"^ *(\d+) \|.*ANWERBEN-BREMSE: Gold (\d+) \(braucht (\d+)\)", text, re.M):
        gold.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))
    start = re.search(r"^START-BEFEHL.*$", text, re.M)
    return {"start_befehl": start.group(0) if start else None,
            "ereignisse": {k: len(re.findall(re.escape(k), text)) for k in EREIGNISSE},
            "anwerbungen": len(re.findall(r"angeworben", text)),
            "gold_bei_bremse": [{"t": t, "gold": g, "braucht": b} for t, g, b in gold],
            "letzte_stand": (re.findall(r"^STAND Tick .*$", text, re.M) or [None])[-1]}


def vergleich(lage, stamp):
    ziel = os.path.join(AUS, "partievergleich_%s.json" % stamp)
    r = subprocess.run([sys.executable, "-P", os.path.join(HIER, "partie_vergleich.py"), lage, "json=" + ziel],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    zeilen = [z for z in r.stdout.splitlines() if z.startswith(("VERGLEICH", "NACHTEIL", "EINBRUCH", "KETTE"))]
    return {"zeilen": zeilen, "datei": os.path.relpath(ziel, os.path.join(HIER, ".."))}


def main():
    pos = [a for a in sys.argv[1:] if "=" not in a]
    arg = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)
    if len(pos) < 2:
        raise SystemExit(__doc__)
    konsole, lage = pos[0], pos[1]
    os.makedirs(AUS, exist_ok=True)
    stamp = re.search(r"(\d{8}_\d{6})", os.path.basename(konsole)).group(1)
    sp = re.search(r"_sp(\d)", os.path.basename(konsole))
    N = namen()
    tr, ende = truppen(lage, N)
    m = mitschrift(konsole)
    v = vergleich(lage, stamp)
    partie = {"partie": stamp, "erfasst": time.strftime("%Y-%m-%d %H:%M"), "lenker_spieler": int(sp.group(1)) if sp else 1,
              "gegner": arg.get("gegner"), "anmerkung": arg.get("anmerkung"), "letzter_tick": ende,
              "konsole": os.path.relpath(konsole, os.path.join(HIER, "..")), "lage": os.path.relpath(lage, os.path.join(HIER, "..")),
              "truppen": tr, "lenker": m, "vergleich": v}
    json.dump(partie, open(os.path.join(AUS, "partie_%s.json" % stamp), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    kurz = {k: partie[k] for k in ("partie", "erfasst", "lenker_spieler", "gegner", "anmerkung", "letzter_tick")}
    kurz["truppen_ende"] = tr[-1]["je_spieler"] if tr else {}
    kurz["gold_max"] = max([g["gold"] for g in m["gold_bei_bremse"]] or [None]) if m["gold_bei_bremse"] else None
    kurz["bremsen"], kurz["anwerbungen"] = m["ereignisse"]["ANWERBEN-BREMSE"], m["anwerbungen"]
    kurz["nachteil"] = next((z for z in v["zeilen"] if z.startswith("NACHTEIL")), None)
    sammlung = os.path.join(AUS, "partien.jsonl")
    schon = os.path.exists(sammlung) and any(json.loads(z).get("partie") == stamp
                                              for z in open(sammlung, encoding="utf-8") if z.strip())
    if schon:
        print("Partie %s steht schon in partien.jsonl - nicht doppelt angehaengt (Einzeldatei neu geschrieben)" % stamp)
    else:
        with open(sammlung, "a", encoding="utf-8") as f:
            f.write(json.dumps(kurz, ensure_ascii=False) + "\n")
    print("PARTIE %s (Lenker Spieler %s, bis Tick %s)" % (stamp, partie["lenker_spieler"], ende))
    for t in tr:
        print("  Tick %5d | %s" % (t["t"], " | ".join("Sp%s: %d (%s)" % (s, sum(k.values()), ", ".join(
            "%d %s" % (n, a) for a, n in sorted(k.items(), key=lambda x: -x[1])[:3])) for s, k in sorted(t["je_spieler"].items()))))
    print("  Lenker: Bremsen %d, Anwerbungen %d, Gold bei Bremsen max %s" % (kurz["bremsen"], kurz["anwerbungen"], kurz["gold_max"]))
    for z in v["zeilen"]:
        print("  " + z[:220])
    print("gesichert: daten/lernen/partie_%s.json + Zeile in daten/lernen/partien.jsonl" % stamp)


if __name__ == "__main__":
    main()
