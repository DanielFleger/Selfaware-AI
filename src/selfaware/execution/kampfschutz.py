# -*- coding: utf-8 -*-
"""No second attack order to a melee unit that already fights that target (B-182; Daniel 13.11.2026: "Ja, abstellen";
Wissensregister S118).

Measured 2026-11-12 23:34 in the map editor (9 of 9 melee types, target E_SPEAR 24): a second identical attack order to a fighting
melee unit makes it walk again (state 101 at +3) and costs 4 / 8 / 12 ticks without damage. Several modules send the same order
again after some rounds (wegfuehrung NEU_ALLE, raids, nahkampf, vorstoss) - so the guard sits on the common order way:
befehl.sende (after the lord lock, before the observers) and kernweg.senden (before the core's ring).

A unit is taken out of an attack order on a unit target when the round's game state shows it fighting exactly that target: core
state 106 and the target in zieleinheit or nahziel. A target switch passes, shooters pass (they shoot in states 4/5/6, the second
order cost them nothing). Building targets (measured 13.11. 21:55, S122): a second order mid-swing restarts the swing - the part
already swung is lost (assassin +48 ticks, spear +24, sword +32); a unit in state 107 next to that building's footprint is taken
out. The Lenker gives the units and buildings of each round with stand(L, G).
"""

KAMPF_EINHEIT = 106
KAMPF_GEBAEUDE = 107
AM_GEBAEUDE = 2       # fields from the footprint (chain_audit.BUILDING_REACH: the attacker stands next to it)
_L, _G = {}, {}
gesperrt = 0          # orders taken out since the start, for the round summary
# Hooks called with (building target?, target, units held back) for each order - those units do what it asks already. The chain
# audit (micro/chain_audit.from_guard) takes it as their order: otherwise it kept the unit's older order (game 16 of 14.11.2026,
# S142: a walk order, while the melee raid wants the fight it holds back here). Data only, no order: nothing goes to the game
ERFUELLT = []


def stand(L, G=None):
    """The Lenker's units and buildings of this round ({nr: unit with zustand, zieleinheit, nahziel, x, y}, {nr: building})."""
    global _L, _G
    _L, _G = L or {}, G or {}


def kaempft_gebaeude(nr, gb):
    """Melee attack on building gb: state 107 and standing next to its footprint (corner x, y, edge sicht.GROESSE)."""
    import selfaware.services.sicht as sicht
    e, g = _L.get(nr), _G.get(gb)
    if e is None or g is None or e.get("zustand") != KAMPF_GEBAEUDE:
        return False
    b = sicht.GROESSE.get(g.get("typ"), 1) or 1
    dx = max(g["x"] - e["x"], 0, e["x"] - (g["x"] + b - 1))
    dy = max(g["y"] - e["y"], 0, e["y"] - (g["y"] + b - 1))
    return max(dx, dy) <= AM_GEBAEUDE


def kaempft(nr, ziel):
    e = _L.get(nr)
    return e is not None and e.get("zustand") == KAMPF_EINHEIT and ziel in (e.get("zieleinheit"), e.get("nahziel"))


def _eins(c):
    """One command -> (command or None, message or None)."""
    a = c.get("angriff") if isinstance(c, dict) else None
    if not isinstance(a, dict) or not a.get("einheiten") or not ("ziel" in a or "gebaeude" in a):
        return c, None
    gebaeude = "ziel" not in a
    ziel = a["gebaeude"] if gebaeude else a["ziel"]
    raus = [n for n in a["einheiten"] if (kaempft_gebaeude(n, ziel) if gebaeude else kaempft(n, ziel))]
    if not raus:
        return c, None
    global gesperrt
    gesperrt += len(raus)
    for hook in ERFUELLT:
        try:
            hook(gebaeude, ziel, list(raus))
        except Exception:      # a hook never stops the order way (like befehl.BEOBACHTER)
            pass
    rest = [n for n in a["einheiten"] if n not in raus]
    meld = "KAMPFSCHUTZ: %s kaempf%s schon gegen %s%s - derselbe Angriff nicht noch einmal (S118, S122)" % (
        ",".join(str(n) for n in raus), "t" if len(raus) == 1 else "en", "B" if gebaeude else "U", ziel)
    if not rest:
        return None, meld
    return dict(c, angriff=dict(a, einheiten=rest)), meld


def filtern(paket):
    """For befehl.sende: a single command or {"befehle": [...]} -> (packet or None when nothing is left, messages)."""
    if isinstance(paket, dict) and "befehle" in paket:
        neu, meld = [], []
        for c in paket["befehle"] or ():
            c2, m = _eins(c)
            if m:
                meld.append(m)
            if c2 is not None:
                neu.append(c2)
        return (dict(paket, befehle=neu) if neu else None), meld
    c2, m = _eins(paket)
    return c2, [m] if m else []


def liste(befehle):
    """For kernweg.senden: a list of commands -> (list without the taken-out units, messages)."""
    neu, meld = [], []
    for c in befehle or ():
        c2, m = _eins(c)
        if m:
            meld.append(m)
        if c2 is not None:
            neu.append(c2)
    return neu, meld
