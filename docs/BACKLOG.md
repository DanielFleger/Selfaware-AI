# Engineering acceptance details

The authoritative task/status list is [backlog/backlog.json](backlog/backlog.json),
with its generated [Backlog.html](backlog/Backlog.html). This document supplies
engineering acceptance details for those points; it is not a second status list.

| Acceptance section | Authoritative points |
| --- | --- |
| LIVE-01 / LIVE-02 | B-94, B-104 |
| ENV-01 / MIGRATE-01 | B-97 |
| MIGRATE-02 | B-98 |
| MIGRATE-03 | B-99 |
| SCALE-01 | B-101 |
| DATA-01 | B-95 |
The source audit is [audit/AUDIT.txt](../audit/AUDIT.txt), against `7b994b7`.
The old [Backlog.md](research/Backlog.md) remains the historical gameplay/research backlog.

## Implemented here

- Installable package, locked development dependencies, Windows/Linux CI.
- Immutable snapshots/session identity, typed proposals, explicit entity UIDs.
- Priority selection, whole-resource reservations and pending-action claims.
- Action receipt/outcome separation, ambiguous-delivery reservation retention.
- Replay of existing JSONL/gzip records; read-only live dependency diagnostics.
- Failure-path tests and agent onboarding. All 176 current-bot modules are relocated by responsibility; evidence hashes
  and the old/new path manifest are checked. Selected current offline checks
  run through the new launcher from an unrelated working directory.

## LIVE-01 — Reliable single-owner UCP adapter (first)

Audit findings 1–5 and 7 remain **open in the old connector/module**:

- A live sender lock can be stolen after 8 seconds while the response wait is 20.
- Same-player concurrent senders can allocate duplicate IDs before locking.
- Timeouts can return normally without an exact request acknowledgement.
- Single-command false returns can escape strict error checks.
- `hinten` can reach the documented unsafe SetWindowPos ABI path.
- Deferred commands can be counted as executed before native dispatch.
- Partner ownership cleanup compares `<pid> partner` with `<pid>` and fails.

The latest upstream [Spielkarte](research/Spielkarte.md) (B-114) documents that
single-player native queue execution uses `currentPlayerSlotID`, ignoring the
queued sender. A Python Session/player value alone therefore establishes no
native isolation. Preserve B-94: verify the actual execution player and human
input separation before supporting multiple player contexts. The proposed
translation change in that research is not implemented or validated here.

Acceptance: obtain and pin the real module; cover same-player and cross-player
concurrency, crashed/slow owners, exact response correlation, ambiguous timeout,
single/batch/deferred results and native queue ordering. Deny the unsafe native
operation. Confirm costs/entities/orders from later observations. Do not retry
non-idempotent commands blindly. Expose actual entity UID in observations.

The new offline contracts model these requirements; they do not replace the
live writer or constitute a fix to its implementation.

## LIVE-02 — Complete guard coverage

Audit finding 6 remains open: direct commands bypass `lordschutz.filtern`.
Normalize supported envelopes and test through the common executor. Keep game
legality and configurable experiment rules distinct. Verify behavior with the
actual Lord/unit IDs and tick state; avoid inventing IDs or game facts.

## ENV-01 — Pin external data/module dependencies

Audit finding 8 remains open: VillageStudio metadata and process helpers are
missing, and many old "offline" tests import them or a game install. Declare
their actual source/revision/hash. Separate data/model loading from game path
validation. Make old pure tests importable without live setup. The diagnostic
does not silently reconfigure those legacy imports.

## MIGRATE-01 — Snapshot and world services

Adapt runde_lesen/Uebersicht to one versioned sample, expose freshness and own
entity UIDs, and extract shared visibility/threat/path/combat queries. Keep
unsupported facts unknown. Introduce explicit profiles/observation policy.

## MIGRATE-02 — Defense, raids and commanders

Wrap waechter/assassinen/feldzug/raids behind Engine. Reuse zuweisung's measured
combat assignment. Introduce long-lived task ownership, preemption/cancellation
and commander duplicate/stuck-order recovery. All participating tasks must
obey one authority before mixing migrated and legacy policy behavior.

Acceptance: no conflicting orders, no stale UID reuse, no duplicate pending
operation, explicit preemption/release, and recorded-decision comparisons plus
controlled live regression evidence.

## MIGRATE-03 — Budgeted macro and strategy

Extract economy, food/popularity and production-chain proposals. Reuse
Auftragsbuch's confirmations and the measured yield models. Extend reservation
dimensions to workers, production capacity and building footprints. Retire
braucht_gold flags incrementally. Fiscal Haushalt remains its own policy.

Acceptance: critical constraints/commitments precede optional returns; building,
recruitment and trade proposals cannot spend the same stock; pending costs are
reconciled without permanent reservation or duplicate accounting.

## SCALE-01 — Scheduling, telemetry, learning

Measure sample age, policy runtime, command queue/effect delay and invalid-run
rate. Schedule urgent tasks separately from slow map/macro work. Cache derived
queries and bound per-game records after measuring retention needs. Add
parallel read-only calculation only when profiling supports it; keep one writer.

Make policy/model/experiment manifests reproducible. Compare repeated controlled
matches and side swaps. Keep tuning/evaluation apart; do not turn corrupted or
technically invalid runs into strategic losses. Replay is a decision test,
not a counterfactual simulator or a win-rate benchmark.

## DATA-01 — Incoherent recorded observation (confirmed during setup)

Reading `data/research/lage_20261018_162313_i1.jsonl.gz` succeeds for its first three
samples, then rejects line 37: record/status tick is 2208, but the embedded unit
table says `tick 2147`. That is an existing capture inconsistency, not a parser
syntax failure. Reproduce with:

```sh
uv run selfaware replay data/research/lage_20261018_162313_i1.jsonl.gz --player 1 --limit 37
```

Investigate stale/failed command responses and how `runde_lesen` and
`Lageprotokoll.schreibe` combine status and file dumps. Preserve the original
archive. Any salvage tool should flag discarded/mixed samples and cannot
claim they are coherent learning/evaluation data. This observation supports
the need for a versioned, coherent snapshot contract in the live adapter.
