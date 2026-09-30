from src.phi_structure import PhiStructure, create_phi_structure
from src.relation import create_relation
from src.structure import create_phi_structure as canonical_create_phi_structure


def relation(source: str, target: str, kind: str = "connect"):
    return create_relation(source, target, kind, "2026-09-30T00:00:00Z")


def test_phi_compatibility_entry_point_matches_canonical_implementation():
    first = relation("a", "b")
    second = relation("b", "c")

    canonical = canonical_create_phi_structure([first, second])
    compatibility = create_phi_structure([second, first])

    assert isinstance(compatibility, PhiStructure)
    assert compatibility == canonical


def test_phi_structure_exposes_derived_counts():
    result = create_phi_structure([relation("a", "b"), relation("b", "c")])

    assert result.edge_count == 2
    assert result.node_count == 3
