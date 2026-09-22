from __future__ import annotations

import pytest

from thenet.engine import commit_self_organizing_resources
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
