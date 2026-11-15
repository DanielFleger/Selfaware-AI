# -*- coding: utf-8 -*-
"""Did each walk order of a game take? (B-182; game 15 of 14.11.2026, S139: archer 309 got a walk order to (186,154), the game
module reported it carried out at tick 3404 - the walk target in the game stayed the old one; the third such case after games 5 and 12.)

Input: the console of the game (lines "BEFEHL Tick N angriff {"lauf":[x,y]} an k Einheiten: [...]", tick = execution tick in the
game) and the per-tick recording of our soldiers (tools/experiments/soldaten_mitschrift.py). An order took for a unit when its walk
target (laufx/laufy) comes within NAH fields of the order's target within TAKTE ticks of the execution; orders whose target was
already the unit's walk target are counted apart. Optional: the game module's log (ucp3.log of the instance) for the group it used.
Per unit order also: its state before, and whether another own walking unit had that target as walk target (game 15: refuted as
a cause - 12 such orders took).

S155: walk orders the core placed itself (raid over the core, Kern 30) come from its log (kern=<samurai_kern.log of the instance>).

Call (PYTHONPATH=src): python -m selfaware.tools.analysis.befehle_greifen <konsole> <soldaten_mitschrift .jsonl> [log=<ucp3.log>]
       [kern=<samurai_kern.log>]
Writes data/research/befehle_greifen_<stamp of the console>.json.
"""

import collections
import json
import os
import re
import sys

from selfaware import workspace as _workspace
from selfaware.tools.experiments import soldaten_mitschrift as SM

NAH = 3  # fields: the walk target counts as the order's target (chain_audit.NEAR)
TAKTE = 20  # ticks after the execution (the game showed taken orders 1-5 ticks after, S136)
BEFEHL = re.compile(r"^BEFEHL Tick (\d+) angriff (\{.*\}) an \S+ Einheiten: \[([\d, ]*)\]")
GRUPPE = re.compile(
    r"ANGRIFF Tick (\d+): (\d+) Einheiten, Gruppe (\d+), Art 17, Ziel (\d+) \(uid (\d+)\)"
)
# S155: the core's own walk orders (Kern 30 writes the units; art 17 - a walk to push through is sent as 17)
KERN = re.compile(
    r"haende tick (\d+): Gruppe \d+, \d+ von \d+ Einheiten von Spieler \d+, Auftrag Auftrag \{ art: 17, a: (\d+), b: (\d+) \}, "
    r"Vorrang \d+ - abgesetzt, Einheiten \[([\d, ]*)\]"
)
WALKING = 101


def befehle(konsole):
    """-> [(tick, (x, y), [units])] of the walk orders the game module carried out."""
    aus = []
    for z in open(konsole, encoding="utf-8", errors="replace"):
        m = BEFEHL.match(z.strip())
        if m and '"lauf"' in m.group(2):
            aus.append(
                (
                    int(m.group(1)),
                    tuple(json.loads(m.group(2))["lauf"]),
                    [int(n) for n in m.group(3).split(",") if n.strip()],
                )
            )
    return aus


def kern_befehle(log):
    """-> [(tick, (x, y), [units])] of the walk orders the core placed - only its last game (the ticks fall back at a new game)."""
    aus, vor = [], None
    for z in open(log, encoding="utf-8", errors="replace"):
        m = KERN.search(z)
        if not m:
            continue
        t = int(m.group(1))
        if vor is not None and t < vor - 500:
            aus = []
        vor = t
        aus.append(
            (
                t,
                (int(m.group(2)), int(m.group(3))),
                [int(n) for n in m.group(4).split(",") if n.strip()],
            )
        )
    return aus


def gruppen(log):
    """{(tick, x, y): group} from the module's log - only its last game (the ticks fall back at a new game)."""
    teil, vor = [], None
    for z in open(log, encoding="utf-8", errors="replace"):
        m = GRUPPE.search(z)
        if not m:
            continue
        t = int(m.group(1))
        if vor is not None and t < vor - 500:
            teil = []
        teil.append(m)
        vor = t
    return {(int(m.group(1)), int(m.group(4)), int(m.group(5))): int(m.group(3)) for m in teil}


def stand_lesen(mitschrift):
    """{unit: {tick: row}} of the last game in the recording (row: typ x y zustand leben zielart zieleinheit nahziel laufx laufy)."""
    stand = collections.defaultdict(dict)
    vor = None
    for z in open(mitschrift, encoding="utf-8"):
        r = json.loads(z)
        if r.get("start") and vor is not None and r["t"] < vor:
            stand.clear()
        vor = r["t"]
        for n, row in r.get("e", {}).items():
            stand[int(n)][r["t"]] = row
    return stand


def _zu(stand, n, t):
    d = stand.get(n, {})
    ks = [k for k in d if k <= t]
    return d[max(ks)] if ks else None


def _nah(row, ziel):
    return row is not None and max(abs(row[8] - ziel[0]), abs(row[9] - ziel[1])) <= NAH


def greifen(orders, stand, gruppe=None):
    """-> one dict per unit order: tick, unit, target, group, state before, walk target before, already, occupied_by, took."""
    gruppe = gruppe or {}
    aus = []
    for t, ziel, einheiten in orders:
        for n in einheiten:
            vorher = _zu(stand, n, t - 1)
            if vorher is None:
                continue
            belegt = [
                m
                for m in stand
                if m != n
                and _zu(stand, m, t - 1)
                and _zu(stand, m, t - 1)[3] == WALKING
                and tuple(_zu(stand, m, t - 1)[8:10]) == tuple(ziel)
            ]
            z = {
                "takt": t,
                "einheit": n,
                "ziel": list(ziel),
                "gruppe": gruppe.get((t, ziel[0], ziel[1])),
                "zustand": vorher[3],
                "laufziel_vorher": [vorher[8], vorher[9]],
                "schon": _nah(vorher, ziel),
                "belegt_von": belegt[0] if belegt else None,
                "einheiten_im_befehl": len(einheiten),
                "gegriffen": any(_nah(_zu(stand, n, t + k), ziel) for k in range(TAKTE + 1)),
            }
            if not z["gegriffen"] and max(stand[n]) < t + TAKTE:
                # Partie 17 (14.11.2026, S143): ausgewertet, waehrend die Mitschrift noch schrieb - fuenf Befehle ohne die Takte danach
                # hiessen "nicht gegriffen" und hatten alle gegriffen. Ohne TAKTE Takte nach der Ausfuehrung ist es offen
                z["gegriffen"] = None
            if z["gegriffen"] is False:
                # S139: was der Marschbefehl je Einheit prueft (Mitschriften ab 14.11.2026 21:05) - vor und nach der Ausfuehrung
                nach = _zu(stand, n, t + TAKTE)
                z["felder_vorher"] = dict(zip(SM.FELDER[10:], vorher[10:], strict=False))
                z["felder_nachher"] = (
                    dict(zip(SM.FELDER[10:], nach[10:], strict=False)) if nach else {}
                )
            aus.append(z)
    return aus


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    frei = [a for a in argv if "=" not in a]
    arg = dict(a.split("=", 1) for a in argv if "=" in a)
    if len(frei) != 2:
        raise SystemExit(__doc__)
    orders = befehle(frei[0]) + (kern_befehle(arg["kern"]) if "kern" in arg else [])
    zeilen = greifen(
        sorted(orders), stand_lesen(frei[1]), gruppen(arg["log"]) if "log" in arg else None
    )
    neu = [z for z in zeilen if not z["schon"]]
    nicht = [z for z in neu if z["gegriffen"] is False]
    offen = [z for z in neu if z["gegriffen"] is None]
    for z in nicht:
        print("GRIFF NICHT:", json.dumps(z))
    print(
        "Laufbefehle je Einheit: %d, davon Ziel schon gesetzt %d; neu %d, gegriffen %d, nicht gegriffen %d, offen %d "
        "(Mitschrift endet vor %d Takten nach der Ausfuehrung)"
        % (
            len(zeilen),
            len(zeilen) - len(neu),
            len(neu),
            len(neu) - len(nicht) - len(offen),
            len(nicht),
            len(offen),
            TAKTE,
        )
    )
    print(
        "Ziel schon Laufziel einer anderen eigenen Einheit: gegriffen %d, nicht gegriffen %d"
        % (
            sum(1 for z in neu if z["belegt_von"] and z["gegriffen"]),
            sum(1 for z in nicht if z["belegt_von"]),
        )
    )
    stempel = re.search(r"(\d{8}_\d{6})", os.path.basename(frei[0]))
    pfad = os.path.join(
        _workspace.DATA,
        "befehle_greifen_%s.json" % (stempel.group(1) if stempel else "ohne_stempel"),
    )
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(
            {
                "konsole": frei[0],
                "mitschrift": frei[1],
                "nah": NAH,
                "takte": TAKTE,
                "befehle": zeilen,
            },
            f,
            indent=1,
        )
    print("->", pfad)


if __name__ == "__main__":
    main()
