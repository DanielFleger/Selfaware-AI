# -*- coding: utf-8 -*-
"""S155: Did the core's pushing of walk orders through fights help? (Kern 30, raid over the core; Daniel 15.11.2026 00:04 "eine einheit
geht nicht einfach weiter, sie braucht noch weitere laufbefehle um durchzuspammen".)

Input: the core's log (samurai_kern.log of the instance, lines "durchsetzen tick T: Einheit N kaempft gegen G - Laufauftrag (x,y) ab jetzt
jeden Takt neu" and "durchsetzen tick T: Einheit N kaempft nicht mehr gegen einen anderen - nach K Takten, Laufauftrag M mal neu"), the
per-tick recording of our soldiers (tools/experiments/soldaten_mitschrift.py) and optionally the round log (lage_*.jsonl.gz) for the
opponent's type and owner.

Per episode (a fight against another than the allowed opponent, start to end): unit, type, opponent, walk target, ticks and orders until
it ended, the state right after, the distance to the walk target at the start and right after the end. Per chain (the episodes of one unit
with the same walk target in a row): the distance at the first start and at the end of the last, and whether the unit came within NAH
fields of the walk target before it got another one or the recording ended.

Call (PYTHONPATH=src): python -m selfaware.tools.analysis.durchsetzen_auswerten <samurai_kern.log> <soldaten_mitschrift .jsonl>
       [lage=<lage_*.jsonl.gz>]
Writes data/research/durchsetzen_<stamp of the recording>.json.
"""

import collections
import gzip
import json
import os
import re
import sys

from selfaware import workspace as _workspace
from selfaware.tools.analysis import befehle_greifen as BG

NAH = BG.NAH  # fields: the walk target counts as reached (the same reach as for "the order took")
BEGINN = re.compile(
    r"durchsetzen tick (\d+): Einheit (\d+) kaempft gegen (-?\d+) - Laufauftrag \((\d+),(\d+)\) ab jetzt jeden Takt neu"
)
ENDE = re.compile(
    r"durchsetzen tick (\d+): Einheit (\d+) kaempft nicht mehr gegen einen anderen - nach (\d+) Takten, Laufauftrag (\d+) mal neu"
)
WALKING = BG.WALKING


def ereignisse(log):
    """-> [(tick, "beginn", unit, opponent, (x, y)) | (tick, "ende", unit, ticks, orders)] of the last game in the core's log."""
    aus, vor = [], None
    for z in open(log, encoding="utf-8", errors="replace"):
        m, art = BEGINN.search(z), "beginn"
        if not m:
            m, art = ENDE.search(z), "ende"
        if not m:
            continue
        t = int(m.group(1))
        if vor is not None and t < vor - 500:
            aus = []
        vor = t
        if art == "beginn":
            aus.append(
                (t, art, int(m.group(2)), int(m.group(3)), (int(m.group(4)), int(m.group(5))))
            )
        else:
            aus.append((t, art, int(m.group(2)), int(m.group(3)), int(m.group(4))))
    return aus


def episoden(ev):
    """Start and end of each fight per unit -> [{unit, start, end, opponent, target, ticks, orders}] (end None: still open)."""
    offen, aus = {}, []
    for e in ev:
        if e[1] == "beginn":
            offen[e[2]] = {
                "einheit": e[2],
                "beginn": e[0],
                "gegner": e[3],
                "ziel": list(e[4]),
                "ende": None,
                "takte": None,
                "mal": None,
            }
            aus.append(offen[e[2]])
        elif e[2] in offen:
            p = offen.pop(e[2])
            p.update(ende=e[0], takte=e[3], mal=e[4])
    return aus


def lage_lesen(pfad):
    """{tick: {unit: (owner, type)}} from the round log."""
    aus = {}
    with gzip.open(pfad, "rt", encoding="utf-8") as f:
        for z in f:
            r = json.loads(z)
            zeilen = r.get("einheiten", "").splitlines()
            if len(zeilen) < 2:
                continue
            kopf = zeilen[1].split()
            i_nr, i_b, i_t = kopf.index("nr"), kopf.index("besitzer"), kopf.index("typ")
            aus[r["t"]] = {
                int(w[i_nr]): (int(w[i_b]), int(w[i_t]))
                for w in (s.split() for s in zeilen[2:])
                if len(w) == len(kopf)
            }
    return aus


def _abstand(row, ziel):
    return None if row is None else max(abs(row[1] - ziel[0]), abs(row[2] - ziel[1]))


def auswerten(eps, stand, lage=None):
    """Fills each episode and builds the chains; -> (episodes, chains)."""
    runden = sorted(lage) if lage else []
    for p in eps:
        n, t0 = p["einheit"], p["beginn"]
        vor = BG._zu(stand, n, t0 - 1)
        p["typ"] = vor[0] if vor else None
        p["abstand_beginn"] = _abstand(vor, p["ziel"])
        if p["ende"] is not None:
            nach = BG._zu(stand, n, p["ende"] + 1)
            p["zustand_danach"] = nach[3] if nach else None
            p["abstand_ende"] = _abstand(nach, p["ziel"])
        if runden:
            r = max((x for x in runden if x <= t0), default=None)
            p["gegner_art"] = lage[r].get(p["gegner"]) if r is not None else None
    ketten, je = [], collections.defaultdict(list)
    for p in eps:
        je[p["einheit"]].append(p)
    for n, liste in je.items():
        kette = None
        for p in liste:
            if kette is None or kette["ziel"] != p["ziel"]:
                kette = {
                    "einheit": n,
                    "typ": p["typ"],
                    "ziel": p["ziel"],
                    "beginn": p["beginn"],
                    "kaempfe": 0,
                    "befehle": 0,
                    "abstand_beginn": p["abstand_beginn"],
                }
                ketten.append(kette)
            kette["kaempfe"] += 1
            kette["befehle"] += p["mal"] or 0
            kette["ende"] = p["ende"]
            kette["abstand_ende"] = p.get("abstand_ende")
    for k in ketten:
        ticks = sorted(t for t in stand.get(k["einheit"], {}) if t >= k["beginn"])
        k["erreicht"] = None
        for t in ticks:
            row = stand[k["einheit"]][t]
            if [row[8], row[9]] != k["ziel"] and t > (k["ende"] or k["beginn"]):
                break  # a new walk target: the chain is over
            if _abstand(row, k["ziel"]) <= NAH:
                k["erreicht"] = t
                break
        k["lebt_am_ende"] = bool(ticks) and ticks[-1] == max(max(v) for v in stand.values())
    return eps, ketten


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    frei = [a for a in argv if "=" not in a]
    arg = dict(a.split("=", 1) for a in argv if "=" in a)
    if len(frei) != 2:
        raise SystemExit(__doc__)
    eps, ketten = auswerten(
        episoden(ereignisse(frei[0])),
        BG.stand_lesen(frei[1]),
        lage_lesen(arg["lage"]) if "lage" in arg else None,
    )
    fertig = [p for p in eps if p["ende"] is not None]
    print(
        "Kaempfe gegen einen anderen als das Ziel: %d (%d Einheiten), beendet %d, offen %d"
        % (len(eps), len({p["einheit"] for p in eps}), len(fertig), len(eps) - len(fertig))
    )
    print("  Takte bis zum Ende:", sorted(collections.Counter(p["takte"] for p in fertig).items()))
    print(
        "  neue Laufbefehle bis zum Ende:",
        sorted(collections.Counter(p["mal"] for p in fertig).items()),
    )
    print(
        "  Zustand direkt danach:",
        collections.Counter(p.get("zustand_danach") for p in fertig).most_common(),
    )
    print("  Art der Einheit:", collections.Counter(p["typ"] for p in eps).most_common())
    if any("gegner_art" in p for p in eps):
        print(
            "  Gegner (Besitzer, Art):",
            collections.Counter(
                tuple(p["gegner_art"]) if p.get("gegner_art") else None for p in eps
            ).most_common(8),
        )
    print(
        "Ketten (eine Einheit, dasselbe Laufziel): %d, Laufziel erreicht %d"
        % (len(ketten), sum(1 for k in ketten if k["erreicht"]))
    )
    for k in sorted(ketten, key=lambda k: -k["kaempfe"])[:12]:
        print(
            "  Einheit %d (Typ %s) -> %s: %d Kaempfe, %d Laufbefehle, Abstand %s -> %s, erreicht %s"
            % (
                k["einheit"],
                k["typ"],
                tuple(k["ziel"]),
                k["kaempfe"],
                k["befehle"],
                k["abstand_beginn"],
                k["abstand_ende"],
                "Takt %d" % k["erreicht"] if k["erreicht"] else "nein",
            )
        )
    stempel = re.search(r"(\d{8}_\d{6})", os.path.basename(frei[1]))
    pfad = os.path.join(
        _workspace.DATA, "durchsetzen_%s.json" % (stempel.group(1) if stempel else "ohne_stempel")
    )
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(
            {
                "kern_log": frei[0],
                "mitschrift": frei[1],
                "lage": arg.get("lage"),
                "nah": NAH,
                "episoden": eps,
                "ketten": ketten,
            },
            f,
            indent=1,
        )
    print("->", pfad)


if __name__ == "__main__":
    main()
