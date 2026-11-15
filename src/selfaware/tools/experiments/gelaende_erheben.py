# -*- coding: utf-8 -*-
"""Terrain survey of the Team-Liga maps (B-182 link 2, docs/plans/Plan_Unit_Status_Log.md section 8; Daniel 2026-11-12 23:04:
"Terrain kannst du eigentlich auch so messen - Erhebung machen und dann einfach jeweils testen").

Per map: a fresh skirmish on instance 2 (karten_holen.gefecht_frisch, paused when both lords stand), then the module command
wegkarte for the whole map - per field path links, building, area, LogicLayer, height, building type - copied to
data/research/gelaende_<short>.txt, and a summary data/research/gelaende_<short>.json: per LogicLayer bit the number of walkable
fields (path links != 0) that carry it, the height steps between walkable neighbours, and per speed class (the two LogicLayer
bits below) the longest straight east-west runs of walkable fields - the test lines for the walking trials.

The rule of the game (calculateUnitMovementSpeed 0x0052F7E0, decompiled 2026-11-13 00:10 from the OpenSHC reference, Ghidra
headless Dekompilieren.java; recomputed every 8 ticks per unit, every 4 on special tiles): water = LogicLayer 0x20000000 unless the
MacroLayer (0x01DCFCB8, 2 bytes a tile, & 0x3f) says 1 there, or LogicLayer 0x40000000; in water the unit's wetness
(negativeHeight) grows by 4 per update (at most 24): speed value +3, then +4 (wetness 5-9), then +6 (10 and more); out of the water
the wetness drops by 8 per update and the +3 stays until it is 0; not in water, LogicLayer 0x200000 gives +2; climbing (unless
LogicLayer 0x800000): height step up 2-3 +1, 4-7 +3, 8-11 +4, 12-16 +5, more than 16 or down: none. The MacroLayer is read
here with peek, row by row, into data/research/gelaende_<short>_macro.txt.

Call (PYTHONPATH=src, SHC_INSTANZ=2):  python -m selfaware.tools.experiments.gelaende_erheben "Liga_Paradise Plains" [...]
       python -m selfaware.tools.experiments.gelaende_erheben auswerten data/research/gelaende_PP.txt     (only the summary)
"""
import collections
import io
import json
import os
import shutil
import sys

from selfaware import workspace as _workspace

SPEED_BITS = (0x200000, 0x20000000)
RUN_MIN = 8          # fields: a test line is at least this long


def read_dump(path):
    """wegkarte.txt -> (x0, y0, rows); rows[y - y0][x - x0] = (link, building, area, logic, height, building type)."""
    with io.open(path, encoding="utf-8") as f:
        head = f.readline().split()
        kv = dict(p.split("=") for p in head if "=" in p)
        rows = []
        for line in f:
            row = []
            for cell in line.split():
                link, geb, area, logic, height, typ = cell.split(":")
                row.append((int(link, 16), int(geb), int(area), int(logic, 16), int(height), int(typ)))
            rows.append(row)
    return int(kv["x0"]), int(kv["y0"]), rows


def in_diamond(x, y, size=400):
    """Is (x, y) a field of the map? The game keeps the map as a diamond: row y holds the fields x_min .. x_min + width - 1
    (translationMatrix 0x023372F8, read 2026-11-13 00:35 on a 400 map: row 0 x 199-200, row 199 and 200 x 0-399, row 399 x
    199-200, 80,400 fields; data/research/kartenraute_400.json). Outside it the layers give the data of OTHER fields (the
    module's wegkarte reads tile = row start + x for every x) - those must not be counted."""
    h = size // 2
    if y < h:
        x_min, width = h - 1 - y, 2 * (y + 1)
    else:
        x_min, width = y - h, 2 * (size - y)
    return 0 <= y < size and x_min <= x < x_min + width


def speed_class(logic):
    return tuple(b for b in SPEED_BITS if logic & b)


def summarize(x0, y0, rows):
    bits, classes, steps, heights = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    walkable = 0
    runs = collections.defaultdict(list)          # speed class -> [(length, x, y, height min, height max)]
    for j, row in enumerate(rows):
        run = None
        for i, (link, _geb, _area, logic, height, _typ) in enumerate(row):
            ok = link != 0 and in_diamond(x0 + i, y0 + j)
            cls = speed_class(logic) if ok else None
            if ok:
                walkable += 1
                classes[cls] += 1
                heights[height] += 1
                for b in range(32):
                    if logic & (1 << b):
                        bits[1 << b] += 1
                if i + 1 < len(row) and row[i + 1][0] != 0 and in_diamond(x0 + i + 1, y0 + j):
                    steps[abs(row[i + 1][4] - height)] += 1
            if run is not None and (not ok or cls != run[0]):
                if run[2] >= RUN_MIN:
                    runs[run[0]].append((run[2], run[1], y0 + j, run[3], run[4]))
                run = None
            if ok:
                if run is None:
                    run = [cls, x0 + i, 0, height, height]
                run[2] += 1
                run[3], run[4] = min(run[3], height), max(run[4], height)
        if run is not None and run[2] >= RUN_MIN:
            runs[run[0]].append((run[2], run[1], y0 + j, run[3], run[4]))
    best = {}
    for cls, lst in runs.items():
        flat = sorted((r for r in lst if r[4] - r[3] <= 2), reverse=True)[:5]
        steep = sorted(lst, key=lambda r: (r[4] - r[3], r[0]), reverse=True)[:5]
        best["+".join("%#x" % b for b in cls) or "none"] = {"flat": flat, "steepest": steep, "runs": len(lst)}
    return {"walkable": walkable,
            "bits": {"%#x" % b: n for b, n in sorted(bits.items())},
            "speed_classes": {"+".join("%#x" % b for b in c) or "none": n for c, n in classes.most_common()},
            "height_steps": dict(sorted(steps.items())),
            "heights": {"min": min(heights) if heights else None, "max": max(heights) if heights else None},
            "test_lines": best}


MACRO_LAYER = 0x01DCFCB8      # TileMapState.MacroLayer, 2 bytes a tile (address from calculateUnitMovementSpeed, 0052f899)
TILE_ROWS = 0x023372F8        # translationMatrix: row y -> first tile index at +8 (as the module's wegkarte)


def read_macro(path, size=400):
    """MacroLayer & 0x3f of every field, one text line per row (values as hex), via peek."""
    from selfaware.game.ucp.laden import peek
    with io.open(path, "w", encoding="utf-8") as f:
        for y in range(size):
            base = peek(TILE_ROWS + y * 12 + 8)[0]
            a = MACRO_LAYER + base * 2
            start = a & ~3
            words = peek(start, size // 2 + 2)
            raw = b"".join(w.to_bytes(4, "little") for w in words)
            f.write(" ".join("%x" % (int.from_bytes(raw[a - start + 2 * i:a - start + 2 * i + 2], "little") & 0x3f)
                             for i in range(size)) + "\n")
    return path


def read_macro_file(path):
    with io.open(path, encoding="utf-8") as f:
        return [[int(v, 16) for v in line.split()] for line in f]


def tile_function(path):
    """tile(x, y) -> (LogicLayer, MacroLayer, height) of a survey (data/research/gelaende_<short>.txt and _macro.txt), as
    services/laufmodell.walk wants it; outside the survey flat ground (0x8000, 1, 8)."""
    x0, y0, rows = read_dump(path)
    macro = read_macro_file(path[:-4] + "_macro.txt")

    def tile(x, y):
        if not (0 <= y - y0 < len(rows) and 0 <= x - x0 < len(rows[0])):
            return 0x8000, 1, 8
        c = rows[y - y0][x - x0]
        return c[3], macro[y][x], c[4]
    return tile


def survey_file(karte):
    """The survey of a map ("Liga_Paradise Plains" -> data/research/gelaende_LigaParadisePlains.txt) or None."""
    path = os.path.join(_workspace.DATA, "gelaende_%s.txt" % "".join(ch for ch in str(karte) if ch.isalnum()))
    return path if os.path.exists(path) and os.path.exists(path[:-4] + "_macro.txt") else None


def survey(karte, short):
    from selfaware.game.ucp.befehl import ABZUG
    from selfaware.game.ucp.laden import befehl
    from selfaware.tools.experiments.karten_holen import gefecht_frisch
    gefecht_frisch(karte, ki=2)
    befehl({"wegkarte": {"x0": 0, "y0": 0, "x1": 399, "y1": 399}}, 90.0, bis="WEGKARTE")
    dst = os.path.join(_workspace.DATA, "gelaende_%s.txt" % short)
    shutil.copy(os.path.join(ABZUG, "wegkarte.txt"), dst)
    read_macro(os.path.join(_workspace.DATA, "gelaende_%s_macro.txt" % short))
    return dst


def water(logic, macro):
    """The game's own water test (calculateUnitMovementSpeed)."""
    return bool((logic & 0x20000000 and macro != 1) or logic & 0x40000000)


def main():
    from selfaware.tools.experiments.karten_holen import kurz_von
    from selfaware.tools.experiments.schlag_messen import exclusive
    args = sys.argv[1:]
    if args and args[0] == "auswerten":
        paths = args[1:]
    else:
        exclusive()
        paths = [survey(k, kurz_von(k)) for k in args]
    for p in paths:
        s = summarize(*read_dump(p))
        out = os.path.splitext(p)[0] + ".json"
        with io.open(out, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=1)
        print("%s: walkable %d, speed classes %s, height steps %s -> %s" % (
            os.path.basename(p), s["walkable"], s["speed_classes"], s["height_steps"], out), flush=True)


if __name__ == "__main__":
    main()
