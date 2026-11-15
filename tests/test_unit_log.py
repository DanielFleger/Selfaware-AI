"""B-182 unit status log (docs/plans/Plan_Unit_Status_Log.md section 6): intent per module, movement phase from the Wegfuehrung,
NO_ORDER for fighters nobody leads. Daniel 2026-11-12 19:50: "Ohne Auftrag ist für mich das Schlimmste - es sollte immer eine
Begründung geben"."""

import gzip
import json
import os
import sys
from types import ModuleType

import pytest

from selfaware.micro import unit_log as UL
from selfaware.micro import wegfuehrung as W
from selfaware.micro.unit_log import Action, UnitLog

HIER = os.path.dirname(os.path.abspath(__file__))
QUELLE = os.path.join(HIER, "..", "src", "selfaware")


def _e(owner, typ, x=100, y=100, leben=10000):
    return {"besitzer": owner, "typ": typ, "x": x, "y": y, "leben": leben}


class Befehle:
    def __init__(self):
        self.liste = []

    def __call__(self, b, _warte=None, bis=None):
        self.liste.append(b)


# ---- the log itself ---------------------------------------------------------------------------------------------------
def test_a_fighter_nobody_reports_is_no_order():
    log = UnitLog(1)
    L = {
        1: _e(1, 71),
        2: _e(1, 22),
        3: _e(1, 55),
        4: _e(2, 22),
        5: _e(1, 3),
    }  # slave, bowman, lord, enemy, worker
    log.report(
        1, "brandtrupp", Action.WAIT_STAGING, reason="all_targets_covered", covered_by="2xT23"
    )
    lines = log.close_round(500, L)
    assert log.no_order() == [2]  # lord, enemy and worker are not fighters of ours
    assert (
        "UNIT t=500 1 (A_SLAVE 71) brandtrupp WAIT_STAGING reason=all_targets_covered path=- covered_by=2xT23 expect=stays_at_point"
        in lines
    )
    assert (
        "UNIT t=500 2 (E_ARCHER 22) nobody NO_ORDER reason=no_module_reported path=- expect=none"
        in lines
    )


def test_only_changes_are_printed_and_the_latest_report_wins():
    log = UnitLog(1)
    L = {1: _e(1, 71)}
    log.report(1, "waechter", Action.HOLD_POST, reason="no_threat_stays")
    log.report(
        1, "brandtrupp", Action.SET_FIRE, target="B7", reason="best_value_per_distance", dist=30
    )
    assert log.close_round(10, L) == [
        "UNIT t=10 1 (A_SLAVE 71) brandtrupp SET_FIRE target=B7 reason=best_value_per_distance path=- dist=30 expect=fire_477t_after_attack_start(measured)"
    ]
    log.report(
        1, "brandtrupp", Action.SET_FIRE, target="B7", reason="best_value_per_distance", dist=28
    )
    assert log.close_round(20, L) == []  # only a parameter changed: no line, the table has it
    assert "1 71 brandtrupp SET_FIRE B7 best_value_per_distance - dist=28" in log.table()


def test_unknown_actions_are_refused():
    with pytest.raises(ValueError, match="unknown action"):
        UnitLog(1).report(1, "x", "DANCE")


def test_a_path_without_module_reason_says_so_and_a_different_path_target_is_kept():
    log = UnitLog(1)
    L = {1: _e(1, 74), 2: _e(1, 70), 3: _e(1, 71)}
    log.path(1, "reiterjagd", "unterwegs", "U40", (120, 100))
    log.report(2, "vorstoss", Action.ATTACK_UNIT, "U41", "safe_target_in_range")
    log.path(2, "vorstoss", "greift_an", "U42")
    log.path(3, "brandtrupp", "am_ziel", "(150,100)")
    lines = log.close_round(30, L)
    assert (
        "UNIT t=30 1 (A_HARCHER 74) reiterjagd ATTACK_UNIT target=U40 reason=no_module_reason path=walking wp=(120,100) expect=hit_UNMEASURED_distance_unknown"
        in lines
    )
    assert (
        "UNIT t=30 2 (A_ARCHER 70) vorstoss ATTACK_UNIT target=U41 reason=safe_target_in_range path=attacking path_target=U42 expect=hit_UNMEASURED_distance_unknown"
        in lines
    )
    assert any(
        z.startswith("UNIT t=30 3 (A_SLAVE 71) brandtrupp WAIT_STAGING target=(150,100)")
        for z in lines
    )
    assert log.no_order() == []
    log.report(4, "waechter", Action.MOVE_TO_STAGING, "(151,280)", "advance_toward_target")
    log.path(
        4, "waechter", "am_ziel", "(151,280)"
    )  # Partie 12.11. 20:34: 42 % of the spearmen's rounds read "moving" while there
    log.close_round(31, {4: _e(1, 24)})
    assert log.last[4][1] == Action.WAIT_STAGING and log.last[4][3] == "advance_toward_target"


def test_gone_units_and_the_table_reads_back():
    log = UnitLog(1)
    log.report(
        1, "brandtrupp", Action.WAIT_STAGING, "(180,100)", "no_free_target", danger=2, taken=1
    )
    log.path(1, "brandtrupp", "unterwegs", "(180,100)", (150, 100))
    log.report(2, "waechter", Action.HOLD_POST, None, "start_post")
    log.close_round(40, {1: _e(1, 71), 2: _e(1, 24)})
    tick, rows = UL.read_table(log.table())
    assert tick == 40 and rows[1]["target"] == "(180,100)" and rows[1]["path"] == "walking"
    assert rows[1]["params"] == {
        "danger": "2",
        "taken": "1",
        "wp": "(150,100)",
    }  # points keep their comma
    assert rows[2]["target"] == "-" and rows[2]["reason"] == "start_post"
    log.report(2, "waechter", Action.HOLD_POST, None, "start_post")
    assert log.close_round(50, {2: _e(1, 24)}) == [
        "UNIT t=50 1 (A_SLAVE 71) gone"
    ]  # the slave died; the spearman did not change


def test_names_follow_the_game_code_and_type_23_stays_a_number():
    assert (
        UL.type_name(74) == "A_HARCHER 74"
        and UL.type_name(24) == "E_SPEAR 24"
        and UL.type_name(23) == "T23"
    )


# ---- the Wegfuehrung ---------------------------------------------------------------------------------------------------
def test_wegfuehrung_reports_phase_target_and_next_waypoint():
    w = W.Wegfuehrung(1)
    L = {1: _e(1, 71, 100, 100), 2: _e(1, 24, 150, 150)}
    G = {7: _e(2, 3, 200, 100)}
    w.fuehre(1, "gebaeude", 7, "brandtrupp")
    w.fuehre(2, "ort", (151, 151), "waechter")
    w.schritt(L, G, Befehle())
    ab = w.absichten()
    assert ab[1][:3] == ("brandtrupp", "unterwegs", "B7") and ab[1][3] is not None
    assert ab[2][:3] == ("waechter", "am_ziel", "(151,151)")


# ---- the modules ---------------------------------------------------------------------------------------------------------
def test_brandtrupp_reports_its_target_and_why_a_slave_waits():
    from selfaware.micro.tasks import raids as RA

    bt = RA.Brandtrupp(1, lambda nr: 0)
    bt.weg = W.Wegfuehrung(1)
    L, G = {1: _e(1, 71, 100, 100)}, {7: _e(2, 3, 200, 100)}
    bt.schritt(L, G, Befehle())
    assert bt.absicht[1] == (
        Action.SET_FIRE,
        "B7",
        "best_value_per_distance",
        {"typ": 3, "dist": 100},
    )
    bt.schritt(L, G, Befehle())
    assert bt.absicht[1] == (Action.SET_FIRE, "B7", "keeps_target", {"typ": 3})
    bt2 = RA.Brandtrupp(1, lambda nr: 0)
    bt2.weg = W.Wegfuehrung(1)
    L2 = {
        1: _e(1, 71, 100, 100),
        60: _e(2, 22, 200, 60),
    }  # a bowman covers the only target (as in test_wegfuehrung)
    bt2.schritt(L2, G, Befehle())
    assert bt2.absicht[1] == (Action.WAIT_STAGING, "(180,100)", "no_free_target", {"danger": 1})


def test_reiterjagd_reports_the_hunt_and_the_flight():
    from selfaware.micro.tasks import raids as RA

    rj = RA.Reiterjagd(1)
    rj.weg = W.Wegfuehrung(1)
    L = {1: _e(1, 74, 100, 100), 30: _e(2, 3, 110, 100)}
    rj.schritt(L, {}, Befehle())
    assert rj.absicht[1] == (Action.ATTACK_UNIT, "U30", "worker_in_range", {"typ": 3, "dist": 10})
    L[31] = _e(2, 24, 104, 100)  # a spearman next to the rider
    rj.schritt(L, {}, Befehle())
    assert (
        rj.absicht[1][0] == Action.FLEE
        and rj.absicht[1][2] == "melee_near"
        and rj.absicht[1][3] == {"typ": 24, "dist": 4}
    )


def test_deckung_reports_attack_front_and_waiting():
    from selfaware.micro.tasks import raids as RA

    d = RA.Deckung(1, (50, 50))
    d.schritt({1: _e(1, 72, 100, 100), 30: _e(2, 3, 105, 100)}, {}, Befehle())
    assert d.absicht[1] == (
        Action.ATTACK_UNIT,
        "U30",
        "enemy_in_range",
        {"typ": 3, "rank": "worker"},
    )
    d.schritt({1: _e(1, 72, 100, 100)}, {7: _e(2, 3, 200, 100)}, Befehle())
    assert d.absicht[1] == (Action.MOVE_TO_STAGING, "(200,100)", "to_front", {})
    d.schritt({1: _e(1, 72, 100, 100)}, {}, Befehle())
    assert d.absicht[1] == (Action.WAIT_STAGING, None, "no_front", {})


def test_vorstoss_reports_one_intent_for_the_group_and_gather_for_a_straggler():
    from selfaware.micro.tasks import vorstoss as VS

    v = VS.Vorstoss(1, (100, 100), bis=40000)
    v.weg = W.Wegfuehrung(1)
    v.schritt(
        500, {1: _e(1, 22, 100, 100), 2: _e(1, 22, 100, 101), 3: _e(2, 3, 130, 110)}, {}, Befehle()
    )
    assert {n: a[:3] for n, a in v.absicht.items()} == {
        1: (Action.ATTACK_UNIT, "U3", "safe_target_in_range"),
        2: (Action.ATTACK_UNIT, "U3", "safe_target_in_range"),
    }
    v2 = VS.Vorstoss(
        1, (149, 274), bis=40000
    )  # the straggler case of test_wegfuehrung (Partie 11.11. 23:40)
    v2.weg = W.Wegfuehrung(1)
    L = {n: _e(1, 22, 199 + n % 3, 185) for n in range(1, 7)}
    L[7] = _e(1, 70, 185, 238)
    L[50] = _e(2, 3, 201, 60)
    v2.schritt(1000, L, {90: _e(2, 74, 201, 133)}, Befehle())
    assert v2.absicht[7][:3] == (Action.GATHER, "(200,185)", "straggler")
    assert {v2.absicht[n][0] for n in range(1, 7)} == {Action.WAIT_STAGING}
    assert v2.absicht[1][2] in ("no_safe_firing_position", "advance_unsafe")
    v2.schritt(40000, L, {}, Befehle())  # end of the advance: released, said once
    assert {a[2] for a in v2.absicht.values()} == {"advance_ended_back_to_guard"} and len(
        v2.absicht
    ) == 7


def test_nahkampf_raid_reports_a_member_without_target():
    from selfaware.micro.tasks import nahkampf as NK

    nk = NK.NahkampfRaid(1)
    nk.schritt({5: _e(1, 1, 100, 100)}, {}, Befehle())  # first round: what exists
    nk.bestellt(75, 1)
    nk.schritt({5: _e(1, 75, 100, 100)}, {}, Befehle())  # the peasant became a swordsman: he joins
    assert 5 in nk.mitglieder and nk.absicht[5] == (
        Action.WAIT_SAFE_TARGET,
        None,
        "no_target_with_value",
        {"targets": 0},
    )


def test_graben_reports_its_diggers_and_releases_them_once():
    import selfaware.macro.kornring as KR

    werte = {"wert": KR.GEPLANT}
    g = KR.Graben(
        (100, 100),
        (200, 200),
        lambda soll: {k: werte["wert"] for k in soll},
        lambda *a: None,
        lambda e, z: None,
    )
    L = {5: _e(1, 24, 102, 102), 6: _e(1, 24, 103, 102)}
    g.schritt(1000, L, 1)
    ab = g.absichten(L)
    assert (
        sorted(ab) == [5, 6]
        and ab[5][0] == Action.DIG
        and ab[5][2] == "moat_unfinished"
        and ab[5][1] is not None
    )
    werte["wert"] = KR.GEGRABEN
    g.schritt(2000, L, 1)
    assert {n: a[2] for n, a in g.absichten(L).items()} == {
        5: "moat_finished_back_to_guard",
        6: "moat_finished_back_to_guard",
    }
    assert g.absichten(L) == {}  # from now on they belong to the Waechter


def test_graben_takes_its_diggers_away_from_the_wegfuehrung():
    """Logbuch, Partie 12.11. 20:34, Takt 1.139: spearmen 331-334 were diggers for the Graben while the Wegfuehrung still led them
    to the Waechter's stacking point (path_target) - one leader per unit."""
    import selfaware.macro.kornring as KR

    w = W.Wegfuehrung(1)
    L = {5: _e(1, 24, 102, 102), 6: _e(1, 24, 103, 102)}
    w.fuehre(5, "ort", (151, 151), "waechter")
    gesendet = []
    g = KR.Graben(
        (100, 100),
        (200, 200),
        lambda soll: {k: KR.GEPLANT for k in soll},
        lambda *a: None,
        lambda e, z: gesendet.append((list(e), z)),
    )
    g.weg = w
    g.schritt(1000, L, 1)
    assert gesendet and 5 in gesendet[0][0] and not w.fuehrt(5)


def test_assassins_report_from_their_state_and_say_when_they_have_no_task():
    try:
        import selfaware.micro.tasks.assassinen as AS
    except (
        RuntimeError
    ) as ex:  # without a game instance (SHC_INSTANZ=99) the module cannot be loaded
        pytest.skip(str(ex))
    a = AS.Einzeln(1)
    a.mitglieder = {5, 6, 7}
    a.ziel[5] = 33
    a.jagd[7] = 40
    L = {5: _e(1, 73), 6: _e(1, 73), 7: _e(1, 73), 40: _e(2, 3)}
    ab = a.absichten(L, {33: _e(2, 13, 150, 150)})
    assert ab[5] == (Action.ATTACK_BUILDING, "B33", "raid_building", {"typ": 13})
    assert ab[6] == (Action.NO_ORDER, None, "module_has_no_task", {})
    assert ab[7] == (Action.ATTACK_UNIT, "U40", "hunt", {"typ": 3})


def test_an_assassin_without_target_who_stays_safe_near_the_front_says_why():
    """Partie 12.11. 20:45: UNIT_NO_ORDER for assassins 498 (tick 17,203) and 494 (35,371) - the module's own count said
    "1 Assassinen ohne Ziel (alle gefaehrlich 1)", but a unit already standing safe near the front gets no order and the decision was
    written nowhere. Real target choice on a small scene: two T23 cover the only building, the assassin stands 25 fields before it."""
    try:
        import selfaware.micro.tasks.assassinen as AS
    except RuntimeError as ex:
        pytest.skip(str(ex))

    def e(nr, owner, typ, x, y, **k):
        d = {
            "nr": nr,
            "gruppe": 0,
            "besitzer": owner,
            "typ": typ,
            "x": x,
            "y": y,
            "leben": 10000,
            "zustand": 1,
            "zielart": 0,
            "zieleinheit": 0,
            "laufx": x,
            "laufy": y,
            "ladung": 0,
            "arbeitsplatz": 0,
            "erreichbar": 1,
            "nahziel": -1,
            "nahangreifer": -1,
        }
        d.update(k)
        return d

    G = {
        33: {
            "besitzer": 2,
            "typ": 3,
            "x": 265,
            "y": 100,
            "leben": 60,
            "uid": 1,
            "erreichbar": 1,
            "vorrat": None,
            "grenze": None,
            "verbund": None,
            "ware": None,
        }
    }
    for armbrust_x, erwartet in (
        (285, (Action.WAIT_STAGING, "(240,100)", "all_targets_dangerous", {})),
        (300, (Action.ATTACK_BUILDING, "B33", "raid_building", {"typ": 3})),
    ):
        a = AS.Einzeln(1)
        L = {
            1: e(1, 1, 55, 100, 100, leben=150000),
            5: e(5, 1, 73, 240, 100, leben=50000),
            60: e(60, 2, 55, 340, 100, leben=150000),
            61: e(61, 2, 23, armbrust_x, 100),
            62: e(62, 2, 23, armbrust_x, 104),
        }
        a.aufnehmen([5])
        a.schritt(L, G, sichere_orte=[(100, 100)], tick=1000)
        assert a.absichten(L, G)[5] == erwartet, armbrust_x


def test_waechter_reports_every_unit_with_its_last_order(monkeypatch):
    try:
        import selfaware.micro.tasks.waechter as WA
    except RuntimeError as ex:
        pytest.skip(str(ex))
    monkeypatch.setattr(WA, "befehl", lambda b, *a, **k: [])

    def e(typ, sp, x, y, **k):
        d = {
            "typ": typ,
            "besitzer": sp,
            "x": x,
            "y": y,
            "leben": 10000,
            "zustand": 1,
            "laufx": x,
            "laufy": y,
            "nahziel": 0,
            "nahangreifer": 0,
            "zieleinheit": 0,
        }
        d.update(k)
        return d

    gebaeude = [(150, 160), (145, 215), (150, 200)]
    ruhig = {60: e(24, 1, 155, 158), 61: e(24, 1, 156, 158), 62: e(75, 1, 156, 159)}
    w = WA.Waechter(1, posten=(150, 160))
    w.schritt(ruhig, gebaeude)
    assert {n: a[2] for n, a in w.absicht.items()} == {
        60: "start_post",
        61: "start_post",
        62: "start_post",
    }
    w.weg = W.Wegfuehrung(1, trotz_gefahr=("waechter",))
    feind = {**ruhig, 156: e(71, 2, 148, 163)}
    w.schritt(feind, gebaeude)
    angreifer = [n for n, z in w.auftrag.items() if z == 156]
    assert angreifer and all(
        w.absicht[n][:3] == (Action.DEFEND, "U156", "intruder") for n in angreifer
    )
    w.schritt(ruhig, gebaeude)  # the intruder is gone: who fought stays where he is, and says so
    assert all(w.absicht[n][2] == "no_threat_stays" for n in angreifer)
    w.schritt(ruhig, gebaeude, ausgenommen={62})
    assert 62 not in w.absicht  # belongs to another module now


def test_waechter_intercept_holds_at_the_enemy_destination(monkeypatch):
    """Partie 12.11. 21:03, tick 17,487: "Abfangen" sent the spearmen to the enemy's destination with a hold order, but the
    Wegfuehrung kept leading them to the stack point (path_target) - they never intercepted."""
    try:
        import selfaware.micro.tasks.waechter as WA
    except RuntimeError as ex:
        pytest.skip(str(ex))
    gesendet = []
    monkeypatch.setattr(WA, "befehl", lambda b, *a, **k: gesendet.append(b) or [])

    def e(typ, sp, x, y, **k):
        d = {
            "typ": typ,
            "besitzer": sp,
            "x": x,
            "y": y,
            "leben": 10000,
            "zustand": 1,
            "laufx": x,
            "laufy": y,
            "nahziel": 0,
            "nahangreifer": 0,
            "zieleinheit": 0,
        }
        d.update(k)
        return d

    gebaeude = [(150, 160)]
    ruhig = {60: e(24, 1, 150, 200), 61: e(24, 1, 151, 200), 70: e(22, 1, 150, 230)}
    w = WA.Waechter(1)
    w.besetzt = True
    w.weg = W.Wegfuehrung(1, trotz_gefahr=("waechter",))
    w.schritt(ruhig, gebaeude)
    assert not w.weg.fuehrt(
        60
    )  # 13.11.2026 23:02: no stacking on the archers' field any more (Daniel: "ueberall entfernen")
    feind = {
        **ruhig,
        555: e(71, 2, 150, 100, laufx=150, laufy=163),
    }  # 60 fields out, heading for our building
    w.schritt(feind, gebaeude)
    assert any(
        "halten" in b and b["halten"].get("x") == 150 and b["halten"].get("y") == 163
        for b in gesendet
    )
    assert not w.weg.fuehrt(60) and not w.weg.fuehrt(61)
    assert w.absicht[60][:3] == (Action.DEFEND, "(150,163)", "intercept_at_enemy_destination")


# ---- collecting a round and the Lenker -------------------------------------------------------------------------------
class _Modul:
    def __init__(self, absicht):
        self.absicht = absicht


class _Raid:
    def __init__(self, **module):
        self.module = module

    def absichten(self):
        return self.module


def test_collect_round_merges_modules_paths_and_names_the_units_without_order():
    log = UnitLog(1)
    w = W.Wegfuehrung(1)
    L = {1: _e(1, 71, 100, 100), 2: _e(1, 24, 160, 160), 3: _e(1, 74, 100, 100)}
    w.fuehre(1, "gebaeude", 7, "brandtrupp")
    w.schritt(L, {7: _e(2, 3, 200, 100)}, Befehle())
    raid = _Raid(brandtrupp={1: (Action.SET_FIRE, "B7", "best_value_per_distance", {"typ": 3})})
    lines = UL.collect_round(
        log,
        700,
        L,
        {},
        waechter=_Modul({2: (Action.HOLD_POST, None, "start_post", {})}),
        raid=raid,
        wegf=w,
    )
    assert any(
        z.startswith(
            "UNIT t=700 1 (A_SLAVE 71) brandtrupp SET_FIRE target=B7 reason=best_value_per_distance path=walking"
        )
        for z in lines
    )
    assert (
        "UNIT t=700 2 (E_SPEAR 24) waechter HOLD_POST reason=start_post path=- expect=stays_at_point"
        in lines
    )
    assert lines[-1] == "UNIT_NO_ORDER t=700 1: 3 (A_HARCHER 74) nobody"


def test_lenker_collects_the_log_after_the_wegfuehrung_and_writes_it_into_the_position_log():
    with open(os.path.join(QUELLE, "runtime", "live", "erstes_spiel.py"), encoding="utf-8") as f:
        t = f.read()
    assert "ulog = UnitLog(SP)" in t
    i_weg = t.index("wegf.schritt(L, G, befehl)")
    i_log = t.index(
        'collect_round(ulog, st["t"], L, G, w, graben, trupp, raid_e if raid_laeuft else None, wegf)'
    )
    assert i_weg < i_log < t.index("lage.intents = ulog.table()")


def _abzug(tmp_path, monkeypatch):
    lb, gb = tmp_path / "lagebild.txt", tmp_path / "gebaeude.txt"
    lb.write_text("tick 500\nnr besitzer typ x y\n7 1 74 155 281\n", encoding="utf-8")
    gb.write_text("nr besitzer typ x y\n", encoding="utf-8")
    wa = ModuleType(
        "selfaware.micro.tasks.waechter"
    )  # the real Waechter needs a game instance - here it only names two files
    wa.LAGEBILD, wa.GEBAEUDEDATEI = str(lb), str(gb)
    monkeypatch.setitem(sys.modules, "selfaware.micro.tasks.waechter", wa)
    return tmp_path / "lage.jsonl.gz"


def test_position_log_writes_the_table_into_the_next_line(tmp_path, monkeypatch):
    import selfaware.telemetry.lageprotokoll as LP

    p = _abzug(tmp_path, monkeypatch)
    lp = LP.Lageprotokoll(str(p))
    lp.schreibe({"t": 500})
    log = UnitLog(1)
    log.report(7, "reiterjagd", Action.ATTACK_UNIT, "U30", "worker_in_range")
    log.close_round(500, {7: _e(1, 74)})
    lp.intents = log.table()
    lp.schreibe({"t": 545})
    lp.schreibe({"t": 590})
    with gzip.open(p, "rt", encoding="utf-8") as f:
        z = [json.loads(r) for r in f]
    assert "intents" not in z[0] and "intents" not in z[2]
    tick, rows = LP.intents_lesen(z[1])
    assert (
        tick == 500
        and rows[7]["action"] == "ATTACK_UNIT"
        and rows[7]["reason"] == "worker_in_range"
    )
    assert LP.intents_lesen(z[0]) == (None, {})


def test_an_assassin_does_not_take_back_a_worker_it_let_go():
    """Partie 12.11. 22:44: assassin 418 let worker 327 go ("dauert zu lange") and took it along again at once - 495 ticks at the
    quarry without damage. Real take-along logic: let go after ARBEITER_ZEIT, then blocked for ARBEITER_SPERRE ticks."""
    try:
        import selfaware.micro.tasks.assassinen as AS
    except RuntimeError as ex:
        pytest.skip(str(ex))

    def e(nr, owner, typ, x, y, **k):
        d = {
            "nr": nr,
            "gruppe": 0,
            "besitzer": owner,
            "typ": typ,
            "x": x,
            "y": y,
            "leben": 10000,
            "zustand": 1,
            "zielart": 0,
            "zieleinheit": 0,
            "laufx": x,
            "laufy": y,
            "ladung": 0,
            "arbeitsplatz": 0,
            "erreichbar": 1,
            "nahziel": -1,
            "nahangreifer": -1,
        }
        d.update(k)
        return d

    a = AS.Einzeln(1)
    L = {
        1: e(1, 1, 55, 100, 100, leben=150000),
        418: e(418, 1, 73, 216, 36, leben=10490),
        327: e(327, 2, 7, 214, 36),
        60: e(60, 2, 55, 330, 100, leben=150000),
    }
    a.aufnehmen([418])
    genommen = []
    for t in range(1000, 1000 + 12 * 50, 50):
        erg = a.schritt(L, {}, sichere_orte=[(100, 100)], tick=t)
        ev = erg[0] if isinstance(erg, tuple) else erg
        genommen += [(t, z) for z in ev if z.startswith("ARBEITER 418")]
    texte = [z for _t, z in genommen]
    assert any("nimmt Arbeiter 327" in z for z in texte) and any(
        "laesst Arbeiter 327" in z for z in texte
    )
    erst_gelassen = next(t for t, z in genommen if "laesst Arbeiter 327" in z)
    assert not any("nimmt Arbeiter 327" in z for t, z in genommen if t > erst_gelassen)
