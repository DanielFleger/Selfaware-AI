from __future__ import annotations

import gzip
import json
from collections.abc import Iterable, Iterator
from pathlib import Path

from selfaware.domain import Intent, Session
from selfaware.game.legacy import decode_record
from selfaware.game.ports import Observation, Receipt, ReceiptStatus


def read_legacy_trace(path: Path, session: Session) -> Iterator[Observation]:
    """Stream .jsonl or .jsonl.gz observations, with errors pointing to their line."""
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise ValueError("record must be an object")
                yield Observation(decode_record(record, session, f"{path.name}:{line_number}"))
            except (ValueError, KeyError, TypeError) as error:
                raise ValueError(f"{path.name}:{line_number}: {error}") from error


class ReplayPort:
    """Feed recorded observations; record proposals without executing a game.

    A received receipt is the only synthesized response. Historical future
    observations are never claimed as results of newly proposed actions.
    Tests may supply explicit observed outcomes in their own fixture frames.
    """

    def __init__(self, observations: Iterable[Observation]) -> None:
        self._observations = iter(observations)
        self.submitted: list[tuple[Session, Intent]] = []
        self._closed = False
        self._session: Session | None = None

    def observe(self, session: Session) -> Observation:
        if self._closed:
            raise RuntimeError("replay port is closed")
        if self._session is not None and session != self._session:
            raise ValueError("replay port is scoped to one session")
        observation = next(self._observations)
        if observation.snapshot.session != session:
            raise ValueError("trace identity differs from the requested session")
        self._session = session
        return observation

    def submit(self, session: Session, intent: Intent) -> Receipt:
        if self._closed or session != self._session:
            raise ValueError("observe the same session before submitting a replay proposal")
        self.submitted.append((session, intent))
        return Receipt(intent.intent_id, ReceiptStatus.RECEIVED, "recorded only; no game effect")

    def close(self) -> None:
        self._closed = True
        close = getattr(self._observations, "close", None)
        if close is not None:
            close()
