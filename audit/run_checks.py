"""Read-only audit checks. No game process, game files, or native functions are used.

Run with Python; lupa is optional for mocked Lua connector checks.
Results are written only to audit/results.json and temporary directories.
"""
from __future__ import annotations

import ast
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import io
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
from threading import Barrier
import types
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "src"))
from selfaware.module_registry import MODULES
import selfaware.game.ucp

LEGACY_FILES = {name + ".py": ROOT / "src" / (module.replace(".", "/") + ".py")
                for name, module in MODULES.items()}


def source(name):
    return LEGACY_FILES[name]



def offline_child(name):
    """Run an existing offline script with a disconnected connector stub."""
    with tempfile.TemporaryDirectory(prefix="selfaware-suite-") as tmp:
        k = types.ModuleType("befehl")
        for key, value in {
            "SPIEL": tmp, "ABZUG": tmp, "LOG": str(Path(tmp) / "ucp3.log"),
            "BEFEHL": str(Path(tmp) / "befehl.json"), "INSTANZ": 1,
            "SPIELER": 1, "PARTNER": False, "STRENG": True,
        }.items():
            setattr(k, key, value)
        def disconnected(*args, **kwargs):
            raise RuntimeError("AUDIT: live connector disabled")
        k.sende = disconnected
        k.neue_id = lambda: 1
        sys.modules["selfaware.game.ucp.befehl"] = k
        original_open, original_io_open = open, io.open
        def guarded(opener):
            def guard(file, mode="r", *args, **kwargs):
                if any(c in mode for c in "wax+") and not isinstance(file, int):
                    resolved = Path(file).resolve()
                    if not resolved.is_relative_to(Path(tempfile.gettempdir()).resolve()):
                        raise RuntimeError("AUDIT: write outside temporary directory blocked: " + str(resolved))
                return opener(file, mode, *args, **kwargs)
            return guard
        sys.argv = [str(source(name))]
        with patch("builtins.open", guarded(original_open)), patch("io.open", guarded(original_io_open)):
            runpy.run_path(str(source(name)), run_name="__main__")


def load_connector(tmp):
    spec = importlib.util.spec_from_file_location("audit_real_befehl", source("befehl.py"))
    k = importlib.util.module_from_spec(spec)
    # Only bypass the machine-specific install-directory check during import.
    env = {"SHC_INSTANZ": "1", "SHC_SPIELER": "1", "SHC_PARTNER": ""}
    with patch.dict(os.environ, env), patch("os.path.isdir", return_value=True):
        spec.loader.exec_module(k)
    for key, name in {"BEFEHL": "befehl.json", "LOG": "ucp3.log", "MERKER": "id",
                      "SENDE": "lock", "LAUF": "owner"}.items():
        setattr(k, key, str(Path(tmp) / name))
    Path(k.LOG).write_text("", encoding="utf-8")
    return k


def connector_probes():
    findings = []
    with tempfile.TemporaryDirectory(prefix="selfaware-connector-") as tmp:
        k = load_connector(tmp)
        # A short response deadline, with no game consumer or acknowledgement.
        k.STRENG = True
        result = k.sende({"player": 1, "zeit": True}, warte=0.05)
        findings.append({"id": "C01", "reproduced": result == [], "returned_without_ack": result})

        k.PARTNER = True
        # An owner still inside the permitted 20-second response wait loses its lock at 9 seconds.
        Path(k.SENDE).write_text("still-active-owner")
        original_time = __import__("time").time()
        os.utime(k.SENDE, (original_time - 9, original_time - 9))
        k._sperren()
        new_owner = Path(k.SENDE).read_text()
        k._entsperren()  # Simulates the original owner's finally deleting the replacement owner's lock.
        findings.append({"id": "C02", "reproduced": new_owner == str(os.getpid()),
                         "active_lock_replaced_after_seconds": 9,
                         "replacement_deleted_by_unconditional_unlock": not Path(k.SENDE).exists()})

        k.belege()
        k.freigeben()
        findings.append({"id": "C03", "reproduced": Path(k.LAUF).exists(),
                         "partner_owner_file_survives_release": Path(k.LAUF).exists()})

        import selfaware.execution.lordschutz as guard
        guard.aktualisieren(5000, {5: {"typ": 55, "besitzer": 1}, 9: {"typ": 55, "besitzer": 2}})
        attack = {"player": 1, "angriff": {"einheiten": [5], "ziel": 9}}
        single, _ = guard.filtern(attack)
        batch, _ = guard.filtern({"befehle": [attack]})
        findings.append({"id": "C04", "reproduced": single is not None and batch is None,
                         "single_allowed": single is not None, "batch_blocked": batch is None})

        # Prefix completion: response to a different request can finish the poll.
        k.PARTNER = False
        def append_other_response(_):
            with open(k.LOG, "a", encoding="utf-8") as f:
                f.write("[villagestudio] | PEEK 0x00001000: DEADBEEF\n")
        with patch.object(k.time, "sleep", side_effect=append_other_response):
            result = k.sende({"player": 1, "peek": 4096}, warte=1, bis="PEEK 0x00001000")
        findings.append({"id": "C05", "reproduced": bool(result) and not any("QUITTUNG" in s for s in result),
                         "unacknowledged_response_accepted": result})

        # Model two independent processes with separate module state, sharing the
        # same player's counter. Synchronize their completed reads deterministically.
        a, b = load_connector(tmp), load_connector(tmp)
        Path(a.MERKER).write_text("0")
        barrier = Barrier(2)
        original_open = a.io.open
        class CounterReader:
            def __init__(self, file):
                self.file = file
            def read(self):
                value = self.file.read()
                self.file.close()
                barrier.wait(timeout=3)
                return value
        def counter_open(path, mode="r", *args, **kwargs):
            file = original_open(path, mode, *args, **kwargs)
            return CounterReader(file) if path == a.MERKER and mode == "r" else file
        with patch.object(a.io, "open", side_effect=counter_open), patch.object(a.time, "time", return_value=1000000000):
            with ThreadPoolExecutor(2) as executor:
                jobs = [executor.submit(sender.neue_id) for sender in (a, b)]
                ids = [job.result() for job in jobs]
        findings.append({"id": "C09", "reproduced": ids[0] == ids[1], "same_player_ids": ids})

        try:
            from lupa import LuaRuntime
        except ImportError:
            return findings + [{"id": "lua", "skipped": "lupa unavailable"}]
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute("""
            INFO=1; WARNING=2; logs={}; mem={[0x01A275DC]=1}; calls={}
            function log(level,msg) table.insert(logs,msg) end
            core={}
            function core.readInteger(a) return mem[a] or 0 end
            core.readSmallInteger=core.readInteger; core.readByte=core.readInteger
            function core.writeInteger(a,v) mem[a]=v end
            core.writeSmallInteger=core.writeInteger; core.writeByte=core.writeInteger
            function core.exposeCode(a,n,c)
              return function(...) table.insert(calls,{address=a,count=n,convention=c}); return 1 end
            end
        """)
        module = lua.execute((ROOT / "bridge/snapshots/logik_stand_20261019.lua").read_text(encoding="utf-8"))
        lua.globals().bridge = module
        lua.execute("logs={}; bridge.handleCommand({id=101,player=1,unknownAuditCommand=true})")
        response = list(lua.globals().logs.values())
        k.STRENG = True
        strict_rejected = False
        try:
            k.pruefe(response)
        except RuntimeError:
            strict_rejected = True
        findings.append({"id": "C06", "reproduced": not strict_rejected,
                         "lua_response": response, "strict_rejected": strict_rejected})

        lua.execute("""
            logs={}; bridge.handleCommand({id=102,befehle={
              {id=201,player=1,baue={x=1,y=1,mapper=51,groesse=3}},
              {id=202,player=2,baue={x=2,y=2,mapper=51,groesse=3}}
            }})
        """)
        before = list(lua.globals().logs.values())
        queued_before = len(lua.globals().calls)
        lua.execute("bridge.everyTick()")
        queued_after = len(lua.globals().calls)
        findings.append({"id": "C07", "reproduced": queued_before == 1 and queued_after == 2,
                         "response_before_execution": before, "native_calls_at_ack": queued_before,
                         "native_calls_after_tick": queued_after})

        lua.execute("""
            calls={}; mem[0x00F98338+0xAC]=123; mem[0x0059E1F4]=456;
            bridge.handleCommand({id=103,player=1,hinten=true})
        """)
        calls = [{key: call[key] for key in ("address", "count", "convention")}
                 for call in lua.globals().calls.values()]
        findings.append({"id": "C08", "reproduced": any(c["count"] == 7 and c["convention"] == 0 for c in calls),
                         "mocked_native_calls": calls})
    return findings


def main():
    results = {"revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()}
    files = list(LEGACY_FILES.values())
    syntax = []
    for p in files:
        try:
            compile(p.read_bytes(), str(p), "exec")
        except Exception as ex:
            syntax.append({"file": p.name, "error": str(ex)})
    results["python_syntax"] = {"files": len(files), "failures": syntax}
    data_failures = []
    data_files = list((ROOT / "data/research").glob("*.json"))
    for p in data_files:
        try:
            json.loads(p.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, ValueError) as ex:
            data_failures.append({"file": p.name, "error": str(ex)})
    results["json_syntax"] = {"files": len(data_files), "failures": data_failures}
    try:
        from lupa import LuaRuntime
        lua = LuaRuntime()
        lua_checks = []
        for p in (ROOT / "bridge/snapshots").glob("*.lua"):
            try:
                lua.compile(p.read_text(encoding="utf-8"))
                lua_checks.append({"file": p.name, "status": "passed"})
            except Exception as ex:
                lua_checks.append({"file": p.name, "status": "failed", "error": str(ex)})
        results["lua_syntax"] = lua_checks
    except ImportError:
        results["lua_syntax"] = {"skipped": "lupa unavailable"}
    results["connector_probes"] = connector_probes()
    tests = []
    for p in sorted(p for p in LEGACY_FILES.values() if p.name.endswith("_pruefen.py")):
        doc = (ast.get_docstring(ast.parse(p.read_bytes())) or "").lower()
        if any(marker in doc for marker in ("ohne spiel", "ohne ein spiel", "ohne laufendes spiel")):
            tests.append(p.name)
    tests += ["lordschutz_trocken.py", "brotbau_trocken.py", "sturm_trocken.py", "stillstand_trocken.py"]
    suites = []
    for name in tests:
        try:
            proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--suite", name],
                                  cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                                  timeout=45, env=dict(os.environ, PYTHONUTF8="1"))
            output = proc.stdout + proc.stderr
            status = "passed" if proc.returncode == 0 else "failed"
            if proc.returncode and "VillageStudio" in output and "FileNotFoundError" in output:
                status = "blocked_missing_VillageStudio"
            suites.append({"file": name, "status": status, "returncode": proc.returncode, "output": output})
        except subprocess.TimeoutExpired:
            suites.append({"file": name, "status": "timeout"})
        print(name, suites[-1]["status"], flush=True)
    results["offline_suites"] = suites
    results["suite_counts"] = dict(Counter(s["status"] for s in suites))
    results["notes"] = [
        "Existing suites run with a disconnected befehl stub, player 1 and instance 1; all game I/O is disabled.",
        "The partie_vergleich_pruefen failure expects a German building name; absent VillageStudio metadata makes the code emit Typ 3 instead.",
        "Connector probes report reproduced defects, not passing product requirements.",
        "Lua execution uses mocked core memory/native calls; it does not verify in-game ABI or timing.",
    ]
    output = Path(__file__).with_name("results.json")
    output.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"python_syntax": results["python_syntax"], "suite_counts": results["suite_counts"],
                      "connector_probes": results["connector_probes"]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--suite":
        offline_child(sys.argv[2])
    else:
        main()
