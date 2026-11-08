# -*- coding: utf-8 -*-
"""Zwei ganze Partien auf Instanz 2 (B-174, B-175): gleiche Einstellungen, einmal zickzack=ja, einmal zickzack=nein.

Was das zeigen kann: ob der Schalter in der ganzen Partie etwas Grobes aendert. Was nicht: ob er die Partie besser macht. Es ist je
Einstellung eine Partie, und schon eine Abweichung frueh im Spiel fuehrt zu einem anderen Verlauf. Darum stehen hier nur Zaehlungen.
Tot heisst: Die Einheit steht in einer Runde im Lagebild und in der naechsten nicht mehr (Abstand der Runden rund 115 Takte).
Spieler 1 sind wir. Eingabe: Lageprotokolle und Mitschriften der beiden Partien. Ausgabe: partie_vergleich.txt.
"""
import gzip
import json
import os
import re

HIER = os.path.dirname(os.path.abspath(__file__))
FORSCHUNG = os.path.join(HIER, "..", "..")
PARTIEN = (
    ("zickzack an", "lage_20261109_001758_i2.jsonl.gz", "zickzack_20261109_001758_an_i2_konsole.txt"),
    ("zickzack aus", "lage_20261109_002159_i2.jsonl.gz", "zickzack_20261109_002159_aus_i2_konsole.txt"),
)
SKLAVE = {71}
SCHUETZEN = {22, 23, 70}
GRUPPEN = (("Sklaven (Typ 71)", SKLAVE), ("Schuetzen (Typ 22, 23, 70)", SCHUETZEN))
SP = 1


def eigene(e):
    """{Nummer: Typ} der eigenen Einheiten einer Runde"""
    zeilen = e.split("\n")
    zeilen = zeilen[next(i for i, z in enumerate(zeilen) if z.startswith("nr ")) :]
    kopf = zeilen[0].split()
    nr, besitzer, typ = kopf.index("nr"), kopf.index("besitzer"), kopf.index("typ")
    aus = {}
    for z in zeilen[1:]:
        t = z.split()
        if len(t) > typ and int(t[besitzer]) == SP:
            aus[int(t[nr])] = int(t[typ])
    return aus


def auswerten(lage):
    rund, vor = 0, None
    gesehen = {n: set() for n, _ in GRUPPEN}
    tot = dict.fromkeys(gesehen, 0)
    summe = dict.fromkeys(gesehen, 0)
    letzter_t = 0
    with gzip.open(lage, "rt", encoding="utf-8") as f:
        for z in f:
            d = json.loads(z)
            if "einheiten" not in d or not d["einheiten"]:
                continue
            letzter_t = d.get("t", letzter_t)
            jetzt = eigene(d["einheiten"])
            rund += 1
            for name, arten in GRUPPEN:
                hier = {n for n, t in jetzt.items() if t in arten}
                gesehen[name] |= hier
                summe[name] += len(hier)
                if vor is not None:
                    tot[name] += sum(1 for n, t in vor.items() if t in arten and jetzt.get(n) != t)
            vor = jetzt
    return rund, letzter_t, gesehen, tot, summe


def main():
    aus = ["Eine Partie je Einstellung: nur eine erste Richtung, keine Statistik.", ""]
    for name, lage, konsole in PARTIEN:
        pfad = os.path.join(FORSCHUNG, lage)
        rund, t, gesehen, tot, summe = auswerten(pfad)
        text = open(os.path.join(FORSCHUNG, konsole), encoding="utf-8", errors="replace").read()
        brand = re.search(r"Brandtrupp: (\d+) Gebaeude", text).group(1)
        jagd = re.search(r"Reiterjagd: (\d+) Arbeiter", text).group(1)
        ende = re.search(r"Ende Phase 2 bei Tick (\d+) nach (\d+) Runden \((.*?) s je Runde\)", text)
        ang = re.search(r"Angriff: zerstoert (\d+) Gebaeude .*?eigene Verluste (\d+)", text)
        aus.append("%s: Ende bei Takt %s nach %s Runden, %s s je Runde" % (name, ende.group(1), ende.group(2), ende.group(3)))
        aus.append("  Brandtrupp: %s Gebaeude angezuendet; Angriff: %s Gebaeude zerstoert, eigene Verluste %s; Reiterjagd: %s Arbeiter getoetet" % (brand, ang.group(1), ang.group(2), jagd))
        for g, _ in GRUPPEN:
            aus.append("  %-28s verschiedene Nummern %3d, tot %3d, im Mittel am Leben %.1f" % (g, len(gesehen[g]), tot[g], summe[g] / rund))
        aus.append("  Lagebilder: %d, letztes bei Takt %d" % (rund, t))
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "partie_vergleich.txt"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
