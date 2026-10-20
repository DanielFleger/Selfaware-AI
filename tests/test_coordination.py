from __future__ import annotations

from itertools import permutations

import pytest

from selfaware.coordination import Planner
from selfaware.domain import EntityRef, Resources
from selfaware.execution import ActionLedger


def test_defense_wins_conflicting_actor_even_when_raid_is_proposed_first(snapshot, intent, evolve):
    defense = evolve(intent, intent_id="defense:1", engine="defense", priority=100)
    for proposals in permutations((intent, defense)):
        decisions = Planner().select(snapshot, proposals, ActionLedger(snapshot.session))
        assert [(d.intent.engine, d.accepted, d.reason) for d in decisions] == [
            ("defense", True, "selected"),
            ("raid", False, "actor_reserved"),
        ]


def test_resource_bundle_is_reserved_atomically(snapshot, intent, evolve):
    mine = evolve(
        intent,
        intent_id="economy:mine",
        engine="economy",
        priority=20,
        actors=(),
        cost=Resources({"gold": 80, "wood": 40}),
    )
    farm = evolve(
        mine, intent_id="economy:farm", priority=10, cost=Resources({"gold": 40, "wood": 10})
    )
    decisions = Planner().select(snapshot, (mine, farm), ActionLedger(snapshot.session))
    assert [(d.accepted, d.reason) for d in decisions] == [
        (False, "insufficient_unreserved_resources"),
        (True, "selected"),
    ]


def test_two_affordable_actions_cannot_spend_same_stock(snapshot, intent, evolve):
    second = evolve(intent, intent_id="raid:2", actors=(snapshot.entities[1].ref,))
    decisions = Planner().select(snapshot, (intent, second), ActionLedger(snapshot.session))
    assert sum(d.accepted for d in decisions) == 1
    assert decisions[1].reason == "insufficient_unreserved_resources"


def test_pending_action_holds_resources_and_actor_across_samples(snapshot, intent, evolve):
    ledger = ActionLedger(snapshot.session)
    ledger.register(snapshot, intent)
    ledger.unresolved(intent.intent_id, "reply lost")
    next_sample = evolve(snapshot, snapshot_id="sample-2", tick=101)
    repeated = evolve(intent, snapshot_id=next_sample.snapshot_id)
    urgent = evolve(repeated, intent_id="defense:1", engine="defense", priority=1000)
    trade = evolve(repeated, intent_id="market:1", actors=())
    decisions = Planner().select(next_sample, (repeated, urgent, trade), ledger)
    assert {d.intent.intent_id: d.reason for d in decisions} == {
        repeated.intent_id: "action_id_already_used",
        urgent.intent_id: "actor_reserved",
        trade.intent_id: "insufficient_unreserved_resources",
    }


@pytest.mark.parametrize(
    "change,reason",
    [
        ({"snapshot_id": "old"}, "stale_snapshot"),
        ({"valid_until_tick": 99}, "deadline_expired"),
        ({"actors": (EntityRef("unit", 1, None),)}, "entity_uid_unavailable"),
        ({"actors": (EntityRef("unit", 1, 9999),)}, "entity_missing_or_replaced"),
        ({"actors": (EntityRef("unit", 3, 2001),)}, "actor_not_owned"),
        ({"targets": (EntityRef("unit", 5, 777),)}, "entity_missing_or_replaced"),
    ],
)
def test_invalid_action_preconditions_are_explained(snapshot, intent, evolve, change, reason):
    (decision,) = Planner().select(
        snapshot, (evolve(intent, **change),), ActionLedger(snapshot.session)
    )
    assert not decision.accepted
    assert decision.reason == reason


def test_all_duplicate_ids_are_denied_instead_of_choosing_arbitrary_producer(
    snapshot, intent, evolve
):
    other = evolve(intent, engine="defense", priority=100)
    decisions = Planner().select(snapshot, (intent, other), ActionLedger(snapshot.session))
    assert all(not d.accepted and d.reason == "duplicate_intent_id" for d in decisions)


def test_ledger_cannot_be_shared_with_another_player(snapshot, intent, evolve):
    other = evolve(snapshot, session=evolve(snapshot.session, player=2))
    with pytest.raises(ValueError, match="across players"):
        Planner().select(other, (intent,), ActionLedger(snapshot.session))
