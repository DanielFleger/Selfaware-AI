"""B-182 chain audit per order (micro/chain_audit.py), without the game. Daniel 2026-11-12 22:34: "Wegberechnung -> Kern bekommt
Befehle -> Ausfuehrung -> Aktion im Spiel"."""

import os

from selfaware.micro.chain_audit import ChainAudit

QUELLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "selfaware")


def _e(owner, typ, x, y, **k):
    d = {"besitzer": owner, "typ": typ, "x": x, "y": y, "leben": 10000, "laufx": 0, "laufy": 0, "zieleinheit": 0, "nahziel": 0,
         "zielart": 0}
    d.update(k)
    return d


def test_a_walk_order_seen_and_arrived_gives_no_line():
    k = ChainAudit(1)
    k.tick = 100
    k.from_module({"befehle": [{"angriff": {"einheiten": [5], "lauf": [150, 100]}}]})
    assert k.check(120, {5: _e(1, 71, 100, 100, laufx=150, laufy=100)}, {}) == []
    assert k.check(400, {5: _e(1, 71, 149, 100)}, {}) == []
    assert "walk/module sent 1 taken 1 arrived 1" in k.summary() and 5 not in k.orders


def test_a_walk_order_not_seen_in_the_game_is_reported_once():
    k = ChainAudit(1)
    k.tick = 100
    k.from_module({"angriff": {"einheiten": [5], "lauf": [150, 100]}})
    L = {5: _e(1, 73, 100, 100, laufx=100, laufy=100)}
    assert k.check(200, L, {}) == []
    lines = k.check(260, L, {})
    assert len(lines) == 1 and "5 (A_ASSASSIN 73) walk (150,100) via module: NOT SEEN in the game state 160 ticks" in lines[0]
    assert k.check(400, L, {}) == []  # once per order


def test_seen_but_no_step_closer_is_no_progress():
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [5], "lauf": [200, 100]}})
    L = {5: _e(1, 70, 100, 100, laufx=200, laufy=100)}
    assert k.check(50, L, {}) == []  # seen: the game's walk target is the point
    assert k.check(200, L, {}) == []
    lines = k.check(351, L, {})
    assert len(lines) == 1 and "NO PROGRESS - seen at tick 50, no step closer for 301 ticks (100 fields left" in lines[0]


def test_a_digger_at_work_is_no_stop_even_away_from_its_tile():
    # game 20261113_220249: spearman 336 sent to dig (188,234) dug at (190..192,235) in state 124 for 500 ticks - the watch stopped
    # the game with NO PROGRESS (S124); standing still in another state is still reported
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [336, 337], "graben": [188, 234]}})
    dig = {336: _e(1, 24, 192, 235, zielart=6, zustand=124), 337: _e(1, 24, 192, 236, zielart=6, zustand=1)}
    assert k.check(1900, dig, {}) == []
    assert k.check(2100, dig, {}) == []
    lines = k.check(2250, dig, {})
    assert len(lines) == 1 and "337 (E_SPEAR 24) dig (188,234) via module: NO PROGRESS" in lines[0]
    assert "dig/module sent 2 taken 2" in k.summary() and "digging 1" in k.summary()


def test_a_digger_that_reached_the_moat_may_walk_on_to_the_next_tile():
    # game 20261113_220614: spearman 332 dug at (187..191, 233..236) from tick 1963, at 2743 it walked on to (193,237) - 5 fields
    # from the tile it was sent to; the watch stopped the game with NO PROGRESS
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [332], "graben": [188, 234]}})
    assert k.check(1900, {332: _e(1, 24, 187, 235, zielart=6, zustand=101)}, {}) == []
    assert k.check(2743, {332: _e(1, 24, 193, 234, zielart=6, zustand=101, laufx=193, laufy=237)}, {}) == []
    assert "arrived 1" in k.summary() and 332 not in k.orders


def test_a_ring_building_attack_shows_the_ring_result_and_the_old_tile():
    """Game 19 (12.11. 21:03): 25 building attacks of the assassins via the core ring, all "wirkt nicht"; assassin 475 stood 610
    ticks at (283, 92), the core still held the tile of its earlier target (267, 89)."""
    k = ChainAudit(1)
    k.from_ring(77, 475, 9, 239, 0, 32527)
    k.ring_result(77, "wirkt nicht")
    G = {239: {"besitzer": 2, "typ": 20, "x": 326, "y": 150, "leben": 350}}
    L = {475: _e(1, 73, 283, 92, laufx=283, laufy=92)}
    lines = k.check(32700, L, G, {475: {"mauerx": 267, "mauery": 89}})
    assert len(lines) == 1
    assert "475 (A_ASSASSIN 73) attack_building B239 via ring: NOT SEEN" in lines[0]
    assert "ring wirkt_nicht" in lines[0] and "core tile (267,89)" in lines[0] and "position (283,92)" in lines[0]
    assert "attack_building/ring sent 1 not_seen 1 ring_wirkt_nicht 1" in k.summary()


def test_an_attack_seen_through_the_core_shot_target_and_a_resend_keeps_the_clock():
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [7], "ziel": 40}})
    k.tick = 100
    k.from_module({"angriff": {"einheiten": [7], "ziel": 40}})  # the same order again: the clock is not reset
    assert k.orders[7].tick == 0
    L = {7: _e(1, 74, 100, 100), 40: _e(2, 3, 130, 100)}
    assert k.check(160, L, {}, {7: {"schusseinheit": 40}}) == [] and k.orders[7].taken == 160


def test_an_order_ends_with_its_target_and_when_the_number_is_given_out_again():
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [7], "ziel": 40}})
    k.check(10, {7: _e(1, 74, 100, 100), 40: _e(2, 3, 130, 100)}, {})
    assert k.check(400, {7: _e(1, 74, 100, 100)}, {}) == [] and 7 not in k.orders  # target dead: over
    k.from_module({"angriff": {"einheiten": [8], "lauf": [150, 100]}})
    k.check(500, {8: _e(1, 70, 100, 100)}, {})
    assert k.check(900, {8: _e(1, 52, 100, 100)}, {}) == [] and 8 not in k.orders  # the number belongs to another unit now


def test_kernweg_tells_the_audit_every_ring_order_and_its_result():
    from selfaware.execution import kernweg as KWG
    from selfaware.game import kern_leitung as KL

    class Leitung:
        def __init__(self):
            self.n, self.erg = 0, {}

        def takt(self):
            return 1000

        def auftrag(self, art, nr, a=0, b=0, vorrang=0, frist=0, auftraggeber=0):
            self.n += 1
            return self.n

        def lesbar(self, ring):
            return True

        def ergebnis(self, ring):
            return self.erg.get(ring, KL.ERG_ANGENOMMEN)

    le = Leitung()
    kw = KWG.Kernweg(le)
    k = ChainAudit(1)
    kw.beobachter = k
    kw.senden([{"angriff": {"einheiten": [475], "gebaeude": 239}}])
    o = k.orders[475]
    assert (o.kind, o.channel, o.target, o.tick) == ("attack_building", "ring", 239, 1000)
    le.erg[o.ring] = KL.ERG_WIRKT_NICHT
    kw.fortgang()
    assert o.ring_result == "wirkt_nicht"


def test_the_module_channel_shows_each_order_after_the_lord_lock_and_the_lenker_checks_each_round():
    with open(os.path.join(QUELLE, "game", "ucp", "befehl.py"), encoding="utf-8") as f:
        t = f.read()
    assert t.index("befehl, meld = lordschutz.filtern(befehl)") < t.index("for beobachter in BEOBACHTER:") < t.index(
        'io.open(BEFEHL, "wb").write')
    with open(os.path.join(QUELLE, "runtime", "live", "erstes_spiel.py"), encoding="utf-8") as f:
        s = f.read()
    assert "KETTE = ChainAudit(SP, tile=" in s and "kanal_kette.BEOBACHTER[:] = [KETTE.from_module]" in s
    assert "_kernweg.beobachter = KETTE" in s
    assert s.index("roh_l = lage.schreibe(st)") < s.index("KETTE.check(st.get(\"t\", 0), L, G, eigen_k)")


def _quarry(life=350):
    """Quarry (core building type 20, a 6x6 footprint from the corner) of game 20."""
    return {200: {"besitzer": 2, "typ": 20, "x": 262, "y": 80, "leben": life}}


def test_link_3_the_attack_must_start_at_once():
    """Game 20: assassin 418 stood in reach of worker 327 with state 1 - the attack never started (measured: 1-3 ticks after the
    order at the target)."""
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [418], "ziel": 327}})
    L = {418: _e(1, 73, 216, 36, zieleinheit=327, zielart=4, zustand=1), 327: _e(2, 7, 214, 36)}
    assert k.check(22722, L, {}) == []
    lines = k.check(22831, L, {})
    assert len(lines) == 1 and "418 (A_ASSASSIN 73) attack_unit U327 via module: ATTACK DID NOT START - in reach since tick 22722" in lines[0]
    assert "attack state 106 expected at once" in lines[0]


def test_link_5_a_melee_swing_on_a_building_must_hurt_it():
    """Measured 23:21: the assassin hits a building 93 ticks after the attack start (75 damage), the frame wraps 24 -> 0."""
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [418], "gebaeude": 200}})
    G = _quarry()
    assert k.check(25069, {418: _e(1, 73, 261, 82, zustand=107, bild=1, bildzyklus=0)}, G) == []
    G[200]["leben"] = 275
    assert k.check(25162, {418: _e(1, 73, 261, 82, zustand=107, bild=0, bildzyklus=30)}, G) == []
    assert "attack_building/module sent 1 taken 1 arrived 1 attack_started 1 damage 1" in k.summary()
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [418], "gebaeude": 200}})
    G = _quarry()
    assert k.check(25069, {418: _e(1, 73, 261, 82, zustand=107, bild=1, bildzyklus=0)}, G) == []
    assert k.check(25100, {418: _e(1, 73, 261, 82, zustand=107, bild=9, bildzyklus=10)}, G) == []
    lines = k.check(25162, {418: _e(1, 73, 261, 82, zustand=107, bild=3, bildzyklus=2)}, G)
    assert len(lines) == 1 and "NO DAMAGE AFTER A SWING (measured 93 ticks, 75 damage per hit) - attack state since tick 25069" in lines[0]
    assert "the animation ran: 3 different frames in 3 looks" in lines[0]


def test_link_4_a_standing_animation_is_its_own_break():
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [418], "gebaeude": 200}})
    G = _quarry()
    still = {418: _e(1, 73, 261, 82, zustand=107, bild=5, bildzyklus=6)}
    assert k.check(25069, still, G) == [] and k.check(25120, still, G) == []
    lines = k.check(25162, still, G)
    assert len(lines) == 1 and "ANIMATION STANDS - attack state since tick 25069, frame 5 cycle 6 in all 3 looks" in lines[0]
    assert "attack_building/module sent 1 taken 1 arrived 1 attack_started 1 animation_stands 1" in k.summary()


def test_the_far_side_of_a_big_building_is_in_reach():
    """The building's x, y is the corner of its footprint (measured 23:20); an attacker on the far side of the 6x6 quarry stands
    7 fields from the corner but next to the building."""
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [418], "gebaeude": 200}})
    G = _quarry()
    far = {418: _e(1, 73, 268, 86, zustand=107, bild=1, bildzyklus=0)}
    assert k.check(25000, far, G) == []
    G[200]["leben"] = 275
    assert k.check(25400, {418: _e(1, 73, 268, 86, zustand=107, bild=2, bildzyklus=1)}, G) == []
    assert "arrived 1 attack_started 1 damage 1" in k.summary() and "no_progress" not in k.summary()


def test_melee_hurts_a_unit_from_the_contact_on_and_must_within_13_ticks():
    """Measured 23:34 (9 melee types against E_SPEAR from 8 fields): the target loses life every tick from the contact on, the core
    shows state 106 3-11 ticks later; the longest gap in a fight was 12 ticks (after a second order)."""
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [5], "ziel": 40}})
    assert k.check(100, {5: _e(1, 73, 100, 100, zustand=101, zieleinheit=40), 40: _e(2, 24, 101, 100, leben=12500)}, {}) == []
    assert k.check(120, {5: _e(1, 73, 100, 100, zustand=101, zieleinheit=40), 40: _e(2, 24, 101, 100, leben=12020)}, {}) == []
    assert "damage 1" in k.summary()
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [5], "ziel": 40}})
    fight = {5: _e(1, 73, 100, 100, zustand=106, zieleinheit=40, bild=2, bildzyklus=1), 40: _e(2, 24, 101, 100, leben=12500)}
    assert k.check(100, fight, {}) == [] and k.check(110, fight, {}) == []
    fight[5] = _e(1, 73, 100, 100, zustand=106, zieleinheit=40, bild=4, bildzyklus=3)
    lines = k.check(113, fight, {})
    assert len(lines) == 1 and "NO DAMAGE AFTER THE CONTACT (melee hurts every tick, measured 120 per tick against E_SPEAR 24)" in lines[0]


def test_a_shooter_on_a_building_is_no_use_and_its_shots_on_units_are_checked_up_to_12_fields():
    """Measured 23:27: shooters do 1 damage per hit to a hut, most shots miss; against a standing assassin 12 fields away every
    shot hits (E_ARCHER first hit 122 ticks after the aim start, then every 129), at 30 fields E_ARCHER hit 0 of 4."""
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [9], "gebaeude": 200}})
    lines = k.check(500, {9: _e(1, 22, 255, 80, zustand=4, bild=1, bildzyklus=0, zielart=9, zielgebaeude=200)}, _quarry())
    assert len(lines) == 1 and "9 (E_ARCHER 22) attack_building B200 via module: NO USEFUL ATTACK - a shooter does 1 damage" in lines[0]
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [9], "ziel": 40}})
    near = {9: _e(1, 22, 100, 100, zustand=4, bild=1, bildzyklus=0), 40: _e(2, 73, 110, 100)}
    assert k.check(1000, near, {}, {9: {"schusseinheit": 40}}) == []
    near[9] = _e(1, 22, 100, 100, zustand=6, bild=7, bildzyklus=9)
    assert k.check(1250, near, {}, {9: {"schusseinheit": 40}}) == []
    near[9] = _e(1, 22, 100, 100, zustand=4, bild=2, bildzyklus=1)
    lines = k.check(1251, near, {}, {9: {"schusseinheit": 40}})
    assert len(lines) == 1 and "NO DAMAGE AFTER TWO SHOTS (measured: first hit 122 ticks after the aim start at 12 fields" in lines[0]
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [9], "ziel": 40}})
    far = {9: _e(1, 22, 100, 100, zustand=4, bild=1, bildzyklus=0), 40: _e(2, 73, 130, 100)}
    assert k.check(1000, far, {}, {9: {"schusseinheit": 40}}) == []
    # 13.11.2026 (Daniel "Ja, einbauen", S126): beyond 12 fields the measured trial size - 4 shots, the first hit 1.6 ticks later
    # per field: 122 + 29 + 3 x 129 = 538 ticks
    far[9] = _e(1, 22, 100, 100, zustand=6, bild=7, bildzyklus=9)    # the animation runs
    assert k.check(1537, far, {}, {9: {"schusseinheit": 40}}) == []
    lines = k.check(1538, far, {}, {9: {"schusseinheit": 40}})
    assert len(lines) == 1 and "NO DAMAGE AFTER 4 SHOTS FROM 30 FIELDS (measured beyond 12 fields: 0 of 4 hit at 30)" in lines[0]
    from selfaware.tools.checks.fehlerwache import kettenbrueche_aus
    assert len(kettenbrueche_aus(lines[0] + "\n")) == 1          # a chain break: the watch stops
    from selfaware.micro.chain_audit import shot_deadline
    assert shot_deadline(76, 15) is None          # no far trial for this type: not checked (its range is 11 fields anyway)


def test_game_5_four_archers_on_the_quarry_mason_from_33_fields_and_every_unit_says_what_it_expects():
    """S126: 308 at (198,69) shot U355 at (213,36) from tick 4648 to 4950, the mason kept 10000 life. Expected results come from
    the same tables the check uses (Daniel 13.11.2026 22:45 "jede Einheit muss ja sagen was sie macht und was das erwartete
    ergebenis ist")."""
    from selfaware.micro.chain_audit import expectation, shot_deadline
    assert shot_deadline(22, 33) == 122 + 34 + 3 * 129
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [308], "ziel": 355}})
    L = {308: _e(1, 22, 198, 69, zustand=4, bild=1, bildzyklus=0), 355: _e(2, 7, 213, 36)}
    assert k.check(4648, L, {}, {308: {"schusseinheit": 355}}) == []
    L[308] = _e(1, 22, 198, 69, zustand=6, bild=7, bildzyklus=9)
    assert k.check(4950, L, {}, {308: {"schusseinheit": 355}}) == []          # 302 ticks: not yet 4 shots
    lines = k.check(4648 + 543, L, {}, {308: {"schusseinheit": 355}})
    assert len(lines) == 1 and "308 (E_ARCHER 22) attack_unit U355 via module: NO DAMAGE AFTER 4 SHOTS FROM 33 FIELDS" in lines[0]
    assert expectation("ATTACK_UNIT", 22, (198, 69), (213, 36), "unit") == "no_hit_expected_from_33f(measured_0_of_4_at_30)"
    assert expectation("ATTACK_UNIT", 70, (100, 100), (130, 100), "unit") == "damage_within_379t_from_30f(measured)"
    assert expectation("ATTACK_UNIT", 22, (100, 100), (110, 100), "unit") == "damage_within_251t_from_10f(measured)"
    assert expectation("ATTACK_UNIT", 24, (100, 100), (101, 100), "unit") == "damage_within_13t_of_contact(measured)"
    assert expectation("ATTACK_BUILDING", 22, (100, 100), (110, 100), "building") == "useless_1_damage_per_hit_most_miss(measured)"
    assert expectation("ATTACK_BUILDING", 73, (100, 100), (101, 100), "building") == "hit_every_93t_75_damage(measured)"
    assert expectation("MOVE_TO_STAGING", 24, (100, 100), (110, 100), "point") == "arrive_in_~120t_for_10f_flat(model)"
    assert expectation("DIG", 24) == "digs_moat_tiles(time_UNMEASURED)"


def test_a_second_identical_order_to_a_fighting_melee_unit_is_reported():
    """Measured 23:34 in 9 of 9 melee types: the second order makes the unit walk (state 101 at +3) and costs 4/8/12 ticks of damage."""
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [5], "ziel": 40}})
    fight = {5: _e(1, 27, 100, 100, zustand=106, zieleinheit=40, bild=2, bildzyklus=1), 40: _e(2, 24, 101, 100, leben=12500)}
    assert k.check(100, fight, {}) == []
    k.tick = 130
    k.from_module({"angriff": {"einheiten": [5], "ziel": 40}})
    fight[40] = _e(2, 24, 101, 100, leben=7000)
    lines = k.check(140, fight, {})
    assert len(lines) == 1 and "RESEND WHILE FIGHTING - the same order again at tick 130 while the unit fought since tick 100" in lines[0]
    assert "no damage for 12 ticks" in lines[0] and k.check(200, fight, {}) == []
    assert "resend_fighting 1" in k.summary()


def test_an_unmeasured_type_is_said_once_and_does_not_stop_the_watch():
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [70], "ziel": 40}})
    L = {70: _e(1, 29, 100, 100, zustand=106, zieleinheit=40), 40: _e(2, 24, 101, 100)}
    lines = k.check(10, L, {})
    assert lines == ["CHAIN_INFO t=10 70 (E_LADDER 29) attack_unit: attack timing UNMEASURED for this type - links 4 and 5 not checked"]
    assert k.check(200, L, {}) == []
    from selfaware.tools.checks.fehlerwache import kettenbrueche_aus
    assert kettenbrueche_aus(lines[0] + "\n") == []


def test_out_of_reach_again_the_clocks_start_anew():
    """The target steps away before the first hit; when the attacker is back, its swing clock starts again - no false break."""
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [5], "ziel": 40}})
    L = {5: _e(1, 73, 100, 100, zustand=106, zieleinheit=40, bild=1, bildzyklus=0), 40: _e(2, 7, 101, 100, leben=1000)}
    assert k.check(100, L, {}) == []
    L[40] = _e(2, 7, 110, 100, leben=1000)
    L[5] = _e(1, 73, 101, 100, zustand=101, zieleinheit=40)
    assert k.check(105, L, {}) == []
    L[40] = _e(2, 7, 111, 100, leben=1000)
    L[5] = _e(1, 73, 110, 100, zustand=106, zieleinheit=40, bild=1, bildzyklus=0)
    assert k.check(200, L, {}) == []
    assert k.orders[5].attack_tick == 200


def test_the_watch_stops_on_every_chain_break():
    from selfaware.tools.checks.fehlerwache import kettenbrueche_aus

    text = ("CHAIN summary: walk/module sent 3 taken 3\n"
            "CHAIN t=23022 418 (A_ASSASSIN 73) attack_unit U327 via module: NO DAMAGE - in reach since tick 22722\n")
    assert kettenbrueche_aus(text) == [{"art": "F5 Kette", "takt": 23022, "einheit": 418,
                                        "text": "A_ASSASSIN 73: attack_unit U327 via module: NO DAMAGE - in reach since tick 22722"}]
    with open(os.path.join(QUELLE, "tools", "checks", "fehlerwache.py"), encoding="utf-8") as f:
        assert "fehler = wache.schritt(w, anspruechen_mit_takt(text)) + kettenbrueche_aus(text)" in f.read()


def test_link_2_a_walk_behind_the_game_speed_names_who_stands_around():
    """Measured 00:20: the core's path index moves one field per field; the assassin walks 16 ticks a field at speed value 1."""
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [5], "lauf": [150, 100]}})
    pos = {5: _e(1, 73, 100, 100, laufx=150, laufy=100, zustand=101)}
    eig = {5: {"wegindex": 0, "weglaenge": 50, "tempo": 1}}
    assert k.check(1000, pos, {}, eig) == []
    eig[5] = {"wegindex": 5, "weglaenge": 50, "tempo": 1}
    pos[5] = _e(1, 73, 105, 100, laufx=150, laufy=100, zustand=101)
    assert k.check(1080, pos, {}, eig) == []              # 5 fields in 80 ticks: on time
    pos.update({7: _e(1, 24, 106, 100), 8: _e(2, 3, 105, 101), 9: _e(2, 24, 104, 99)})
    pos[5] = _e(1, 73, 105, 100, laufx=150, laufy=100, zustand=1)
    eig[5] = {"wegindex": 5, "weglaenge": 50, "tempo": 1}
    assert k.check(1120, pos, {}, eig) == []              # 2.5 fields behind: not yet
    lines = k.check(1150, pos, {}, eig)
    assert len(lines) == 1 and "WALK BEHIND THE GAME'S SPEED - path index 5 of 50, 0.0 fields walked since on time where the " \
                               "speed value 1 (flat 1) gives 4.4: blocked or crowded; within 1 field: enemy 1, own 1, population 1" \
                               in lines[0]
    assert "slow_walk 1" in k.summary()


def test_link_2_a_walker_that_fights_is_named_as_fighting_not_as_blocked():
    """Game 16 of 14.11.2026 (S142): spearman 332 had a walk order to (230,70) and fought the enemy woodcutter 365 two fields away
    (state 106, nahziel 365); the line said 'blocked or crowded; within 1 field: nobody'. The line stays (the walk order is not
    carried out) - it names the fight and the opponent."""
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [332], "lauf": [230, 70]}})
    eig = {332: {"wegindex": 2, "weglaenge": 9, "tempo": 1}}
    pos = {332: _e(1, 24, 229, 62, laufx=230, laufy=70, zustand=101)}
    assert k.check(4763, pos, {}, eig) == []
    pos = {332: _e(1, 24, 229, 62, laufx=230, laufy=70, zustand=106, nahziel=365), 365: _e(2, 3, 231, 63, zustand=106)}
    assert k.check(4885, pos, {}, eig) == []      # S147: the first check that sees the fight waits - the module may take it over
    lines = k.check(5005, pos, {}, eig)
    assert len(lines) == 1 and "FIGHTS INSTEAD OF WALKING - state 106 (melee against a unit) against U365 (population, type 3, " \
                               "2 fields away); within 1 field: nobody; state 106" in lines[0], lines
    assert "blocked or crowded" not in lines[0]


def test_an_attack_the_fight_guard_holds_back_becomes_the_units_order():
    """Game 16 (S142): the melee raid takes the worker its spearman fights as target; the fight guard holds the attack back (the
    unit fights exactly that target). The chain audit takes it as the unit's order - without it the walk order before it stayed and
    would stop the game on 'FIGHTS INSTEAD OF WALKING'. A second held attack on the same target is no new order (S118)."""
    from selfaware.execution import kampfschutz

    k = ChainAudit(1)
    k.tick = 4745
    k.from_module({"angriff": {"einheiten": [332], "lauf": [230, 70]}})
    eig = {332: {"wegindex": 2, "weglaenge": 9, "tempo": 1}}
    pos = {332: _e(1, 24, 229, 62, laufx=230, laufy=70, zustand=106, nahziel=365), 365: _e(2, 3, 231, 63, zustand=106, leben=6975)}
    assert k.check(4763, pos, {}, eig) == []
    kampfschutz.ERFUELLT[:] = [k.from_guard]
    try:
        kampfschutz.stand(pos)
        k.tick = 4770
        for _ in range(2):
            assert kampfschutz.filtern({"angriff": {"einheiten": [332], "ziel": 365}})[0] is None
    finally:
        kampfschutz.ERFUELLT[:] = []
        kampfschutz.stand({})
    o = k.orders[332]
    assert (o.kind, o.target, o.channel, o.tick) == ("attack_unit", 365, "guard", 4770)
    assert k.check(4885, pos, {}, eig) == []
    pos[365] = _e(2, 3, 231, 63, zustand=106, leben=3925)
    assert k.check(5000, pos, {}, eig) == []
    assert "attack_unit/guard held 1 taken 1" in k.summary() and "slow_walk" not in k.summary()


def test_game_19_a_fight_the_game_started_waits_one_check_for_the_module():
    """Game 19 (S147): spearman 330 walked to (237,69) and fought the enemy woodcutter 365 at the next check; the melee raid took
    the fight over in the same round, the fight guard held its attack back - but the check at the start of that round had already
    stopped the game. Now that first check waits; the held attack becomes the order, and no line comes."""
    from selfaware.execution import kampfschutz

    k = ChainAudit(1)
    k.tick = 5059
    k.from_module({"angriff": {"einheiten": [330], "lauf": [237, 69]}})
    eig = {330: {"wegindex": 4, "weglaenge": 16, "tempo": 1}}
    assert k.check(5059, {330: _e(1, 24, 240, 110, laufx=237, laufy=69, zustand=101)}, {}, eig) == []
    pos = {330: _e(1, 24, 238, 100, laufx=237, laufy=69, zustand=106, nahziel=365), 365: _e(2, 3, 238, 98, zustand=106, leben=5000)}
    eig[330] = {"wegindex": 7, "weglaenge": 16, "tempo": 1}
    assert k.check(5250, pos, {}, eig) == []
    k.tick = 5250
    kampfschutz.ERFUELLT[:] = [k.from_guard]
    try:
        kampfschutz.stand(pos)
        assert kampfschutz.filtern({"angriff": {"einheiten": [330], "ziel": 365}})[0] is None
    finally:
        kampfschutz.ERFUELLT[:] = []
        kampfschutz.stand({})
    pos[365] = _e(2, 3, 238, 98, zustand=106, leben=2000)
    assert k.check(5400, pos, {}, eig) == [] and k.orders[330].kind == "attack_unit"


def test_game_19_a_held_attack_is_taken_at_once_and_a_new_opponent_waits_one_check():
    """Game 19 (S147): the guard held an attack of 331 on worker 360 (tick 5059); at the next check 331 fought worker 321 - the
    held order counted as never seen and stopped the game on NOT SEEN."""
    k = ChainAudit(1)
    k.tick = 5059
    k.from_guard(False, 360, [331])
    assert k.orders[331].taken == 5059
    pos = {331: _e(1, 24, 295, 133, laufx=295, laufy=133, zustand=106, zieleinheit=321), 360: _e(2, 3, 300, 140),
           321: _e(2, 3, 296, 134)}
    assert k.check(5250, pos, {}, {331: {}}) == []
    assert "attack_unit/guard held 1 taken 1" in k.summary() and "not_seen" not in k.summary()


def test_link_2_with_the_terrain_map_mud_between_two_reads_is_no_break():
    """Game 8 of 13.11.2026 (S129): spearman 332 crossed mud between two reads of its speed value (both flat) - the old check
    expected flat speed and stopped the game. With the terrain map the walked fields count through the game's rule (Daniel 23:35
    "Ja, umbauen"); a unit that stands still is still reported."""
    import selfaware.services.laufmodell as LM

    def tile(x, y):
        return (0x208000 if 103 <= x <= 110 and y == 100 else 0x8000), 1, 8      # mud (LogicLayer 0x200000) on 8 fields

    need = LM.walk(24, LM.gerade((100, 100), (113, 100)), tile)[-1]
    assert need > 13 * 12 + 4 * 12                   # the mud costs more than 4 flat fields
    for terrain, broken in ((tile, False), (None, True)):
        k = ChainAudit(1, tile=terrain)
        k.from_module({"angriff": {"einheiten": [332], "lauf": [150, 100]}})
        pos = {332: _e(1, 24, 100, 100, laufx=150, laufy=100, zustand=101)}
        assert k.check(1000, pos, {}, {332: {"wegindex": 0, "weglaenge": 50, "tempo": 1}}) == []
        pos[332] = _e(1, 24, 113, 100, laufx=150, laufy=100, zustand=101)
        lines = k.check(1000 + need, pos, {}, {332: {"wegindex": 13, "weglaenge": 50, "tempo": 1}})
        assert bool(lines) == broken and (not lines or "WALK BEHIND THE GAME'S SPEED" in lines[0])
    k = ChainAudit(1, tile=tile)
    k.from_module({"angriff": {"einheiten": [332], "lauf": [150, 100]}})
    pos = {332: _e(1, 24, 113, 100, laufx=150, laufy=100, zustand=101)}
    assert k.check(2000, pos, {}, {332: {"wegindex": 13, "weglaenge": 50, "tempo": 1}}) == []
    assert k.check(2059, pos, {}, {332: {"wegindex": 13, "weglaenge": 50, "tempo": 1}}) == []      # 59 - 12 in the field: under 4 x 12
    lines = k.check(2060, pos, {}, {332: {"wegindex": 13, "weglaenge": 50, "tempo": 1}})
    assert len(lines) == 1 and "WALK BEHIND THE TERRAIN - path index 13 of 50, 0 fields walked since on time, 48 ticks behind" in lines[0]


def test_link_2_the_limit_grows_with_the_way_by_the_measured_spread():
    """Game 9 of 13.11.2026 (S131): spearman 330 was 54 ticks (6 %) behind the terrain model after 75 fields - inside the measured
    spread of spearmen (slowest quarter 0.87 of the model). Daniel 23:40 "Ja, mitrechnen". 25 % slower is still reported."""
    import selfaware.micro.chain_audit as CA
    import selfaware.services.laufmodell as LM

    def flat(x, y):
        return 0x8000, 1, 8

    assert CA.STREUUNG.get(24) == 0.87
    for slower, broken in ((1.06, False), (1.25, True)):
        k = ChainAudit(1, tile=flat)
        k.from_module({"angriff": {"einheiten": [330], "lauf": [400, 100]}})
        t, x, lines = 1000, 100, []
        k.check(t, {330: _e(1, 24, x, 100, laufx=400, laufy=100, zustand=101)}, {}, {330: {"wegindex": 0, "weglaenge": 300,
                                                                                         "tempo": 1}})
        for i in range(5):                                    # 5 x 15 fields = 75 fields
            need = LM.walk(24, LM.gerade((x, 100), (x + 15, 100)), flat)[-1]
            t, x = t + int(need * slower), x + 15
            lines += k.check(t, {330: _e(1, 24, x, 100, laufx=400, laufy=100, zustand=101)}, {},
                             {330: {"wegindex": 15 * (i + 1), "weglaenge": 300, "tempo": 1}})
        assert bool(lines) == broken
        assert not lines or "slowest quarter of the measured walks 0.87 of the model" in lines[0]


def test_link_2_terrain_is_counted_by_the_game_and_no_break():
    """In water the speed value rises (+3/+4/+6): the walk is slower, but as fast as the game says - no line."""
    k = ChainAudit(1)
    k.from_module({"angriff": {"einheiten": [5], "lauf": [150, 100]}})
    pos = {5: _e(1, 73, 100, 100, laufx=150, laufy=100, zustand=101)}
    t, idx = 1000, 0
    assert k.check(t, pos, {}, {5: {"wegindex": 0, "weglaenge": 50, "tempo": 5}}) == []
    for _ in range(6):
        t, idx = t + 96, idx + 2                      # speed value 5: 6 ticks a move, 48 a field -> 2 fields in 96 ticks
        pos[5] = _e(1, 73, 100 + idx, 100, laufx=150, laufy=100, zustand=101)
        assert k.check(t, pos, {}, {5: {"wegindex": idx, "weglaenge": 50, "tempo": 5}}) == []
    assert k.orders[5].slowed == 7 and "slow_walk" not in k.summary()


def test_link_2_a_ford_walked_exactly_as_the_game_rule_says_is_no_break():
    """Game 13 of 14.11.2026 (S137): spearman 336 waded through a ford at (166,216..209) - one model walk over the whole recorded
    way hit every field within a few ticks; the check cut the way into pieces per round and saw the unit at the end of a slow water
    field. Here the unit walks exactly as the model says and is looked at every 90-130 ticks: no line."""
    import selfaware.services.laufmodell as LM

    def tile(x, y):
        return (0x20008000 if 209 <= y <= 216 else 0x8000), (2 if 209 <= y <= 216 else 1), 8   # water: LogicLayer 0x20000000, macro 2

    weg = LM.gerade((166, 230), (166, 120))
    an = LM.walk(24, weg, tile, start_tick=2000)                 # tick at which each next field is reached
    k = ChainAudit(1, tile=tile)
    k.from_module({"angriff": {"einheiten": [336], "lauf": [166, 100]}})
    lines = []
    for t in (2000, 2095, 2190, 2320, 2410, 2540, 2650):
        i = sum(1 for a in an if a <= t)                            # fields reached by now
        x, y = weg[i]
        lines += k.check(t, {336: _e(1, 24, x, y, laufx=166, laufy=100, zustand=101)}, {},
                         {336: {"wegindex": i, "weglaenge": 130, "tempo": 1}})
    assert lines == []


def test_link_2_a_new_order_right_after_a_ford_goes_on_with_the_wet_unit():
    """Game 14 of 14.11.2026 (S138): spearman 334 waded the ford at (166,216..210) and got a new walk order at (166,209); the
    check began the model anew - dry, from move count 0, and with 4 fields (the path index) where the unit stood 5 fields on - and
    stopped the game: '62 ticks behind'. Over the whole way, from the most favourable of the 8 move counts, the unit hit every
    field. Here the unit walks as the model says with move count 4 and gets the new order behind the ford: no line. Standing in the
    ford after the new order is still reported."""
    import selfaware.services.laufmodell as LM

    def tile(x, y):
        wasser = 210 <= y <= 216
        return (0x20008000 if 208 <= y <= 217 else 0x8000), (4 if wasser else 1), 8   # 217, 209, 208: water flag, macro 1

    weg = LM.gerade((166, 253), (166, 120))
    an = LM.walk(24, weg, tile, start_tick=1894, phase=4)
    runden = (1894, 2011, 2104, 2171, 2270, 2323, 2433, 2550, 2666, 2780, 2900)
    # spaet: the game shows the new order one round late (its walk target still the old one at 2550) - the way goes on all the same
    for steht, spaet, broken in ((False, False, False), (False, True, False), (True, False, True)):
        k = ChainAudit(1, tile=tile)
        k.from_module({"angriff": {"einheiten": [334], "lauf": [166, 102]}})
        lines, i_neu = [], None
        for t in runden:
            i = sum(1 for a in an if a <= t)
            k.tick = t                                   # the Lenker sets it each round (the sending tick of module orders)
            if t == 2550:
                k.from_module({"angriff": {"einheiten": [334], "lauf": [170, 98]}})
                i_neu = i
            if steht and i_neu is not None:
                i = i_neu
            x, y = weg[i]
            neu = i_neu is not None and not (spaet and t == 2550)
            idx, n = (max(0, i - i_neu - 1), 111) if neu else (i, 200)          # the new path index lags one field
            lines += k.check(t, {334: _e(1, 24, x, y, laufx=170 if neu else 166, laufy=98 if neu else 102, zustand=101)},
                             {}, {334: {"wegindex": idx, "weglaenge": n, "tempo": 1}})
        assert bool(lines) == broken, lines
        assert k.trails[334].t0 == 1894 or steht        # followed since the first round over both orders
        assert not lines or ("WALK BEHIND THE TERRAIN" in lines[0] and "since the path began at tick 2550, the most favourable "
                                                                          "of the 8 move counts, the unit's state carried since tick 1894 over 2 orders" in lines[0])
