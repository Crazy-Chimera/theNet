from dataclasses import FrozenInstanceError

import pytest

from src.execution_ledger import (
    ExecutionLedger,
    ExecutionRecord,
    create_execution_ledger,
    create_execution_record,
)


STAMP = "2026-09-22T00:00:00Z"


def make_record():
    return create_execution_record(
        contribution_ledger_id="ledger-1",
        allocation_id="allocation-1",
        memory_before_id="memory-before",
        memory_after_id="memory-after",
        compute_before_id="compute-before",
        compute_after_id="compute-after",
        memory_by_contributor=(("a", 2.0), ("b", 1.0)),
        compute_by_contributor=(("a", 3.0), ("b", 0.0)),
        created_at=STAMP,
    )


def test_execution_record_binds_contribution_allocation_and_resource_transition():
    record = make_record()

    assert isinstance(record, ExecutionRecord)
    assert record.contribution_ledger_id == "ledger-1"
    assert record.allocation_id == "allocation-1"
    assert record.memory_before_id != record.memory_after_id
    assert record.compute_before_id != record.compute_after_id
    assert record.memory_by_contributor == (("a", 2.0), ("b", 1.0))


def test_execution_record_identity_is_deterministic():
    assert make_record().id == make_record().id


def test_execution_record_is_immutable():
    record = make_record()

    with pytest.raises(FrozenInstanceError):
        record.allocation_id = "other"


def test_allocation_contributor_sets_must_match():
    with pytest.raises(ValueError, match="contributor sets"):
        create_execution_record(
            "ledger",
            "allocation",
            "memory-before",
            "memory-after",
            "compute-before",
            "compute-after",
            (("a", 1.0),),
            (("b", 1.0),),
            STAMP,
        )


def test_negative_or_non_finite_allocation_is_rejected():
    with pytest.raises(ValueError, match="finite"):
        create_execution_record(
            "ledger",
            "allocation",
            "memory-before",
            "memory-after",
            "compute-before",
            "compute-after",
            (("a", float("inf")),),
            (("a", 1.0),),
            STAMP,
        )


def test_execution_ledger_is_deterministic_and_order_independent():
    first = make_record()
    second = create_execution_record(
        "ledger-2",
        "allocation-2",
        "memory-before-2",
        "memory-after-2",
        "compute-before-2",
        "compute-after-2",
        (("a", 1.0),),
        (("a", 1.0),),
        STAMP,
    )

    left = create_execution_ledger([first, second])
    right = create_execution_ledger([second, first])

    assert isinstance(left, ExecutionLedger)
    assert left == right


def test_execution_ledger_rejects_duplicate_records():
    record = make_record()

    with pytest.raises(ValueError, match="only once"):
        create_execution_ledger([record, record])


def test_execution_ledger_rejects_invalid_items():
    with pytest.raises(TypeError):
        create_execution_ledger([object()])


def test_empty_execution_ledger_is_valid():
    ledger = create_execution_ledger([])

    assert ledger.entries == ()
    assert ledger.id
