# -*- coding: utf-8 -*-
"""Unit status log: per own fighter and round the module's intent (action, target, reason) and the Wegfuehrung's movement phase
(B-182, docs/plans/Plan_Unit_Status_Log.md section 6).

Daniel 2026-11-12 19:50: "Gedanken der Einheit zu jedem Spiel oder Anweisungen des Kriegsführers zu jeder Einheit/Zeit" and "Ohne Auftrag
ist für mich das Schlimmste - es sollte immer eine Begründung geben". Every module that leads a unit reports it each round
(report / report_many), the Wegfuehrung reports the movement phase of every unit it guides (path). A fighter nobody reported is
NO_ORDER (severity STOP in the error catalog).
"""

from selfaware.baukasten.obergrenze import KAEMPFER


class Action:
    ATTACK_UNIT = "ATTACK_UNIT"
    ATTACK_BUILDING = "ATTACK_BUILDING"
    SET_FIRE = "SET_FIRE"
    MOVE_TO_ATTACK = "MOVE_TO_ATTACK"
    MOVE_TO_STAGING = "MOVE_TO_STAGING"
    WAIT_STAGING = "WAIT_STAGING"
    WAIT_SAFE_TARGET = "WAIT_SAFE_TARGET"
    GATHER = "GATHER"
    RETREAT = "RETREAT"
    FLEE = "FLEE"
    HOLD_POST = "HOLD_POST"
    DEFEND = "DEFEND"
    DIG = "DIG"
    GAME_PATH = "GAME_PATH"
    NO_ORDER = "NO_ORDER"


ACTIONS = frozenset(v for k, v in vars(Action).items() if k.isupper())

# Wegfuehrung status (micro/wegfuehrung.py) -> movement phase: what the unit physically does
PHASES = {"neu": "new", "unterwegs": "walking", "greift_an": "attacking", "am_ziel": "at_point", "gefahr": "danger_at_stand",
          "kein_weg": "no_path", "direkt": "game_path", "steckt": "stuck", "wartet": "command_budget", "ziel_weg": "target_gone"}

# Code names of the game's unit types (UT_ without the prefix, as in the game data); Daniel: names with code and number.
# Type 23 stays a number.
NAMES = {5: "TUNNELER", 22: "E_ARCHER", 24: "E_SPEAR", 25: "E_PIKE", 26: "E_MACE", 27: "E_SWORD", 28: "E_KNIGHT", 29: "E_LADDER",
         30: "E_ENGINEER", 37: "E_MONK", 55: "LORD", 70: "A_ARCHER", 71: "A_SLAVE", 72: "A_SLINGER", 73: "A_ASSASSIN",
         74: "A_HARCHER", 75: "A_SWORDSMAN", 76: "A_FIRETHROWER"}


def type_name(typ):
    return "%s %s" % (NAMES[typ], typ) if typ in NAMES else "T%s" % (typ,)


def unit(n):
    return "U%d" % n


def building(n):
    return "B%d" % n


def point(p):
    return "(%d,%d)" % (int(p[0]), int(p[1]))


def _text(v):
    return str(v).replace(" ", "")


def _expect(action, typ, e, target, L, G):
    """The expected result of the order (Daniel 13.11.2026 22:45, "Ja, einbauen" 22:49) - from chain_audit.expectation, the same
    measured tables the chain check checks. target: "U<n>", "B<n>", "(x,y)" or None."""
    import selfaware.services.sicht as sicht
    from selfaware.micro import chain_audit  # here: chain_audit imports this module
    goal, kind = None, None
    t = str(target or "")
    if t.startswith("U") and t[1:].isdigit():
        z, kind = L.get(int(t[1:])), "unit"
        goal = (z["x"], z["y"]) if z else None
    elif t.startswith("B") and t[1:].isdigit():
        g, kind = (G or {}).get(int(t[1:])), "building"
        if g:
            b = sicht.GROESSE.get(g.get("typ"), 1) or 1
            goal = (g["x"] + b // 2, g["y"] + b // 2)
    elif t.startswith("(") and t.endswith(")"):
        try:
            goal, kind = tuple(int(v) for v in t[1:-1].split(",")), "point"
        except ValueError:
            pass
    pos = (e["x"], e["y"]) if e else None
    return chain_audit.expectation(action, typ, pos, goal, kind)


class UnitLog:
    def __init__(self, sp):
        self.sp = sp
        self.reports = {}      # unit -> (owner, action, target, reason, params) of the running round, from the modules
        self.paths = {}        # unit -> (owner, phase, target, waypoint) of the running round, from the Wegfuehrung
        self.last = {}         # unit -> (owner, action, target, reason, phase, params, type) of the round closed last
        self.tick = None

    def report(self, unit, owner, action, target=None, reason="", **params):
        if action not in ACTIONS:
            raise ValueError("unknown action %r - add it to docs/plans/Plan_Unit_Status_Log.md and Action first" % (action,))
        self.reports[unit] = (owner, action, target, reason, tuple(sorted(params.items())))

    def report_many(self, owner, intents):
        """intents: {unit: (action, target, reason, params)} - the `absicht` a module filled this round."""
        for n, (action, target, reason, params) in sorted(intents.items()):
            self.report(n, owner, action, target, reason, **(params or {}))

    def path(self, unit, owner, phase, target, waypoint=None):
        self.paths[unit] = (owner, PHASES.get(phase, phase), target, waypoint)

    def _entry(self, n, typ):
        r, p = self.reports.get(n), self.paths.get(n)
        phase = p[1] if p else "-"
        if r is None:
            owner, _phase, target, _wp = p
            if target.startswith("U"):
                action = Action.ATTACK_UNIT
            elif target.startswith("B"):
                action = Action.ATTACK_BUILDING
            else:
                action = Action.WAIT_STAGING if phase == "at_point" else Action.MOVE_TO_STAGING
            owner, reason, params = owner, "no_module_reason", ()
        else:
            owner, action, target, reason, params = r
            if action == Action.MOVE_TO_STAGING and phase == "at_point":
                action = Action.WAIT_STAGING      # arrived: the module's "go there" is now "wait there" (Partie 12.11. 20:34)
        if p is not None:
            extra = []
            if p[3] is not None:
                extra.append(("wp", point(p[3])))
            if r is not None and p[2] != target:
                extra.append(("path_target", p[2]))
            params = tuple(params) + tuple(extra)
        return (owner, action, target, reason, phase, params, typ)

    def close_round(self, tick, L, G=None):
        """Ends the round: merges intents and paths of living own units; every own living fighter without either gets NO_ORDER.
        Returns the console lines for units whose owner, action, target, reason or phase changed, and for units that are gone."""
        self.tick = tick
        now = {}
        for n in set(self.reports) | set(self.paths):
            e = L.get(n)
            if e is not None and e.get("besitzer") == self.sp and e.get("leben", 1) > 0:
                now[n] = self._entry(n, e.get("typ"))
        for n, e in L.items():
            if e.get("besitzer") == self.sp and e.get("typ") in KAEMPFER and e.get("leben", 1) > 0 and n not in now:
                now[n] = ("nobody", Action.NO_ORDER, None, "no_module_reported", "-", (), e.get("typ"))
        lines = []
        for n in sorted(now):
            r = now[n]
            if self.last.get(n, (None,) * 5)[:5] != r[:5]:
                lines.append("UNIT t=%s %d (%s) %s %s%s%s path=%s%s expect=%s" % (
                    tick, n, type_name(r[6]), r[0], r[1], "" if r[2] is None else " target=%s" % (r[2],),
                    " reason=%s" % r[3] if r[3] else "", r[4], "".join(" %s=%s" % (k, _text(v)) for k, v in r[5]),
                    _expect(r[1], r[6], L.get(n), r[2], L, G)))
        for n in sorted(set(self.last) - set(now)):
            lines.append("UNIT t=%s %d (%s) gone" % (tick, n, type_name(self.last[n][6])))
        self.last, self.reports, self.paths = now, {}, {}
        return lines

    def no_order(self):
        """Units that had NO_ORDER in the round closed last (unreported, or a module that said it has no order for them)."""
        return sorted(n for n, r in self.last.items() if r[1] == Action.NO_ORDER)

    def table(self):
        """Text table of the round closed last, for the position log (key "intents"): first line the tick, then one row per unit;
        params as k=v separated by ";" (points contain commas)."""
        rows = ["tick %s" % self.tick, "unit type owner action target reason path params"]
        for n in sorted(self.last):
            o, a, t, why, phase, params, typ = self.last[n]
            rows.append("%d %s %s %s %s %s %s %s" % (n, typ, o, a, "-" if t is None else t, why or "-", phase,
                                                     ";".join("%s=%s" % (k, _text(v)) for k, v in params) or "-"))
        return "\n".join(rows) + "\n"


def collect_round(log, tick, L, G, waechter=None, graben=None, assassins=None, raid=None, wegf=None):
    """End of a Lenker round: collects the intents of all modules (a later report wins: Waechter, Graben, Assassinen, raid modules),
    the movement phases of the Wegfuehrung, closes the round. Returns the console lines: the UNIT change lines and, if own fighters
    had no order, one UNIT_NO_ORDER line. Modules without a log (older plug-in versions) are skipped - their units show as
    NO_ORDER, which is the point."""
    if waechter is not None:
        log.report_many("waechter", getattr(waechter, "absicht", None) or {})
    if graben is not None and hasattr(graben, "absichten"):
        log.report_many("graben", graben.absichten(L))
    if assassins is not None and hasattr(assassins, "absichten"):
        log.report_many("assassinen", assassins.absichten(L, G))
    if raid is not None and hasattr(raid, "absichten"):
        for owner, intents in raid.absichten().items():
            log.report_many(owner, intents)
    if wegf is not None and hasattr(wegf, "absichten"):
        for n, (owner, status, target, wp) in wegf.absichten().items():
            log.path(n, owner, status, target, wp)
    lines = log.close_round(tick, L, G)
    missing = log.no_order()
    if missing:
        lines.append("UNIT_NO_ORDER t=%s %d: %s" % (tick, len(missing), ", ".join(
            "%d (%s) %s" % (n, type_name(log.last[n][6]), log.last[n][0]) for n in missing)))
    return lines


def read_table(text):
    """(tick, {unit: {type, owner, action, target, reason, path, params}}) from a table() text; (None, {}) without one."""
    if not text:
        return None, {}
    z = text.splitlines()
    tick = z[0].split()[1] if z and z[0].startswith("tick ") else None
    rows = {}
    for r in z[2:]:
        w = r.split(" ")
        if len(w) < 8:
            continue
        rows[int(w[0])] = {"type": w[1], "owner": w[2], "action": w[3], "target": w[4], "reason": w[5], "path": w[6],
                           "params": dict(kv.split("=", 1) for kv in w[7].split(";") if "=" in kv)}
    return (int(tick) if tick not in (None, "None") else None), rows
