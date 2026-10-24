# Selfaware AI 0.1.0 — packaging candidate

UCP 3.0.7, Stronghold Crusader 1.41 (32-bit game, 64-bit Windows controller).
Select **Selfaware AI** in Content, apply, start Crusader normally, select
**SamurAI** in a fresh custom skirmish. The other lords keep their configured AI.
The controller starts with the game and exits with it. No LLM account, Python
installation, mouse/keyboard automation, old save or development checkout is needed.

Under Customisations, **Selfaware AI: Starteinheiten** sets the starting roster
for the packaged Abbot slot in new matches. Defaults are 4 assassins and 6 Arabian
archers, replacing rather than supplementing the inherited monks. Every supported
troop count is editable, including zero; totals above 100 are rejected before any
native writes. Other AI slots keep their existing starting troops. This is a
moderate proposed preset, not an experimentally proven balance guarantee.

The current game's native bridge and kernel 19 are bundled without tactical
changes. The existing online learner measures damage and movement, persists its
model and automatically reads it in subsequent decisions. Per-match receipts
record good/bad observations and distinguish native outcomes from unverified
interruptions. These are measured model updates, not general autonomous source
code rewriting or proof of stronger play.

State and learning: `%LOCALAPPDATA%\Selfaware AI\<game-path-hash>\<runtime-hash>`.
Startup trace and errors: `bootstrap-<game-pid>.log`; worker output:
`worker-<game-pid>.log`, both in the game-path state directory. Startup uses .NET
APIs so a missing PowerShell module search path does not silently prevent it.
Each runtime revision
has separate state so incompatible model formats cannot silently mix. Learned
mechanic models are also separated by the effective UCP configuration; changing
balance profiles does not silently reuse incompatible measurements.

The official Store must build/sign the runtime module and accept the recipe.
An unsigned development ZIP is not a secure-mode release. Do not advise users to
disable security as the permanent installation procedure. This candidate is not
declared released until both secure-mode loading and a fresh menu match pass.
