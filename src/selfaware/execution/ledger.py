from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from selfaware.domain import EntityRef, Intent, Resources, Session, Snapshot
from selfaware.game.ports import Observation, ObservedOutcome, OutcomeStatus, Receipt, ReceiptStatus


class ActionStatus(str, Enum):
    RESERVED = "reserved"
    RECEIVED = "received"
    DISPATCHED = "dispatched"
    UNRESOLVED = "unresolved"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


TERMINAL = frozenset({ActionStatus.CONFIRMED, ActionStatus.REJECTED, ActionStatus.CANCELLED})


@dataclass(frozen=True)
class ActionRecord:
    intent: Intent
    created_tick: int
    status: ActionStatus = ActionStatus.RESERVED
    detail: str = ""
    observed_snapshot_id: str | None = None
    was_dispatched: bool = False


class ActionLedger:
    def __init__(self, session: Session) -> None:
        self.session = session
        self._records: dict[str, ActionRecord] = {}

    @property
    def records(self) -> tuple[ActionRecord, ...]:
        return tuple(self._records.values())

    @property
    def pending(self) -> tuple[ActionRecord, ...]:
        return tuple(r for r in self.records if r.status not in TERMINAL)

    @property
    def reserved(self) -> Resources:
        total = Resources()
        for record in self.pending:
            total = total.plus(record.intent.cost)
        return total

    @property
    def claimed(self) -> frozenset[EntityRef]:
        return frozenset(ref for record in self.pending for ref in record.intent.actors)

    def contains(self, action_id: str) -> bool:
        return action_id in self._records

    def register(self, snapshot: Snapshot, intent: Intent) -> None:
        if snapshot.session != self.session or intent.snapshot_id != snapshot.snapshot_id:
            raise ValueError("action and ledger must belong to the current observation/session")
        if self.contains(intent.intent_id):
            raise ValueError(f"action ID already used: {intent.intent_id}")
        self._records[intent.intent_id] = ActionRecord(intent, snapshot.tick)

    def receive(self, receipt: Receipt) -> None:
        if not isinstance(receipt.status, ReceiptStatus):
            raise ValueError("a receipt cannot confirm an observed game effect")
        record = self._records[receipt.action_id]
        if record.status in TERMINAL:
            raise ValueError("cannot update a terminal action with a transport receipt")
        status = ActionStatus(receipt.status.value)
        if record.was_dispatched and status == ActionStatus.RECEIVED:
            raise ValueError("cannot regress a dispatched action to received")
        if record.was_dispatched and status == ActionStatus.REJECTED:
            raise ValueError(
                "a dispatched action needs an observed rejection, not a transport receipt"
            )
        self._records[receipt.action_id] = replace(
            record,
            status=status,
            detail=receipt.detail,
            was_dispatched=record.was_dispatched or status == ActionStatus.DISPATCHED,
        )

    def unresolved(self, action_id: str, detail: str) -> None:
        record = self._records[action_id]
        if record.status in TERMINAL:
            raise ValueError("cannot make a terminal action unresolved")
        # Keep resources and actors reserved: delivery may have succeeded.
        self._records[action_id] = replace(record, status=ActionStatus.UNRESOLVED, detail=detail)

    def reconcile(self, observation: Observation) -> tuple[ObservedOutcome, ...]:
        snapshot = observation.snapshot
        if snapshot.session != self.session:
            raise ValueError("observation belongs to another session")
        updates: dict[str, ActionRecord] = {}
        fresh_outcomes = []
        for outcome in observation.outcomes:
            if not isinstance(outcome.status, OutcomeStatus):
                raise ValueError("unsupported observed outcome")
            if outcome.snapshot_id != snapshot.snapshot_id or not outcome.detail.strip():
                raise ValueError("outcomes need evidence from the current observation")
            record = updates.get(outcome.action_id, self._records.get(outcome.action_id))
            if record is None or snapshot.tick < record.created_tick:
                raise ValueError(
                    f"unknown action or outcome predates submission: {outcome.action_id}"
                )
            if outcome.snapshot_id == record.intent.snapshot_id:
                raise ValueError("an outcome must come from a later observation than the proposal")
            status = ActionStatus(outcome.status.value)
            if record.status in TERMINAL:
                if record.status != status:
                    raise ValueError("contradictory terminal outcomes")
                continue
            updates[outcome.action_id] = replace(
                record,
                status=status,
                detail=outcome.detail,
                observed_snapshot_id=snapshot.snapshot_id,
            )
            fresh_outcomes.append(outcome)
        # Validate the complete sample before committing any state changes.
        self._records.update(updates)
        return tuple(fresh_outcomes)
