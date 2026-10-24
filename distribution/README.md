# Selfaware AI 0.1.0 — separate local development mod

This is NOT a Store-compatible module. The Store proposal was withdrawn on
24 October 2026 after maintainer review. Signing the old prototype alone would
not make it acceptable. Preserve a working local mod before redesigning its API.

## Install and play

Extract Selfaware-AI-local-0.1.0.zip to a normal folder and run setup.ps1 with
PowerShell. Choose the Crusader game folder. The installer creates the desktop
shortcut **Selfaware AI (lokal)**. No separate Python installation, LLM account,
development checkout, mouse/keyboard automation or old save is needed.
Requirements: 64-bit Windows, UCP 3.0.7, Stronghold Crusader 1.41.

The separate installer unpacks the portable runtime under Local AppData. The
external starter launches the game, waits for the native bridge readiness
message, then starts the controller. It reports startup failures visibly.
The game module neither unpacks nor launches the external runtime.
The existing runtime directory and learned models are reused when unchanged;
upgrades preserve backups and keep incompatible runtime revisions separate.

Select SamurAI in a fresh custom skirmish. It occupies the Abbot slot; other
configured lords remain available. The native bridge disables its placeholder
before simulation tick zero, independently of worker readiness. The worker reads
the selected slots from a native receipt. Returning to the menu restores the
lobby choices. Observer slot zero is supported without changing the local player.

Under Customisations, **Selfaware AI: Starteinheiten** sets the starting roster.
Default: 4 assassins and 6 Arabian archers instead of inherited monks. Supported
counts are editable, including zero; totals above 100 are rejected before writes.
Other AI slots retain their configured troops. This is a proposed moderate preset,
not an experimentally proven balance guarantee.

## Learning and evidence

Selfaware is the project name, not a claim of consciousness. The existing online
learner persists measured damage and movement models for later decisions. Match
journals distinguish native outcomes from interruptions. This does not mean
arbitrary autonomous code rewriting or demonstrate improved overall strength.

State: Local AppData/Selfaware AI/<game-path-hash>/<runtime-hash>.
The parent directory holds local-start.log, bootstrap-<pid>.log and worker-<pid>.log.
Mechanic models also have separate profiles for effective UCP balance settings.
No tactical algorithm changes are included in this packaging correction.

## Remaining Store blockers

The native bridge is still LOCAL DEVELOPMENT: legacy file communication and
snapshots access game directories; some engine bindings use fixed addresses.
Moving extraction and learning outside UCP does not fix these remaining issues.
The shortcut's --ucp-no-security argument applies only to this local development
copy; the installer does not globally disable UCP security.

A future Store bridge must use reviewed communication and UCP infrastructure,
load entirely from its signed in-memory ZIP, only read its own directory, create
no files or persistent state, and have inspectable source-to-binary builds.
Do not resubmit this legacy bridge as compliant. An external mod can remain
separate while the minimal bridge is redesigned and reviewed.

The pinned OpenSHC source in openshc-reference.json is a read-only reference for
engine types, offsets and function semantics. The new owner resolver uses a
verified instruction signature. No OpenSHC DLL was built or installed, and this
is not a reconstruction or understanding of every line of the game.
