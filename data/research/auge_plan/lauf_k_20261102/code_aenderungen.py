# -*- coding: utf-8 -*-
"""B-142: Welche Funktionen des Spiels laufen nicht so, wie sie in der Datei stehen? Vergleicht den Code im Speicher der Laufinstanz mit der exe und ordnet die Stellen den Funktionen zu.
Das Funktionswissen beschreibt die Datei. Wo UCP oder ein Modul Code aendert, gilt dort das Gemessene (Beispiel setCurrentAttackStrength: Staerke = AttForceBase x Welle + 5 statt Welle x 5).

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/code_aenderungen.py 2
Schreibt code_aenderungen.csv neben dieses Programm: Adresse, Laenge, Funktion, Art. Liest nur.
"""
import bisect
import csv
import glob
import json
import os
import struct
import sys

from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz

n = int(sys.argv[1])
HIER = os.path.dirname(os.path.abspath(__file__))
EXPORT = r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference\functions"
q = ProzessQuelle(pid_der_instanz(n))
roh = open(q.pfad, "rb").read()
pe = struct.unpack_from("<I", roh, 0x3C)[0]
anzahl = struct.unpack_from("<H", roh, pe + 6)[0]
opt = struct.unpack_from("<H", roh, pe + 20)[0]
o = pe + 24 + opt
vs, va, rs, rp = struct.unpack_from("<IIII", roh, o + 8)
assert roh[o:o + 5] == b".text", roh[o:o + 8]
datei = roh[rp:rp + min(vs, rs)]
speicher = q.lies(0x400000 + va, len(datei))
stellen = []
i = 0
while i < len(datei):
    if datei[i] != speicher[i]:
        j = i
        while j < len(datei) and (datei[j] != speicher[j] or (j + 8 < len(datei) and datei[j:j + 8] != speicher[j:j + 8])):
            j += 1
        stellen.append((0x400000 + va + i, j - i))
        i = j
    else:
        i += 1
namen = {}
for p in glob.glob(os.path.join(EXPORT, "*.json")):
    try:
        namen[int(os.path.basename(p)[:-5], 16)] = json.load(open(p, encoding="utf-8")).get("name") or ""
    except (ValueError, OSError):
        pass
reihe = sorted(namen)


def funktion(a):
    k = bisect.bisect_right(reihe, a) - 1
    return (reihe[k], namen[reihe[k]].replace("_HoldStrong::", "")) if k >= 0 else (0, "?")


aus = []
for a, l in stellen:
    fa, fn = funktion(a)
    alt = datei[a - 0x400000 - va:a - 0x400000 - va + l]
    neu = speicher[a - 0x400000 - va:a - 0x400000 - va + l]
    art = "Sprung nach aussen" if neu[:1] in (b"\xe9", b"\xe8") else "Zahl oder kurzer Tausch" if l <= 8 else "Stueck ersetzt"
    aus.append((hex(a), l, hex(fa), fn, art, alt[:12].hex(), neu[:12].hex()))
with open(os.path.join(HIER, "code_aenderungen.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(("adresse", "laenge", "funktion_adresse", "funktion", "art", "datei", "speicher"))
    w.writerows(aus)
fu = {}
for x in aus:
    fu.setdefault(x[3], []).append(x)
print("Stellen", len(aus), "Funktionen", len(fu), "Bytes", sum(x[1] for x in aus))
print("Arten", {k: sum(1 for x in aus if x[4] == k) for k in {x[4] for x in aus}})
ki = [n for n in fu if any(w in n for w in ("AI::", "AIC", "Attack", "aiRecruit", "Tribe"))]
print("KI und Angriff", len(ki), sorted(ki)[:60])
