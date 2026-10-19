"""Decode existing lageprotokoll records without importing any live legacy tool."""

from __future__ import annotations

from collections.abc import Mapping

from selfaware.domain import Entity, EntityRef, Resources, Session, Snapshot

RESOURCE_NAMES = {
    "gold": "gold",
    "holz": "wood",
    "stein": "stone",
    "eisen": "iron",
    "pech": "pitch",
    "weizen": "wheat",
    "mehl": "flour",
    "brot": "bread",
    "kaese": "cheese",
    "fleisch": "meat",
    "apfel": "apples",
    "bier": "beer",
    "hopfen": "hops",
}
ENTITY_COLUMNS = frozenset({"nr", "besitzer", "typ", "x", "y", "leben"})


def _table(text: str, header_line: int) -> list[dict[str, int]]:
    lines = text.splitlines()
    if len(lines) <= header_line:
        raise ValueError("snapshot table has no header")
    header = lines[header_line].split()
    if not header or len(header) != len(set(header)):
        raise ValueError("snapshot table has an empty or duplicate header")
    if not ENTITY_COLUMNS.issubset(header):
        raise ValueError("entity table is missing required identity/state columns")
    rows = []
    for line_number, line in enumerate(lines[header_line + 1 :], header_line + 2):
        if not line.strip():
            continue
        values = line.split()
        if len(values) != len(header):
            raise ValueError(f"snapshot table line {line_number}: column count differs from header")
        try:
            rows.append(dict(zip(header, (int(v) for v in values), strict=True)))
        except ValueError as error:
            raise ValueError(f"snapshot table line {line_number}: non-integer value") from error
    return rows


def decode_record(record: Mapping[str, object], session: Session, snapshot_id: str) -> Snapshot:
    """Keep absent unit UIDs unknown; never substitute the target's zieluid.

    Legacy traces do not record the session/player reliably. The caller must
    provide that identity explicitly; it must match the trace being inspected.
    This is an observation decoder, not a simulator or a live game adapter.
    """
    status = record.get("st")
    tick = record.get("t")
    if not isinstance(status, Mapping) or type(tick) is not int or status.get("t") != tick:
        raise ValueError("record and status need the same integer tick")
    if any(not isinstance(k, str) or type(v) is not int for k, v in status.items()):
        raise ValueError("status fields must be integer facts")
    units, buildings = record.get("einheiten"), record.get("gebaeude")
    if not isinstance(units, str) or not isinstance(buildings, str):
        raise ValueError("record needs raw einheiten and gebaeude tables")
    if not units.splitlines() or units.splitlines()[0].split() != ["tick", str(tick)]:
        raise ValueError("unit table and status were captured at different ticks")
    entities = []
    for kind, rows in (("unit", _table(units, 1)), ("building", _table(buildings, 0))):
        for row in rows:
            entities.append(
                Entity(
                    EntityRef(kind, row["nr"], row.get("uid")),
                    row["besitzer"],
                    row["typ"],
                    row["x"],
                    row["y"],
                    row["leben"],
                )
            )
    resources = Resources(
        {english: status[german] for german, english in RESOURCE_NAMES.items() if german in status}
    )
    return Snapshot(session, snapshot_id, tick, resources, tuple(entities), status)
