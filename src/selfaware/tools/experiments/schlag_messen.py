# -*- coding: utf-8 -*-
"""Attack chain timing per unit type (B-182, docs/plans/Plan_Unit_Status_Log.md section 8).

Daniel 2026-11-12 22:55: "Ziel waehlen -> Am Ziel (erkannt sonst Pause) -> sollte instant Angriffsanimation starten (sonst Pause)
-> fuehrt erste Angriffsanimation aus -> Schaden (sonst Pause)"; 23:04: "ja alle Einheitenarten ... das kannst du in der Sandbox
testen".

Sandbox = map editor on instance 2 (steps in the plan, section 8). One trial: an own unit of type A two fields next to an enemy
target (a building by mapper code, or a unit of type B), one attack order, then every tick from the core (kern_leitung): attacker
state, substate, frame (bild), frame cycle, position, life; target life, fire, state. Every trial stands on its own free spot: a
building of an earlier trial can still burn there (measured 2026-11-12 23:07: the swordsman trial hit a burning hut with 4 life left).

Result per trial, one line in data/research/schlag_messung_<stamp>.jsonl: the state sequence, ticks order -> attack state, the
frames of the first swing, every life loss of the target (ticks after the attack state, damage, frame before/after, target burning),
the ticks between two swings, why the trial ended.

Call (PYTHONPATH=src, SHC_INSTANZ=2):
  python -m selfaware.tools.experiments.schlag_messen leben mapper=56:6,55:2,80:4          life of each building class
  python -m selfaware.tools.experiments.schlag_messen gebaeude typen=73,75 mapper=56 groesse=6 [ticks=900] [treffer=5] [tempo=20]
  python -m selfaware.tools.experiments.schlag_messen einheit typen=73,75 ziel=24 [abstand=2] [nachsenden=20] [ticks=900] [treffer=5]
"""
import json
import os
import sys
import time

from selfaware import workspace as _workspace
from selfaware.micro.unit_log import type_name

CENTRE = (200, 200)     # inside the map diamond for every map size
GRID = 16               # fields between two trial spots
FREE = 10               # no building within this many fields of a spot
NEXT_TO = 2             # the target stands this many fields east of the attacker
ATTACK = (106, 107)     # core state: melee attack on a unit / a building (measured in game 20)
RANGED = (4, 5, 6)      # core state of a shooter: aim animation, shot, reload (measured 2026-11-12 23:22, archers vs a hut)
STARTS = ATTACK + (4,)  # the attack has started
NO_ATTACK_TICKS = 300   # no attack state this long after the order: this type does not attack this target
NO_HIT_TICKS = 600      # attack state, but the target loses no life this long: no damage
FIELDS = ("t", "state", "substate", "frame", "cycle", "x", "y", "life", "target_life", "target_fire", "target_state")
T, STATE, SUB, FRAME, CYCLE, X, Y, LIFE, T_LIFE, T_FIRE, T_STATE = range(len(FIELDS))


_LOCK = []


def exclusive(path=None):
    """One measurement at a time on the instance: every trial starts with "kill all units", a second run kills the units of the
    first (2026-11-12 23:24: two runs at once, the trials ended "attacker_gone"). The lock is a file held open with an
    exclusive OS lock - it goes away with the process, also when the process is killed."""
    path = path or os.path.join(_workspace.DATA, ".messung_instanz%s.lock" % os.environ.get("SHC_INSTANZ", "?"))
    f = open(path, "a+")
    try:
        if os.name == "nt":
            import msvcrt
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        f.close()
        raise SystemExit("ERROR: another measurement runs on instance %s (lock %s)" % (os.environ.get("SHC_INSTANZ"), path)) from None
    _LOCK.append(f)
    return path


def _channel():
    import selfaware.game.ucp.befehl as K
    return K


def send(orders, until=None, wait=4.0):
    return _channel().sende({"befehle": orders}, wait, bis=until)


def clear():
    """All units of players 1 and 2 except the lords (in a skirmish the lords must live; in the editor there are none)."""
    send([{"toeteAlle": {"spieler": 1, "ohneLord": True}}, {"toeteAlle": {"spieler": 2, "ohneLord": True}}], until="TOETE ALLE")
    time.sleep(2.0)


def place_unit(player, typ, x, y):
    for s in send([{"setzeEinheit": {"spieler": player, "typ": typ, "x": x, "y": y}}], until="SETZE EINHEIT"):
        if "SETZE EINHEIT" in s and "Nummern" in s:
            try:
                return int(s.rsplit("Nummern", 1)[1].strip().split(",")[0])
            except ValueError:
                return None
    return None


def spots():
    """Trial spots around the map centre, nearest first."""
    r = [(CENTRE[0] + GRID * i, CENTRE[1] + GRID * j) for i in range(-4, 5) for j in range(-4, 5)]
    return sorted(r, key=lambda p: (abs(p[0] - CENTRE[0]) + abs(p[1] - CENTRE[1]), p))


def free_spot(buildings, used):
    """buildings: {nr: {"x", "y", ...}} of the world now; used: spots of this run (changed). -> the first spot without a building
    within FREE fields."""
    for p in spots():
        if p in used or any(max(abs(g["x"] - p[0]), abs(g["y"] - p[1])) <= FREE for g in buildings.values()):
            continue
        used.add(p)
        return p
    raise RuntimeError("no free trial spot left - open a new map in the editor")


def _world(le):
    for _ in range(20):
        w = le.lesen()
        if w is not None:
            return w
        time.sleep(0.05)
    raise RuntimeError("the core gives no world")


def place_building(le, player, mapper, size, x, y):
    """-> number of the new building of the player, or None (the game placed nothing)."""
    before = set(_world(le).gebaeude)
    send([{"setzeGebaeude": {"spieler": player, "x": x, "y": y, "mapper": mapper, "groesse": size}}], until="SETZE GEBAEUDE")
    time.sleep(0.5)
    new = [(max(abs(g["x"] - x), abs(g["y"] - y)), n) for n, g in _world(le).gebaeude.items()
           if n not in before and g.get("besitzer") == player]
    return min(new)[1] if new else None


def row(w, a, target, on_building):
    e = w.einheiten.get(a) or {}
    z = (w.gebaeude.get(target) if on_building else w.einheiten.get(target)) or {}
    return [w.tick, e.get("zustand"), e.get("teilzustand"), e.get("bild"), e.get("bildzyklus"), e.get("x"), e.get("y"),
            e.get("leben"), z.get("leben"), z.get("feuer"), z.get("zustand")]


def hits(rows):
    """Every life loss of the target: (index of the row after the loss, damage)."""
    return [(i + 1, a[T_LIFE] - b[T_LIFE]) for i, (a, b) in enumerate(zip(rows, rows[1:], strict=False))
            if a[T_LIFE] is not None and b[T_LIFE] is not None and b[T_LIFE] < a[T_LIFE]]


def stop_reason(rows, ticks, hits_wanted):
    """None while the trial goes on."""
    last, t0 = rows[-1], rows[0][T]
    if last[LIFE] is None:
        return "attacker_gone"
    if last[T_LIFE] is None or last[T_LIFE] <= 0:
        return "target_gone"
    attack = next((r[T] for r in rows if r[STATE] in STARTS), None)
    if attack is None and last[T] - t0 >= NO_ATTACK_TICKS:
        return "no_attack"
    found = hits(rows)
    if attack is not None and not found and last[T] - attack >= NO_HIT_TICKS:
        return "no_hit"
    if len(found) >= hits_wanted:
        return "hits"
    if last[T] - t0 >= ticks:
        return "time"
    return None


def summarize(rows, reason=None, resend=None):
    """rows: lists in FIELDS order, the first one the tick of the order -> the chain of the trial; resend: tick of a second
    identical order."""
    t0 = rows[0][T]
    states, prev = [], object()
    for r in rows:
        if r[STATE] != prev:
            states.append([r[T] - t0, r[STATE]])
            prev = r[STATE]
    attack = next((r[T] for r in rows if r[STATE] in STARTS), None)
    ref = attack if attack is not None else t0   # without an attack state the losses count from the order
    loss = []
    for i, d in hits(rows):
        a, b = rows[i - 1], rows[i]
        loss.append({"after_attack": b[T] - ref, "damage": d, "frames": [a[FRAME], b[FRAME]],
                     "burning": bool(a[T_FIRE] or b[T_FIRE])})
    swings = [h for h in loss if not h["burning"]]
    first_end = None if not swings or attack is None else attack + swings[0]["after_attack"]
    frames, prev = [], object()
    for r in rows:
        if attack is not None and r[T] >= attack and r[STATE] in STARTS + RANGED and (first_end is None or r[T] <= first_end):
            if r[FRAME] != prev:
                frames.append([r[T] - attack, r[FRAME]])
                prev = r[FRAME]
    fire = next((r[T] for r in rows if r[T_FIRE]), None)
    life = [r[LIFE] for r in rows if r[LIFE] is not None]
    return {"order_to_attack": None if attack is None else attack - t0,
            "first_hit": swings[0]["after_attack"] if swings else None,
            "between_hits": [b["after_attack"] - a["after_attack"] for a, b in zip(swings, swings[1:], strict=False)],
            "damage": [h["damage"] for h in swings],
            "fire_losses": [[h["after_attack"], h["damage"]] for h in loss if h["burning"]],
            "fire_from": None if fire is None else fire - ref, "losses_from": "attack" if attack is not None else "order",
            "first_swing_frames": frames, "states": states, "target_life": rows[0][T_LIFE],
            "attacker_loss": None if not life else life[0] - life[-1],
            "skipped_ticks": sum(b[T] - a[T] - 1 for a, b in zip(rows, rows[1:], strict=False)), "end": reason,
            "resend_gap": None if resend is None else _gap_after(rows, resend)}


def _gap_after(rows, t):
    """Ticks from tick t to the first life loss of the target after it, and the longest gap between two losses before t."""
    after = [rows[i][T] for i, _d in hits(rows) if rows[i][T] > t]
    before = [rows[i][T] for i, _d in hits(rows) if rows[i][T] <= t]
    return {"to_next_loss": after[0] - t if after else None,
            "longest_before": max((b - a for a, b in zip(before, before[1:], strict=False)), default=None)}


def trial(le, a_typ, target, spot, ticks=900, hits_wanted=5, distance=NEXT_TO, resend_after=None, resend_delay=0):
    """target: ("gebaeude", mapper, size) or ("einheit", typ); distance: fields east of the attacker for a unit target (two units
    two fields apart fight before the order - measured 2026-11-12 23:31; shooters need the target out of melee reach).
    resend_after: after so many life losses the same order goes out once more (23:31: a second order to a fighting swordsman
    made it walk 8 ticks without damage) - the tick is in "resend", the gap in the result."""
    clear()
    a = place_unit(1, a_typ, spot[0], spot[1])
    if target[0] == "gebaeude":
        z = place_building(le, 2, target[1], target[2], spot[0] + NEXT_TO, spot[1] - 1)
        order = {"angriff": {"einheiten": [a], "gebaeude": z}}
    else:
        z = place_unit(2, target[1], spot[0] + distance, spot[1])
        order = {"angriff": {"einheiten": [a], "ziel": z}}
    out = {"attacker": a_typ, "target": list(target), "spot": list(spot), "nr": a, "target_nr": z, "fields": FIELDS}
    if a is None or z is None:
        out.update(result={"end": "not_placed"}, rows=[])
        return out
    time.sleep(0.3)
    e = _world(le).einheiten.get(a) or {}
    if max(abs((e.get("x") or -99) - spot[0]), abs((e.get("y") or -99) - spot[1])) > 3:
        out.update(result={"end": "wrong_spot", "at": [e.get("x"), e.get("y")]}, rows=[])  # outside the map diamond?
        return out
    send([order], until="ANGRIFF")  # the channel looks every 20 ms: the first row is at most a tick after the order
    rows, reason = [row(_world(le), a, z, target[0] == "gebaeude")], None
    last = rows[0][T]
    while reason is None:
        w = le.lesen()
        if w is None or w.tick == last:
            time.sleep(0.004)
            continue
        last = w.tick
        rows.append(row(w, a, z, target[0] == "gebaeude"))
        reason = stop_reason(rows, ticks, hits_wanted)
        h = hits(rows)
        if resend_after and out.get("resend") is None and len(h) >= resend_after and (
                w.tick - rows[h[resend_after - 1][0]][T] >= resend_delay):     # mid-swing: resend_delay ticks after that hit
            out["resend"] = w.tick
            send([order], wait=0.0)       # no wait for the answer: the rows go on
    out.update(result=summarize(rows, reason, out.get("resend")), rows=rows)
    return out


def life_of(le, classes, used):
    """classes: [(mapper, size)] -> [(mapper, size, building type, life, fire)] of a freshly placed enemy building."""
    out = []
    for mapper, size in classes:
        spot = free_spot(_world(le).gebaeude, used)
        n = place_building(le, 2, mapper, size, spot[0], spot[1])
        g = _world(le).gebaeude.get(n) or {}
        out.append((mapper, size, g.get("typ"), g.get("leben"), g.get("feuer")))
    return out


def main():
    import selfaware.game.kern_leitung as KL
    from selfaware.game.ucp.befehl import SPIEL
    what = sys.argv[1]
    arg = dict(a.split("=", 1) for a in sys.argv[2:])
    exclusive()
    le = KL.Leitung(SPIEL)
    used = set()
    if "tempo" in arg:
        send([{"tempo": int(arg["tempo"])}], wait=2.0)
    if what == "leben":
        classes = [tuple(int(v) for v in p.split(":")) for p in arg["mapper"].split(",")]
        for mapper, size, typ, life, fire in life_of(le, classes, used):
            print("mapper %d size %d: building type %s, life %s, fire %s" % (mapper, size, typ, life, fire), flush=True)
        return
    types = [int(x) for x in arg["typen"].split(",")]
    target = ("gebaeude", int(arg["mapper"]), int(arg.get("groesse", 3))) if what == "gebaeude" else ("einheit", int(arg["ziel"]))
    path = os.path.join(_workspace.DATA, "schlag_messung_%s.jsonl" % time.strftime("%Y%m%d_%H%M%S"))
    for typ in types:
        r = trial(le, typ, target, free_spot(_world(le).gebaeude, used), int(arg.get("ticks", 900)), int(arg.get("treffer", 5)),
                  int(arg.get("abstand", NEXT_TO)), int(arg["nachsenden"]) if "nachsenden" in arg else None,
                  int(arg.get("nachsenden_takte", 0)))
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(r) + "\n")
        s = r["result"]
        print("%s vs %s: %s" % (type_name(typ), target, json.dumps({k: v for k, v in s.items() if k != "first_swing_frames"})),
              flush=True)
    print("file:", path)


if __name__ == "__main__":
    main()
