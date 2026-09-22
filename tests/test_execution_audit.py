from dataclasses import FrozenInstanceError

import pytest

from src.execution_audit import ExecutionAudit, create_execution_audit
from src.execution_ledger import create_execution_record


def make_record(contribution_ledger_id: str, suffix: str):
    return create_execution_record(
        contribution_ledger_id=contribution_ledger_id,
        allocation_id=f"allocation-{suffix}",
        memory_before_id=f"memory-before-{suffix}",
        memory_after_id=f"memory-after-{suffix}",
        compute_before_id=f"compute-before-{suffix}",
        compute_after_id=f"compute-after-{suffix}",
        memory_by_contributor=(("alice", 1.0),),
        compute_by_contributor=(("alice", 2.0),),
        created_at=f"2026-09-22T12:0{suffix}:00Z",
    )


def test_audit_indexes_records_by_identity():
    record = make_record("ledger-a", "1")
    audit = create_execution_audit([record])

    assert isinstance(audit, ExecutionAudit)
    assert audit.find_record(record.id) == record
    assert audit.find_record("missing") is None


def test_audit_indexes_records_by_contribution_ledger():
    first = make_record("ledger-a", "1")
    second = make_record("ledger-a", "2")
    third = make_record("ledger-b", "3")
    audit = create_execution_audit([third, second, first])

    assert audit.find_records_by_contribution_ledger("ledger-a") == tuple(
        sorted((first, second), key=lambda record: record.id)
    )
    assert audit.find_records_by_contribution_ledger("missing") == ()


def test_audit_is_order_independent():
    first = make_record("ledger-a", "1")
    second = make_record("ledger-b", "2")

    assert create_execution_audit([first, second]) == create_execution_audit([second, first])


def test_audit_rejects_duplicate_record_identity():
    record = make_record("ledger-a", "1")

    with pytest.raises(ValueError, match="only once"):
        create_execution_audit([record, record])


def test_audit_rejects_non_records():
    with pytest.raises(TypeError, match="ExecutionRecord"):
        create_execution_audit([object()])


def test_audit_is_immutable():
    audit = create_execution_audit([make_record("ledger-a", "1")])

    with pytest.raises(FrozenInstanceError):
        audit.records = ()