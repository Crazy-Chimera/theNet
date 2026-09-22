"""Immutable provenance ledger for verified resource transitions."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from hashlib import sha256
import json
import math


@dataclass(frozen=True)
class ExecutionRecord:
    id: str
    contribution_ledger_id: str
    allocation_id: str
    memory_before_id: str
    memory_after_id: str
    compute_before_id: str
    compute_after_id: str
    memory_by_contributor: tuple[tuple[str, float], ...]
    compute_by_contributor: tuple[tuple[str, float], ...]
    created_at: str
    version: int = 1


@dataclass(frozen=True)
class ExecutionLedger:
    id: str
    entries: tuple[str, ...]
    version: int = 1


def _validate_id(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty")


def _validate_allocations(
    memory: tuple[tuple[str, float], ...],
    compute: tuple[tuple[str, float], ...],
) -> None:
    if tuple(item[0] for item in memory) != tuple(item[0] for item in compute):
        raise ValueError("memory and compute contributor sets must match")

    for contributor_id, value in (*memory, *compute):
        _validate_id("contributor_id", contributor_id)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("allocation values must be finite and non-negative")
        if not math.isfinite(float(value)) or value < 0.0:
            raise ValueError("allocation values must be finite and non-negative")


def _record_canonical(record: ExecutionRecord) -> str:
    return json.dumps(
        {
            "allocation_id": record.allocation_id,
            "compute_after_id": record.compute_after_id,
            "compute_before_id": record.compute_before_id,
            "compute_by_contributor": record.compute_by_contributor,
            "contribution_ledger_id": record.contribution_ledger_id,
            "created_at": record.created_at,
            "memory_after_id": record.memory_after_id,
            "memory_before_id": record.memory_before_id,
            "memory_by_contributor": record.memory_by_contributor,
            "version": record.version,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_execution_record(
    contribution_ledger_id: str,
    allocation_id: str,
    memory_before_id: str,
    memory_after_id: str,
    compute_before_id: str,
    compute_after_id: str,
    memory_by_contributor: Iterable[tuple[str, float]],
    compute_by_contributor: Iterable[tuple[str, float]],
    created_at: str,
) -> ExecutionRecord:
    for name, value in (
        ("contribution_ledger_id", contribution_ledger_id),
        ("allocation_id", allocation_id),
        ("memory_before_id", memory_before_id),
        ("memory_after_id", memory_after_id),
        ("compute_before_id", compute_before_id),
        ("compute_after_id", compute_after_id),
        ("created_at", created_at),
    ):
        _validate_id(name, value)

    memory = tuple(memory_by_contributor)
    compute = tuple(compute_by_contributor)
    _validate_allocations(memory, compute)

    draft = ExecutionRecord(
        id="",
        contribution_ledger_id=contribution_ledger_id,
        allocation_id=allocation_id,
        memory_before_id=memory_before_id,
        memory_after_id=memory_after_id,
        compute_before_id=compute_before_id,
        compute_after_id=compute_after_id,
        memory_by_contributor=memory,
        compute_by_contributor=compute,
        created_at=created_at,
    )
    identifier = sha256(_record_canonical(draft).encode("utf-8")).hexdigest()

    return ExecutionRecord(
        id=identifier,
        contribution_ledger_id=contribution_ledger_id,
        allocation_id=allocation_id,
        memory_before_id=memory_before_id,
        memory_after_id=memory_after_id,
        compute_before_id=compute_before_id,
        compute_after_id=compute_after_id,
        memory_by_contributor=memory,
        compute_by_contributor=compute,
        created_at=created_at,
    )


def _ledger_canonical(entries: tuple[str, ...]) -> str:
    return json.dumps(
        {"entries": entries, "version": 1},
        sort_keys=True,
        separators=(",", ":"),
    )


def create_execution_ledger(
    records: Iterable[ExecutionRecord],
) -> ExecutionLedger:
    items = tuple(records)
    if any(not isinstance(item, ExecutionRecord) for item in items):
        raise TypeError("records must contain only ExecutionRecord objects")

    entry_ids = tuple(sorted(item.id for item in items))
    if len(entry_ids) != len(set(entry_ids)):
        raise ValueError("each ExecutionRecord may appear only once")

    identifier = sha256(
        _ledger_canonical(entry_ids).encode("utf-8")
    ).hexdigest()

    return ExecutionLedger(id=identifier, entries=entry_ids)


__all__ = [
    "ExecutionLedger",
    "ExecutionRecord",
    "create_execution_ledger",
    "create_execution_record",
]
