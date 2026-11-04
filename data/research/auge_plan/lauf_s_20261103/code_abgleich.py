# -*- coding: utf-8 -*-
"""B-142: Wo weicht der laufende Spielcode vom Ghidra-Export ab? Liest nur (ReadProcessMemory), aendert nichts am Spiel.

Anlass: Das Tor reagierte bei 3 bis 16 Feldern, nicht bei 24, obwohl der Export 200 Mikro (25 Felder) sagt. Im Speicher von Instanz 2 steht 140. Der Vermittler ist UCP3: Er aendert Befehle im laufenden Spiel. Wer nur den Export liest, rechnet also mit falschen Zahlen.

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/code_abgleich.py <prozessnummer> > data/research/auge_plan/lauf_s_20261103/code_abgleich.txt
Dazu eine Datei code_abgleich.json: je Funktion die abweichenden Befehle.
"""
import collections
import glob
import json
import os
import sys

from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle

E = r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference\functions"
HIER = os.path.dirname(os.path.abspath(__file__))


def main(pid):
    q = ProzessQuelle(pid)
    print("Programm:", q.pfad)
    funktionen = geprueft = gleich = 0
    aus = []
    fehler = collections.Counter()
    for f in sorted(glob.glob(os.path.join(E, "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        zeilen = d.get("assembly") or []
        if not zeilen:
            continue
        funktionen += 1
        abw = []
        for z in zeilen:
            soll = bytes.fromhex(z["bytes"])
            try:
                ist = q.lies(int(z["address"], 16), len(soll))
            except OSError:
                fehler["nicht lesbar"] += 1
                continue
            geprueft += 1
            if ist == soll:
                gleich += 1
            else:
                abw.append({"adresse": z["address"], "befehl": z["text"], "export": z["bytes"], "speicher": ist.hex()})
        if abw:
            aus.append({"funktion": d["name"].split("::")[-1], "adresse": d["address"], "abweichend": len(abw), "befehle_gesamt": len(zeilen), "zeilen": abw})
    json.dump(aus, open(os.path.join(HIER, "code_abgleich.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"Funktionen {funktionen}, Befehle geprueft {geprueft}, gleich {gleich}, abweichend {geprueft - gleich}, nicht lesbar {dict(fehler)}")
    print(f"Funktionen mit Abweichung: {len(aus)}")
    ganz = [a for a in aus if a["abweichend"] >= 0.5 * a["befehle_gesamt"]]
    print("Fast ganz ersetzt (mindestens die Haelfte):", len(ganz))
    # Sprung am Funktionsanfang = Haken: Die ganze Funktion laeuft anders
    for a in sorted(aus, key=lambda z: z["adresse"]):
        erste = a["zeilen"][0]
        print(f'{a["adresse"]} {a["funktion"]}: {a["abweichend"]} von {a["befehle_gesamt"]} Befehlen')
        for z in a["zeilen"][:6]:
            print(f'    {z["adresse"]} {z["befehl"][:60]:60s} Export {z["export"][:24]:24s} Speicher {z["speicher"][:24]}')
        if a["abweichend"] > 6:
            print(f'    ... noch {a["abweichend"] - 6}')


if __name__ == "__main__":
    main(int(sys.argv[1]))
