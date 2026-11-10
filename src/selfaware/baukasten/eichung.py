"""Eichung der Wirkungsrechnung aus echten Partien (B-182, Plan_Raid_Liga: Fokus 1).

Die Raid-Module schreiben jede Zuweisung und jeden Erfolg in die Mitschrift: Brandtrupp (Sklaven an Gebaeuden, seit B-129), Reiterjagd und
Nahkampf-Raid (Arbeiter und Gebaeude, Erfolgszeilen seit B-182). Diese Datei paart beides je Einheit und Ziel und misst je Art und Zielart:
- Erfolgsanteil: Erfolge je Zuweisung, mit einer gedachten Zuweisung mit und einer ohne Erfolg dazu (wenige Daten ergeben so nie 0 oder 100 %).
- Takte am Ziel: Median von (Takte von der Zuweisung bis zum Erfolg) minus (Weg beim Zuweisen mal Takte je Feld der Art).
Gemessen an den Reihen 6 bis 9 (10.11.): Sklaven hatten in 18 % der 557 Zuweisungen Erfolg, nach 550 Takten am Ziel (Median); die Rechnung
nahm sicheren Erfolg nach 165 Takten an. wirkung.Wissen nimmt diese Werte statt der Ersatzwerte, sobald genug Daten da sind.
Nur Sichtbares (FAIRNESS R3): Die Mitschrift enthaelt nur, was der Lenker selbst gesehen und befohlen hat.

Aufruf: python -m selfaware.baukasten.eichung <konsole> [...] [--schreiben]
"""

import collections
import datetime
import json
import os
import re
import statistics
import sys

import selfaware.services.spielwerte as SW
from selfaware import workspace

EICHUNG = os.path.join(workspace.DATA, "raid_eichung.json")
MIN_ZUWEISUNGEN = 10  # Startwert: darunter bleibt der Erfolgsanteil beim Ersatz
MIN_ERFOLGE = 5  # Startwert: darunter bleiben die Takte am Ziel beim Ersatz

_TAKT = re.compile(r"\s*(\d+) \|")
# (Zuweisung, Erfolg, Zielart, feste Art oder None = Art steht in der Zeile)
MUSTER = (
    (
        re.compile(
            r"BRANDTRUPP: Sklave (?P<n>\d+) -> Gebaeude (?P<z>\d+) \(Typ \d+\) bei \(\d+, \d+\), (?P<d>\d+) Felder"
        ),
        re.compile(
            r"BRANDTRUPP: Sklave (?P<n>\d+) hat Gebaeude (?P<z>\d+) \(Typ \d+\) angezuendet"
        ),
        "g",
        71,
    ),
    (
        re.compile(
            r"REITERJAGD: Reiter (?P<n>\d+) jagt Arbeiter (?P<z>\d+) \(Typ \d+\) in (?P<d>\d+) Feldern"
        ),
        re.compile(r"REITERJAGD: Reiter (?P<n>\d+) hat Arbeiter (?P<z>\d+) erledigt"),
        "e",
        74,
    ),
    (
        re.compile(
            r"NAHKAMPF-RAID: (?P<n>\d+) \(Typ (?P<t>\d+)\) -> Gebaeude (?P<z>\d+) \(Typ \d+\) bei \(\d+, \d+\), \d+ Wegpunkte, (?P<d>\d+) Felder"
        ),
        re.compile(r"NAHKAMPF-RAID: (?P<n>\d+) \(Typ \d+\) hat Gebaeude (?P<z>\d+) erledigt"),
        "g",
        None,
    ),
    (
        re.compile(
            r"NAHKAMPF-RAID: (?P<n>\d+) \(Typ (?P<t>\d+)\) -> Arbeiter (?P<z>\d+) \(Typ \d+\) bei \(\d+, \d+\), \d+ Wegpunkte, (?P<d>\d+) Felder"
        ),
        re.compile(r"NAHKAMPF-RAID: (?P<n>\d+) \(Typ \d+\) hat Arbeiter (?P<z>\d+) erledigt"),
        "e",
        None,
    ),
)


# Muster, die dieselbe Erfolgszeile teilen (der Nahkampf-Raid meldet Gebaeude und Arbeiter mit demselben Satz)
MODUL = (0, 1, 2, 2)


def aus_zeilen(zeilen):
    """{(Art, Zielart): {"zuweisungen": n, "dauer": [Takte], "weg": [Felder]}} aus den Zeilen einer Mitschrift. Ein Modul ohne eine einzige
    Erfolgszeile in dieser Mitschrift zaehlt hier nicht: Vor B-182 schrieben Reiterjagd und Nahkampf-Raid keine, ihre Zuweisungen waeren
    sonst lauter Fehlschlaege. (Eine echte Partie ganz ohne Erfolg dieses Moduls faellt dadurch auch heraus.)"""
    aus = collections.defaultdict(lambda: {"zuweisungen": 0, "dauer": [], "weg": []})
    zuweisungen = collections.Counter()
    mit_erfolg = set()
    offen = {}
    for zeile in zeilen:
        m = _TAKT.match(zeile)
        if not m:
            continue
        t = int(m.group(1))
        # in Lesereihenfolge: Jedes Modul schreibt den Erfolg mit dem alten Ziel vor die neue Zuweisung derselben Einheit in dieselbe Zeile
        # (11:25 berichtigt - erst alle Zuweisungen, dann alle Erfolge zu lesen, ueberschrieb das alte Ziel und verlor die meisten Erfolge)
        ereignisse = sorted(
            (
                (x.start(), ist_erfolg, i, x)
                for i, (zuw, erf, _, _) in enumerate(MUSTER)
                for ist_erfolg, rz in ((False, zuw), (True, erf))
                for x in rz.finditer(zeile)
            ),
            key=lambda e: e[0],
        )
        for _, ist_erfolg, i, x in ereignisse:
            art, typ = MUSTER[i][2], MUSTER[i][3]
            if not ist_erfolg:
                t_art = typ if typ is not None else int(x.group("t"))
                offen[(MODUL[i], x.group("n"))] = (i, x.group("z"), t, int(x.group("d")), t_art)
                zuweisungen[(MODUL[i], t_art, art)] += 1
                continue
            mit_erfolg.add(MODUL[i])
            o = offen.pop((MODUL[i], x.group("n")), None)
            if o is not None and o[0] == i and o[1] == x.group("z"):
                aus[(o[4], art)]["dauer"].append(t - o[2])
                aus[(o[4], art)]["weg"].append(o[3])
    for (modul, t_art, art), n in zuweisungen.items():
        if modul in mit_erfolg:
            aus[(t_art, art)]["zuweisungen"] += n
    return dict(aus)


def zusammenfassen(roh, partien):
    """Die Werte fuer raid_eichung.json; jede Zahl mit dem, woraus sie stammt."""
    arten = {}
    for (typ, art), w in sorted(roh.items()):
        n, erfolge = w["zuweisungen"], len(w["dauer"])
        tempo = SW.takte_je_feld(typ, "trupp")
        am_ziel = [max(0.0, d - s * tempo) for d, s in zip(w["dauer"], w["weg"], strict=True)]
        arten.setdefault(str(typ), {})[art] = {
            "zuweisungen": n,
            "erfolge": erfolge,
            "anteil": round((erfolge + 1) / (n + 2), 4),
            "takte_bis_erfolg": statistics.median(w["dauer"]) if w["dauer"] else None,
            "weg_felder": statistics.median(w["weg"]) if w["weg"] else None,
            "takte_je_feld": tempo,
            "takte_am_ziel": round(statistics.median(am_ziel), 1) if am_ziel else None,
        }
    return {
        "stand": datetime.date.today().isoformat(),
        "herkunft": "selfaware.baukasten.eichung aus %d Mitschriften" % len(partien),
        "partien": sorted(os.path.basename(p) for p in partien),
        "min_zuweisungen": MIN_ZUWEISUNGEN,
        "min_erfolge": MIN_ERFOLGE,
        "arten": arten,
    }


def aus_mitschriften(pfade):
    roh = collections.defaultdict(lambda: {"zuweisungen": 0, "dauer": [], "weg": []})
    for p in pfade:
        with open(p, encoding="utf-8", errors="replace") as f:
            for k, w in aus_zeilen(f).items():
                roh[k]["zuweisungen"] += w["zuweisungen"]
                roh[k]["dauer"] += w["dauer"]
                roh[k]["weg"] += w["weg"]
    return zusammenfassen(dict(roh), pfade)


def laden(pfad=EICHUNG):
    """{(Art, Zielart): (Erfolgsanteil oder None, Takte am Ziel oder None)}; nur Werte mit genug Daten, sonst None (dann gilt der Ersatz)."""
    try:
        with open(pfad, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return {}
    aus = {}
    for typ, je in d.get("arten", {}).items():
        for art, w in je.items():
            anteil = (
                w["anteil"]
                if w["zuweisungen"] >= d.get("min_zuweisungen", MIN_ZUWEISUNGEN)
                else None
            )
            takte = (
                w["takte_am_ziel"] if w["erfolge"] >= d.get("min_erfolge", MIN_ERFOLGE) else None
            )
            if anteil is not None or takte is not None:
                aus[(int(typ), art)] = (anteil, takte)
    return aus


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    schreiben = "--schreiben" in argv
    pfade = [a for a in argv if a != "--schreiben"]
    d = aus_mitschriften(pfade)
    for typ, je in d["arten"].items():
        for art, w in je.items():
            print(
                "Art %s, Ziel %s: %d Zuweisungen, %d Erfolge, Anteil %.3f, Takte am Ziel %s"
                % (typ, art, w["zuweisungen"], w["erfolge"], w["anteil"], w["takte_am_ziel"])
            )
    if schreiben:
        with open(EICHUNG, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("geschrieben:", EICHUNG)
    return 0


if __name__ == "__main__":
    sys.exit(main())
