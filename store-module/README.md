# Selfaware AI Bridge — Store review candidate

This module is a bridge to the separately installed Selfaware application.
It does not install or start Python, unpack a runtime, write command files,
save snapshots or persist learned models. UCP loads its Lua and native DLL
from the module ZIP through its own read-only/proxied infrastructure.

Communication is a bounded, pagefile-backed Windows allocation tied to the
game process. Requests and replies use sequence/consumption counters; delayed
responses cannot be overwritten, and an uncertain command is never replayed.
The external application writes its own observations and learning under
Documents/Selfaware AI. The game module's named resource streams are volatile
binary response records, not files opened by the game module.

Screenshot/export-to-disk, save/load, dynamic DLL replacement and desktop/window
commands are unavailable, including when nested in deferred command batches.
The native Store feature compiles out the old kernel log, snapshot-file writer
and discovery-file writer. Its diagnostics use a bounded in-memory queue.

The tactical implementation and frame-zero SamurAI takeover are shared with
the local prototype. Generated release sources are checked against their
canonical source hashes in source-manifest.json. This folder builds independently
with build.ps1 and Cargo.lock; files.xml packages only the module, not its tools,
source snapshot, external app or development probe.

Supported engine: Stronghold Crusader 1.41, UCP 3.0.7. Function hooks check known
instruction signatures. The game logic still uses version-specific engine
offsets; this is not a universal engine interface or complete OpenSHC port.
Store approval and certificate signing remain decisions of the UCP maintainers.
No approval is implied by this candidate or its offline checks.

Install the matching Selfaware AI content entry and the separate external app,
then start through Selfaware AI (lokal). The production external app requires
the Store's signed module and keeps secure mode enabled. A separately labelled
unsigned review bundle is for isolated developer tests only.
