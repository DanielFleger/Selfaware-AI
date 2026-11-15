"""B-182 attack chain measurement (tools/experiments/schlag_messen.py), the analysis without the game. The numbers in
chain_audit.ATTACK_TIMING come from summarize(), so it is checked against hand-made series."""

from selfaware.tools.experiments import schlag_messen as S


def _rows(spec):
    """spec: [(tick, state, frame, target_life, target_fire)] -> rows in S.FIELDS order."""
    return [[t, z, 0, b, 0, 100, 100, 1000, life, fire, 0] for t, z, b, life, fire in spec]


def test_a_clean_swing_series():
    """Shape of the assassin against the woodcutter hut (measured 2026-11-12 23:07): attack state 2 ticks after the order, the
    frames 1..24 run, the hit at the wrap 24 -> 0; here two swings of 93 ticks."""
    spec = [
        (100, 1, 0, 500, 0),
        (101, 101, 3, 500, 0),
        (102, 107, 1, 500, 0),
        (150, 107, 12, 500, 0),
        (194, 107, 24, 500, 0),
        (195, 107, 0, 425, 0),
        (240, 107, 12, 425, 0),
        (287, 107, 24, 425, 0),
        (288, 107, 0, 350, 0),
    ]
    s = S.summarize(_rows(spec), "hits")
    assert (
        s["order_to_attack"] == 2
        and s["first_hit"] == 93
        and s["between_hits"] == [93]
        and s["damage"] == [75, 75]
    )
    assert s["first_swing_frames"] == [[0, 1], [48, 12], [92, 24], [93, 0]]
    assert (
        s["states"] == [[0, 1], [1, 101], [2, 107]]
        and s["fire_losses"] == []
        and s["end"] == "hits"
    )
    assert s["skipped_ticks"] == 180  # sparse rows here: 188 ticks, 9 rows


def test_fire_losses_are_no_swings():
    """The slave (measured 23:07): first life loss 477 ticks after the attack state, then 4 every 20 ticks - the hut burns."""
    spec = [
        (0, 1, 0, 60, 0),
        (2, 107, 1, 60, 0),
        (470, 107, 5, 60, 1),
        (479, 107, 6, 56, 1),
        (499, 107, 7, 52, 1),
    ]
    s = S.summarize(_rows(spec))
    assert (
        s["first_hit"] is None
        and s["damage"] == []
        and s["fire_losses"] == [[477, 4], [497, 4]]
        and s["fire_from"] == 468
    )


def test_the_trial_stops_for_the_right_reason():
    r = _rows([(0, 1, 0, 500, 0), (300, 1, 0, 500, 0)])
    assert S.stop_reason(r, 900, 5) == "no_attack"
    r = _rows([(0, 1, 0, 500, 0), (2, 107, 1, 500, 0), (602, 107, 3, 500, 0)])
    assert S.stop_reason(r, 900, 5) == "no_hit"
    r = _rows([(0, 1, 0, 500, 0), (2, 107, 1, 500, 0), (95, 107, 0, 425, 0)])
    assert S.stop_reason(r, 900, 1) == "hits" and S.stop_reason(r, 900, 2) is None
    r[-1][S.T_LIFE] = None
    assert S.stop_reason(r, 900, 5) == "target_gone"
    r[-1][S.LIFE] = None
    assert S.stop_reason(r, 900, 5) == "attacker_gone"


def test_every_trial_gets_a_spot_without_a_building_near_it():
    used = set()
    first = S.free_spot({}, used)
    assert first == S.CENTRE and first in used
    second = S.free_spot({}, used)
    assert second != first
    nxt = next(p for p in S.spots() if p not in used)
    burning = {
        1: {"x": nxt[0] + 3, "y": nxt[1] - 1}
    }  # an old hut of an earlier run on the next spot
    third = S.free_spot(burning, used)
    assert third not in (first, second, nxt)
    assert all(
        max(abs(g["x"] - third[0]), abs(g["y"] - third[1])) > S.FREE for g in burning.values()
    )


def test_a_shooter_starts_with_its_aim_state_and_losses_without_an_attack_state_count_from_the_order():
    """Archers against a hut (measured 2026-11-12 23:22): states 0 -> 4 (aim) -> 5 (shot) -> 6 (reload) -> 0, no state 107."""
    spec = [
        (0, 8, 0, 200, 0),
        (1, 0, 0, 200, 0),
        (2, 4, 1, 200, 0),
        (57, 5, 9, 200, 0),
        (60, 6, 1, 190, 0),
        (130, 4, 1, 190, 0),
        (189, 6, 2, 180, 0),
    ]
    s = S.summarize(_rows(spec))
    assert (
        s["order_to_attack"] == 2
        and s["losses_from"] == "attack"
        and s["first_hit"] == 58
        and s["between_hits"] == [129]
    )
    spec = [(0, 8, 0, 200, 0), (60, 12, 1, 190, 0), (189, 12, 2, 180, 0)]
    s = S.summarize(_rows(spec))
    assert (
        s["order_to_attack"] is None
        and s["losses_from"] == "order"
        and s["first_hit"] == 60
        and s["between_hits"] == [129]
    )


def test_a_second_measurement_on_the_same_instance_is_refused(tmp_path):
    """2026-11-12 23:24: two runs at once killed each other's units (every trial starts with "kill all units")."""
    import os
    import subprocess
    import sys

    lock = str(tmp_path / "messung.lock")
    S.exclusive(lock)
    code = (
        "from selfaware.tools.experiments import schlag_messen as S\n"
        "S.exclusive(%r)\nprint('GOT THE LOCK')\n" % lock
    )
    env = dict(
        os.environ, PYTHONPATH=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
    )
    r = subprocess.run(
        [sys.executable, "-c", code], env=env, capture_output=True, text=True, timeout=60
    )
    assert "GOT THE LOCK" not in r.stdout and "another measurement runs" in (r.stdout + r.stderr)
    S._LOCK.pop().close()
    r = subprocess.run(
        [sys.executable, "-c", code], env=env, capture_output=True, text=True, timeout=60
    )
    assert "GOT THE LOCK" in r.stdout


def test_the_gap_after_a_second_identical_order():
    """23:31: the swordsman fought (a loss every tick), the second order made it walk 8 ticks without damage."""
    spec = (
        [(t, 106, 1, 1000 - 10 * t, 0) for t in range(0, 6)]
        + [(t, 101, 1, 950, 0) for t in range(6, 14)]
        + [(t, 101, 1, 950 - 10 * (t - 13), 0) for t in range(14, 18)]
    )
    s = S.summarize(_rows(spec), None, 5)
    assert s["resend_gap"] == {"to_next_loss": 9, "longest_before": 1}
