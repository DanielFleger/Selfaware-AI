# -*- coding: utf-8 -*-
"""Walking time per unit type and terrain (B-182 link 2, docs/plans/Plan_Unit_Status_Log.md section 8).

Daniel 2026-11-12 23:00: "du kennst natuerlich die Laufgeschwindigkeit je Einheit je Terrain, das brauchst du auch spaeter damit
du den naechsten Schritt berechnen kannst"; 23:04: "Terrain kannst du eigentlich auch so messen - Erhebung machen und dann einfach
jeweils testen".

One trial: an own unit of type A on a free spot, one walk order N fields east (gerade) or south-east (schraeg), then every tick
from the core: state, field, micro position (feinx, feiny), the game's own speed value of the unit (tempo =
calculatedMovementSpeed), terrain height, path index and length. Result: ticks order -> walking state, the tick of every field
change, ticks per field (median and all), the speed values seen while walking, ticks order -> arrival.

Read from the code before (Wissensregister P13 and L190 in Selfaware-AI, 25.10.): one move every (calculatedMovementSpeed +
stateBasedSpeed + moveDelay + 1) ticks, (stateBasedSpeed + 1) micro steps per move, 8 micro steps a field, diagonal like straight.
The trials check this per type: "formula" in the result is 8 x (speed value + 1) for the speed value seen most.

Call (PYTHONPATH=src, SHC_INSTANZ=2):
  python -m selfaware.tools.experiments.lauf_messen typen=73,75 [felder=24] [richtung=gerade|schraeg] [tempo=40]   (map editor open)
  python -m selfaware.tools.experiments.lauf_messen linie gelaende=data/research/gelaende_LigaParadisePlains.txt
         karte="Liga_Paradise Plains" typen=73,24 [klassen=0x20000000,0x200000,none]     (a fresh skirmish on the map)
"""

import collections
import json
import os
import statistics
import sys
import time

from selfaware import workspace as _workspace
from selfaware.micro.unit_log import type_name
from selfaware.tools.experiments import schlag_messen as S

WALKING = 101
FIELDS = (
    "t",
    "state",
    "x",
    "y",
    "fine_x",
    "fine_y",
    "speed",
    "height",
    "path_index",
    "path_length",
)
T, STATE, X, Y, FX, FY, SPEED, HEIGHT, P_INDEX, P_LEN = range(len(FIELDS))
NO_WALK_TICKS = 200  # no walking state this long after the order: the order did not work
ARRIVED_IDLE = 20  # standing this long at the end point: arrived


def row(w, a):
    e = w.einheiten.get(a) or {}
    return [
        w.tick,
        e.get("zustand"),
        e.get("x"),
        e.get("y"),
        e.get("feinx"),
        e.get("feiny"),
        e.get("tempo"),
        e.get("gelaendehoehe"),
        e.get("wegindex"),
        e.get("weglaenge"),
    ]


def summarize(rows, goal, reason=None, terrain=None):
    """rows in FIELDS order, the first one the tick of the order -> the walk of the trial. terrain: {(x, y): (class, height)}
    from the survey (gelaende_erheben) - then every field's ticks also go to its terrain class and to the height step to the
    next field ("per_class", "per_step"); the first field change is left out (the unit starts somewhere inside its field)."""
    t0 = rows[0][T]
    start = (rows[0][X], rows[0][Y])
    walk = next((r[T] for r in rows if r[STATE] == WALKING), None)
    changes = [
        r
        for a, r in zip(rows, rows[1:], strict=False)
        if (r[X], r[Y]) != (a[X], a[Y]) and r[X] is not None
    ]
    per_field = [b[T] - a[T] for a, b in zip(changes, changes[1:], strict=False)]
    arrival = next((r[T] for r in rows if (r[X], r[Y]) == goal), None)
    speeds = collections.Counter(r[SPEED] for r in rows if r[STATE] == WALKING)
    common = speeds.most_common(1)[0][0] if speeds else None
    out = {
        "order_to_walk": None if walk is None else walk - t0,
        "arrival": None if arrival is None else arrival - t0,
        "fields": max(abs(goal[0] - start[0]), abs(goal[1] - start[1]))
        if None not in start
        else None,
        "ticks_per_field": statistics.median(per_field) if per_field else None,
        "per_field": per_field,
        "speed_values": {str(k): v for k, v in sorted(speeds.items(), key=lambda kv: str(kv[0]))},
        "formula": None if common is None else 8 * (common + 1),
        "heights": sorted({r[HEIGHT] for r in rows if r[HEIGHT] is not None}),
        "field_ticks": [[r[T] - t0, r[X], r[Y]] for r in changes],
        "end": reason,
    }
    if terrain is not None:
        per_class, per_step, speed_class = (
            collections.defaultdict(list),
            collections.defaultdict(list),
            collections.defaultdict(collections.Counter),
        )
        for a, b in zip(changes, changes[1:], strict=False):
            here, nxt = terrain.get((a[X], a[Y])), terrain.get((b[X], b[Y]))
            if here is None:
                continue
            per_class[here[0]].append(b[T] - a[T])
            if nxt is not None:
                per_step[nxt[1] - here[1]].append(b[T] - a[T])
        for r in rows:
            here = terrain.get((r[X], r[Y]))
            if here is not None and r[STATE] == WALKING:
                speed_class[here[0]][r[SPEED]] += 1
        out["per_class"] = dict(per_class)
        out["per_step"] = {str(k): v for k, v in sorted(per_step.items())}
        out["speed_per_class"] = {
            c: {str(k): n for k, n in v.items()} for c, v in speed_class.items()
        }
    return out


CLEAN = 30  # a LogicLayer value on fewer walkable fields of a map is "rare" - mixed values, up to 585 fields a map (23:55)


def terrain_of(path, by="speed"):
    """The survey dump (gelaende_erheben) -> {(x, y): (class name, height, path links)} of the walkable fields of the main area
    (PathConnectionLayer, the area with the most fields). by="speed": the two speed
    bits of the code (Wissensregister P11); by="value": the whole LogicLayer value, values on fewer than CLEAN fields "rare"."""
    from selfaware.tools.experiments.gelaende_erheben import in_diamond, read_dump, speed_class

    x0, y0, rows = read_dump(path)
    count = (
        collections.Counter(c[3] for row in rows for c in row if c[0]) if by == "value" else None
    )
    out = {}
    areas = collections.Counter(
        c[2]
        for j, row in enumerate(rows)
        for i, c in enumerate(row)
        if c[0] and in_diamond(x0 + i, y0 + j)
    )
    main = areas.most_common(1)[0][0] if areas else None
    for j, row in enumerate(rows):
        for i, (link, _g, area, logic, height, _t) in enumerate(row):
            if (
                not link or area != main or not in_diamond(x0 + i, y0 + j)
            ):  # only the map's own fields of the main area
                continue
            if by == "value":
                name = ("%#x" % logic) if count[logic] >= CLEAN else "rare"
            else:
                name = "+".join("%#x" % b for b in speed_class(logic)) or "none"
            out[(x0 + i, y0 + j)] = (name, height, link)
    return out


EAST = 4  # PathLinkageLayer bit: the step to x+1 is allowed (services/wegkarte.py)


def _walkable_east(cells):
    """Every field but the last allows the step east - else the game walks around or not at all (the slope line (323,54) of
    Paradise Plains: no walk, 2026-11-13 00:00)."""
    return all(len(c) < 3 or c[2] & EAST for c in cells[:-1])


def reanalyse(jsonl, dump, by="value"):
    """Trials of a line run again against another terrain classification (the rows are stored) -> {class: [ticks per field]}
    over all trials, per unit type."""
    terrain = terrain_of(dump, by)
    per_type = collections.defaultdict(lambda: collections.defaultdict(list))
    steps = collections.defaultdict(lambda: collections.defaultdict(list))
    with open(jsonl, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if not r.get("rows"):
                continue
            s = summarize(r["rows"], tuple(r["goal"]), None, terrain)
            for c, v in s["per_class"].items():
                per_type[r["unit"]][c] += v
            for k, v in s["per_step"].items():
                steps[r["unit"]][int(k)] += v
    return per_type, steps


def best_lines(terrain, cls, length=20, n=3, keep_away=()):
    """East-west lines of `length` walkable fields with the most fields of terrain class `cls` (at least 3), each line far from
    the others and at least 40 fields from every point in keep_away (castles: their towers shoot). -> [(count, start, goal)]"""
    xs = [p[0] for p in terrain]
    ys = [p[1] for p in terrain]
    found = []
    for y in range(min(ys), max(ys) + 1):
        for x in range(min(xs), max(xs) - length + 2):
            cells = [terrain.get((x + i, y)) for i in range(length)]
            if None in cells or not _walkable_east(cells):
                continue
            count = sum(1 for c in cells if c[0] == cls)
            if count >= 3:
                found.append((count, (x, y), (x + length - 1, y)))
    found.sort(key=lambda f: -f[0])
    out = []
    for f in found:
        if all(
            max(abs(f[1][0] - g[1][0]), abs(f[1][1] - g[1][1])) > 2 * length for g in out
        ) and all(max(abs(f[1][0] - k[0]), abs(f[1][1] - k[1])) > 40 for k in keep_away):
            out.append(f)
        if len(out) >= n:
            break
    return out


def line_trial(le, typ, start, goal, ticks, terrain):
    """On a real map (a paused skirmish): place an own unit at start, walk it to goal, then remove all own units of this type
    (toeteAlle with typen - our lord stays)."""
    a = S.place_unit(
        1, typ, start[0] - 1, start[1] - 1
    )  # the game puts a placed unit one field further (x/y +1)
    out = {"unit": typ, "start": list(start), "goal": list(goal), "nr": a, "fields": FIELDS}
    if a is None:
        out.update(result={"end": "not_placed"}, rows=[])
        return out
    time.sleep(0.3)
    S.send([{"angriff": {"einheiten": [a], "lauf": list(goal)}}], until="ANGRIFF")
    rows, reason = [row(S._world(le), a)], None
    last = rows[0][T]
    while reason is None:
        w = le.lesen()
        if w is None or w.tick == last:
            time.sleep(0.004)
            continue
        last = w.tick
        rows.append(row(w, a))
        reason = stop_reason(rows, goal, ticks)
    S.send([{"toeteAlle": {"spieler": 1, "ohneLord": True, "typen": [typ]}}], until="TOETE")
    out.update(result=summarize(rows, goal, reason, terrain), rows=rows)
    return out


def stop_reason(rows, goal, ticks):
    last, t0 = rows[-1], rows[0][T]
    if last[STATE] is None:
        return "unit_gone"
    if last[T] - t0 >= NO_WALK_TICKS and not any(r[STATE] == WALKING for r in rows):
        return "no_walk"
    if (
        (last[X], last[Y]) == goal
        and len(rows) > ARRIVED_IDLE
        and all(r[STATE] != WALKING and (r[X], r[Y]) == goal for r in rows[-ARRIVED_IDLE:])
    ):
        return "arrived"
    if last[T] - t0 >= ticks:
        return "time"
    return None


def free_line(buildings, start, goal, used):
    """A spot whose walk to the goal (same offset) passes no building within S.FREE fields."""
    dx, dy = goal
    for p in S.spots():
        if p in used:
            continue
        end = (p[0] + dx, p[1] + dy)
        steps = max(abs(dx), abs(dy))
        line = [(p[0] + dx * i // steps, p[1] + dy * i // steps) for i in range(steps + 1)]
        if any(
            max(abs(g["x"] - q[0]), abs(g["y"] - q[1])) <= S.FREE // 2
            for g in buildings.values()
            for q in line + [end]
        ):
            continue
        used.add(p)
        return p
    raise RuntimeError("no free walking line left - open a new map in the editor")


def trial(le, typ, offset, spot, ticks):
    S.clear()
    a = S.place_unit(1, typ, spot[0], spot[1])
    out = {"unit": typ, "offset": list(offset), "spot": list(spot), "nr": a, "fields": FIELDS}
    if a is None:
        out.update(result={"end": "not_placed"}, rows=[])
        return out
    time.sleep(0.3)
    e = S._world(le).einheiten.get(a) or {}
    start = (e.get("x"), e.get("y"))
    goal = (start[0] + offset[0], start[1] + offset[1])
    S.send([{"angriff": {"einheiten": [a], "lauf": list(goal)}}], until="ANGRIFF")
    rows, reason = [row(S._world(le), a)], None
    last = rows[0][T]
    while reason is None:
        w = le.lesen()
        if w is None or w.tick == last:
            time.sleep(0.004)
            continue
        last = w.tick
        rows.append(row(w, a))
        reason = stop_reason(rows, goal, ticks)
    out.update(goal=list(goal), result=summarize(rows, goal, reason), rows=rows)
    return out


def steepest_line(terrain, length=20, keep_away=()):
    """The east-west line of walkable fields with the largest height range, at least 40 fields from every point in keep_away."""
    best = None
    for x, y in terrain:
        cells = [terrain.get((x + i, y)) for i in range(length)]
        if (
            None in cells
            or not _walkable_east(cells)
            or any(max(abs(x - k[0]), abs(y - k[1])) <= 40 for k in keep_away)
        ):
            continue
        rng = max(c[1] for c in cells) - min(c[1] for c in cells)
        if best is None or rng > best[0]:
            best = (rng, (x, y), (x + length - 1, y))
    return best


def main_lines(arg):
    """Walking over the terrain classes of a real map (Daniel 23:04 "Erhebung machen und dann einfach jeweils testen"): a fresh
    skirmish on the map, then per class the best test line (best_lines) and the steepest line, each walked by every type."""
    import selfaware.game.kern_leitung as KL
    from selfaware.game.ucp.befehl import SPIEL
    from selfaware.tools.experiments.karten_holen import gefecht_frisch

    terrain = terrain_of(arg["gelaende"])
    gefecht_frisch(arg["karte"], ki=2)
    le = KL.Leitung(SPIEL)
    lords = [(e["x"], e["y"]) for e in S._world(le).einheiten.values() if e.get("typ") == 55]
    lines = []
    for cls in arg.get("klassen", "0x20000000,0x200000,none").split(","):
        found = best_lines(terrain, cls, 20, 1, keep_away=lords)
        if found:
            lines.append((cls,) + found[0])
        else:
            print("no test line for class %s" % cls, flush=True)
    steep = steepest_line(terrain, 20, keep_away=lords)
    if steep:
        lines.append(("slope",) + steep)
    print("lords", lords, "lines", lines, flush=True)
    S.send([{"pause": False}, {"tempo": int(arg.get("tempo", 40))}], wait=2.0)
    path = os.path.join(_workspace.DATA, "lauf_gelaende_%s.jsonl" % time.strftime("%Y%m%d_%H%M%S"))
    for cls, count, start, goal in lines:
        for typ in [int(x) for x in arg["typen"].split(",")]:
            r = line_trial(le, typ, start, goal, int(arg.get("ticks", 3000)), terrain)
            r["line"] = {"class": cls, "count": count}
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(r) + "\n")
            s = r["result"]
            med = {c: statistics.median(v) for c, v in (s.get("per_class") or {}).items() if v}
            print(
                "%s on %s line %s->%s: ticks per field by class %s, n %s, speed values by class %s, end %s"
                % (
                    type_name(typ),
                    cls,
                    start,
                    goal,
                    med,
                    {c: len(v) for c, v in (s.get("per_class") or {}).items()},
                    s.get("speed_per_class"),
                    s.get("end"),
                ),
                flush=True,
            )
    S.send([{"pause": True}], wait=1.0)
    print("file:", path)


def model_check(jsonl, dump):
    """Every arrived walk of a line run against services/laufmodell.py (the game's rule): for each of the 8 update phases the
    model's ticks from the first to the last field change against the measured ones, and the flat-ground model. -> rows
    (type, line class, measured, model min/max error, flat error)."""
    from selfaware.services import laufmodell as LM
    from selfaware.tools.experiments.gelaende_erheben import read_dump, read_macro_file

    x0, y0, rows = read_dump(dump)
    macro = read_macro_file(dump[:-4] + "_macro.txt")

    def tile(x, y):
        c = rows[y - y0][x - x0]
        return c[3], macro[y][x], c[4]

    out = []
    with open(jsonl, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            rw = r.get("rows") or []
            if not rw or r["result"].get("end") != "arrived" or r["unit"] not in LM.TYPES:
                continue
            fields, ticks = [(rw[0][X], rw[0][Y])], []
            for a, b in zip(rw, rw[1:], strict=False):
                if (b[X], b[Y]) != (a[X], a[Y]):
                    fields.append((b[X], b[Y]))
                    ticks.append(b[T])
            if len(ticks) < 2:
                continue
            blocked = blocked_fields(rw, r["unit"])
            measured = ticks[-1] - ticks[0]
            errs = []
            for phase in range(LM.UPDATE):
                sim = LM.walk(r["unit"], fields, tile, 0, phase)
                errs.append((sim[-1] - sim[0]) - measured)
            h0 = tile(*fields[0])[2]
            flat = LM.walk(r["unit"], fields, lambda x, y, h=h0: (0x8000, 1, h), 0, 0)
            out.append(
                (
                    r["unit"],
                    r.get("line", {}).get("class"),
                    measured,
                    min(errs),
                    max(errs),
                    (flat[-1] - flat[0]) - measured,
                    blocked,
                )
            )
    return out


def blocked_fields(rows, typ):
    """Fields on which the unit stayed more than twice as long as the game's own speed value allows (one move every speed + run +
    1 ticks, (run + 1) of 8 micro steps) plus one update (8 moves) - blocked or crowded, not terrain. -> [(x, y, ticks, allowed)]"""
    from selfaware.services import laufmodell as LM

    _base, run = LM.TYPES[typ]
    out, start, speeds = [], None, []
    for a, b in zip(rows, rows[1:], strict=False):
        if start is None:
            start = a[T]
        if a[SPEED] is not None:
            speeds.append(a[SPEED])
        if (b[X], b[Y]) != (a[X], a[Y]):
            v = max(speeds) if speeds else 1
            allowed = 2 * LM.STEPS * (v + run + 1) / (run + 1) + LM.UPDATE * (v + run + 1)
            if b[T] - start > allowed:
                out.append((a[X], a[Y], b[T] - start, round(allowed)))
            start, speeds = b[T], []
    return (
        out[1:]
        if out and out[0][2] and rows and (out[0][0], out[0][1]) == (rows[0][X], rows[0][Y])
        else out
    )


def main():
    import selfaware.game.kern_leitung as KL
    from selfaware.game.ucp.befehl import SPIEL

    if sys.argv[1:2] == ["modell"]:
        arg = dict(a.split("=", 1) for a in sys.argv[2:])
        for typ, cls, measured, lo, hi, flat, blocked in model_check(arg["lauf"], arg["gelaende"]):
            print(
                "%-22s %-11s measured %4d ticks | model %+4d .. %+4d (%+.0f %% .. %+.0f %%) | flat ground %+4d (%+.0f %%)%s"
                % (
                    type_name(typ),
                    cls,
                    measured,
                    lo,
                    hi,
                    100.0 * lo / measured,
                    100.0 * hi / measured,
                    flat,
                    100.0 * flat / measured,
                    " | BLOCKED %s" % blocked if blocked else "",
                )
            )
        return
    if sys.argv[1:2] == ["linie"]:
        S.exclusive()
        return main_lines(dict(a.split("=", 1) for a in sys.argv[2:]))
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    S.exclusive()
    n = int(arg.get("felder", 24))
    offset = (n, 0) if arg.get("richtung", "gerade") == "gerade" else (n, n)
    le = KL.Leitung(SPIEL)
    if "tempo" in arg:
        S.send([{"tempo": int(arg["tempo"])}], wait=2.0)
    used = set()
    path = os.path.join(_workspace.DATA, "lauf_messung_%s.jsonl" % time.strftime("%Y%m%d_%H%M%S"))
    for typ in [int(x) for x in arg["typen"].split(",")]:
        r = trial(
            le,
            typ,
            offset,
            free_line(S._world(le).gebaeude, None, offset, used),
            int(arg.get("ticks", 3000)),
        )
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(r) + "\n")
        s = r["result"]
        print(
            "%s %s: %s"
            % (
                type_name(typ),
                offset,
                json.dumps({k: v for k, v in s.items() if k not in ("field_ticks", "per_field")}),
            ),
            flush=True,
        )
    print("file:", path)


if __name__ == "__main__":
    main()
