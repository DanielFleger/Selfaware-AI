from __future__ import annotations

import pytest

from selfaware.execution import ActionLedger, ActionStatus
from selfaware.game.ports import (
    Observation,
    ObservedOutcome,
    OutcomeStatus,
    Receipt,
    ReceiptStatus,
)


def test_ack_and_dispatch_do_not_confirm_or_release_cost(snapshot, intent):
    ledger = ActionLedger(snapshot.session)
    ledger.register(snapshot, intent)
    ledger.receive(Receipt(intent.intent_id, ReceiptStatus.RECEIVED))
    ledger.receive(Receipt(intent.intent_id, ReceiptStatus.DISPATCHED))
    assert ledger.records[0].status == ActionStatus.DISPATCHED
    assert ledger.reserved.amounts["gold"] == 70
    assert intent.actors[0] in ledger.claimed


def test_ambiguous_timeout_can_be_resolved_by_later_observed_effect(snapshot, intent, evolve):
    ledger = ActionLedger(snapshot.session)
    ledger.register(snapshot, intent)
    ledger.unresolved(intent.intent_id, "transport disconnected")
    later = evolve(snapshot, snapshot_id="sample-2", tick=110)
    ledger.reconcile(
        Observation(
            later,
            (
                ObservedOutcome(
                    intent.intent_id, OutcomeStatus.CONFIRMED, "sample-2", "order observed"
                ),
            ),
        )
    )
    assert ledger.records[0].status == ActionStatus.CONFIRMED
    assert ledger.records[0].observed_snapshot_id == "sample-2"
    assert not ledger.pending and not ledger.claimed and not ledger.reserved.amounts


def test_explicit_pre_dispatch_rejection_releases_reservation(snapshot, intent):
    ledger = ActionLedger(snapshot.session)
    ledger.register(snapshot, intent)
    ledger.receive(Receipt(intent.intent_id, ReceiptStatus.REJECTED, "not queued"))
    assert not ledger.pending


@pytest.mark.parametrize(
    "status,source,detail",
    [
        (OutcomeStatus.CONFIRMED, "stale-sample", "effect"),
        (OutcomeStatus.CONFIRMED, "sample-1", ""),
        ("confirmed", "sample-1", "effect"),
    ],
)
def test_confirmation_requires_typed_current_observation_evidence(
    snapshot, intent, status, source, detail
):
    ledger = ActionLedger(snapshot.session)
    ledger.register(snapshot, intent)
    with pytest.raises(ValueError):
        ledger.reconcile(
            Observation(snapshot, (ObservedOutcome(intent.intent_id, status, source, detail),))
        )
    assert ledger.records[0].status == ActionStatus.RESERVED


def test_outcome_batch_validation_does_not_partially_release_reservations(snapshot, intent, evolve):
    ledger = ActionLedger(snapshot.session)
    ledger.register(snapshot, intent)
    snapshot = evolve(snapshot, snapshot_id="sample-2")
    with pytest.raises(ValueError, match="unknown action"):
        ledger.reconcile(
            Observation(
                snapshot,
                (
                    ObservedOutcome(
                        intent.intent_id, OutcomeStatus.CONFIRMED, snapshot.snapshot_id, "effect"
                    ),
                    ObservedOutcome(
                        "unrecognized", OutcomeStatus.CONFIRMED, snapshot.snapshot_id, "effect"
                    ),
                ),
            )
        )
    assert len(ledger.pending) == 1


def test_terminal_results_are_idempotent_but_contradictions_are_rejected(snapshot, intent, evolve):
    ledger = ActionLedger(snapshot.session)
    ledger.register(snapshot, intent)
    snapshot = evolve(snapshot, snapshot_id="sample-2")
    result = ObservedOutcome(
        intent.intent_id, OutcomeStatus.CONFIRMED, snapshot.snapshot_id, "effect"
    )
    ledger.reconcile(Observation(snapshot, (result, result)))
    ledger.reconcile(Observation(snapshot, (result,)))
    with pytest.raises(ValueError, match="contradictory"):
        ledger.reconcile(
            Observation(
                snapshot,
                (
                    ObservedOutcome(
                        intent.intent_id, OutcomeStatus.REJECTED, snapshot.snapshot_id, "bad"
                    ),
                ),
            )
        )


def test_receipt_cannot_forge_observed_confirmation(snapshot, intent):
    ledger = ActionLedger(snapshot.session)
    ledger.register(snapshot, intent)
    with pytest.raises(ValueError, match="cannot confirm"):
        ledger.receive(Receipt(intent.intent_id, "confirmed"))


def test_proposal_source_sample_cannot_prove_its_own_effect(snapshot, intent):
    ledger = ActionLedger(snapshot.session)
    ledger.register(snapshot, intent)
    with pytest.raises(ValueError, match="later observation"):
        ledger.reconcile(
            Observation(
                snapshot,
                (
                    ObservedOutcome(
                        intent.intent_id, OutcomeStatus.CONFIRMED, snapshot.snapshot_id, "effect"
                    ),
                ),
            )
        )


def test_dispatched_action_cannot_be_released_by_a_late_transport_rejection(snapshot, intent):
    ledger = ActionLedger(snapshot.session)
    ledger.register(snapshot, intent)
    ledger.receive(Receipt(intent.intent_id, ReceiptStatus.DISPATCHED))
    ledger.unresolved(intent.intent_id, "connection lost after dispatch")
    with pytest.raises(ValueError, match="observed rejection"):
        ledger.receive(Receipt(intent.intent_id, ReceiptStatus.REJECTED))
    assert ledger.reserved.amounts["gold"] == 70
