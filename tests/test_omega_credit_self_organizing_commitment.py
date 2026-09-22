from __future__ import annotations

import pytest

from src.omega_credit_self_organizing_commitment import (
    commit_self_organizing_allocation,
)
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


def test_commit_applies_verified_credit_to_memory_and_compute():
    utilities = (_utility("a"), _utility("b"))
    memory = create_resource_state(10.0, 2.0, "2026-09-22T12:00:00Z")
    compute = create_resource_state(20.0, 4.0, "2026-09-22T12:00:00Z")

    next_memory, next_compute = commit_self_organizing_allocation(
        utilities,
        memory,
        compute,
        {"a": 1.0, "b": 1.0},
        "2026-09-22T12:01:00Z",
    )

    assert next_memory.used == pytest.approx(10.0)
    assert next_compute.used == pytest.approx(20.0)


def test_unverified_utility_does_not_allocate():
    utilities = (_utility("a", verified=False),)
    memory = create_resource_state(10.0, 2.0, "2026-09-22T12:00:00Z")
    compute = create_resource_state(20.0, 4.0, "2026-09-22T12:00:00Z")

    next_memory, next_compute = commit_self_organizing_allocation(
        utilities,
        memory,
        compute,
        {"a": 1.0},
        "2026-09-22T12:01:00Z",
    )

    assert next_memory.used == memory.used
    assert next_compute.used == compute.used


def test_missing_coherence_is_rejected():
    with pytest.raises(ValueError, match="missing Φ coherence"):
        commit_self_organizing_allocation(
            (_utility("a"),),
            create_resource_state(10.0, 2.0, "2026-09-22T12:00:00Z"),
            create_resource_state(20.0, 4.0, "2026-09-22T12:00:00Z"),
            {},
            "2026-09-22T12:01:00Z",
        )


def test_inputs_remain_unchanged():
    memory = create_resource_state(10.0, 2.0, "2026-09-22T12:00:00Z")
    compute = create_resource_state(20.0, 4.0, "2026-09-22T12:00:00Z")

    commit_self_organizing_allocation(
        (_utility("a"),),
        memory,
        compute,
        {"a": 1.0},
        "2026-09-22T12:01:00Z",
    )

    assert memory.used == 2.0
    assert compute.used == 4.0


def test_commit_is_deterministic_for_same_input():
    utilities = (_utility("a"), _utility("b"))
    memory = create_resource_state(10.0, 2.0, "2026-09-22T12:00:00Z")
    compute = create_resource_state(20.0, 4.0, "2026-09-22T12:00:00Z")

    first = commit_self_organizing_allocation(
        utilities,
        memory,
        compute,
        {"a": 1.0, "b": 1.0},
        "2026-09-22T12:01:00Z",
    )
    second = commit_self_organizing_allocation(
        utilities,
        memory,
        compute,
        {"a": 1.0, "b": 1.0},
        "2026-09-22T12:01:00Z",
    )

    assert first == second


def test_changed_contribution_changes_next_state():
    utilities = (_utility("a"), _utility("b"))
    memory = create_resource_state(10.0, 2.0, "2026-09-22T12:00:00Z")
    compute = create_resource_state(20.0, 4.0, "2026-09-22T12:00:00Z")

    equal = commit_self_organizing_allocation(
        utilities,
        memory,
        compute,
        {"a": 1.0, "b": 1.0},
        "2026-09-22T12:01:00Z",
    )
    zero_credit = commit_self_organizing_allocation(
        utilities,
        memory,
        compute,
        {"a": 0.0, "b": 0.0},
        "2026-09-22T12:01:00Z",
    )

    assert equal != zero_credit
    assert zero_credit[0].used == memory.used
    assert zero_credit[1].used == compute.used
