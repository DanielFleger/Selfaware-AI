from __future__ import annotations

import pytest

from selfaware.execution import ActionStatus
from selfaware.game.ports import Observation, ObservedOutcome, OutcomeStatus, Receipt, ReceiptStatus
from selfaware.game.replay import ReplayPort
from selfaware.runtime import BotRuntime, Engine


class TestEngine(Engine):
    __test__ = False

    def __init__(self, name, propose):
        self._name, self._propose = name, propose
        self.started, self.ended = 0, 0

    @property
    def name(self):
        return self._name

    def on_start(self, session):
        self.started += 1

    def propose(self, snapshot):
        return self._propose(snapshot)

    def on_end(self):
        self.ended += 1


def test_real_loop_deduplicates_pending_action_and_calls_lifecycle_once(snapshot, intent, evolve):
    second = evolve(snapshot, snapshot_id="sample-2", tick=101)
    port = ReplayPort((Observation(snapshot), Observation(second)))
    engine = TestEngine("raid", lambda s: (evolve(intent, snapshot_id=s.snapshot_id),))
    with BotRuntime(snapshot.session, port, (engine,)) as runtime:
        first = runtime.step()
        last = runtime.step()
        assert len(first.receipts) == 1
        assert last.decisions[0].reason == "action_id_already_used"
        assert runtime.ledger.records[0].status == ActionStatus.RECEIVED
        assert len(port.submitted) == 1
    runtime.close()
    assert engine.started == engine.ended == 1


def test_failed_policy_generator_cannot_leak_partial_commands(snapshot, intent):
    def fails(_):
        yield intent
        raise RuntimeError("calculation failed")

    port = ReplayPort((Observation(snapshot),))
    with BotRuntime(snapshot.session, port, (TestEngine("raid", fails),)) as runtime:
        cycle = runtime.step()
        assert not cycle.decisions and not port.submitted
        assert "calculation failed" in cycle.errors[0]


def test_transport_failure_stops_batch_and_keeps_ambiguous_action_reserved(
    snapshot, intent, evolve
):
    class FailingPort(ReplayPort):
        def submit(self, session, intent):
            super().submit(session, intent)
            raise TimeoutError("reply lost after submission")

    other = evolve(
        intent,
        intent_id="raid:second",
        actors=(snapshot.entities[1].ref,),
        cost=evolve(intent.cost, amounts={}),
    )
    port = FailingPort((Observation(snapshot),))
    with BotRuntime(
        snapshot.session, port, (TestEngine("raid", lambda _: (intent, other)),)
    ) as runtime:
        cycle = runtime.step()
        assert len(port.submitted) == len(runtime.ledger.pending) == 1
        assert runtime.ledger.pending[0].status == ActionStatus.UNRESOLVED
        assert "TimeoutError" in cycle.errors[0]


def test_foreign_receipt_does_not_resolve_current_request(snapshot, intent):
    class WrongReceipt(ReplayPort):
        def submit(self, session, intent):
            return Receipt("another-action", ReceiptStatus.RECEIVED)

    with BotRuntime(
        snapshot.session,
        WrongReceipt((Observation(snapshot),)),
        (TestEngine("raid", lambda _: (intent,)),),
    ) as runtime:
        cycle = runtime.step()
        assert "another action" in cycle.errors[0]
        assert runtime.ledger.pending[0].status == ActionStatus.UNRESOLVED


@pytest.mark.parametrize("field,value", [("tick", 99), ("snapshot_id", "sample-1")])
def test_nonmonotonic_or_repeated_samples_stop_decisions(snapshot, evolve, field, value):
    later = evolve(snapshot, **{field: value})
    port = ReplayPort((Observation(snapshot), Observation(later)))
    with BotRuntime(snapshot.session, port) as runtime:
        runtime.step()
        with pytest.raises(ValueError):
            runtime.step()


def test_wrong_player_sample_is_rejected_before_policy_runs(snapshot, evolve):
    port = ReplayPort((Observation(evolve(snapshot, session=evolve(snapshot.session, player=2))),))
    with BotRuntime(snapshot.session, port) as runtime:
        with pytest.raises(ValueError, match="identity"):
            runtime.step()
        assert not port.submitted


def test_two_runtime_contexts_have_independent_ledgers(snapshot, intent, evolve):
    second = evolve(snapshot, session=evolve(snapshot.session, instance=2, epoch="another-game"))
    with BotRuntime(snapshot.session, ReplayPort((Observation(snapshot),))) as first:
        with BotRuntime(second.session, ReplayPort((Observation(second),))) as other:
            first.ledger.register(snapshot, intent)
            assert not other.ledger.records


def test_engine_cannot_impersonate_other_policy(snapshot, intent):
    port = ReplayPort((Observation(snapshot),))
    with BotRuntime(
        snapshot.session, port, (TestEngine("defense", lambda _: (intent,)),)
    ) as runtime:
        cycle = runtime.step()
        assert not port.submitted
        assert "identity" in cycle.errors[0]


def test_repeated_terminal_results_reach_learning_hooks_only_once(snapshot, intent, evolve):
    class FeedbackEngine(TestEngine):
        def on_outcomes(self, outcomes):
            self.feedback.extend(outcomes)

    engine = FeedbackEngine("raid", lambda s: (evolve(intent, snapshot_id=s.snapshot_id),))
    engine.feedback = []
    frames = [Observation(snapshot)]
    for number in (2, 3):
        later = evolve(snapshot, snapshot_id=f"sample-{number}", tick=100 + number)
        frames.append(
            Observation(
                later,
                (
                    ObservedOutcome(
                        intent.intent_id, OutcomeStatus.CONFIRMED, later.snapshot_id, "effect"
                    ),
                ),
            )
        )
    with BotRuntime(snapshot.session, ReplayPort(frames), (engine,)) as runtime:
        for _ in frames:
            runtime.step()
    assert len(engine.feedback) == 1


def test_reusing_an_older_observation_id_is_rejected(snapshot, evolve):
    frames = (
        Observation(snapshot),
        Observation(evolve(snapshot, snapshot_id="sample-2", tick=101)),
        Observation(evolve(snapshot, tick=102)),
    )
    with BotRuntime(snapshot.session, ReplayPort(frames)) as runtime:
        runtime.step()
        runtime.step()
        with pytest.raises(ValueError, match="repeated"):
            runtime.step()


def test_cleanup_continues_after_a_policy_cleanup_error(snapshot):
    class BadCleanup(TestEngine):
        def on_end(self):
            super().on_end()
            raise RuntimeError("cleanup failed")

    bad = BadCleanup("bad", lambda _: ())
    good = TestEngine("good", lambda _: ())
    port = ReplayPort((Observation(snapshot),))
    runtime = BotRuntime(snapshot.session, port, (bad, good))
    runtime.step()
    with pytest.raises(RuntimeError, match="cleanup failed"):
        runtime.close()
    assert bad.ended == good.ended == 1
    with pytest.raises(RuntimeError, match="closed"):
        port.observe(snapshot.session)


def test_failed_start_closes_port_and_already_started_policies(snapshot):
    class BadStart(TestEngine):
        def on_start(self, session):
            raise RuntimeError("startup failed")

    good = TestEngine("good", lambda _: ())
    bad = BadStart("bad", lambda _: ())
    port = ReplayPort((Observation(snapshot),))
    runtime = BotRuntime(snapshot.session, port, (good, bad))
    with pytest.raises(RuntimeError, match="startup failed"):
        runtime.step()
    assert good.started == good.ended == 1
    with pytest.raises(RuntimeError, match="closed"):
        port.observe(snapshot.session)
