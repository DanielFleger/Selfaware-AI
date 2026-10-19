from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType


def _integer(name: str, value: int, minimum: int | None = None) -> None:
    if type(value) is not int or (minimum is not None and value < minimum):
        raise ValueError(f"{name} must be an integer" + (f" >= {minimum}" if minimum else ""))


@dataclass(frozen=True)
class Session:
    instance: int
    player: int
    epoch: str

    def __post_init__(self) -> None:
        _integer("instance", self.instance, 1)
        _integer("player", self.player, 1)
        if self.player > 8 or not self.epoch.strip():
            raise ValueError("a session needs a player from 1 to 8 and a game epoch")


@dataclass(frozen=True)
class Resources:
    """A copied, immutable resource vector; unreported resources cannot be spent."""

    amounts: Mapping[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        copied = dict(self.amounts)
        for name, value in copied.items():
            if not isinstance(name, str) or not name:
                raise ValueError("resource names must be nonempty strings")
            _integer(name, value, 0)
        object.__setattr__(self, "amounts", MappingProxyType(copied))

    def covers(self, cost: Resources) -> bool:
        return all(self.amounts.get(name, 0) >= value for name, value in cost.amounts.items())

    def plus(self, other: Resources) -> Resources:
        names = self.amounts.keys() | other.amounts.keys()
        return Resources({n: self.amounts.get(n, 0) + other.amounts.get(n, 0) for n in names})

    def available_after(self, reserved: Resources) -> Resources:
        # Ongoing game consumption can reduce the stock below a pending commitment.
        return Resources(
            {n: max(0, v - reserved.amounts.get(n, 0)) for n, v in self.amounts.items()}
        )


@dataclass(frozen=True)
class EntityRef:
    kind: str
    slot: int
    uid: int | None

    def __post_init__(self) -> None:
        if self.kind not in {"unit", "building"}:
            raise ValueError("entity kind must be unit or building")
        _integer("slot", self.slot, 0)
        if self.uid is not None:
            _integer("uid", self.uid, 0)


@dataclass(frozen=True)
class Entity:
    ref: EntityRef
    owner: int
    type_id: int
    x: int
    y: int
    health: int

    def __post_init__(self) -> None:
        for name in ("owner", "type_id", "health"):
            _integer(name, getattr(self, name), 0)
        for name in ("x", "y"):
            _integer(name, getattr(self, name))
        if self.owner > 8:
            raise ValueError("entity owner must be from 0 to 8")


@dataclass(frozen=True)
class Snapshot:
    session: Session
    snapshot_id: str
    tick: int
    resources: Resources
    entities: tuple[Entity, ...] = ()
    facts: Mapping[str, int] = field(default_factory=dict)
    schema_version: int = 1

    def __post_init__(self) -> None:
        _integer("tick", self.tick, 0)
        if not self.snapshot_id or self.schema_version != 1:
            raise ValueError("a snapshot needs an ID and supported schema_version=1")
        entities = tuple(self.entities)
        slots = [(e.ref.kind, e.ref.slot) for e in entities]
        if len(slots) != len(set(slots)):
            raise ValueError("a snapshot cannot contain duplicate entity slots")
        facts = dict(self.facts)
        if any(not isinstance(k, str) or type(v) is not int for k, v in facts.items()):
            raise ValueError("snapshot facts must map strings to integers")
        object.__setattr__(self, "entities", entities)
        object.__setattr__(self, "facts", MappingProxyType(facts))

    def entity(self, ref: EntityRef) -> Entity | None:
        return next((entity for entity in self.entities if entity.ref == ref), None)


def _freeze(value: object) -> object:
    if value is None or type(value) in {str, int, bool}:
        return value
    if isinstance(value, Mapping):
        if any(not isinstance(k, str) for k in value):
            raise ValueError("command argument keys must be strings")
        return MappingProxyType({k: _freeze(v) for k, v in value.items()})
    if isinstance(value, (tuple, list)):
        return tuple(_freeze(v) for v in value)
    raise ValueError("command arguments must contain JSON-compatible integers, strings or booleans")


def thaw(value: object) -> object:
    """Produce JSON-serializable copies of immutable command values."""
    if isinstance(value, Mapping):
        return {k: thaw(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [thaw(v) for v in value]
    return value


@dataclass(frozen=True)
class Command:
    """Logical action, deliberately independent of raw UCP addresses/opcodes."""

    name: str
    arguments: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("command name cannot be empty")
        object.__setattr__(self, "arguments", _freeze(dict(self.arguments)))


@dataclass(frozen=True)
class Intent:
    intent_id: str
    engine: str
    command: Command
    snapshot_id: str
    valid_until_tick: int
    priority: int = 0  # Larger values are more urgent; ties use stable IDs.
    actors: tuple[EntityRef, ...] = ()
    targets: tuple[EntityRef, ...] = ()
    cost: Resources = field(default_factory=Resources)
    reason: str = ""

    def __post_init__(self) -> None:
        if not self.intent_id or not self.engine or not self.snapshot_id:
            raise ValueError("an intent needs an ID, engine and source snapshot")
        _integer("priority", self.priority, 0)
        _integer("valid_until_tick", self.valid_until_tick, 0)
        for name in ("actors", "targets"):
            refs = tuple(getattr(self, name))
            if len(refs) != len(set(refs)):
                raise ValueError(f"duplicate {name} in intent")
            object.__setattr__(self, name, refs)
