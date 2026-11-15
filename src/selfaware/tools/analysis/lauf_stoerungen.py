# -*- coding: utf-8 -*-
"""How much walking time our units lose in real games (B-182 link 2; Daniel 2026-11-12 23:00: "Stoerungen waehrend des Laufs hin,
z.B. feindliche Einheiten, Terrain oder Bevoelkerung ... muss beruecksichtigt werden"; plan point 1 of 13.11.2026 21:42).

From a Lageprotokoll (lage_*.jsonl.gz, one line per round, all units with zustand, position and walk target laufx/laufy): every
section between two rounds in which an own fighter walks (state 101) towards its walk target. Expected = how many fields the game's
rule (services/laufmodell.py) gives on the straight line to the walk target on this terrain in the time between the two rounds
(at most the distance); walked = fields between the two positions (Schach). A section is
  on time     walked >= 80 % of expected
  slow        50-80 %
  disrupted   under 50 % - then the units within 1 field of the second position are counted (own fighters, own workers, enemy
              fighters, enemy workers, neutral).
Limits: the straight line is the shortest way - a winding path counts as slower than it was (the shares of "slow" are an upper
bound); sections longer than MAX_GAP ticks and under MIN_EXPECTED fields are left out (too little to tell).

Call (PYTHONPATH=src): python -m selfaware.tools.analysis.lauf_stoerungen gelaende=data/research/gelaende_LigaParadisePlains.txt
       data/research/lage_20261112_210347_i2.jsonl.gz [...]
"""

import collections
import gzip
import json
import sys

from selfaware.services import laufmodell as LM

WALKING = 101
MAX_GAP = 200  # ticks between two rounds at most
MIN_EXPECTED = 4  # fields expected at least
WORKERS = set(range(1, 22)) | set(range(31, 37))


def table(text):
    """'einheiten' text block -> {nr: dict} (first line: 'tick N', second: field names)."""
    lines = text.split("\n")
    names = lines[1].split()
    out = {}
    for line in lines[2:]:
        v = line.split()
        if len(v) >= 7:
            d = {k: int(x) for k, x in zip(names, v, strict=False)}
            out[d["nr"]] = d
    return out


line_fields = LM.gerade  # one place: services/laufmodell.py


def expected_fields(typ, a, goal, ticks, tile):
    """Fields the game's rule lets a unit of this type walk from a towards goal in `ticks` ticks (at most the distance)."""
    fields = line_fields(a, goal)
    if len(fields) < 2:
        return 0
    reach = LM.walk(typ, fields, tile)
    return sum(1 for t in reach if t <= ticks)


def near(units, pos, me, sp=1):
    c = collections.Counter()
    for n, u in units.items():
        if n == me or max(abs(u["x"] - pos[0]), abs(u["y"] - pos[1])) > 1:
            continue
        own, work = u["besitzer"] == sp, u["typ"] in WORKERS
        c[
            "neutral"
            if not u["besitzer"]
            else ("own_" if own else "enemy_") + ("workers" if work else "fighters")
        ] += 1
    return c


def sections(rounds, tile, sp=1):
    """rounds: [(tick, {nr: unit})] -> list of (typ, expected, walked, verdict, near counter)."""
    out = []
    for (t1, u1), (t2, u2) in zip(rounds, rounds[1:], strict=False):
        if not 0 < t2 - t1 <= MAX_GAP:
            continue
        for n, a in u1.items():
            b = u2.get(n)
            if (
                b is None
                or a["besitzer"] != sp
                or a["typ"] not in LM.TYPES
                or a.get("zustand") != WALKING
                or b["typ"] != a["typ"]
                or not a.get("laufx")
            ):
                continue
            goal = (a["laufx"], a["laufy"])
            p1, p2 = (a["x"], a["y"]), (b["x"], b["y"])
            exp = expected_fields(a["typ"], p1, goal, t2 - t1, tile)
            if exp < MIN_EXPECTED:
                continue
            walked = max(abs(p2[0] - p1[0]), abs(p2[1] - p1[1]))
            share = walked / exp
            verdict = "on_time" if share >= 0.8 else ("slow" if share >= 0.5 else "disrupted")
            out.append(
                (
                    a["typ"],
                    exp,
                    walked,
                    verdict,
                    near(u2, p2, n, sp) if verdict == "disrupted" else collections.Counter(),
                )
            )
    return out


def read_rounds(path):
    rounds = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            z = json.loads(line)
            if isinstance(z.get("einheiten"), str):
                rounds.append((z["t"], table(z["einheiten"])))
    return rounds


def main():
    from selfaware.tools.experiments.gelaende_erheben import tile_function

    arg = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)
    files = [a for a in sys.argv[1:] if "=" not in a]
    tile = tile_function(arg["gelaende"])

    total, by_type, who = (
        collections.Counter(),
        collections.defaultdict(collections.Counter),
        collections.Counter(),
    )
    for p in files:
        s = sections(read_rounds(p), tile)
        c = collections.Counter(v for _t, _e, _w, v, _n in s)
        print(
            "%s: %d sections - on time %d, slow %d, disrupted %d"
            % (p, len(s), c["on_time"], c["slow"], c["disrupted"]),
            flush=True,
        )
        for typ, _e, _w, v, n in s:
            total[v] += 1
            by_type[typ][v] += 1
            who.update(set(n))  # sections, not units (13.11. 22:05: units were counted first)
            if v == "disrupted" and not n:
                who["nobody_within_1"] += 1
    n = sum(total.values())
    print(
        "ALL: %d sections - on time %d (%.0f %%), slow %d (%.0f %%), disrupted %d (%.0f %%)"
        % (
            n,
            total["on_time"],
            100.0 * total["on_time"] / max(n, 1),
            total["slow"],
            100.0 * total["slow"] / max(n, 1),
            total["disrupted"],
            100.0 * total["disrupted"] / max(n, 1),
        )
    )
    for typ, c in sorted(by_type.items(), key=lambda kv: -sum(kv[1].values())):
        m = sum(c.values())
        print(
            "  type %d: %d sections, disrupted %.0f %%, slow %.0f %%"
            % (typ, m, 100.0 * c["disrupted"] / m, 100.0 * c["slow"] / m)
        )
    print("disrupted sections with ... within 1 field of the stop point:", dict(who.most_common()))


if __name__ == "__main__":
    main()
