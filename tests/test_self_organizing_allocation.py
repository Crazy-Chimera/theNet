import pytest

from src.relational_utility import create_relational_utility
from src.resource_state import create_resource_state
from src.self_organizing_allocation import allocate_memory_and_compute


def test_verified_utility_coherence_and_resource_state_drive_both_pools():
    utility = create_relational_utility(
        "agent-a", 1.0, ["evidence-a"], True, "2026-09-22T00:00:00Z"
    )
    memory = create_resource_state(100.0, 20.0, "2026-09-22T00:00:01Z")
    compute = create_resource_state(50.0, 10.0, "2026-09-22T00:00:02Z")

    result = allocate_memory_and_compute(
        [utility], memory, compute, {"agent-a": 1.0}
    )

    assert result.memory[0].allocation == 64.0
    assert result.compute[0].allocation == 32.0


def test_unverified_utility_receives_zero_allocation():
    utility = create_relational_utility(
        "agent-a", 1.0, [], False, "2026-09-22T00:00:00Z"
    )
    resource = create_resource_state(100.0, 20.0, "2026-09-22T00:00:01Z")

    result = allocate_memory_and_compute(
        [utility], resource, resource, {"agent-a": 1.0}
    )

    assert result.memory[0].allocation == 0.0
    assert result.compute[0].allocation == 0.0


def test_phi_coherence_changes_relative_allocation():
    a = create_relational_utility(
        "agent-a", 1.0, ["evidence-a"], True, "2026-09-22T00:00:00Z"
    )
    b = create_relational_utility(
        "agent-b", 1.0, ["evidence-b"], True, "2026-09-22T00:00:00Z"
    )
    resource = create_resource_state(100.0, 0.0, "2026-09-22T00:00:01Z")

    result = allocate_memory_and_compute(
        [a, b], resource, resource, {"agent-a": 1.0, "agent-b": 0.5}
    )

    assert result.memory[0].contributor_id == "agent-a"
    assert result.memory[0].allocation > result.memory[1].allocation


def test_missing_coherence_is_rejected():
    utility = create_relational_utility(
        "agent-a", 1.0, ["evidence-a"], True, "2026-09-22T00:00:00Z"
    )
    resource = create_resource_state(10.0, 0.0, "2026-09-22T00:00:01Z")

    with pytest.raises(ValueError):
        allocate_memory_and_compute([utility], resource, resource, {})


def test_invalid_coherence_is_rejected():
    utility = create_relational_utility(
        "agent-a", 1.0, ["evidence-a"], True, "2026-09-22T00:00:00Z"
    )
    resource = create_resource_state(10.0, 0.0, "2026-09-22T00:00:01Z")

    with pytest.raises(ValueError):
        allocate_memory_and_compute(
            [utility], resource, resource, {"agent-a": 1.1}
        )
