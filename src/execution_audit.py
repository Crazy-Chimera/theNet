"""Immutable query surface for execution provenance."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from src.execution_ledger import (
    ExecutionLedger,
    ExecutionRecord,
    create_execution_ledger,
)


@dataclass(frozen=True)
class ExecutionAudit:
    ledger: ExecutionLedger
    records: tuple[ExecutionRecord, ...]

    def find_record(self, record_id: str) -> ExecutionRecord | None:
        for record in self.records:
            if record.id == record_id:
                return record
        return None

    def find_records_by_contribution_ledger(
        self, contribution_ledger_id: str
    ) -> tuple[ExecutionRecord, ...]:
        return tuple(
            record
            for record in self.records
            if record.contribution_ledger_id == contribution_ledger_id
        )


def create_execution_audit(
    records: Iterable[ExecutionRecord],
) -> ExecutionAudit:
    items = tuple(records)
    if any(not isinstance(item, ExecutionRecord) for item in items):
        raise TypeError("records must contain only ExecutionRecord objects")

    ordered = tuple(sorted(items, key=lambda record: record.id))
    if len({record.id for record in ordered}) != len(ordered):
        raise ValueError("each ExecutionRecord may appear only once")

    return ExecutionAudit(
        ledger=create_execution_ledger(ordered),
        records=ordered,
    )


__all__ = [
    "ExecutionAudit",
    "create_execution_audit",
]