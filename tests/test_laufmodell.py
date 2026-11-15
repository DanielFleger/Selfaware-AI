"""B-182 link 2: the game's walking rule (services/laufmodell.py, calculateUnitMovementSpeed 0x0052F7E0) against hand-made
tiles and the measured flat-ground walks (2026-11-12 23:43)."""

from selfaware.services import laufmodell as LM

PLAIN, WATER_BIT, MUD = 0x8000, 0x20008000, 0x208000


def test_flat_ground_gives_the_measured_ticks_per_field():
    """Measured 23:43 in the editor: ticks from the first to the last field change over 23 fields (lauf_messung_..234314)."""
    measured = {73: 368, 24: 276, 26: 276, 71: 276, 22: 276, 70: 276, 72: 276, 28: 244, 74: 244, 75: 552, 25: 552, 37: 552,
                76: 552, 23: 552, 27: 736}
    for typ, span in measured.items():
        sim = LM.walk(typ, [(x, 0) for x in range(25)], lambda x, y: (PLAIN, 1, 8))
        assert abs((sim[-1] - sim[0]) - span) <= 4, (typ, sim[-1] - sim[0], span)
        assert abs(LM.flat_ticks_per_field(typ) * 23 - span) <= 4


def test_water_builds_up_and_lingers():
    u = LM.Unit(73, 8)
    assert [u.update(WATER_BIT, 4, 8) for _ in range(4)] == [4, 5, 7, 7]      # +3, +4, +6, +6
    assert [u.update(PLAIN, 1, 8) for _ in range(4)] == [4, 4, 1, 1]          # wet 16 -> 8 -> 0: +3 twice, then plain


def test_macro_layer_1_cancels_the_water_bit_and_mud_gives_two():
    u = LM.Unit(24, 8)
    assert [u.update(WATER_BIT, 1, 8) for _ in range(3)] == [1, 1, 1]
    assert u.update(MUD, 1, 8) == 3
    assert u.update(0x40008000, 1, 8) == 1 + 3 + 1    # 0x40000000 is water whatever the MacroLayer says; wet 4 -> 8: +4


def test_climbing_up_costs_and_down_does_not():
    u = LM.Unit(73, 8)
    assert u.update(PLAIN, 1, 14) == 1 + 3     # 6 up: +3, climb height 8 -> 11
    assert u.update(PLAIN, 1, 14) == 1 + 1     # 3 up: +1, -> 13
    assert u.update(PLAIN, 1, 14) == 1         # 1 up: none, -> 14
    assert u.update(PLAIN, 1, 4) == 1          # 10 down: none


def test_a_walk_through_water_is_slower_than_on_flat_ground():
    fields = [(x, 0) for x in range(21)]
    dry = LM.walk(73, fields, lambda x, y: (PLAIN, 1, 8))
    wet = LM.walk(73, fields, lambda x, y: (WATER_BIT, 4, 8) if 5 <= x <= 14 else (PLAIN, 1, 8))
    assert (wet[-1] - wet[0]) > 1.5 * (dry[-1] - dry[0])


def test_the_speed_value_changes_every_eighth_move_not_every_eighth_tick():
    """Measured 00:40 on the slope of Paradise Plains: 24 ticks between two changes at speed value 2, 40 at 4, 48 at 5 - eight
    moves of the assassin (one every speed + 1 ticks). By hand for deep water from the start (wet 4 -> v 4, 8 -> 5, 12 -> 7):
    the first field change after 4 moves of 5 ticks (20), then 4 x 5 + 4 x 6 (64), 4 x 6 + 4 x 8 (120), 8 x 8 (184)."""
    assert LM.walk(73, [(x, 0) for x in range(8)], lambda x, y: (WATER_BIT, 4, 8))[:4] == [20, 64, 120, 184]
