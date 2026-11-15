"""B-182 link 2 offline: walking sections of real games against the game's rule (tools/analysis/lauf_stoerungen.py)."""

from selfaware.tools.analysis import lauf_stoerungen as L


def _u(nr, owner, typ, x, y, state=101, goal=(0, 0)):
    return {"nr": nr, "besitzer": owner, "typ": typ, "x": x, "y": y, "zustand": state, "laufx": goal[0], "laufy": goal[1]}


def test_sections_on_time_slow_and_disrupted_with_the_units_at_the_stop():
    flat = lambda x, y: (0x8000, 1, 8)  # noqa: E731
    # assassin: 16 ticks a field on flat ground -> 92 ticks give 5 fields (first change after 8)
    r1 = (1000, {5: _u(5, 1, 73, 100, 100, goal=(150, 100)), 6: _u(6, 1, 73, 100, 120, goal=(150, 120)),
                 7: _u(7, 1, 73, 100, 140, goal=(150, 140))})
    r2 = (1092, {5: _u(5, 1, 73, 105, 100), 6: _u(6, 1, 73, 103, 120), 7: _u(7, 1, 73, 101, 140),
                 8: _u(8, 2, 24, 102, 140), 9: _u(9, 1, 7, 101, 141)})
    s = L.sections([r1, r2], flat)
    v = {round(e): (w, verdict) for _t, e, w, verdict, _n in s}
    assert [x[3] for x in s] == ["on_time", "slow", "disrupted"]
    assert s[2][4] == {"enemy_fighters": 1, "own_workers": 1}
    assert v


def test_standing_units_and_short_gaps_are_left_out():
    flat = lambda x, y: (0x8000, 1, 8)  # noqa: E731
    r1 = (1000, {5: _u(5, 1, 73, 100, 100, state=1, goal=(150, 100)), 6: _u(6, 1, 73, 100, 120, goal=(102, 120))})
    r2 = (1092, {5: _u(5, 1, 73, 100, 100), 6: _u(6, 1, 73, 100, 120)})
    assert L.sections([r1, r2], flat) == []      # 5 stands, 6 has only 2 fields to go (expected under MIN_EXPECTED)
    r2b = (1400, {5: _u(5, 1, 73, 100, 100), 6: _u(6, 1, 73, 100, 120)})
    assert L.sections([r1, r2b], flat) == []     # gap over MAX_GAP
