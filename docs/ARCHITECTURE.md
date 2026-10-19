# Architecture and migration boundaries

This branch introduces an installable **offline framework** and relocates the
current bot into the same responsibility-based package tree. Its active entry
point is `selfaware.runtime.live.erstes_spiel`; native access is under
`selfaware.game.ucp`. The new `BotRuntime` has a real replay port; connecting
the existing policies to its typed execution contracts remains implementation work. Integration work is listed in [BACKLOG.md](BACKLOG.md).

The design is informed by Sharky at
[`2628ba1`](https://github.com/sharknice/Sharky/tree/2628ba1c5c2083aeeddf9f13c25bf6f218820a05),
particularly its manager lifecycle, prioritized micro tasks, build/macro split,
and unit order tracking. The existing [Plan_Architektur.md](plans/Plan_Architektur.md)
and [source review](../audit/SHARKY_ARCHITECTURE.txt) explain the domain mapping.

## Implemented package

| Package | Responsibility |
| --- | --- |
| `domain` | Immutable session identity, entity references, resource vectors, snapshots and command proposals |
| `game` | GamePort contract, pure legacy trace decoder, streaming JSONL/gzip replay adapter |
| `coordination` | Deterministic priority selection; exclusive actors and resource bundles |
| `execution` | Action ledger, reservation lifetime, transport receipts and observed outcomes |
| `runtime` | Engine lifecycle, feedback, observe/propose/select/submit loop and failure isolation |
| `config`, `diagnostics`, `cli` | Explicit local paths, read-only dependency inventory and offline commands |

Policy engines receive a read-only snapshot. They return `Intent` objects and
never call legacy `sende`, `peek`, or native memory functions. Only a GamePort
performs external I/O. Instance, player and game epoch are explicit `Session`
values. Engine instances and ledgers belong to one runtime/player context.
A live GamePort must be a per-session view over the instance's shared broker;
closing one view must not close another player or terminate the game.

## Decision and execution cycle

1. Observe the current session; reject foreign, reused or backwards samples.
2. Validate the complete outcome batch and reconcile existing reservations.
3. Deliver verified outcomes to engines; materialize each engine's proposal batch.
4. Sort by descending priority, engine name and intent ID. Reject stale/dead/
   foreign/reused entities, missing UIDs, duplicate IDs and conflicting claims.
5. Select whole resource bundles. Subtract pending commitments before selecting
   new proposals. Log a reason for every acceptance/denial.
6. Submit selected actions serially. A transport fault marks the affected action
   unresolved and stops further submissions for that cycle. Unsent selections
   are not recorded as dispatched or reserved in the ledger.

`CycleReport.decisions` reports planning decisions, not dispatch success. Its
`receipts` records successful transport calls. The ledger is authoritative for
pending state; an exception can leave a submitted action unresolved.

## Evidence and reservations

`reserved -> received -> dispatched` does **not** establish a game effect.
Confirmation needs an `ObservedOutcome` from a different, later observation
with an evidence description. The adapter is responsible for verifying the
actual cost/entity/order postcondition; the ledger validates provenance and
state transitions, not arbitrary free-text claims against game physics.

An ambiguous timeout keeps the action's resource and actor reservations. There
is no automatic retry, timeout-based lock theft or automatic release. Explicit
rejection/cancellation or observed confirmation ends the commitment. This is
conservative; an eventual live adapter needs reconciliation/watchdog tooling.

Observed stock may already reflect a pending debit. Until the adapter confirms
and reconciles that action, the allocator conservatively retains its reservation;
this can temporarily under-allocate. Budget optimization is a later step.

## Deliberate limits

- The planner is a greedy priority allocator, not an economic optimizer. It
  does not yet implement production-chain planning, footprint reservations,
  long-lived tactical leases or automatic preemption of in-flight commands.
- Actor claims last while an action is pending. Higher priority can win a fresh
  conflict; it cannot steal an in-flight action. Add explicit cancellation and
  observation before implementing tactical preemption.
- Existing traces omit each unit's own UID. `zieluid` belongs to its target.
  Unknown identity is preserved; actor/target-based proposals using it are denied.
- Replay provides historical observations. It never fabricates action success
  or predicts a new policy's match outcome. The CLI's replay mode is observation-only.
- No legacy economy/attack policy has silently been replaced. Port one engine
  at a time, with recorded-decision checks and separate actual-match evaluation.
- No native address/calling convention has been validated by this branch.
- IDs/records are retained for the runtime's game epoch. Long-running sessions
  will need measured retention/trace policies without forgetting pending work.

## Current implementation and next boundaries

The existing `macro`, `micro/tasks`, `micro`, `strategy`, `services`, `learning`
and `telemetry` packages contain the actual current implementation. Files were
moved, imports qualified, and shared data/process paths updated. The original
flat `werkzeug/` tree is retired. [ORGANIZATION.md](ORGANIZATION.md) maps key
classes to their destinations; the complete manifest is [relocations.json](relocations.json).

The current `Wirtschaft`, `Waechter`, `Angriffstrupp`/`Einzeln`, `Feldzug` and
`Raids` still have their existing interfaces and game I/O. They are not yet
`runtime.Engine` implementations. The active live runner still owns its
existing loop. Package location is not evidence that typed arbitration,
reservations or observed outcomes govern those old command paths.

Keep `Haushalt` as fiscal/popularity policy; the resource allocator is a
separate responsibility. Reuse `execution.auftragsbuch` for observed building
effects, `services.uebersicht` for derived state, `micro.zuweisung` for combat
assignment, and the measured economy/visibility/combat models. Extract
controllers and long-lived tasks as those implementations migrate to `Engine`.

Keep lifecycle/configuration code in the runtime, protocol/native details in
the game adapter, decisions in policies, and experiments in explicit profiles.
Preserve Crusader's worker logistics and native climbing/pathing behavior.
