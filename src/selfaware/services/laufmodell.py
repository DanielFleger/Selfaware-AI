# -*- coding: utf-8 -*-
"""Walking time per unit type and terrain, the game's own rule (B-182 link 2, docs/plans/Plan_Unit_Status_Log.md section 8;
Daniel 2026-11-12 23:00: "du kennst natuerlich die Laufgeschwindigkeit je Einheit je Terrain, das brauchst du auch spaeter damit
du den naechsten Schritt berechnen kannst").

Rule (calculateUnitMovementSpeed 0x0052F7E0, decompiled 2026-11-13 00:10 from the OpenSHC reference): every 8th move of a unit
(the code counts its own calls; measured 00:40 on a slope) the game sets the speed value of the unit from the tile under it:
  - water = LogicLayer 0x20000000 unless the MacroLayer (& 0x3f) of the tile is 1, or LogicLayer 0x40000000;
  - in water the wetness grows by 4 (at most 24): +3 while it is at most 4, +4 up to 9, +6 from 10 on;
  - out of the water the wetness drops by 8 per update, +3 as long as it was not 0 yet;
  - not in water: LogicLayer 0x200000 +2 (and the wetness grows by 4, at most 16 - it then counts as above when water comes);
  - climbing (unless LogicLayer 0x800000), against the unit's climb height that follows the tile height in steps: up 2-3 +1,
    4-7 +3, 8-11 +4, 12-16 +5; more than 16 or down: no surcharge.
Moving (Wissensregister L190, measured 25.10.): one move every (speed value + run + 1) ticks, (run + 1) micro steps per move,
8 micro steps per field, diagonal like straight. movement speed and run per type: measured 2026-11-12 23:43 on flat ground in the
editor (data/research/lauf_messung_20261112_234314.jsonl / _234635.jsonl): 12 ticks per field = (1, 1), mounted 10.6 (field ticks
8, 12, 12) = (1, 2), 16 = (1, 0), 24 = (2, 0), 32 = (3, 0). Not in the model: moveDelay (crowding, setMoveDelayForUnitsOnSameTiles), troops walking with their slowest member.
"""

# type -> (movement speed value on flat ground, run) - measured ticks per field 12 / 16 / 24 / 32
TYPES = {24: (1, 1), 26: (1, 1), 71: (1, 1), 22: (1, 1), 70: (1, 1), 72: (1, 1),
         28: (1, 2), 74: (1, 2),     # mounted: field ticks 8, 12, 12 - 10.6 a field (the median 12 hid it, 00:50)
         73: (1, 0),
         75: (2, 0), 25: (2, 0), 37: (2, 0), 76: (2, 0), 23: (2, 0),
         27: (3, 0)}
UPDATE = 8           # moves between two speed updates of a unit (every 4 on building tiles - not modelled)
STEPS = 8            # micro steps per field


def gerade(a, b):
    """Fields from a to b, diagonal first (Schach steps) - the line the walk model and the walk check use."""
    x, y = a
    out = [(x, y)]
    while (x, y) != tuple(b):
        x += (b[0] > x) - (b[0] < x)
        y += (b[1] > y) - (b[1] < y)
        out.append((x, y))
    return out


def flat_ticks_per_field(typ):
    """Mean ticks per field on flat ground: 8 micro steps, (run + 1) per move, one move every (speed + run + 1) ticks."""
    v, run = TYPES[typ]
    return STEPS * (v + run + 1) / (run + 1)


class Unit:
    """The speed state of one walking unit (wetness, climb height) as the game keeps it."""

    def __init__(self, typ, height=0):
        self.base, self.run = TYPES[typ]
        self.wet = 0
        self.climb = height
        self.speed = self.base

    def update(self, logic, macro, height):
        """One speed update on a tile (logic: LogicLayer, macro: MacroLayer & 0x3f, height: HeightLayer)."""
        water = bool((logic & 0x20000000 and macro != 1) or logic & 0x40000000)
        s = self.base
        if not logic & 0x800000:
            if self.climb < height:
                d = height - self.climb
                if d <= 16:
                    if d < 2:
                        self.climb += 1
                    elif d < 4:
                        self.climb += 2
                        s = self.base + 1
                    elif d < 8:
                        self.climb += 3
                        s = self.base + 3
                    elif d < 12:
                        self.climb += 4
                        s = self.base + 4
                    else:
                        self.climb += 4
                        s = self.base + 5
                else:
                    self.climb = height
            elif height < self.climb:
                d = self.climb - height
                if d > 16:
                    self.climb = height
                elif d >= 12:
                    self.climb -= 4
                elif d >= 8:
                    self.climb -= 3
                elif d > 3:
                    self.climb -= 2
                else:
                    self.climb -= 1
                    s = self.speed       # down 1-3: the code does not reset the speed value here (0052f9a3)
        if not water:
            if logic & 0x200000:
                if self.wet < 16:
                    self.wet += 4
                s += 2
            elif self.wet:
                self.wet = max(0, self.wet - 8)
                s += 3
        else:
            if self.wet < 24:
                self.wet += 4
            s += 3 if self.wet <= 4 else (4 if self.wet < 10 else 6)
        self.speed = s
        return s


class Walker:
    """The walk of walk(), field after field: add() appends the next fields of the way and goes on from where the unit was - with
    its wetness, climb height and move count (the chain audit follows a unit round by round and over a new order in the middle of
    its way; game 14 of 14.11.2026, S138: a walk begun anew at the new order started dry right after a ford)."""

    def __init__(self, typ, start, tile, start_tick=0, phase=0):
        self.tile = tile
        self.unit = Unit(typ, tile(*start)[2])
        self.unit.update(*tile(*start))
        self.fields = [tuple(start)]
        self.t, self.micro, self.i, self.moves = start_tick, STEPS // 2, 0, phase
        self.times = []          # tick at which each next field is reached

    def add(self, fields):
        self.fields += [tuple(f) for f in fields]
        u = self.unit
        while self.i < len(self.fields) - 1:
            self.t += u.speed + u.run + 1
            self.moves += 1
            if self.moves % UPDATE == 0:
                u.update(*self.tile(*self.fields[self.i]))
            self.micro += u.run + 1
            while self.micro >= STEPS and self.i < len(self.fields) - 1:
                self.micro -= STEPS
                self.i += 1
                self.times.append(self.t)
        return self.times


def walk(typ, fields, tile, start_tick=0, phase=0):
    """Simulate a walk over `fields` (list of (x, y), the first is the start field) -> ticks at which each next field is
    reached. tile(x, y) -> (logic, macro, height). The speed update comes every UPDATE-th MOVE of the unit, not every UPDATE-th
    tick (the code counts its own calls, field +0x440; measured on the slope of Paradise Plains 2026-11-13 00:40: 24 ticks between
    two changes at speed value 2, 40 at 4, 48 at 5 - one move every speed + 1 ticks for the assassin). phase: the unit's place in
    that count at the start (the count runs over the unit's whole life and is not read from the game - unknown, 0 to 7)."""
    return list(Walker(typ, fields[0], tile, start_tick, phase).add(fields[1:]))
