from __future__ import annotations

import gzip
import json
from pathlib import Path

import pytest

from selfaware.game.legacy import decode_record
from selfaware.game.replay import ReplayPort, read_legacy_trace

FIXTURE = Path(__file__).parent / "fixtures/legacy_sample.jsonl"


@pytest.fixture
def legacy_record():
    return json.loads(FIXTURE.read_text().splitlines()[0])


def test_old_target_uid_is_never_used_as_actor_identity(legacy_record, session):
    snapshot = decode_record(legacy_record, session, "sample-1")
    assert snapshot.entities[0].ref.uid is None
    assert snapshot.entities[-1].ref.uid == 4001
    assert snapshot.resources.amounts["wood"] == 30
    assert "apples" not in snapshot.resources.amounts


def test_status_and_unit_table_must_come_from_same_tick(legacy_record, session):
    legacy_record["einheiten"] = legacy_record["einheiten"].replace("tick 100", "tick 99")
    with pytest.raises(ValueError, match="different ticks"):
        decode_record(legacy_record, session, "sample-1")


def test_truncated_entity_row_does_not_become_a_partial_world(legacy_record, session):
    legacy_record["einheiten"] += "4 1 73\n"
    with pytest.raises(ValueError, match="column count"):
        decode_record(legacy_record, session, "sample-1")


def test_empty_table_still_needs_the_expected_schema(legacy_record, session):
    legacy_record["gebaeude"] = "unrecognized columns\n"
    with pytest.raises(ValueError, match="required identity"):
        decode_record(legacy_record, session, "sample-1")


def test_plain_and_compressed_trace_have_same_observations(tmp_path, session):
    compressed = tmp_path / "trace.jsonl.gz"
    with gzip.open(compressed, "wt", encoding="utf-8") as stream:
        stream.write(FIXTURE.read_text())
    plain = list(read_legacy_trace(FIXTURE, session))
    zipped = list(read_legacy_trace(compressed, session))
    assert [o.snapshot.tick for o in plain] == [o.snapshot.tick for o in zipped] == [100, 110]
    assert plain[0].snapshot.entities == zipped[0].snapshot.entities


def test_corrupt_line_error_identifies_trace_location(tmp_path, session):
    path = tmp_path / "bad.jsonl"
    path.write_text(FIXTURE.read_text().splitlines()[0] + '\n{"bad":}\n')
    frames = read_legacy_trace(path, session)
    next(frames)
    with pytest.raises(ValueError, match="bad.jsonl:2"):
        next(frames)


def test_replay_never_fabricates_success_from_historical_future(snapshot, intent, evolve):
    from selfaware.game.ports import Observation, ReceiptStatus

    port = ReplayPort(
        (Observation(snapshot), Observation(evolve(snapshot, snapshot_id="later", tick=110)))
    )
    port.observe(snapshot.session)
    assert port.submit(snapshot.session, intent).status == ReceiptStatus.RECEIVED
    assert not port.observe(snapshot.session).outcomes
    port.close()


def test_replay_port_cannot_mix_players(session, snapshot, evolve):
    from selfaware.game.ports import Observation

    port = ReplayPort((Observation(snapshot), Observation(snapshot)))
    port.observe(session)
    with pytest.raises(ValueError, match="one session"):
        port.observe(evolve(session, player=2))
    port.close()
