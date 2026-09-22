"""Deterministic continuity model for ordered execution provenance."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from hashlib import sha256
import json

from src.execution_ledger import ExecutionRecord


@dataclass(frozen=True)
class ExecutionChain:
    id: str
    records: tuple[ExecutionRecord, ...]
    continuous: bool
    version: int = 1


def _canonical(records: tuple[ExecutionRecord, ...]) -> str:
    return json.dumps(
        {
            "entries": tuple(record.id for record in records),
            "version": 1,
        },
        separators=(",", ":"),
    )


def _is_continuous(records: tuple[ExecutionRecord, ...]) -> bool:
    return all(
        previous.memory_after_id == current.memory_before_id
        and previous.compute_after_id == current.compute_before_id
        for previous, current in zip(records, records[1:])
    )


def create_execution_chain(
    records: Iterable[ExecutionRecord],
) -> ExecutionChain:
    items = tuple(records)

    if any(not isinstance(item, ExecutionRecord) for item in items):
        raise TypeError("records must contain only ExecutionRecord objects")

    identifier = sha256(_canonical(items).encode("utf-8")).hexdigest()

    return ExecutionChain(
        id=identifier,
        records=items,
        continuous=_is_continuous(items),
    )


__all__ = ["ExecutionChain", "create_execution_chain"]
