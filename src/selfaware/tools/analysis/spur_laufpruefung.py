# -*- coding: utf-8 -*-
"""Replays the way of ONE own unit from a game through the walk check (micro/chain_audit.ChainAudit, link 2 with the terrain map) -
to tell a walk alarm of the watch from a unit that was really held up (B-182; game 14 of 14.11.2026, S138: replayed, the old check
gave exactly the alarm of the game, 62 ticks behind at limit 48; the new one 7 ticks at most).

Input: the console of the game (aufstellung_*_konsole.txt: the line "KETTE Laufpruefung: Gelaende aus <file>" and the lines
"BEFEHL Tick N <art> {...} an k Einheiten: [...]"), its Lageprotokoll (lage_*.jsonl.gz, one line per round) and the unit number.
Each order goes to the check after the last round before its tick (the Lenker sends in the round before, after its check).
Path index: from the table "eigen" of the Lageprotokoll (wegindex, weglaenge, tempo - written since 14.11.2026, S138). Older
protocols have none - then the replay counts the fields between two rounds (Schach) as index steps and gives every order a path
of its own; on a winding path that is too few fields (replay of game 13: two alarms the game with its real index did not give).

Call (PYTHONPATH=src): python -m selfaware.tools.analysis.spur_laufpruefung <konsole> <lage> <einheit> [gelaende=<survey .txt>]
"""
import gzip
import json
import os
import re
import sys

from selfaware import workspace as _workspace
from selfaware.micro import chain_audit as CA
from selfaware.services import laufmodell as LM
from selfaware.telemetry.lageprotokoll import eigen_lesen
from selfaware.tools.experiments.gelaende_erheben import tile_function

BEFEHL = re.compile(r"^BEFEHL Tick (\d+) (angriff|halten) (\{.*\}) an \S+ Einheiten: \[([\d, ]*)\]")
GELAENDE = re.compile(r"KETTE Laufpruefung: Gelaende aus (\S+)")


def befehle(konsole, einheit):
    """-> [(tick, paket for ChainAudit.from_module)] of the orders to this unit, and the survey file named by the console."""
    aus, gelaende = [], None
    for zeile in open(konsole, encoding="utf-8", errors="replace"):
        g = GELAENDE.search(zeile)
        if g:
            gelaende = g.group(1)
        m = BEFEHL.match(zeile.strip())
        if not m or einheit not in [int(n) for n in m.group(4).replace(" ", "").split(",") if n]:
            continue
        ziel = json.loads(m.group(3))
        paket = {"angriff": dict(ziel, einheiten=[einheit])} if m.group(2) == "angriff" else {"halten": dict(ziel, nr=[einheit])}
        aus.append((int(m.group(1)), paket))
    return aus, gelaende


def _tabelle(text):
    zeilen = [z.split() for z in text.split("\n") if z.strip()]
    kopf = next(i for i, z in enumerate(zeilen) if z and z[0] == "nr")
    return {int(z[0]): {k: int(v) for k, v in zip(zeilen[kopf], z) if v.lstrip("-").isdigit()} for z in zeilen[kopf + 1:] if z}


def runden(lage):
    """-> [(tick, units {nr: fields}, buildings {nr: fields}, own core fields {nr: fields})] from a Lageprotokoll."""
    aus = []
    for zeile in gzip.open(lage, "rt", encoding="utf-8"):
        r = json.loads(zeile)
        aus.append((r["t"], _tabelle(r["einheiten"]), _tabelle(r.get("gebaeude", "nr")), eigen_lesen(r)))
    return aus


def nachspielen(konsole, lage, einheit, gelaende=None):
    """-> [(tick, (x, y), state, delay, model ticks, limit, CHAIN lines)] per round with an order of the unit."""
    orders, genannt = befehle(konsole, einheit)
    gelaende = gelaende or (genannt and os.path.join(_workspace.DATA, genannt))
    if not gelaende or not os.path.exists(gelaende):
        raise SystemExit("Geländekarte fehlt (%s) - ohne sie prüft die Kette nur das Tempo je Runde" % gelaende)
    k = CA.ChainAudit(1, tile=tile_function(gelaende))
    folge = runden(lage)
    aus, schritte, pfad, letzte = [], 0, 0, None
    for tick, paket in orders:                     # carried out before the first round of the protocol
        if folge and tick <= folge[0][0]:
            k.tick = tick
            k.from_module(paket)
            pfad += 1
    for i, (t, L, G, eigen) in enumerate(folge):
        e = L.get(einheit)
        if e is not None:
            k.sp = e["besitzer"]
            pos = (e["x"], e["y"])
            schritte += max(abs(pos[0] - letzte[0]), abs(pos[1] - letzte[1])) if letzte else 0
            letzte = pos
            typ = e["typ"]
            v = LM.TYPES[typ][0] if typ in LM.TYPES else 1
            k.tick = t
            kern = eigen.get(einheit, {})
            if "wegindex" not in kern:      # older protocol: the fields walked as index, one path per order
                kern = dict(kern, wegindex=schritte, weglaenge=10 ** 6 + pfad, tempo=v)
            zeilen = k.check(t, L, G, {einheit: kern})
            o = k.orders.get(einheit)
            if o is not None and typ in LM.TYPES:
                p25 = CA.STREUUNG.get(typ)
                limit = max(CA.SLOW_FIELDS * LM.flat_ticks_per_field(typ), o.walk_need * (1.0 / p25 - 1.0) if p25 else 0.0)
                aus.append((t, pos, e.get("zustand"), o.walk_lag, o.walk_need, limit, zeilen))
        nachste = folge[i + 1][0] if i + 1 < len(folge) else float("inf")
        for tick, paket in orders:                 # sent in this round, after the check: carried out before the next one
            if t < tick <= nachste:
                k.tick = t
                k.from_module(paket)
                pfad, schritte = pfad + 1, 0
    return aus


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    frei = [a for a in argv if "=" not in a]
    arg = dict(a.split("=", 1) for a in argv if "=" in a)
    if len(frei) != 3:
        raise SystemExit(__doc__)
    zeilen = nachspielen(frei[0], frei[1], int(frei[2]), arg.get("gelaende"))
    schlimmst = max(zeilen, key=lambda z: z[3] - z[5], default=None)
    for t, pos, zustand, lag, need, limit, chain in zeilen:
        print("Takt %5d %-10s Zustand %3s  Rueckstand %4.0f  Modell %5.0f  Grenze %4.0f%s" % (
            t, "(%d,%d)" % pos, zustand, lag, need, limit, "  " + chain[0][:160] if chain else ""))
    if schlimmst:
        print("Groesster Rueckstand gegen die Grenze: %.0f bei Grenze %.0f, Takt %d; Alarme: %d" % (
            schlimmst[3], schlimmst[5], schlimmst[0], sum(1 for z in zeilen if z[6])))


if __name__ == "__main__":
    main()
