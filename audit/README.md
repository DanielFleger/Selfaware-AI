# Baseline audit and architecture research

- `AUDIT.txt`: prioritized source audit of live-code baseline `7b994b7`.
- `SHARKY_ARCHITECTURE.txt`: detailed source mapping and migration proposal.
- `sharky_architecture.html`: standalone interactive architecture comparison.
- `run_checks.py`: isolated bug reproductions and selected old offline scripts.

The audit runner reports **known defects**, including reproductions that are
expected to return `reproduced: true`. Its exit status means the diagnostic run
completed, not that product requirements passed. It is not the new CI gate.

```sh
uv sync --locked --extra dev --extra audit
uv run python audit/run_checks.py
```

It writes `audit/results.json` (ignored). The runner disconnects game I/O and
limits its fixture writes to temporary directories. Its baseline selected
38 scripts: 20 passed, 17 lacked VillageStudio metadata, and one failed a
metadata-dependent name assertion. These counts can change when that legacy
work is migrated; diagnose changes rather than treating them as approvals.

`audit/lint.json` is also generated and ignored. Historical machine paths and
tool versions in the baseline reports are provenance, not installation settings.
Current integration status lives in [docs/BACKLOG.md](../docs/BACKLOG.md).

The runner now resolves relocated modules through `selfaware.module_registry`
and Lua snapshots through `bridge/snapshots/`. Written baseline findings remain
unchanged historical evidence. The isolated run after relocation retained the
same 20 passing / 17 metadata-blocked / 1 metadata-dependent failing suites.

Latest upstream also adds the B-94 sender-tag patch and its explicit offline
validator (`uv run --extra audit selfaware run absender_pruefen`). The original
Lua audit mock does not activate that machine-code patch; its deferred-command
probe therefore exercises the fallback path. It does not refute the separate
upstream B-94 evidence or validate the patched native execution path.
