from __future__ import annotations

import pytest

from thenet.engine import (
    allocate_resources_from_phi,
    commit_self_organizing_resources_from_phi,
)
from src.genesis import create_genesis
from src.phi import create_phi
from src.relational_utility import create_relational_utility
from src.relation import create_relation
from src.resource_state import create_resource_state


STAMP = "2026-09-22T15:00:00Z"


def structure(source: str, target: str):
    a = create_genesis(source, STAMP)
    b = create_genesis(target, STAMP)
    return create_phi([create_relation(a.id, b.id, "supports", STAMP)])


def test_verified_agent_flow_reaches_resource_commit():
    utilities = [
        create_relational_utility("agent:a", 1.0, ["evidence-a"], True, STAMP),
        create_relational_utility("agent:b", 0.5, ["evidence-b"], True, STAMP),
    ]
    structures = {
        "agent:a": structure("a", "b"),
        "agent:b": structure("b", "c"),
    }
    memory = create_resource_state(100.0, 0.0, STAMP)
    compute = create_resource_state(100.0, 0.0, STAMP)

    allocation = allocate_resources_from_phi(
        utilities, memory, compute, structures
    )

    next_memory, next_compute = commit_self_organizing_resources_from_phi(
        utilities,
        memory,
        compute,
        structures,
        "2026-09-22T15:01:00Z",
    )

    assert sum(value for _, value in allocation.memory_by_contributor) > 0.0
    assert sum(value for _, value in allocation.compute_by_contributor) > 0.0
    assert next_memory.used == pytest.approx(
        sum(value for _, value in allocation.memory_by_contributor)
    )
    assert next_compute.used == pytest.approx(
        sum(value for _, value in allocation.compute_by_contributor)
    )


def test_unverified_agent_does_not_cross_into_resource_commit():
    utilities = [
        create_relational_utility("agent:a", 1.0, ["evidence-a"], True, STAMP),
        create_relational_utility("agent:b", 1.0, ["evidence-b"], False, STAMP),
    ]
    structures = {
        "agent:a": structure("a", "b"),
        "agent:b": structure("b", "c"),
    }
    memory = create_resource_state(100.0, 0.0, STAMP)
    compute = create_resource_state(100.0, 0.0, STAMP)

    next_memory, next_compute = commit_self_organizing_resources_from_phi(
        utilities,
        memory,
        compute,
        structures,
        "2026-09-22T15:01:00Z",
    )

    assert next_memory.used > 0.0
    assert next_compute.used > 0.0
    assert next_memory.used < 100.0
    assert next_compute.used < 100.0


def test_missing_structure_blocks_the_flow():
    utility = create_relational_utility(
        "agent:a", 1.0, ["evidence-a"], True, STAMP
    )

    with pytest.raises(ValueError, match="missing Φ structure"):
        allocate_resources_from_phi(
            [utility],
            create_resource_state(10.0, 0.0, STAMP),
            create_resource_state(10.0, 0.0, STAMP),
            {},
        )
