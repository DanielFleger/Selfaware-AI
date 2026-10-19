from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from selfaware.domain import Intent, Session, Snapshot
from selfaware.game.ports import ObservedOutcome


class Engine(ABC):
    """A policy sees immutable samples and returns proposals, never game I/O.

    Store any policy state on the engine instance, scoped to one BotRuntime.
    Give proposal IDs an engine namespace; reuse an ID while awaiting its
    result, then use a new ID for a deliberate new attempt.
    """

    @property
    def name(self) -> str:
        return type(self).__name__

    def on_start(self, session: Session) -> None:
        """Optional per-session setup, before the first decision."""
        return None

    def on_outcomes(self, outcomes: tuple[ObservedOutcome, ...]) -> None:
        """Optional feedback from outcomes verified by the observation adapter."""
        return None

    @abstractmethod
    def propose(self, snapshot: Snapshot) -> Iterable[Intent]:
        raise NotImplementedError

    def on_end(self) -> None:
        """Optional cleanup; called once for every successfully started engine."""
        return None
