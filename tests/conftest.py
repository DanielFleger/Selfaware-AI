from __future__ import annotations

import importlib.util
import sys
from dataclasses import replace

import pytest

from selfaware.domain import Command, Entity, EntityRef, Intent, Resources, Session, Snapshot

# B-167: Diese Testdateien brauchen, was es in der Pruefung auf GitHub nicht gibt - ohne es werden sie nicht gesammelt.
collect_ignore = []
if importlib.util.find_spec("numpy") is None:  # numpy kommt nur mit dem Extra "legacy"
    collect_ignore += ["test_auge_lauf_s.py", "test_streuung.py"]
if sys.platform != "win32":  # spielcode_rufen laedt Windows-Bibliotheken (ctypes.WinDLL)
    collect_ignore += ["test_spielcode_rufen.py"]


@pytest.fixture
def session():
    return Session(1, 1, "test-game")


@pytest.fixture
def snapshot(session):
    return Snapshot(
        session,
        "sample-1",
        100,
        Resources({"gold": 100, "wood": 30}),
        (
            Entity(EntityRef("unit", 1, 1001), 1, 73, 10, 10, 12500),
            Entity(EntityRef("unit", 2, 1002), 1, 70, 11, 10, 10000),
            Entity(EntityRef("unit", 3, 2001), 2, 73, 20, 20, 12500),
        ),
    )


@pytest.fixture
def intent(snapshot):
    return Intent(
        "raid:move:1",
        "raid",
        Command("move", {"x": 20, "y": 20}),
        snapshot.snapshot_id,
        200,
        priority=10,
        actors=(snapshot.entities[0].ref,),
        cost=Resources({"gold": 70}),
        reason="test task",
    )


@pytest.fixture
def evolve():
    return replace
