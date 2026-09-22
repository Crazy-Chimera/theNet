from __future__ import annotations

import pytest

from thenet.engine import commit_self_organizing_resources_from_phi
from src.genesis import create_genesis
from src.phi import create_phi
from src.relational_utility import create_relational_utility
from src.relation import create_relation
from src.resource_state import create_resource_state


STAMP = "2026-09-22T14:00:00Z"


def make_structure(source: str, target: str):
    first = create_genesis(source, STAMP)
    second = create_genesis(target, STAMP)
    relation = create_relation(first.id, second.id, "supports", STAMP)
    return create_phi([relation])


def test_runtime_derives_phi_coherence_before_commit():
    utility = create_relational_utility(
        "agent:a", 1.0, ["evidence"], True, STAMP
    )
    memory = create_resource_state(100.0, 20.0, STAMP)
    compute = create_resource_state(50.0, 10.0, STAMP)

    next_memory, next_compute = commit_self_organizing_resources_from_phi(
        [utility],
        memory,
        compute,
        {"agent:a": make_structure("a", "b")},
        "2026-09-22T14:01:00Z",
    )

    assert next_memory.used == pytest.approx(100.0)
    assert next_compute.used == pytest.approx(50.0)


def test_zero_phi_coherence_preserves_resources():
    utility = create_relational_utility(
        "agent:a", 1.0, ["evidence"], True, STAMP
    )
    memory = create_resource_state(100.0, 20.0, STAMP)
    compute = create_resource_state(50.0, 10.0, STAMP)

    next_memory, next_compute = commit_self_organizing_resources_from_phi(
        [utility],
        memory,
        compute,
        {"agent:a": create_phi([])},
        "2026-09-22T14:01:00Z",
    )

    assert next_memory is memory
    assert next_compute is compute


def test_unverified_utility_produces_no_phi_derived_allocation():
    utility = create_relational_utility(
        "agent:a", 1.0, ["evidence"], False, STAMP
    )
    memory = create_resource_state(100.0, 20.0, STAMP)
    compute = create_resource_state(50.0, 10.0, STAMP)

    next_memory, next_compute = commit_self_organizing_resources_from_phi(
        [utility],
        memory,
        compute,
        {"agent:a": make_structure("a", "b")},
        "2026-09-22T14:01:00Z",
    )

    assert next_memory is memory
    assert next_compute is compute


def test_missing_phi_structure_is_rejected():
    utility = create_relational_utility(
        "agent:a", 1.0, ["evidence"], True, STAMP
    )

    with pytest.raises(ValueError, match="missing Φ structure"):
        commit_self_organizing_resources_from_phi(
            [utility],
            create_resource_state(10.0, 0.0, STAMP),
            create_resource_state(10.0, 0.0, STAMP),
            {},
            "2026-09-22T14:01:00Z",
        )
