from __future__ import annotations

from dataclasses import dataclass

from selfaware.coordination import Decision, Planner
from selfaware.domain import Session, Snapshot
from selfaware.execution import ActionLedger
from selfaware.game.ports import GamePort, Receipt
from selfaware.runtime.engine import Engine


@dataclass(frozen=True)
class CycleReport:
    snapshot: Snapshot
    decisions: tuple[Decision, ...]
    receipts: tuple[Receipt, ...]
    errors: tuple[str, ...]


class BotRuntime:
    def __init__(self, session: Session, port: GamePort, engines: tuple[Engine, ...] = ()) -> None:
        self.session, self.port, self.engines = session, port, tuple(engines)
        names = [engine.name for engine in self.engines]
        if len(names) != len(set(names)):
            raise ValueError("engine names must be unique within a player context")
        self.ledger = ActionLedger(session)
        self.planner = Planner()
        self._started = False
        self._started_engines: list[Engine] = []
        self._closed = False
        self._previous: Snapshot | None = None
        self._seen_snapshot_ids: set[str] = set()

    def step(self) -> CycleReport:
        if self._closed:
            raise RuntimeError("runtime is closed")
        if not self._started:
            try:
                for engine in self.engines:
                    engine.on_start(self.session)
                    self._started_engines.append(engine)
            except Exception:
                self.close()
                raise
            self._started = True
        observation = self.port.observe(self.session)
        snapshot = observation.snapshot
        if snapshot.session != self.session:
            raise ValueError("port returned another player's/game's observation")
        if self._previous is not None:
            if snapshot.tick < self._previous.tick:
                raise ValueError("tick moved backwards; start a new game epoch/runtime")
        if snapshot.snapshot_id in self._seen_snapshot_ids:
            raise ValueError("port repeated an observation ID")
        fresh_outcomes = self.ledger.reconcile(observation)
        self._previous = snapshot
        self._seen_snapshot_ids.add(snapshot.snapshot_id)
        proposals, errors = [], []
        for engine in self.engines:
            try:
                engine.on_outcomes(fresh_outcomes)
                # Materialize first: a generator failure must not leave half a plan.
                proposed = tuple(engine.propose(snapshot))
                if any(intent.engine != engine.name for intent in proposed):
                    raise ValueError("proposal engine identity does not match its producer")
                proposals.extend(proposed)
            except Exception as error:
                errors.append(f"engine {engine.name}: {type(error).__name__}: {error}")
        decisions = self.planner.select(snapshot, proposals, self.ledger)
        receipts = []
        for decision in decisions:
            if not decision.accepted:
                continue
            intent = decision.intent
            self.ledger.register(snapshot, intent)
            try:
                receipt = self.port.submit(self.session, intent)
                if receipt.action_id != intent.intent_id:
                    raise ValueError("transport receipt belongs to another action")
                self.ledger.receive(receipt)
                receipts.append(receipt)
            except Exception as error:
                detail = f"transport: {type(error).__name__}: {error}"
                self.ledger.unresolved(intent.intent_id, detail)
                errors.append(detail)
                # Do not continue sending into an unhealthy transport. Later
                # selected proposals were never registered/submitted and can
                # be planned again from a fresh sample.
                break
        return CycleReport(snapshot, decisions, tuple(receipts), tuple(errors))

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        errors = []
        try:
            for engine in self._started_engines:
                try:
                    engine.on_end()
                except Exception as error:
                    errors.append(error)
        finally:
            self.port.close()
        if errors:
            raise errors[0]

    def __enter__(self) -> BotRuntime:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
