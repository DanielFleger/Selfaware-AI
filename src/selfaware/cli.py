from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path

from selfaware import __version__
from selfaware.config import load_live_paths
from selfaware.diagnostics import report
from selfaware.domain import Session
from selfaware.game.replay import ReplayPort, read_legacy_trace
from selfaware.module_registry import MODULES
from selfaware.runtime import BotRuntime


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Selfaware-AI offline framework and setup diagnostics"
    )
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    doctor = commands.add_parser("doctor", help="report dependencies without starting a game")
    doctor.add_argument("--config", type=Path)
    doctor.add_argument("--offline", action="store_true", help="check only the installed framework")
    replay = commands.add_parser(
        "replay", help="inspect legacy observations; never send game commands"
    )
    replay.add_argument("trace", type=Path)
    replay.add_argument("--instance", type=int, default=1)
    replay.add_argument(
        "--player", type=int, default=1, help="player whose st fields the trace records"
    )
    replay.add_argument("--epoch", default="offline-replay")
    replay.add_argument("--limit", type=int, default=0, help="0 reads the complete trace")
    commands.add_parser(
        "modules", help="list the relocated current-bot modules without importing them"
    )
    run = commands.add_parser(
        "run", help="execute an existing bot/tool module with its original arguments"
    )
    run.add_argument("name", choices=sorted(MODULES))
    run.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    try:
        if args.command == "modules":
            print(json.dumps(MODULES, indent=2))
            return 0
        if args.command == "run":
            previous = sys.argv
            sys.argv = [MODULES[args.name], *args.arguments]
            try:
                runpy.run_module(MODULES[args.name], run_name="__main__", alter_sys=True)
            finally:
                sys.argv = previous
            return 0
        if args.command == "doctor":
            result = report(load_live_paths(args.config), offline=args.offline)
            print(json.dumps(result, indent=2))
            return 0 if args.offline else 2
        if args.limit < 0:
            raise ValueError("--limit cannot be negative")
        session = Session(args.instance, args.player, args.epoch)
        count, first, last, units, buildings, missing_uids = 0, None, None, 0, 0, 0
        port = ReplayPort(read_legacy_trace(args.trace, session))
        with BotRuntime(session, port) as runtime:
            while not args.limit or count < args.limit:
                try:
                    cycle = runtime.step()
                except StopIteration:
                    break
                snapshot = cycle.snapshot
                count += 1
                first = snapshot.tick if first is None else first
                last = snapshot.tick
                units = sum(e.ref.kind == "unit" for e in snapshot.entities)
                buildings = len(snapshot.entities) - units
                missing_uids = sum(e.ref.uid is None for e in snapshot.entities)
        if count == 0:
            raise ValueError("trace contains no observations")
        print(
            json.dumps(
                {
                    "mode": "observation_replay",
                    "frames": count,
                    "first_tick": first,
                    "last_tick": last,
                    "last_units": units,
                    "last_buildings": buildings,
                    "last_entities_without_uid": missing_uids,
                    "submitted_actions": len(port.submitted),
                    "game_effects_simulated": False,
                },
                indent=2,
            )
        )
        return 0
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}))
        return 2
