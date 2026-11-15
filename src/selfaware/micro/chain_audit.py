# -*- coding: utf-8 -*-
"""Chain audit per order (B-182; Daniel 2026-11-12 22:34: "das ist der Vorteil wenn wir die komplette Chain auditen - uns faellt
sofort auf wenn sie bricht. Wegberechnung -> Kern bekommt Befehle -> Ausfuehrung -> Aktion im Spiel").

Every unit order that leaves the Lenker is followed through the chain:
  1. planned  - a module decided it (the unit log, micro/unit_log.py, has owner, intent and reason)
  2. sent     - it left through a channel: "module" (befehl.json -> logik.lua, seen in befehl.sende after the lord lock) or "ring"
                (order ring of the Rust core, execution/kernweg.py); the ring also reports its own result per order
                (angenommen, abgesetzt, wirkt / wirkt nicht / verfallen / doppelt / fremd ...)
  3. taken    - the game shows it: walk and hold -> walk target (laufx, laufy) at the point; attack unit -> the target in
                zieleinheit, nahziel or the core's schusseinheit; attack building -> zielgebaeude (shooters), the core's attack tile
                (mauerx, mauery, melee) or the walk target at the building; dig -> attack tile at the field or target kind 6
  4. acting   - the unit gets closer to its target, or is there
A break is reported once per order as a "CHAIN" line. What is measured is the game state, so the words are "not seen" and
"no progress", never "refused"; summary() counts the orders per kind, channel and link. Game 19
(2026-11-12 21:03) is why: the core ring said "wirkt nicht" for all 25 building attacks of the assassins, and assassin 475 stood
610 ticks while the module believed it raided. TAKE_TICKS, ACT_TICKS and the distances are self-set, not measured.
Zigzag orders of the core (AUSWEICHEN) are not followed yet.
"""

import collections
import json
import os

import selfaware.services.laufmodell as LM
import selfaware.services.sicht as sicht
import selfaware.services.spielwerte as SW
from selfaware.micro.unit_log import type_name

TAKE_TICKS = 150  # so many ticks after sending, the game must show the order
ACT_TICKS = 300  # so many ticks without a step closer to the target, while not there: not acting
# Attack chain (Daniel 12.11. 22:55: "Ziel waehlen -> Am Ziel (erkannt sonst Pause) -> sollte instant Angriffsanimation starten
# (sonst Pause) -> fuehrt erste Angriffsanimation aus -> Schaden (sonst Pause)"; plan section 8). Attack states of the game:
WALKING = 101
# Digging (2026-11-13 22:05, game 20261113_220249 + the 5 games of 12.11.): state 124 is shown only by moat diggers - our spearmen
# 24 (787 + 39 unit rounds, all 39 of 13.11. at the moat) and the enemy's type 25 (2227) - and the game seems to hand each digger the
# next planned moat tile itself (not measured one by one), so a digger in this state works even when it is not closer to the tile it was sent to (S124).
DIGGING = 124
ATTACK_STATES = {"attack_unit": 106, "attack_building": 107}  # melee
SHOOTER_STATES = (
    4,
    5,
    6,
)  # aim -> shot -> reload, 0 for one tick between two shots (measured 2026-11-12 23:27)
# Measured per unit type in the map editor on instance 2, per tick from the core (tools/experiments/schlag_messen.py,
# data/research/schlag_messung_20261112_*.jsonl, 2026-11-12 23:21-23:40), plan section 8:
#   swing       melee against a building: ticks between two hits; the hit lands when the animation frame wraps to 0, the attack
#               state starts 1-2 ticks after the order at the target, the first hit 0-3 ticks before a full swing (a hut, 200 life)
#   building    damage per hit against a building (the assassin 75 also against the woodcutter hut and the quarry of game 20)
#   unit        melee against a unit: damage per TICK against E_SPEAR 24 - a melee fight hurts every tick from the contact on, the
#               core shows state 106 3-11 ticks after the first loss (9 types, from 8 fields)
#   resend_gap  ticks without damage after a second identical attack order to the fighting unit (9 of 9 melee types: the unit walks
#               again, state 101 at +3, no damage from +2 for 4 / 8 / 12 ticks)
#   fire        fire setters against a building: ticks from the attack start to the fire (slave 370-372 in 4 trials on a hut, the
#               first loss at 477 on the woodcutter hut; fire thrower 493 in one); a burning building loses 4 life every 20 ticks
#   cycle       shooters: ticks per shot (aim 4 -> shot 5 -> reload 6 -> 0); against a building 1 damage per hit and most shots
#               without any loss, against a unit one hit per cycle (a standing assassin 12 fields away)
#   first_shot  shooters against a unit: ticks from the aim start to the first loss, 12 fields away (+1.6 ticks per field further:
#               A_ARCHER 80 -> 109 and A_HARCHER 72 -> 99 at 30 fields)
ATTACK = {
    73: {"swing": 93, "building": 75, "unit": 120, "resend_gap": 4},
    75: {"swing": 96, "building": 100, "unit": 125, "resend_gap": 8},
    24: {"swing": 48, "building": 10, "unit": 25, "resend_gap": 4},
    25: {"swing": 28, "building": 40, "unit": 30, "resend_gap": 8},
    26: {"swing": 48, "building": 80, "unit": 70, "resend_gap": 4},
    27: {"swing": 60, "building": 100, "unit": 150, "resend_gap": 12},
    28: {"swing": 72, "building": 100, "unit": 150, "resend_gap": 4},
    37: {"swing": 24, "building": 20, "unit": 50, "resend_gap": 8},
    71: {"fire": 477, "unit": 10, "resend_gap": 4},
    22: {"cycle": 129, "building": 1, "first_shot": 122},
    23: {"cycle": 228, "building": 1, "first_shot": 176},
    70: {"cycle": 90, "building": 1, "first_shot": 80},
    72: {"cycle": 56, "building": 1, "first_shot": 74},
    74: {"cycle": 78, "building": 1, "first_shot": 72},
    76: {
        "cycle": 141,
        "building": 1,
        "fire": 493,
        "first_shot": 359,
    },  # first_shot 80 and 359 in 2 trials at 8 fields
}
SOURCE = "measured in the editor 2026-11-12 23:21-23:40 (schlag_messen.py)"
FIRE_TICK = 20  # a burning building loses life every 20 ticks (measured): the first loss after the fire start
UNIT_LOSS_TICKS = 13  # melee against a unit: the target must lose life within the longest measured gap (12) + 1 tick
# Link 2 (walking): the core's path index (wegindex) moves one field per field walked (measured 2026-11-13 00:20, 20 of 20); the
# game's own speed value (tempo) of the unit already counts water, mud and climbing (calculateUnitMovementSpeed, services/
# laufmodell.py) - one move every (speed + run + 1) ticks, (run + 1) of 8 micro steps per field. A walk that falls SLOW_FIELDS
# fields behind that since it was last on time is blocked or crowded. SLOW_FIELDS self-set, above the measured error of the model
# (12 walks on Paradise Plains: arrival -12 % .. +6 % for foot units, single fields up to 45 ticks off).
SLOW_FIELDS = 4
# Daniel 13.11.2026 23:40 "Ja, mitrechnen": with the terrain map the limit grows with the way - a walk is slow only when it is
# slower than the slowest quarter of the measured walks of its type (game 9: spearman 330, 54 ticks behind after 75 fields = 6 %;
# spearmen walk at 0.95 of the model in the median, 0.87 at the slowest quarter, S131). The measurement lives in a data file; types
# without one keep the fixed SLOW_FIELDS limit.
STREUUNG_DATEI = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "..",
    "..",
    "data",
    "research",
    "lauf_streuung_20261113.json",
)


def _streuung(pfad=STREUUNG_DATEI):
    """type -> slowest quarter (model ticks / walked ticks) of the measured walks; {} without the file."""
    try:
        with open(pfad, encoding="utf-8") as f:
            return {int(t): v["p25"] for t, v in json.load(f)["je_art"].items()}
    except (OSError, ValueError, KeyError):
        return {}


STREUUNG = _streuung()
WORKER_TYPES = set(range(1, 22)) | set(
    range(31, 37)
)  # population: peasants and workers (UT_PEASANT 1 .. UT_INNKEEPER 36)
SHOT_CHECKED = 12  # fields: a shot is checked for its hit up to here (5 of 5 shots hit at 12 fields, one trial per shooter;
#                        at 30 fields E_ARCHER and T23 hit 0 of 4, A_ARCHER and A_HARCHER 3 of 3; A_SLINGER 0 of 4 at 17)
# Shots beyond SHOT_CHECKED: type -> (fields, hits, shots) of those editor trials. Game 5 of 13.11. (S126): four E_ARCHER shot the
# quarry mason U355 from 30-36 fields (Schach) for 302 ticks, its life stayed 10000.
FAR_SHOTS = {22: (30, 0, 4), 23: (30, 0, 4), 70: (30, 3, 3), 74: (30, 3, 3), 72: (17, 0, 4)}
FAR_SHOTS_DUE = 4  # the trial size: so many shots beyond SHOT_CHECKED before "no damage" is said
FAR_TICKS_PER_FIELD = 1.6  # the first hit comes later per field beyond 12 (A_ARCHER 80 -> 109, A_HARCHER 72 -> 99 at 30 fields)
NEAR = 3  # fields (Schach): a walk target or a position counts as "at the point"
BUILDING_NEAR = (
    2  # fields from the footprint: an attack tile or walk target counts as "at the building"
)
MELEE_REACH = 2  # fields: melee attacker at its target unit
BUILDING_REACH = 2  # fields from the footprint (corner at x, y, edge sicht.GROESSE - measured 23:20): a melee attacker
#                        stands next to it (the hut trials: 1 field), one field of slack (the core field of a unit can be one off)
# kern_leitung order kinds: LAUF 17, ANGRIFF_EINHEIT 4, ANGRIFF_GEBAEUDE 9; LAUF_DURCHSETZEN 18 (S155) is a walk the core repeats in a fight
RING_KINDS = {17: "walk", 18: "walk", 4: "attack_unit", 9: "attack_building"}


def _schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def _point(p):
    return "(%d,%d)" % (int(p[0]), int(p[1]))


def shot_deadline(typ, d):
    """Ticks from the aim start until a shooter of this type must have hurt a unit d fields (Schach) away: two shots up to
    SHOT_CHECKED, FAR_SHOTS_DUE shots beyond (the first hit FAR_TICKS_PER_FIELD later per field); None when unmeasured."""
    m = ATTACK.get(typ) or {}
    if "first_shot" not in m:
        return None
    if d <= SHOT_CHECKED:
        return m["first_shot"] + m["cycle"]
    if typ not in FAR_SHOTS:
        return None
    return (
        m["first_shot"]
        + int(FAR_TICKS_PER_FIELD * (d - SHOT_CHECKED) + 0.5)
        + (FAR_SHOTS_DUE - 1) * m["cycle"]
    )


ATTACK_ACTIONS = ("ATTACK_UNIT", "DEFEND", "MOVE_TO_ATTACK", "ATTACK_BUILDING", "SET_FIRE")
POINT_ACTIONS = ("MOVE_TO_STAGING", "GATHER", "RETREAT", "FLEE", "GAME_PATH")
STAY_ACTIONS = ("WAIT_STAGING", "HOLD_POST")


def expectation(action, typ, pos=None, goal=None, kind=None):
    """The result a unit's order should bring, from the same measured tables the chain check checks (Daniel 13.11.2026 22:45:
    "jede Einheit muss ja sagen was sie macht und was das erwartete ergebenis ist"). kind: "unit", "building" or "point" (the
    target), goal its place, pos the unit's. One word without spaces for the UNIT line; UNMEASURED where nothing is measured."""
    d = _schach(pos, goal) if pos is not None and goal is not None else None
    m = ATTACK.get(typ) or {}
    if action in ATTACK_ACTIONS:
        pre = "reach_then_" if action == "MOVE_TO_ATTACK" else ""
        if kind == "building" or action == "SET_FIRE":
            if "fire" in m:
                return pre + "fire_%dt_after_attack_start(measured)" % m["fire"]
            if "cycle" in m:
                return pre + "useless_1_damage_per_hit_most_miss(measured)"
            if "swing" in m:
                return pre + "hit_every_%dt_%d_damage(measured)" % (m["swing"], m["building"])
            return pre + "UNMEASURED_building_attack"
        if "cycle" in m:
            if d is None:
                return pre + "hit_UNMEASURED_distance_unknown"
            far = FAR_SHOTS.get(typ)
            if d > SHOT_CHECKED and far is not None and far[1] == 0 and d >= far[0]:
                return pre + "no_hit_expected_from_%df(measured_0_of_%d_at_%d)" % (
                    d,
                    far[2],
                    far[0],
                )
            t = shot_deadline(typ, d)
            if t is None:
                return pre + "hit_UNMEASURED_from_%df" % d
            return pre + "damage_within_%dt_from_%df(measured)" % (t, d)
        if "unit" in m:
            return pre + "damage_within_%dt_of_contact(measured)" % UNIT_LOSS_TICKS
        return pre + "UNMEASURED_attack"
    if action in POINT_ACTIONS:
        if d is None:
            return "arrive_UNMEASURED_distance_unknown"
        if typ not in LM.TYPES:
            return "arrive_in_%df_speed_UNMEASURED" % d
        return "arrive_in_~%dt_for_%df_flat(model)" % (
            int(d * LM.flat_ticks_per_field(typ) + 0.5),
            d,
        )
    if action in STAY_ACTIONS:
        return "stays_at_point"
    if action == "WAIT_SAFE_TARGET":
        return "waits_until_a_safe_target"
    if action == "DIG":
        return "digs_moat_tiles(time_UNMEASURED)"
    if action == "NO_ORDER":
        return "none"
    return "UNMEASURED"


def _gap(pos, g):
    """Fields between a position and the footprint of building g (0 = on it); corner at (x, y), edge from sicht.GROESSE."""
    b = sicht.GROESSE.get(g.get("typ"), 1) or 1
    dx = max(g["x"] - pos[0], 0, pos[0] - (g["x"] + b - 1))
    dy = max(g["y"] - pos[1], 0, pos[1] - (g["y"] + b - 1))
    return max(dx, dy)


class _Order:
    def __init__(self, unit, tick, channel, kind, target):
        self.unit, self.tick, self.channel, self.kind, self.target = (
            unit,
            tick,
            channel,
            kind,
            target,
        )
        self.ring, self.ring_result = None, None
        self.typ = None  # type of the unit at the first check - the game gives numbers of dead units out again
        self.taken = None  # tick at which the game showed the order
        self.best, self.best_tick = None, None
        self.flags = set()
        self.reach_tick = (
            None  # first check in reach, not walking - the attack state must start (link 3)
        )
        self.attack_tick, self.attack_life = (
            None,
            None,
        )  # first check with the attack state, life of the target then
        self.looks = []  # (frame, frame cycle) at each check in the attack state - does the animation run (link 4)
        self.reach_life = None  # life of the target at the first check in reach (melee hurts a unit before state 106 shows)
        self.resent = None  # tick of an identical order while the unit fights (costs ATTACK[typ]["resend_gap"] ticks)
        self.walk = None  # link 2: (tick, path index, path length, position) at the last check
        self.walk_exp = self.walk_done = (
            0.0  # fields due by the game's speed value / fields walked, since the path began
        )
        self.walk_lag = self.walk_need = (
            0.0  # terrain map: delay / model ticks of the unit's way (_Trail)
        )
        self.slowed = 0  # checks with a speed value above flat ground (terrain)
        self.fight = (
            None  # opponent of a fight the order did not ask for, seen at the last check (S147)
        )

    def same(self, kind, target):
        return self.kind == kind and self.target == target


class _Trail:
    """Link 2 with a terrain map: ONE unit while it walks without a break, over its orders (game 14 of 14.11.2026, S138: spearman
    334 got a new walk order right after a ford; the check began the model anew - dry, and from move count 0 - and stopped the game;
    over the whole way, with move count 2 to 5, it hit every round within 2-7 ticks). The model walks go on over the orders:
    the unit's wetness, climb height and move count stay. The clock does not: at a new path it is set anew (anker) - the fields
    between the last check and the new path are only the straight line between two positions (the path index of the old path at
    the switch is unknown), on a winding way too few; carried over, that delay stayed for the rest of the way (replay of games
    13 and 14: 13 alarms where the game had none). One model walk per move count (unknown, the game counts the moves over the
    unit's life); 'on time' is the best point since the path began, for each of them."""

    def __init__(self, typ, tick, pos, tile):
        self.t0, self.last, self.walking, self.orders = tick, (tick, pos), True, set()
        self.walkers = [LM.Walker(typ, pos, tile, 0, p) for p in range(LM.UPDATE)]
        self.base = [0.0] * LM.UPDATE
        self.need0 = [0.0] * LM.UPDATE  # model ticks at the start of the current path
        self.anchor, self.fields0 = (
            tick,
            0,
        )  # tick and fields walked at which the current path began

    def add(self, fields):
        for w in self.walkers:
            w.add(fields)

    def _roh(self, tick, typ):
        for p, w in enumerate(self.walkers):
            z = w.times
            need = z[-1] if z else 0
            # the unit is somewhere inside its current field: up to one more field of the model's time is no delay (game 13: in
            # the ford one field took 26-36 ticks, the check saw the unit at the end of such a field and called it 'behind')
            im_feld = (z[-1] - z[-2]) if len(z) >= 2 else LM.flat_ticks_per_field(typ)
            yield p, need, (tick - self.t0) - need - im_feld

    def anker(self, tick, typ):
        """A new path: from here on time again - the unit's state goes on."""
        self.anchor, self.fields0 = tick, len(self.walkers[0].fields) - 1
        for p, need, roh in self._roh(tick, typ):
            self.base[p], self.need0[p] = roh, need

    def lag(self, tick, typ):
        """-> (delay, model ticks since the path began) of the most favourable move count."""
        best = None
        for p, need, roh in self._roh(tick, typ):
            self.base[p] = min(self.base[p], roh)
            if best is None or roh - self.base[p] < best[0]:
                best = (roh - self.base[p], need - self.need0[p])
        return best


class ChainAudit:
    def __init__(self, sp, tile=None):
        self.sp = sp
        # link 2 with a terrain map (tile(x, y) -> (LogicLayer, MacroLayer, height), tools/experiments/gelaende_erheben.tile_function):
        # the walk is measured against the terrain of the fields it crossed (Daniel 13.11.2026 23:35 "Ja, umbauen" - game 8: the
        # speed value read once a round missed the mud between two reads, S129); without one, the speed value of each round
        self.tile = tile
        self.trails = {}  # unit -> _Trail (terrain map only)
        self.prev_check = self._now = (
            None  # ticks of the check before this one and of this one: a trail goes on only from there
        )
        self.tick = (
            0  # the Lenker sets it each round; module-channel orders take it as their sending tick
        )
        self.orders = {}  # unit -> _Order (the latest order of each unit)
        self.by_ring = {}  # ring slot -> _Order
        self.counts = collections.Counter()
        self.unmeasured = set()  # (type, target class) without measured attack timing, said once

    # ---- 2. sent ---------------------------------------------------------------------------------------------------------
    def _new(self, unit, channel, kind, target, tick):
        alt = self.orders.get(unit)
        if alt is not None and alt.same(kind, target) and alt.channel == channel:
            if alt.attack_tick is not None and alt.resent is None:
                alt.resent = tick  # the unit fights already: the order makes a melee unit walk again (measured 23:34)
            return (
                alt  # the same order again (a resend): the clock keeps running, nothing is hidden
            )
        o = _Order(unit, tick, channel, kind, target)
        self.orders[unit] = o
        self.counts[(kind, channel, "sent")] += 1
        return o

    def from_module(self, paket):
        """Observer for befehl.sende: every unit order that goes to the game module (after the lord lock)."""
        cmds = paket.get("befehle") if isinstance(paket, dict) and "befehle" in paket else [paket]
        for c in cmds or ():
            if not isinstance(c, dict):
                continue
            a, h = c.get("angriff"), c.get("halten")
            if isinstance(a, dict) and a.get("einheiten"):
                if "lauf" in a:
                    kind, target = "walk", (int(a["lauf"][0]), int(a["lauf"][1]))
                elif "ziel" in a:
                    kind, target = "attack_unit", int(a["ziel"])
                elif "gebaeude" in a:
                    kind, target = "attack_building", int(a["gebaeude"])
                elif "graben" in a:
                    kind, target = "dig", (int(a["graben"][0]), int(a["graben"][1]))
                else:
                    continue
                for n in a["einheiten"]:
                    self._new(int(n), "module", kind, target, self.tick)
            elif isinstance(h, dict) and h.get("nr") and "x" in h:
                for n in h["nr"]:
                    self._new(int(n), "module", "hold", (int(h["x"]), int(h["y"])), self.tick)
            elif isinstance(h, dict) and h.get("los"):
                for n in h["los"]:  # hold released: no expectation any more
                    o = self.orders.get(int(n))
                    if o is not None and o.kind == "hold":
                        del self.orders[int(n)]

    def from_guard(self, gebaeude, ziel, einheiten):
        """Hook of the fight guard (execution/kampfschutz.ERFUELLT): an attack on unit (or building) ziel held back because these
        units fight exactly that target already. It becomes their order - channel "guard", not a resend (it never reached the
        game). Without it the unit's older order stayed (game 16 of 14.11.2026, S142: the melee raid took the worker its spearman
        fought as target, the guard held the attack back, and the walk order before it would have stopped the game on 'FIGHTS
        INSTEAD OF WALKING')."""
        kind, target = ("attack_building" if gebaeude else "attack_unit"), int(ziel)
        for n in einheiten:
            n = int(n)
            alt = self.orders.get(n)
            if alt is not None and alt.same(kind, target):
                continue  # the unit follows that order already (S118: the same attack again)
            self.trails.pop(n, None)
            o = self.orders[n] = _Order(n, self.tick, "guard", kind, target)
            # S147 (game 19, 331): the guard saw the fight on this round's state - taken now; registered as unseen, the next check
            # found the unit already fighting another worker and stopped the game on NOT SEEN
            o.taken, o.best, o.best_tick = self.tick, float("inf"), self.tick
            self.counts[(kind, "guard", "held")] += 1
            self.counts[(kind, "guard", "taken")] += 1

    def from_ring(self, ring, unit, art, a, b, tick):
        """Observer for kernweg.Kernweg: an order placed in the core's order ring."""
        kind = RING_KINDS.get(art)
        if kind is None:
            return
        target = (int(a), int(b)) if kind == "walk" else int(a)
        o = self._new(int(unit), "ring", kind, target, tick)
        if o.ring is not None:
            self.by_ring.pop(o.ring, None)
        o.ring = ring
        self.by_ring[ring] = o

    def ring_result(self, ring, name):
        """Final result of a ring order as the core reports it (kern_leitung.ERGEBNIS_NAMEN)."""
        o = self.by_ring.pop(ring, None)
        if o is not None:
            o.ring_result = str(name).replace(" ", "_")
            self.counts[(o.kind, "ring", "ring_" + o.ring_result)] += 1

    # ---- 3. taken, 4. acting -----------------------------------------------------------------------------------------------
    def _target_pos(self, o, L, G):
        """Point of the target (a building: the middle of its footprint), None when the target is gone."""
        if o.kind in ("walk", "hold", "dig"):
            return o.target
        if o.kind == "attack_unit":
            z = L.get(o.target)
            if z is None or z.get("besitzer") in (None, 0, self.sp) or z.get("leben", 1) <= 0:
                return None
            return (z["x"], z["y"])
        g = G.get(o.target)
        if g is None or g.get("besitzer") in (None, 0, self.sp) or g.get("leben", 1) <= 0:
            return None
        b = sicht.GROESSE.get(g.get("typ"), 1) or 1
        return (g["x"] + b // 2, g["y"] + b // 2)

    def _dist(self, o, pos, ziel, G):
        """Fields to the target: to a building's footprint, else to the point."""
        if o.kind == "attack_building":
            return _gap(pos, G[o.target])
        return _schach(pos, ziel)

    @staticmethod
    def _taken(o, e, k, ziel, pos, g=None):
        lauf = (e.get("laufx", 0) or 0, e.get("laufy", 0) or 0)
        tile = (k.get("mauerx", 0) or 0, k.get("mauery", 0) or 0)
        if o.kind in ("walk", "hold"):
            return _schach(lauf, ziel) <= NEAR or _schach(pos, ziel) <= NEAR
        if o.kind == "attack_unit":
            return o.target in (
                e.get("zieleinheit"),
                e.get("nahziel"),
                k.get("schusseinheit"),
                k.get("zieleinheit"),
            )
        if (
            o.kind == "attack_building"
        ):  # melee: the core tile is a tile of the building; shooters: zielgebaeude (measured 23:44)
            return (
                e.get("zielgebaeude") == o.target
                or (tile != (0, 0) and _gap(tile, g) <= BUILDING_NEAR)
                or (lauf != (0, 0) and _gap(lauf, g) <= BUILDING_NEAR)
                or _gap(pos, g) <= BUILDING_REACH
            )
        return (
            k.get("zielart") == 6
            or e.get("zielart") == 6
            or (tile != (0, 0) and _schach(tile, ziel) <= NEAR)
        )

    @staticmethod
    def _reach(o, typ):
        if o.kind in ("walk", "hold", "dig"):
            return NEAR
        r = SW.erfassen(typ)
        if o.kind == "attack_unit":
            return int(r) if r is not None else MELEE_REACH
        return BUILDING_REACH if r is None else int(r)

    def _line(self, tick, o, typ, text):
        return "CHAIN t=%s %d (%s) %s %s via %s: %s" % (
            tick,
            o.unit,
            type_name(typ),
            o.kind,
            _point(o.target)
            if isinstance(o.target, tuple)
            else ("U%d" % o.target if o.kind == "attack_unit" else "B%d" % o.target),
            o.channel,
            text,
        )

    def check(self, tick, L, G, eigen=None):
        """One round: follows every open order through links 3 and 4. eigen: {unit: core fields} of own units (mauerx, mauery,
        schusseinheit, zieleinheit, zielart). Returns the CHAIN lines of new breaks."""
        eigen = eigen or {}
        lines = []
        self.prev_check, self._now = self._now, tick
        for n, o in list(self.orders.items()):
            e = L.get(n)
            if (
                e is None
                or e.get("besitzer") != self.sp
                or e.get("leben", 1) <= 0
                or (o.typ is not None and e.get("typ") != o.typ)
            ):
                self._drop(n, o)
                continue
            if o.typ is None:
                o.typ = e.get("typ")
            ziel = self._target_pos(o, L, G)
            if ziel is None:  # target dead or burned down: the order is over
                self._drop(n, o)
                continue
            pos = (e["x"], e["y"])
            k = eigen.get(n, {})
            # S147 (game 19, 330; Daniel 23:10 "Ja, beide bauen"): a fight the order did not ask for (the game started it) - the first
            # check that sees it does not judge: the check runs at the start of the round, the module can take the fight over only
            # later in it (the melee raid did, the fight guard held its attack back - the walk order before it stopped the game)
            gegner = self._kampf_ausser_auftrag(o, e, k)
            if gegner is None:
                o.fight = None
            elif o.fight != gegner:
                o.fight = gegner
                if o.kind == "walk":
                    self._walk(
                        tick, o, e, k, L, pos, judge=False
                    )  # the unit's way goes on, nothing is judged
                continue
            if o.taken is None:
                if self._taken(
                    o, e, k, ziel, pos, G.get(o.target) if o.kind == "attack_building" else None
                ):
                    o.taken = tick
                    o.best, o.best_tick = self._dist(o, pos, ziel, G), tick
                    self.counts[(o.kind, o.channel, "taken")] += 1
                    # seen: the same round goes on to reach and damage (the damage clock starts when it is in reach)
                elif tick - o.tick >= TAKE_TICKS and "not_seen" not in o.flags:
                    o.flags.add("not_seen")
                    self.counts[(o.kind, o.channel, "not_seen")] += 1
                    lines.append(
                        self._line(
                            tick,
                            o,
                            e.get("typ"),
                            "NOT SEEN in the game state %d ticks after sending (checked: walk "
                            "target, attack target, core tile) - ring %s, game walk target %s, attack target U%s, core tile %s, position %s"
                            % (
                                tick - o.tick,
                                o.ring_result or ("open" if o.channel == "ring" else "-"),
                                _point((e.get("laufx", 0) or 0, e.get("laufy", 0) or 0)),
                                e.get("zieleinheit") or k.get("schusseinheit") or 0,
                                _point((k.get("mauerx", 0) or 0, k.get("mauery", 0) or 0)),
                                _point(pos),
                            ),
                        )
                    )
                if o.taken is None:
                    self._walk(tick, o, e, k, L, pos, judge=False)  # the unit's way goes on (S138)
                    continue
            if (
                o.resent is not None
                and "resend" not in o.flags
                and ATTACK.get(o.typ, {}).get("resend_gap")
            ):
                o.flags.add("resend")
                self.counts[(o.kind, o.channel, "resend_fighting")] += 1
                lines.append(
                    self._line(
                        tick,
                        o,
                        e.get("typ"),
                        "RESEND WHILE FIGHTING - the same order again at tick %d while the unit "
                        "fought since tick %d: a melee unit walks again and does no damage for %d ticks (measured "
                        "for this type, %s)"
                        % (o.resent, o.attack_tick, ATTACK[o.typ]["resend_gap"], SOURCE),
                    )
                )
            d = self._dist(o, pos, ziel, G)
            if d <= self._reach(o, e.get("typ")):
                if "arrived" not in o.flags:
                    o.flags.add("arrived")
                    self.counts[(o.kind, o.channel, "arrived")] += 1
                if o.kind in (
                    "walk",
                    "hold",
                    "dig",
                ):  # dig: at the moat the game hands out the tiles itself (S124)
                    self._drop(n, o)
                elif o.kind in ("attack_unit", "attack_building"):
                    lines += self._attack(tick, o, e, L, G)
                continue
            o.reach_tick, o.reach_life = None, None
            if o.attack_tick is not None and "damage" not in o.flags:
                o.attack_tick, o.attack_life, o.looks = (
                    None,
                    None,
                    [],
                )  # out of reach again: the clocks start anew
            if (
                o.kind == "dig" and e.get("zustand") == DIGGING
            ):  # digs the moat: the order has arrived (game 3 of 13.11.: a
                self.counts[(o.kind, o.channel, "digging")] += (
                    1  # digger walks on to the next tile and away from the first)
                )
                self._drop(n, o)
                continue
            lines += self._walk(tick, o, e, k, L, pos)
            if d < o.best:
                o.best, o.best_tick = d, tick
            elif tick - o.best_tick >= ACT_TICKS and "no_progress" not in o.flags:
                o.flags.add("no_progress")
                self.counts[(o.kind, o.channel, "no_progress")] += 1
                lines.append(
                    self._line(
                        tick,
                        o,
                        e.get("typ"),
                        "NO PROGRESS - seen at tick %d, no step closer for %d ticks "
                        "(%d fields left, position %s)"
                        % (o.taken, tick - o.best_tick, d, _point(pos)),
                    )
                )
        return lines

    def _attack(self, tick, o, e, L, G):
        """Links 3-5 for an attacker in reach (Daniel 12.11. 22:55: at the target -> the attack starts at once -> the animation
        runs -> damage, each else a stop; plan section 8). The checks run once per Lenker round, so every deadline is a measured
        time (ATTACK), counted from the first round that saw the attack state - never earlier than the real start."""
        state, m = e.get("zustand"), ATTACK.get(o.typ)
        shooter = m is not None and "cycle" in m
        states = SHOOTER_STATES if shooter else (ATTACK_STATES[o.kind],)
        target = L.get(o.target) if o.kind == "attack_unit" else G.get(o.target)
        life = (target or {}).get("leben")
        if o.attack_tick is None:
            if o.reach_life is None:
                o.reach_life = (
                    life  # kept until the unit leaves the reach: melee hurts before state 106 shows
                )
            if o.reach_tick is None:
                o.reach_tick = tick
        if o.attack_tick is None and state in states:
            o.attack_tick, o.attack_life, o.looks = tick, life, []
            self.counts[(o.kind, o.channel, "attack_started")] += 1
        if o.attack_tick is not None and state in states and e.get("bild") is not None:
            o.looks.append(
                (e.get("bild"), e.get("bildzyklus"))
            )  # without the frame fields nothing is said about link 4
        base = o.reach_life if o.reach_life is not None else o.attack_life
        if life is not None and base is not None and life < base:
            if (
                "damage" not in o.flags
            ):  # melee hurts a unit from the contact on, before the core shows state 106
                o.flags.add("damage")
                self.counts[(o.kind, o.channel, "damage")] += 1
            return []
        if o.flags & {"damage", "no_damage", "no_attack", "useless"}:
            return []
        if o.attack_tick is None:  # link 3: the attack state starts at once (one round of slack)
            if state == WALKING or (shooter and state == 0):
                o.reach_tick = None  # the game still walks it in / a shooter between two shots
                return []
            if tick == o.reach_tick:
                return []
            o.flags.add("no_attack")
            self.counts[(o.kind, o.channel, "no_attack")] += 1
            return [
                self._line(
                    tick,
                    o,
                    e.get("typ"),
                    "ATTACK DID NOT START - in reach since tick %d, unit state %s, attack state %s "
                    "expected at once (measured: 1-3 ticks after the order at the target)"
                    % (o.reach_tick, state, "/".join(str(s) for s in states)),
                )
            ]
        if m is None:
            if (o.typ, o.kind) not in self.unmeasured:
                self.unmeasured.add((o.typ, o.kind))
                return [
                    "CHAIN_INFO t=%s %d (%s) %s: attack timing UNMEASURED for this type - links 4 and 5 not checked"
                    % (tick, o.unit, type_name(o.typ), o.kind)
                ]
            return []
        if o.kind == "attack_building" and shooter and "fire" not in m:
            o.flags.add("useless")
            self.counts[(o.kind, o.channel, "useless")] += 1
            return [
                self._line(
                    tick,
                    o,
                    e.get("typ"),
                    "NO USEFUL ATTACK - a shooter does 1 damage per hit to a building and most shots "
                    "miss (measured: E_ARCHER 5 losses of 1 life in 1,500 ticks); the target has %s life"
                    % life,
                )
            ]
        deadline, what = self._deadline(o, m, e, target)
        if deadline is None:
            if what and (o.typ, o.kind, what) not in self.unmeasured:
                self.unmeasured.add((o.typ, o.kind, what))
                return [
                    "CHAIN_INFO t=%s %d (%s) %s: link 5 not checked - %s"
                    % (tick, o.unit, type_name(o.typ), o.kind, what)
                ]
            return []
        if tick - o.attack_tick < deadline or life is None:
            return []
        o.flags.add("no_damage")
        looks, distinct = len(o.looks), len(set(o.looks))
        if looks >= 2 and distinct == 1:
            self.counts[(o.kind, o.channel, "animation_stands")] += 1
            return [
                self._line(
                    tick,
                    o,
                    e.get("typ"),
                    "ANIMATION STANDS - attack state since tick %d, frame %s cycle %s in all %d looks, "
                    "no damage after %s; the target's life is still %d"
                    % (o.attack_tick, o.looks[0][0], o.looks[0][1], looks, what, life),
                )
            ]
        self.counts[(o.kind, o.channel, "no_damage")] += 1
        ran = (
            "the animation ran: %d different frames in %d looks" % (distinct, looks)
            if looks >= 2
            else "animation not checked: %d looks with a frame in the attack state" % looks
        )
        return [
            self._line(
                tick,
                o,
                e.get("typ"),
                "NO DAMAGE AFTER %s - attack state since tick %d, the target's life is still %d "
                "(%s, unit state %s)" % (what, o.attack_tick, life, ran, state),
            )
        ]

    @staticmethod
    def _deadline(o, m, e, target):
        """Link 5: (ticks after the attack start, what is due) - or (None, why not checked)."""
        if o.kind == "attack_building":
            if "swing" in m:
                return m["swing"], "A SWING (measured %d ticks, %d damage per hit)" % (
                    m["swing"],
                    m["building"],
                )
            if "fire" in m:
                return (
                    m["fire"] + FIRE_TICK,
                    "THE FIRE (measured: burning %d ticks after the attack start, then 4 life every %d "
                    "ticks)" % (m["fire"], FIRE_TICK),
                )
            return None, None
        if "cycle" in m:
            d = _schach((e["x"], e["y"]), (target["x"], target["y"])) if target else None
            if "first_shot" not in m:
                return None, "first shot against a unit unmeasured"
            if d is None:
                return None, "shot distance unknown"
            if d > SHOT_CHECKED:
                far = FAR_SHOTS.get(o.typ)
                if far is None:
                    return (
                        None,
                        "shot from %d fields - beyond %d fields unmeasured for this type"
                        % (d, SHOT_CHECKED),
                    )
                return shot_deadline(
                    o.typ, d
                ), "%d SHOTS FROM %d FIELDS (measured beyond %d fields: %d of %d hit at %d)" % (
                    FAR_SHOTS_DUE,
                    d,
                    SHOT_CHECKED,
                    far[1],
                    far[2],
                    far[0],
                )
            return (
                m["first_shot"] + m["cycle"],
                "TWO SHOTS (measured: first hit %d ticks after the aim start at 12 fields, one "
                "shot every %d ticks)" % (m["first_shot"], m["cycle"]),
            )
        if "unit" in m:
            return (
                UNIT_LOSS_TICKS,
                "THE CONTACT (melee hurts every tick, measured %d per tick against E_SPEAR 24)"
                % m["unit"],
            )
        return None, None

    def _walk(self, tick, o, e, k, L, pos, judge=True):
        """Link 2 on the way (Daniel 12.11. 23:00: disruptions on the way - enemy units, terrain, the population that blocks):
        the path index must move as fast as the game's own speed value of the unit says. SLOW_FIELDS behind it since on time:
        one line with the units around it; a speed value above flat ground is the terrain (water, mud, climbing) - named, no
        break, the game counts it already. judge=False (the game does not show the order yet): with a terrain map the unit's way
        goes on, nothing is judged - else a new order seen one round late would cut the way again (S138)."""
        if not judge and self.tile is None:
            return []
        idx, n, v = k.get("wegindex"), k.get("weglaenge"), k.get("tempo")
        if idx is None or n is None or v is None or o.typ not in LM.TYPES or "slow_walk" in o.flags:
            return []
        base, run = LM.TYPES[o.typ]
        last, o.walk = o.walk, (tick, idx, n, pos)
        if judge and v > base:
            o.slowed += 1
        same_path = last is not None and last[2] == n and last[1] <= idx < n
        if self.tile is not None:
            # One model walk over the whole way (game 13, S137: cut into pieces - per round, or anew at each 'on time' - every
            # piece started with a head start and dry, the model ran ahead in a ford; over the whole recorded way it hit each field
            # within a few ticks) - and over a new order while the unit walks on (game 14, S138). The fields walked since the last
            # check: the straight line between the two positions - at least, also when the path index moved less (game 14: index
            # 4, the unit stood 5 fields on; cut to the index the model left out a field); a winding path has more steps than that
            # line - the extra steps count with the terrain of the last field.
            tr = self.trails.get(o.unit)
            walking = e.get("zustand") == WALKING
            if (
                idx >= n
                or tr is None
                or tr.last[0] != self.prev_check
                or not (same_path or (tr.walking and walking))
            ):
                self.trails[o.unit] = tr = _Trail(
                    o.typ, tick, pos, self.tile
                )  # a new way (or none left): a new window
                tr.walking = walking
                tr.orders.add(id(o))
                o.walk_done = o.walk_lag = o.walk_need = 0.0
                return []
            stueck = LM.gerade(tr.last[1], pos)
            if same_path:
                stueck += [stueck[-1]] * max(0, idx - last[1] + 1 - len(stueck))
            tr.add(stueck[1:])
            tr.last, tr.walking = (tick, pos), walking
            tr.orders.add(id(o))
            if not same_path:  # a new path: the clock anew, the unit's state goes on
                tr.anker(tick, o.typ)
                o.walk_done = o.walk_lag = o.walk_need = 0.0
                return []
            o.walk_lag, o.walk_need = tr.lag(tick, o.typ)
            o.walk_done = len(tr.walkers[0].fields) - 1 - tr.fields0
            if not judge or o.walk_lag <= 0:
                return []
            p25 = STREUUNG.get(o.typ)
            limit = max(
                SLOW_FIELDS * LM.flat_ticks_per_field(o.typ),
                o.walk_need * (1.0 / p25 - 1.0) if p25 else 0.0,
            )
            if o.walk_lag < limit:
                return []
            behind = (
                "%d ticks behind what the terrain of the walked fields gives (services/laufmodell.py, %d ticks since the path "
                "began at tick %d, the most favourable of the %d move counts, the unit's state carried since tick %d over %d "
                "orders), limit %d (%s)"
                % (
                    o.walk_lag,
                    o.walk_need,
                    tr.anchor,
                    LM.UPDATE,
                    tr.t0,
                    len(tr.orders),
                    limit,
                    "slowest quarter of the measured walks %.2f of the model" % p25
                    if p25
                    else "%d flat fields, spread of this type unmeasured" % SLOW_FIELDS,
                )
            )
        elif not same_path:
            o.walk_exp = o.walk_done = 0.0  # a new path (or none left): a new window
            return []
        else:
            o.walk_exp += (tick - last[0]) * (run + 1) / (8.0 * (v + run + 1))
            o.walk_done += idx - last[1]
            if o.walk_exp <= o.walk_done:
                o.walk_exp = o.walk_done = 0.0  # on time: the deficit counts from here
                return []
            if o.walk_exp - o.walk_done < SLOW_FIELDS:
                return []
            behind = None
        o.flags.add("slow_walk")
        self.counts[(o.kind, o.channel, "slow_walk")] += 1
        near = collections.Counter()
        for m, u in L.items():
            if m == o.unit or _schach((u["x"], u["y"]), pos) > 1:
                continue
            near[self._side(u)] += 1
        who = ", ".join("%s %d" % kv for kv in sorted(near.items())) or "nobody"
        # why: a unit that fights does not walk (game 16 of 14.11.2026, S142: spearman 332 with a walk order fought an enemy
        # woodcutter 2 fields away - state 106 - and the line said 'blocked or crowded; within 1 field: nobody')
        why = self._fight(o, e, k, L, pos) or "blocked or crowded"
        if behind is not None:
            return [
                self._line(
                    tick,
                    o,
                    e.get("typ"),
                    "WALK BEHIND THE TERRAIN - path index %d of %d, %.0f fields walked since on "
                    "time, %s: %s; within 1 field: %s; state %s"
                    % (idx, n, o.walk_done, behind, why, who, e.get("zustand")),
                )
            ]
        return [
            self._line(
                tick,
                o,
                e.get("typ"),
                "WALK BEHIND THE GAME'S SPEED - path index %d of %d, %.1f fields walked since "
                "on time where the speed value %s (flat %d) gives %.1f: %s; within 1 field: %s; state %s%s"
                % (
                    idx,
                    n,
                    o.walk_done,
                    v,
                    base,
                    o.walk_exp,
                    why,
                    who,
                    e.get("zustand"),
                    "; terrain slowed it in %d checks" % o.slowed if o.slowed else "",
                ),
            )
        ]

    def _side(self, u):
        owner = u.get("besitzer")
        return (
            "own"
            if owner == self.sp
            else (
                "neutral"
                if not owner
                else ("population" if u.get("typ") in WORKER_TYPES else "enemy")
            )
        )

    def _angriff_zustaende(self, o):
        m = ATTACK.get(o.typ)
        return SHOOTER_STATES if (m is not None and "cycle" in m) else tuple(ATTACK_STATES.values())

    def _kampf_ausser_auftrag(self, o, e, k):
        """Opponent (0 when the game names none) of a fight the order does not ask for, else None: the unit is in its attack state
        and the order is no attack on that unit (or, for a building order, the unit is not attacking a building)."""
        state = e.get("zustand")
        if state not in self._angriff_zustaende(o):
            return None
        if o.kind == "attack_building" and state != ATTACK_STATES["attack_unit"]:
            return None
        gegner = e.get("nahziel") or e.get("zieleinheit") or k.get("schusseinheit") or 0
        if o.kind == "attack_unit" and gegner == o.target:
            return None
        return gegner

    def _fight(self, o, e, k, L, pos):
        """'FIGHTS INSTEAD OF WALKING ...' when the unit is in its attack state (the states _attack checks), else None. The
        opponent: nahziel, the game's attack target or the core's shot target."""
        state = e.get("zustand")
        if state not in self._angriff_zustaende(o):
            return None
        art = (
            "melee against a building"
            if state == ATTACK_STATES["attack_building"]
            else ("melee against a unit" if state == ATTACK_STATES["attack_unit"] else "shooting")
        )
        gegner = e.get("nahziel") or e.get("zieleinheit") or k.get("schusseinheit") or 0
        u = L.get(gegner)
        if not gegner or u is None:
            return "FIGHTS INSTEAD OF WALKING - state %s (%s), opponent %s" % (
                state,
                art,
                "U%d not in the game state" % gegner if gegner else "not named by the game",
            )
        return (
            "FIGHTS INSTEAD OF WALKING - state %s (%s) against U%d (%s, type %s, %d fields away)"
            % (state, art, gegner, self._side(u), u.get("typ"), _schach((u["x"], u["y"]), pos))
        )

    def _drop(self, n, o):
        self.orders.pop(n, None)
        self.trails.pop(n, None)
        if o.ring is not None:
            self.by_ring.pop(o.ring, None)

    def summary(self):
        """One line: per kind and channel the orders sent, taken, not taken, arrived, not acting, and the ring results."""
        groups = collections.defaultdict(dict)
        for (kind, channel, stage), v in self.counts.items():
            groups[(kind, channel)][stage] = v
        parts = []
        for kind, channel in sorted(groups):
            g = groups[(kind, channel)]
            order = [
                "sent",
                "held",
                "taken",
                "not_seen",
                "arrived",
                "attack_started",
                "no_attack",
                "damage",
                "no_damage",
                "animation_stands",
                "useless",
                "resend_fighting",
                "slow_walk",
                "digging",
                "no_progress",
            ] + sorted(s for s in g if s.startswith("ring_"))
            parts.append(
                "%s/%s %s" % (kind, channel, " ".join("%s %d" % (s, g[s]) for s in order if s in g))
            )
        return "CHAIN summary: " + ("; ".join(parts) if parts else "no orders yet")
