from src.contribution_ledger import create_contribution_ledger
from src.execution_ledger import ExecutionRecord
from src.omega_credit import create_omega_credit
from src.omega_credit_self_organizing_commitment import (
    commit_ledger_backed_allocation_with_record,
)
from src.resource_state import create_resource_state


def test_ledger_backed_commit_returns_auditable_provenance_record():
    ledger = create_contribution_ledger(
        [
            create_omega_credit(
                "b", 0.25, 1.0, 1.0, True, "2026-09-22T12:00:00Z"
            ),
            create_omega_credit(
                "a", 0.75, 1.0, 1.0, True, "2026-09-22T12:01:00Z"
            ),
        ]
    )
    memory = create_resource_state(100.0, 0.0, "2026-09-22T12:00:00Z")
    compute = create_resource_state(50.0, 0.0, "2026-09-22T12:00:00Z")

    next_memory, next_compute, record = commit_ledger_backed_allocation_with_record(
        ledger,
        memory,
        compute,
        memory_capacity=40.0,
        compute_capacity=20.0,
        created_at="2026-09-22T12:02:00Z",
    )

    assert isinstance(record, ExecutionRecord)
    assert record.contribution_ledger_id == ledger.id
    assert record.memory_before_id == memory.id
    assert record.memory_after_id == next_memory.id
    assert record.compute_before_id == compute.id
    assert record.compute_after_id == next_compute.id
    assert record.memory_by_contributor == (("a", 30.0), ("b", 10.0))
    assert record.compute_by_contributor == (("a", 15.0), ("b", 5.0))


def test_provenance_record_is_deterministic():
    credit = create_omega_credit(
        "a", 1.0, 1.0, 1.0, True, "2026-09-22T12:00:00Z"
    )
    ledger = create_contribution_ledger([credit])
    memory = create_resource_state(10.0, 0.0, "2026-09-22T12:00:00Z")
    compute = create_resource_state(10.0, 0.0, "2026-09-22T12:00:00Z")

    first = commit_ledger_backed_allocation_with_record(
        ledger, memory, compute, 4.0, 6.0, "2026-09-22T12:01:00Z"
    )
    second = commit_ledger_backed_allocation_with_record(
        ledger, memory, compute, 4.0, 6.0, "2026-09-22T12:01:00Z"
    )

    assert first == second
