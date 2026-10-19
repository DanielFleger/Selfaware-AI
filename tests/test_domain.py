from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from selfaware.domain import Command, EntityRef, Resources, Session
from selfaware.domain.models import thaw


def test_observations_and_nested_commands_do_not_share_mutable_inputs(snapshot):
    source = {"gold": 100}
    resources = Resources(source)
    source["gold"] = 0
    assert resources.amounts["gold"] == 100
    with pytest.raises(TypeError):
        resources.amounts["gold"] = 5
    args = {"units": [1, 2], "target": {"x": 20}}
    command = Command("move", args)
    args["units"].append(3)
    args["target"]["x"] = 30
    assert thaw(command.arguments) == {"units": [1, 2], "target": {"x": 20}}
    with pytest.raises(FrozenInstanceError):
        snapshot.tick = 0


@pytest.mark.parametrize("amount", [-1, True, 1.5, "1"])
def test_invalid_resource_values_cannot_enter_budget(amount):
    with pytest.raises(ValueError):
        Resources({"gold": amount})


@pytest.mark.parametrize(
    "instance,player,epoch", [(0, 1, "x"), (1, 9, "x"), (1, 1, ""), (True, 1, "x")]
)
def test_invalid_session_identity_is_rejected(instance, player, epoch):
    with pytest.raises(ValueError):
        Session(instance, player, epoch)


def test_snapshot_rejects_two_generations_of_same_entity_slot(snapshot, evolve):
    old = snapshot.entities[0]
    new = evolve(old, ref=EntityRef("unit", old.ref.slot, 9999))
    with pytest.raises(ValueError, match="duplicate entity slots"):
        evolve(snapshot, entities=(old, new))


def test_unknown_resource_is_not_assumed_available():
    assert not Resources({"gold": 100}).covers(Resources({"stone": 1}))


def test_ongoing_consumption_cannot_make_budget_negative():
    assert Resources({"gold": 5}).available_after(Resources({"gold": 10})).amounts["gold"] == 0
