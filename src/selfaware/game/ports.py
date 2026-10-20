from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from selfaware.domain import Intent, Session, Snapshot


class ReceiptStatus(str, Enum):
    RECEIVED = "received"
    DISPATCHED = "dispatched"
    REJECTED = "rejected"


class OutcomeStatus(str, Enum):
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Receipt:
    action_id: str
    status: ReceiptStatus
    detail: str = ""


@dataclass(frozen=True)
class ObservedOutcome:
    action_id: str
    status: OutcomeStatus
    snapshot_id: str
    detail: str


@dataclass(frozen=True)
class Observation:
    snapshot: Snapshot
    outcomes: tuple[ObservedOutcome, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "outcomes", tuple(self.outcomes))


class GamePort(Protocol):
    """A session-scoped view of one game-instance channel owner.

    Each runtime gets its own view; a live adapter shares a single underlying
    broker across player views. close releases only this view, never another
    player's context or the game process. Player state belongs to its Session.

    submit must return REJECTED only when the action was never dispatched.
    Transport exceptions are ambiguous. Confirmation requires a later observed
    effect, supplied as an ObservedOutcome tied to that sample, not an ACK.
    A live adapter must implement capabilities/version checks before use.
    """

    def observe(self, session: Session) -> Observation: ...

    def submit(self, session: Session, intent: Intent) -> Receipt: ...

    def close(self) -> None: ...
