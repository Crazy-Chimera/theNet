from src.phi_derived_allocation import allocate_memory_and_compute_from_phi
from src.phi_structure import PhiStructure
from src.genesis import create_genesis
from src.relation import create_relation
from src.relational_utility import create_relational_utility
from src.resource_state import create_resource_state


STAMP = "2026-09-22T14:00:00Z"


def make_structure(source: str, target: str) -> PhiStructure:
    first = create_genesis(source, STAMP)
    second = create_genesis(target, STAMP)
    relation = create_relation(first.id, second.id, "supports", STAMP)
    return __import__("src.phi", fromlist=["create_phi"]).create_phi([relation])


def test_phi_derived_allocation_uses_structural_coherence():
    utility = create_relational_utility(
        "agent:a", 1.0, ["evidence"], True, STAMP
    )
    memory = create_resource_state(100.0, 20.0, STAMP)
    compute = create_resource_state(50.0, 10.0, STAMP)

    result = allocate_memory_and_compute_from_phi(
        [utility],
        memory,
        compute,
        {"agent:a": make_structure("a", "b")},
    )

    assert result.memory[0].allocation == 80.0
    assert result.compute[0].allocation == 40.0


def test_phi_derived_allocation_rejects_missing_structure():
    utility = create_relational_utility(
        "agent:a", 1.0, ["evidence"], True, STAMP
    )
    memory = create_resource_state(10.0, 0.0, STAMP)
    compute = create_resource_state(10.0, 0.0, STAMP)

    try:
        allocate_memory_and_compute_from_phi(
            [utility], memory, compute, {}
        )
    except ValueError as error:
        assert "missing Φ structure" in str(error)
    else:
        raise AssertionError("missing Φ structure must be rejected")
