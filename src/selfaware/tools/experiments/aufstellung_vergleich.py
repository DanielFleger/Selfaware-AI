"""Zwei oder mehr Aufstellungen nacheinander spielen und die Kennzahlen nebeneinander stellen (B-176).

Aufruf: python -m selfaware.tools.experiments.aufstellung_vergleich --instanz 2 raid_frueh vorstoss_laptop
Eine Partie je Aufstellung ist nur eine erste Richtung; mit --partien n laeuft jede Aufstellung n-mal, abwechselnd.
Ausgabe: je Partie die Mitschrift data/research/aufstellung_<stempel>_<name>_i<n>_konsole.txt, am Ende eine Tabelle.
"""

import argparse
import collections
import glob
import gzip
import json
import os
import re
import subprocess
import sys
import time

from selfaware import workspace

FORSCHUNG = os.path.join(workspace.ROOT, "data", "research")
# wie SOLDATEN in auge_lauf_s.py, getrennt in Raid-Einheiten und alle anderen, ohne Lord
GRUPPEN = {
    "raid": {71, 72, 73, 74},
    "reiter": {74},
    "andere": {5, 22, 23, 24, 25, 26, 27, 28, 29, 30, 37, 70, 75, 76},
}


def _eigene(text, sp=1):
    zeilen = text.split("\n")
    zeilen = zeilen[next(i for i, z in enumerate(zeilen) if z.startswith("nr ")) :]
    kopf = zeilen[0].split()
    nr, bes, typ = kopf.index("nr"), kopf.index("besitzer"), kopf.index("typ")
    return {
        int(t[nr]): int(t[typ])
        for t in (z.split() for z in zeilen[1:])
        if len(t) > typ and int(t[bes]) == sp
    }


def lage_zahlen(pfad):
    """Je Gruppe (neu, tot): wie viele eigene Einheiten seit dem ersten Lagebild dazukamen und wie viele verschwanden.

    Das erste Lagebild kommt um Takt 700 und enthaelt die Starttruppen (Takt 202 und 403), die sind nicht geworben. Wer vorher wirbt, zaehlt
    hier nicht mit. Bei nur Raids muss "andere neu" 0 sein.
    """
    neu = dict.fromkeys(GRUPPEN, 0)
    tot = dict.fromkeys(GRUPPEN, 0)
    je_art = collections.Counter()
    vor = None
    with gzip.open(pfad, "rt", encoding="utf-8") as f:
        for z in f:
            d = json.loads(z)
            if not d.get("einheiten"):
                continue
            jetzt = _eigene(d["einheiten"])
            if vor is not None:
                je_art.update(
                    t
                    for n, t in jetzt.items()
                    if vor.get(n) != t and t in GRUPPEN["raid"] | GRUPPEN["andere"]
                )
                for g, arten in GRUPPEN.items():
                    neu[g] += sum(1 for n, t in jetzt.items() if t in arten and vor.get(n) != t)
                    tot[g] += sum(1 for n, t in vor.items() if t in arten and jetzt.get(n) != t)
            vor = jetzt
    return {**{g: (neu[g], tot[g]) for g in GRUPPEN}, "je_art": dict(sorted(je_art.items()))}


def kennzahlen(text):
    """Die Zahlen aus dem Ende der Mitschrift. None, wo die Zeile fehlt: Eine fehlende Zahl ist keine Null."""

    def such(muster):
        m = re.search(muster, text)
        return int(m.group(1)) if m else None

    return {
        "ende": such(r"Ende Phase 2 bei Tick (\d+)"),
        "angezuendet": such(r"Brandtrupp: (\d+) Gebaeude"),
        "arbeiter": such(r"Reiterjagd: (\d+) Arbeiter"),
        "zerstoert": such(r"Angriff: zerstoert (\d+) Gebaeude"),
        "verluste": such(r"eigene Verluste (\d+)"),
        "reiter_bestellt": sum(
            int(n) for n in re.findall(r"RAID-WERBUNG: (\d+) Pferdebogen", text)
        ),
    }


def partie(name, instanz, stempel):
    konsole = os.path.join(FORSCHUNG, f"aufstellung_{stempel}_{name}_i{instanz}_konsole.txt")
    umgebung = dict(os.environ, SHC_INSTANZ=str(instanz), PYTHONIOENCODING="utf-8")
    vorher = time.time()
    with open(konsole, "w", encoding="utf-8") as f:
        code = subprocess.call(
            [sys.executable, "-m", "selfaware.runtime.live.erstes_spiel", f"aufstellung={name}"],
            stdout=f,
            stderr=subprocess.STDOUT,
            env=umgebung,
        )
    neu = [
        p
        for p in glob.glob(os.path.join(FORSCHUNG, f"lage_*_i{instanz}.jsonl.gz"))
        if os.path.getmtime(p) >= vorher
    ]
    text = open(konsole, encoding="utf-8", errors="replace").read()
    z = kennzahlen(text)
    z.update(
        code=code,
        konsole=os.path.basename(konsole),
        einheiten=lage_zahlen(max(neu, key=os.path.getmtime)) if neu else None,
    )
    return z


def tabelle(ergebnisse):
    aus = [
        "Aufstellung: Rueckgabe | Ende | angezuendet | zerstoert | Verluste | Arbeiter | Raid neu/tot | Reiter bestellt/neu | andere Soldaten neu/tot"
    ]
    for name, z in ergebnisse:
        e = z.get("einheiten") or dict.fromkeys(GRUPPEN, ("-", "-"))
        aus.append(
            "  %-18s %s | %s | %s | %s | %s | %s | %s/%s | %s/%s | %s/%s"
            % (
                name,
                z["code"],
                z["ende"],
                z["angezuendet"],
                z["zerstoert"],
                z["verluste"],
                z["arbeiter"],
                *e["raid"],
                z["reiter_bestellt"],
                e["reiter"][0],
                *e["andere"],
            )
        )
    return "\n".join(aus)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("aufstellungen", nargs="+")
    p.add_argument("--instanz", type=int, required=True)
    p.add_argument("--partien", type=int, default=1)
    a = p.parse_args()
    if a.instanz in (4, 5):
        sys.exit("Instanz 4 gehoert SAI, Instanz 5 ist Daniels Spiel")
    ergebnisse = []
    for i in range(a.partien):
        for name in a.aufstellungen:
            stempel = time.strftime("%Y%m%d_%H%M%S")
            print(f"Partie {i + 1}, Aufstellung {name}", flush=True)
            ergebnisse.append((name, partie(name, a.instanz, stempel)))
            print(tabelle(ergebnisse[-1:]), flush=True)
            print(
                "  neu je Art:",
                (ergebnisse[-1][1].get("einheiten") or {}).get("je_art"),
                flush=True,
            )
    print(tabelle(ergebnisse))


if __name__ == "__main__":
    main()
