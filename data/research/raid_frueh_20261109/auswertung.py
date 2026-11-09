# -*- coding: utf-8 -*-
"""Partie raid_frueh vom 09.11.2026 (B-177, B-178): Wer wurde geworben, wann lag Gold brach, was wurde aus den bestellten Reitern?

Neu heisst: Die Einheit steht in einem Lagebild und im vorigen nicht (Abstand meist unter 150 Takte). Das erste Lagebild (Takt 698) enthaelt die
Starttruppen. Eine Partie, also nur eine erste Richtung. Spieler 1 sind wir.
Eingabe: Lageprotokoll und Mitschrift der Partie, kern_ausweichen.txt (die Ausweichen-Zeilen des Kern-Protokolls dieser Partie). Ausgabe: ergebnis.txt.
"""
import collections
import gzip
import json
import os
import re

HIER = os.path.dirname(os.path.abspath(__file__))
FORSCHUNG = os.path.join(HIER, "..")
LAGE = os.path.join(FORSCHUNG, "lage_20261109_223747_i2.jsonl.gz")
KONSOLE = os.path.join(FORSCHUNG, "aufstellung_20261109_223741_raid_frueh_i2_konsole.txt")
KERN = os.path.join(HIER, "kern_ausweichen.txt")
SOLDATEN = {5, 22, 23, 24, 25, 26, 27, 28, 29, 30, 37, 70, 71, 72, 73, 74, 75, 76}
RAID = {71, 72, 73, 74}
SKLAVE, ASSASSINE, REITER = 71, 73, 74


def eigene(e):
    z = e.split("\n")
    z = z[next(i for i, x in enumerate(z) if x.startswith("nr ")) :]
    k = z[0].split()
    nr, b, t = k.index("nr"), k.index("besitzer"), k.index("typ")
    return {int(s[nr]): int(s[t]) for s in (x.split() for x in z[1:]) if len(s) > t and int(s[b]) == 1}


def bilder_lesen():
    aus = []
    with gzip.open(LAGE, "rt", encoding="utf-8") as f:
        for z in f:
            d = json.loads(z)
            if d.get("einheiten"):
                aus.append((d["t"], d.get("st") or {}, eigene(d["einheiten"])))
    return aus


def main():
    bilder = bilder_lesen()
    aus = ["Eine Partie: nur eine erste Richtung, keine Statistik.", ""]
    neu, tot = collections.Counter(), collections.Counter()
    je_bereich = collections.defaultdict(collections.Counter)
    for (t0, _, a), (t1, _, b) in zip(bilder, bilder[1:]):
        for n, x in b.items():
            if a.get(n) != x and x in SOLDATEN:
                neu[x] += 1
                je_bereich[t1 // 2500 * 2500][x] += 1
        for n, x in a.items():
            if b.get(n) != x and x in SOLDATEN:
                tot[x] += 1
    erstes = collections.Counter(x for x in bilder[0][2].values() if x in SOLDATEN)
    aus.append("Erstes Lagebild (Takt %d), Soldaten je Art: %s" % (bilder[0][0], dict(sorted(erstes.items()))))
    aus.append("Neu je Art: %s" % dict(sorted(neu.items())))
    aus.append("Verschwunden je Art: %s" % dict(sorted(tot.items())))
    aus.append("Neu, die keine Raid-Einheit sind: %d" % sum(v for k, v in neu.items() if k not in RAID))
    aus += ["", "Je 2.500 Takte das erste Lagebild: Takt, Gold, Feuer, Leute | lebend Assassinen, Sklaven, Reiter | neu in diesem Bereich"]
    gesehen = set()
    for t, st, j in bilder:
        b = t // 2500 * 2500
        if b in gesehen:
            continue
        gesehen.add(b)
        c = collections.Counter(j.values())
        aus.append("%6d %6s %3s %4s | %2d %2d %2d | %s" % (t, st.get("gold"), st.get("feuer"), st.get("leute"), c[ASSASSINE], c[SKLAVE], c[REITER], dict(sorted(je_bereich[b].items()))))

    aus += ["", "Bestellte Reiter je Runde: Takt, Gold davor und danach, neu in den naechsten 4 Lagebildern (Assassine, Reiter, Sklave)"]
    text = open(KONSOLE, encoding="utf-8", errors="replace").read()
    summe = collections.Counter()
    bestellt = 0
    for z in text.splitlines():
        m = re.search(r"RAID-WERBUNG: (\d+) Pferdebogen", z)
        if not m:
            continue
        bestellt += int(m.group(1))
        t = int(re.match(r"\s*(\d+) \|", z).group(1))
        i = max(k for k, b in enumerate(bilder) if b[0] <= t)
        spaeter = collections.Counter()
        for k in range(i, min(i + 4, len(bilder) - 1)):
            for n, x in bilder[k + 1][2].items():
                if bilder[k][2].get(n) != x:
                    spaeter[x] += 1
        summe.update(spaeter)
        aus.append("%6d %5d -> %5d (%+d) | %d %d %d" % (t, bilder[i][1].get("gold"), bilder[i + 1][1].get("gold"), bilder[i + 1][1].get("gold") - bilder[i][1].get("gold"), spaeter[ASSASSINE], spaeter[REITER], spaeter[SKLAVE]))
    aus.append("Bestellt %d Reiter, in der ganzen Partie neu %d. Nach diesen Runden neu: Assassinen %d, Reiter %d, Sklaven %d" % (bestellt, neu[REITER], summe[ASSASSINE], summe[REITER], summe[SKLAVE]))

    z = re.findall(r"(?m)^ausweichen tick (\d+): (\d+) Trupps, Wegpunkte (\d+), am Ziel (\d+), festgelaufen (\d+)", open(KERN, encoding="utf-8").read())
    aus += ["", "Ausweichen im Kern (je 500 Takte eine Zeile): %d Zeilen, mit Trupps %d, Wegpunkte zuletzt %s, am Ziel %s, festgelaufen %s" % (len(z), sum(1 for x in z if int(x[1]) > 0), z[-1][2], z[-1][3], z[-1][4])]
    ergebnis = "\n".join(aus) + "\n"
    open(os.path.join(HIER, "ergebnis.txt"), "w", encoding="utf-8", newline="\n").write(ergebnis)
    print(ergebnis)


if __name__ == "__main__":
    main()
