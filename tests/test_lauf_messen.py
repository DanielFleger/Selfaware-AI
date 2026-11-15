"""B-182 link 2 walking measurement (tools/experiments/lauf_messen.py), the analysis without the game."""

from selfaware.tools.experiments import lauf_messen as M


def _rows(spec):
    """spec: [(tick, state, x, y, speed)] -> rows in M.FIELDS order."""
    return [[t, z, x, y, x * 8 + 4, y * 8 + 4, v, 0, 0, 0] for t, z, x, y, v in spec]


def test_ticks_per_field_and_the_formula_of_the_game():
    """One field every 16 ticks at speed value 1 - the code says 8 x (speed value + 1) (Wissensregister P13)."""
    spec = [
        (0, 1, 100, 100, 1),
        (2, 101, 100, 100, 1),
        (10, 101, 101, 100, 1),
        (26, 101, 102, 100, 1),
        (42, 101, 103, 100, 1),
        (58, 1, 104, 100, 1),
    ]
    s = M.summarize(_rows(spec), (104, 100))
    assert s["order_to_walk"] == 2 and s["arrival"] == 58 and s["fields"] == 4
    assert s["per_field"] == [16, 16, 16] and s["ticks_per_field"] == 16 and s["formula"] == 16
    assert s["field_ticks"] == [[10, 101, 100], [26, 102, 100], [42, 103, 100], [58, 104, 100]]


def test_the_walk_stops_when_it_arrived_or_never_started():
    goal = (104, 100)
    r = _rows([(0, 1, 100, 100, 1)] + [(t, 1, 100, 100, 1) for t in range(1, M.NO_WALK_TICKS + 1)])
    assert M.stop_reason(r, goal, 3000) == "no_walk"
    r = _rows(
        [(0, 1, 100, 100, 1), (1, 101, 101, 100, 1)]
        + [(t, 1, 104, 100, 1) for t in range(2, 2 + M.ARRIVED_IDLE)]
    )
    assert M.stop_reason(r, goal, 3000) == "arrived"
    r[-1][M.STATE] = 101  # still walking on the goal field: not yet
    assert M.stop_reason(r, goal, 3000) is None
    r[-1][M.STATE] = None
    assert M.stop_reason(r, goal, 3000) == "unit_gone"


def test_a_walking_line_keeps_away_from_buildings():
    used = set()
    first = M.free_line({}, None, (24, 0), used)
    nxt = next(p for p in M.S.spots() if p not in used)
    in_the_way = {1: {"x": nxt[0] + 12, "y": nxt[1]}}  # a building in the middle of the next line
    second = M.free_line(in_the_way, None, (24, 0), used)
    assert second not in (first, nxt)


def test_every_field_goes_to_its_terrain_class_and_height_step():
    """A walk over plain ground, then two fields with the speed bit 0x20000000, then up a step of 4."""
    spec = [
        (0, 1, 100, 100, 1),
        (1, 101, 100, 100, 1),
        (8, 101, 101, 100, 1),
        (20, 101, 102, 100, 1),
        (40, 101, 103, 100, 3),
        (60, 101, 104, 100, 3),
        (76, 101, 105, 100, 1),
        (90, 1, 106, 100, 1),
    ]
    terrain = {
        (100, 100): ("none", 8),
        (101, 100): ("none", 8),
        (102, 100): ("none", 8),
        (103, 100): ("0x20000000", 8),
        (104, 100): ("0x20000000", 8),
        (105, 100): ("none", 12),
        (106, 100): ("none", 12),
    }
    s = M.summarize(_rows(spec), (106, 100), "arrived", terrain)
    assert s["per_class"] == {
        "none": [12, 20, 14],
        "0x20000000": [20, 16],
    }  # the first change (start inside the field) is left out
    assert s["per_step"] == {"0": [12, 20, 20, 14], "4": [16]}
    assert s["speed_per_class"]["0x20000000"] == {"3": 2}


def test_the_best_line_has_the_most_fields_of_the_class_and_keeps_away_from_castles():
    terrain = {(x, 10): ("none", 8) for x in range(0, 60)}
    terrain.update({(x, 10): ("0x200000", 8) for x in (30, 31, 32, 33)})
    terrain.update({(x, 60): ("none", 8) for x in range(0, 60)})
    terrain.update({(x, 60): ("0x200000", 8) for x in (5, 6, 7)})
    best = M.best_lines(terrain, "0x200000", length=20, n=2)
    assert best[0][0] == 4 and best[0][1][1] == 10 and best[1][1][1] == 60
    away = M.best_lines(terrain, "0x200000", length=20, n=2, keep_away=[(30, 12)])
    assert away and all(b[1][1] == 60 for b in away)
