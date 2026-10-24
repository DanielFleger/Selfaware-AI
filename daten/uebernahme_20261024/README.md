# Observer commands and first-tick takeover, 24 October 2026

Daniel's actual match on `!KOphase Map 1` had two SamurAI, observer slot zero,
one inherited hop farm per side, and no successful controller construction. The
previous automated menu fixture explicitly set `eigenerPlatz: 1`; that masked
the observer bug. Prior worker/bootstrap changes did not fix this command path.

Root contracts were read from existing decompilation:
`daten/dekomp_absender.c`, `daten/dekomp_queuecommand.c`, and
`daten/dekomp_befehl_ausfuehren.c`. Native selection resolves command owners and
rejects neutral zero BEFORE the existing sender hook at execution. A tagged
owner must therefore resolve at selection too, while ordinary IDs retain the
native result. `command_owner.lua` hooks the native thiscall converter at
0x47EAF0, verifying its six original instruction bytes before installation.

Placeholder suppression now runs in the native bridge BEFORE processGameTick,
not in the later Python polling loop. Its session receipt records selected slots
and exact takeover tick; the watcher uses that receipt and does not pause play.
Native slot/full-ID state is restored when returning to the lobby. Source
`takeover.lua`, `command_owner.lua`, and two real-Lua tests are included.

Validation used Daniel's map and two SamurAI, through native menu handlers,
without saves, input simulation, or `eigenerPlatz` correction:

- Full observer self-play: takeover tick 0, both controllers construct economic
  buildings, recruit and attack. Native receipts record player 1's defeat and
  player 2's victory. This is an integration test, not a strength benchmark.
- Actual no-worker counterexample: deliberately stop the watcher before starting
  a fresh match. At ticks 509 and 1008 the same 18 initial buildings remain,
  both native AI slots are zero, and no farm is added. Leaving restores both
  lobby AI values to 16. See no-worker-probe.json.
- Final normal restart: native takeover tick 0, observer remains zero, and
  direct building-table reads find 22/19 additional non-initial objects by
  tick 471. These counts include associated stone piles; do not call them
  22/19 productive workplaces. Both lobby AI values are restored after leaving.
  The short final test is aborted, not called a win.

Before and after controller transcripts, generated maps/plans, learning
receipts and compressed native logs are preserved. No screenshots are included.
The installed local candidate remains unsigned; official Store signing/review
and secure-mode acceptance are still pending.
