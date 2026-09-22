from __future__ import annotations

import pytest

from thenet.engine import (
    commit_ledger_backed_resources_with_record,
    commit_self_organizing_resources,
)
from src.contribution_ledger import create_contribution_ledger
from src.execution_ledger import ExecutionRecord
from src.omega_credit import create_omega_credit
from src.relational_utility import create_relational_utility
from src.resource_state import create_resource_state


def _utility(contributor_id: str, verified: bool = True):
    return create_relational_utility(
        contributor_id=contributor_id,
        value=1.0,
        evidence_ids=(f"evidence-{contributor_id}",),
        verified=verified,
        created_at="2026-09-22T12:00:00Z",
    )


def test_runtime_facade_commits_verified_self_organizing_allocation():
    memory = create_resource_state(10.0, 2.0, "2026-09-22T12:00:00Z")
    compute = create_resource_state(20.0, 4.0, "2026-09-22T12:00:00Z")

    next_memory, next_compute = commit_self_organizing_resources(
        [_utility("a"), _utility("b")],
        memory,
        compute,
        {"a": 1.0, "b": 1.0},
        "2026-09-22T12:01:00Z",
    )

    assert next_memory.used == pytest.approx(10.0)
    assert next_compute.used == pytest.approx(20.0)


def test_runtime_facade_preserves_unverified_zero_credit():
    memory = create_resource_state(10.0, 2.0, "2026-09-22T12:00:00Z")
    compute = create_resource_state(20.0, 4.0, "2026-09-22T12:00:00Z")

    next_memory, next_compute = commit_self_organizing_resources(
        [_utility("a", verified=False)],
        memory,
        compute,
        {"a": 1.0},
        "2026-09-22T12:01:00Z",
    )

    assert next_memory == memory
    assert next_compute == compute


def test_runtime_facade_requires_coherence_for_each_contributor():
    with pytest.raises(ValueError, match="missing Φ coherence"):
        commit_self_organizing_resources(
            [_utility("a")],
            create_resource_state(10.0, 2.0, "2026-09-22T12:00:00Z"),
            create_resource_state(20.0, 4.0, "2026-09-22T12:00:00Z"),
            {},
            "2026-09-22T12:01:00Z",
        )


def test_runtime_facade_exposes_ledger_backed_provenance():
    ledger = create_contribution_ledger(
        [
            create_omega_credit("a", 0.75, 1.0, 1.0, True, "2026-09-22T12:00:00Z"),
            create_omega_credit("b", 0.25, 1.0, 1.0, True, "2026-09-22T12:01:00Z"),
        ]
    )
    memory = create_resource_state(100.0, 0.0, "2026-09-22T12:00:00Z")
    compute = create_resource_state(50.0, 0.0, "2026-09-22T12:00:00Z")

    next_memory, next_compute, record = commit_ledger_backed_resources_with_record(
        ledger,
        memory,
        compute,
        40.0,
        20.0,
        "2026-09-22T12:02:00Z",
    )

    assert isinstance(record, ExecutionRecord)
    assert record.contribution_ledger_id == ledger.id
    assert record.memory_after_id == next_memory.id
    assert record.compute_after_id == next_compute.id
