from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass

from selfaware.domain import Intent, Snapshot
from selfaware.execution import ActionLedger


@dataclass(frozen=True)
class Decision:
    intent: Intent
    accepted: bool
    reason: str


class Planner:
    """Greedy priority selection, not a global economic optimizer.

    Claims last while actions are pending. Preempting a dispatched action needs
    an observed cancellation; a higher score cannot steal its reservation.
    Longer-lived tactical task leases are a separate migration step.
    """

    def select(
        self,
        snapshot: Snapshot,
        proposals: Iterable[Intent],
        ledger: ActionLedger,
    ) -> tuple[Decision, ...]:
        if ledger.session != snapshot.session:
            raise ValueError("planner cannot share a ledger across players/games")
        proposals = tuple(proposals)
        counts = Counter(intent.intent_id for intent in proposals)
        claimed = set(ledger.claimed)
        available = snapshot.resources.available_after(ledger.reserved)
        decisions = []
        for intent in sorted(proposals, key=lambda p: (-p.priority, p.engine, p.intent_id)):
            reason = "selected"
            if counts[intent.intent_id] > 1:
                reason = "duplicate_intent_id"
            elif ledger.contains(intent.intent_id):
                reason = "action_id_already_used"
            elif intent.snapshot_id != snapshot.snapshot_id:
                reason = "stale_snapshot"
            elif intent.valid_until_tick < snapshot.tick:
                reason = "deadline_expired"
            elif any(ref.uid is None for ref in intent.actors + intent.targets):
                reason = "entity_uid_unavailable"
            elif any(snapshot.entity(ref) is None for ref in intent.actors + intent.targets):
                reason = "entity_missing_or_replaced"
            elif any(
                snapshot.entity(ref).owner != snapshot.session.player for ref in intent.actors
            ):
                reason = "actor_not_owned"
            elif any(snapshot.entity(ref).health <= 0 for ref in intent.actors + intent.targets):
                reason = "entity_dead"
            elif claimed.intersection(intent.actors):
                reason = "actor_reserved"
            elif not available.covers(intent.cost):
                reason = "insufficient_unreserved_resources"
            accepted = reason == "selected"
            decisions.append(Decision(intent, accepted, reason))
            if accepted:
                claimed.update(intent.actors)
                available = available.available_after(intent.cost)
        return tuple(decisions)
