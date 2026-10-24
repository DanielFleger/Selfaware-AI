# Starting troops and local startup correction, 24 October 2026

The user reported idle SamurAI with inherited monks and requested configurable
starting troops that can raid and defend. The proposed moderate default is four
assassins and six Arabian archers, replacing the Abbot roster in all three match
modes. It is not claimed to be experimentally balanced. No other lord's starting
roster or existing tactical controller was changed.

`starttroops.lua` uses the exact native table contract from the installed
aiSwapper 1.3.0 `scripts/troops.lua`; it validates all counts before writing only
the Abbot slot. UCP numeric settings allow every supported unit, including zero.
The runtime explicitly depends on aiSwapper so its override runs after AI swaps.
Three Lua tests exercise real Lua with neighbouring-slot sentinels, custom/zero
counts, all modes, inherited monks, and rejected configurations with no writes.

The fresh native-menu match automatically launched both controllers. At tick 708,
each had six Arabian archers and five assassins: four starters plus one recruited
by the existing opener. Console evidence records early movement/attack orders and
destruction of economic buildings. The match was explicitly left, not scored as
a victory. Native-table reads separately verify the intended roster in all modes.

The user's prior native log reported the worker launch request but the old shared
worker log had no corresponding readiness entry. PowerShell module autoloading
disabled is a reproduced failure condition: the old bootstrap fails at Join-Path
(exit 1), the corrected .NET-only bootstrap starts its worker and exits cleanly
(exit 0, isolated fixture with a dead game PID). This proves a fixed failure class,
not that missing modules were conclusively the sole cause of the user's report.
Per-game bootstrap/worker logs now remove shared-output collisions and reveal
startup failures. See verification.json, native snapshots, receipts and logs.

Unsigned local setup only; official signing and Store review are still pending.
Commands: `python werkzeug/starttruppen_pruefen.py`,
`python werkzeug/samurai_zuordnung_pruefen.py`,
`python werkzeug/lernbuch_pruefen.py`; native probes use read-only process memory.
